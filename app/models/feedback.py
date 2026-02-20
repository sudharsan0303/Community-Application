from .database import get_db_connection
from .helper import Helper
from datetime import datetime

class Feedback:
    @staticmethod
    def get_by_user_id(user_id):
        """Get all feedback entries for a given user_id"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM feedback WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Feedback(**dict(row)) for row in rows]
    def __init__(self, id=None, user_id=None, helper_id=None, service_request_id=None,
                 rating=None, review=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.helper_id = helper_id
        self.service_request_id = service_request_id
        self.rating = rating
        self.review = review
        self.created_at = self._convert_to_datetime(created_at)
    
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
    def create(user_id, helper_id, service_request_id, rating, review=None):
        """Create a new feedback entry"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO feedback (user_id, helper_id, service_request_id, rating, review)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, helper_id, service_request_id, rating, review))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Update helper's rating
        helper = Helper.get_by_id(helper_id)
        if helper:
            helper.update_rating(rating)
        
        return feedback_id
    
    @staticmethod
    def get_by_id(feedback_id):
        """Get feedback by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM feedback WHERE id = ?', (feedback_id,))
        feedback_data = cursor.fetchone()
        conn.close()
        
        if feedback_data:
            return Feedback(
                id=feedback_data['id'],
                user_id=feedback_data['user_id'],
                helper_id=feedback_data['helper_id'],
                service_request_id=feedback_data['service_request_id'],
                rating=feedback_data['rating'],
                review=feedback_data['review'],
                created_at=feedback_data['created_at']
            )
        return None
    
    @staticmethod
    def get_by_helper_id(helper_id):
        """Get all feedback for a specific helper"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM feedback WHERE helper_id = ? ORDER BY created_at DESC', (helper_id,))
        feedback_data_list = cursor.fetchall()
        conn.close()
        
        feedback_list = []
        for feedback_data in feedback_data_list:
            feedback_list.append(Feedback(
                id=feedback_data['id'],
                user_id=feedback_data['user_id'],
                helper_id=feedback_data['helper_id'],
                service_request_id=feedback_data['service_request_id'],
                rating=feedback_data['rating'],
                review=feedback_data['review'],
                created_at=feedback_data['created_at']
            ))
        return feedback_list
    
    @staticmethod
    def get_by_service_request_id(service_request_id):
        """Get feedback for a specific service request"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM feedback WHERE service_request_id = ?', (service_request_id,))
        feedback_data = cursor.fetchone()
        conn.close()
        
        if feedback_data:
            return Feedback(
                id=feedback_data['id'],
                user_id=feedback_data['user_id'],
                helper_id=feedback_data['helper_id'],
                service_request_id=feedback_data['service_request_id'],
                rating=feedback_data['rating'],
                review=feedback_data['review'],
                created_at=feedback_data['created_at']
            )
        return None
    
    def to_dict(self):
        """Convert feedback object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'helper_id': self.helper_id,
            'service_request_id': self.service_request_id,
            'rating': self.rating,
            'review': self.review,
            'created_at': self.created_at
        }
    
    @staticmethod
    def get_by_request_id(request_id):
        """Alias for get_by_service_request_id"""
        return Feedback.get_by_service_request_id(request_id)