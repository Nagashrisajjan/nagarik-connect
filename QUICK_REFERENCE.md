# 🚀 Nagarik Connect - Quick Reference Card

## ⚡ Quick Commands

### Start Application
```bash
# Windows
run_app.bat

# Linux/Mac
./run_app.sh

# Manual
python app.py
```

### Test Setup
```bash
python test_setup.py
```

### Access Points
- **Main App**: http://localhost:5000
- **Admin**: http://localhost:5000/admin (admin / admin@123)
- **API Stats**: http://localhost:5000/api/stats

## 📁 Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main Flask application |
| `database_sqlite.py` | Database wrapper |
| `config.py` | Configuration settings |
| `translations.py` | Multi-language support |
| `requirements.txt` | Python dependencies |
| `test_setup.py` | Automated tests |

## 🗂️ Database Tables

| Table | Description |
|-------|-------------|
| `users` | User accounts |
| `complaints` | Citizen complaints |
| `workers` | Department workers |
| `dept_admins` | Department admins |
| `feedback` | User feedback |

## 🔐 User Roles

| Role | Access Level |
|------|--------------|
| **Super Admin** | Full system access |
| **Dept Admin** | Department-specific access |
| **Citizen** | Submit & track complaints |

## 🌐 Main Routes

### Public
```
GET  /                    Home page
GET  /api/stats           JSON stats
POST /register            User registration
POST /login               User login
```

### User (Requires Login)
```
GET  /user/dashboard      User dashboard
POST /submit_complaint    Submit complaint
GET  /feedback            Feedback page
```

### Admin (Requires Admin Role)
```
GET  /admin/dashboard     Admin dashboard
POST /assign_worker       Assign worker
POST /update_status/<id>  Update status
```

## 🛠️ Common Tasks

### Add New User
1. Go to http://localhost:5000/register
2. Fill in details
3. Click Register

### Submit Complaint
1. Login as user
2. Click "Lodge Complaint"
3. Fill form with title, description, image
4. Submit

### Assign Worker (Admin)
1. Login as admin
2. View complaint
3. Select worker from dropdown
4. Click Assign

### Update Status (Admin)
1. Login as admin
2. Find complaint
3. Change status dropdown
4. Click Update

## 🐛 Quick Fixes

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### Module Not Found
```bash
pip install -r requirements.txt
```

### Database Reset
```bash
# Windows
del icgs_complaints.db
python app.py

# Linux/Mac
rm icgs_complaints.db
python app.py
```

### Clear Browser Cache
```
Ctrl + Shift + Delete (Windows/Linux)
Cmd + Shift + Delete (Mac)
```

## 📊 Status Values

| Status | Meaning |
|--------|---------|
| `Pending` | Newly submitted |
| `In Progress` | Being worked on |
| `Resolved` | Completed |

## 🏢 Departments

- Water Crisis
- Road Maintenance (Engg)
- Solid Waste (Garbage) Related
- Electrical
- General Department

## 🌍 Language Codes

| Code | Language |
|------|----------|
| `en` | English |
| `hi` | Hindi |
| `kn` | Kannada |
| `te` | Telugu |
| `ta` | Tamil |

## 🔧 Environment Variables

```bash
SECRET_KEY=your_secret_key
PORT=5000
FLASK_ENV=production
```

## 📦 Dependencies

### Core
- Flask 3.0.3
- Werkzeug 3.0.3
- Flask-Babel 4.0.0
- Gunicorn 21.2.0

### ML (Optional)
- scikit-learn 1.3.0
- transformers 4.30.0
- torch 2.0.0

## 🧪 Test Checklist

- [ ] Server starts without errors
- [ ] Home page loads
- [ ] User registration works
- [ ] User login works
- [ ] Complaint submission works
- [ ] Admin login works
- [ ] Worker assignment works
- [ ] Status update works
- [ ] Feedback submission works
- [ ] API endpoint returns data

## 📝 Code Snippets

### Get Database Connection
```python
from database_sqlite import get_db

db = get_db()
users = db.users.find({})
```

### Add New Route
```python
@app.route("/new_route")
def new_route():
    return render_template("new_template.html")
```

### Query Complaints
```python
db = get_db()
complaints = db.complaints.find({"status": "Pending"})
```

### Update Complaint
```python
db = get_db()
db.complaints.update_one(
    {"id": complaint_id},
    {"$set": {"status": "Resolved"}}
)
```

## 🚀 Deployment Commands

### Render
```bash
git push origin main
```

### Heroku
```bash
heroku create app-name
git push heroku main
```

### Local Production
```bash
gunicorn app:app
```

## 📞 Support Contacts

- **Email**: support@nagarikconnect.gov.in
- **Phone**: 1800-XXX-XXXX

## 🔗 Useful Links

- [Full Documentation](SETUP_GUIDE.md)
- [Architecture](PROJECT_ARCHITECTURE.md)
- [Fixes Applied](FIXES_APPLIED.md)
- [README](README.md)

## 💡 Tips

1. **Always test locally** before deploying
2. **Change default passwords** in production
3. **Backup database** regularly
4. **Monitor logs** for errors
5. **Use HTTPS** in production
6. **Keep dependencies updated**
7. **Test on multiple browsers**
8. **Validate user input**
9. **Handle errors gracefully**
10. **Document your changes**

## ⚠️ Common Mistakes

❌ Forgetting to activate virtual environment
❌ Not installing dependencies
❌ Using default admin password in production
❌ Not setting SECRET_KEY
❌ Hardcoding sensitive data
❌ Not handling file upload errors
❌ Ignoring database backups
❌ Not testing on mobile devices

## ✅ Best Practices

✓ Use virtual environment
✓ Keep requirements.txt updated
✓ Write meaningful commit messages
✓ Test before committing
✓ Use environment variables
✓ Validate all inputs
✓ Handle exceptions properly
✓ Log important events
✓ Comment complex code
✓ Follow PEP 8 style guide

---

**Last Updated**: 2025-11-27
**Version**: 1.0.0

For detailed information, see [SETUP_GUIDE.md](SETUP_GUIDE.md)
