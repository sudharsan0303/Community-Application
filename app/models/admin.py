from .database import get_db_connection

class Admin:
    def __init__(self, id=None, user_id=None, role='admin', created_at=None):
        self.id = id
        self.user_id = user_id
        self.role = role
        self.created_at = created_at
    
    @staticmethod
    def create(user_id, role='admin'):
        """Create a new admin"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO admins (user_id, role)
        VALUES (?, ?)
        ''', (user_id, role))
        
        admin_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return admin_id
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get admin by user ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM admins WHERE user_id = ?', (user_id,))
        admin_data = cursor.fetchone()
        conn.close()
        
        if admin_data:
            return Admin(
                id=admin_data['id'],
                user_id=admin_data['user_id'],
                role=admin_data['role'],
                created_at=admin_data['created_at']
            )
        return None
    
    @staticmethod
    def get_all():
        """Get all admins"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM admins')
        admins_data = cursor.fetchall()
        conn.close()
        
        admins = []
        for admin_data in admins_data:
            admins.append(Admin(
                id=admin_data['id'],
                user_id=admin_data['user_id'],
                role=admin_data['role'],
                created_at=admin_data['created_at']
            ))
        return admins
    
    def to_dict(self):
        """Convert admin object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role': self.role,
            'created_at': self.created_at
        }