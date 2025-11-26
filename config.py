import os
from urllib.parse import quote_plus

class Config:
    """Application configuration"""
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super_secret_key_change_in_production')
    
    # MongoDB Atlas Configuration
    MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME', 'root')
    MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD', '2004')  # ← REPLACE <db_password> with your actual password
    MONGODB_CLUSTER = os.environ.get('MONGODB_CLUSTER', 'cluster0.fmpvhuj.mongodb.net')
    MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE', 'icgs_complaints')
    
    # Build MongoDB URI
    @staticmethod
    def get_mongodb_uri():
        username = quote_plus(Config.MONGODB_USERNAME)
        password = quote_plus(Config.MONGODB_PASSWORD)
        return f"mongodb+srv://{username}:{password}@{Config.MONGODB_CLUSTER}/{Config.MONGODB_DATABASE}?retryWrites=true&w=majority"
    
    # Upload folder
    UPLOAD_FOLDER = "static/uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Babel configuration
    BABEL_DEFAULT_LOCALE = 'en'
    LANGUAGES = ['en', 'kn', 'hi', 'te', 'ta']
