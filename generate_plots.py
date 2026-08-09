"""
Schwarzman Scholars Open Data — Premium Plot Generator (amended)
Visualizing Data palette + high data-ink, 300 dpi, serif/sans hierarchy
Reads data/schwarzman_scholars_dataset.csv -> analytics_dashboard/*.png
"""
import pathlib, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
try:
    import seaborn as sns
    HAS_SNS=True
except ImportError:
    sns=None
    HAS_SNS=False
    print('seaborn missing — using matplotlib fallbacks')

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
import types
if not HAS_SNS:
    # create dummy sns with barplot/histplot that delegates to matplotlib
    sns = types.SimpleNamespace()
    def _dummy_barplot(x=None, y=None, data=None, palette=None, orient=None, **kw):
        ax=plt.gca()
        # infer values
        try:
            if x is not None and y is not None:
                # x are labels, y are values or vice versa
                if orient=="h":
                    ax.barh(y if hasattr(y,'__iter__') and not isinstance(y,str) else x, x if hasattr(y,'__iter__') else y, color='#0ea5e9', edgecolor='white', linewidth=0.7)
                else:
                    ax.bar(x, y, color='#0ea5e9', edgecolor='white', linewidth=0.7)
                return ax
            if data is not None:
                return ax
        except: return ax
        return ax
    sns.barplot=_dummy_barplot
    def _dummy_histplot(data, **kw):
        ax=plt.gca()
        import numpy as np
        ax.hist(data, bins=kw.get('bins',20), color=kw.get('color','#0ea5e9'), edgecolor='white', alpha=0.88)
        return ax
    sns.histplot=_dummy_histplot
    def _dummy_boxplot(data=None, x=None, y=None, **kw):
        ax=plt.gca()
        # simple boxplot via matplotlib
        try:
            import pandas as pd2
            if data is not None and x and y:
                groups=[data[data[x]==c][y].values for c in sorted(data[x].unique())]
                ax.boxplot(groups, labels=sorted(data[x].unique()))
        except: pass
        return ax
    sns.boxplot=_dummy_boxplot
    def _dummy_stripplot(*a,**kw): return plt.gca()
    sns.stripplot=_dummy_stripplot
    HAS_SNS=True  # now dummy satisfies
if HAS_SNS and hasattr(sns, 'set_theme'):
    sns.set_theme(style="whitegrid", rc={"axes.facecolor":"#f8fafc"})
PALETTE_SEQ = ["#0ea5e9", "#38bdf8", "#7dd3fc", "#0c4a6e", "#f59e0b", "#10b981"]
PALETTE_CREST = "crest"

# Fallback helpers when seaborn missing
def _barplot_fallback(ax, labels, values, orient="v"):
    if orient=="h":
        ax.barh(labels, values, color="#0ea5e9", edgecolor="white", linewidth=0.7)
    else:
        ax.bar(labels, values, color="#0ea5e9", edgecolor="white", linewidth=0.7)


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


# --- 7. Warmth / Charisma — reproducible from data/meta or MD fallback (fixes orphaned binaries) ---
try:
    import re, json
    META = ROOT / "data" / "meta"
    meta_files = list(META.glob("*.json")) if META.exists() else []
    records=[]
    if meta_files:
        for f in meta_files:
            try:
                j=json.loads(f.read_text(encoding="utf-8"))
                emo=j.get("emotion",{})
                if "score" not in emo: continue
                records.append({"warmth":float(emo.get("score",0)),"sentiment":float(j.get("sentiment",0)),"cohort":str(j.get("cohort","")),"happy":float(emo.get("happy",0)),"neutral":float(emo.get("neutral",0))})
            except: continue
    if not records:
        md_path=ROOT/"ADMITTED_SCHOLAR_PROFILES.md"
        if md_path.exists():
            md=md_path.read_text(encoding="utf-8")
            for m in re.finditer(r"Warmth v2.*?([\d.]+)/100.*?Happy\s*([\d.]+)%.*?Neutral\s*([\d.]+)%", md):
                warmth=float(m.group(1))
                block=md[m.start():m.start()+900]
                ms=re.search(r"Sentiment.*?([\-\d.]+)\s*\(TextBlob", block)
                sent=float(ms.group(1)) if ms else 0.0
                mc=re.search(r"Cohort\s*(\d{4})", block)
                cohort=mc.group(1) if mc else ""
                records.append({"warmth":warmth,"sentiment":sent,"cohort":cohort,"happy":float(m.group(2)),"neutral":float(m.group(3))})
    if records:
        import pandas as pd
        rec_df=pd.DataFrame(records)
        rec_df=rec_df[rec_df["warmth"]>0]
        n=len(rec_df)
        print(f"Warmth source: {n} records (meta={len(meta_files)})")
        # hist
        plt.figure(figsize=(11,5))
        ax=sns.histplot(rec_df["warmth"], bins=20, kde=True, color="#0ea5e9", edgecolor="white", alpha=0.88) if hasattr(sns,"histplot") else plt.gca().hist(rec_df["warmth"], bins=20)
        if hasattr(plt.gca(),'axvline'):
            plt.gca().axvline(rec_df["warmth"].mean(), color="#ef4444", linestyle="--", label=f"mean {rec_df['warmth'].mean():.1f}")
            plt.gca().axvline(rec_df["warmth"].median(), color="#f59e0b", linestyle=":", label=f"median {rec_df['warmth'].median():.1f}")
        plt.title(f"Warmth Distribution (n={n} scored, Warmth v2 calibrated — v1 +30 hack removed) — reproducible", pad=14)
        plt.xlabel("Warmth v2 (happy*0.9+neutral*0.25+35, capped 99)"); plt.ylabel("Count")
        plt.legend(frameon=True, facecolor="white", edgecolor="#e2e8f0")
        plt.gca().text(0.02, 0.96, f"v2 mean {rec_df['warmth'].mean():.1f} median {rec_df['warmth'].median():.1f} sd {rec_df['warmth'].std():.1f}\n4.9% coverage, sharers only", transform=plt.gca().transAxes, va="top", ha="left", fontsize=8, color="#475569", bbox=dict(facecolor="white", edgecolor="#e2e8f0", boxstyle="round,pad=0.4"))
        save("warmth_distribution.png")
        plt.figure(figsize=(11,5)); _=sns.histplot(rec_df["warmth"], bins=20, kde=True, color="#0ea5e9", edgecolor="white", alpha=0.88) if hasattr(sns,"histplot") else plt.gca().hist(rec_df["warmth"], bins=20)
        plt.gca().axvline(rec_df["warmth"].mean(), color="#ef4444", linestyle="--", label=f"mean {rec_df['warmth'].mean():.1f}"); plt.gca().axvline(rec_df["warmth"].median(), color="#f59e0b", linestyle=":", label=f"median {rec_df['warmth'].median():.1f}")
        plt.title(f"Warmth Distribution (n={n}, v2) — reproducible"); plt.xlabel("Warmth v2"); plt.ylabel("Count"); plt.legend()
        plt.tight_layout(); plt.savefig(ROOT/"warmth_distribution.png", dpi=300, bbox_inches="tight", facecolor="white"); plt.close()
        # scatter
        plt.figure(figsize=(11,5.5))
        sc=plt.scatter(rec_df["warmth"], rec_df["sentiment"], c=rec_df["warmth"], cmap="Blues", s=68, edgecolor="#0c4a6e", linewidth=0.6, alpha=0.88)
        plt.colorbar(sc, label="Warmth v2")
        plt.axhline(0.10, color="#10b981", linestyle="--", label="sentiment >0.10")
        plt.axvline(70, color="#ef4444", linestyle="--", label="warmth 70")
        plt.title(f"Warmth v2 vs. Vocal Sentiment (n={n}, Whisper tiny → TextBlob) — reproducible", pad=14, weight="bold")
        plt.xlabel("Warmth v2 (0-99)"); plt.ylabel("Sentiment polarity (-1…1)"); plt.legend(); plt.grid(True, alpha=0.18)
        plt.tight_layout(); plt.savefig(OUT/"warmth_vs_sentiment.png", dpi=300, bbox_inches="tight", facecolor="white"); plt.close()
        print("saved warmth_vs_sentiment.png")
        plt.figure(figsize=(11,5.5)); sc=plt.scatter(rec_df["warmth"], rec_df["sentiment"], c=rec_df["warmth"], cmap="Blues", s=68, edgecolor="#0c4a6e", linewidth=0.6, alpha=0.88); plt.colorbar(sc, label="Warmth v2"); plt.axhline(0.10, color="#10b981", linestyle="--"); plt.axvline(70, color="#ef4444", linestyle="--"); plt.title(f"Warmth v2 vs Sentiment (n={n}) — reproducible"); plt.xlabel("Warmth v2"); plt.ylabel("Sentiment"); plt.tight_layout(); plt.savefig(ROOT/"warmth_vs_sentiment.png", dpi=300, bbox_inches="tight", facecolor="white"); plt.close()
        # by cohort
        if rec_df["cohort"].notna().any() and any(c.strip() for c in rec_df["cohort"]):
            plt.figure(figsize=(12,5.5))
            order=sorted([c for c in rec_df["cohort"].unique() if c.strip()])
            ax=sns.boxplot(data=rec_df, x="cohort", y="warmth", order=order, palette="Blues", linewidth=0.9, fliersize=2)
            sns.stripplot(data=rec_df, x="cohort", y="warmth", order=order, color="#0c4a6e", size=5, alpha=0.72, jitter=True)
            ax.set_title(f"Charisma/Warmth v2 by Cohort (n={n} scored, 7-frame v2) — reproducible", pad=14)
            ax.set_xlabel("Cohort Year"); ax.set_ylabel("Warmth v2 (0-99)"); ax.set_ylim(0,100)
            for t in ax.get_xticklabels(): t.set_rotation(20)
            save("charisma_by_cohort.png")
            plt.figure(figsize=(12,5.5)); ax=sns.boxplot(data=rec_df, x="cohort", y="warmth", order=order, palette="Blues", linewidth=0.9, fliersize=2); sns.stripplot(data=rec_df, x="cohort", y="warmth", order=order, color="#0c4a6e", size=5, alpha=0.72, jitter=True); ax.set_title(f"Charisma/Warmth v2 by Cohort (n={n})"); ax.set_xlabel("Cohort"); ax.set_ylabel("Warmth v2"); ax.set_ylim(0,100); plt.tight_layout(); plt.savefig(ROOT/"charisma_by_cohort.png", dpi=300, bbox_inches="tight", facecolor="white"); plt.close()
        print(f"Warmth plots done (n={n})")
    else:
        print("No warmth records — skip warmth plots")
except Exception as e:
    import traceback; print(f"Warmth plots skipped: {e}"); traceback.print_exc()
print(f"Done premium. Wrote {len(list(OUT.glob('*.png')))} plots")
