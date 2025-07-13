# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies
```bash
python install.py
```

### 2. Test the Application
```bash
python test_app.py
```

### 3. Start the Application
```bash
python main.py
```

Then open your browser to: **http://localhost:5000**

## 📋 What You Get

✅ **Real-time Price Tracking**
- Cryptocurrencies: Bitcoin, Ethereum, Binance Coin, Cardano, Solana, Ripple, Polkadot, Dogecoin
- Stocks: Apple, Google, Microsoft, Tesla, Amazon, NVIDIA, Meta, Netflix

✅ **Web Dashboard**
- Live price display with 24h changes
- Interactive historical charts
- System statistics and alerts

✅ **Data Storage**
- SQLite database for historical data
- CSV logging for easy export
- Duplicate prevention

✅ **Alert System**
- Configurable price change thresholds
- Terminal, email, and webhook alerts
- Cooldown periods to prevent spam

## ⚙️ Configuration

Edit `config.py` to customize:

- **Assets to track**: Add/remove crypto and stock symbols
- **Update intervals**: How often to fetch prices
- **Alert settings**: Thresholds and cooldown periods
- **Email/webhook**: Configure alert delivery

## 🔧 Troubleshooting

### Common Issues

**Import Errors**: Run `pip install -r requirements.txt`

**Port Already in Use**: Change `FLASK_PORT` in `config.py`

**No Data**: Check internet connection and API availability

**Alerts Not Working**: Verify email/webhook settings in `config.py`

## 📊 Features

### Price Scraper
- CoinGecko API for crypto prices (free, no API key)
- Yahoo Finance for stock prices
- Rate limiting and error handling

### Data Logger
- SQLite database with proper indexing
- CSV export for analysis
- Automatic duplicate prevention

### Alert System
- Real-time price monitoring
- Multiple alert channels
- Configurable thresholds

### Web Dashboard
- Modern, responsive UI
- Real-time price updates
- Interactive charts with Plotly
- System statistics

## 🎯 Next Steps

1. **Customize Assets**: Edit `config.py` to add your preferred cryptocurrencies and stocks
2. **Set Up Alerts**: Configure email or webhook settings for price alerts
3. **Monitor Performance**: Check the dashboard for system statistics
4. **Export Data**: Use the CSV logs for external analysis

## 📈 Advanced Usage

### API Endpoints
- `GET /api/prices` - Current prices
- `GET /api/chart/<symbol>` - Historical data
- `GET /api/alerts` - Alert statistics
- `POST /api/update_threshold` - Update alert threshold

### Database Schema
```sql
CREATE TABLE price_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    symbol TEXT NOT NULL,
    price REAL NOT NULL,
    change_24h REAL,
    asset_type TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Log Files
- Database: `database/price_data.db`
- CSV logs: `logs/price_logs.csv`
- Application logs: Console output

## 🤝 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify your internet connection
3. Ensure all dependencies are installed
4. Check the configuration settings

Happy tracking! 📊📈 