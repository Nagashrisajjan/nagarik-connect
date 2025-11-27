#!/usr/bin/env python3
"""
Fix all MongoDB aggregation calls in app.py
Replace with SQLite-compatible code
"""

import re

print("="*80)
print("  FIXING ALL DATABASE AGGREGATIONS")
print("="*80)
print()

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open('app.py.backup_aggregation', 'w', encoding='utf-8') as f:
    f.write(content)
print("✅ Created backup: app.py.backup_aggregation")
print()

fixes_applied = []

# Fix 1: User Dashboard - Remove complex aggregation
print("🔧 Fix 1: User Dashboard aggregation...")
old_user_dashboard = r'''    # MongoDB aggregation to join complaints with workers and users
    complaints = list\(db\.complaints\.aggregate\(\[
        \{"\\$match": \{"user_id": user_id\}\},
        \{"\\$lookup": \{[^}]+\}\},
        \{"\\$unwind": \{[^}]+\}\},
        \{"\\$addFields": \{[^}]+\}\},
        \{"\\$sort": \{"created_at": -1\}\}
    \]\)\)'''

new_user_dashboard = '''    # Fetch user complaints (simplified for SQLite)
    complaints = list(db.complaints.find({"user_id": user_id}))
    
    # Manually add worker info
    for complaint in complaints:
        if complaint.get("assigned_worker_id"):
            try:
                worker = db.workers.find_one({"id": int(complaint["assigned_worker_id"])})
                if worker:
                    complaint["assigned_worker_name"] = worker.get("name")
                    complaint["assigned_worker_phone"] = worker.get("phone")
            except (ValueError, TypeError):
                pass
    
    # Sort by created_at
    complaints.sort(key=lambda x: x.get("created_at", ""), reverse=True)'''

if re.search(old_user_dashboard, content, re.DOTALL):
    content = re.sub(old_user_dashboard, new_user_dashboard, content, flags=re.DOTALL)
    fixes_applied.append("User Dashboard")
    print("   ✅ Fixed")
else:
    print("   ⏭️  Already fixed or pattern not found")

# Fix 2: Department Dashboard
print("🔧 Fix 2: Department Dashboard aggregation...")
old_dept_dashboard = r'''    # Fetch complaints for this department with user info
    complaints = list\(db\.complaints\.aggregate\(\[
        \{"\\$match": \{"department": dept_name\}\},
        \{"\\$lookup": \{[^}]+\}\},
        \{"\\$unwind": \{[^}]+\}\},
        \{"\\$addFields": \{[^}]+\}\},
        \{"\\$sort": \{"created_at": -1\}\}
    \]\)\)'''

new_dept_dashboard = '''    # Fetch complaints for this department (simplified for SQLite)
    complaints = list(db.complaints.find({"department": dept_name}))
    
    # Manually add user info
    for complaint in complaints:
        if complaint.get("user_id"):
            try:
                user_id = int(complaint["user_id"]) if str(complaint["user_id"]).isdigit() else None
                if user_id:
                    user = db.users.find_one({"id": user_id})
                    if user:
                        complaint["user_name"] = user.get("name")
            except (ValueError, TypeError):
                pass
    
    # Sort by created_at
    complaints.sort(key=lambda x: x.get("created_at", ""), reverse=True)'''

if re.search(old_dept_dashboard, content, re.DOTALL):
    content = re.sub(old_dept_dashboard, new_dept_dashboard, content, flags=re.DOTALL)
    fixes_applied.append("Department Dashboard")
    print("   ✅ Fixed")
else:
    print("   ⏭️  Already fixed or pattern not found")

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print()
print("="*80)
print(f"  FIXES APPLIED: {len(fixes_applied)}")
print("="*80)
for fix in fixes_applied:
    print(f"  ✅ {fix}")
print()
print("⚠️  Note: Some complex aggregations may need manual review")
print("   Check feedback and dept_admin_dashboard sections")
print()
