# 🗄️ MongoDB Atlas - Complete Setup Guide

## Step-by-Step Instructions with Screenshots Guide

---

## PART 1: Create MongoDB Atlas Account

### Step 1: Go to MongoDB Atlas Website
1. Open your browser
2. Go to: **https://www.mongodb.com/cloud/atlas/register**
3. You'll see the registration page

### Step 2: Sign Up
Choose one of these options:

**Option A: Sign up with Google (Recommended - Fastest)**
- Click "Sign up with Google"
- Select your Google account
- Accept permissions

**Option B: Sign up with Email**
- Enter your email address
- Create a password (minimum 8 characters)
- Enter your first and last name
- Click "Create your Atlas account"
- Check your email for verification link
- Click the verification link

### Step 3: Complete Welcome Survey (Optional)
MongoDB will ask some questions:
- What brings you to Atlas? → Select "Learning MongoDB"
- What is your goal? → Select "Build a new app"
- What is your preferred language? → Select "Python"
- Click "Finish"

---

## PART 2: Create Your First Cluster

### Step 4: Create a Free Cluster

You'll see "Deploy a cloud database" page:

1. **Choose Deployment Option:**
   - Click on **"M0 FREE"** (the free tier)
   - This gives you 512MB storage for free

2. **Choose Cloud Provider & Region:**
   - **Provider**: Select **AWS** (recommended) or Google Cloud or Azure
   - **Region**: Select closest to your location or users
     - For India: Select **Mumbai (ap-south-1)** or **Singapore (ap-southeast-1)**
     - For USA: Select **N. Virginia (us-east-1)**
     - For Europe: Select **Ireland (eu-west-1)**
   
3. **Cluster Name:**
   - Default name: `Cluster0` (you can keep this or change it)
   - Example: `NagarikConnectDB`

4. **Click "Create"**
   - Wait 1-3 minutes for cluster creation
   - You'll see "Your cluster is being created..."

---

## PART 3: Configure Database Access (Create User)

### Step 5: Create Database User

After cluster is created, you'll see a "Security Quickstart" popup:

1. **Authentication Method:**
   - Keep "Username and Password" selected (default)

2. **Create Database User:**
   - **Username**: Enter a username (example: `icgs_admin`)
   - **Password**: Click "Autogenerate Secure Password" 
     - **IMPORTANT**: Copy this password immediately!
     - Save it in a safe place (Notepad, password manager)
     - Example password: `xK9mP2nQ7vL5wR8t`
   
   OR
   
   - Create your own password (minimum 8 characters)
   - **IMPORTANT**: Remember this password!

3. **Database User Privileges:**
   - Keep default: "Read and write to any database"

4. **Click "Create User"**

**⚠️ CRITICAL: Save these credentials now!**
```
Username: icgs_admin
Password: xK9mP2nQ7vL5wR8t
```

---

## PART 4: Configure Network Access (Whitelist IP)

### Step 6: Add IP Address

Still in the "Security Quickstart" popup:

1. **Where would you like to connect from?**
   - Select **"My Local Environment"**

2. **Add IP Address:**
   - Click **"Add My Current IP Address"** (for testing)
   
   **OR (Recommended for deployment):**
   
   - Click **"Add a Different IP Address"**
   - In the IP Address field, enter: **`0.0.0.0/0`**
   - Description: `Allow all IPs` or `Deployment access`
   - This allows connections from anywhere (needed for Render/Railway)

3. **Click "Add Entry"**

4. **Click "Finish and Close"**

---

## PART 5: Get Connection String

### Step 7: Get Your Connection Details

1. **Go to Database:**
   - Click "Database" in the left sidebar
   - You'll see your cluster (Cluster0)

2. **Click "Connect":**
   - Click the "Connect" button on your cluster

3. **Choose Connection Method:**
   - Click **"Connect your application"**

4. **Select Driver and Version:**
   - **Driver**: Select **"Python"**
   - **Version**: Select **"3.12 or later"**

5. **Copy Connection String:**
   You'll see a connection string like this:
   ```
   mongodb+srv://icgs_admin:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

6. **Extract Your Details:**
   From the connection string, note these values:
   
   ```
   Username: icgs_admin
   Password: (your password from Step 5)
   Cluster: cluster0.xxxxx.mongodb.net
   ```
   
   **Example:**
   ```
   Connection String:
   mongodb+srv://icgs_admin:xK9mP2nQ7vL5wR8t@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
   
   Extract:
   Username: icgs_admin
   Password: xK9mP2nQ7vL5wR8t
   Cluster: cluster0.abc123.mongodb.net
   ```

---

## PART 6: Configure Your Application

### Step 8: Update config.py

1. **Open your project folder:**
   ```
   icgs_project3/config.py
   ```

2. **Update these lines with YOUR credentials:**

```python
# MongoDB Atlas Configuration
MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME', 'icgs_admin')  # ← Your username
MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD', 'xK9mP2nQ7vL5wR8t')  # ← Your password
MONGODB_CLUSTER = os.environ.get('MONGODB_CLUSTER', 'cluster0.abc123.mongodb.net')  # ← Your cluster
MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE', 'icgs_complaints')
```

**Replace:**
- `icgs_admin` → Your username
- `xK9mP2nQ7vL5wR8t` → Your password
- `cluster0.abc123.mongodb.net` → Your cluster URL

### Step 9: Test Connection (Optional but Recommended)

Create a test file to verify connection:

```bash
# In icgs_project3 folder, create test_connection.py
```

```python
from pymongo import MongoClient
from config import Config

try:
    # Get MongoDB URI
    mongodb_uri = Config.get_mongodb_uri()
    print(f"Connecting to: {mongodb_uri[:50]}...")
    
    # Connect
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    
    # Test connection
    client.server_info()
    
    print("✅ SUCCESS! Connected to MongoDB Atlas!")
    print(f"Database: {Config.MONGODB_DATABASE}")
    
    # List databases
    print("\nAvailable databases:")
    for db in client.list_database_names():
        print(f"  - {db}")
    
    client.close()
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Check your username and password in config.py")
    print("2. Verify cluster URL is correct")
    print("3. Ensure network access is configured (0.0.0.0/0)")
    print("4. Check if cluster is active in MongoDB Atlas dashboard")
```

**Run the test:**
```bash
pip install pymongo dnspython
python test_connection.py
```

**Expected output:**
```
Connecting to: mongodb+srv://icgs_admin:***@cluster0.abc123...
✅ SUCCESS! Connected to MongoDB Atlas!
Database: icgs_complaints

Available databases:
  - admin
  - local
```

---

## PART 7: Migrate Your Data

### Step 10: Run Migration Script

Now that connection is working, migrate your MySQL data:

```bash
python migrate_to_mongodb.py
```

**Expected output:**
```
🚀 Starting migration from MySQL to MongoDB Atlas...
✅ Connected to MySQL
✅ Connected to MongoDB Atlas

📦 Migrating users...
✅ Migrated 5 users

📦 Migrating complaints...
✅ Migrated 23 complaints

📦 Migrating workers...
✅ Migrated 8 workers

📦 Migrating department admins...
✅ Migrated 6 department admins

📦 Migrating feedback...
✅ Migrated 12 feedback entries

🎉 Migration completed successfully!
```

---

## PART 8: Verify Data in MongoDB Atlas

### Step 11: Check Your Data

1. **Go to MongoDB Atlas Dashboard:**
   - Click "Database" in left sidebar
   - Click "Browse Collections" on your cluster

2. **You should see:**
   - Database: `icgs_complaints`
   - Collections:
     - `users`
     - `complaints`
     - `workers`
     - `dept_admins`
     - `feedback`

3. **Click on each collection to view data**

---

## 📋 Quick Reference Card

**Save these credentials:**

```
═══════════════════════════════════════════════════
         MONGODB ATLAS CREDENTIALS
═══════════════════════════════════════════════════

Username:     _________________________________

Password:     _________________________________

Cluster URL:  _________________________________

Database:     icgs_complaints

Full Connection String:
mongodb+srv://USERNAME:PASSWORD@CLUSTER/?retryWrites=true&w=majority

═══════════════════════════════════════════════════
```

---

## 🆘 Troubleshooting

### Problem: "Authentication failed"
**Solution:**
- Double-check username and password
- Ensure no extra spaces in credentials
- Password might contain special characters - use URL encoding

### Problem: "Connection timeout"
**Solution:**
- Check network access settings (should be 0.0.0.0/0)
- Verify cluster is active (not paused)
- Check your internet connection

### Problem: "Server selection timeout"
**Solution:**
- Verify cluster URL is correct
- Check if cluster is still being created (wait 2-3 minutes)
- Ensure dnspython is installed: `pip install dnspython`

### Problem: "IP not whitelisted"
**Solution:**
- Go to Network Access in MongoDB Atlas
- Add 0.0.0.0/0 to allow all IPs
- Wait 1-2 minutes for changes to apply

### Problem: "Database user not found"
**Solution:**
- Go to Database Access in MongoDB Atlas
- Verify user exists
- Check username spelling
- Recreate user if needed

---

## 🔐 Security Best Practices

1. **Never commit credentials to Git:**
   - Use environment variables
   - Keep .env file in .gitignore

2. **Use strong passwords:**
   - Minimum 12 characters
   - Mix of letters, numbers, symbols

3. **Limit IP access in production:**
   - Use specific IPs instead of 0.0.0.0/0
   - Add only your server's IP

4. **Regular backups:**
   - MongoDB Atlas provides automatic backups
   - Export data periodically

5. **Monitor usage:**
   - Check MongoDB Atlas dashboard regularly
   - Set up alerts for storage limits

---

## 📊 MongoDB Atlas Dashboard Overview

### Key Sections:

1. **Database:**
   - View clusters
   - Browse collections
   - Monitor performance

2. **Database Access:**
   - Manage users
   - Set permissions
   - Reset passwords

3. **Network Access:**
   - Manage IP whitelist
   - Add/remove IPs
   - Configure VPC peering

4. **Metrics:**
   - View database usage
   - Monitor connections
   - Check storage

5. **Backup:**
   - Configure backup schedule
   - Restore from backup
   - Download snapshots

---

## ✅ Verification Checklist

- [ ] MongoDB Atlas account created
- [ ] Email verified (if using email signup)
- [ ] Free cluster (M0) created
- [ ] Cluster is active (green status)
- [ ] Database user created with password
- [ ] Password saved securely
- [ ] Network access configured (0.0.0.0/0)
- [ ] Connection string copied
- [ ] Username extracted
- [ ] Password extracted
- [ ] Cluster URL extracted
- [ ] config.py updated with credentials
- [ ] Test connection successful
- [ ] Migration script executed
- [ ] Data visible in MongoDB Atlas
- [ ] All collections present

---

## 🎯 Next Steps

After completing MongoDB Atlas setup:

1. ✅ **Verify data migration** - Check collections in Atlas
2. ✅ **Update environment variables** - For deployment
3. ✅ **Push to GitHub** - Prepare for deployment
4. ✅ **Deploy to Render** - Follow DEPLOYMENT_GUIDE.md

---

## 📞 Need Help?

### MongoDB Atlas Support:
- Documentation: https://docs.atlas.mongodb.com
- Community Forums: https://www.mongodb.com/community/forums
- Support: https://support.mongodb.com

### Common Resources:
- Connection String Format: https://docs.mongodb.com/manual/reference/connection-string/
- Security Checklist: https://docs.atlas.mongodb.com/security-checklist/
- Free Tier Limits: https://docs.atlas.mongodb.com/reference/free-shared-limitations/

---

## 🎉 Success!

Once you see "✅ Connected to MongoDB Atlas!" you're ready to deploy!

**Next:** Follow `DEPLOYMENT_GUIDE.md` to deploy your app to Render.

---

*Your data is now in the cloud and ready for deployment!* ☁️
