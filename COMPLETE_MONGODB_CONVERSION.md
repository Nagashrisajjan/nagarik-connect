# 🔄 Complete MongoDB Conversion Guide

## Status: Your app.py still has SQL queries that need conversion

The automatic script converted simple queries, but complex JOINs need manual work.

## Remaining SQL Queries to Convert:

### 1. User Dashboard - Complex JOIN Query (Line ~177)
**MySQL:**
```sql
SELECT c.*, w.name AS assigned_worker_name, w.phone AS assigned_worker_phone, u.name AS user_name
FROM complaints c
JOIN users u ON c.user_id = u.id
LEFT JOIN workers w ON c.assigned_worker_id = w.id
WHERE c.user_id = %s
```

**MongoDB (using aggregation):**
```python
complaints = list(db.complaints.aggregate([
    {"$match": {"user_id": session["user_id"]}},
    {"$lookup": {
        "from": "users",
        "localField": "user_id",
        "foreignField": "_id",
        "as": "user_info"
    }},
    {"$lookup": {
        "from": "workers",
        "localField": "assigned_worker_id",
        "foreignField": "_id",
        "as": "worker_info"
    }},
    {"$unwind": {"path": "$user_info", "preserveNullAndEmptyArrays": True}},
    {"$unwind": {"path": "$worker_info", "preserveNullAndEmptyArrays": True}},
    {"$addFields": {
        "id": {"$toString": "$_id"},
        "user_name": "$user_info.name",
        "assigned_worker_name": "$worker_info.name",
        "assigned_worker_phone": "$worker_info.phone"
    }},
    {"$sort": {"created_at": -1}}
]))
```

### 2. Count Queries with WHERE
**MySQL:**
```sql
SELECT COUNT(*) as total FROM complaints WHERE user_id=%s
```

**MongoDB:**
```python
total = db.complaints.count_documents({"user_id": session["user_id"]})
resolved = db.complaints.count_documents({"user_id": session["user_id"], "status": "Resolved"})
pending = db.complaints.count_documents({"user_id": session["user_id"], "status": "Pending"})
in_progress = db.complaints.count_documents({"user_id": session["user_id"], "status": {"$regex": "in progress", "$options": "i"}})
```

### 3. Admin Dashboard - All Complaints with JOINs
Similar aggregation pipeline but without user_id filter.

### 4. INSERT Complaint
**MySQL:**
```sql
INSERT INTO complaints (user_id, title, description, ...) VALUES (%s, %s, ...)
```

**MongoDB:**
```python
result = db.complaints.insert_one({
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
complaint_id = str(result.inserted_id)
```

### 5. UPDATE Status
**MySQL:**
```sql
UPDATE complaints SET status=%s, remarks=%s WHERE id=%s
```

**MongoDB:**
```python
db.complaints.update_one(
    {"_id": ObjectId(complaint_id)},
    {"$set": {"status": status, "remarks": remarks}}
)
```

## Quick Fix: Use Pre-Converted Version

I'll create a fully converted app.py for you. Due to the complexity (828 lines with many JOINs), this requires careful manual conversion.

## Estimated Time:
- Manual conversion: 2-3 hours
- Testing: 1 hour
- Total: 3-4 hours

## Alternative: Deploy with MySQL First

Since full conversion takes time, you could:
1. Deploy with MySQL on Render (using PlanetScale)
2. Get app working
3. Convert to MongoDB later

This gets you deployed TODAY while we work on MongoDB conversion.

What do you prefer?
