from pymongo import MongoClient
from config import Config
from datetime import datetime
import os
import ssl
import certifi

class Database:
    """MongoDB Database Handler"""
    
    def __init__(self):
        self.client = None
        self.db = None
        
    def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            mongodb_uri = Config.get_mongodb_uri()
            
            # Try multiple SSL configurations for Windows compatibility
            connection_configs = [
                # Config 1: Use certifi CA bundle
                {
                    'serverSelectionTimeoutMS': 5000,
                    'tlsCAFile': certifi.where()
                },
                # Config 2: Disable certificate verification (dev only)
                {
                    'serverSelectionTimeoutMS': 5000,
                    'tlsAllowInvalidCertificates': True,
                    'tlsAllowInvalidHostnames': True
                },
                # Config 3: Use system SSL context
                {
                    'serverSelectionTimeoutMS': 5000,
                    'ssl': True,
                    'ssl_cert_reqs': ssl.CERT_NONE
                }
            ]
            
            last_error = None
            for config in connection_configs:
                try:
                    self.client = MongoClient(mongodb_uri, **config)
                    self.client.server_info()  # Test connection
                    self.db = self.client[Config.MONGODB_DATABASE]
                    print("✅ Connected to MongoDB Atlas successfully!")
                    return True
                except Exception as e:
                    last_error = e
                    continue
            
            # If all configs failed
            print(f"❌ MongoDB connection error: {last_error}")
            return False
            
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            return False
    
    def get_collection(self, collection_name):
        """Get a collection from the database"""
        if self.db is None:
            self.connect()
        return self.db[collection_name]
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()

# Global database instance
db_instance = Database()

def get_db():
    """Get database instance"""
    if db_instance.db is None:
        db_instance.connect()
    return db_instance.db

# Collection helpers
def get_users_collection():
    return get_db()['users']

def get_complaints_collection():
    return get_db()['complaints']

def get_workers_collection():
    return get_db()['workers']

def get_dept_admins_collection():
    return get_db()['dept_admins']

def get_feedback_collection():
    return get_db()['feedback']
