"""
Script to create department admin accounts in the database
Run this once to set up department admins
"""
import mysql.connector
from werkzeug.security import generate_password_hash

def setup_department_admins():
    # Database connection
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="updatedicgs"
    )
    cursor = conn.cursor()
    
    # Create department_admins table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS department_admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            department VARCHAR(100) NOT NULL,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Department admin accounts
    dept_admins = [
        {
            'username': 'water_admin',
            'password': 'water123',
            'department': 'Water Crisis',
            'name': 'Water Department Admin',
            'email': 'water@nagarik.gov.in'
        },
        {
            'username': 'road_admin',
            'password': 'road123',
            'department': 'Road Maintenance(Engg)',
            'name': 'Road Department Admin',
            'email': 'road@nagarik.gov.in'
        },
        {
            'username': 'garbage_admin',
            'password': 'garbage123',
            'department': 'Solid Waste (Garbage) Related',
            'name': 'Garbage Department Admin',
            'email': 'garbage@nagarik.gov.in'
        },
        {
            'username': 'electrical_admin',
            'password': 'electrical123',
            'department': 'Electrical',
            'name': 'Electrical Department Admin',
            'email': 'electrical@nagarik.gov.in'
        },
        {
            'username': 'general_admin',
            'password': 'general123',
            'department': 'General Department',
            'name': 'General Department Admin',
            'email': 'general@nagarik.gov.in'
        }
    ]
    
    # Insert department admins
    for admin in dept_admins:
        hashed_password = generate_password_hash(admin['password'])
        try:
            cursor.execute("""
                INSERT INTO department_admins (username, password, department, name, email)
                VALUES (%s, %s, %s, %s, %s)
            """, (admin['username'], hashed_password, admin['department'], admin['name'], admin['email']))
            print(f"✅ Created: {admin['username']} - {admin['department']}")
        except mysql.connector.IntegrityError:
            print(f"⚠️  Already exists: {admin['username']}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print("Department Admin Accounts Created Successfully!")
    print("="*60)
    print("\nLogin Credentials:")
    print("-" * 60)
    for admin in dept_admins:
        print(f"Department: {admin['department']}")
        print(f"Username: {admin['username']}")
        print(f"Password: {admin['password']}")
        print("-" * 60)

if __name__ == "__main__":
    setup_department_admins()
