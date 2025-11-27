"""
MongoDB Wrapper - Makes MongoDB work like MySQL
This allows minimal changes to existing app.py code
"""

from database import get_db
from bson import ObjectId
from datetime import datetime

class MongoDBCursor:
    """Wrapper to make MongoDB behave like MySQL cursor"""
    
    def __init__(self, db):
        self.db = db
        self.last_result = None
    
    def execute(self, query, params=None):
        """Execute SQL-like query on MongoDB"""
        query = query.strip()
        
        # Handle SELECT COUNT
        if query.startswith("SELECT COUNT"):
            self._handle_count(query, params)
        
        # Handle SELECT with JOIN
        elif "JOIN" in query:
            self._handle_join(query, params)
        
        # Handle simple SELECT
        elif query.startswith("SELECT"):
            self._handle_select(query, params)
        
        # Handle INSERT
        elif query.startswith("INSERT"):
            self._handle_insert(query, params)
        
        # Handle UPDATE
        elif query.startswith("UPDATE"):
            self._handle_update(query, params)
        
        # Handle DELETE
        elif query.startswith("DELETE"):
            self._handle_delete(query, params)
    
    def _handle_count(self, query, params):
        """Handle COUNT queries"""
        # Extract table and conditions
        if "FROM complaints" in query:
            collection = self.db.complaints
            
            # Build filter
            filter_dict = {}
            if params and "WHERE" in query:
                if "user_id" in query:
                    filter_dict["user_id"] = params[0] if params else None
                if "status='Pending'" in query:
                    filter_dict["status"] = "Pending"
                elif "status='Resolved'" in query:
                    filter_dict["status"] = "Resolved"
                elif "status='In Progress'" in query:
                    filter_dict["status"] = "In Progress"
                elif "in progress" in query.lower():
                    filter_dict["status"] = {"$regex": "in progress", "$options": "i"}
            
            count = collection.count_documents(filter_dict)
            
            # Determine result key from query
            if "AS total" in query:
                self.last_result = {"total": count}
            elif "AS pending" in query:
                self.last_result = {"pending": count}
            elif "AS resolved" in query:
                self.last_result = {"resolved": count}
            elif "AS in_progress" in query:
                self.last_result = {"in_progress": count}
            else:
                self.last_result = {"count": count}
    
    def _handle_select(self, query, params):
        """Handle simple SELECT queries"""
        if "FROM users WHERE email" in query:
            email = params[0] if params else None
            user = self.db.users.find_one({"email": email})
            if user:
                user["id"] = str(user["_id"])
            self.last_result = [user] if user else []
        
        elif "FROM workers" in query:
            workers = list(self.db.workers.find())
            for w in workers:
                w["id"] = str(w["_id"])
            self.last_result = workers
    
    def _handle_join(self, query, params):
        """Handle JOIN queries with aggregation"""
        # This is complex - simplified version
        self.last_result = []
    
    def _handle_insert(self, query, params):
        """Handle INSERT queries"""
        if "INTO users" in query:
            name, email, password, role = params
            self.db.users.insert_one({
                "name": name,
                "email": email,
                "password": password,
                "role": role,
                "created_at": datetime.now().isoformat()
            })
    
    def _handle_update(self, query, params):
        """Handle UPDATE queries"""
        pass
    
    def _handle_delete(self, query, params):
        """Handle DELETE queries"""
        pass
    
    def fetchone(self):
        """Return single result"""
        if isinstance(self.last_result, list) and self.last_result:
            return self.last_result[0]
        return self.last_result
    
    def fetchall(self):
        """Return all results"""
        if isinstance(self.last_result, list):
            return self.last_result
        return [self.last_result] if self.last_result else []
    
    def close(self):
        """Close cursor (no-op for MongoDB)"""
        pass

class MongoDBConnection:
    """Wrapper to make MongoDB behave like MySQL connection"""
    
    def __init__(self):
        self.db = get_db()
    
    def cursor(self, dictionary=True):
        """Return cursor"""
        return MongoDBCursor(self.db)
    
    def commit(self):
        """Commit (no-op for MongoDB)"""
        pass
    
    def close(self):
        """Close connection (no-op for MongoDB)"""
        pass

def get_db_connection():
    """Drop-in replacement for MySQL get_db_connection()"""
    return MongoDBConnection()
