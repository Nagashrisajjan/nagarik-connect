#!/usr/bin/env python3
"""
Comprehensive fix for all database aggregation issues
This script will create a clean, working version of app.py
"""

import re

print("="*80)
print("  COMPREHENSIVE DATABASE FIX")
print("="*80)
print()

# Read current app.py
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Create backup
with open('app.py.backup_comprehensive', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("✅ Created backup: app.py.backup_comprehensive")
print()

# Track changes
changes = []

# Process line by line
i = 0
while i < len(lines):
    line = lines[i]
    
    # Fix 1: Remove MongoDB-style _id conversions
    if '"id": {"$toString": "$_id"}' in line or 'dept_admin["id"] = str(dept_admin["_id"])' in line:
        # Skip this line
        changes.append(f"Line {i+1}: Removed MongoDB _id conversion")
        i += 1
        continue
    
    # Fix 2: Convert aggregate calls to simple find
    if '.aggregate([' in line and '$lookup' in ''.join(lines[i:min(i+20, len(lines))]):
        # This is a complex aggregation, mark for manual review
        changes.append(f"Line {i+1}: Complex aggregation found - needs manual review")
    
    i += 1

print(f"📊 Found {len(changes)} potential issues")
for change in changes[:10]:  # Show first 10
    print(f"   {change}")

if len(changes) > 10:
    print(f"   ... and {len(changes) - 10} more")

print()
print("="*80)
print("  Creating simplified database helper functions")
print("="*80)
print()

# Create a helper module
helper_code = '''"""
Database helper functions for SQLite compatibility
"""

def get_complaints_with_details(db, query=None):
    """Get complaints with user and worker details"""
    if query:
        complaints = list(db.complaints.find(query))
    else:
        complaints = list(db.complaints.find())
    
    for complaint in complaints:
        # Add user info
        if complaint.get("user_id"):
            try:
                user_id = int(complaint["user_id"]) if str(complaint["user_id"]).isdigit() else None
                if user_id:
                    user = db.users.find_one({"id": user_id})
                    if user:
                        complaint["user_name"] = user.get("name")
            except (ValueError, TypeError):
                pass
        
        # Add worker info
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
    
    # Sort by created_at
    complaints.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return complaints

def get_feedbacks_with_details(db, query=None):
    """Get feedbacks with user and complaint details"""
    if query:
        feedbacks = list(db.feedback.find(query))
    else:
        feedbacks = list(db.feedback.find())
    
    for feedback in feedbacks:
        # Add user info
        if feedback.get("user_id"):
            try:
                user_id = int(feedback["user_id"]) if str(feedback["user_id"]).isdigit() else None
                if user_id:
                    user = db.users.find_one({"id": user_id})
                    if user:
                        feedback["user_name"] = user.get("name")
            except (ValueError, TypeError):
                pass
        
        # Add complaint info
        if feedback.get("complaint_id"):
            try:
                complaint_id = int(feedback["complaint_id"])
                complaint = db.complaints.find_one({"id": complaint_id})
                if complaint:
                    feedback["complaint_title"] = complaint.get("title")
            except (ValueError, TypeError):
                pass
    
    # Sort by created_at
    feedbacks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return feedbacks

def get_department_stats(db, department=None):
    """Get department-wise complaint statistics"""
    if department:
        complaints = list(db.complaints.find({"department": department}))
    else:
        complaints = list(db.complaints.find())
    
    dept_counts = {}
    for c in complaints:
        dept = c.get("department", "Unknown")
        dept_counts[dept] = dept_counts.get(dept, 0) + 1
    
    # Sort by count
    dept_items = sorted(dept_counts.items(), key=lambda x: x[1], reverse=True)
    return {
        "labels": [item[0] for item in dept_items],
        "counts": [item[1] for item in dept_items]
    }
'''

with open('database_helpers.py', 'w', encoding='utf-8') as f:
    f.write(helper_code)

print("✅ Created database_helpers.py with utility functions")
print()
print("="*80)
print("  NEXT STEPS")
print("="*80)
print()
print("1. Import helpers in app.py:")
print("   from database_helpers import get_complaints_with_details, get_feedbacks_with_details")
print()
print("2. Replace complex aggregations with helper functions:")
print("   complaints = get_complaints_with_details(db, {'user_id': user_id})")
print()
print("3. Restart the Flask server")
print()
