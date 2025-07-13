"""
Integration Test Script for Crypto/Stock Price Tracker
Tests all components work together properly
"""

import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all modules can be imported"""
    logger.info("Testing imports...")
    
    try:
        import config
        logger.info("✓ config imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import config: {e}")
        return False
    
    try:
        import security_config
        logger.info("✓ security_config imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import security_config: {e}")
        return False
    
    try:
        from price_scraper import price_scraper
        logger.info("✓ price_scraper imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import price_scraper: {e}")
        return False
    
    try:
        from data_logger import data_logger
        logger.info("✓ data_logger imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import data_logger: {e}")
        return False
    
    try:
        from alert_system import alert_system
        logger.info("✓ alert_system imported successfully")
    except Exception as e:
        logger.error(f"✗ Failed to import alert_system: {e}")
        return False
    
    return True

def test_security_config():
    """Test security configuration"""
    logger.info("Testing security configuration...")
    
    try:
        from security_config import SecurityConfig
        
        # Test symbol validation
        assert SecurityConfig.validate_symbol("bitcoin") == True
        assert SecurityConfig.validate_symbol("") == False
        assert SecurityConfig.validate_symbol("a" * 100) == False
        logger.info("✓ Symbol validation works")
        
        # Test price validation
        assert SecurityConfig.validate_price(100.0) == True
        assert SecurityConfig.validate_price(-100.0) == False
        assert SecurityConfig.validate_price("invalid") == False
        logger.info("✓ Price validation works")
        
        # Test change validation
        assert SecurityConfig.validate_change_percent(5.0) == True
        assert SecurityConfig.validate_change_percent(-5.0) == True
        assert SecurityConfig.validate_change_percent(2000.0) == False
        logger.info("✓ Change validation works")
        
        return True
    except Exception as e:
        logger.error(f"✗ Security config test failed: {e}")
        return False

def test_data_logger():
    """Test data logger functionality"""
    logger.info("Testing data logger...")
    
    try:
        from data_logger import data_logger
        
        # Test with sample data
        test_prices = {
            'bitcoin': {
                'symbol': 'bitcoin',
                'price': 45000.0,
                'change_24h': 2.5,
                'timestamp': datetime.now(),
                'type': 'crypto'
            }
        }
        
        # Test logging
        logged_count = data_logger.log_prices(test_prices)
        logger.info(f"✓ Logged {logged_count} entries")
        
        # Test getting latest prices
        latest = data_logger.get_latest_prices(5)
        logger.info(f"✓ Retrieved {len(latest)} latest prices")
        
        # Test summary stats
        stats = data_logger.get_summary_stats()
        logger.info(f"✓ Got summary stats: {stats}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Data logger test failed: {e}")
        return False

def test_alert_system():
    """Test alert system functionality"""
    logger.info("Testing alert system...")
    
    try:
        from alert_system import alert_system
        
        # Test with sample data
        test_prices = {
            'bitcoin': {
                'symbol': 'bitcoin',
                'price': 45000.0,
                'change_24h': 7.5,  # Above threshold
                'timestamp': datetime.now(),
                'type': 'crypto'
            }
        }
        
        # Test alert processing
        alerts = alert_system.check_price_alerts(test_prices)
        logger.info(f"✓ Found {len(alerts)} alerts")
        
        # Test stats
        stats = alert_system.get_alert_stats()
        logger.info(f"✓ Got alert stats: {stats}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Alert system test failed: {e}")
        return False

def test_price_scraper():
    """Test price scraper functionality"""
    logger.info("Testing price scraper...")
    
    try:
        from price_scraper import price_scraper
        
        # Test crypto prices (this will make actual API calls)
        crypto_prices = price_scraper.get_crypto_prices(['bitcoin'])
        logger.info(f"✓ Retrieved {len(crypto_prices)} crypto prices")
        
        # Test stock prices (this will make actual API calls)
        stock_prices = price_scraper.get_stock_prices(['AAPL'])
        logger.info(f"✓ Retrieved {len(stock_prices)} stock prices")
        
        return True
    except Exception as e:
        logger.error(f"✗ Price scraper test failed: {e}")
        return False

def test_security_audit():
    """Test security audit functionality"""
    logger.info("Testing security audit...")
    
    try:
        from security_audit import SecurityAuditor
        
        auditor = SecurityAuditor()
        results = auditor.run_full_audit()
        
        logger.info(f"✓ Security audit completed")
        logger.info(f"  - Issues: {len(results['issues'])}")
        logger.info(f"  - Warnings: {len(results['warnings'])}")
        logger.info(f"  - Recommendations: {len(results['recommendations'])}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Security audit test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    logger.info("Starting integration tests...")
    
    tests = [
        ("Imports", test_imports),
        ("Security Config", test_security_config),
        ("Data Logger", test_data_logger),
        ("Alert System", test_alert_system),
        ("Security Audit", test_security_audit),
        ("Price Scraper", test_price_scraper),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {test_name} test...")
        logger.info(f"{'='*50}")
        
        try:
            if test_func():
                logger.info(f"✓ {test_name} test PASSED")
                passed += 1
            else:
                logger.error(f"✗ {test_name} test FAILED")
                failed += 1
        except Exception as e:
            logger.error(f"✗ {test_name} test FAILED with exception: {e}")
            failed += 1
    
    logger.info(f"\n{'='*50}")
    logger.info("INTEGRATION TEST RESULTS")
    logger.info(f"{'='*50}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Total: {passed + failed}")
    
    if failed == 0:
        logger.info("🎉 All tests passed! Integration is working properly.")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 