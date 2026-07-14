import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as plt_sns
import os

out_dir = '/Users/alrarsung/.gemini/antigravity-cli/brain/e67cd145-fd0e-46ab-9da5-735cc3381614'

plt.style.use('dark_background')
plt_sns.set_palette('crest')

conn = sqlite3.connect('scholars.db')
df = pd.read_sql_query('SELECT * FROM scholars', conn)
conn.close()

# 1. Cohort
plt.figure(figsize=(10, 5))
cohort_counts = df['cohort_year'].value_counts().sort_index()
plt_sns.barplot(x=cohort_counts.index, y=cohort_counts.values)
plt.title('Total Scholars per Cohort Year')
plt.ylabel('Count')
plt.xlabel('Cohort Year')
plt.tight_layout()
plt.savefig(f'{out_dir}/cohort_trends.png')
plt.close()

# 2. Unis
plt.figure(figsize=(12, 6))
top_unis = df['university'].value_counts().head(15)
plt_sns.barplot(y=top_unis.index, x=top_unis.values, orient='h')
plt.title('Top 15 Feeder Universities')
plt.xlabel('Number of Scholars')
plt.ylabel('University')
plt.tight_layout()
plt.savefig(f'{out_dir}/top_unis.png')
plt.close()

# 3. Video
plt.figure(figsize=(8, 5))
video_counts = df['has_intro_video'].value_counts().rename(index={1: 'Has Video', 0: 'No Video'})
plt.pie(video_counts, labels=video_counts.index, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff'])
plt.title('Proportion of Scholars with Known Intro Videos')
plt.tight_layout()
plt.savefig(f'{out_dir}/video_submissions.png')
plt.close()

# 4. Countries
plt.figure(figsize=(12, 6))
top_countries = df['country'].value_counts().head(10)
plt_sns.barplot(x=top_countries.values, y=top_countries.index, orient='h')
plt.title('Top 10 Countries of Origin')
plt.xlabel('Number of Scholars')
plt.ylabel('Country')
plt.tight_layout()
plt.savefig(f'{out_dir}/top_countries.png')
plt.close()
