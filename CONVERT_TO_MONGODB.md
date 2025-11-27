# 🔄 Converting app.py from MySQL to MongoDB

## The Problem:
Your app.py still uses MySQL queries, but you're now using MongoDB Atlas.

## The Solution:
We need to convert all MySQL queries to MongoDB queries.

## MySQL vs MongoDB Syntax:

### SELECT (Find)
```python
# MySQL
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
user = cursor.fetchone()

# MongoDB
user = db.users.find_one({"email": email})
```

### INSERT (Insert)
```python
# MySQL
cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
conn.commit()

# MongoDB
db.users.insert_one({"name": name, "email": email})
```

### UPDATE (Update)
```python
# MySQL
cursor.execute("UPDATE complaints SET status = %s WHERE id = %s", (status, id))
conn.commit()

# MongoDB
db.complaints.update_one({"_id": ObjectId(id)}, {"$set": {"status": status}})
```

### DELETE (Delete)
```python
# MySQL
cursor.execute("DELETE FROM users WHERE id = %s", (id,))
conn.commit()

# MongoDB
db.users.delete_one({"_id": ObjectId(id)})
```

### COUNT
```python
# MySQL
cursor.execute("SELECT COUNT(*) as total FROM complaints")
total = cursor.fetchone()['total']

# MongoDB
total = db.complaints.count_documents({})
```

## Key Differences:
1. MongoDB uses `_id` instead of `id`
2. MongoDB `_id` is ObjectId type, not integer
3. No need for cursor.close() or conn.close()
4. No SQL injection risk (uses dictionaries)
5. More Pythonic syntax

## Your app.py needs updating!
This is a significant change affecting all routes.
