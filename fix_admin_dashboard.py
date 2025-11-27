#!/usr/bin/env python3
"""
Quick fix script for the 500 error in admin dashboard
This script will patch the admin_dashboard function in app.py
"""

import re

print("=" * 60)
print("  Fixing Admin Dashboard 500 Error")
print("=" * 60)
print()

# Read the current app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The problematic pattern (MongoDB aggregation)
old_pattern = r'''    # Fetch all complaints with user and worker info using MongoDB aggregation
    complaints = list\(db\.complaints\.aggregate\(\[[\s\S]*?\]\)\)\)

    # Fetch all workers
    all_workers = list\(db\.workers\.find\(\)\)
    # SQLite already has 'id' field

    # ✅ Complaint statistics
    total = db\.complaints\.count_documents\(\{\}\)

    pending = db\.complaints\.count_documents\(\{"status": "Pending"\}\)

    in_progress = db\.complaints\.count_documents\(\{"status": "In Progress"\}\)

    resolved = db\.complaints\.count_documents\(\{"status": "Resolved"\}\)

    # Fetch department-wise complaint counts using MongoDB aggregation
    dept_data = list\(db\.complaints\.aggregate\(\[
        \{"\$group": \{"_id": "\$department", "count": \{"\$sum": 1\}\}\},
        \{"\$sort": \{"count": -1\}\}
    \]\)\)
    
    dept_labels = \[d\["_id"\] for d in dept_data\]
    dept_counts = \[d\["count"\] for d in dept_data\]

    # ✅ Format timestamps
    for c in complaints:
        if isinstance\(c\.get\("created_at"\), datetime\):
            c\["created_at"\] = c\["created_at"\]\.strftime\("%Y-%m-%d %H:%M"\)'''

# The fixed version (SQLite compatible)
new_code = '''    # Fetch all complaints (simplified for SQLite)
    complaints = list(db.complaints.find())
    
    # Manually join with users and workers
    for complaint in complaints:
        # Get user info
        if complaint.get("user_id"):
            try:
                user_id = int(complaint["user_id"]) if str(complaint["user_id"]).isdigit() else None
                if user_id:
                    user = db.users.find_one({"id": user_id})
                    if user:
                        complaint["user_name"] = user.get("name")
            except (ValueError, TypeError, AttributeError):
                pass
        
        # Get worker info
        if complaint.get("assigned_worker_id"):
            try:
                worker_id = int(complaint["assigned_worker_id"])
                worker = db.workers.find_one({"id": worker_id})
                if worker:
                    complaint["assigned_worker_name"] = worker.get("name")
                    complaint["assigned_worker_phone"] = worker.get("phone")
                    complaint["worker_department"] = worker.get("department")
            except (ValueError, TypeError):
                pass
    
    # Sort by created_at (newest first)
    complaints.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    # Fetch all workers
    all_workers = list(db.workers.find())

    # Complaint statistics
    total = db.complaints.count_documents({})
    pending = db.complaints.count_documents({"status": "Pending"})
    in_progress = db.complaints.count_documents({"status": "In Progress"})
    resolved = db.complaints.count_documents({"status": "Resolved"})

    # Department-wise complaint counts (manual grouping for SQLite)
    all_complaints = db.complaints.find()
    dept_counts_dict = {}
    for c in all_complaints:
        dept = c.get("department", "Unknown")
        dept_counts_dict[dept] = dept_counts_dict.get(dept, 0) + 1
    
    # Sort by count
    dept_items = sorted(dept_counts_dict.items(), key=lambda x: x[1], reverse=True)
    dept_labels = [item[0] for item in dept_items]
    dept_counts = [item[1] for item in dept_items]

    # Format timestamps
    for c in complaints:
        if c.get("created_at"):
            try:
                if isinstance(c["created_at"], str):
                    c["created_at"] = datetime.fromisoformat(c["created_at"]).strftime("%Y-%m-%d %H:%M")
                elif isinstance(c["created_at"], datetime):
                    c["created_at"] = c["created_at"].strftime("%Y-%m-%d %H:%M")
            except:
                pass'''

# Try to replace
if re.search(old_pattern, content):
    new_content = re.sub(old_pattern, new_code, content)
    
    # Backup original
    with open('app.py.backup', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Created backup: app.py.backup")
    
    # Write fixed version
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✓ Fixed admin_dashboard function in app.py")
    print()
    print("=" * 60)
    print("  Fix Applied Successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Restart your Flask server")
    print("2. Try logging in as admin again")
    print("3. The 500 error should be resolved")
    print()
else:
    print("⚠ Could not find the exact pattern to replace.")
    print("  The code may have already been modified.")
    print()
    print("Manual fix required:")
    print("1. Open app.py")
    print("2. Find the admin_dashboard function (around line 246)")
    print("3. Replace the MongoDB aggregation code with the fixed version")
    print("4. See admin_dashboard_fix.py for the complete fixed function")
    print()
