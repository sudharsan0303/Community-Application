from .database import get_db_connection

class Helper:
    def __init__(self, id=None, user_id=None, skills=None, experience=None, availability=None,
                 verified=False, rating=0, total_ratings=0, created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.skills = skills
        self.experience = experience
        self.availability = availability
        self.verified = verified
        self.rating = rating
        self.total_ratings = total_ratings
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def create(user_id, skills, experience=None, availability=None):
        """Create a new helper profile"""
        if not user_id or not skills:
            raise ValueError('User ID and skills are required')
            
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # First verify that the user exists and is a helper
            cursor.execute('SELECT user_type FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            if not user:
                raise ValueError('User not found')
            if user['user_type'] != 'helper':
                raise ValueError('User is not registered as a helper')
            
            # Create helper profile
            cursor.execute('''
            INSERT INTO helpers (user_id, skills, experience, availability)
            VALUES (?, ?, ?, ?)
            ''', (user_id, skills, experience, availability))
            
            helper_id = cursor.lastrowid
            conn.commit()
            return helper_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f'Failed to create helper profile: {str(e)}')
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_by_id(helper_id):
        """Get helper by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM helpers WHERE id = ?', (helper_id,))
        helper_data = cursor.fetchone()
        conn.close()
        
        if helper_data:
            return Helper(
                id=helper_data['id'],
                user_id=helper_data['user_id'],
                skills=helper_data['skills'],
                experience=helper_data['experience'],
                availability=helper_data['availability'],
                verified=bool(helper_data['verified']),
                rating=helper_data['rating'],
                total_ratings=helper_data['total_ratings'],
                created_at=helper_data['created_at'],
                updated_at=helper_data['updated_at']
            )
        return None
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get helper by user ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM helpers WHERE user_id = ?', (user_id,))
        helper_data = cursor.fetchone()
        conn.close()
        
        if helper_data:
            return Helper(
                id=helper_data['id'],
                user_id=helper_data['user_id'],
                skills=helper_data['skills'],
                experience=helper_data['experience'],
                availability=helper_data['availability'],
                verified=bool(helper_data['verified']),
                rating=helper_data['rating'],
                total_ratings=helper_data['total_ratings'],
                created_at=helper_data['created_at'],
                updated_at=helper_data['updated_at']
            )
        return None
    
    @staticmethod
    def get_all(verified_only=False):
        """Get all helpers, optionally filtered by verification status"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if verified_only:
            cursor.execute('SELECT * FROM helpers WHERE verified = 1')
        else:
            cursor.execute('SELECT * FROM helpers')
            
        helpers_data = cursor.fetchall()
        conn.close()
        
        helpers = []
        for helper_data in helpers_data:
            helpers.append(Helper(
                id=helper_data['id'],
                user_id=helper_data['user_id'],
                skills=helper_data['skills'],
                experience=helper_data['experience'],
                availability=helper_data['availability'],
                verified=bool(helper_data['verified']),
                rating=helper_data['rating'],
                total_ratings=helper_data['total_ratings'],
                created_at=helper_data['created_at'],
                updated_at=helper_data['updated_at']
            ))
        return helpers
    
    @staticmethod
    def get_available_helpers_by_category(category_name):
        """Get all available helpers for a specific category"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
        SELECT h.* FROM helpers h
        JOIN helper_categories hc ON h.id = hc.helper_id
        JOIN categories c ON hc.category_id = c.id
        WHERE c.name = ? AND h.availability = 'available'
        ''', (category_name,))

        helpers_data = cursor.fetchall()
        conn.close()

        helpers = []
        for helper_data in helpers_data:
            helpers.append(Helper(
                id=helper_data['id'],
                user_id=helper_data['user_id'],
                skills=helper_data['skills'],
                experience=helper_data['experience'],
                availability=helper_data['availability'],
                verified=bool(helper_data['verified']),
                rating=helper_data['rating'],
                total_ratings=helper_data['total_ratings'],
                created_at=helper_data['created_at'],
                updated_at=helper_data['updated_at']
            ))
        return helpers
    
    def update(self):
        """Update helper information"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE helpers
        SET skills = ?, experience = ?, availability = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (self.skills, self.experience, self.availability, self.id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def verify(self, verified=True):
        """Set helper verification status"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE helpers
        SET verified = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (1 if verified else 0, self.id))
        
        conn.commit()
        conn.close()
        
        self.verified = verified
        return True
    
    def update_rating(self, new_rating):
        """Update helper rating with a new rating value"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate new average rating
        new_total = self.total_ratings + 1
        new_avg = ((self.rating * self.total_ratings) + new_rating) / new_total
        
        cursor.execute('''
        UPDATE helpers
        SET rating = ?, total_ratings = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (new_avg, new_total, self.id))
        
        conn.commit()
        conn.close()
        
        self.rating = new_avg
        self.total_ratings = new_total
        return True
    
    def to_dict(self):
        """Convert helper object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skills': self.skills,
            'experience': self.experience,
            'availability': self.availability,
            'verified': self.verified,
            'rating': self.rating,
            'total_ratings': self.total_ratings,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }