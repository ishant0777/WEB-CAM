import sqlite3
import bcrypt
from datetime import datetime
import json

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Detection logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_name TEXT NOT NULL,
                objects_detected TEXT NOT NULL,
                confidence_scores TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Camera status table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS camera_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_name TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create default admin user
        self.create_user('admin', 'admin123')
        
        conn.commit()
        conn.close()
    
    def create_user(self, username, password):
        """Create a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                'INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)',
                (username, password_hash)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return bcrypt.checkpw(password.encode('utf-8'), result[0])
            return False
        except Exception as e:
            print(f"Error verifying user: {e}")
            return False
    
    def log_detection(self, camera_name, objects, confidences):
        """Log object detection results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO detection_logs (camera_name, objects_detected, confidence_scores)
                VALUES (?, ?, ?)
            ''', (camera_name, json.dumps(objects), json.dumps(confidences)))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging detection: {e}")
    
    def update_camera_status(self, camera_name, status):
        """Update camera status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO camera_status (camera_name, status, last_seen)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (camera_name, status))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating camera status: {e}")
    
    def get_detection_history(self, camera_name=None, limit=100):
        """Get detection history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if camera_name:
                cursor.execute('''
                    SELECT * FROM detection_logs 
                    WHERE camera_name = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (camera_name, limit))
            else:
                cursor.execute('''
                    SELECT * FROM detection_logs 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"Error getting detection history: {e}")
            return []
