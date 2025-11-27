import sqlite3
from datetime import datetime
import json
from contextlib import contextmanager

DATABASE_FILE = "icgs_complaints.db"

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initialize SQLite database with tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'citizen',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Complaints table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                user_name TEXT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                department TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                image TEXT,
                location TEXT,
                latitude TEXT,
                longitude TEXT,
                assigned_worker_id TEXT,
                assigned_worker_name TEXT,
                assigned_worker_phone TEXT,
                remarks TEXT,
                admin_image TEXT
            )
        ''')
        
        # Workers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                department TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Department admins table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dept_admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                department TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                image TEXT,
                rating TEXT,
                complaint_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                admin_reply TEXT,
                replied_at TEXT
            )
        ''')
        
        conn.commit()
        print("✅ SQLite database initialized successfully!")

def create_default_dept_admins():
    """Create default department admin accounts if they don't exist"""
    from werkzeug.security import generate_password_hash
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if admins already exist
        cursor.execute("SELECT COUNT(*) FROM dept_admins")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ Department admins already exist ({count} admins)")
            return
        
        # Create default department admins
        dept_admins = [
            {
                "name": "Water Department Admin",
                "username": "water_admin",
                "password": generate_password_hash("water123"),
                "department": "Water Crisis"
            },
            {
                "name": "Road Department Admin",
                "username": "road_admin",
                "password": generate_password_hash("road123"),
                "department": "Road Maintenance(Engg)"
            },
            {
                "name": "Garbage Department Admin",
                "username": "garbage_admin",
                "password": generate_password_hash("garbage123"),
                "department": "Solid Waste (Garbage) Related"
            },
            {
                "name": "Electrical Department Admin",
                "username": "electrical_admin",
                "password": generate_password_hash("electrical123"),
                "department": "Electrical"
            },
            {
                "name": "General Department Admin",
                "username": "general_admin",
                "password": generate_password_hash("general123"),
                "department": "General Department"
            }
        ]
        
        try:
            for admin in dept_admins:
                cursor.execute(
                    "INSERT INTO dept_admins (name, username, password, department) VALUES (?, ?, ?, ?)",
                    (admin["name"], admin["username"], admin["password"], admin["department"])
                )
            
            conn.commit()
            print(f"✅ Created {len(dept_admins)} department admin accounts")
        except Exception as e:
            print(f"❌ Error creating department admins: {e}")
            conn.rollback()

# Initialize database on import
init_db()
create_default_dept_admins()

class SQLiteDB:
    """SQLite Database wrapper to mimic MongoDB interface"""
    
    def __init__(self, table_name):
        self.table_name = table_name
    
    def find_one(self, query):
        """Find one document"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            where_clause, params = self._build_where(query)
            sql = f"SELECT * FROM {self.table_name} {where_clause} LIMIT 1"
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def find(self, query=None):
        """Find all documents matching query"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if query:
                where_clause, params = self._build_where(query)
                sql = f"SELECT * FROM {self.table_name} {where_clause}"
                cursor.execute(sql, params)
            else:
                cursor.execute(f"SELECT * FROM {self.table_name}")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def insert_one(self, document):
        """Insert one document"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            columns = ', '.join(document.keys())
            placeholders = ', '.join(['?' for _ in document])
            sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, list(document.values()))
            return type('Result', (), {'inserted_id': cursor.lastrowid})()
    
    def update_one(self, query, update):
        """Update one document"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            where_clause, where_params = self._build_where(query)
            
            if '$set' in update:
                set_data = update['$set']
                set_clause = ', '.join([f"{k} = ?" for k in set_data.keys()])
                sql = f"UPDATE {self.table_name} SET {set_clause} {where_clause}"
                cursor.execute(sql, list(set_data.values()) + where_params)
    
    def count_documents(self, query=None):
        """Count documents"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if query:
                where_clause, params = self._build_where(query)
                sql = f"SELECT COUNT(*) FROM {self.table_name} {where_clause}"
                cursor.execute(sql, params)
            else:
                cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            return cursor.fetchone()[0]
    
    def aggregate(self, pipeline):
        """Enhanced aggregation support for MongoDB-style queries"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Start with all records
            sql = f"SELECT * FROM {self.table_name}"
            params = []
            
            # Process pipeline stages
            for stage in pipeline:
                if "$match" in stage:
                    where_clause, where_params = self._build_where(stage["$match"])
                    if where_clause:
                        sql += f" {where_clause}"
                        params.extend(where_params)
                
                if "$sort" in stage:
                    sort_field = list(stage["$sort"].keys())[0]
                    sort_order = "DESC" if stage["$sort"][sort_field] == -1 else "ASC"
                    sql += f" ORDER BY {sort_field} {sort_order}"
                
                if "$limit" in stage:
                    sql += f" LIMIT {stage['$limit']}"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def _build_where(self, query):
        """Build WHERE clause from query dict"""
        if not query:
            return "", []
        
        conditions = []
        params = []
        
        for key, value in query.items():
            if isinstance(value, dict):
                if '$regex' in value:
                    conditions.append(f"{key} LIKE ?")
                    params.append(f"%{value['$regex']}%")
            else:
                conditions.append(f"{key} = ?")
                params.append(value)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        return where_clause, params

class Database:
    """Database wrapper"""
    def __init__(self):
        self.users = SQLiteDB('users')
        self.complaints = SQLiteDB('complaints')
        self.workers = SQLiteDB('workers')
        self.dept_admins = SQLiteDB('dept_admins')
        self.feedback = SQLiteDB('feedback')

def get_db():
    """Get database instance"""
    return Database()
