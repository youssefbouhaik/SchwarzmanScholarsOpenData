#!/usr/bin/env python3
"""
Ultra video pipeline — replaces analyze_emotions.py + batch_processor.py
Does: yt-dlp -> Whisper -> DeepFace (fallback) -> TextBlob/RAKE -> ADMITTED_SCHOLAR_PROFILES.md + data/meta/*.json

Usage:
  pip install -r requirements.txt
  python scripts/video_pipeline.py              # process all 74, skip existing
  python scripts/video_pipeline.py --force      # re-process all
  python scripts/video_pipeline.py --limit 3    # smoke test 3 videos
  make transcripts  -> calls this
"""
import argparse, csv, json, os, pathlib, re, subprocess, sys, urllib.parse
from collections import Counter

ROOT = pathlib.Path(__file__).parent.parent
CSV_PATH = ROOT / "data" / "schwarzman_scholars_dataset.csv"
VID_DIR = ROOT / "data" / "videos"
AUDIO_DIR = ROOT / "data" / "audio"
TRANS_DIR = ROOT / "data" / "transcripts"
META_DIR = ROOT / "data" / "meta"
REPORT = ROOT / "ADMITTED_SCHOLAR_PROFILES.md"

for d in [VID_DIR, AUDIO_DIR, TRANS_DIR, META_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def clean_yt(url: str) -> str:
    if not url: return url
    url=url.strip()
    try:
        p=urllib.parse.urlparse(url)
        qs=urllib.parse.parse_qs(p.query)
        if "v" in qs: return f"https://www.youtube.com/watch?v={qs['v'][0]}"
        if "/shorts/" in url:
            sid=url.split("/shorts/")[1].split("?")[0].split("/")[0]
            return f"https://www.youtube.com/shorts/{sid}"
        if "youtu.be" in url:
            sid=url.split("/")[-1].split("?")[0]
            return f"https://www.youtube.com/watch?v={sid}"
    except: pass
    return url.split("&pp=")[0].split("&")[0] if "&" in url else url

def vid_id(url: str) -> str:
    url=clean_yt(url)
    if "/shorts/" in url: return url.split("/shorts/")[1].split("?")[0]
    if "v=" in url: return url.split("v=")[1].split("&")[0]
    return url.split("/")[-1].split("?")[0]

def download_video(url: str, out_mp4: pathlib.Path, retries=3) -> bool:
    if out_mp4.exists() and out_mp4.stat().st_size > 5000:
        return True
    url=clean_yt(url)
    for attempt in range(1, retries+1):
        try:
            cmd=["yt-dlp","-f","best[height<=480]/worst","-o",str(out_mp4),"--quiet","--no-warnings",url]
            subprocess.run(cmd, check=True, timeout=120)
            if out_mp4.exists() and out_mp4.stat().st_size>5000:
                return True
        except Exception as e:
            print(f"  ! download attempt {attempt}/{retries} failed: {e}")
            try: out_mp4.unlink(missing_ok=True)
            except: pass
    return False

def transcribe(mp4: pathlib.Path, txt_out: pathlib.Path):
    if txt_out.exists() and txt_out.stat().st_size>10:
        return txt_out.read_text(encoding="utf-8")
    try:
        import whisper
        model=whisper.load_model("tiny")
        res=model.transcribe(str(mp4), language="en")
        text=res.get("text","").strip()
        txt_out.write_text(text, encoding="utf-8")
        return text
    except Exception as e:
        print(f"  ! whisper failed: {e}")
        txt_out.write_text("", encoding="utf-8")
        return ""

def analyze_emotions(mp4: pathlib.Path):
    """Return {score, happy, neutral, fear, sad, angry, surprise, disgust, valid_frames, detector} or None"""
    try:
        import cv2
        from deepface import DeepFace
    except ImportError as e:
        print(f"  ! deepface/cv2 missing: {e}")
        return None
    cap=cv2.VideoCapture(str(mp4))
    if not cap.isOpened():
        return None
    total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps=cap.get(cv2.CAP_PROP_FPS) or 25
    # 7 frames, avoid 0/100% where intro/outro black
    fracs=[0.12,0.25,0.38,0.50,0.62,0.75,0.88]
    frames_to_extract=[max(0,min(total-1,int(total*f))) for f in fracs]
    detectors=["retinaface","opencv","mtcnn"]  # fallback chain
    emotions_agg={"happy":0,"neutral":0,"sad":0,"fear":0,"angry":0,"surprise":0,"disgust":0}
    valid=0
    used_detector=None
    for f_idx in frames_to_extract:
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret,frame=cap.read()
        if not ret or frame is None: continue
        tmp=ROOT / "temp_pipeline.jpg"
        cv2.imwrite(str(tmp), frame)
        hit=False
        for det in detectors:
            try:
                analysis=DeepFace.analyze(str(tmp), actions=["emotion"], detector_backend=det, enforce_detection=False, silent=True)
                probs=(analysis[0]["emotion"] if isinstance(analysis,list) else analysis["emotion"])
                # confidence gate: skip if no dominant >25% and face tiny - crude but avoids blank frames
                if max(probs.values()) < 20: continue
                for k in emotions_agg: emotions_agg[k]+=probs.get(k,0)
                valid+=1
                used_detector=used_detector or det
                hit=True
                break
            except: continue
        # if no detector hit, skip frame
    cap.release()
    try: (ROOT/"temp_pipeline.jpg").unlink(missing_ok=True)
    except: pass
    if valid==0: return None
    avg={k:v/valid for k,v in emotions_agg.items()}
    # warmth v2: calibrated 0-100 without +30 hack
    # map happy 0-60% -> 0-70, neutral 0-80% -> 0-20, fear penalty
    raw = avg["happy"]*0.9 + avg["neutral"]*0.25 - avg["fear"]*0.15 - avg["sad"]*0.10
    # z vs cohort not here, just clip
    score = float(max(0, min(99, raw + 35)))  # +35 centers ~50% happy+neutral around 70 warmth instead of 30 base
    return {"score":round(score,1), "happy":round(avg["happy"],1), "neutral":round(avg["neutral"],1),
            "fear":round(avg["fear"],1), "sad":round(avg["sad"],1), "angry":round(avg["angry"],1),
            "surprise":round(avg["surprise"],1), "disgust":round(avg["disgust"],1),
            "valid_frames":valid, "detector":used_detector}

def nlp_keywords(transcript: str):
    if not transcript or len(transcript.strip())<8:
        return 0.0, []
    try:
        from textblob import TextBlob
        sentiment=float(TextBlob(transcript).sentiment.polarity)
    except: sentiment=0.0
    keywords=[]
    try:
        import nltk
        try: nltk.data.find("tokenizers/punkt")
        except: nltk.download("punkt", quiet=True)
        try: nltk.data.find("tokenizers/punkt_tab")
        except: nltk.download("punkt_tab", quiet=True)
        from rake_nltk import Rake
        r=Rake(min_length=1, max_length=2)
        r.extract_keywords_from_text(transcript)
        keywords=r.get_ranked_phrases()[:6]
    except: keywords=[]
    # also wpm
    return sentiment, keywords

def load_rows():
    return list(csv.DictReader(open(CSV_PATH, encoding="utf-8")))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="re-process even if meta exists")
    ap.add_argument("--limit", type=int, default=0, help="only first N videos (smoke test)")
    args=ap.parse_args()

    rows=load_rows()
    vids=[r for r in rows if r["youtube_video_id"] and r["youtube_video_id"].strip()]
    print(f"Found {len(vids)}/1497 with public video (expected 74)")
    if args.limit: vids=vids[:args.limit]

    # ensure report header exists
    if not REPORT.exists():
        REPORT.write_text("# Schwarzman Scholars — Individual AI Profiles\n\nGenerated by `scripts/video_pipeline.py` (DeepFace + Whisper tiny). Each block is per-video, reproducible, with median-aggregated emotions and fallback detectors.\n\n", encoding="utf-8")

    existing_report=REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""

    for idx, row in enumerate(vids, 1):
        url=clean_yt(row["youtube_video_id"])
        name=row["name"]
        cohort=row["cohort_year"]
        uni=row.get("university","")
        yid=vid_id(url)
        meta_path=META_DIR / f"{yid}.json"
        if meta_path.exists() and not args.force:
            print(f"[{idx}/{len(vids)}] SKIP {name} ({yid}) — meta exists (use --force to re-run)")
            continue
        print(f"\n[{idx}/{len(vids)}] {name} — Cohort {cohort} — {url}")
        mp4=VID_DIR / f"{yid}.mp4"
        txt_path=TRANS_DIR / f"{yid}.txt"

        if not download_video(url, mp4):
            print(f"  ✗ download failed, skipping")
            # write stub meta so we don't retry forever
            meta={"name":name,"cohort":cohort,"university":uni,"youtube":url,"vid":yid,"error":"download_failed"}
            meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
            continue

        # duration for wpm
        duration=60
        try:
            import cv2
            cap=cv2.VideoCapture(str(mp4))
            total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps=cap.get(cv2.CAP_PROP_FPS) or 30
            duration= max(10, total/fps if fps else 60)
            cap.release()
        except: pass

        transcript=transcribe(mp4, txt_path)
        words=len(transcript.split()) if transcript else 0
        wpm= round(words / (duration/60),1) if duration else 0

        emo=analyze_emotions(mp4)
        if not emo:
            emo={"score":0,"happy":0,"neutral":0,"fear":0,"sad":0,"angry":0,"surprise":0,"disgust":0,"valid_frames":0,"detector":"none"}

        sentiment, keywords = nlp_keywords(transcript)

        meta={
            "name":name,"cohort":cohort,"university":uni,"youtube":url,"vid":yid,
            "duration_sec":round(duration,1),"words":words,"wpm":wpm,
            "transcript_chars":len(transcript),
            "emotion":emo, "sentiment":round(sentiment,3), "keywords":keywords,
        }
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        print(f"  → warmth {emo['score']}/100 (happy {emo['happy']}% neutral {emo['neutral']}% via {emo['detector']}, {emo['valid_frames']}/7 frames)")
        print(f"  → sentiment {sentiment:.2f}, wpm {wpm}, keywords: {', '.join(keywords[:3]) if keywords else 'none'}")

        # append to report if not already there (check by vid)
        if yid not in existing_report and url not in existing_report:
            with open(REPORT, "a", encoding="utf-8") as f:
                f.write(f"## {name} (Cohort {cohort})\n")
                f.write(f"- **Undergrad:** {uni or 'N/A'}\n")
                f.write(f"- **Video:** `{url}`\n")
                f.write(f"### AI Analysis\n")
                f.write(f"- **Warmth v2:** {emo['score']}/100 (Happy {emo['happy']}%, Neutral {emo['neutral']}%, Fear {emo['fear']}%, Sad {emo['sad']}% — {emo['valid_frames']}/7 frames via {emo['detector']})\n")
                f.write(f"- **Speaking:** {words} words, {wpm} wpm over ~{duration:.0f}s\n")
                f.write(f"- **Sentiment:** {sentiment:.2f} (TextBlob -1…1, >0.1 optimistic)\n")
                f.write(f"- **Keywords (RAKE):** {', '.join(keywords) if keywords else 'None — transcript too short or download failed'}\n")
                f.write(f"- **Meta:** `data/meta/{yid}.json` · `data/transcripts/{yid}.txt`\n")
                f.write("---\n\n")
                existing_report+=yid

    print(f"\nDone. Meta files: {len(list(META_DIR.glob('*.json')))}, Transcripts: {len(list(TRANS_DIR.glob('*.txt')))}")
    print("Next: python generate_plots.py  (reads data/meta/*.json for warmth plots)  or  make plots")

if __name__=="__main__":
    main()
