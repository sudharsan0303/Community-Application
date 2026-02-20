from .database import get_db_connection

class Complaint:
    def __init__(self, id=None, user_id=None, helper_id=None, service_request_id=None,
                 description=None, status='pending', resolution=None, created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.helper_id = helper_id
        self.service_request_id = service_request_id
        self.description = description
        self.status = status
        self.resolution = resolution
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def create(user_id, helper_id, service_request_id, description):
        """Create a new complaint"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO complaints (user_id, helper_id, service_request_id, description)
        VALUES (?, ?, ?, ?)
        ''', (user_id, helper_id, service_request_id, description))
        
        complaint_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return complaint_id
    
    @staticmethod
    def get_by_id(complaint_id):
        """Get complaint by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM complaints WHERE id = ?', (complaint_id,))
        complaint_data = cursor.fetchone()
        conn.close()
        
        if complaint_data:
            return Complaint(
                id=complaint_data['id'],
                user_id=complaint_data['user_id'],
                helper_id=complaint_data['helper_id'],
                service_request_id=complaint_data['service_request_id'],
                description=complaint_data['description'],
                status=complaint_data['status'],
                resolution=complaint_data['resolution'],
                created_at=complaint_data['created_at'],
                updated_at=complaint_data['updated_at']
            )
        return None
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get all complaints filed by a specific user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM complaints WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        complaints_data = cursor.fetchall()
        conn.close()
        
        complaints = []
        for complaint_data in complaints_data:
            complaints.append(Complaint(
                id=complaint_data['id'],
                user_id=complaint_data['user_id'],
                helper_id=complaint_data['helper_id'],
                service_request_id=complaint_data['service_request_id'],
                description=complaint_data['description'],
                status=complaint_data['status'],
                resolution=complaint_data['resolution'],
                created_at=complaint_data['created_at'],
                updated_at=complaint_data['updated_at']
            ))
        return complaints
    
    @staticmethod
    def get_by_helper_id(helper_id):
        """Get all complaints against a specific helper"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM complaints WHERE helper_id = ? ORDER BY created_at DESC', (helper_id,))
        complaints_data = cursor.fetchall()
        conn.close()
        
        complaints = []
        for complaint_data in complaints_data:
            complaints.append(Complaint(
                id=complaint_data['id'],
                user_id=complaint_data['user_id'],
                helper_id=complaint_data['helper_id'],
                service_request_id=complaint_data['service_request_id'],
                description=complaint_data['description'],
                status=complaint_data['status'],
                resolution=complaint_data['resolution'],
                created_at=complaint_data['created_at'],
                updated_at=complaint_data['updated_at']
            ))
        return complaints
    
    @staticmethod
    def get_all_pending():
        """Get all pending complaints"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM complaints WHERE status = "pending" ORDER BY created_at ASC')
        complaints_data = cursor.fetchall()
        conn.close()
        
        complaints = []
        for complaint_data in complaints_data:
            complaints.append(Complaint(
                id=complaint_data['id'],
                user_id=complaint_data['user_id'],
                helper_id=complaint_data['helper_id'],
                service_request_id=complaint_data['service_request_id'],
                description=complaint_data['description'],
                status=complaint_data['status'],
                resolution=complaint_data['resolution'],
                created_at=complaint_data['created_at'],
                updated_at=complaint_data['updated_at']
            ))
        return complaints
    
    def resolve(self, resolution):
        """Resolve a complaint"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE complaints
        SET status = "resolved", resolution = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (resolution, self.id))
        
        conn.commit()
        conn.close()
        
        self.status = "resolved"
        self.resolution = resolution
        return True
    
    def to_dict(self):
        """Convert complaint object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'helper_id': self.helper_id,
            'service_request_id': self.service_request_id,
            'description': self.description,
            'status': self.status,
            'resolution': self.resolution,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }