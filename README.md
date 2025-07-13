# Crypto/Stock Price Tracker

A comprehensive real-time cryptocurrency and stock price tracking application with alert system, web dashboard, and data logging capabilities.

## Features

- **Real-time Price Tracking**: Monitor crypto and stock prices from CoinGecko and Yahoo Finance APIs
- **Web Dashboard**: Beautiful, responsive web interface with live price updates
- **Alert System**: Configurable price alerts via terminal, email, and webhook
- **Data Logging**: SQLite database and CSV logging with duplicate prevention
- **Security**: Comprehensive input validation, rate limiting, and security measures
- **Historical Charts**: Interactive price history charts for any tracked asset
- **Automated Cleanup**: Automatic data cleanup to prevent database bloat

## Requirements

- Python 3.8+
- Internet connection for API access
- Modern web browser for dashboard

##  Installation

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd crypto-stock-tracker
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Access the dashboard**: Open http://localhost:5000 in your browser

### Advanced Installation

For production deployment, see [SECURITY.md](SECURITY.md) for security best practices.

##  Project Structure

```
crypto-stock-tracker/
├── main.py                 # Main application entry point
├── config.py              # Configuration settings
├── security_config.py     # Security utilities and validation
├── price_scraper.py      # API integration for price data
├── data_logger.py        # Database and CSV logging
├── alert_system.py       # Alert processing and notifications
├── dashboard.py          # Flask web dashboard
├── security_audit.py     # Security audit tool
├── test_integration.py   # Integration tests
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── dashboard.html    # Main dashboard template
│   └── error.html       # Error page template
├── database/            # SQLite database (auto-created)
├── logs/               # Log files (auto-created)
├── README.md           # This file
├── SECURITY.md         # Security documentation
├── QUICKSTART.md       # Quick start guide
└── .gitignore          # Git ignore rules
```

##  Configuration

### Basic Configuration

Edit `config.py` to customize:

- **Assets**: Add/remove crypto and stock symbols
- **Update Intervals**: Set how often to fetch prices
- **Alert Thresholds**: Configure price change alerts
- **Web Settings**: Dashboard host and port

### Environment Variables

Set these for enhanced security:

```bash
# Email alerts (optional)
export EMAIL_PASSWORD="your-email-password"

# Flask secret key (recommended)
export SECRET_KEY="your-secret-key-here"
```

## Usage

### Starting the Application

```bash
# Basic start
python main.py

# With custom configuration
python -c "import config; config.FLASK_PORT = 8080; import main; main.main()"
```

### Running Tests

```bash
# Run integration tests
python test_integration.py

# Run security audit
python security_audit.py
```

### Web Dashboard

- **Main Page**: http://localhost:5000
- **API Endpoints**:
  - `/api/prices` - Current prices
  - `/api/chart/<symbol>` - Historical data
  - `/api/alerts` - Alert statistics
  - `/api/stats` - System statistics

## Security Features

- **Input Validation**: All user inputs validated and sanitized
- **Rate Limiting**: API endpoints protected against abuse
- **SQL Injection Prevention**: Parameterized queries
- **Error Handling**: Secure error messages
- **File Permissions**: Secure file access controls
- **Environment Variables**: No hardcoded secrets

## Supported Assets

### Cryptocurrencies
- Bitcoin (BTC)
- Ethereum (ETH)
- Binance Coin (BNB)
- Cardano (ADA)
- Solana (SOL)
- Ripple (XRP)
- Polkadot (DOT)
- Dogecoin (DOGE)

### Stocks
- Apple (AAPL)
- Google (GOOGL)
- Microsoft (MSFT)
- Tesla (TSLA)
- Amazon (AMZN)
- NVIDIA (NVDA)
- Meta (META)
- Netflix (NFLX)

## Alert System

The application monitors price changes and sends alerts when:

- Price changes exceed the configured threshold (default: 5%)
- Alerts respect cooldown periods to prevent spam
- Multiple notification channels: terminal, email, webhook

## Data Management

- **Real-time Logging**: All price data logged to SQLite and CSV
- **Duplicate Prevention**: Prevents duplicate entries
- **Automatic Cleanup**: Removes old data to prevent bloat
- **Historical Analysis**: Access historical price data via API

##  Security Audit

Run the security audit to check for issues:

```bash
python security_audit.py
```

This checks:
- File permissions
- Configuration security
- Database security
- Dependency vulnerabilities
- Environment variables

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test_integration.py`
5. Run security audit: `python security_audit.py`
6. Submit a pull request

##  License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Disclaimer

This application is for educational and personal use. Cryptocurrency and stock trading involves risk. Always do your own research and consider consulting with financial advisors.

## Support

- **Issues**: Create an issue on GitHub
- **Security**: Report security issues privately
- **Documentation**: See [SECURITY.md](SECURITY.md) for security details

##  Updates

- **Dependencies**: Regularly update with `pip install -r requirements.txt --upgrade`
- **Security**: Run `python security_audit.py` regularly
- **Data**: Monitor database size and cleanup as needed

---

