import sqlite3

def main():
    conn = sqlite3.connect('scholars.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, bio FROM scholars WHERE bio IS NOT NULL AND bio != ''")
    rows = cursor.fetchall()
    
    with open('all_bios.txt', 'w', encoding='utf-8') as f:
        for row in rows:
            name, bio = row
            f.write(f"--- {name} ---\n{bio}\n\n")
    
    print(f"Extracted {len(rows)} bios to all_bios.txt")

if __name__ == '__main__':
    main()
