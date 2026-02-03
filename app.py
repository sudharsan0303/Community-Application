from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from dotenv import load_dotenv
from datetime import timedelta
from flask_wtf.csrf import CSRFProtect
from models.database import init_db_pool, init_db
from controllers.user_controller import user_bp
from controllers.helper_controller import helper_bp
from controllers.admin_controller import admin_bp
from controllers.feedback_controller import feedback_bp
from controllers.auth_controller import auth_bp
from rate_limiter import limiter
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure app
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'dev_community_app_secret_key_123'),
    DATABASE_PATH=os.getenv('DATABASE_PATH', 'community_helper.db'),
    DB_MAX_CONNECTIONS=int(os.getenv('DB_MAX_CONNECTIONS', '10')),
    DEBUG=os.getenv('FLASK_ENV') == 'development',
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=1),
    UPLOAD_FOLDER=os.path.join(os.path.dirname(__file__), 'static/uploads')
)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Setup rate limiter
limiter.init_app(app)

# Initialize database
init_db()

# Initialize database pool
init_db_pool(app)

# Register blueprints and ensure proper URL prefixes
auth_bp.url_prefix = '/auth'  # Explicitly set URL prefix
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(helper_bp, url_prefix='/helper')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(feedback_bp, url_prefix='/feedback')

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(429)
def ratelimit_error(error):
    return render_template('errors/429.html'), 429

# Logout is handled by auth_controller

@app.route('/')
@limiter.exempt
def index():
    if 'user_type' in session:
        if session['user_type'] == 'user':
            return redirect(url_for('user.dashboard'))
        elif session['user_type'] == 'helper':
            return redirect(url_for('helper.dashboard'))
        elif session['user_type'] == 'admin':
            return redirect(url_for('admin.dashboard'))
    return render_template('index.html')

# Root route is already defined above

@app.route('/about')
@limiter.exempt
def about():
    return render_template('about.html')

@app.route('/contact')
@limiter.exempt
def contact():
    return render_template('contact.html')

# Login route is already defined above

# Removed the incorrect usage of limiter.exempt_when

if __name__ == '__main__':
    app.run(debug=True)