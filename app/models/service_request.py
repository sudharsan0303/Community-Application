from .database import get_db_connection
from datetime import datetime

class ServiceRequest:
    def __init__(self, id=None, user_id=None, helper_id=None, category=None, title=None,
                 description=None, deadline=None, status='open', created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.helper_id = helper_id
        self.category = category
        self.title = title
        self.description = description
        self.deadline = deadline
        self.status = status
        self.created_at = self._convert_to_datetime(created_at)
        self.updated_at = self._convert_to_datetime(updated_at)
    
    def _convert_to_datetime(self, date_value):
        """Convert string date to datetime object"""
        if date_value is None:
            return None
        if isinstance(date_value, datetime):
            return date_value
        if isinstance(date_value, str):
            try:
                # Try different date formats that SQLite might use
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d']:
                    try:
                        return datetime.strptime(date_value, fmt)
                    except ValueError:
                        continue
                # If no format matches, return the string
                return date_value
            except Exception:
                return date_value
        return date_value
    
    @staticmethod
    def create(user_id, category, title, description, deadline=None):
        """Create a new service request"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO service_requests (user_id, category, title, description, deadline)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, category, title, description, deadline))
        
        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return request_id
    
    @staticmethod
    def get_by_id(request_id):
        """Get service request by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM service_requests WHERE id = ?', (request_id,))
        request_data = cursor.fetchone()
        conn.close()
        
        if request_data:
            return ServiceRequest(
                id=request_data['id'],
                user_id=request_data['user_id'],
                helper_id=request_data['helper_id'],
                category=request_data['category'],
                title=request_data['title'],
                description=request_data['description'],
                deadline=request_data['deadline'],
                status=request_data['status'],
                created_at=request_data['created_at'],
                updated_at=request_data['updated_at']
            )
        return None
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get all service requests for a specific user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM service_requests WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        requests_data = cursor.fetchall()
        conn.close()
        
        requests = []
        for request_data in requests_data:
            requests.append(ServiceRequest(
                id=request_data['id'],
                user_id=request_data['user_id'],
                helper_id=request_data['helper_id'],
                category=request_data['category'],
                title=request_data['title'],
                description=request_data['description'],
                deadline=request_data['deadline'],
                status=request_data['status'],
                created_at=request_data['created_at'],
                updated_at=request_data['updated_at']
            ))
        return requests
    
    @staticmethod
    def get_by_helper_id(helper_id):
        """Get all service requests assigned to a specific helper"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM service_requests WHERE helper_id = ? ORDER BY created_at DESC', (helper_id,))
        requests_data = cursor.fetchall()
        conn.close()
        
        requests = []
        for request_data in requests_data:
            requests.append(ServiceRequest(
                id=request_data['id'],
                user_id=request_data['user_id'],
                helper_id=request_data['helper_id'],
                category=request_data['category'],
                title=request_data['title'],
                description=request_data['description'],
                deadline=request_data['deadline'],
                status=request_data['status'],
                created_at=request_data['created_at'],
                updated_at=request_data['updated_at']
            ))
        return requests
    
    @staticmethod
    def get_open_requests():
        """Get all open service requests"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM service_requests WHERE status = "open" ORDER BY created_at DESC')
        requests_data = cursor.fetchall()
        conn.close()
        
        requests = []
        for request_data in requests_data:
            requests.append(ServiceRequest(
                id=request_data['id'],
                user_id=request_data['user_id'],
                helper_id=request_data['helper_id'],
                category=request_data['category'],
                title=request_data['title'],
                description=request_data['description'],
                deadline=request_data['deadline'],
                status=request_data['status'],
                created_at=request_data['created_at'],
                updated_at=request_data['updated_at']
            ))
        return requests
    
    def assign_helper(self, helper_id):
        """Assign a helper to this service request"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE service_requests
        SET helper_id = ?, status = "assigned", updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (helper_id, self.id))
        
        conn.commit()
        conn.close()
        
        self.helper_id = helper_id
        self.status = "assigned"
        return True
    
    def update_status(self, status):
        """Update the status of this service request"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE service_requests
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (status, self.id))
        
        conn.commit()
        conn.close()
        
        self.status = status
        return True
    
    def to_dict(self):
        """Convert service request object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'helper_id': self.helper_id,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def get_available_for_helper(helper_id):
        """Get available service requests (open status, not assigned to this helper)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM service_requests 
        WHERE status = 'open' AND (helper_id IS NULL OR helper_id != ?)
        ORDER BY created_at DESC
        ''', (helper_id,))
        
        requests = []
        for row in cursor.fetchall():
            requests.append(ServiceRequest(
                id=row['id'],
                user_id=row['user_id'],
                helper_id=row['helper_id'],
                category=row['category'],
                title=row['title'],
                description=row['description'],
                deadline=row['deadline'],
                status=row['status'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            ))
        
        conn.close()
        return requests