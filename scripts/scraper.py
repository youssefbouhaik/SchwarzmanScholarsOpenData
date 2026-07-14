import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import time

# Your YouTube API Key
YOUTUBE_API_KEY = "AIzaSyBCpXAmzJCD9p-pGV0d9Eg9vB-A1FndR-Q"
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def scrape_alumni():
    """
    Scrapes the Schwarzman Scholars directory.
    Targeting the specific CSS class: 'people-card__name'
    """
    url = "https://www.schwarzmanscholars.org/scholars/"
    print(f"Fetching scholars from {url}...")
    
    # Send a User-Agent header so the website doesn't block the scraper
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # We found that the names are stored in <h3> tags with the class 'people-card__name'
    elements = soup.find_all('h3', class_='people-card__name')
    
    # Clean up the names and remove duplicates
    names = list(set([el.text.strip() for el in elements if el.text.strip()]))
    print(f"Successfully extracted {len(names)} scholar names.\n")
    return names

def search_youtube_videos(name):
    """
    Searches YouTube for public application/introduction videos.
    """
    query = f"{name} Schwarzman Scholar application video"
    
    try:
        request = youtube.search().list(
            q=query, 
            part='snippet', 
            type='video', 
            maxResults=1
        )
        response = request.execute()
        
        if not response['items']: 
            return None
        
        return response['items'][0]['id']['videoId']
    except Exception as e:
        print(f"  [!] YouTube Search API Error for {name}: {e}")
        return None

def analyze_comments(video_id):
    """
    Pulls the top 100 comments and scans for admission-related keywords.
    Returns True if keywords are found, False otherwise.
    """
    try:
        request = youtube.commentThreads().list(
            part="snippet", 
            videoId=video_id, 
            maxResults=100
        )
        response = request.execute()
    except Exception as e:
        # Handles cases where comments are disabled or API limits are hit
        return False 
        
    keywords = ['congrats', 'got in', 'admitted', 'proud', 'accepted', 'congratulations']
    
    for item in response.get('items', []):
        comment = item['snippet']['topLevelComment']['snippet']['textOriginal'].lower()
        if any(keyword in comment for keyword in keywords):
            return True
            
    return False

def main():
    alumni = scrape_alumni()
    
    # To avoid blowing through all 10,000 API quota units immediately, 
    # we will process the first 10 scholars as a test run.
    print("Starting YouTube scanning (Testing first 10 scholars to save API Quota)...")
    
    for name in alumni[:10]:
        print(f"\nProcessing {name}...")
        video_id = search_youtube_videos(name)
        
        if video_id:
            success_inferred = analyze_comments(video_id)
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"  -> Video Found: {video_url}")
            print(f"  -> Admission inferred from comments: {success_inferred}")
        else:
            print(f"  -> No public video found.")
            
        # Add a tiny delay to be nice to the API
        time.sleep(1)

if __name__ == "__main__":
    main()
