import sqlite3
from datetime import datetime

# Brand names from the JSON
brands = [
        "The Viridi-anne",
        "Kazuyuki Kumagai",
        "Lad Musician",
        "Kiryuyrik",
        "Ziggy Chen",
        "Taichi Murakami",
        "Alessandro",
        "GmbH"
]

# Connect to SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect('Website/clothes.db')
cursor = conn.cursor()

# Create the results table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS results (
        ID TEXT PRIMARY KEY,
        last_checked TEXT
    )
''')

# Insert all brands into the table
for brand in brands:
    try:
        cursor.execute('''
            INSERT INTO results (ID, last_checked)
            VALUES (?, NULL)
        ''', (brand,))
        print(f"Inserted: {brand}")
    except sqlite3.IntegrityError:
        print(f"Brand already exists: {brand}")

# Commit changes and close connection
conn.commit()
conn.close()

print("\nAll brands have been inserted into the database!")