
import sqlite3
import os
import sys

# Default database path
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'community_helper.db')

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def check_user(email):
    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()
    
    print(f"Checking for user: {email}")
    try:
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user:
            print("User found:")
            print(f"ID: {user['id']}")
            print(f"Name: {user['name']}")
            print(f"Email: {user['email']}")
            print(f"User Type: {user['user_type']}")
            
            # Show that password is hashed
            print(f"Password stored as hash: {user['password_hash'][:10]}...") 
        else:
            print(f"User with email '{email}' not found.")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    email = "abcd123@gmail.com"
    if len(sys.argv) > 1:
        email = sys.argv[1]
    check_user(email)
