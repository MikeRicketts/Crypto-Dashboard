"""
Alert System Module
Monitors price changes and sends alerts via terminal, email, or webhook
"""

import smtplib
import requests
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class AlertSystem:
    def __init__(self):
        self.threshold = config.ALERT_THRESHOLD
        self.cooldown = config.ALERT_COOLDOWN
        self.last_alerts = {}  # Track last alert time for each asset
        self.email_enabled = config.EMAIL_ENABLED
        self.webhook_enabled = config.WEBHOOK_ENABLED
        
    def check_price_alerts(self, prices: Dict) -> List[Dict]:
        """
        Check if any price changes exceed the alert threshold
        
        Args:
            prices: Dict of current price data
            
        Returns:
            List of alert messages
        """
        alerts = []
        current_time = datetime.now()
        
        if not prices:
            return alerts
        
        for symbol, price_data in prices.items():
            # Validate price data
            if not self._validate_price_data(symbol, price_data):
                logger.warning(f"Invalid price data for {symbol}, skipping alert check")
                continue
                
            change_24h = price_data.get('change_24h', 0)
            price = price_data.get('price', 0)
            
            # Check if change exceeds threshold
            if abs(change_24h) >= self.threshold:
                # Check cooldown
                if self._can_send_alert(symbol, current_time):
                    alert = {
                        'symbol': symbol,
                        'price': price,
                        'change_24h': change_24h,
                        'threshold': self.threshold,
                        'timestamp': current_time,
                        'type': price_data.get('type', 'unknown'),
                        'message': self._format_alert_message(symbol, price, change_24h)
                    }
                    alerts.append(alert)
                    
                    # Update last alert time
                    self.last_alerts[symbol] = current_time
                    
        return alerts
    
    def _validate_price_data(self, symbol: str, price_data: Dict) -> bool:
        """Validate price data before processing alerts"""
        from security_config import SecurityConfig
        return SecurityConfig.validate_price_data(symbol, price_data)
    
    def _can_send_alert(self, symbol: str, current_time: datetime) -> bool:
        """
        Check if enough time has passed since the last alert for this symbol
        
        Args:
            symbol: Asset symbol
            current_time: Current timestamp
            
        Returns:
            True if alert can be sent
        """
        if symbol not in self.last_alerts:
            return True
            
        time_since_last = current_time - self.last_alerts[symbol]
        return time_since_last.total_seconds() >= self.cooldown
    
    def _format_alert_message(self, symbol: str, price: float, change_24h: float) -> str:
        """
        Format alert message
        
        Args:
            symbol: Asset symbol
            price: Current price
            change_24h: 24h price change percentage
            
        Returns:
            Formatted alert message
        """
        direction = "📈" if change_24h > 0 else "📉"
        change_text = "increased" if change_24h > 0 else "decreased"
        
        message = (
            f"🚨 PRICE ALERT 🚨\n"
            f"Asset: {symbol.upper()}\n"
            f"Current Price: ${price:,.2f}\n"
            f"24h Change: {change_24h:+.2f}% {direction}\n"
            f"Threshold: ±{self.threshold}%\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return message
    
    def send_terminal_alert(self, alert: Dict):
        """
        Send alert to terminal
        
        Args:
            alert: Alert data dictionary
        """
        try:
            print("\n" + "="*50)
            print(alert['message'])
            print("="*50 + "\n")
            logger.info(f"Terminal alert sent for {alert['symbol']}")
            
        except Exception as e:
            logger.error(f"Error sending terminal alert: {e}")
    
    def send_email_alert(self, alert: Dict):
        """
        Send alert via email
        
        Args:
            alert: Alert data dictionary
        """
        if not self.email_enabled:
            return
            
        try:
            # Validate email configuration
            if not self._validate_email_config():
                logger.warning("Email configuration is invalid, skipping email alert")
                return
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = config.EMAIL_FROM
            msg['To'] = config.EMAIL_TO
            msg['Subject'] = f"Price Alert: {alert['symbol'].upper()}"
            
            # Create HTML body
            html_body = f"""
            <html>
            <body>
                <h2>🚨 Price Alert 🚨</h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Asset:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{alert['symbol'].upper()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Current Price:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">${alert['price']:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>24h Change:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd; color: {'green' if alert['change_24h'] > 0 else 'red'};">
                            {alert['change_24h']:+.2f}%
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Threshold:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">±{alert['threshold']}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Time:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                </table>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(config.EMAIL_SMTP_SERVER, config.EMAIL_SMTP_PORT)
            server.starttls()
            
            # Get password from environment variable
            email_password = os.getenv('EMAIL_PASSWORD', config.EMAIL_PASSWORD)
            if not email_password:
                logger.error("Email password not found in environment variables")
                return
                
            server.login(config.EMAIL_FROM, email_password)
            
            text = server.send_message(msg)
            server.quit()
            
            logger.info(f"Email alert sent for {alert['symbol']}")
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
    
    def _validate_email_config(self) -> bool:
        """Validate email configuration"""
        try:
            required_fields = ['EMAIL_FROM', 'EMAIL_TO', 'EMAIL_SMTP_SERVER', 'EMAIL_SMTP_PORT']
            for field in required_fields:
                if not hasattr(config, field) or not getattr(config, field):
                    return False
            
            # Check if password is available
            email_password = os.getenv('EMAIL_PASSWORD', config.EMAIL_PASSWORD)
            if not email_password:
                return False
                
            return True
        except Exception:
            return False
    
    def send_webhook_alert(self, alert: Dict):
        """
        Send alert via webhook
        
        Args:
            alert: Alert data dictionary
        """
        if not self.webhook_enabled:
            return
            
        try:
            # Validate webhook configuration
            if not self._validate_webhook_config():
                logger.warning("Webhook configuration is invalid, skipping webhook alert")
                return
            
            # Prepare webhook payload
            payload = {
                'text': alert['message'],
                'attachments': [{
                    'color': 'danger' if alert['change_24h'] < 0 else 'good',
                    'fields': [
                        {
                            'title': 'Asset',
                            'value': alert['symbol'].upper(),
                            'short': True
                        },
                        {
                            'title': 'Current Price',
                            'value': f"${alert['price']:,.2f}",
                            'short': True
                        },
                        {
                            'title': '24h Change',
                            'value': f"{alert['change_24h']:+.2f}%",
                            'short': True
                        },
                        {
                            'title': 'Threshold',
                            'value': f"±{alert['threshold']}%",
                            'short': True
                        }
                    ],
                    'footer': f"Alert triggered at {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
                }]
            }
            
            # Send webhook with timeout
            response = requests.post(
                config.WEBHOOK_URL,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            logger.info(f"Webhook alert sent for {alert['symbol']}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending webhook alert: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending webhook alert: {e}")
    
    def _validate_webhook_config(self) -> bool:
        """Validate webhook configuration"""
        try:
            if not hasattr(config, 'WEBHOOK_URL') or not config.WEBHOOK_URL:
                return False
            return True
        except Exception:
            return False
    
    def process_alerts(self, prices: Dict):
        """
        Process all alerts for current prices
        
        Args:
            prices: Dict of current price data
        """
        alerts = self.check_price_alerts(prices)
        
        for alert in alerts:
            # Send to all configured channels
            self.send_terminal_alert(alert)
            self.send_email_alert(alert)
            self.send_webhook_alert(alert)
            
        if alerts:
            logger.info(f"Processed {len(alerts)} price alerts")
    
    def get_alert_stats(self) -> Dict:
        """
        Get alert system statistics
        
        Returns:
            Dict with alert statistics
        """
        current_time = datetime.now()
        active_alerts = 0
        
        for symbol, last_alert_time in self.last_alerts.items():
            time_since_last = current_time - last_alert_time
            if time_since_last.total_seconds() < self.cooldown:
                active_alerts += 1
        
        return {
            'total_alerts_sent': len(self.last_alerts),
            'active_alerts': active_alerts,
            'threshold': self.threshold,
            'cooldown_seconds': self.cooldown,
            'email_enabled': self.email_enabled,
            'webhook_enabled': self.webhook_enabled
        }
    
    def update_threshold(self, new_threshold: float):
        """
        Update alert threshold
        
        Args:
            new_threshold: New threshold percentage
        """
        if not isinstance(new_threshold, (int, float)) or new_threshold <= 0:
            logger.warning(f"Invalid threshold value: {new_threshold}")
            return
            
        self.threshold = float(new_threshold)
        logger.info(f"Alert threshold updated to {new_threshold}%")
    
    def update_cooldown(self, new_cooldown: int):
        """
        Update alert cooldown period
        
        Args:
            new_cooldown: New cooldown period in seconds
        """
        if not isinstance(new_cooldown, int) or new_cooldown <= 0:
            logger.warning(f"Invalid cooldown value: {new_cooldown}")
            return
            
        self.cooldown = new_cooldown
        logger.info(f"Alert cooldown updated to {new_cooldown} seconds")

# Global alert system instance
alert_system = AlertSystem()

if __name__ == "__main__":
    # Test the alert system
    print("Testing Alert System...")
    
    # Test data
    test_prices = {
        'bitcoin': {
            'symbol': 'bitcoin',
            'price': 45000.0,
            'change_24h': 7.5,  # Above threshold
            'timestamp': datetime.now(),
            'type': 'crypto'
        },
        'AAPL': {
            'symbol': 'AAPL',
            'price': 150.0,
            'change_24h': -6.2,  # Above threshold
            'timestamp': datetime.now(),
            'type': 'stock'
        }
    }
    
    # Test alert processing
    alert_system.process_alerts(test_prices)
    
    # Test stats
    stats = alert_system.get_alert_stats()
    print("Alert stats:", stats) 