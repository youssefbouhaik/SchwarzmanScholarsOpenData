import cv2
from deepface import DeepFace
import os
import sys

def analyze_video(video_path):
    print(f"\\n--- Analyzing: {os.path.basename(video_path)} ---")
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Get total frames to sample 5 frames across the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps else 0
    
    frames_to_extract = [
        int(total_frames * 0.2),
        int(total_frames * 0.4),
        int(total_frames * 0.6),
        int(total_frames * 0.8),
    ]

    emotions_aggregated = {'happy': 0, 'neutral': 0, 'sad': 0, 'fear': 0, 'surprise': 0, 'angry': 0, 'disgust': 0}
    valid_faces = 0

    for f_idx in frames_to_extract:
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret, frame = cap.read()
        if not ret:
            continue
            
        print(f"Extracting frame at {f_idx/fps:.1f}s...")
        # Save temp frame for deepface
        cv2.imwrite("temp_frame.jpg", frame)
        
        try:
            # Analyze emotion
            analysis = DeepFace.analyze("temp_frame.jpg", actions=['emotion'], detector_backend='retinaface', enforce_detection=False, silent=True)
            # DeepFace can return a list of faces
            if isinstance(analysis, list):
                dom_emotion = analysis[0]['dominant_emotion']
                emotion_probs = analysis[0]['emotion']
            else:
                dom_emotion = analysis['dominant_emotion']
                emotion_probs = analysis['emotion']
                
            print(f"  -> Dominant: {dom_emotion} (Happy: {emotion_probs['happy']:.1f}%, Neutral: {emotion_probs['neutral']:.1f}%)")
            
            for k in emotions_aggregated.keys():
                emotions_aggregated[k] += emotion_probs.get(k, 0)
            valid_faces += 1
            
        except Exception as e:
            print(f"  -> Error detecting face: {str(e)}")

    cap.release()
    if os.path.exists("temp_frame.jpg"):
        os.remove("temp_frame.jpg")

    if valid_faces > 0:
        print("\\n=== FINAL AGGREGATE SCORES ===")
        print(f"Avg Happy:   {emotions_aggregated['happy']/valid_faces:.1f}%")
        print(f"Avg Neutral: {emotions_aggregated['neutral']/valid_faces:.1f}%")
        print(f"Avg Fear:    {emotions_aggregated['fear']/valid_faces:.1f}%")
        
        # Calculate warmth score
        avg_happy = emotions_aggregated['happy'] / valid_faces
        avg_neutral = emotions_aggregated['neutral'] / valid_faces
        
        # Similar math to our JS frontend, but out of 100
        score = min(99, max(0, (avg_happy * 1.2) + (avg_neutral * 0.5) + 30))
        print(f"\\n🌟 FINAL CHARISMA/WARMTH SCORE: {score:.1f}/100")
    else:
        print("No faces could be analyzed in the video.")

if __name__ == "__main__":
    videos = [
        "frontend/public/videos/16.mp4",
        "frontend/public/videos/51.mp4",
        "frontend/public/videos/54.mp4"
    ]
    for v in videos:
        if os.path.exists(v):
            analyze_video(v)
        else:
            print(f"Not found: {v}")
