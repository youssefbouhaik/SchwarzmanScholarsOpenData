# Contributing to the Schwarzman Scholars Open Data Project

Thank you for wanting to contribute! This project relies on community submissions to stay up to date and provide the best resources for future applicants.

## How to Contribute

### 1. Adding Your Introduction Video
If you are a Schwarzman Scholar (or applicant) and you have a public 1-minute introduction video on YouTube, you can add it to our database:
1. Fork this repository.
2. Edit the `data/scholars_public.csv` file.
3. Find your row (search by name) and update the `youtube_video_id` column with the 11-character ID of your YouTube video (e.g., if your link is `https://youtube.com/watch?v=dQw4w9WgXcQ`, put `dQw4w9WgXcQ`).
4. Commit your changes and submit a Pull Request!

### 2. Fixing Typos or Updating Bios
If your bio is outdated or contains a typo, feel free to submit a Pull Request updating the `bio` column in `scholars_public.csv`.

### 3. Adding New Analytics
Data scientists, we welcome you! If you have a cool idea for visualizing this dataset:
1. Create a new Jupyter notebook in the `notebooks/` directory.
2. Ensure your code is well-commented and easy to read.
3. Submit a Pull Request with a brief explanation of the insights you discovered!

## Code of Conduct
Please remember that this is a collaborative, positive environment aimed at helping students. Keep all contributions respectful. Do not add or infer demographic data (like ethnicity or religious affiliation) that the scholars have not made explicitly public in their biographies.
