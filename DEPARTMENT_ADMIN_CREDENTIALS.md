# 🏢 Department Admin Credentials

## 🔐 All Login Credentials

### Department Admin Login URL
**http://localhost:5000/dept_admin/login**

---

## 💧 Water Crisis Department

| Field | Value |
|-------|-------|
| **Department** | Water Crisis |
| **Username** | `water_admin` |
| **Password** | `water123` |
| **Login URL** | http://localhost:5000/dept_admin/login |

**Responsibilities:**
- Manage water-related complaints
- Assign water department workers
- Update complaint status
- View department analytics

---

## 🛣️ Road Maintenance Department

| Field | Value |
|-------|-------|
| **Department** | Road Maintenance(Engg) |
| **Username** | `road_admin` |
| **Password** | `road123` |
| **Login URL** | http://localhost:5000/dept_admin/login |

**Responsibilities:**
- Manage road maintenance complaints
- Assign road workers
- Update complaint status
- View department analytics

---

## 🗑️ Solid Waste (Garbage) Department

| Field | Value |
|-------|-------|
| **Department** | Solid Waste (Garbage) Related |
| **Username** | `garbage_admin` |
| **Password** | `garbage123` |
| **Login URL** | http://localhost:5000/dept_admin/login |

**Responsibilities:**
- Manage garbage collection complaints
- Assign sanitation workers
- Update complaint status
- View department analytics

---

## ⚡ Electrical Department

| Field | Value |
|-------|-------|
| **Department** | Electrical |
| **Username** | `electrical_admin` |
| **Password** | `electrical123` |
| **Login URL** | http://localhost:5000/dept_admin/login |

**Responsibilities:**
- Manage electrical complaints
- Assign electrical workers
- Update complaint status
- View department analytics

---

## 📋 General Department

| Field | Value |
|-------|-------|
| **Department** | General Department |
| **Username** | `general_admin` |
| **Password** | `general123` |
| **Login URL** | http://localhost:5000/dept_admin/login |

**Responsibilities:**
- Manage general complaints
- Assign general workers
- Update complaint status
- View department analytics

---

## 🎯 Quick Reference Table

| Department | Username | Password |
|------------|----------|----------|
| Water Crisis | `water_admin` | `water123` |
| Road Maintenance | `road_admin` | `road123` |
| Solid Waste (Garbage) | `garbage_admin` | `garbage123` |
| Electrical | `electrical_admin` | `electrical123` |
| General | `general_admin` | `general123` |

---

## 🔑 Other Admin Credentials

### Super Admin
- **URL**: http://localhost:5000/admin
- **Username**: `admin`
- **Password**: `admin@123`
- **Access**: Full system access

---

## 📝 How to Login

1. **Open your browser**
2. **Go to**: http://localhost:5000/dept_admin/login
3. **Enter username** (e.g., `water_admin`)
4. **Enter password** (e.g., `water123`)
5. **Click Login**

You'll be redirected to your department-specific dashboard!

---

## 🎨 Department Dashboard Features

Each department admin can:

✅ **View Department Complaints**
- See all complaints assigned to their department
- Filter by status (Pending, In Progress, Resolved)

✅ **Manage Workers**
- View department workers
- Assign workers to complaints
- Add new workers

✅ **Update Complaint Status**
- Change status (Pending → In Progress → Resolved)
- Add remarks
- Upload resolution images

✅ **View Analytics**
- Department statistics
- Complaint trends
- Worker performance

✅ **Handle Feedback**
- View department-related feedback
- Respond to citizen feedback

---

## ⚠️ Security Notes

### For Production Deployment:

1. **Change all default passwords**
2. **Use strong passwords** (minimum 12 characters)
3. **Enable HTTPS**
4. **Set up password reset functionality**
5. **Implement account lockout after failed attempts**
6. **Add two-factor authentication (optional)**

### Recommended Password Format:
- Minimum 12 characters
- Mix of uppercase and lowercase
- Include numbers and special characters
- Example: `W@ter$ecure2025!`

---

## 🔄 Reset/Change Passwords

To change a department admin password:

```python
python change_dept_admin_password.py
```

Or manually in the database:

```python
from werkzeug.security import generate_password_hash
from database_sqlite import get_db

db = get_db()
new_password = generate_password_hash("new_password_here")
db.dept_admins.update_one(
    {"username": "water_admin"},
    {"$set": {"password": new_password}}
)
```

---

## 📞 Support

If you have issues logging in:

1. **Check credentials** - Make sure username and password are correct
2. **Check database** - Ensure department admins are created
3. **Check server** - Make sure Flask server is running
4. **Check logs** - Look for error messages in console

**Need help?** Contact: support@nagarikconnect.gov.in

---

## 🎓 Testing the Accounts

### Quick Test:
1. Login as `water_admin` / `water123`
2. You should see the Water Crisis department dashboard
3. Try viewing complaints, assigning workers, updating status

### Full Test:
- Test each department admin account
- Verify department-specific data is shown
- Test all CRUD operations
- Check analytics and reports

---

**Status**: ✅ All department admin accounts created and ready to use!

**Last Updated**: 2025-11-27

**Version**: 1.0.0
