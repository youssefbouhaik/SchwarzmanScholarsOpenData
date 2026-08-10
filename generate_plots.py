"""
Schwarzman Scholars Open Data — Ensemble Plot Generator
Treemap × L-system unified style · schwarzman_style.py is the single source of truth
Reads data/schwarzman_scholars_dataset.csv -> analytics_dashboard/*.png
Ensemble: Grammar of Graphics (Theme fixed once) + Visual Hierarchy (color sparingly) + Small Multiples
"""
import pathlib, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── Ensemble preamble (same as notebooks/schwarzman_overview.ipynb cell 3) ──
import schwarzman_style as ss
ss.apply_style()

try:
    import seaborn as sns
    HAS_SNS = True
except ImportError:
    sns = None
    HAS_SNS = False
    print('seaborn missing — using matplotlib fallbacks (still ensemble-aligned)')

# For dummy seaborn fallback, route through ensemble tokens instead of #0ea5e9
import types
if not HAS_SNS:
    sns = types.SimpleNamespace()
    def _dummy_barplot(x=None, y=None, data=None, palette=None, orient=None, **kw):
        ax = plt.gca()
        try:
            if x is not None and y is not None:
                if orient == "h":
                    # monochrome slate — area/length encodes, not hue
                    labels = y if hasattr(y, '__iter__') and not isinstance(y, str) else x
                    values = x if hasattr(y, '__iter__') and not isinstance(y, str) else y
                    ss.bar(ax, labels, values, orient="h")
                else:
                    ss.bar(ax, x, y, orient="v")
                return ax
            if data is not None:
                return ax
        except:
            return ax
        return ax
    sns.barplot = _dummy_barplot
    def _dummy_histplot(data, **kw):
        ax = plt.gca()
        import numpy as np
        bins = kw.get('bins', 20)
        # use ink for hist, white edge — monochrome
        ax.hist(data, bins=bins, color=ss.INK, edgecolor=ss.CANVAS, alpha=0.88, linewidth=0.7)
        return ax
    sns.histplot = _dummy_histplot
    def _dummy_boxplot(data=None, x=None, y=None, **kw):
        ax = plt.gca()
        try:
            if data is not None and x and y:
                groups = [data[data[x] == c][y].values for c in sorted(data[x].unique())]
                # patch boxes to ensemble ink/muted
                bp = ax.boxplot(groups, labels=sorted(data[x].unique()), patch_artist=True, boxprops=dict(facecolor=ss.PANEL, edgecolor=ss.BORDER), medianprops=dict(color=ss.SCHWARZMAN_RED, linewidth=1.4), whiskerprops=dict(color=ss.MUTED), capprops=dict(color=ss.MUTED))
                # color boxes with muted ramp
                for patch, c in zip(bp['boxes'], ss.PALETTE_MONO_SEQ):
                    patch.set_facecolor(c)
                    patch.set_alpha(0.18)
        except:
            pass
        return ax
    sns.boxplot = _dummy_boxplot
    def _dummy_stripplot(*a, **kw):
        return plt.gca()
    sns.stripplot = _dummy_stripplot
    HAS_SNS = True

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data" / "schwarzman_scholars_dataset.csv"
OUT = ROOT / "analytics_dashboard"
OUT.mkdir(parents=True, exist_ok=True)

# Ensemble palettes — do NOT reintroduce Blues_d / viridis / crest / tab20
PALETTE_SEQ = ss.PALETTE_MONO_SEQ          # for legacy refs
PALETTE_CREST = ss.CMAP_WARMTH             # warmth scatter uses this, not crest
COLOR_INK = ss.INK
COLOR_RED = ss.SCHWARZMAN_RED
COLOR_MUTED = ss.MUTED
COLOR_BORDER = ss.BORDER

# save helper — keeps outer white generous border like Ref 2 (L-system)
def save(fig_name):
    plt.tight_layout()
    plt.savefig(OUT / fig_name, dpi=ss.SAVEDPI, bbox_inches="tight", facecolor=ss.CANVAS, edgecolor=ss.CANVAS)
    plt.close()
    print(f"saved {fig_name}")

df = pd.read_csv(DATA, encoding="utf-8")
df["cohort_year"] = df["cohort_year"].astype(str)
df["has_intro_video"] = pd.to_numeric(df["has_intro_video"], errors="coerce").fillna(0).astype(int)

# ── 1. Cohort trends — monochrome ramp, darkest = most (area/length encodes) ──
plt.figure(figsize=ss.FIGSIZE_WIDE)
cohort_counts = df["cohort_year"].value_counts().sort_index()
# use ensemble bar helper directly (monochrome, white edges)
fig, ax = plt.subplots(figsize=ss.FIGSIZE_WIDE)
# darkest for largest cohort to enforce Visual Hierarchy
order_idx = cohort_counts.values.argsort()[::-1]
# map rank to palette: darkest for largest
cols = [ss.PALETTE_MONO_BAR[0]] * len(cohort_counts)
# simpler: just use ramp darkest->lightest in data order; keep area as encoding, not hue rank
# we keep straight monochrome ink for all bars — most editorial, like treemap tiles
ax.bar(cohort_counts.index, cohort_counts.values, color=ss.INK, edgecolor=ss.CANVAS, linewidth=0.9, zorder=3)
for i, v in enumerate(cohort_counts.values):
    ax.text(i, v + 2, str(v), ha="center", fontsize=8, weight="bold", color=ss.INK)
ss.style_axes(ax, title="Scholars per Cohort Year (2017–2027, n=1497)", subtitle="Ensemble: monochrome — length encodes, hue stays muted (treemap logic)", source="data/schwarzman_scholars_dataset.csv")
ax.set_ylabel("Count"); ax.set_xlabel("Cohort Year")
save("cohort_trends.png")
plt.close("all")

# ── 2. Top 15 feeder universities — horizontal, monochrome ──
plt.figure(figsize=(12, 6.5))
top_unis = df["university"].dropna()
top_unis = top_unis[top_unis.str.strip().str.len() > 2].value_counts().head(15)
fig, ax = plt.subplots(figsize=(12, 6.5))
ss.bar(ax, top_unis.index, top_unis.values, orient="h")
# annotate
for i, v in enumerate(top_unis.values):
    ax.text(v + 1, i, str(v), va="center", fontsize=8, color=ss.SLATE)
ss.style_axes(ax, title="Top 15 Feeder Universities (raw affiliation string)", subtitle="Raw string — longest bar = most, color is not the encoding", source="data/schwarzman_scholars_dataset.csv")
ax.set_xlabel("Scholars"); ax.set_ylabel("")
save("top_unis.png")
plt.close("all")

# ── 3. Video submission proportion - donut — ink + border only (no #0ea5e9) ──
plt.figure(figsize=ss.FIGSIZE_SQUARE)
video_counts = df["has_intro_video"].value_counts().rename(index={1: "Has Video (74)", 0: "No Video"})
colors = [ss.INK, ss.BORDER]  # ink for the 4.9% slice — Visual Hierarchy highlights the rare
wedges, texts, autotexts = plt.pie(video_counts, labels=video_counts.index, autopct="%1.1f%%", startangle=90,
                                   colors=colors[:len(video_counts)], wedgeprops=dict(width=0.42, edgecolor=ss.CANVAS, linewidth=1.5),
                                   textprops=dict(fontsize=9, color=ss.INK), pctdistance=0.85)
plt.title("Intro Video Coverage (74 / 1497 = 4.9% public)", pad=14, fontsize=12, fontweight="bold", color=ss.INK, fontfamily=ss.SANS[0])
save("video_submissions.png")
plt.close("all")

# ── 4. Top 10 countries — horizontal monochrome ──
fig, ax = plt.subplots(figsize=(12, 6))
top_countries = df["country"].dropna()
top_countries = top_countries[~top_countries.str.strip().isin(["0", "and"])].value_counts().head(10)
ss.bar(ax, top_countries.index, top_countries.values, orient="h")
for i, v in enumerate(top_countries.values):
    ax.text(v + 3, i, str(v), va="center", fontsize=8, weight="bold", color=ss.INK)
ss.style_axes(ax, title="Top 10 Countries of Origin — US-China bridge", subtitle="Monochrome ramp — US #617 darkest, then China #300 (area logic, not hue)", source="data/schwarzman_scholars_dataset.csv")
ax.set_xlabel("Scholars"); ax.set_ylabel("")
save("top_countries.png")
plt.close("all")

# ── 5. Videos per cohort — monochrome ink, red only if highlighting a gap ──
fig, ax = plt.subplots(figsize=ss.FIGSIZE_WIDE)
videos_per_cohort = df[df["has_intro_video"] == 1]["cohort_year"].value_counts().sort_index()
all_cohorts = sorted(df["cohort_year"].unique())
videos_per_cohort = videos_per_cohort.reindex(all_cohorts, fill_value=0)
ax.bar(videos_per_cohort.index, videos_per_cohort.values, color=ss.INK, edgecolor=ss.CANVAS, linewidth=0.9, zorder=3)
for i, v in enumerate(videos_per_cohort.values):
    if v > 0:
        ax.text(i, v + 0.25, str(int(v)), ha="center", fontsize=8, weight="bold", color=ss.INK)
ss.style_axes(ax, title="Public Intro Videos per Cohort (n=74)", subtitle="4.9% coverage — bare where data is sparse, not rainbowed", source="data/schwarzman_scholars_dataset.csv")
ax.set_ylabel("Videos"); ax.set_xlabel("Cohort Year")
save("videos_per_cohort.png")
plt.close("all")

# ── 6. Stacked country share — muted slate stack (replaces tab20) ──
try:
    fig, ax = plt.subplots(figsize=(12, 6))
    top5 = df["country"].value_counts().head(5).index.tolist()
    df["country_bucket"] = df["country"].apply(lambda c: c if c in top5 else "Other")
    ct = pd.crosstab(df["cohort_year"], df["country_bucket"], normalize="index") * 100
    ct = ct.reindex(sorted(ct.index))
    # ensemble muted stack — no tab20
    # order columns so US first (ink), then China red highlight, then others muted
    desired_order = [c for c in ["United States of America", "China", "United Kingdom", "Canada", "India", "Other"] if c in ct.columns]
    remaining = [c for c in ct.columns if c not in desired_order]
    ct = ct[desired_order + remaining]
    cmap_colors = [ss.INK if "United States" in c else ss.SCHWARZMAN_RED if c == "China" else ss.PALETTE_MONO_SEQ[i % len(ss.PALETTE_MONO_SEQ)] for i, c in enumerate(ct.columns)]
    # assign muted tints for non-highlight
    ct.plot(kind="bar", stacked=True, figsize=(12, 6), ax=ax, edgecolor=ss.CANVAS, linewidth=0.5, width=0.72, color=cmap_colors)
    ss.style_axes(ax, title="Country Composition by Cohort (%, top 5 + Other)", subtitle="US ink · China crimson highlight · Other muted — hue only for the bridge finding", grid_axis="y")
    ax.set_ylabel("Share (%)"); ax.set_xlabel("Cohort Year")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True, facecolor=ss.CANVAS, edgecolor=ss.BORDER, fontsize=8)
    save("country_share_by_cohort.png")
    plt.close("all")
except Exception as e:
    print(f"skip stacked {e}")

# ── 7. Warmth / Charisma — ensemble: slate→crimson cmap, crimson mean, muted hist ──
try:
    import re, json
    META = ROOT / "data" / "meta"
    meta_files = list(META.glob("*.json")) if META.exists() else []
    records = []
    if meta_files:
        for f in meta_files:
            try:
                j = json.loads(f.read_text(encoding="utf-8"))
                emo = j.get("emotion", {})
                if "score" not in emo:
                    continue
                records.append({"warmth": float(emo.get("score", 0)), "sentiment": float(j.get("sentiment", 0)), "cohort": str(j.get("cohort", "")), "happy": float(emo.get("happy", 0)), "neutral": float(emo.get("neutral", 0))})
            except:
                continue
    if not records:
        md_path = ROOT / "ADMITTED_SCHOLAR_PROFILES.md"
        if md_path.exists():
            md = md_path.read_text(encoding="utf-8")
            for m in re.finditer(r"Warmth v2.*?([\d.]+)/100.*?Happy\s*([\d.]+)%.*?Neutral\s*([\d.]+)%", md):
                warmth = float(m.group(1))
                block = md[m.start():m.start() + 900]
                ms = re.search(r"Sentiment.*?([\-\d.]+)\s*\(TextBlob", block)
                sent = float(ms.group(1)) if ms else 0.0
                mc = re.search(r"Cohort\s*(\d{4})", block)
                cohort = mc.group(1) if mc else ""
                records.append({"warmth": warmth, "sentiment": sent, "cohort": cohort, "happy": float(m.group(2)), "neutral": float(m.group(3))})
    if records:
        rec_df = pd.DataFrame(records)
        rec_df = rec_df[rec_df["warmth"] > 0]
        n = len(rec_df)
        print(f"Warmth source: {n} records (meta={len(meta_files)})")
        # hist — monochrome ink, crimson/orange means, muted caption
        fig, ax = plt.subplots(figsize=ss.FIGSIZE_WIDE)
        ax.hist(rec_df["warmth"], bins=20, color=ss.INK, edgecolor=ss.CANVAS, alpha=0.88, linewidth=0.7)
        ax.axvline(rec_df["warmth"].mean(), color=ss.SCHWARZMAN_RED, linestyle="--", linewidth=1.2, label=f"mean {rec_df['warmth'].mean():.1f}")
        ax.axvline(rec_df["warmth"].median(), color=ss.FAINT, linestyle=":", linewidth=1.2, label=f"median {rec_df['warmth'].median():.1f}")
        ss.style_axes(ax, title=f"Warmth Distribution (n={n} scored, Warmth v2 calibrated)", subtitle="Ink hist + crimson mean — color only for the statistic, not the bars")
        ax.set_xlabel("Warmth v2 (happy*0.9+neutral*0.25+35, capped 99)"); ax.set_ylabel("Count")
        ax.legend(frameon=True, facecolor=ss.CANVAS, edgecolor=ss.BORDER)
        ax.text(0.02, 0.96, f"v2 mean {rec_df['warmth'].mean():.1f} median {rec_df['warmth'].median():.1f} sd {rec_df['warmth'].std():.1f}\n4.9% coverage, sharers only", transform=ax.transAxes, va="top", ha="left", fontsize=8, color=ss.MUTED, bbox=dict(facecolor=ss.CANVAS, edgecolor=ss.BORDER, boxstyle="round,pad=0.4"))
        save("warmth_distribution.png")
        plt.close("all")
        # save root copy too
        fig, ax = plt.subplots(figsize=ss.FIGSIZE_WIDE)
        ax.hist(rec_df["warmth"], bins=20, color=ss.INK, edgecolor=ss.CANVAS, alpha=0.88, linewidth=0.7)
        ax.axvline(rec_df["warmth"].mean(), color=ss.SCHWARZMAN_RED, linestyle="--", linewidth=1.2, label=f"mean {rec_df['warmth'].mean():.1f}")
        ax.axvline(rec_df["warmth"].median(), color=ss.FAINT, linestyle=":", linewidth=1.2, label=f"median {rec_df['warmth'].median():.1f}")
        ss.style_axes(ax, title=f"Warmth Distribution (n={n}, v2)")
        ax.set_xlabel("Warmth v2"); ax.set_ylabel("Count"); ax.legend()
        plt.tight_layout(); plt.savefig(ROOT / "warmth_distribution.png", dpi=ss.SAVEDPI, bbox_inches="tight", facecolor=ss.CANVAS); plt.close("all")
        # scatter — slate→crimson cmap (replaces Blues), crimson/ink guides
        fig, ax = plt.subplots(figsize=(11, 5.5))
        sc = ax.scatter(rec_df["warmth"], rec_df["sentiment"], c=rec_df["warmth"], cmap=ss.CMAP_WARMTH, s=68, edgecolor=ss.CANVAS, linewidth=0.6, alpha=0.88)
        plt.colorbar(sc, ax=ax, label="Warmth v2")
        ax.axhline(0.10, color=ss.MUTED, linestyle="--", linewidth=0.9, label="sentiment >0.10")
        ax.axvline(70, color=ss.SCHWARZMAN_RED, linestyle="--", linewidth=0.9, label="warmth 70")
        ss.style_axes(ax, title=f"Warmth v2 vs. Vocal Sentiment (n={n}, Whisper tiny - TextBlob)", subtitle="Slate to crimson encodes warmth - warmer = darker/redder (Ref 1 area logic)", grid_axis="both")
        ax.set_xlabel("Warmth v2 (0-99)"); ax.set_ylabel("Sentiment polarity (-1…1)"); ax.legend(); ax.grid(True, alpha=0.18, color=ss.BORDER, linestyle="--", linewidth=0.6)
        plt.tight_layout(); plt.savefig(OUT / "warmth_vs_sentiment.png", dpi=ss.SAVEDPI, bbox_inches="tight", facecolor=ss.CANVAS); plt.close("all")
        print("saved warmth_vs_sentiment.png")
        fig, ax = plt.subplots(figsize=(11, 5.5))
        sc = ax.scatter(rec_df["warmth"], rec_df["sentiment"], c=rec_df["warmth"], cmap=ss.CMAP_WARMTH, s=68, edgecolor=ss.CANVAS, linewidth=0.6, alpha=0.88); plt.colorbar(sc, ax=ax, label="Warmth v2"); ax.axhline(0.10, color=ss.MUTED, linestyle="--", linewidth=0.9); ax.axvline(70, color=ss.SCHWARZMAN_RED, linestyle="--", linewidth=0.9); ss.style_axes(ax, title=f"Warmth v2 vs Sentiment (n={n})", grid_axis="both"); ax.set_xlabel("Warmth v2"); ax.set_ylabel("Sentiment"); plt.tight_layout(); plt.savefig(ROOT / "warmth_vs_sentiment.png", dpi=ss.SAVEDPI, bbox_inches="tight", facecolor=ss.CANVAS); plt.close("all")
        # by cohort — muted boxes, ink strip
        if rec_df["cohort"].notna().any() and any(c.strip() for c in rec_df["cohort"]):
            fig, ax = plt.subplots(figsize=(12, 5.5))
            order = sorted([c for c in rec_df["cohort"].unique() if c.strip()])
            # use ensemble boxplot if seaborn available but override palette to muted mono
            try:
                sns.boxplot(data=rec_df, x="cohort", y="warmth", order=order, palette=[ss.PANEL]*len(order), linewidth=0.9, fliersize=2, width=0.55)
                # recolor boxes to ensemble faint
                for patch in ax.artists:
                    patch.set_facecolor(ss.PANEL)
                    patch.set_edgecolor(ss.BORDER)
                sns.stripplot(data=rec_df, x="cohort", y="warmth", order=order, color=ss.INK, size=5, alpha=0.72, jitter=True, edgecolor=ss.CANVAS, linewidth=0.4)
            except:
                # fallback bare matplotlib
                groups = [rec_df[rec_df["cohort"] == c]["warmth"].values for c in order]
                bp = ax.boxplot(groups, labels=order, patch_artist=True, boxprops=dict(facecolor=ss.PANEL, edgecolor=ss.BORDER), medianprops=dict(color=ss.SCHWARZMAN_RED))
            ss.style_axes(ax, title=f"Charisma/Warmth v2 by Cohort (n={n} scored, 7-frame v2)", subtitle="Box = distribution, dots = scholars — ink dots, muted boxes", grid_axis="y")
            ax.set_xlabel("Cohort Year"); ax.set_ylabel("Warmth v2 (0-99)"); ax.set_ylim(0, 100)
            for t in ax.get_xticklabels():
                t.set_rotation(20)
            save("charisma_by_cohort.png")
            plt.close("all")
            # root copy
            fig, ax = plt.subplots(figsize=(12, 5.5))
            try:
                sns.boxplot(data=rec_df, x="cohort", y="warmth", order=order, palette=[ss.PANEL]*len(order), linewidth=0.9, fliersize=2, width=0.55)
                sns.stripplot(data=rec_df, x="cohort", y="warmth", order=order, color=ss.INK, size=5, alpha=0.72, jitter=True)
                ax.set_xlabel("Cohort"); ax.set_ylabel("Warmth v2"); ax.set_ylim(0, 100)
            except:
                pass
            ax.set_title(f"Charisma/Warmth v2 by Cohort (n={n})", fontsize=12, color=ss.INK, fontweight="bold", fontfamily=ss.SANS[0], loc="left", pad=12)
            plt.tight_layout(); plt.savefig(ROOT / "charisma_by_cohort.png", dpi=ss.SAVEDPI, bbox_inches="tight", facecolor=ss.CANVAS); plt.close("all")
        print(f"Warmth plots done (n={n})")
    else:
        print("No warmth records — skip warmth plots")
except Exception as e:
    import traceback; print(f"Warmth plots skipped: {e}"); traceback.print_exc()

# ── Bonus: regenerate token sheet (visible proof the ensemble is wired) ──
try:
    ss.preview_tokens(save_path=str(OUT / "style_tokens.png"))
    print("saved style_tokens.png (ensemble cheat-sheet)")
except Exception as e:
    print(f"token sheet skip: {e}")

print(f"Done ensemble. Wrote {len(list(OUT.glob('*.png')))} plots → {OUT}")
