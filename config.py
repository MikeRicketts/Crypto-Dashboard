"""
Configuration settings for Crypto/Stock Price Tracker
"""

# Asset Configuration
CRYPTO_ASSETS = [
    "bitcoin",
    "ethereum", 
    "binancecoin",
    "cardano",
    "solana",
    "ripple",
    "polkadot",
    "dogecoin"
]

STOCK_ASSETS = [
    "AAPL",  # Apple
    "GOOGL", # Google
    "MSFT",  # Microsoft
    "TSLA",  # Tesla
    "AMZN",  # Amazon
    "NVDA",  # NVIDIA
    "META",  # Meta
    "NFLX"   # Netflix
]

# Database Configuration
DATABASE_PATH = "database/price_data.db"
CSV_LOG_PATH = "logs/price_logs.csv"

# Update Intervals (in seconds)
CRYPTO_UPDATE_INTERVAL = 60  # 1 minute
STOCK_UPDATE_INTERVAL = 300   # 5 minutes

# Alert Configuration
ALERT_THRESHOLD = 5.0  # 5% price change
ALERT_COOLDOWN = 300   # 5 minutes between alerts

# Web Dashboard Configuration
FLASK_HOST = "127.0.0.1"  # Changed from 0.0.0.0 for security
FLASK_PORT = 5000
FLASK_DEBUG = False  # Disabled for production security

# API Configuration
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
COINGECKO_RATE_LIMIT = 50  # requests per minute

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Email Alert Configuration (optional)
EMAIL_ENABLED = False
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
EMAIL_FROM = "your-email@gmail.com"
EMAIL_TO = "recipient@example.com"
EMAIL_PASSWORD = ""  # Set in environment variable

# Webhook Configuration (optional)
WEBHOOK_ENABLED = False
WEBHOOK_URL = "https://your-webhook-url.com/endpoint"

# Chart Configuration
CHART_HISTORY_HOURS = 24  # Hours of historical data to show
CHART_UPDATE_INTERVAL = 60  # Chart update interval in seconds

# Security Configuration
MAX_REQUESTS_PER_MINUTE = 60  # Rate limiting
INPUT_VALIDATION_ENABLED = True
LOG_SENSITIVE_DATA = False  # Disable logging of sensitive information

# Data Management Constants
DEFAULT_LIMIT = 50  # Default number of records to retrieve
MAX_LIMIT = 1000  # Maximum number of records to retrieve
DEFAULT_HISTORY_HOURS = 24  # Default hours of history
MAX_HISTORY_HOURS = 8760  # Maximum hours of history (1 year)
DEFAULT_CLEANUP_DAYS = 30  # Default days for cleanup
MAX_CLEANUP_DAYS = 3650  # Maximum days for cleanup (10 years)

# Validation Constants
MIN_THRESHOLD = 0.1  # Minimum alert threshold
MAX_THRESHOLD = 100.0  # Maximum alert threshold
MIN_COOLDOWN = 60  # Minimum cooldown in seconds
MAX_COOLDOWN = 3600  # Maximum cooldown in seconds (1 hour)
MIN_CLEANUP_DAYS = 1  # Minimum cleanup days
MAX_CLEANUP_DAYS_INPUT = 365  # Maximum cleanup days for user input 