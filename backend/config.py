import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-123-replace-in-prod')
    
    # Database Configuration
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///taskmanager.db')
    
    # Support for Railway's Postgres and MySQL URL formats
    if db_url:
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        elif db_url.startswith('mysql://'):
            db_url = db_url.replace('mysql://', 'mysql+pymysql://', 1)
            
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # App Settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    @staticmethod
    def init_app(app):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
