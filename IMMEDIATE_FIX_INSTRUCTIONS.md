# 🚨 IMMEDIATE FIX FOR 500 ERROR

## Problem
**500 Internal Server Error** when logging into admin dashboard

## Root Cause
The `admin_dashboard()` function in `app.py` is using MongoDB aggregation operations (`$lookup`, `$unwind`, `$group`) that are NOT supported by SQLite.

## Quick Fix (2 Minutes)

### Step 1: Open app.py
Find the `admin_dashboard()` function (starts around line 246)

### Step 2: Find This Section
Look for this code:
```python
# Fetch all complaints with user and worker info using MongoDB aggregation
complaints = list(db.complaints.aggregate([
```

### Step 3: Replace Everything
Replace from the line above **down to** (but not including):
```python
return render_template(
```

### Step 4: Paste This Fixed Code

```python
    # Fetch all complaints (simplified for SQLite)
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
                pass

```

### Step 5: Save and Restart
1. Save `app.py`
2. Restart your Flask server
3. Try logging in as admin again

## Expected Result
✅ Admin dashboard should load without 500 error
✅ You should see the dashboard with statistics
✅ Complaints list should display

## If Still Getting Errors
Check the Flask console for the specific error message and share it.

## Why This Fix Works
- Removes complex MongoDB aggregation operations
- Uses simple SQLite-compatible queries
- Joins data manually in Python (which works with any database)
- No changes to database structure needed

## Visual Guide

**BEFORE (Broken - MongoDB style):**
```python
complaints = list(db.complaints.aggregate([
    {"$lookup": {...}},  # ❌ Not supported in SQLite
    {"$unwind": {...}},  # ❌ Not supported in SQLite
    ...
]))
```

**AFTER (Fixed - SQLite compatible):**
```python
complaints = list(db.complaints.find())  # ✅ Simple query
for complaint in complaints:
    # ✅ Manual join in Python
    user = db.users.find_one({"id": user_id})
    ...
```

## Need Help?
If you're unsure about the exact lines to replace, look for:
- Line starting with: `# Fetch all complaints with user and worker info`
- Line ending with: `c["created_at"] = c["created_at"].strftime("%Y-%m-%d %H:%M")`

Replace everything between these two sections.
