# Fix for 500 Internal Server Error

## Problem
The application is using MongoDB-style aggregation operations (`$lookup`, `$unwind`, `$group`) that are NOT supported by the SQLite database wrapper.

## Root Cause
The `database_sqlite.py` wrapper only supports basic aggregation (`$match`, `$sort`, `$limit`) but the app.py code uses complex MongoDB operations throughout.

## Solution
We need to replace all complex aggregation queries with simple SQLite-compatible queries and manual data joining.

## Files to Fix
- `app.py` - Multiple functions using complex aggregation

## Quick Fix Instructions

### Option 1: Use Python Script (Recommended)
Run this command to automatically fix all issues:
```bash
python fix_aggregation.py
```

### Option 2: Manual Fix
Replace the complex aggregation queries with simple queries + manual joins.

## Affected Functions in app.py:
1. `user_dashboard()` - Line ~176
2. `admin_dashboard()` - Line ~254 ⚠️ **CAUSING YOUR 500 ERROR**
3. `department_dashboard()` - Line ~352
4. `feedback()` - Line ~611
5. `admin_feedback()` - Line ~659
6. `dept_admin_dashboard()` - Line ~751
7. `dept_admin_feedback()` - Line ~958

## Immediate Fix for Admin Dashboard (Your Current Error)

The admin dashboard is failing because it's trying to use `$lookup` and `$unwind` operations.

**Replace lines 253-301 in app.py with:**

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

## Testing After Fix
1. Restart the Flask server
2. Try logging in as admin again
3. The dashboard should load without 500 error

## Why This Happens
- MongoDB supports complex aggregation pipelines with joins ($lookup)
- SQLite doesn't have these operations
- The wrapper was trying to translate but failed on complex operations
- Solution: Use simple queries and join data in Python

## Prevention
When writing new code:
- Use simple `find()` queries
- Join data manually in Python
- Avoid `$lookup`, `$unwind`, `$group` operations
- Test with SQLite before deploying
