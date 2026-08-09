"""
Schwarzman Scholars Open Data — Plot Generator
Reads data/schwarzman_scholars_dataset.csv and renders analytics_dashboard/*.png
Run: python generate_plots.py
"""
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data" / "schwarzman_scholars_dataset.csv"
OUT = ROOT / "analytics_dashboard"
OUT.mkdir(parents=True, exist_ok=True)

# Use a reproducible style that works without dark_background dependency
plt.style.use("default")
sns.set_theme(style="whitegrid")
PALETTE = "crest"

df = pd.read_csv(DATA, encoding="utf-8")
# normalize types
df["cohort_year"] = df["cohort_year"].astype(str)
df["has_intro_video"] = pd.to_numeric(df["has_intro_video"], errors="coerce").fillna(0).astype(int)
# strip pp remnants already cleaned, but ensure youtube id is canonical
# count scholars per cohort
# 1. Cohort trends (2017-2027)
plt.figure(figsize=(10, 5))
cohort_counts = df["cohort_year"].value_counts().sort_index()
ax = sns.barplot(x=cohort_counts.index, y=cohort_counts.values, palette=PALETTE)
ax.set_title("Scholars per Cohort Year (2017-2027, n=1497)")
ax.set_ylabel("Count")
ax.set_xlabel("Cohort Year")
for i, v in enumerate(cohort_counts.values):
    ax.text(i, v + 1, str(v), ha="center", fontsize=9)
plt.tight_layout()
plt.savefig(OUT / "cohort_trends.png", dpi=200)
plt.close()

# 2. Top 15 feeder universities
plt.figure(figsize=(12, 6))
# Split combined universities like "Harvard, MIT" -> count each separately for ranking clarity
# Keep original for plot label, but also show split: here we use raw string value_counts
top_unis = df["university"].dropna()
# Filter out obvious noise: empty, single char
top_unis = top_unis[top_unis.str.strip().str.len() > 2]
top_unis = top_unis.value_counts().head(15)
ax = sns.barplot(y=top_unis.index, x=top_unis.values, orient="h", palette=PALETTE)
ax.set_title("Top 15 Feeder Universities (raw affiliation string)")
ax.set_xlabel("Number of Scholars")
ax.set_ylabel("University")
plt.tight_layout()
plt.savefig(OUT / "top_unis.png", dpi=200)
plt.close()

# 3. Video submission proportion
plt.figure(figsize=(8, 5))
video_counts = df["has_intro_video"].value_counts().rename(index={1: "Has Video (74)", 0: "No Video"})
colors = ["#66b3ff", "#ff9999"] if 1 in df["has_intro_video"].values else ["#ff9999"]
plt.pie(video_counts, labels=video_counts.index, autopct="%1.1f%%", startangle=90, colors=colors[:len(video_counts)])
plt.title("Intro Video Coverage (74 / 1497 = 4.9% public)")
plt.tight_layout()
plt.savefig(OUT / "video_submissions.png", dpi=200)
plt.close()

# 4. Top 10 countries
plt.figure(figsize=(12, 6))
top_countries = df["country"].dropna()
top_countries = top_countries[top_countries.str.strip().str.len() > 1]
# Remove numeric placeholders if any remain
top_countries = top_countries[~top_countries.str.strip().isin(["0", "and"])]
top_countries = top_countries.value_counts().head(10)
ax = sns.barplot(x=top_countries.values, y=top_countries.index, orient="h", palette=PALETTE)
ax.set_title("Top 10 Countries of Origin")
ax.set_xlabel("Number of Scholars")
ax.set_ylabel("Country")
for i, v in enumerate(top_countries.values):
    ax.text(v + 3, i, str(v), va="center", fontsize=9)
plt.tight_layout()
plt.savefig(OUT / "top_countries.png", dpi=200)
plt.close()

# 5. Videos per cohort (only where has_intro_video == 1)
plt.figure(figsize=(10, 5))
videos_per_cohort = df[df["has_intro_video"] == 1]["cohort_year"].value_counts().sort_index()
# Ensure all cohorts appear even with 0
all_cohorts = sorted(df["cohort_year"].unique())
videos_per_cohort = videos_per_cohort.reindex(all_cohorts, fill_value=0)
ax = sns.barplot(x=videos_per_cohort.index, y=videos_per_cohort.values, palette="viridis")
ax.set_title("Public Intro Videos per Cohort (n=74)")
ax.set_ylabel("Videos found")
ax.set_xlabel("Cohort Year")
for i, v in enumerate(videos_per_cohort.values):
    if v > 0:
        ax.text(i, v + 0.2, str(int(v)), ha="center", fontsize=9)
plt.tight_layout()
plt.savefig(OUT / "videos_per_cohort.png", dpi=200)
plt.close()

# 6. Stacked country share over time (optional, for README)
try:
    plt.figure(figsize=(12, 6))
    top5 = df["country"].value_counts().head(5).index.tolist()
    # bucket others
    df["country_bucket"] = df["country"].apply(lambda c: c if c in top5 else "Other")
    ct = pd.crosstab(df["cohort_year"], df["country_bucket"], normalize="index") * 100
    ct = ct.reindex(sorted(ct.index))
    ct.plot(kind="bar", stacked=True, colormap="tab20", figsize=(12, 6), ax=plt.gca())
    plt.title("Country Composition by Cohort (%, top 5 + Other)")
    plt.ylabel("Share of cohort (%)")
    plt.xlabel("Cohort Year")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(OUT / "country_share_by_cohort.png", dpi=200)
    plt.close()
except Exception as e:
    print(f"Skipping stacked share plot: {e}")

print(f"Done. Wrote {len(list(OUT.glob('*.png')))} plots to {OUT}")
print(f"Rows: {len(df)}, Videos: {int(df['has_intro_video'].sum())}, Bios: {df['bio'].notna().sum()}")
