# Contributing

Thank you for helping demystify Schwarzman admissions — this repo lives on hand-checked data + scholar consent.

## 1) Add / fix your intro video

You are a Schwarzman Scholar with a public 1-min video?

1. Fork → edit `data/schwarzman_scholars_dataset.csv`
2. Find your row (by `name`) → set `youtube_video_id` to the **canonical** URL:
   - `https://www.youtube.com/watch?v=XXXXXXXXXXX` or
   - `https://www.youtube.com/shorts/XXXXXXXXXXX`
   - No `&pp=`, no `&t=`, no trailing params — they break `yt-dlp`. The recent clean stripped 59 such params.
3. Set `has_intro_video=1` if you added a link, `0` if removing. Keep `admission_inferred=1`.
4. PR with a clear title: `Add video: First Last (Cohort 2027)` or `Fix video: strip pp param`.

We’ll verify the link is public and re-run `python batch_processor.py` to generate your transcript/keywords — only committed if you consent in the PR.

## 2) Fix a bio / affiliation

- Edit the `bio` or `university` cell **exactly** as on `schwarzmanscholars.org`. Keep CSV quoting (multiline bios must stay `"..."` quoted).
- If you were interviewed for this repo and your summary exists in `INTERVIEWS.md` (coming), you can correct it via PR too.

## 3) Add analytics

1. Create your plot locally — use `python generate_plots.py` as template (reads `data/schwarzman_scholars_dataset.csv`, writes to `analytics_dashboard/`).
2. Save as `analytics_dashboard/your_plot_name.png` (200 dpi, no hardcoded absolute paths).
3. Add a 2–3 sentence insight in `README.md` under “Analytics Dashboard” and reference the image as `analytics_dashboard/your_plot_name.png`.
4. PR.

**Good first plots we want:** `country_share_by_cohort.png` (already scaffolded), `feeder HHI per cohort`, `bio word count distribution`, `transcript speaking rate`.

## 4) Transcripts & interviews

- Transcripts live in `data/transcripts/{youtube_id}.txt` (Whisper tiny, manual-fixed). Do **not** commit a transcript for a scholar who hasn’t consented to publish it — keep it local. Open an Issue: `Transcript consent: Name (ID)` and we’ll tag you.
- Interview notes for `INTERVIEWS.md` are anonymized by default. If you were interviewed and want attribution or removal, PR or email via your interview contact.

## Ethics — non-negotiable

- **Do not** add or infer ethnicity, religion, gender identity, political affiliation, or other protected traits. Only what the scholar explicitly published or consented to in an interview.
- **Takedowns honored same-day:** Open an Issue titled `Takedown: Name` or email the maintainer; we remove bio/video/transcript and re-render plots within 24h.
- Be respectful — this is a public-good dataset to help applicants, not to rank people.

## Dev quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python generate_plots.py          # no network needed
python batch_processor.py         # needs yt-dlp + ~2GB whisper model, slow
```

Questions? Open an Issue — we respond faster there than email.
