import requests
from bs4 import BeautifulSoup
import sqlite3
import time

DB_NAME = "scholars.db"

def setup_database():
    """Creates the SQLite database and the scholars table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create a table for the scholars
    # We include an 'ethnicity_guess' column as requested, but it will default to Unknown
    # since accurate ethnicity prediction requires an ML model or API.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scholars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        country TEXT,
        university TEXT,
        cohort_year TEXT,
        ethnicity_guess TEXT DEFAULT 'Unknown',
        youtube_video_id TEXT,
        admission_inferred BOOLEAN
    )
    ''')
    conn.commit()
    return conn

def fetch_all_scholars():
    """
    Fetches the main directory page. The base page actually contains 
    the full directory (around 1,500 scholars) baked into the HTML.
    """
    url = "https://www.schwarzmanscholars.org/scholars/"
    print("Fetching the full historical directory...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all scholar items
    items = soup.find_all('div', class_='people-feed__item')
    print(f"Found {len(items)} scholar records in the HTML.")
    
    scholars_data = []
    
    for item in items:
        # Extract data attributes
        country = item.get('data-country', 'Unknown')
        cohort_year = item.get('data-year', 'Unknown')
        university = item.get('data-university', 'Unknown').replace('|', ', ')
        
        # Extract name
        name_tag = item.find('h3', class_='people-card__name')
        if not name_tag:
            continue
            
        name = name_tag.text.strip()
        
        # Super basic heuristic for grouping (Real ethnicity requires ML like ethnicolr)
        # We will just categorize by Country for now which is highly accurate.
        scholars_data.append((name, country, university, cohort_year))
        
    return scholars_data

def populate_database(conn, scholars_data):
    """Inserts the scraped data into the SQLite database."""
    cursor = conn.cursor()
    
    inserted = 0
    for scholar in scholars_data:
        try:
            cursor.execute('''
            INSERT INTO scholars (name, country, university, cohort_year)
            VALUES (?, ?, ?, ?)
            ''', scholar)
            inserted += 1
        except sqlite3.IntegrityError:
            # Skip duplicates (name is UNIQUE in the DB)
            pass
            
    conn.commit()
    print(f"Successfully inserted {inserted} new scholars into the database.")

def main():
    print("--- Schwarzman Scholars Database Builder ---")
    conn = setup_database()
    
    # 1. Scrape all scholars and their metadata
    scholars_data = fetch_all_scholars()
    
    # 2. Save to SQLite
    populate_database(conn, scholars_data)
    
    conn.close()
    print(f"\nDatabase successfully built at {DB_NAME}")
    print("You can now query this using any SQLite viewer!")

if __name__ == "__main__":
    main()
