"""
Main Application - Crypto/Stock Price Tracker
Orchestrates all modules and provides the complete application
"""

import time
import threading
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import config
from price_scraper import price_scraper
from data_logger import data_logger
from alert_system import alert_system
from dashboard import app

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class PriceTracker:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.running = False
        
    def start(self):
        """Start the price tracker application"""
        try:
            logger.info("Starting Crypto/Stock Price Tracker...")
            
            # Initialize components
            self._init_components()
            
            # Start scheduled jobs
            self._start_scheduler()
            
            # Start Flask dashboard
            self._start_dashboard()
            
            self.running = True
            logger.info("Price tracker started successfully!")
            
        except Exception as e:
            logger.error(f"Error starting price tracker: {e}")
            raise
    
    def _init_components(self):
        """Initialize all components"""
        logger.info("Initializing components...")
        
        # Test price scraper
        try:
            test_prices = price_scraper.get_all_prices()
            logger.info(f"Price scraper initialized. Found {len(test_prices)} assets.")
        except Exception as e:
            logger.error(f"Error initializing price scraper: {e}")
        
        # Test data logger
        try:
            stats = data_logger.get_summary_stats()
            logger.info(f"Data logger initialized. Database stats: {stats}")
        except Exception as e:
            logger.error(f"Error initializing data logger: {e}")
        
        # Test alert system
        try:
            alert_stats = alert_system.get_alert_stats()
            logger.info(f"Alert system initialized. Alert stats: {alert_stats}")
        except Exception as e:
            logger.error(f"Error initializing alert system: {e}")
    
    def _start_scheduler(self):
        """Start the background scheduler for periodic tasks"""
        logger.info("Starting background scheduler...")
        
        # Schedule crypto price updates
        self.scheduler.add_job(
            func=self._update_crypto_prices,
            trigger=IntervalTrigger(seconds=config.CRYPTO_UPDATE_INTERVAL),
            id='crypto_price_update',
            name='Crypto Price Update',
            replace_existing=True
        )
        
        # Schedule stock price updates
        self.scheduler.add_job(
            func=self._update_stock_prices,
            trigger=IntervalTrigger(seconds=config.STOCK_UPDATE_INTERVAL),
            id='stock_price_update',
            name='Stock Price Update',
            replace_existing=True
        )
        
        # Schedule data cleanup (daily)
        self.scheduler.add_job(
            func=self._cleanup_old_data,
            trigger=IntervalTrigger(days=1),
            id='data_cleanup',
            name='Data Cleanup',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Background scheduler started successfully!")
    
    def _start_dashboard(self):
        """Start the Flask dashboard in a separate thread"""
        def run_dashboard():
            try:
                app.run(
                    host=config.FLASK_HOST,
                    port=config.FLASK_PORT,
                    debug=False,  # Set to False for production
                    use_reloader=False
                )
            except Exception as e:
                logger.error(f"Error starting dashboard: {e}")
        
        # Start dashboard in a separate thread
        dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        dashboard_thread.start()
        logger.info(f"Dashboard started at http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    
    def _update_crypto_prices(self):
        """Update crypto prices and process alerts"""
        try:
            logger.info("Updating crypto prices...")
            prices = price_scraper.get_crypto_prices()
            
            if prices:
                # Log prices
                logged_count = data_logger.log_prices(prices)
                logger.info(f"Logged {logged_count} crypto price entries")
                
                # Process alerts
                alert_system.process_alerts(prices)
                
            else:
                logger.warning("No crypto prices received")
                
        except Exception as e:
            logger.error(f"Error updating crypto prices: {e}")
    
    def _update_stock_prices(self):
        """Update stock prices and process alerts"""
        try:
            logger.info("Updating stock prices...")
            prices = price_scraper.get_stock_prices()
            
            if prices:
                # Log prices
                logged_count = data_logger.log_prices(prices)
                logger.info(f"Logged {logged_count} stock price entries")
                
                # Process alerts
                alert_system.process_alerts(prices)
                
            else:
                logger.warning("No stock prices received")
                
        except Exception as e:
            logger.error(f"Error updating stock prices: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old data to prevent database bloat"""
        try:
            logger.info("Running data cleanup...")
            data_logger.cleanup_old_data(days=30)
            logger.info("Data cleanup completed")
        except Exception as e:
            logger.error(f"Error during data cleanup: {e}")
    
    def stop(self):
        """Stop the price tracker application"""
        try:
            logger.info("Stopping price tracker...")
            
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Background scheduler stopped")
            
            self.running = False
            logger.info("Price tracker stopped successfully!")
            
        except Exception as e:
            logger.error(f"Error stopping price tracker: {e}")
    
    def get_status(self):
        """Get current application status"""
        try:
            # Get component status
            crypto_prices = price_scraper.get_crypto_prices()
            stock_prices = price_scraper.get_stock_prices()
            alert_stats = alert_system.get_alert_stats()
            db_stats = data_logger.get_summary_stats()
            
            return {
                'running': self.running,
                'scheduler_running': self.scheduler.running,
                'crypto_assets_tracked': len(crypto_prices),
                'stock_assets_tracked': len(stock_prices),
                'alert_stats': alert_stats,
                'database_stats': db_stats,
                'last_update': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {'error': str(e)}

def main():
    """Main entry point"""
    tracker = PriceTracker()
    
    try:
        # Start the application
        tracker.start()
        
        # Keep the main thread alive
        while tracker.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
        tracker.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        tracker.stop()
        raise

if __name__ == "__main__":
    main() 