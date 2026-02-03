from models.database import get_db_connection
import datetime

class Verification:
    def __init__(self, id=None, helper_id=None, document_type=None, document_path=None, 
                 status=None, admin_id=None, admin_notes=None, created_at=None, updated_at=None):
        self.id = id
        self.helper_id = helper_id
        self.document_type = document_type
        self.document_path = document_path
        self.status = status
        self.admin_id = admin_id
        self.admin_notes = admin_notes
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def create(helper_id, document_type, document_path):
        """Create a new verification request"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
        INSERT INTO verifications (helper_id, document_type, document_path, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (helper_id, document_type, document_path, 'Pending', now, now))
        
        verification_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return verification_id
    
    @staticmethod
    def get_by_id(verification_id):
        """Get verification by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM verifications WHERE id = ?', (verification_id,))
        verification_data = cursor.fetchone()
        conn.close()
        
        if verification_data:
            return Verification(
                id=verification_data['id'],
                helper_id=verification_data['helper_id'],
                document_type=verification_data['document_type'],
                document_path=verification_data['document_path'],
                status=verification_data['status'],
                admin_id=verification_data['admin_id'],
                admin_notes=verification_data['admin_notes'],
                created_at=verification_data['created_at'],
                updated_at=verification_data['updated_at']
            )
        return None
    
    @staticmethod
    def get_by_helper_id(helper_id):
        """Get verification by helper ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM verifications WHERE helper_id = ? ORDER BY created_at DESC', (helper_id,))
        verification_data = cursor.fetchone()
        conn.close()
        
        if verification_data:
            return Verification(
                id=verification_data['id'],
                helper_id=verification_data['helper_id'],
                document_type=verification_data['document_type'],
                document_path=verification_data['document_path'],
                status=verification_data['status'],
                admin_id=verification_data['admin_id'],
                admin_notes=verification_data['admin_notes'],
                created_at=verification_data['created_at'],
                updated_at=verification_data['updated_at']
            )
        return None
    
    @staticmethod
    def get_by_status(status, limit=None):
        """Get verifications by status"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if limit:
            cursor.execute('SELECT * FROM verifications WHERE status = ? ORDER BY created_at ASC LIMIT ?', (status, limit))
        else:
            cursor.execute('SELECT * FROM verifications WHERE status = ? ORDER BY created_at ASC', (status,))
            
        verifications_data = cursor.fetchall()
        conn.close()
        
        verifications = []
        for verification_data in verifications_data:
            verifications.append(Verification(
                id=verification_data['id'],
                helper_id=verification_data['helper_id'],
                document_type=verification_data['document_type'],
                document_path=verification_data['document_path'],
                status=verification_data['status'],
                admin_id=verification_data['admin_id'],
                admin_notes=verification_data['admin_notes'],
                created_at=verification_data['created_at'],
                updated_at=verification_data['updated_at']
            ))
        return verifications
    
    @staticmethod
    def get_all_paginated(page, per_page, status=None, search=None):
        """Get all verifications with pagination"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        offset = (page - 1) * per_page
        
        query = 'SELECT v.* FROM verifications v JOIN helpers h ON v.helper_id = h.id JOIN users u ON h.user_id = u.id'
        count_query = 'SELECT COUNT(*) as count FROM verifications v JOIN helpers h ON v.helper_id = h.id JOIN users u ON h.user_id = u.id'
        
        params = []
        where_clauses = []
        
        if status and status != 'all':
            where_clauses.append('v.status = ?')
            params.append(status)
        
        if search:
            where_clauses.append('(u.name LIKE ? OR u.email LIKE ?)')
            params.extend(['%' + search + '%', '%' + search + '%'])
        
        if where_clauses:
            query += ' WHERE ' + ' AND '.join(where_clauses)
            count_query += ' WHERE ' + ' AND '.join(where_clauses)
        
        query += ' ORDER BY v.created_at DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        verifications_data = cursor.fetchall()
        
        # Get total count
        cursor.execute(count_query, params[:-2] if params else [])
        total = cursor.fetchone()['count']
        
        conn.close()
        
        verifications = []
        for verification_data in verifications_data:
            verifications.append(Verification(
                id=verification_data['id'],
                helper_id=verification_data['helper_id'],
                document_type=verification_data['document_type'],
                document_path=verification_data['document_path'],
                status=verification_data['status'],
                admin_id=verification_data['admin_id'],
                admin_notes=verification_data['admin_notes'],
                created_at=verification_data['created_at'],
                updated_at=verification_data['updated_at']
            ))
        
        return verifications, total
    
    @staticmethod
    def update_status(verification_id, status, admin_id, notes=None):
        """Update verification status"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
        UPDATE verifications 
        SET status = ?, admin_id = ?, admin_notes = ?, updated_at = ? 
        WHERE id = ?
        ''', (status, admin_id, notes, now, verification_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    @staticmethod
    def count_by_status(status):
        """Count verifications by status"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM verifications WHERE status = ?', (status,))
        result = cursor.fetchone()
        conn.close()
        
        return result['count'] if result else 0