# Data Dictionary — `data/schwarzman_scholars_dataset.csv`

**1,497 rows × 9 columns • 2017–2027 cohorts • UTF-8, quoted bios • 74 rows have a public YouTube intro**

| Column | Type | Example | Notes |
|---|---|---|---|
| `id` | Integer | `1` | Stable row id (1..1497). Do not treat as rank. |
| `name` | String | `Amber` | Full name as on Schwarzman site. No duplicates. |
| `country` | String | `China` | Citizenship / country of origin as listed. `Top 3: United States 617, China 300, United Kingdom 50`. |
| `university` | String | `Peking University` or `Peking University, New York University` | Undergraduate affiliation(s) verbatim. Some scholars list joint degrees — string contains comma, hence CSV-quoted. |
| `cohort_year` | Integer (as string) | `2026` | Cohort start year (2026 = 2026–27 academic year). Range 2017–2027. Counts: 2017:108, 2018:125, 2019:135, 2020:139, 2021:131, 2022:150, 2023:142, 2024:142, 2025:140, 2026:144, 2027:141. |
| `youtube_video_id` | String (URL or empty) | `https://www.youtube.com/watch?v=jasK1AyzUhE` or `https://www.youtube.com/shorts/yOkVcvo2wgM` or empty | Canonical public 1-min intro link. **74 rows** non-empty (4.9%). Cleaned — no `&pp=` tracking params (59 rows were stripped). Empty means no public video found. |
| `admission_inferred` | Boolean 0/1 | `1` | `1` = confirmed admitted (all 1,497 here). Legacy column — will be deprecated; use presence in file as admission. |
| `bio` | String (quoted, multiline) | `Amber was born and raised in...` | Official public biography text. **285 rows** non-empty (19%), avg ~685 chars. Multiline, CSV-quoted; preserve newlines. Empty means no public bio for that cohort/year. |
| `has_intro_video` | Boolean 0/1 | `1` | `1` if `youtube_video_id` non-empty after cleaning, else `0`. Should match URL presence — fixed 1 mismatch in recent clean. |

## Derived / locally generated (not in CSV)

| Artifact | How to generate | Description |
|---|---|---|
| `data/videos/{youtube_id}.mp4` | `python batch_processor.py` (needs `yt-dlp`) | Cached video file. Not committed — download on demand. |
| `data/transcripts/{youtube_id}.txt` | `batch_processor.py` via `openai/whisper tiny` | Auto-transcription of intro audio. Commit only with scholar consent. |
| `ADMITTED_SCHOLAR_PROFILES.md` | `batch_processor.py` (DeepFace + TextBlob + RAKE) | Per-video warmth score, sentiment, top 5 key phrases. |

## Encoding quirks

- Bios contain commas, smart quotes (`’`), and `&amp;` entities — file is RFC-4180 quoted. Use `csv.DictReader`, don't split on `,`.
- `youtube_video_id` may be `watch?v=` or `shorts/` — normalize with `urllib.parse.parse_qs` on `v=` param.
- `country` is citizenship as listed; do not infer ethnicity/religion. Respect `CONTRIBUTING.md` ethics rule.

## Example row (truncated)

```
1,Amber,China,Peking University,2026,https://www.youtube.com/watch?v=...,0,"Gesangzhuoma (Amber) was born ...",0
74,Celene Aridin,United States of America,University of California Davis,2026,https://www.youtube.com/watch?v=jasK1AyzUhE,1,"...",1
```

## Validation

```python
import csv
rows = list(csv.DictReader(open("data/schwarzman_scholars_dataset.csv", encoding="utf-8")))
assert len(rows) == 1497
assert sum(1 for r in rows if r["youtube_video_id"]) == 74  # 4.9%
assert sum(1 for r in rows if r["bio"]) == 285
assert all("pp=" not in (r["youtube_video_id"] or "") for r in rows)
```
