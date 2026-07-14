# Contributing to the Schwarzman Scholars Open Data Project

Thank you for wanting to contribute! This project relies on community submissions to stay up to date and provide the best resources for future applicants.

## How to Contribute

### 1. Adding Your Introduction Video
If you are a Schwarzman Scholar (or applicant) and you have a public 1-minute introduction video on YouTube, you can add it to our database:
1. Fork this repository.
2. Edit the `data/schwarzman_scholars_dataset.csv` file.
3. Find your row (search by name) and update the `youtube_video_id` column with the full URL of your YouTube video (e.g., `https://youtube.com/watch?v=dQw4w9WgXcQ`).
4. Commit your changes and submit a Pull Request!

### 2. Fixing Typos or Updating Bios
If your bio is outdated or contains a typo, feel free to submit a Pull Request updating the `bio` column in `data/schwarzman_scholars_dataset.csv`.

### 3. Adding New Analytics
Data scientists, we welcome you! If you have a cool idea for visualizing this dataset:
1. Create new charts locally using Python, R, or your preferred tool.
2. Save your visualization images as `.png` files in the `analytics_dashboard/` directory.
3. Update the main `README.md` to display your new graph and briefly explain the insight.
4. Submit a Pull Request!

## Code of Conduct
Please remember that this is a collaborative, positive environment aimed at helping students. Keep all contributions respectful. Do not add or infer demographic data (like ethnicity or religious affiliation) that the scholars have not made explicitly public in their biographies.
