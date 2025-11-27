#!/usr/bin/env python3
"""
Complete Database Check and Fix Script
Verifies all tables and connections
"""

from database_sqlite import get_db, init_db
from werkzeug.security import generate_password_hash
import sqlite3

print("="*80)
print("  COMPLETE DATABASE CHECK & FIX")
print("="*80)
print()

# Initialize database
print("🔧 Initializing database...")
init_db()
print()

db = get_db()

# Check all tables
tables = ['users', 'complaints', 'workers', 'dept_admins', 'feedback']

print("📊 Checking all tables...")
print("-"*80)

for table in tables:
    try:
        if table == 'users':
            count = db.users.count_documents({})
        elif table == 'complaints':
            count = db.complaints.count_documents({})
        elif table == 'workers':
            count = db.workers.count_documents({})
        elif table == 'dept_admins':
            count = db.dept_admins.count_documents({})
        elif table == 'feedback':
            count = db.feedback.count_documents({})
        
        print(f"✅ {table:20} - {count} records")
    except Exception as e:
        print(f"❌ {table:20} - Error: {e}")

print("-"*80)
print()

# Add sample data if needed
print("🔧 Setting up sample data...")
print()

# 1. Add department admins if not exist
print("1️⃣  Department Admins...")
dept_admins = [
    {'username': 'water_admin', 'password': 'water123', 'department': 'Water Crisis', 'name': 'Water Department Admin'},
    {'username': 'road_admin', 'password': 'road123', 'department': 'Road Maintenance(Engg)', 'name': 'Road Department Admin'},
    {'username': 'garbage_admin', 'password': 'garbage123', 'department': 'Solid Waste (Garbage) Related', 'name': 'Garbage Department Admin'},
    {'username': 'electrical_admin', 'password': 'electrical123', 'department': 'Electrical', 'name': 'Electrical Department Admin'},
    {'username': 'general_admin', 'password': 'general123', 'department': 'General Department', 'name': 'General Department Admin'}
]

for admin in dept_admins:
    existing = db.dept_admins.find_one({"username": admin['username']})
    if not existing:
        hashed_password = generate_password_hash(admin['password'])
        db.dept_admins.insert_one({
            'username': admin['username'],
            'password': hashed_password,
            'department': admin['department'],
            'name': admin['name']
        })
        print(f"   ✅ Created: {admin['username']}")
    else:
        print(f"   ⏭️  Exists: {admin['username']}")

print()

# 2. Add sample workers if not exist
print("2️⃣  Sample Workers...")
sample_workers = [
    {'name': 'Rajesh Kumar', 'phone': '9876543210', 'department': 'Water Crisis'},
    {'name': 'Priya Sharma', 'phone': '9876543211', 'department': 'Water Crisis'},
    {'name': 'Amit Patel', 'phone': '9876543212', 'department': 'Road Maintenance(Engg)'},
    {'name': 'Sunita Reddy', 'phone': '9876543213', 'department': 'Road Maintenance(Engg)'},
    {'name': 'Vijay Singh', 'phone': '9876543214', 'department': 'Solid Waste (Garbage) Related'},
    {'name': 'Lakshmi Iyer', 'phone': '9876543215', 'department': 'Solid Waste (Garbage) Related'},
    {'name': 'Ravi Verma', 'phone': '9876543216', 'department': 'Electrical'},
    {'name': 'Anjali Desai', 'phone': '9876543217', 'department': 'Electrical'},
    {'name': 'Suresh Nair', 'phone': '9876543218', 'department': 'General Department'},
    {'name': 'Meena Gupta', 'phone': '9876543219', 'department': 'General Department'}
]

existing_workers = db.workers.count_documents({})
if existing_workers == 0:
    for worker in sample_workers:
        db.workers.insert_one(worker)
        print(f"   ✅ Created worker: {worker['name']} ({worker['department']})")
else:
    print(f"   ⏭️  {existing_workers} workers already exist")

print()

# 3. Add sample user if not exist
print("3️⃣  Sample Test User...")
test_user = db.users.find_one({"email": "test@example.com"})
if not test_user:
    hashed_password = generate_password_hash("test123")
    db.users.insert_one({
        'name': 'Test User',
        'email': 'test@example.com',
        'password': hashed_password,
        'role': 'citizen'
    })
    print("   ✅ Created test user: test@example.com / test123")
else:
    print("   ⏭️  Test user already exists")

print()

# Final verification
print("="*80)
print("  FINAL DATABASE STATUS")
print("="*80)
print()

for table in tables:
    try:
        if table == 'users':
            count = db.users.count_documents({})
        elif table == 'complaints':
            count = db.complaints.count_documents({})
        elif table == 'workers':
            count = db.workers.count_documents({})
        elif table == 'dept_admins':
            count = db.dept_admins.count_documents({})
        elif table == 'feedback':
            count = db.feedback.count_documents({})
        
        status = "✅" if count > 0 else "⚠️ "
        print(f"{status} {table:20} - {count} records")
    except Exception as e:
        print(f"❌ {table:20} - Error: {e}")

print()
print("="*80)
print("  DATABASE SETUP COMPLETE!")
print("="*80)
print()
print("📋 Quick Reference:")
print("-"*80)
print("Super Admin:     admin / admin@123")
print("Test User:       test@example.com / test123")
print("Water Admin:     water_admin / water123")
print("Road Admin:      road_admin / road123")
print("Garbage Admin:   garbage_admin / garbage123")
print("Electrical Admin: electrical_admin / electrical123")
print("General Admin:   general_admin / general123")
print("-"*80)
print()
