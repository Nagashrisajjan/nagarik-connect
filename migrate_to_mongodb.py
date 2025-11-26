"""
Migration script to transfer data from MySQL to MongoDB Atlas
Run this script ONCE before deploying to migrate your existing data
"""

import mysql.connector
from pymongo import MongoClient
from datetime import datetime
from config import Config

def migrate_data():
    """Migrate data from MySQL to MongoDB"""
    
    print("🚀 Starting migration from MySQL to MongoDB Atlas...")
    
    # Connect to MySQL
    try:
        mysql_conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="updatedicgs"
        )
        mysql_cursor = mysql_conn.cursor(dictionary=True)
        print("✅ Connected to MySQL")
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return
    
    # Connect to MongoDB
    try:
        mongodb_uri = Config.get_mongodb_uri()
        mongo_client = MongoClient(mongodb_uri)
        mongo_db = mongo_client[Config.MONGODB_DATABASE]
        print("✅ Connected to MongoDB Atlas")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return
    
    # Migrate Users
    print("\n📦 Migrating users...")
    try:
        mysql_cursor.execute("SELECT * FROM users")
        users = mysql_cursor.fetchall()
        if users:
            # Convert id to string for MongoDB
            for user in users:
                user['_id'] = str(user.pop('id'))
                if 'created_at' in user and user['created_at']:
                    user['created_at'] = user['created_at'].isoformat() if isinstance(user['created_at'], datetime) else str(user['created_at'])
            mongo_db.users.insert_many(users)
            print(f"✅ Migrated {len(users)} users")
        else:
            print("⚠️  No users to migrate")
    except Exception as e:
        print(f"❌ Users migration error: {e}")
    
    # Migrate Complaints
    print("\n📦 Migrating complaints...")
    try:
        mysql_cursor.execute("SELECT * FROM complaints")
        complaints = mysql_cursor.fetchall()
        if complaints:
            for complaint in complaints:
                complaint['_id'] = str(complaint.pop('id'))
                complaint['user_id'] = str(complaint['user_id'])
                if 'created_at' in complaint and complaint['created_at']:
                    complaint['created_at'] = complaint['created_at'].isoformat() if isinstance(complaint['created_at'], datetime) else str(complaint['created_at'])
            mongo_db.complaints.insert_many(complaints)
            print(f"✅ Migrated {len(complaints)} complaints")
        else:
            print("⚠️  No complaints to migrate")
    except Exception as e:
        print(f"❌ Complaints migration error: {e}")
    
    # Migrate Workers
    print("\n📦 Migrating workers...")
    try:
        mysql_cursor.execute("SELECT * FROM workers")
        workers = mysql_cursor.fetchall()
        if workers:
            for worker in workers:
                worker['_id'] = str(worker.pop('id'))
                if 'created_at' in worker and worker['created_at']:
                    worker['created_at'] = worker['created_at'].isoformat() if isinstance(worker['created_at'], datetime) else str(worker['created_at'])
            mongo_db.workers.insert_many(workers)
            print(f"✅ Migrated {len(workers)} workers")
        else:
            print("⚠️  No workers to migrate")
    except Exception as e:
        print(f"❌ Workers migration error: {e}")
    
    # Migrate Department Admins
    print("\n📦 Migrating department admins...")
    try:
        mysql_cursor.execute("SELECT * FROM dept_admins")
        dept_admins = mysql_cursor.fetchall()
        if dept_admins:
            for admin in dept_admins:
                admin['_id'] = str(admin.pop('id'))
                if 'created_at' in admin and admin['created_at']:
                    admin['created_at'] = admin['created_at'].isoformat() if isinstance(admin['created_at'], datetime) else str(admin['created_at'])
            mongo_db.dept_admins.insert_many(dept_admins)
            print(f"✅ Migrated {len(dept_admins)} department admins")
        else:
            print("⚠️  No department admins to migrate")
    except Exception as e:
        print(f"❌ Department admins migration error: {e}")
    
    # Migrate Feedback
    print("\n📦 Migrating feedback...")
    try:
        mysql_cursor.execute("SELECT * FROM feedback")
        feedbacks = mysql_cursor.fetchall()
        if feedbacks:
            for feedback in feedbacks:
                feedback['_id'] = str(feedback.pop('id'))
                if 'created_at' in feedback and feedback['created_at']:
                    feedback['created_at'] = feedback['created_at'].isoformat() if isinstance(feedback['created_at'], datetime) else str(feedback['created_at'])
            mongo_db.feedback.insert_many(feedbacks)
            print(f"✅ Migrated {len(feedbacks)} feedback entries")
        else:
            print("⚠️  No feedback to migrate")
    except Exception as e:
        print(f"❌ Feedback migration error: {e}")
    
    # Close connections
    mysql_cursor.close()
    mysql_conn.close()
    mongo_client.close()
    
    print("\n🎉 Migration completed successfully!")
    print("\n⚠️  IMPORTANT: Update your .env file with MongoDB Atlas credentials before deploying")

if __name__ == "__main__":
    migrate_data()
