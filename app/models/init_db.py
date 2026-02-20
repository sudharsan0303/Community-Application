import sqlite3
import os
import datetime
from werkzeug.security import generate_password_hash

def init_db():
    """Initialize the database"""
    # Get the directory of this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root
    project_dir = os.path.dirname(base_dir)

    # Database file path
    db_path = os.path.join(project_dir, 'community_helper.db')
    print(f"Initializing database at {db_path}")

    # Create database connection
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        # Read schema file
        schema_path = os.path.join(base_dir, 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_script = f.read()

        cursor = conn.cursor()

        # Drop the users table if it exists
        cursor.execute('DROP TABLE IF EXISTS users')

        # Execute schema script
        conn.executescript(schema_script)
        print("Schema created successfully")

        # Check if we need to add test data
        cursor.execute('SELECT COUNT(*) as count FROM users')
        user_count = cursor.fetchone()['count']

        # Add test data if database is empty
        if user_count == 0:
            print("Adding test data...")

            # Add helpers for each category
            categories = [
                ('Home Repair', 'Assistance with home repairs and maintenance'),
                ('Technology', 'Help with computers, phones, and other tech'),
                ('Transportation', 'Rides to appointments, grocery shopping, etc.'),
                ('Cleaning', 'Help with household cleaning tasks'),
                ('Cooking', 'Meal preparation assistance'),
                ('Gardening', 'Help with garden maintenance and planting'),
                ('Companionship', 'Social visits and companionship'),
                ('Education', 'Tutoring and educational assistance'),
                ('Healthcare', 'Non-medical healthcare assistance'),
                ('Pet Care', 'Assistance with pet care and walking')
            ]

            for category_name, _ in categories:
                # Insert 5 helpers for each category
                for i in range(1, 6):
                    helper_name = f"{category_name} Helper {i}"
                    email = f"{category_name.lower().replace(' ', '_')}_helper{i}@example.com"
                    password = generate_password_hash("password123")

                    cursor.execute(
                        """
                        INSERT INTO users (name, email, password_hash, user_type)
                        VALUES (?, ?, ?, 'helper')
                        """,
                        (helper_name, email, password)
                    )

                    # Link helper to the category
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO helper_categories (helper_id, category_id)
                        SELECT users.id, categories.id
                        FROM users, categories
                        WHERE users.email = ? AND categories.name = ?
                        """,
                        (email, category_name)
                    )

            conn.commit()
            print("Test data added successfully")

    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()