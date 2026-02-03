import sqlite3

def update_helper_names():
    connection = sqlite3.connect("community_helper.db")
    cursor = connection.cursor()

    # List of valid Indian names
    indian_names = [
        "Aarav Sharma",
        "Ishita Verma",
        "Rohan Gupta",
        "Ananya Singh",
        "Kabir Mehta",
        "Priya Patel",
        "Aditya Rao",
        "Sneha Iyer",
        "Vikram Das",
        "Meera Nair"
    ]

    # Fetch all helpers
    cursor.execute("SELECT id FROM users WHERE user_type = 'helper'")
    helper_ids = cursor.fetchall()

    # Update names for helpers
    for i, helper_id in enumerate(helper_ids):
        if i < len(indian_names):
            cursor.execute(
                "UPDATE users SET name = ? WHERE id = ?",
                (indian_names[i], helper_id[0])
            )

    connection.commit()
    connection.close()

if __name__ == "__main__":
    update_helper_names()