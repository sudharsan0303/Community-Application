import sqlite3

# Connect to database
conn = sqlite3.connect('community_app.db')
cursor = conn.cursor()

# Check available tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Available tables:")
for table in tables:
    print(f"  - {table[0]}")

# Check users
print("\nUsers:")
cursor.execute("SELECT id, name, email, user_type FROM users")
users = cursor.fetchall()
for user in users:
    print(f"  ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Type: {user[3]}")

# Check helpers
print("\nHelpers:")
cursor.execute("SELECT h.id, u.name, u.email, h.skills FROM helpers h JOIN users u ON h.user_id = u.id")
helpers = cursor.fetchall()
for helper in helpers:
    print(f"  Helper ID: {helper[0]}, Name: {helper[1]}, Email: {helper[2]}, Skills: {helper[3]}")

conn.close()