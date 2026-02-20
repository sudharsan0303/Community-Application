import sqlite3
from datetime import datetime
import random

def adapt_datetime_isoformat(dt):
    return dt.isoformat()

def convert_datetime_isoformat(s):
    return datetime.fromisoformat(s.decode())

# Register the adapters and converters for datetime
sqlite3.register_adapter(datetime, adapt_datetime_isoformat)
sqlite3.register_converter("DATETIME", convert_datetime_isoformat)

def populate_helpers():
    connection = sqlite3.connect("community_helper.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = connection.cursor()

    # Fetch all categories
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()

    # Helper data template
    helper_list = [
        {"name": "Aarav Sharma", "phone": "9876543210", "address": "Mumbai, Maharashtra", "location": "Mumbai"},
        {"name": "Ishita Verma", "phone": "9123456789", "address": "Delhi, Delhi", "location": "Delhi"},
        {"name": "Rohan Gupta", "phone": "9988776655", "address": "Bangalore, Karnataka", "location": "Bangalore"},
        {"name": "Ananya Singh", "phone": "9871234567", "address": "Hyderabad, Telangana", "location": "Hyderabad"},
        {"name": "Kabir Mehta", "phone": "9123987654", "address": "Chennai, Tamil Nadu", "location": "Chennai"},
    ]

    for category_id, category_name in categories:
        print(f"Adding helpers for category: {category_name}")
        for i, helper in enumerate(helper_list):
            # Generate a unique email by appending a random number
            unique_email = f"{helper['name'].lower().replace(' ', '.')}+{random.randint(1000, 9999)}@example.com"

            # Insert user
            user_data = (
                unique_email,
                helper["name"],
                "hashed_password",
                helper["phone"],
                helper["address"],
                "helper",
                helper["location"],
                datetime.now(),
                datetime.now(),
            )
            cursor.execute(
                """
                INSERT INTO users (email, name, password_hash, phone, address, user_type, location, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                user_data,
            )
            user_id = cursor.lastrowid

            # Insert helper
            helper_data = (
                user_id,
                "General assistance",
                "2 years",
                "Weekdays",
                1,
                4.5,
                10,
                datetime.now(),
                datetime.now(),
            )
            cursor.execute(
                """
                INSERT INTO helpers (user_id, skills, experience, availability, verified, rating, total_ratings, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                helper_data,
            )
            helper_id = cursor.lastrowid

            # Link helper to category
            cursor.execute(
                "INSERT INTO helper_categories (helper_id, category_id) VALUES (?, ?)",
                (helper_id, category_id),
            )

    connection.commit()
    connection.close()

if __name__ == "__main__":
    populate_helpers()