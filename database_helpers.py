"""
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
