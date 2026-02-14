import sqlite3
from datetime import datetime

# Brand names from the JSON
brands = [
    "Givenchy",
    "Hood By Air",
    "Yves Saint Laurent",
    "Balenciaga",
    "Rick Owen",
    "Maison Margiela",
    "Dolce & Gabbana",
    "Balmain",
    "291295 homme",
    "Blackmeans",
    "Dsquared2",
    "Carol Christian Poell",
    "C.P. Company",
    "Ato",
    "Matsumoto",
    "Buffalo Bobs",
    "Roberto Cavalli",
    "Amiri",
    "Dirk Bikkembergs",
    "in the attic",
    "semantic design",
    "Jun Takahashi",
    "Telfar",
    "Commes Des Garcons Homme",
    "Cinzia Araia",
    "Acne Studios",
    "Jean Paul Gaultier",
    "Undercover",
    "PPFM",
    "Le Grande Bleu",
    "KMrii",
    "Share Spirit Homme",
    "5351 Pour Les Hommes",
    "Les hommes",
    "Kapital",
    "Alexander mcqueen",
    "Murder License",
    "Jeremy scott",
    "Vivienne westwood",
    "Diesel Black and gold",
    "Giusepper Zanotti",
    "Gucci",
    "Christian Dior",
    "Dior Homme",
    "Burberry",
    "Fendi",
    "Louis Vuitton",
    "Prada",
    "Raf Simons"
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