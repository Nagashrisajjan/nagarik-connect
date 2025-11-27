"""
Final conversion script - converts ALL remaining SQL to MongoDB
This is the last pass!
"""

import re

def finish_mongodb_conversion():
    print("🚀 Final MongoDB conversion pass...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove all remaining cursor/conn references
    content = re.sub(r'cursor\s*=\s*conn\.cursor\(dictionary=True\)', '', content)
    content = re.sub(r'conn\s*=\s*get_db_connection\(\)', 'db = get_db()', content)
    
    # Replace INSERT INTO complaints
    content = re.sub(
        r'cursor\.execute\(\s*"""INSERT INTO complaints.*?""",\s*\([^)]+\)\s*\)',
        '''result = db.complaints.insert_one({
            "user_id": session["user_id"],
            "user_name": session["name"],
            "title": title,
            "description": description,
            "department": department,
            "status": "Pending",
            "image": filename,
            "latitude": latitude,
            "longitude": longitude,
            "location": location_text,
            "created_at": datetime.now().isoformat(),
            "remarks": None,
            "admin_image": None,
            "assigned_worker_id": None
        })
        complaint_id = str(result.inserted_id)''',
        content,
        flags=re.DOTALL
    )
    
    # Replace UPDATE complaints SET status
    content = re.sub(
        r'cursor\.execute\(\s*"""UPDATE complaints\s+SET status\s*=\s*%s.*?WHERE id\s*=\s*%s""",\s*\([^)]+\)\s*\)',
        'db.complaints.update_one({"_id": ObjectId(complaint_id)}, {"$set": {"status": status}})',
        content,
        flags=re.DOTALL
    )
    
    # Replace SELECT * FROM workers WHERE id
    content = re.sub(
        r'cursor\.execute\("SELECT \* FROM workers WHERE id=%s",\s*\([^)]+\)\s*\)\s*worker\s*=\s*cursor\.fetchone\(\)',
        '''worker = db.workers.find_one({"_id": ObjectId(worker_id)})
        if worker:
            worker["id"] = str(worker["_id"])''',
        content
    )
    
    # Replace INSERT INTO workers
    content = re.sub(
        r'cursor\.execute\(\s*"""INSERT INTO workers.*?""",\s*\([^)]+\)\s*\)',
        '''result = db.workers.insert_one({
            "name": name,
            "phone": phone,
            "department": department,
            "created_at": datetime.now().isoformat()
        })
        worker_id = str(result.inserted_id)''',
        content,
        flags=re.DOTALL
    )
    
    # Replace cursor.lastrowid
    content = content.replace('cursor.lastrowid', 'worker_id')
    
    # Replace UPDATE complaints SET admin_image
    content = re.sub(
        r'cursor\.execute\(\s*"""UPDATE complaints\s+SET admin_image\s*=\s*%s.*?WHERE id\s*=\s*%s""",\s*\([^)]+\)\s*\)',
        'db.complaints.update_one({"_id": ObjectId(complaint_id)}, {"$set": {"admin_image": filename}})',
        content,
        flags=re.DOTALL
    )
    
    # Replace INSERT INTO feedback
    content = re.sub(
        r'cursor\.execute\(\s*"""INSERT INTO feedback.*?""",\s*\([^)]+\)\s*\)',
        '''db.feedback.insert_one({
            "name": name,
            "email": email,
            "message": message,
            "created_at": datetime.now().isoformat()
        })''',
        content,
        flags=re.DOTALL
    )
    
    # Replace SELECT * FROM feedback
    content = re.sub(
        r'cursor\.execute\("SELECT \* FROM feedback.*?ORDER BY.*?"\)\s*feedbacks\s*=\s*cursor\.fetchall\(\)',
        '''feedbacks = list(db.feedback.find().sort("created_at", -1))
        for f in feedbacks:
            f["id"] = str(f["_id"])''',
        content
    )
    
    # Remove any remaining db.commit() and db.close()
    content = content.replace('db.commit()', '')
    content = content.replace('db.close()', '')
    
    # Save
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Final conversion complete!")
    print("\n📝 Remaining manual fixes needed:")
    print("   - Complex UPDATE queries with multiple fields")
    print("   - Department admin routes")
    print("   - Any remaining cursor.execute statements")
    
    # Count remaining issues
    remaining = content.count('cursor.')
    print(f"\n⚠️  Remaining cursor references: {remaining}")
    
    if remaining == 0:
        print("\n🎉 ALL SQL CONVERTED TO MONGODB!")
    else:
        print(f"\n📍 Search for 'cursor.' to find remaining {remaining} references")

if __name__ == "__main__":
    finish_mongodb_conversion()
