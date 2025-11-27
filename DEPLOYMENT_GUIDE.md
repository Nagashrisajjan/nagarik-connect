# 🚀 Deployment Guide - ICGS Complaints System

## ✅ Recommended: Deploy to Render.com

Your app is ready to deploy! Follow these steps:

---

## 📋 Pre-Deployment Checklist

- [x] Flask app with SQLite database
- [x] `render.yaml` configured
- [x] `requirements.txt` with all dependencies
- [x] `gunicorn` installed for production server
- [x] Database initialized with department admins

---

## 🌐 Deploy to Render.com (FREE)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub account
3. Authorize Render to access your repositories

### Step 3: Deploy
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Render will auto-detect `render.yaml`
4. Click **"Apply"** to use the configuration
5. Click **"Create Web Service"**

### Step 4: Wait for Build
- First build takes 3-5 minutes
- Watch the logs for any errors
- Once deployed, you'll get a URL like: `https://icgs-complaints-system.onrender.com`

---

## 🔧 Important Notes

### SQLite Database Persistence
- Your `render.yaml` includes a persistent disk
- Database file `icgs_complaints.db` will be saved
- Data persists across deployments

### Free Tier Limitations
- App sleeps after 15 minutes of inactivity
- Wakes up in ~30 seconds on first request
- 750 hours/month free (enough for 24/7)

### Department Admin Credentials
After deployment, these accounts will be available:
- Username: `water_admin` / Password: `water123`
- Username: `road_admin` / Password: `road123`
- Username: `garbage_admin` / Password: `garbage123`
- Username: `electrical_admin` / Password: `electrical123`
- Username: `general_admin` / Password: `general123`

---

## 🔄 Alternative: Railway.app

If Render doesn't work, try Railway:

1. Go to https://railway.app
2. Sign in with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Railway auto-detects Flask app
6. Add environment variable: `SECRET_KEY` = (any random string)
7. Deploy!

---

## 🐍 Alternative: PythonAnywhere

For a Python-specific host:

1. Go to https://www.pythonanywhere.com
2. Create free account
3. Upload your code via Git or file upload
4. Configure WSGI file to point to `app:app`
5. Set working directory
6. Reload web app

---

## 🧪 Test After Deployment

1. Visit your deployed URL
2. Test citizen registration and login
3. Test department admin login
4. Submit a test complaint
5. Check admin dashboard
6. Verify ML predictions work

---

## 🆘 Troubleshooting

### If deployment fails:
1. Check Render logs for errors
2. Ensure all files are committed to Git
3. Verify `requirements.txt` has all dependencies
4. Check Python version compatibility

### If database is empty:
- The database initializes automatically on first run
- Department admins are created by `database_sqlite.py`
- Check logs to confirm initialization

### If ML models don't load:
- TensorFlow/scikit-learn may take time to install
- Check build logs for memory issues
- Consider using Railway (more resources on free tier)

---

## 📊 Monitor Your App

After deployment:
- Check Render dashboard for metrics
- View logs for errors
- Monitor response times
- Set up alerts for downtime

---

## 🎉 You're Ready!

Your app is production-ready with:
- ✅ SQLite database with persistent storage
- ✅ Department admin accounts pre-configured
- ✅ ML-powered complaint routing
- ✅ Multi-language support
- ✅ Image upload functionality
- ✅ Responsive design

**Next Step**: Push to GitHub and deploy to Render! 🚀
