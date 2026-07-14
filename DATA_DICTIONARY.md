# Data Dictionary

This document describes the columns available in the `data/schwarzman_scholars_dataset.csv` file.

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| `id` | Integer | A unique identifier for the database entry. |
| `name` | String | The full name of the scholar or applicant. |
| `country` | String | The country of origin or citizenship. |
| `university` | String | The undergraduate institution attended by the scholar. |
| `cohort_year` | Integer | The year the scholar's cohort begins the program (e.g., 2026 for the 2026-2027 academic year). |
| `youtube_video_id` | String | The full URL link to the applicant's 1-minute public introduction video. |
| `admission_inferred` | Boolean (0/1) | Indicates whether admission is confirmed (1) or rejected/unknown (0). |
| `bio` | String | The text of the scholar's official public biography (if available). |
| `has_intro_video` | Boolean (0/1) | Indicates if the scholar submitted a public introduction video (1) or not (0). |
