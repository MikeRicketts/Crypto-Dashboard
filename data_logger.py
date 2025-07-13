"""
Data Logger Module
Handles CSV and SQLite storage with duplicate prevention
"""

import sqlite3
import pandas as pd
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import config

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class DataLogger:
    def __init__(self):
        self.db_path = config.DATABASE_PATH
        self.csv_path = config.CSV_LOG_PATH
        self._ensure_directories()
        self._init_database()
        self._init_csv()
        
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        
    def _init_database(self):
        """Initialize SQLite database with proper schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create price_data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    change_24h REAL,
                    asset_type TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp_symbol 
                ON price_data(timestamp, symbol)
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            
    def _init_csv(self):
        """Initialize CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_path):
            try:
                df = pd.DataFrame(columns=pd.Index(['timestamp', 'symbol', 'price', 'change_24h', 'asset_type']))
                df.to_csv(self.csv_path, index=False)
                logger.info("CSV file initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing CSV file: {e}")
                
    def _is_duplicate(self, symbol: str, timestamp: datetime, asset_type: str) -> bool:
        """
        Check if a price entry already exists for the given symbol and time window
        
        Args:
            symbol: Asset symbol
            timestamp: Price timestamp
            asset_type: 'crypto' or 'stock'
            
        Returns:
            True if duplicate exists within 1 minute window
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for entries within 1 minute of the timestamp
            time_window = timedelta(minutes=1)
            start_time = timestamp - time_window
            end_time = timestamp + time_window
            
            cursor.execute('''
                SELECT COUNT(*) FROM price_data 
                WHERE symbol = ? AND asset_type = ? 
                AND timestamp BETWEEN ? AND ?
            ''', (symbol, asset_type, start_time, end_time))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking for duplicates: {e}")
            return False
            
    def log_prices(self, prices: Dict) -> int:
        """
        Log price data to both CSV and SQLite
        
        Args:
            prices: Dict of price data from price scraper
            
        Returns:
            Number of entries logged
        """
        if not prices:
            logger.warning("No prices to log")
            return 0
            
        logged_count = 0
        
        try:
            # Prepare data for logging
            data_to_log = []
            current_time = datetime.now()
            
            for symbol, price_data in prices.items():
                # Validate input data
                if not self._validate_price_data(symbol, price_data):
                    logger.warning(f"Invalid price data for {symbol}, skipping")
                    continue
                
                # Check for duplicates
                if self._is_duplicate(symbol, current_time, price_data['type']):
                    logger.debug(f"Skipping duplicate entry for {symbol}")
                    continue
                    
                data_to_log.append({
                    'timestamp': current_time,
                    'symbol': symbol,
                    'price': price_data['price'],
                    'change_24h': price_data['change_24h'],
                    'asset_type': price_data['type']
                })
                
            if not data_to_log:
                logger.info("No new data to log (all entries were duplicates)")
                return 0
                
            # Log to SQLite
            logged_count += self._log_to_sqlite(data_to_log)
            
            # Log to CSV
            logged_count += self._log_to_csv(data_to_log)
            
            logger.info(f"Successfully logged {logged_count} price entries")
            return logged_count
            
        except Exception as e:
            logger.error(f"Error logging prices: {e}")
            return 0
    
    def _validate_price_data(self, symbol: str, price_data: Dict) -> bool:
        """Validate price data before logging"""
        from security_config import SecurityConfig
        return SecurityConfig.validate_price_data(symbol, price_data)
            
    def _log_to_sqlite(self, data: List[Dict]) -> int:
        """Log data to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for entry in data:
                cursor.execute('''
                    INSERT INTO price_data (timestamp, symbol, price, change_24h, asset_type)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    entry['timestamp'],
                    entry['symbol'],
                    entry['price'],
                    entry['change_24h'],
                    entry['asset_type']
                ))
                
            conn.commit()
            conn.close()
            return len(data)
            
        except Exception as e:
            logger.error(f"Error logging to SQLite: {e}")
            return 0
            
    def _log_to_csv(self, data: List[Dict]) -> int:
        """Log data to CSV file"""
        try:
            df_new = pd.DataFrame(data)
            df_new.to_csv(self.csv_path, mode='a', header=False, index=False)
            return len(data)
            
        except Exception as e:
            logger.error(f"Error logging to CSV: {e}")
            return 0
            
    def get_latest_prices(self, limit: int = 50) -> pd.DataFrame:
        """
        Get the latest price entries
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            DataFrame with latest price data
        """
        try:
            # Validate limit parameter
            if not isinstance(limit, int) or limit <= 0 or limit > config.MAX_LIMIT:
                limit = config.DEFAULT_LIMIT
            
            conn = sqlite3.connect(self.db_path)
            query = '''
                SELECT timestamp, symbol, price, change_24h, asset_type
                FROM price_data
                ORDER BY timestamp DESC
                LIMIT ?
            '''
            
            df = pd.read_sql_query(query, conn, params=[limit])
            conn.close()
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting latest prices: {e}")
            return pd.DataFrame()
            
    def get_asset_history(self, symbol: str, hours: int = 24) -> pd.DataFrame:
        """
        Get historical price data for a specific asset
        
        Args:
            symbol: Asset symbol
            hours: Number of hours of history to retrieve
            
        Returns:
            DataFrame with historical price data
        """
        try:
            # Validate inputs
            if not symbol or not isinstance(symbol, str):
                return pd.DataFrame()
            
            if not isinstance(hours, int) or hours <= 0 or hours > config.MAX_HISTORY_HOURS:
                hours = config.DEFAULT_HISTORY_HOURS
            
            conn = sqlite3.connect(self.db_path)
            
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            query = '''
                SELECT timestamp, price, change_24h
                FROM price_data
                WHERE symbol = ?
                AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            '''
            
            df = pd.read_sql_query(query, conn, params=[symbol, start_time, end_time])
            conn.close()
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting asset history for {symbol}: {e}")
            return pd.DataFrame()
            
    def get_summary_stats(self) -> Dict:
        """
        Get summary statistics of logged data
        
        Returns:
            Dict with summary statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total entries
            cursor.execute('SELECT COUNT(*) FROM price_data')
            total_entries = cursor.fetchone()[0]
            
            # Get unique assets
            cursor.execute('SELECT COUNT(DISTINCT symbol) FROM price_data')
            unique_assets = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM price_data')
            date_range = cursor.fetchone()
            
            # Get latest entry
            cursor.execute('SELECT MAX(timestamp) FROM price_data')
            latest_entry = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_entries': total_entries,
                'unique_assets': unique_assets,
                'date_range': date_range,
                'latest_entry': latest_entry
            }
            
        except Exception as e:
            logger.error(f"Error getting summary stats: {e}")
            return {}
            
    def cleanup_old_data(self, days: int = 30):
        """
        Clean up old data to prevent database bloat
        
        Args:
            days: Number of days of data to keep
        """
        try:
            # Validate days parameter
            if not isinstance(days, int) or days <= 0 or days > config.MAX_CLEANUP_DAYS:
                days = config.DEFAULT_CLEANUP_DAYS
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('DELETE FROM price_data WHERE timestamp < ?', (cutoff_date,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} old entries")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

# Global logger instance
data_logger = DataLogger()

if __name__ == "__main__":
    # Test the data logger
    print("Testing Data Logger...")
    
    # Test data
    test_prices = {
        'bitcoin': {
            'symbol': 'bitcoin',
            'price': 45000.0,
            'change_24h': 2.5,
            'timestamp': datetime.now(),
            'type': 'crypto'
        },
        'AAPL': {
            'symbol': 'AAPL',
            'price': 150.0,
            'change_24h': -1.2,
            'timestamp': datetime.now(),
            'type': 'stock'
        }
    }
    
    # Test logging
    logged_count = data_logger.log_prices(test_prices)
    print(f"Logged {logged_count} entries")
    
    # Test getting latest prices
    latest = data_logger.get_latest_prices(10)
    print("Latest prices:", latest)
    
    # Test summary stats
    stats = data_logger.get_summary_stats()
    print("Summary stats:", stats) 