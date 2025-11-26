"""Test MongoDB Atlas connection"""
from pymongo import MongoClient
from config import Config

print("🔍 Testing MongoDB Atlas connection...")
print(f"Username: {Config.MONGODB_USERNAME}")
print(f"Cluster: {Config.MONGODB_CLUSTER}")
print(f"Database: {Config.MONGODB_DATABASE}")
print()

try:
    # Get MongoDB URI
    mongodb_uri = Config.get_mongodb_uri()
    print(f"Connecting to MongoDB Atlas...")
    
    # Connect with timeout
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    
    # Test connection
    client.server_info()
    
    print("✅ SUCCESS! Connected to MongoDB Atlas!")
    print()
    
    # Get database
    db = client[Config.MONGODB_DATABASE]
    
    # List collections
    collections = db.list_collection_names()
    if collections:
        print(f"📦 Existing collections in '{Config.MONGODB_DATABASE}':")
        for col in collections:
            count = db[col].count_documents({})
            print(f"   - {col}: {count} documents")
    else:
        print(f"📦 Database '{Config.MONGODB_DATABASE}' is empty (ready for migration)")
    
    client.close()
    print()
    print("🎉 MongoDB Atlas is ready!")
    print("Next step: Run 'python migrate_to_mongodb.py' to migrate your data")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print()
    print("🔧 Troubleshooting:")
    print("1. Check your password is correct in .env and config.py")
    print("2. Verify Network Access in MongoDB Atlas (should be 0.0.0.0/0)")
    print("3. Ensure cluster is active (not paused)")
    print("4. Wait 1-2 minutes and try again")
    print()
    print("💡 To reset password:")
    print("   - Go to https://cloud.mongodb.com")
    print("   - Database Access → Edit user 'root' → Edit Password")
