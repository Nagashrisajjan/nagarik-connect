# 🚀 ONE-COMMAND DEPLOYMENT

## Option 1: Railway (Easiest - One Command!)

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

### Step 2: Login
```bash
railway login
```
(Opens browser to login with GitHub)

### Step 3: Deploy!
```bash
railway init
railway up
```

### Step 4: Get Your Link
```bash
railway domain
```

**Done! You'll get a link like:** `https://your-app.up.railway.app`

---

## Option 2: Render (Via GitHub - No CLI needed)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Deploy ICGS app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Go to Render
1. Visit: https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect GitHub repo
4. Click "Create Web Service"

**Done! You'll get a link like:** `https://icgs-complaints-system.onrender.com`

---

## Option 3: Heroku (Classic)

### Step 1: Install Heroku CLI
Download from: https://devcenter.heroku.com/articles/heroku-cli

### Step 2: Login & Deploy
```bash
heroku login
heroku create icgs-complaints-app
git init
git add .
git commit -m "Deploy"
git push heroku main
heroku open
```

**Done! You'll get a link like:** `https://icgs-complaints-app.herokuapp.com`

---

## ⚡ FASTEST: Railway (Recommended)

Just run these 3 commands:
```bash
npm install -g @railway/cli
railway login
railway up
```

That's it! 🎉
