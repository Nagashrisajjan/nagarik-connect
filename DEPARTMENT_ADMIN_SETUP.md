# Department Admin System - Setup Guide

## Overview
This system provides separate dashboards for each department with individual admin credentials.

## Features
✅ Separate login for each department admin
✅ Department-specific complaint management
✅ Worker assignment and tracking
✅ Status updates with remarks
✅ Charts and analytics for each department
✅ Monthly trend analysis
✅ Image upload functionality

## Setup Instructions

### Step 1: Create Department Admin Accounts

Run the setup script to create department admin accounts in your database:

```bash
python icgs_project3/setup_dept_admins.py
```

This will create the `department_admins` table and insert admin accounts for all departments.

### Step 2: Department Admin Credentials

After running the setup script, you'll have these accounts:

| Department | Username | Password |
|------------|----------|----------|
| Water Crisis | water_admin | water123 |
| Road Maintenance(Engg) | road_admin | road123 |
| Solid Waste (Garbage) Related | garbage_admin | garbage123 |
| Electrical | electrical_admin | electrical123 |
| General Department | general_admin | general123 |

### Step 3: Access Department Dashboards

1. **Start the Flask application:**
   ```bash
   python icgs_project3/app.py
   ```

2. **Navigate to Department Admin Login:**
   - URL: `http://localhost:5000/dept_admin/login`
   - Or click "🏢 Dept Admin" button on the home page

3. **Login with department credentials**

4. **Access your department dashboard**

## Department Admin Features

### Dashboard Overview
- **Statistics Cards**: Total, Pending, In Progress, Resolved complaints
- **Status Chart**: Pie chart showing complaint distribution
- **Trend Chart**: Monthly complaint trends (last 6 months)
- **Workers Section**: List of assigned workers with complaint counts
- **Complaints Table**: Full complaint management interface

### Complaint Management
- View all complaints for your department
- Update complaint status (Pending → In Progress → Resolved)
- Add remarks to complaints
- Upload admin images
- Assign workers to complaints
- View user-uploaded images
- Access GPS location on Google Maps

### Worker Management
- Add new workers to your department
- Assign workers to specific complaints
- Track worker performance (complaint count)

## System Architecture

### Database Tables

#### department_admins
```sql
CREATE TABLE department_admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/dept_admin/login` | GET, POST | Department admin login |
| `/dept_admin/dashboard` | GET | Department dashboard |
| `/dept_admin/update_status/<id>` | POST | Update complaint status |
| `/dept_admin/upload_image/<id>` | POST | Upload admin image |
| `/dept_admin/add_worker` | POST | Add and assign worker |
| `/dept_admin/feedback` | GET, POST | View and reply to feedback |

## User Flow

### For Citizens
1. Register/Login as citizen
2. Submit complaint with title, description, location, image
3. ML model automatically assigns complaint to appropriate department
4. Track complaint status in user dashboard
5. View assigned worker details
6. Provide feedback

### For Department Admins
1. Login with department credentials
2. View department-specific dashboard
3. See all complaints assigned to department
4. Assign workers to complaints
5. Update status and add remarks
6. Upload resolution images
7. Monitor department performance through charts

### For Super Admin
1. Login with super admin credentials (admin/admin@123)
2. View all complaints across all departments
3. See department-wise analytics
4. Manage all workers
5. Access comprehensive reports

## Security Features

- Password hashing using Werkzeug security
- Session-based authentication
- Role-based access control (citizen, dept_admin, admin)
- Department-specific data isolation
- Secure file uploads

## Customization

### Adding New Departments

1. **Update setup_dept_admins.py:**
   ```python
   {
       'username': 'new_dept_admin',
       'password': 'newdept123',
       'department': 'New Department Name',
       'name': 'New Department Admin',
       'email': 'newdept@nagarik.gov.in'
   }
   ```

2. **Run the setup script again:**
   ```bash
   python icgs_project3/setup_dept_admins.py
   ```

3. **Update ML model** to recognize new department

### Changing Passwords

Use Python to generate new password hash:
```python
from werkzeug.security import generate_password_hash
new_hash = generate_password_hash('new_password')
print(new_hash)
```

Then update in database:
```sql
UPDATE department_admins 
SET password = 'new_hash_here' 
WHERE username = 'water_admin';
```

## Troubleshooting

### Issue: Cannot login as department admin
**Solution:** Ensure you've run the setup script and the department_admins table exists

### Issue: No complaints showing in department dashboard
**Solution:** Check that complaints are being assigned to the correct department name (exact match required)

### Issue: Charts not displaying
**Solution:** Ensure Chart.js is loading properly and there's data in the database

### Issue: Worker assignment not working
**Solution:** Verify workers table exists and department names match exactly

## Support

For issues or questions:
- Check the Flask console for error messages
- Verify database connections
- Ensure all required tables exist
- Check that ML model is working for department prediction

## Future Enhancements

- Email notifications for department admins
- SMS alerts for workers
- Advanced analytics and reporting
- Export functionality (PDF/Excel)
- Mobile app for workers
- Real-time updates using WebSockets
- Department performance metrics
- SLA tracking and alerts
