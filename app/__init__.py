
from flask import Flask, render_template, redirect, url_for, session
from flask_wtf.csrf import CSRFProtect
from .models.database import init_db_pool, init_db
from .rate_limiter import limiter
from config.default import Config
import logging
import os

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_class)
    
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
    # Note: init_db() might rely on global path, we should ideally pass config or app
    # Ensuring database exists
    with app.app_context():
         init_db()
         init_db_pool(app)

    # Register blueprints
    from .controllers.auth_controller import auth_bp
    from .controllers.user_controller import user_bp
    from .controllers.helper_controller import helper_bp
    from .controllers.admin_controller import admin_bp
    from .controllers.feedback_controller import feedback_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
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

    # Global routes
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

    @app.route('/about')
    @limiter.exempt
    def about():
        return render_template('about.html')

    @app.route('/contact')
    @limiter.exempt
    def contact():
        return render_template('contact.html')

    return app
