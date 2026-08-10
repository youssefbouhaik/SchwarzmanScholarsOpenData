"""
Regenerate bios_cluster_* PNGs with ensemble style (schwarzman_style)
Replaces rainbow tab10/set2 with muted slate + crimson highlight
"""
import pathlib, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import schwarzman_style as ss
ss.apply_style()

ROOT = pathlib.Path(__file__).parent.parent
DATA_BIOS = ROOT / "data" / "bios_clusters.csv"
DATA_WITH = ROOT / "data" / "bios_clusters_with_region.csv"
DATA_FULL = ROOT / "data" / "schwarzman_scholars_dataset.csv"
OUT = ROOT / "analytics_dashboard"
OUT.mkdir(parents=True, exist_ok=True)

clusters = pd.read_csv(DATA_BIOS, encoding="utf-8")
with_region = pd.read_csv(DATA_WITH, encoding="utf-8")
df = pd.read_csv(DATA_FULL, encoding="utf-8")

# names mapping as in notebook (must match PCA cell)
names = {0:"Health Systems (n27)", 1:"Climate & China Bridge (n70)", 2:"Policy/International (n84)", 3:"Tech-Business Builders (n104)"}
# ensemble order for clusters: 0 ink, 1 slate, 2 muted, 3 crimson (largest gets highlight)
cluster_colors = [ss.PALETTE_CAT4[i] for i in [0,1,2,3]]
# region palette mapping — muted slates + CN crimson
region_order = ["US","CN","Other","Europe/LatAm","Asia-Pacific","Africa/MiddleEast","UK","CA"]
region_colors = {
    "US": ss.INK,
    "CN": ss.SCHWARZMAN_RED,
    "Other": ss.PALETTE_MONO_SEQ[5],
    "Europe/LatAm": ss.PALETTE_MONO_SEQ[3],
    "Asia-Pacific": ss.PALETTE_MONO_SEQ[4],
    "Africa/MiddleEast": "#7C8A9B",
    "UK": ss.PALETTE_MONO_SEQ[2],
    "CA": ss.PALETTE_MONO_SEQ[6],
}

# 1. bios_cluster_sizes.png — monochrome + one crimson highlight (largest)
counts = clusters["cluster"].value_counts().sort_index()
labels = [names[i] for i in counts.index]
# darkest = smallest? Keep visual hierarchy: largest darkest? Use ink for 0..crimson for 3? Already set
colors = [cluster_colors[i] for i in counts.index]
fig, ax = plt.subplots(figsize=(8,4.2))
ax.bar(range(len(counts)), counts.values, color=colors, edgecolor=ss.CANVAS, linewidth=0.9, zorder=3)
ax.set_xticks(range(len(counts)))
ax.set_xticklabels([f"c{i}" for i in counts.index], fontsize=7)
for i, (lab, v, c) in enumerate(zip(labels, counts.values, colors)):
    ax.text(i, v+1.2, f"{v}\n{int(v/285*100)}%", ha="center", fontsize=7, weight="bold", color=c)
    ax.text(i, -4.5, lab.replace(" (", "\n("), ha="center", fontsize=6, color=ss.MUTED, va="top")
ss.style_axes(ax, title="Cluster sizes — 285 bios", subtitle="4 archetypes · Tech-Business 36% largest (crimson) · Health 9% smallest (ink)", source="data/bios_clusters.csv (TF-IDF400 + KMeans k=4)")
ax.set_ylabel("Bios"); ax.set_xlabel("Cluster")
ax.set_ylim(0, max(counts.values)*1.25)
plt.tight_layout()
plt.savefig(OUT/"bios_cluster_sizes.png", dpi=ss.SAVEDPI, bbox_inches="tight", facecolor=ss.CANVAS)
plt.close()
print("saved bios_cluster_sizes.png")

# 2. bios_clusters_by_region.png — 100% stacked horizontal, muted + CN red
# compute share per cluster
ct = with_region.groupby(["cluster","region"]).size().unstack(fill_value=0)
ct = ct.div(ct.sum(axis=1), axis=0)*100
# ensure order US first then CN etc.
for col in region_order:
    if col not in ct.columns:
        ct[col]=0
ct = ct[region_order]
fig, axes = plt.subplots(4, 1, figsize=(9, 6.2), sharex=True)
fig.patch.set_facecolor(ss.CANVAS)
for i, cl in enumerate(sorted(ct.index)):
    ax = axes[i]
    vals = ct.loc[cl]
    left=0
    for reg in region_order:
        v = vals[reg]
        if v<0.5: 
            continue
        ax.barh(0, v, left=left, color=region_colors[reg], edgecolor=ss.CANVAS, linewidth=0.6, height=0.58)
        if v>6:
            ax.text(left+v/2, 0, f"{v:.0f}%", ha="center", va="center", fontsize=6, color="white" if reg in ["US","CN"] else ss.INK, weight="bold")
        left+=v
    ax.set_yticks([0])
    ax.set_yticklabels([names[cl]], fontsize=7, color=ss.INK, weight="bold")
    ax.set_xlim(0,100)
    ax.set_xticks([0,25,50,75,100])
    ss.style_axes(ax, grid_axis="x", despine=True)
    ax.tick_params(axis="y", length=0)
    ax.invert_yaxis()
axes[-1].set_xlabel("Share within cluster (%)")
fig.suptitle("Where each archetype comes from — region mix", fontsize=11, color=ss.INK, fontweight="bold", fontfamily=ss.SANS[0], x=0.08, ha="left")
fig.text(0.08, 0.92, "CN crimson · US ink · Other muted —  Climate n70 is 44% CN, Policy n84 is 64% US", fontsize=7, color=ss.MUTED, ha="left", fontfamily=ss.SANS[0])
# legend outside
handles = [plt.Rectangle((0,0),1,1, color=region_colors[r], ec=ss.CANVAS) for r in region_order]
fig.legend(handles, region_order, loc="upper right", bbox_to_anchor=(0.98,0.98), fontsize=6, frameon=True, facecolor=ss.CANVAS, edgecolor=ss.BORDER, ncol=2, handlelength=1.2)
plt.tight_layout(rect=[0,0,1,0.90])
plt.savefig(OUT/"bios_clusters_by_region.png", dpi=ss.SAVEDPI, bbox_inches="tight", facecolor=ss.CANVAS)
plt.close()
print("saved bios_clusters_by_region.png")

# 3. bios_clusters_by_cohort.png — small multiples? Use grouped bars per cohort share per cluster
# Compute counts per cluster per cohort_year (only bios have cohort)
# Use cohort_year from with_region (has cohort_year)
cohort_ct = with_region.groupby(["cohort_year","cluster"]).size().unstack(fill_value=0)
# sort cohort_year
cohort_ct = cohort_ct.sort_index()
# plot stacked bars? Use 100% share? Keep counts as bars per cluster faceted
# Simpler: grouped bars per cohort: 4 bars per cohort-year
fig, ax = plt.subplots(figsize=(11,5))
years = sorted(with_region["cohort_year"].unique())
# For each cluster, plot bars offset
import numpy as np
width=0.18
x=np.arange(len(years))
for idx, cl in enumerate(sorted(with_region["cluster"].unique())):
    vals = [cohort_ct.loc[y, cl] if y in cohort_ct.index and cl in cohort_ct.columns else 0 for y in years]
    ax.bar(x+idx*width, vals, width=width, color=cluster_colors[cl], edgecolor=ss.CANVAS, linewidth=0.6, label=names[cl])
ax.set_xticks(x+1.5*width)
ax.set_xticklabels(years, fontsize=7, rotation=0)
ss.style_axes(ax, title="Cluster presence by cohort year", subtitle="Counts per cohort — 4 archetypes stable 2026/2027 (Tech 51/53, Policy 43/41, Climate 36/34, Health 14/13)", source="data/bios_clusters_with_region.csv")
ax.set_ylabel("Bios"); ax.set_xlabel("Cohort year")
ax.legend(frameon=True, facecolor=ss.CANVAS, edgecolor=ss.BORDER, fontsize=7, ncol=2, loc="upper left")
plt.tight_layout()
plt.savefig(OUT/"bios_clusters_by_cohort.png", dpi=ss.SAVEDPI, bbox_inches="tight", facecolor=ss.CANVAS)
plt.close()
print("saved bios_clusters_by_cohort.png")

# 4. bios_clusters_by_feeder.png — top feeders per cluster? Use university counts per cluster
# For each cluster, get top 5 universities
# Then plot horizontal bars per cluster small multiples (4 panels)
import collections
fig, axes = plt.subplots(2,2, figsize=(12,7), sharex=False)
fig.patch.set_facecolor(ss.CANVAS)
for idx, cl in enumerate(sorted(clusters["cluster"].unique())):
    ax = axes.flat[idx]
    sub = clusters[clusters["cluster"]==cl]
    top = sub["university"].value_counts().head(6)
    # horizontal bars monochrome ink shade per cluster
    # use cluster color for bars (muted)
    ax.barh(top.index, top.values, color=cluster_colors[cl], edgecolor=ss.CANVAS, linewidth=0.7, alpha=0.9)
    ax.invert_yaxis()
    for i, v in enumerate(top.values):
        ax.text(v+0.3, i, str(v), va="center", fontsize=6, color=ss.SLATE)
    ss.style_axes(ax, title=names[cl], title_color=cluster_colors[cl], grid_axis="x")
    ax.set_xlabel("Bios" if idx>=2 else "")
    ax.tick_params(axis="y", labelsize=6)
    for lbl in ax.get_yticklabels():
        lbl.set_fontsize(6)
fig.suptitle("Top feeder universities per archetype", fontsize=11, color=ss.INK, fontweight="bold", fontfamily=ss.SANS[0], x=0.06, ha="left")
fig.text(0.06, 0.92, "Harvard loads only in Policy (n84) — Tech/Climate are feeder-dispersed (CS27 Fresno, DM27 Montana win there)", fontsize=7, color=ss.MUTED, ha="left")
plt.tight_layout(rect=[0,0,1,0.92])
plt.savefig(OUT/"bios_clusters_by_feeder.png", dpi=ss.SAVEDPI, bbox_inches="tight", facecolor=ss.CANVAS)
plt.close()
print("saved bios_clusters_by_feeder.png")
print("done cluster ensemble")
