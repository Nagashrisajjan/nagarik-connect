# This is a helper script showing how to convert MySQL queries to MongoDB
# Use this as reference to update your app.py

from database import get_db
from bson import ObjectId

# Example conversions:

# 1. COUNT queries
def count_complaints():
    db = get_db()
    total = db.complaints.count_documents({})
    resolved = db.complaints.count_documents({"status": {"$regex": "resolved", "$options": "i"}})
    pending = db.complaints.count_documents({"status": {"$regex": "pending", "$options": "i"}})
    in_progress = db.complaints.count_documents({"status": {"$regex": "in progress", "$options": "i"}})
    return total, resolved, pending, in_progress

# 2. FIND ONE (login)
def find_user_by_email(email):
    db = get_db()
    user = db.users.find_one({"email": email})
    if user:
        user['id'] = str(user['_id'])
    return user

# 3. INSERT (register)
def insert_user(name, email, hashed_password, role="citizen"):
    db = get_db()
    result = db.users.insert_one({
        "name": name,
        "email": email,
        "password": hashed_password,
        "role": role,
        "created_at": datetime.now().isoformat()
    })
    return str(result.inserted_id)

# 4. FIND with JOIN (complaints with worker info)
def get_user_complaints_with_workers(user_id):
    db = get_db()
    # MongoDB doesn't have JOINs, use aggregation pipeline
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$lookup": {
            "from": "workers",
            "localField": "assigned_worker_id",
            "foreignField": "_id",
            "as": "worker_info"
        }},
        {"$unwind": {
            "path": "$worker_info",
            "preserveNullAndEmptyArrays": True
        }}
    ]
    complaints = list(db.complaints.aggregate(pipeline))
    
    # Convert ObjectIds to strings
    for c in complaints:
        c['id'] = str(c['_id'])
        c['user_id'] = str(c.get('user_id', ''))
        if 'worker_info' in c and c['worker_info']:
            c['assigned_worker_name'] = c['worker_info'].get('name')
            c['assigned_worker_phone'] = c['worker_info'].get('phone')
    
    return complaints

# 5. UPDATE
def update_complaint_status(complaint_id, status, remarks=None):
    db = get_db()
    update_data = {"status": status}
    if remarks:
        update_data["remarks"] = remarks
    
    db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": update_data}
    )

# 6. INSERT complaint
def insert_complaint(user_id, title, description, department, image=None, latitude=None, longitude=None, location=None):
    db = get_db()
    result = db.complaints.insert_one({
        "user_id": user_id,
        "user_name": session.get('name'),
        "title": title,
        "description": description,
        "department": department,
        "status": "Pending",
        "image": image,
        "latitude": latitude,
        "longitude": longitude,
        "location": location,
        "created_at": datetime.now().isoformat(),
        "remarks": None,
        "admin_image": None,
        "assigned_worker_id": None,
        "assigned_worker_name": None,
        "assigned_worker_phone": None
    })
    return str(result.inserted_id)
