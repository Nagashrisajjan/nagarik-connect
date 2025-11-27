# 🔐 ICGS Complaints System - Login Credentials

## 👨‍💼 Super Admin Login
**URL:** `/admin/login` or just `/login`

- **Username:** `admin`
- **Password:** `admin@123`

**Access:** Full system access, view all complaints, manage all departments

---

## 🏢 Department Admin Logins
**URL:** `/dept_admin/login`

### 1. Water Department
- **Username:** `water_admin`
- **Password:** `water123`
- **Department:** Water Crisis
- **Name:** Water Admin

### 2. Road Department
- **Username:** `road_admin`
- **Password:** `road123`
- **Department:** Road Maintenance(Engg)
- **Name:** Road Admin

### 3. Garbage Department
- **Username:** `garbage_admin`
- **Password:** `garbage123`
- **Department:** Solid Waste (Garbage) Related
- **Name:** Garbage Admin

### 4. Electrical Department
- **Username:** `electrical_admin`
- **Password:** `electrical123`
- **Department:** Electrical
- **Name:** Electrical Admin

### 5. General Department
- **Username:** `general_admin`
- **Password:** `general123`
- **Department:** General Department
- **Name:** General Admin

---

## 👥 Citizen/User Login
**URL:** `/register` (for new users) or `/login`

Citizens need to register first with:
- Name
- Email
- Password

After registration, they can login and submit complaints.

---

## 🌐 Live Deployment URLs

Once deployed on Render, your URLs will be:

- **Homepage:** `https://your-app.onrender.com/`
- **Citizen Login:** `https://your-app.onrender.com/login`
- **Admin Login:** `https://your-app.onrender.com/login` (use admin credentials)
- **Dept Admin Login:** `https://your-app.onrender.com/dept_admin/login`

---

## 📋 Quick Reference Table

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| Super Admin | admin | admin@123 | All departments |
| Water Admin | water_admin | water123 | Water complaints only |
| Road Admin | road_admin | road123 | Road complaints only |
| Garbage Admin | garbage_admin | garbage123 | Garbage complaints only |
| Electrical Admin | electrical_admin | electrical123 | Electrical complaints only |
| General Admin | general_admin | general123 | General complaints only |

---

## ⚠️ Security Note

**IMPORTANT:** After deployment, you should change these default passwords!

To change passwords, you can:
1. Access the SQLite database
2. Update the password hashes in the `dept_admins` table
3. Or create a password reset feature

---

## 🎯 Testing Workflow

1. **Register as Citizen** → Submit a complaint
2. **Login as Dept Admin** → View and manage department complaints
3. **Login as Super Admin** → View all complaints across departments

---

**All credentials are pre-configured and ready to use!** ✅
