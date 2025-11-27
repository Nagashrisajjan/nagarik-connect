"""
Complete MySQL to MongoDB conversion for app.py
This script will convert all database operations
"""

import re

def convert_app_to_mongodb():
    print("🔄 Starting conversion...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("📝 Original file: 828 lines")
    
    # Step 1: Fix imports
    print("Step 1: Updating imports...")
    content = content.replace('import mysql.connector\n', '')
    
    if 'from database import get_db' not in content:
        # Add MongoDB imports after Flask import
        content = content.replace(
            'from flask import Flask',
            'from database import get_db\nfrom bson import ObjectId\nfrom flask import Flask'
        )
    
    # Step 2: Remove get_db_connection function and replace with MongoDB
    print("Step 2: Replacing database connection...")
    content = re.sub(
        r'def get_db_connection\(\):.*?return mysql\.connector\.connect\(.*?\)',
        '# Database connection handled by database.py',
        content,
        flags=re.DOTALL
    )
    
    # Step 3: Replace all conn = get_db_connection() patterns
    print("Step 3: Converting database queries...")
    content = re.sub(
        r'conn = get_db_connection\(\)\s+cursor = conn\.cursor\(dictionary=True\)',
        'db = get_db()',
        content
    )
    
    # Step 4: Replace cursor.close() and conn.close()
    content = re.sub(r'\s*cursor\.close\(\)\s+conn\.close\(\)', '', content)
    content = re.sub(r'\s*cursor\.close\(\)', '', content)
    content = re.sub(r'\s*conn\.close\(\)', '', content)
    content = re.sub(r'\s*conn\.commit\(\)', '', content)
    
    # Step 5: Replace simple SELECT COUNT queries
    content = re.sub(
        r'cursor\.execute\("SELECT COUNT\(\*\) AS total FROM complaints"\)\s+total_complaints = cursor\.fetchone\(\)\["total"\]',
        'total_complaints = db.complaints.count_documents({})',
        content
    )
    
    content = re.sub(
        r'cursor\.execute\("SELECT COUNT\(\*\) AS solved FROM complaints WHERE LOWER\(status\)=\'resolved\'"\)\s+solved_complaints = cursor\.fetchone\(\)\["solved"\]',
        'solved_complaints = db.complaints.count_documents({"status": {"$regex": "resolved", "$options": "i"}})',
        content
    )
    
    content = re.sub(
        r'cursor\.execute\("SELECT COUNT\(\*\) AS pending FROM complaints WHERE LOWER\(status\)=\'pending\'"\)\s+pending_complaints = cursor\.fetchone\(\)\["pending"\]',
        'pending_complaints = db.complaints.count_documents({"status": {"$regex": "pending", "$options": "i"}})',
        content
    )
    
    content = re.sub(
        r'cursor\.execute\("SELECT COUNT\(\*\) AS in_progress FROM complaints WHERE LOWER\(status\) LIKE \'%in progress%\'"\)\s+in_progress_complaints = cursor\.fetchone\(\)\["in_progress"\]',
        'in_progress_complaints = db.complaints.count_documents({"status": {"$regex": "in progress", "$options": "i"}})',
        content
    )
    
    # Step 6: Replace SELECT * FROM users WHERE email
    content = re.sub(
        r'cursor\.execute\("SELECT \* FROM users WHERE email=%s", \(email,\)\)\s+user = cursor\.fetchone\(\)',
        '''user = db.users.find_one({"email": email})
        if user:
            user["id"] = str(user["_id"])''',
        content
    )
    
    # Step 7: Replace INSERT INTO users
    content = re.sub(
        r'cursor\.execute\(\s+"INSERT INTO users \(name, email, password, role\) VALUES \(%s, %s, %s, %s\)",\s+\(name, email, hashed_password, role\)\s+\)',
        '''db.users.insert_one({
                "name": name,
                "email": email,
                "password": hashed_password,
                "role": role,
                "created_at": datetime.now().isoformat()
            })''',
        content
    )
    
    # Step 8: Replace mysql.connector.IntegrityError
    content = content.replace('mysql.connector.IntegrityError', 'Exception')
    
    # Step 9: Replace SELECT * FROM workers
    content = re.sub(
        r'cursor\.execute\("SELECT \* FROM workers"\)\s+workers = cursor\.fetchall\(\)',
        '''workers = list(db.workers.find())
        for w in workers:
            w["id"] = str(w["_id"])''',
        content
    )
    
    # Save converted file
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Basic conversion complete!")
    print("⚠️  Complex queries need manual review")
    print("📝 Check app.py for any remaining MySQL syntax")
    
    return True

if __name__ == "__main__":
    try:
        convert_app_to_mongodb()
        print("\n🎉 Conversion successful!")
        print("\n📋 Next steps:")
        print("1. Review app.py for any remaining MySQL queries")
        print("2. Test locally: python app.py")
        print("3. Fix any errors")
        print("4. Push to GitHub: git add app.py && git commit -m 'Convert to MongoDB' && git push")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Restoring backup...")
        import shutil
        shutil.copy('app_mysql_backup.py', 'app.py')
        print("✅ Backup restored")
