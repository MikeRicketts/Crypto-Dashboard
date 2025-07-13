"""
Flask Web Dashboard
Provides real-time price display and historical charts
"""

from flask import Flask, render_template, jsonify, request, abort
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from functools import wraps
import config
from price_scraper import price_scraper
from data_logger import data_logger
from alert_system import alert_system

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Simple rate limiting
request_counts = {}

def rate_limit(f):
    """Rate limiting decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not config.INPUT_VALIDATION_ENABLED:
            return f(*args, **kwargs)
            
        client_ip = request.remote_addr
        current_time = datetime.now()
        
        # Clean old entries
        request_counts.clear()
        
        if client_ip not in request_counts:
            request_counts[client_ip] = {'count': 0, 'reset_time': current_time + timedelta(minutes=1)}
        
        if current_time > request_counts[client_ip]['reset_time']:
            request_counts[client_ip] = {'count': 0, 'reset_time': current_time + timedelta(minutes=1)}
        
        request_counts[client_ip]['count'] += 1
        
        if request_counts[client_ip]['count'] > config.MAX_REQUESTS_PER_MINUTE:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        return f(*args, **kwargs)
    return decorated_function

def validate_symbol(symbol: str) -> bool:
    """Validate asset symbol"""
    if not symbol or not isinstance(symbol, str):
        return False
    
    # Check if symbol exists in configured assets
    all_symbols = config.CRYPTO_ASSETS + config.STOCK_ASSETS
    return symbol.lower() in [s.lower() for s in all_symbols]

def validate_numeric_input(value: any, min_val: Optional[float] = None, max_val: Optional[float] = None) -> Optional[float]:
    """Validate and convert numeric input"""
    try:
        num_val = float(value)
        if min_val is not None and num_val < min_val:
            return None
        if max_val is not None and num_val > max_val:
            return None
        return num_val
    except (ValueError, TypeError):
        return None

@app.route('/')
@rate_limit
def index():
    """Main dashboard page"""
    try:
        # Get current prices
        current_prices = price_scraper.get_all_prices()
        
        # Get latest logged prices
        latest_prices = data_logger.get_latest_prices(20)
        
        # Get alert stats
        alert_stats = alert_system.get_alert_stats()
        
        # Get summary stats
        summary_stats = data_logger.get_summary_stats()
        
        return render_template('dashboard.html',
                             current_prices=current_prices,
                             latest_prices=latest_prices.to_dict('records') if not latest_prices.empty else [],
                             alert_stats=alert_stats,
                             summary_stats=summary_stats)
                             
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return render_template('error.html', error="An error occurred while loading the dashboard")

@app.route('/api/prices')
@rate_limit
def api_prices():
    """API endpoint for current prices"""
    try:
        prices = price_scraper.get_all_prices()
        return jsonify({
            'success': True,
            'data': prices,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching prices: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch prices'
        }), 500

@app.route('/api/chart/<symbol>')
@rate_limit
def api_chart(symbol):
    """API endpoint for historical chart data"""
    try:
        # Validate symbol
        if not validate_symbol(symbol):
            return jsonify({
                'success': False,
                'error': 'Invalid symbol'
            }), 400
        
        # Validate hours parameter
        hours_raw = request.args.get('hours', config.CHART_HISTORY_HOURS, type=int)
        hours = validate_numeric_input(hours_raw, 1, 168)  # 1 hour to 1 week
        if hours is None:
            hours = config.CHART_HISTORY_HOURS
        
        history = data_logger.get_asset_history(symbol, int(hours))
        
        if history.empty:
            return jsonify({
                'success': False,
                'error': 'No historical data available'
            }), 404
        
        # Create chart data
        chart_data = {
            'x': history['timestamp'].tolist(),
            'y': history['price'].tolist(),
            'name': symbol.upper(),
            'type': 'scatter',
            'mode': 'lines+markers',
            'line': {'color': '#1f77b4'}
        }
        
        return jsonify({
            'success': True,
            'data': chart_data,
            'symbol': symbol.upper()
        })
        
    except Exception as e:
        logger.error(f"Error fetching chart data for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch chart data'
        }), 500

@app.route('/api/alerts')
@rate_limit
def api_alerts():
    """API endpoint for alert statistics"""
    try:
        alert_stats = alert_system.get_alert_stats()
        return jsonify({
            'success': True,
            'data': alert_stats
        })
    except Exception as e:
        logger.error(f"Error fetching alert stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch alert statistics'
        }), 500

@app.route('/api/stats')
@rate_limit
def api_stats():
    """API endpoint for system statistics"""
    try:
        summary_stats = data_logger.get_summary_stats()
        return jsonify({
            'success': True,
            'data': summary_stats
        })
    except Exception as e:
        logger.error(f"Error fetching system stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch system statistics'
        }), 500

@app.route('/api/update_threshold', methods=['POST'])
@rate_limit
def api_update_threshold():
    """API endpoint to update alert threshold"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid request data'
            }), 400
        
        new_threshold = data.get('threshold')
        threshold = validate_numeric_input(new_threshold, config.MIN_THRESHOLD, config.MAX_THRESHOLD)
        
        if threshold is None:
            return jsonify({
                'success': False,
                'error': 'Invalid threshold value (must be between 0.1 and 100.0)'
            }), 400
        
        alert_system.update_threshold(threshold)
        
        return jsonify({
            'success': True,
            'message': f'Threshold updated to {threshold}%'
        })
        
    except Exception as e:
        logger.error(f"Error updating threshold: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update threshold'
        }), 500

@app.route('/api/update_cooldown', methods=['POST'])
@rate_limit
def api_update_cooldown():
    """API endpoint to update alert cooldown"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid request data'
            }), 400
        
        new_cooldown = data.get('cooldown')
        cooldown = validate_numeric_input(new_cooldown, config.MIN_COOLDOWN, config.MAX_COOLDOWN)
        
        if cooldown is None:
            return jsonify({
                'success': False,
                'error': 'Invalid cooldown value (must be between 60 and 3600 seconds)'
            }), 400
        
        alert_system.update_cooldown(int(cooldown))
        
        return jsonify({
            'success': True,
            'message': f'Cooldown updated to {int(cooldown)} seconds'
        })
        
    except Exception as e:
        logger.error(f"Error updating cooldown: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update cooldown'
        }), 500

@app.route('/api/cleanup', methods=['POST'])
@rate_limit
def api_cleanup():
    """API endpoint to cleanup old data"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid request data'
            }), 400
        
        days = data.get('days', 30)
        days = validate_numeric_input(days, config.MIN_CLEANUP_DAYS, config.MAX_CLEANUP_DAYS_INPUT)
        
        if days is None:
            return jsonify({
                'success': False,
                'error': 'Invalid days value (must be between 1 and 365)'
            }), 400
        
        data_logger.cleanup_old_data(int(days))
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up data older than {int(days)} days'
        })
        
    except Exception as e:
        logger.error(f"Error cleaning up data: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to cleanup data'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Internal server error'), 500

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

if __name__ == '__main__':
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    ) 