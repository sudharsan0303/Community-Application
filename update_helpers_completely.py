import sqlite3

def update_helpers_completely():
    connection = sqlite3.connect("community_helper.db")
    cursor = connection.cursor()

    # List of valid Indian names and details
    helper_details = [
        {"name": "Aarav Sharma", "phone": "9876543210", "address": "Mumbai, Maharashtra", "location": "Mumbai"},
        {"name": "Ishita Verma", "phone": "9123456789", "address": "Delhi, Delhi", "location": "Delhi"},
        {"name": "Rohan Gupta", "phone": "9988776655", "address": "Bangalore, Karnataka", "location": "Bangalore"},
        {"name": "Ananya Singh", "phone": "9871234567", "address": "Hyderabad, Telangana", "location": "Hyderabad"},
        {"name": "Kabir Mehta", "phone": "9123987654", "address": "Chennai, Tamil Nadu", "location": "Chennai"},
        {"name": "Priya Patel", "phone": "9876543211", "address": "Ahmedabad, Gujarat", "location": "Ahmedabad"},
        {"name": "Aditya Rao", "phone": "9123456788", "address": "Pune, Maharashtra", "location": "Pune"},
        {"name": "Sneha Iyer", "phone": "9988776654", "address": "Kochi, Kerala", "location": "Kochi"},
        {"name": "Vikram Das", "phone": "9871234568", "address": "Kolkata, West Bengal", "location": "Kolkata"},
        {"name": "Meera Nair", "phone": "9123987653", "address": "Thiruvananthapuram, Kerala", "location": "Thiruvananthapuram"},
    ]

    # Fetch all helpers
    cursor.execute("SELECT id FROM users WHERE user_type = 'helper'")
    helper_ids = cursor.fetchall()

    # Update names and details for helpers
    for i, helper_id in enumerate(helper_ids):
        if i < len(helper_details):
            cursor.execute(
                "UPDATE users SET name = ?, phone = ?, address = ?, location = ? WHERE id = ?",
                (
                    helper_details[i]["name"],
                    helper_details[i]["phone"],
                    helper_details[i]["address"],
                    helper_details[i]["location"],
                    helper_id[0]
                )
            )

    connection.commit()
    connection.close()

if __name__ == "__main__":
    update_helpers_completely()