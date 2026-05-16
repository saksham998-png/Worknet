import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-secret-key')
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///taskmanager.db')
    if db_url and db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Email (console fallback when SMTP not configured)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', '')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in {'1', 'true', 'yes'}
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'worknet@localhost')
    MAIL_ENABLED = bool(os.environ.get('MAIL_SERVER', ''))

    # Integrations
    SLACK_WEBHOOK_DEFAULT = os.environ.get('SLACK_WEBHOOK_URL', '')
    TEAMS_WEBHOOK_DEFAULT = os.environ.get('TEAMS_WEBHOOK_URL', '')

    @staticmethod
    def init_app(app):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
