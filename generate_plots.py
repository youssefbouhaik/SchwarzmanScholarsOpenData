"""
Schwarzman Scholars Open Data — Premium Plot Generator (amended)
Visualizing Data palette + high data-ink, 300 dpi, serif/sans hierarchy
Reads data/schwarzman_scholars_dataset.csv -> analytics_dashboard/*.png
"""
import pathlib, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data" / "schwarzman_scholars_dataset.csv"
OUT = ROOT / "analytics_dashboard"
OUT.mkdir(parents=True, exist_ok=True)

# Premium style - Visualizing Data inspired
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "#f8fafc",
    "axes.edgecolor": "#e2e8f0",
    "axes.grid": True,
    "grid.color": "#e2e8f0",
    "grid.linestyle": "--",
    "grid.alpha": 0.35,
    "font.family": "DejaVu Sans",
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.titlecolor": "#0f172a",
    "axes.labelcolor": "#475569",
    "xtick.color": "#475569",
    "ytick.color": "#475569",
})
sns.set_theme(style="whitegrid", rc={"axes.facecolor":"#f8fafc"})
PALETTE_SEQ = ["#0ea5e9", "#38bdf8", "#7dd3fc", "#0c4a6e", "#f59e0b", "#10b981"]
PALETTE_CREST = "crest"
df = pd.read_csv(DATA, encoding="utf-8")
df["cohort_year"] = df["cohort_year"].astype(str)
df["has_intro_video"] = pd.to_numeric(df["has_intro_video"], errors="coerce").fillna(0).astype(int)

def save(fig_name):
    plt.tight_layout()
    plt.savefig(OUT / fig_name, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"saved {fig_name}")

# 1. Cohort trends
plt.figure(figsize=(11,5))
cohort_counts = df["cohort_year"].value_counts().sort_index()
ax = sns.barplot(x=cohort_counts.index, y=cohort_counts.values, palette="Blues_d", edgecolor="white", linewidth=0.9)
ax.set_title("Scholars per Cohort Year (2017–2027, n=1497) — amended premium", pad=14)
ax.set_ylabel("Count"); ax.set_xlabel("Cohort Year")
for i, v in enumerate(cohort_counts.values):
    ax.text(i, v+2, str(v), ha="center", fontsize=8, weight="bold", color="#0f172a")
ax.grid(axis="y", alpha=0.18)
save("cohort_trends.png")

# 2. Top 15 feeder universities
plt.figure(figsize=(12,6.5))
top_unis = df["university"].dropna()
top_unis = top_unis[top_unis.str.strip().str.len()>2].value_counts().head(15)
ax = sns.barplot(y=top_unis.index, x=top_unis.values, orient="h", palette="Blues_r", edgecolor="white", linewidth=0.7)
ax.set_title("Top 15 Feeder Universities (raw affiliation string) — premium", pad=14)
ax.set_xlabel("Scholars"); ax.set_ylabel("")
for i, v in enumerate(top_unis.values):
    ax.text(v+1, i, str(v), va="center", fontsize=8, color="#334155")
save("top_unis.png")

# 3. Video submission proportion - donut
plt.figure(figsize=(7,5))
video_counts = df["has_intro_video"].value_counts().rename(index={1: "Has Video (74)", 0: "No Video"})
colors = ["#0ea5e9", "#e2e8f0"]
wedges, texts, autotexts = plt.pie(video_counts, labels=video_counts.index, autopct="%1.1f%%", startangle=90, colors=colors[:len(video_counts)], wedgeprops=dict(width=0.42, edgecolor="white", linewidth=1.5), textprops=dict(fontsize=9, color="#1e293b"), pctdistance=0.85)
plt.title("Intro Video Coverage (74 / 1497 = 4.9% public) — amended", pad=14, weight="bold")
save("video_submissions.png")

# 4. Top 10 countries
plt.figure(figsize=(12,6))
top_countries = df["country"].dropna()
top_countries = top_countries[~top_countries.str.strip().isin(["0","and"])].value_counts().head(10)
ax = sns.barplot(x=top_countries.values, y=top_countries.index, orient="h", palette="Blues_d", edgecolor="white", linewidth=0.7)
ax.set_title("Top 10 Countries of Origin — premium (US-China bridge)", pad=14)
ax.set_xlabel("Scholars"); ax.set_ylabel("")
for i, v in enumerate(top_countries.values):
    ax.text(v+3, i, str(v), va="center", fontsize=8, weight="bold", color="#0f172a")
save("top_countries.png")

# 5. Videos per cohort
plt.figure(figsize=(11,5))
videos_per_cohort = df[df["has_intro_video"]==1]["cohort_year"].value_counts().sort_index()
all_cohorts = sorted(df["cohort_year"].unique())
videos_per_cohort = videos_per_cohort.reindex(all_cohorts, fill_value=0)
ax = sns.barplot(x=videos_per_cohort.index, y=videos_per_cohort.values, palette="viridis", edgecolor="white", linewidth=0.7)
ax.set_title("Public Intro Videos per Cohort (n=74) — amended", pad=14)
ax.set_ylabel("Videos"); ax.set_xlabel("Cohort Year")
for i, v in enumerate(videos_per_cohort.values):
    if v>0: ax.text(i, v+0.25, str(int(v)), ha="center", fontsize=8, weight="bold")
save("videos_per_cohort.png")

# 6. Stacked country share
try:
    plt.figure(figsize=(12,6))
    top5 = df["country"].value_counts().head(5).index.tolist()
    df["country_bucket"] = df["country"].apply(lambda c: c if c in top5 else "Other")
    ct = pd.crosstab(df["cohort_year"], df["country_bucket"], normalize="index")*100
    ct = ct.reindex(sorted(ct.index))
    ct.plot(kind="bar", stacked=True, colormap="tab20", figsize=(12,6), ax=plt.gca(), edgecolor="white", linewidth=0.5, width=0.72)
    plt.title("Country Composition by Cohort (%, top 5 + Other) — Visualizing Data palette", pad=14, weight="bold")
    plt.ylabel("Share (%)"); plt.xlabel("Cohort Year")
    plt.legend(bbox_to_anchor=(1.02,1), loc="upper left", frameon=True, facecolor="white", edgecolor="#e2e8f0")
    save("country_share_by_cohort.png")
except Exception as e:
    print(f"skip stacked {e}")

print(f"Done premium. Wrote {len(list(OUT.glob('*.png')))} plots")
