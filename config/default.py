
import os
from datetime import timedelta

class Config:
    # Get the project root directory (two levels up from config/)
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_community_app_secret_key_123')
    # Use absolute path for database to avoid issues
    DATABASE_PATH = os.getenv('DATABASE_PATH', os.path.join(PROJECT_ROOT, 'community_helper.db'))
    DB_MAX_CONNECTIONS = int(os.getenv('DB_MAX_CONNECTIONS', '10'))
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'app', 'static', 'uploads')
    
    # Firebase settings (if needed, loading from env or check logic)
    FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
    FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN')
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
    FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')
    FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID')
    FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID')