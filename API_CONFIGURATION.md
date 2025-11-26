# 🔌 API Configuration & Deployment Checklist

## Required Services & APIs

### 1. MongoDB Atlas (Database) ✅
**Purpose**: Cloud database to replace local MySQL  
**Free Tier**: Yes (512MB storage)  
**Setup**: https://www.mongodb.com/cloud/atlas

**What you need**:
- Username
- Password
- Cluster URL (e.g., cluster0.xxxxx.mongodb.net)
- Database name: `icgs_complaints`

**Environment Variables**:
```
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
MONGODB_CLUSTER=cluster0.xxxxx.mongodb.net
MONGODB_DATABASE=icgs_complaints
```

---

### 2. Render / Railway / Heroku (Hosting) ✅
**Purpose**: Host your Flask application  
**Free Tier**: Yes  
**Recommended**: Render (easiest for Flask)

**Render**: https://render.com  
**Railway**: https://railway.app  
**Heroku**: https://heroku.com

---

### 3. GitHub (Code Repository) ✅
**Purpose**: Store code and connect to hosting platform  
**Free**: Yes  
**Setup**: https://github.com

---

## APIs Currently Used in Your App

### Local APIs (Need to be replaced/configured):

1. **MySQL Database** → **MongoDB Atlas** ✅
   - Status: Migration script created
   - Action: Run `migrate_to_mongodb.py`

2. **File Storage (static/uploads)** → **Cloud Storage (Optional)**
   - Current: Local file system
   - Issue: Files lost on free tier restarts
   - Solutions:
     - **Cloudinary** (Free tier: 25GB storage)
     - **AWS S3** (Free tier: 5GB for 12 months)
     - **Keep local** (acceptable for testing)

---

## Optional APIs for Production

### 1. Cloudinary (Image/Video Storage)
**Purpose**: Store uploaded complaint images/videos  
**Free Tier**: 25GB storage, 25GB bandwidth/month  
**Setup**: https://cloudinary.com

**Environment Variables**:
```
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

**Integration** (if needed):
```bash
pip install cloudinary
```

---

### 2. SendGrid / Mailgun (Email Notifications)
**Purpose**: Send email notifications for complaint updates  
**Free Tier**: SendGrid (100 emails/day)  
**Setup**: https://sendgrid.com

**Environment Variables**:
```
SENDGRID_API_KEY=your_api_key
FROM_EMAIL=noreply@nagarikconnect.com
```

---

### 3. Twilio (SMS Notifications)
**Purpose**: Send SMS updates to users  
**Free Tier**: Trial credits  
**Setup**: https://twilio.com

**Environment Variables**:
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

---

### 4. Google Maps API (Location Services)
**Purpose**: Enhanced location mapping  
**Free Tier**: $200 credit/month  
**Setup**: https://console.cloud.google.com

**Environment Variables**:
```
GOOGLE_MAPS_API_KEY=your_api_key
```

---

## Current App Configuration

### Files Created for Deployment:
- ✅ `config.py` - Configuration management
- ✅ `database.py` - MongoDB connection handler
- ✅ `migrate_to_mongodb.py` - Data migration script
- ✅ `requirements.txt` - Updated with MongoDB dependencies
- ✅ `Procfile` - Deployment configuration
- ✅ `runtime.txt` - Python version specification
- ✅ `render.yaml` - Render deployment config
- ✅ `.env.example` - Environment variables template
- ✅ `.gitignore` - Git ignore rules
- ✅ `DEPLOYMENT_GUIDE.md` - Full deployment instructions
- ✅ `QUICK_DEPLOY.md` - Quick start guide

---

## Minimum Required for Deployment

### Essential (Must Have):
1. ✅ MongoDB Atlas account + credentials
2. ✅ Render/Railway/Heroku account
3. ✅ GitHub repository
4. ✅ Environment variables configured

### Optional (Nice to Have):
1. ⚪ Cloudinary for image storage
2. ⚪ SendGrid for email notifications
3. ⚪ Custom domain name
4. ⚪ Google Analytics

---

## Environment Variables Checklist

Copy this to your hosting platform (Render/Railway/Heroku):

```bash
# Required
MONGODB_USERNAME=your_mongodb_username
MONGODB_PASSWORD=your_mongodb_password
MONGODB_CLUSTER=cluster0.xxxxx.mongodb.net
MONGODB_DATABASE=icgs_complaints
SECRET_KEY=generate_random_secret_key_here
PYTHON_VERSION=3.11.0

# Optional (for production)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
SENDGRID_API_KEY=your_sendgrid_key
FROM_EMAIL=noreply@nagarikconnect.com
```

---

## Deployment Steps Summary

### Step 1: Setup MongoDB Atlas
1. Create account
2. Create free cluster
3. Add database user
4. Configure network access (0.0.0.0/0)
5. Get connection credentials

### Step 2: Migrate Data
```bash
# Update config.py with MongoDB credentials
python migrate_to_mongodb.py
```

### Step 3: Push to GitHub
```bash
git init
git add .
git commit -m "Initial deployment"
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### Step 4: Deploy to Render
1. Sign up at render.com
2. New Web Service
3. Connect GitHub repo
4. Add environment variables
5. Deploy

### Step 5: Test
- Visit your deployed URL
- Test registration/login
- Submit complaint
- Check admin dashboard

---

## Cost Breakdown (Free Tier)

| Service | Free Tier | Limits |
|---------|-----------|--------|
| MongoDB Atlas | ✅ Free | 512MB storage |
| Render | ✅ Free | 750 hours/month, sleeps after 15min |
| Railway | ✅ Free | 500 hours/month, $5 credit |
| Heroku | ✅ Free | 550-1000 hours/month |
| GitHub | ✅ Free | Unlimited public repos |
| Cloudinary | ✅ Free | 25GB storage |
| SendGrid | ✅ Free | 100 emails/day |

**Total Cost**: $0/month for basic deployment! 🎉

---

## Production Upgrade Path

When you outgrow free tier:

1. **Render Pro**: $7/month (no sleep, better performance)
2. **MongoDB Atlas M10**: $0.08/hour (~$57/month)
3. **Cloudinary Plus**: $89/month (100GB storage)
4. **Custom Domain**: $10-15/year

---

## Security Checklist

- [ ] Strong SECRET_KEY generated
- [ ] MongoDB credentials secured
- [ ] .env file in .gitignore
- [ ] HTTPS enabled (automatic on Render)
- [ ] MongoDB network access configured
- [ ] No hardcoded passwords in code
- [ ] Environment variables used for all secrets

---

## Next Steps

1. ✅ Read DEPLOYMENT_GUIDE.md for detailed instructions
2. ✅ Read QUICK_DEPLOY.md for 5-minute setup
3. ✅ Setup MongoDB Atlas
4. ✅ Run migration script
5. ✅ Deploy to Render
6. ✅ Test your live application

---

## Support Resources

- **MongoDB Atlas Docs**: https://docs.atlas.mongodb.com
- **Render Docs**: https://render.com/docs
- **Flask Deployment**: https://flask.palletsprojects.com/en/latest/deploying/
- **Python Deployment**: https://realpython.com/python-web-applications/

---

🚀 **You're ready to deploy! Follow QUICK_DEPLOY.md to get started.**
