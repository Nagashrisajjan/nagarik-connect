# This file contains the key MongoDB conversion patterns
# Use these to replace corresponding sections in app.py

from database import get_db
from bson import ObjectId
from datetime import datetime

# ===== ADMIN DASHBOARD =====
def admin_dashboard_mongodb():
    """Admin dashboard with MongoDB"""
    db = get_db()
    
    # Fetch all complaints with user and worker info
    complaints = list(db.complaints.aggregate([
        {"$lookup": {
            "from": "users",
            "let": {"user_id_str": "$user_id"},
            "pipeline": [
                {"$addFields": {"id_str": {"$toString": "$_id"}}},
                {"$match": {"$expr": {"$eq": ["$id_str", "$$user_id_str"]}}}
            ],
            "as": "user_info"
        }},
        {"$lookup": {
            "from": "workers",
            "let": {"worker_id": "$assigned_worker_id"},
            "pipeline": [
                {"$match": {"$expr": {"$eq": [{"$toString": "$_id"}, "$$worker_id"]}}}
            ],
            "as": "worker_info"
        }},
        {"$unwind": {"path": "$user_info", "preserveNullAndEmptyArrays": True}},
        {"$unwind": {"path": "$worker_info", "preserveNullAndEmptyArrays": True}},
        {"$addFields": {
            "id": {"$toString": "$_id"},
            "user_name": "$user_info.name",
            "assigned_worker_name": "$worker_info.name",
            "assigned_worker_phone": "$worker_info.phone",
            "worker_department": "$worker_info.department"
        }},
        {"$sort": {"created_at": -1}}
    ]))
    
    # Get all workers
    all_workers = list(db.workers.find().sort([("department", 1), ("name", 1)]))
    for w in all_workers:
        w["id"] = str(w["_id"])
    
    # Statistics
    total_all = db.complaints.count_documents({})
    pending_all = db.complaints.count_documents({"status": "Pending"})
    in_progress_all = db.complaints.count_documents({"status": "In Progress"})
    resolved_all = db.complaints.count_documents({"status": "Resolved"})
    
    # Department-wise counts
    dept_data = list(db.complaints.aggregate([
        {"$group": {"_id": "$department", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]))
    dept_labels = [d["_id"] for d in dept_data]
    dept_counts = [d["count"] for d in dept_data]
    
    return complaints, all_workers, total_all, pending_all, in_progress_all, resolved_all, dept_labels, dept_counts

# ===== DEPARTMENT DASHBOARD =====
def department_dashboard_mongodb(dept_name):
    """Department dashboard with MongoDB"""
    db = get_db()
    
    # Fetch complaints for this department with user info
    complaints = list(db.complaints.aggregate([
        {"$match": {"department": dept_name}},
        {"$lookup": {
            "from": "users",
            "let": {"user_id_str": "$user_id"},
            "pipeline": [
                {"$addFields": {"id_str": {"$toString": "$_id"}}},
                {"$match": {"$expr": {"$eq": ["$id_str", "$$user_id_str"]}}}
            ],
            "as": "user_info"
        }},
        {"$unwind": {"path": "$user_info", "preserveNullAndEmptyArrays": True}},
        {"$addFields": {
            "id": {"$toString": "$_id"},
            "user_name": "$user_info.name"
        }},
        {"$sort": {"created_at": -1}}
    ]))
    
    # Statistics
    total = db.complaints.count_documents({"department": dept_name})
    pending = db.complaints.count_documents({"department": dept_name, "status": "Pending"})
    in_progress = db.complaints.count_documents({"department": dept_name, "status": "In Progress"})
    resolved = db.complaints.count_documents({"department": dept_name, "status": "Resolved"})
    
    return complaints, total, pending, in_progress, resolved

# ===== SUBMIT COMPLAINT =====
def submit_complaint_mongodb(user_id, user_name, title, description, department, filename, latitude, longitude, location_text):
    """Submit complaint to MongoDB"""
    db = get_db()
    
    result = db.complaints.insert_one({
        "user_id": user_id,
        "user_name": user_name,
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
        "assigned_worker_id": None,
        "assigned_worker_name": None,
        "assigned_worker_phone": None
    })
    
    return str(result.inserted_id)

# ===== UPDATE STATUS =====
def update_status_mongodb(complaint_id, status):
    """Update complaint status in MongoDB"""
    db = get_db()
    
    db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {"status": status}}
    )

# ===== ADD WORKER =====
def add_worker_mongodb(complaint_id, worker_name, worker_phone, department):
    """Add/assign worker to complaint in MongoDB"""
    db = get_db()
    
    # First, insert or find worker
    worker = db.workers.find_one({"name": worker_name, "phone": worker_phone})
    if not worker:
        result = db.workers.insert_one({
            "name": worker_name,
            "phone": worker_phone,
            "department": department,
            "created_at": datetime.now().isoformat()
        })
        worker_id = str(result.inserted_id)
    else:
        worker_id = str(worker["_id"])
    
    # Update complaint with worker info
    db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {
            "assigned_worker_id": worker_id,
            "assigned_worker_name": worker_name,
            "assigned_worker_phone": worker_phone
        }}
    )

# ===== UPLOAD ADMIN IMAGE =====
def upload_admin_image_mongodb(complaint_id, filename):
    """Upload admin progress image to MongoDB"""
    db = get_db()
    
    db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {"admin_image": filename}}
    )

# ===== FEEDBACK =====
def submit_feedback_mongodb(name, email, message):
    """Submit feedback to MongoDB"""
    db = get_db()
    
    db.feedback.insert_one({
        "name": name,
        "email": email,
        "message": message,
        "created_at": datetime.now().isoformat()
    })

def get_all_feedback_mongodb():
    """Get all feedback from MongoDB"""
    db = get_db()
    
    feedback = list(db.feedback.find().sort("created_at", -1))
    for f in feedback:
        f["id"] = str(f["_id"])
    
    return feedback
