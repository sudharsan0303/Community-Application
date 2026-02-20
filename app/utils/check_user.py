
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.database import get_db_connection

def check_user(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print(f"Checking for user: {email}")
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    
    if user:
        print("User found:")
        print(f"ID: {user['id']}")
        print(f"Name: {user['name']}")
        print(f"Email: {user['email']}")
        print(f"User Type: {user['user_type']}")
        print(f"Password Hash: {user['password_hash'][:20]}...") # Truncate hash for security/display
        
        if user['user_type'] == 'helper':
             cursor.execute('SELECT * FROM helpers WHERE user_id = ?', (user['id'],))
             helper = cursor.fetchone()
             if helper:
                 print("Helper Profile Found.")
    else:
        print("User not found.")
    
    conn.close()

if __name__ == "__main__":
    email = "abcd123@gmail.com"
    if len(sys.argv) > 1:
        email = sys.argv[1]
    check_user(email)
