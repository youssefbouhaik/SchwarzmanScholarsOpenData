import requests
from bs4 import BeautifulSoup
import sqlite3

DB_NAME = "scholars.db"

def add_bio_column():
    """Adds the bio column to the database if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE scholars ADD COLUMN bio TEXT")
        print("Added 'bio' column to the database.")
    except sqlite3.OperationalError:
        print("'bio' column already exists.")
    conn.commit()
    conn.close()

def update_bios():
    """Fetches the HTML and extracts the bio text from data attributes."""
    print("Fetching scholar directory to extract bios...")
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    response = requests.get('https://www.schwarzmanscholars.org/scholars/', headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # The bios are stored in <a> tags with the class 'action-launch-bio-modal'
    bio_elements = soup.find_all('a', class_='action-launch-bio-modal')
    print(f"Found {len(bio_elements)} bio elements on the page.")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    updated_count = 0
    for el in bio_elements:
        name = el.get('data-bio-modal-name', '').strip()
        bio_text = el.get('data-bio-modal-text', '').strip()
        
        if name and bio_text:
            # Update the scholar's row with their bio
            cursor.execute("UPDATE scholars SET bio = ? WHERE name = ?", (bio_text, name))
            if cursor.rowcount > 0:
                updated_count += 1
                
    conn.commit()
    conn.close()
    
    print(f"Successfully updated the SQL database with {updated_count} biographies!")

if __name__ == "__main__":
    add_bio_column()
    update_bios()
