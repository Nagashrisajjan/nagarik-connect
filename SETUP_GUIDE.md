# Nagarik Connect - Complete Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Initialize Database**
The SQLite database will be automatically created when you first run the app.

3. **Run the Application**
```bash
python app.py
```

4. **Access the Application**
- Main App: http://localhost:5000
- Admin Login: http://localhost:5000/admin
  - Username: `admin`
  - Password: `admin@123`

## 🔧 Configuration

### Environment Variables
Create a `.env` file (optional, defaults are provided):
```
SECRET_KEY=your_secret_key_here
PORT=5000
```

### Database
The application uses SQLite by default (`icgs_complaints.db`). No additional setup required.

## 📁 Project Structure

```
├── app.py                  # Main Flask application
├── database_sqlite.py      # SQLite database wrapper
├── config.py              # Configuration settings
├── translations.py        # Multi-language support
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
├── static/              # CSS, images, uploads
├── ml/                  # Machine learning models
└── netlify-frontend/    # Static frontend (optional)
```

## 🌐 Features

### User Features
- Register and login
- Submit complaints with images and location
- Track complaint status
- Provide feedback
- Multi-language support (English, Hindi, Kannada, Telugu, Tamil)

### Admin Features
- View all complaints
- Assign workers to complaints
- Update complaint status
- View analytics and statistics
- Manage feedback

### Department Admin Features
- Department-specific dashboard
- Manage department complaints
- Assign workers
- Update status

## 🔐 Default Credentials

### Super Admin
- URL: `/admin`
- Username: `admin`
- Password: `admin@123`

### Department Admins
Set up using: `python icgs_project3/setup_dept_admins.py`

## 🐛 Troubleshooting

### Issue: 404 Error on Stats API
**Fixed**: Added `/api/stats` endpoint in app.py

### Issue: Google APIs Error (ERR_INTERNET_DISCONNECTED)
**Solution**: This is a browser geolocation warning. The app works offline with manual location entry.

### Issue: Database Connection Errors
**Solution**: The app now uses SQLite by default. MongoDB code is wrapped for compatibility.

### Issue: Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production (Render/Heroku)
The app is configured with:
- `Procfile` for Heroku
- `render.yaml` for Render
- `runtime.txt` for Python version

Environment variables needed:
- `SECRET_KEY`: Your secret key
- `PORT`: Automatically set by platform

## 📊 API Endpoints

### Public Endpoints
- `GET /` - Home page with statistics
- `GET /api/stats` - JSON stats for frontend
- `POST /register` - User registration
- `POST /login` - User login

### Protected Endpoints
- `GET /user/dashboard` - User dashboard
- `POST /submit_complaint` - Submit new complaint
- `GET /admin/dashboard` - Admin dashboard
- `POST /assign_worker` - Assign worker to complaint

## 🌍 Multi-Language Support

Supported languages:
- English (en)
- Hindi (hi)
- Kannada (kn)
- Telugu (te)
- Tamil (ta)

Change language using the dropdown in the header.

## 📝 License

Government of India Initiative - Public Domain

## 🤝 Support

For issues or questions, contact: support@nagarikconnect.gov.in
