import csv
import subprocess
import os

os.makedirs('frontend/public/videos', exist_ok=True)

with open('data/schwarzman_scholars_dataset.csv', 'r') as f:
    reader = csv.DictReader(f)
    videos = [row for row in reader if row.get('youtube_video_id')]

print(f"Found {len(videos)} videos to download.")

# Limit to first 3 for testing
for row in videos[:3]:
    link = row['youtube_video_id']
    vid_id = row['id']
    print(f"Downloading {link}...")
    subprocess.run(['yt-dlp', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', '-o', f'frontend/public/videos/{vid_id}.mp4', link])

print("Test downloads complete!")
