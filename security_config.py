"""
Security Configuration for Crypto/Stock Price Tracker
Centralized security settings and validation functions
"""

import os
import re
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SecurityConfig:
    """Security configuration and validation utilities"""
    
    # Security settings
    MAX_SYMBOL_LENGTH = 50
    MAX_PRICE_VALUE = 1000000000  # $1 billion max
    MAX_CHANGE_PERCENT = 1000  # 1000% max change
    MIN_PASSWORD_LENGTH = 8
    MAX_REQUEST_SIZE = 1024 * 1024  # 1MB max request size
    
    # Rate limiting
    RATE_LIMIT_ENABLED = True
    MAX_REQUESTS_PER_MINUTE = 60
    RATE_LIMIT_WINDOW = 60  # seconds
    
    # Input validation patterns
    SYMBOL_PATTERN = re.compile(r'^[A-Za-z0-9.-]{1,50}$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    URL_PATTERN = re.compile(r'^https?://[^\s/$.?#].[^\s]*$')
    
    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """Validate asset symbol"""
        if not symbol or not isinstance(symbol, str):
            return False
        
        # Check length
        if len(symbol) > SecurityConfig.MAX_SYMBOL_LENGTH:
            return False
        
        # Check pattern
        if not SecurityConfig.SYMBOL_PATTERN.match(symbol):
            return False
        
        return True
    
    @staticmethod
    def validate_price(price: Any) -> bool:
        """Validate price value"""
        try:
            if not isinstance(price, (int, float)):
                return False
            
            if price <= 0 or price > SecurityConfig.MAX_PRICE_VALUE:
                return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_change_percent(change: Any) -> bool:
        """Validate percentage change"""
        try:
            if not isinstance(change, (int, float)):
                return False
            
            if abs(change) > SecurityConfig.MAX_CHANGE_PERCENT:
                return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_price_data(symbol: str, price_data: Dict) -> bool:
        """Centralized price data validation"""
        try:
            if not symbol or not isinstance(symbol, str):
                return False
                
            required_fields = ['price', 'change_24h', 'type']
            for field in required_fields:
                if field not in price_data:
                    return False
            
            # Validate price is numeric and positive
            if not SecurityConfig.validate_price(price_data['price']):
                return False
            
            # Validate change_24h is numeric
            if not SecurityConfig.validate_change_percent(price_data['change_24h']):
                return False
            
            # Validate asset type
            if price_data['type'] not in ['crypto', 'stock']:
                return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address"""
        if not email or not isinstance(email, str):
            return False
        
        return bool(SecurityConfig.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL"""
        if not url or not isinstance(url, str):
            return False
        
        return bool(SecurityConfig.URL_PATTERN.match(url))
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Sanitize user input"""
        if not input_str or not isinstance(input_str, str):
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', input_str)
        return sanitized.strip()
    
    @staticmethod
    def validate_configuration() -> Dict[str, bool]:
        """Validate security configuration"""
        issues = {}
        
        # Check environment variables
        if os.getenv('EMAIL_PASSWORD'):
            issues['email_password_set'] = True
        else:
            issues['email_password_set'] = False
            logger.warning("EMAIL_PASSWORD environment variable not set")
        
        # Check file permissions
        try:
            db_path = "database/price_data.db"
            if os.path.exists(db_path):
                # Check if file is readable/writable by owner only
                stat = os.stat(db_path)
                if stat.st_mode & 0o777 != 0o600:
                    issues['db_permissions'] = False
                    logger.warning("Database file permissions should be 600")
                else:
                    issues['db_permissions'] = True
        except Exception as e:
            issues['db_permissions'] = False
            logger.error(f"Error checking database permissions: {e}")
        
        return issues
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get security headers for web responses"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; img-src 'self' data:; font-src 'self' cdnjs.cloudflare.com;"
        } 