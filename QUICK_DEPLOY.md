# ⚡ Quick Deploy Guide (5 Minutes)

## 1️⃣ MongoDB Atlas Setup (2 minutes)

1. **Create Account**: https://www.mongodb.com/cloud/atlas/register
2. **Create Free Cluster** (M0 - Free tier)
3. **Database Access**: Add user with password
4. **Network Access**: Allow 0.0.0.0/0
5. **Get Connection Info**:
   - Username: `your_username`
   - Password: `your_password`  
   - Cluster: `cluster0.xxxxx.mongodb.net`

## 2️⃣ Migrate Data (1 minute)

```bash
# Update config.py with your MongoDB credentials
# Then run:
pip install pymongo dnspython
python migrate_to_mongodb.py
```

## 3️⃣ Deploy to Render (2 minutes)

1. **Push to GitHub**:
```bash
git init
git add .
git commit -m "Deploy to Render"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

2. **Deploy on Render**:
   - Go to https://render.com
   - Sign up with GitHub
   - New → Web Service
   - Connect your repo
   - Add environment variables:
     ```
     MONGODB_USERNAME=your_username
     MONGODB_PASSWORD=your_password
     MONGODB_CLUSTER=cluster0.xxxxx.mongodb.net
     MONGODB_DATABASE=icgs_complaints
     SECRET_KEY=random_secret_key_here
     ```
   - Click "Create Web Service"

3. **Done!** Your app will be live in 5-10 minutes at:
   `https://your-app-name.onrender.com`

---

## Environment Variables Needed

Copy these to Render dashboard:

```
MONGODB_USERNAME=your_mongodb_username
MONGODB_PASSWORD=your_mongodb_password
MONGODB_CLUSTER=cluster0.xxxxx.mongodb.net
MONGODB_DATABASE=icgs_complaints
SECRET_KEY=generate_random_string_here
PYTHON_VERSION=3.11.0
```

---

## Test Your Deployment

1. Visit your Render URL
2. Register a new user
3. Submit a complaint
4. Login as admin (if you have admin credentials)

---

## Common Issues

**"Application Error"**
→ Check Render logs, verify environment variables

**"Database Connection Failed"**  
→ Check MongoDB Atlas network access (0.0.0.0/0)

**"Module Not Found"**
→ Ensure requirements.txt is in root directory

---

## Need Help?

1. Check Render logs: Dashboard → Logs
2. Verify MongoDB connection in Atlas
3. Ensure all environment variables are set
4. Review full DEPLOYMENT_GUIDE.md for details
