"""
Price Scraper Module
Fetches real-time prices from CoinGecko (crypto) and Yahoo Finance (stocks)
"""

import requests
import yfinance as yf
import pandas as pd
from datetime import datetime
import time
import logging
from typing import Dict, List, Optional
import config

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class PriceScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.last_request_time = 0
        self.rate_limit_delay = 60 / config.COINGECKO_RATE_LIMIT  # seconds between requests
        
    def _rate_limit(self):
        """Implement rate limiting for CoinGecko API"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _validate_symbols(self, symbols: List[str]) -> List[str]:
        """Validate and clean symbol list"""
        if not symbols:
            return []
        
        valid_symbols = []
        for symbol in symbols:
            if symbol and isinstance(symbol, str):
                # Clean and validate symbol
                clean_symbol = symbol.strip().lower()
                if clean_symbol and len(clean_symbol) <= 50:  # Reasonable length limit
                    valid_symbols.append(clean_symbol)
        
        return valid_symbols
    
    def get_crypto_prices(self, symbols: Optional[List[str]] = None) -> Dict:
        """
        Fetch cryptocurrency prices from CoinGecko API
        
        Args:
            symbols: List of crypto symbols (e.g., ['bitcoin', 'ethereum'])
            
        Returns:
            Dict with price data for each asset
        """
        if symbols is None:
            symbols = config.CRYPTO_ASSETS
        
        # Validate and clean symbols
        symbols = self._validate_symbols(symbols)
        if not symbols:
            logger.warning("No valid crypto symbols provided")
            return {}
            
        try:
            self._rate_limit()
            
            # CoinGecko API endpoint for multiple coins
            url = f"{config.COINGECKO_API_URL}/simple/price"
            params = {
                'ids': ','.join(symbols),
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_last_updated_at': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            results = {}
            timestamp = datetime.now()
            
            for symbol in symbols:
                if symbol in data:
                    coin_data = data[symbol]
                    
                    # Validate coin data
                    if self._validate_coin_data(coin_data):
                        results[symbol] = {
                            'symbol': symbol,
                            'price': coin_data.get('usd', 0),
                            'change_24h': coin_data.get('usd_24h_change', 0),
                            'timestamp': timestamp,
                            'type': 'crypto'
                        }
                    else:
                        logger.warning(f"Invalid data received for crypto symbol: {symbol}")
                else:
                    logger.warning(f"No data found for crypto symbol: {symbol}")
                    
            logger.info(f"Successfully fetched prices for {len(results)} crypto assets")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching crypto prices: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error in crypto price fetching: {e}")
            return {}
    
    def _validate_coin_data(self, coin_data: Dict) -> bool:
        """Validate coin data from API response"""
        try:
            if not isinstance(coin_data, dict):
                return False
            
            # Check for required fields
            required_fields = ['usd']
            for field in required_fields:
                if field not in coin_data:
                    return False
            
            # Validate price is numeric and positive
            price = coin_data.get('usd')
            if not isinstance(price, (int, float)) or price <= 0:
                return False
            
            # Validate change_24h if present
            change_24h = coin_data.get('usd_24h_change')
            if change_24h is not None and not isinstance(change_24h, (int, float)):
                return False
            
            return True
        except Exception:
            return False
    
    def get_stock_prices(self, symbols: Optional[List[str]] = None) -> Dict:
        """
        Fetch stock prices from Yahoo Finance using yfinance
        
        Args:
            symbols: List of stock symbols (e.g., ['AAPL', 'GOOGL'])
            
        Returns:
            Dict with price data for each asset
        """
        if symbols is None:
            symbols = config.STOCK_ASSETS
        
        # Validate and clean symbols
        symbols = self._validate_symbols(symbols)
        if not symbols:
            logger.warning("No valid stock symbols provided")
            return {}
            
        results = {}
        timestamp = datetime.now()
        
        try:
            # Fetch data for all symbols at once
            tickers = yf.Tickers(' '.join(symbols))
            
            for symbol in symbols:
                try:
                    ticker = tickers.tickers[symbol]
                    info = ticker.info
                    
                    # Validate stock data
                    if self._validate_stock_data(info):
                        # Get current price and 24h change
                        current_price = info.get('regularMarketPrice', 0)
                        previous_close = info.get('regularMarketPreviousClose', current_price)
                        
                        if previous_close and current_price:
                            change_24h = ((current_price - previous_close) / previous_close) * 100
                        else:
                            change_24h = 0
                        
                        results[symbol] = {
                            'symbol': symbol,
                            'price': current_price,
                            'change_24h': change_24h,
                            'timestamp': timestamp,
                            'type': 'stock'
                        }
                    else:
                        logger.warning(f"Invalid data received for stock symbol: {symbol}")
                        
                except Exception as e:
                    logger.warning(f"Error fetching data for stock {symbol}: {e}")
                    continue
                    
            logger.info(f"Successfully fetched prices for {len(results)} stock assets")
            return results
            
        except Exception as e:
            logger.error(f"Error fetching stock prices: {e}")
            return {}
    
    def _validate_stock_data(self, stock_data: Dict) -> bool:
        """Validate stock data from yfinance"""
        try:
            if not isinstance(stock_data, dict):
                return False
            
            # Check for required fields
            required_fields = ['regularMarketPrice']
            for field in required_fields:
                if field not in stock_data:
                    return False
            
            # Validate price is numeric and positive
            price = stock_data.get('regularMarketPrice')
            if not isinstance(price, (int, float)) or price <= 0:
                return False
            
            return True
        except Exception:
            return False
    
    def get_all_prices(self) -> Dict:
        """
        Fetch both crypto and stock prices
        
        Returns:
            Combined dict with all asset prices
        """
        crypto_prices = self.get_crypto_prices()
        stock_prices = self.get_stock_prices()
        
        # Combine results
        all_prices = {**crypto_prices, **stock_prices}
        
        logger.info(f"Total assets tracked: {len(all_prices)}")
        return all_prices
    
    def get_asset_info(self, symbol: str, asset_type: str = 'crypto') -> Optional[Dict]:
        """
        Get detailed information about a specific asset
        
        Args:
            symbol: Asset symbol
            asset_type: 'crypto' or 'stock'
            
        Returns:
            Dict with detailed asset information
        """
        try:
            # Validate inputs
            if not symbol or not isinstance(symbol, str):
                return None
            
            if asset_type not in ['crypto', 'stock']:
                return None
            
            if asset_type == 'crypto':
                self._rate_limit()
                url = f"{config.COINGECKO_API_URL}/coins/{symbol}"
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                return {
                    'name': data.get('name', symbol),
                    'symbol': data.get('symbol', symbol).upper(),
                    'market_cap': data.get('market_data', {}).get('market_cap', {}).get('usd', 0),
                    'volume_24h': data.get('market_data', {}).get('total_volume', {}).get('usd', 0),
                    'circulating_supply': data.get('market_data', {}).get('circulating_supply', 0),
                    'max_supply': data.get('market_data', {}).get('max_supply', 0),
                    'image': data.get('image', {}).get('large', ''),
                    'description': data.get('description', {}).get('en', '')[:200] + '...'
                }
                
            elif asset_type == 'stock':
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                return {
                    'name': info.get('longName', symbol),
                    'symbol': symbol,
                    'market_cap': info.get('marketCap', 0),
                    'volume': info.get('volume', 0),
                    'sector': info.get('sector', ''),
                    'industry': info.get('industry', ''),
                    'website': info.get('website', ''),
                    'description': info.get('longBusinessSummary', '')[:200] + '...'
                }
                
        except Exception as e:
            logger.error(f"Error fetching asset info for {symbol}: {e}")
            return None

# Global scraper instance
price_scraper = PriceScraper()

if __name__ == "__main__":
    # Test the scraper
    print("Testing Price Scraper...")
    
    # Test crypto prices
    crypto_prices = price_scraper.get_crypto_prices(['bitcoin', 'ethereum'])
    print("Crypto Prices:", crypto_prices)
    
    # Test stock prices
    stock_prices = price_scraper.get_stock_prices(['AAPL', 'GOOGL'])
    print("Stock Prices:", stock_prices)
    
    # Test combined prices
    all_prices = price_scraper.get_all_prices()
    print("All Prices:", all_prices) 