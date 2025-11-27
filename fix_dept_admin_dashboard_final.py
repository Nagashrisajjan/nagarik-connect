#!/usr/bin/env python3
"""
Final fix for dept_admin_dashboard
Replace all MongoDB aggregations with SQLite-compatible code
"""

import re

print("="*80)
print("  FIXING DEPT_ADMIN_DASHBOARD")
print("="*80)
print()

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open('app.py.backup_dept_dashboard', 'w', encoding='utf-8') as f:
    f.write(content)
print("✅ Created backup: app.py.backup_dept_dashboard")
print()

# Find and replace the dept_admin_dashboard function
# Look for the function definition
pattern = r'@app\.route\("/dept_admin/dashboard", endpoint="dept_admin_dashboard"\)\s+def dept_admin_dashboard\(\):'

if re.search(pattern, content):
    print("✅ Found dept_admin_dashboard function")
    
    # Find the start and end of the function
    start_match = re.search(pattern, content)
    if start_match:
        start_pos = start_match.start()
        
        # Find the next function definition (end of this function)
        next_func_pattern = r'\n@app\.route\('
        next_match = re.search(next_func_pattern, content[start_pos + 100:])
        
        if next_match:
            end_pos = start_pos + 100 + next_match.start()
            
            # Extract the function
            old_function = content[start_pos:end_pos]
            
            # Create new function
            new_function = '''@app.route("/dept_admin/dashboard", endpoint="dept_admin_dashboard")
def dept_admin_dashboard():
    if "dept_admin_id" not in session or session.get("role") != "dept_admin":
        flash("Please login as department admin", "warning")
        return redirect(url_for("dept_admin_login"))

    department = session.get("department")
    admin_name = session.get("dept_admin_name")

    db = get_db()

    # Fetch complaints for this department (simplified for SQLite)
    complaints = list(db.complaints.find({"department": department}))
    
    # Manually add user and worker info
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
            except (ValueError, TypeError):
                pass
    
    # Sort by created_at
    complaints.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    # Statistics
    total = db.complaints.count_documents({"department": department})
    pending = db.complaints.count_documents({"department": department, "status": "Pending"})
    in_progress = db.complaints.count_documents({"department": department, "status": "In Progress"})
    resolved = db.complaints.count_documents({"department": department, "status": "Resolved"})

    # Fetch workers for this department (simplified for SQLite)
    workers = list(db.workers.find({"department": department}))
    
    # Add complaint counts manually
    for worker in workers:
        worker_complaints = db.complaints.count_documents({
            "assigned_worker_id": str(worker["id"])
        })
        worker["complaint_count"] = worker_complaints
    
    # Sort by name
    workers.sort(key=lambda x: x.get("name", ""))

    # Monthly trend data (simplified for SQLite)
    dept_complaints = list(db.complaints.find({"department": department}))
    trend_dict = {}
    for c in dept_complaints:
        if c.get("created_at"):
            month = str(c["created_at"])[:7] if isinstance(c["created_at"], str) else ""
            if month:
                trend_dict[month] = trend_dict.get(month, 0) + 1
    
    # Sort and limit to last 6 months
    trend_items = sorted(trend_dict.items())[-6:] if trend_dict else []
    trend_labels = [item[0] for item in trend_items]
    trend_data = [item[1] for item in trend_items]

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

    return render_template(
        "dept_admin_dashboard.html",
        department=department,
        admin_name=admin_name,
        complaints=complaints,
        workers=workers,
        total=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
        trend_labels=trend_labels,
        trend_data=trend_data
    )

'''
            
            # Replace
            content = content[:start_pos] + new_function + content[end_pos:]
            
            # Write back
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Fixed dept_admin_dashboard function")
            print()
            print("="*80)
            print("  FIX COMPLETE - RESTART SERVER")
            print("="*80)
        else:
            print("❌ Could not find end of function")
    else:
        print("❌ Could not find function start")
else:
    print("❌ Function not found")

print()
