# 📊 Schwarzman Scholars Data Analytics

Here are the visual trends extracted from your newly updated database. Since you've corrected the `youtube_video_id` tags for cohorts all the way back to 2018, the ML models now correctly interpret video submissions independently of written bios. All plots are reproducible via `python generate_plots.py` (reads `data/schwarzman_scholars_dataset.csv` + `ADMITTED_SCHOLAR_PROFILES.md` / `data/meta/*.json`).

### Global Competitiveness
Here's a breakdown of where the most successful candidates have originated. The program is heavily slanted toward candidates from the US and China, with significant representation from the UK and Canada.
![Top 10 Countries of Origin](top_countries.png)

### Feeder Universities
The most dominant undergraduate institutions for candidates admitted into the program:
![Top 15 Feeder Universities](top_unis.png)

### Video Submissions vs "The Bio Bias"
Thanks to your recent manual corrections (adding YouTube links), we can now accurately see the proportion of candidates who submitted an intro video across all historical cohorts, bypassing the fact that the older cohorts didn't mandate written biographies. 74/1497 = 4.9% public — video findings apply to sharers only.
![Video Submission Rate](video_submissions.png)

### Program Growth Over Time
Overall recorded cohort distribution across the years we've tracked:
![Scholars Per Cohort](cohort_trends.png)

---

## 🤖 DeepFace & NLP — Warmth v2 (calibrated)

We recalibrated the **Warmth v2** pipeline (fixes v1 `+30` hack clipped at 99). v2 = `happy*0.9 + neutral*0.25 - fear*0.15 - sad*0.10 + 35`, 7 frames (12/25/38/50/62/75/88%), fallback RetinaFace→OpenCV→MTCNN, confidence gate. 24/74 scored (mean 63.1, median 57.2 vs v1 mean 71.2); 50 pending — run `make transcripts` to finish. See `ADMITTED_SCHOLAR_PROFILES.md` + `python generate_plots.py`.

### Warmth v2 vs. Vocal Sentiment (n=24 scored)
Warmth v2 (x) vs. Whisper-tiny → TextBlob sentiment (y). v2 shows warm and optimistic are weakly coupled — videos optimistic (0.14) vs. flat-formal bios (0.064).

![Warmth v2 vs Sentiment](warmth_vs_sentiment.png)

### Warmth Distribution (v2, no longer clipped at 99)
![Warmth Distribution](warmth_distribution.png)

### Charisma by Cohort (v2)
![Charisma by Cohort](charisma_by_cohort.png)

*All warmth figures reproducible — `python generate_plots.py` rebuilds them from `ADMITTED_SCHOLAR_PROFILES.md` (fallback) or `data/meta/*.json`.*

---
