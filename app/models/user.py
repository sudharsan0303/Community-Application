import sqlite3
from .database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, id=None, email=None, name=None, phone=None, 
                 address=None, profile_picture=None, user_type=None, password_hash=None,
                 created_at=None, updated_at=None, location=None):
        self.id = id
        self.email = email
        self.name = name
        self.phone = phone
        self.address = address
        self.profile_picture = profile_picture
        self.user_type = user_type
        self.password_hash = password_hash
        self.created_at = created_at
        self.updated_at = updated_at
        self.location = location
    
    @staticmethod
    def create(email, name, password, user_type, phone=None, address=None, profile_picture=None, location=None):
        """Create a new user in the database with local authentication"""
        if not email or not name or not password or not user_type:
            raise ValueError('All required fields must be provided')
            
        # Validate user type
        if user_type not in ['user', 'helper', 'admin']:
            raise ValueError('Invalid user type')
            
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if email already exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                raise ValueError('Email address already registered')
                
            # Hash the password
            password_hash = generate_password_hash(password)
            
            # Insert new user
            cursor.execute('''
                INSERT INTO users (email, name, phone, address, profile_picture, user_type, password_hash, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, name, phone, address, profile_picture, user_type, password_hash, location))
            
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
            
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise Exception(f'Database error: {str(e)}')
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return User(
                id=user_data['id'],
                email=user_data['email'],
                name=user_data['name'],
                phone=user_data['phone'],
                address=user_data['address'],
                profile_picture=user_data['profile_picture'],
                user_type=user_data['user_type'],
                created_at=user_data['created_at'],
                updated_at=user_data['updated_at'],
                location=user_data['location']
            )
        return None
    
    @staticmethod
    def get_all():
        """Get all users"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users')
        users_data = cursor.fetchall()
        conn.close()
        
        users = []
        for user_data in users_data:
            users.append(User(
                id=user_data['id'],
                email=user_data['email'],
                name=user_data['name'],
                phone=user_data['phone'],
                address=user_data['address'],
                profile_picture=user_data['profile_picture'],
                user_type=user_data['user_type'],
                created_at=user_data['created_at'],
                updated_at=user_data['updated_at'],
                location=user_data['location']
            ))
        return users
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return User(
                id=user_data['id'],
                email=user_data['email'],
                name=user_data['name'],
                phone=user_data['phone'],
                address=user_data['address'],
                profile_picture=user_data['profile_picture'],
                user_type=user_data['user_type'],
                password_hash=user_data['password_hash'],
                created_at=user_data['created_at'],
                updated_at=user_data['updated_at'],
                location=user_data['location']
            )
        return None
    
    def update(self):
        """Update user information"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE users
        SET name = ?, phone = ?, address = ?, profile_picture = ?, location = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (self.name, self.phone, self.address, self.profile_picture, self.location, self.id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def verify_password(self, password):
        """Verify the user's password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'profile_picture': self.profile_picture,
            'user_type': self.user_type,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'location': self.location
        }