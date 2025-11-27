"""
Automatic converter: MySQL app.py → MongoDB app.py
Run this to convert your app.py to use MongoDB instead of MySQL
"""

import re

def convert_mysql_to_mongodb(input_file='app.py', output_file='app_converted.py'):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove mysql import
    content = content.replace('import mysql.connector\n', '')
    
    # Add MongoDB imports if not present
    if 'from database import get_db' not in content:
        content = content.replace(
            'from flask import',
            'from database import get_db\nfrom bson import ObjectId\nfrom flask import'
        )
    
    # Replace get_db_connection() calls
    content = re.sub(
        r'conn = get_db_connection\(\)\s*cursor = conn\.cursor\(dictionary=True\)',
        'db = get_db()',
        content
    )
    
    # Replace SELECT COUNT queries
    content = re.sub(
        r'cursor\.execute\("SELECT COUNT\(\*\) AS (\w+) FROM complaints"\)\s*(\w+)_complaints = cursor\.fetchone\(\)\["(\w+)"\]',
        r'\2_complaints = db.complaints.count_documents({})',
        content
    )
    
    # Replace SELECT COUNT with WHERE
    content = re.sub(
        r'cursor\.execute\("SELECT COUNT\(\*\) AS (\w+) FROM complaints WHERE LOWER\(status\)=\'(\w+)\'"\)\s*(\w+)_complaints = cursor\.fetchone\(\)\["(\w+)"\]',
        r'\3_complaints = db.complaints.count_documents({"status": {"$regex": "\2", "$options": "i"}})',
        content
    )
    
    # Replace cursor.close() and conn.close()
    content = re.sub(r'\s*cursor\.close\(\)\s*conn\.close\(\)', '', content)
    
    # Replace SELECT * FROM users WHERE email
    content = re.sub(
        r'cursor\.execute\("SELECT \* FROM users WHERE email=%s", \((\w+),\)\)\s*(\w+) = cursor\.fetchone\(\)',
        r'\2 = db.users.find_one({"email": \1})\n        if \2:\n            \2["id"] = str(\2["_id"])',
        content
    )
    
    # Replace INSERT INTO users
    content = re.sub(
        r'cursor\.execute\(\s*"INSERT INTO users \(name, email, password, role\) VALUES \(%s, %s, %s, %s\)",\s*\((\w+), (\w+), (\w+), (\w+)\)\s*\)\s*conn\.commit\(\)',
        r'db.users.insert_one({"name": \1, "email": \2, "password": \3, "role": \4, "created_at": datetime.now().isoformat()})',
        content
    )
    
    # Save converted file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Converted {input_file} → {output_file}")
    print("⚠️  Manual review needed for complex queries!")
    print("📝 Check the output file and test before deploying")

if __name__ == "__main__":
    convert_mysql_to_mongodb()
    print("\n🎯 Next steps:")
    print("1. Review app_converted.py")
    print("2. Test locally: python app_converted.py")
    print("3. If works: mv app_converted.py app.py")
    print("4. Push to GitHub and redeploy on Render")
