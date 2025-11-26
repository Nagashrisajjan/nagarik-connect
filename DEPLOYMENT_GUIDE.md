# 🚀 Deployment Guide - Nagarik Connect

## Prerequisites
- MongoDB Atlas account (free tier available)
- Render account (free tier available) OR Railway/Heroku
- Git installed
- Your project pushed to GitHub

---

## Step 1: Setup MongoDB Atlas (Database)

### 1.1 Create MongoDB Atlas Account
1. Go to https://www.mongodb.com/cloud/atlas/register
2. Sign up for a free account
3. Create a new cluster (choose FREE tier - M0)
4. Wait for cluster to be created (2-3 minutes)

### 1.2 Configure Database Access
1. Click "Database Access" in left sidebar
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Username: `icgs_admin` (or your choice)
5. Password: Generate a secure password (SAVE THIS!)
6. Database User Privileges: "Read and write to any database"
7. Click "Add User"

### 1.3 Configure Network Access
1. Click "Network Access" in left sidebar
2. Click "Add IP Address"
3. Click "Allow Access from Anywhere" (0.0.0.0/0)
4. Click "Confirm"

### 1.4 Get Connection String
1. Click "Database" in left sidebar
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Copy the connection string (looks like):
   ```
   mongodb+srv://icgs_admin:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. Extract these values:
   - **Username**: `icgs_admin`
   - **Password**: Your password
   - **Cluster**: `cluster0.xxxxx.mongodb.net`

---

## Step 2: Migrate Data from MySQL to MongoDB

### 2.1 Update config.py with your MongoDB credentials
Edit `config.py` and update:
```python
MONGODB_USERNAME = 'icgs_admin'  # Your username
MONGODB_PASSWORD = 'your_password'  # Your password
MONGODB_CLUSTER = 'cluster0.xxxxx.mongodb.net'  # Your cluster
```

### 2.2 Run Migration Script
```bash
cd icgs_project3
pip install pymongo dnspython
python migrate_to_mongodb.py
```

This will transfer all data from MySQL to MongoDB Atlas.

---

## Step 3: Deploy to Render (Recommended)

### 3.1 Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 3.2 Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### 3.3 Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `nagarik-connect`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`

### 3.4 Add Environment Variables
Click "Advanced" → "Add Environment Variable" and add:

| Key | Value |
|-----|-------|
| `MONGODB_USERNAME` | Your MongoDB username |
| `MONGODB_PASSWORD` | Your MongoDB password |
| `MONGODB_CLUSTER` | Your cluster URL |
| `MONGODB_DATABASE` | `icgs_complaints` |
| `SECRET_KEY` | Generate random string |
| `PYTHON_VERSION` | `3.11.0` |

### 3.5 Deploy
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Your app will be live at: `https://nagarik-connect.onrender.com`

---

## Alternative: Deploy to Railway

### Railway Setup
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables (same as Render)
6. Railway will auto-detect Flask and deploy

---

## Alternative: Deploy to Heroku

### Heroku Setup
```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create nagarik-connect

# Set environment variables
heroku config:set MONGODB_USERNAME=your_username
heroku config:set MONGODB_PASSWORD=your_password
heroku config:set MONGODB_CLUSTER=cluster0.xxxxx.mongodb.net
heroku config:set MONGODB_DATABASE=icgs_complaints
heroku config:set SECRET_KEY=your_secret_key

# Deploy
git push heroku main

# Open app
heroku open
```

---

## Step 4: Post-Deployment

### 4.1 Test Your Application
1. Visit your deployed URL
2. Test login/registration
3. Submit a test complaint
4. Check admin dashboard

### 4.2 Monitor Logs
**Render**: Dashboard → Logs tab
**Railway**: Project → Deployments → View Logs
**Heroku**: `heroku logs --tail`

### 4.3 Setup Custom Domain (Optional)
- Render: Settings → Custom Domain
- Railway: Settings → Domains
- Heroku: Settings → Domains

---

## Troubleshooting

### Issue: "Application Error"
- Check logs for specific error
- Verify all environment variables are set
- Ensure MongoDB Atlas IP whitelist includes 0.0.0.0/0

### Issue: "Database Connection Failed"
- Verify MongoDB credentials
- Check MongoDB Atlas network access
- Ensure connection string format is correct

### Issue: "Module Not Found"
- Verify requirements.txt includes all dependencies
- Check Python version matches runtime.txt

### Issue: "Static Files Not Loading"
- Ensure `static/` folder is in repository
- Check file paths are relative
- Verify uploads folder exists

---

## Important Notes

1. **Free Tier Limitations**:
   - Render: App sleeps after 15 min inactivity (wakes on request)
   - MongoDB Atlas: 512MB storage limit
   - Railway: 500 hours/month free

2. **File Uploads**:
   - Uploaded files are stored in `static/uploads/`
   - On free tiers, files may be lost on restart
   - Consider using cloud storage (AWS S3, Cloudinary) for production

3. **Security**:
   - Never commit `.env` file to Git
   - Use strong SECRET_KEY
   - Keep MongoDB credentials secure

4. **Scaling**:
   - Start with free tier
   - Upgrade when needed
   - Monitor usage in dashboard

---

## Support

If you encounter issues:
1. Check deployment logs
2. Verify environment variables
3. Test MongoDB connection separately
4. Review Render/Railway documentation

---

## Quick Commands Reference

```bash
# Local testing
python app.py

# Check requirements
pip freeze > requirements.txt

# Test MongoDB connection
python -c "from database import get_db; print(get_db())"

# View Heroku logs
heroku logs --tail

# Restart Render service
# Go to Dashboard → Manual Deploy → Deploy Latest Commit
```

---

## Success Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Database user created with password
- [ ] Network access configured (0.0.0.0/0)
- [ ] Data migrated from MySQL to MongoDB
- [ ] Code pushed to GitHub
- [ ] Render/Railway account created
- [ ] Web service created and configured
- [ ] Environment variables added
- [ ] Application deployed successfully
- [ ] Login/registration tested
- [ ] Complaint submission tested
- [ ] Admin dashboard accessible

---

🎉 **Congratulations! Your application is now live!**
