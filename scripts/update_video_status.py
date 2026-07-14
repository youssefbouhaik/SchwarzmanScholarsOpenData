import os
import sqlite3
import re

db_path = "scholars.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Try to add the column (it might already exist)
try:
    cursor.execute("ALTER TABLE scholars ADD COLUMN has_intro_video BOOLEAN DEFAULT 0")
    conn.commit()
except sqlite3.OperationalError:
    # Column likely already exists
    pass

# List all text files we just copied
files = [f for f in os.listdir(".") if f.endswith(".txt") and "Schwarzman" in f]

names_found = []

for f in files:
    # We want to extract the name from the filename. 
    # Filenames format examples:
    # "Anita Bassey Schwarzman Introduction Video.txt"
    # "Schwarzman Scholar Introduction Video - Xavier Ramirez.txt"
    # "Schwarzman Scholars Application – Introduction Video [Alex Tseng].txt"
    
    # Try different regex patterns
    name = None
    if "-" in f:
        # e.g. "Natalie Delille - Schwarzman Scholar Introduction.txt"
        # or "Schwarzman Scholar Introduction Video - Xavier Ramirez.txt"
        parts = f.replace(".txt", "").split("-")
        for part in parts:
            part = part.strip()
            if "Schwarzman" not in part and "Video" not in part and "Intro" not in part:
                name = part
    elif "[" in f and "]" in f:
        # e.g. "Schwarzman Scholars Application – Introduction Video [Alex Tseng].txt"
        name = re.search(r"\[(.*?)\]", f)
        if name:
            name = name.group(1)
    else:
        # e.g. "Anita Bassey Schwarzman Introduction Video.txt"
        # Remove common keywords
        cleaned = re.sub(r"Schwarzman[\s]*|Scholar[\s]*|s[\s]*|Introduction[\s]*|Video[\s]*|Program[\s]*|Application[\s]*|Scholarship[\s]*|\.txt", "", f, flags=re.IGNORECASE).strip()
        # "1-Minute Intro" might be left in some generic ones
        if cleaned and not "Minute" in cleaned and not "Intro" in cleaned and len(cleaned.split()) >= 1:
            name = cleaned
            
    if name:
        names_found.append(name.strip())

print(f"Names extracted: {names_found}")

# Update the database
for name in names_found:
    # Use LIKE or exact match to update the row. We will use LIKE to be safe against minor differences.
    cursor.execute("UPDATE scholars SET has_intro_video = 1 WHERE name LIKE ?", ('%' + name + '%',))
    print(f"Updated {name}: {cursor.rowcount} row(s) affected")

conn.commit()
conn.close()
