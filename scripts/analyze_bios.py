import requests
from bs4 import BeautifulSoup
from collections import defaultdict

def analyze_bios():
    url = "https://www.schwarzmanscholars.org/scholars/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    print("Fetching HTML...")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    items = soup.find_all('div', class_='people-feed__item')
    
    cohort_stats = defaultdict(lambda: {'total': 0, 'with_bio': 0})
    
    for item in items:
        cohort_year = item.get('data-year', 'Unknown')
        cohort_stats[cohort_year]['total'] += 1
        
        # Check if the "View Bio" link exists
        bio_link = item.find('div', class_='people-card__link')
        if bio_link and 'View Bio' in bio_link.text:
            cohort_stats[cohort_year]['with_bio'] += 1
            
    print("\n--- Bio Availability by Cohort Year ---")
    for year in sorted(cohort_stats.keys()):
        stats = cohort_stats[year]
        total = stats['total']
        with_bio = stats['with_bio']
        pct = (with_bio / total) * 100 if total > 0 else 0
        print(f"Class of {year}: {with_bio}/{total} scholars have bios ({pct:.1f}%)")

if __name__ == "__main__":
    analyze_bios()
