#!/usr/bin/env python3
"""
Script to create department admin accounts in SQLite database
Run this to set up department admins
"""
from database_sqlite import get_db
from werkzeug.security import generate_password_hash

def setup_department_admins():
    db = get_db()
    
    # Department admin accounts
    dept_admins = [
        {
            'username': 'water_admin',
            'password': 'water123',
            'department': 'Water Crisis',
            'name': 'Water Department Admin'
        },
        {
            'username': 'road_admin',
            'password': 'road123',
            'department': 'Road Maintenance(Engg)',
            'name': 'Road Department Admin'
        },
        {
            'username': 'garbage_admin',
            'password': 'garbage123',
            'department': 'Solid Waste (Garbage) Related',
            'name': 'Garbage Department Admin'
        },
        {
            'username': 'electrical_admin',
            'password': 'electrical123',
            'department': 'Electrical',
            'name': 'Electrical Department Admin'
        },
        {
            'username': 'general_admin',
            'password': 'general123',
            'department': 'General Department',
            'name': 'General Department Admin'
        }
    ]
    
    print("="*70)
    print("  Setting Up Department Admin Accounts")
    print("="*70)
    print()
    
    # Insert department admins
    for admin in dept_admins:
        hashed_password = generate_password_hash(admin['password'])
        
        # Check if already exists
        existing = db.dept_admins.find_one({"username": admin['username']})
        
        if existing:
            print(f"⚠️  Already exists: {admin['username']} - {admin['department']}")
        else:
            try:
                db.dept_admins.insert_one({
                    'username': admin['username'],
                    'password': hashed_password,
                    'department': admin['department'],
                    'name': admin['name']
                })
                print(f"✅ Created: {admin['username']} - {admin['department']}")
            except Exception as e:
                print(f"❌ Error creating {admin['username']}: {e}")
    
    print()
    print("="*70)
    print("  Department Admin Accounts Setup Complete!")
    print("="*70)
    print()
    print("📋 LOGIN CREDENTIALS:")
    print("="*70)
    print()
    
    for admin in dept_admins:
        print(f"🏢 Department: {admin['department']}")
        print(f"   Username:   {admin['username']}")
        print(f"   Password:   {admin['password']}")
        print(f"   Login URL:  http://localhost:5000/dept_admin/login")
        print("-" * 70)
    
    print()
    print("💡 TIP: Use these credentials to login to department-specific dashboards")
    print()

if __name__ == "__main__":
    setup_department_admins()
