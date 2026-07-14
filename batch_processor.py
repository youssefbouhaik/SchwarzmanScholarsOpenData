import pandas as pd
import os
import subprocess
import cv2
from deepface import DeepFace
import whisper
from textblob import TextBlob
import sys

# Ensure nltk data is downloaded for rake
try:
    import nltk
    nltk.download('punkt_tab')
    from rake_nltk import Rake
except:
    pass

def download_video(video_id, output_path):
    if os.path.exists(output_path):
        return True
    
    if video_id.startswith("http"):
        url = video_id
    else:
        url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"Downloading {url}...")
    try:
        # download worst video + worst audio to save time and space, since we just need faces and transcript
        # actually, let's download worst video that has at least 360p or something so faces are detectable
        cmd = [
            "yt-dlp", 
            "-f", "best[height<=480]/worst", 
            "-o", output_path,
            "--quiet",
            url
        ]
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to download {video_id}")
        return False

def analyze_video_emotions(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps else 0
    
    # 5 frames across the video
    frames_to_extract = [
        int(total_frames * 0.1),
        int(total_frames * 0.3),
        int(total_frames * 0.5),
        int(total_frames * 0.7),
        int(total_frames * 0.9),
    ]

    emotions_aggregated = {'happy': 0, 'neutral': 0, 'fear': 0, 'sad': 0, 'angry': 0, 'surprise': 0, 'disgust': 0}
    valid_faces = 0

    for f_idx in frames_to_extract:
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret, frame = cap.read()
        if not ret:
            continue
            
        cv2.imwrite("temp_batch.jpg", frame)
        try:
            analysis = DeepFace.analyze("temp_batch.jpg", actions=['emotion'], detector_backend='retinaface', enforce_detection=False, silent=True)
            if isinstance(analysis, list):
                emotion_probs = analysis[0]['emotion']
            else:
                emotion_probs = analysis['emotion']
                
            for k in emotions_aggregated.keys():
                emotions_aggregated[k] += emotion_probs.get(k, 0)
            valid_faces += 1
        except Exception:
            pass

    cap.release()
    if os.path.exists("temp_batch.jpg"):
        os.remove("temp_batch.jpg")

    if valid_faces > 0:
        avg_happy = emotions_aggregated['happy'] / valid_faces
        avg_neutral = emotions_aggregated['neutral'] / valid_faces
        score = min(99, max(0, (avg_happy * 1.2) + (avg_neutral * 0.5) + 30))
        return {
            'score': score,
            'happy': avg_happy,
            'neutral': avg_neutral
        }
    return None

def process_all():
    print("Loading Whisper tiny model...")
    model = whisper.load_model("tiny")
    
    df = pd.read_csv('data/schwarzman_scholars_dataset.csv')
    videos_df = df[df['youtube_video_id'].notna() & (df['youtube_video_id'] != '')].copy()
    
    os.makedirs("frontend/public/videos", exist_ok=True)
    report_file = "ADMITTED_SCHOLAR_PROFILES.md"
    
    if not os.path.exists(report_file):
        with open(report_file, "w") as f:
            f.write("# Schwarzman Scholars - Individual AI Profiles\n\n")
            f.write("This report contains a psychological and thematic profile for each admitted scholar's video, generated entirely by ML.\n\n")
    
    # Read existing IDs to allow resume
    with open(report_file, "r") as f:
        existing = f.read()
    
    for idx, row in videos_df.iterrows():
        vid_id = row['youtube_video_id']
        name = row['name']
        
        if vid_id in existing:
            print(f"Skipping {name} (already processed)")
            continue
            
        print(f"\nProcessing: {name} ({vid_id})")
        
        # Extract the actual ID for the filename to prevent invalid paths
        clean_id = vid_id.split("v=")[-1] if "v=" in vid_id else vid_id
        video_path = f"frontend/public/videos/{clean_id}.mp4"
        
        if not download_video(vid_id, video_path):
            continue
            
        print("  - Running DeepFace analysis...")
        emotion_data = analyze_video_emotions(video_path)
        if not emotion_data:
            emotion_data = {'score': 0, 'happy': 0, 'neutral': 0}
            
        print("  - Transcribing with Whisper...")
        try:
            result = model.transcribe(video_path)
            transcript = result["text"]
        except:
            transcript = "Could not transcribe audio."
            
        print("  - Running NLP Sentiment & Keyword extraction...")
        blob = TextBlob(transcript)
        sentiment = blob.sentiment.polarity  # -1 to 1
        
        keywords = []
        try:
            r = Rake(min_length=1, max_length=2)
            r.extract_keywords_from_text(transcript)
            keywords = r.get_ranked_phrases()[:5]
        except:
            pass
            
        # Write to report
        with open(report_file, "a") as f:
            f.write(f"## {name} (Cohort {row['cohort_year']})\n")
            f.write(f"- **Undergrad:** {row.get('undergraduate_university', 'N/A')}\n")
            f.write(f"- **Video ID:** `{vid_id}`\n")
            f.write("### AI Analysis\n")
            f.write(f"- **Visual Charisma & Warmth Score:** {emotion_data['score']:.1f}/100 (Happy: {emotion_data['happy']:.1f}%, Neutral: {emotion_data['neutral']:.1f}%)\n")
            f.write(f"- **Vocal/Thematic Sentiment:** {sentiment:.2f} (Positive > 0.1 is optimistic)\n")
            f.write(f"- **Core Themes (Keywords):** {', '.join(keywords) if keywords else 'None detected'}\n")
            f.write("---\n\n")

if __name__ == "__main__":
    process_all()
