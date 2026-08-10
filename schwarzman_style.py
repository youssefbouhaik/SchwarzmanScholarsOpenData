"""
Schwarzman Ensemble — single source of truth for the whole repo
===============================================================
Unites the two visual references:

  Ref 1  treemap  (bios_word_treemap_clean / schwarzman_hybrid_4K)
         → Grammar of Graphics: geometry=rect, aesthetic=area∝frequency,
           theme=minimal ink, monochrome, thin gray strokes, black sans labels.
         → Anti-pattern avoided: color as decoration / overplotting.
           Treemap *is* the small-multiples alternative to a wordcloud.

  Ref 2  L-system  (l-system-schwarzman.png)
         → Visual Hierarchy: vast white negative space, delicate black ink
           tree (high data-ink), single accent (Schwarzman crimson + tiny
           cyan dot), editorial serif display type.
         → Principle: minimal theme, color used strategically to highlight,
           not to fill.

Ensemble rule: every figure in the notebook *and* in generate_plots.py
inherits the same tokens below. Run `apply_style()` once at the top of
any notebook/script and all subsequent plots are aligned.

Usage — notebook preamble:
    import schwarzman_style as ss
    ss.apply_style()
    # optional: display tokens
    ss.preview_tokens()

    fig, ax = plt.subplots(figsize=ss.FIGSIZE_WIDE)
    ... plot ...
    ss.style_axes(ax, title="Scholars per Cohort", subtitle="n=1497 · 2017–2027")
    ss.save(fig, "my_plot.png")

Usage — generate_plots.py:
    import schwarzman_style as ss
    ss.apply_style()   # replaces the old plt.rcParams block
    colours = ss.PALETTE_MONO_SEQ  # instead of sns palette blues/viridis

Tokens are intentionally muted. If a plot needs 4 categories (the 4
archetypes), use PALETTE_CAT4 — three slates + one crimson highlight.
Never use viridis / Blues_d / crest in this repo; they break the
editorial monochrome.
"""

from __future__ import annotations
import matplotlib as mpl
import matplotlib.pyplot as plt

# ── Canvas & ink ──────────────────────────────────────────────────
CANVAS = "#FFFFFF"        # figure face — pure white (both refs)
PANEL  = "#F8FAFC"         # optional axes face for bars/lines (very light slate)
BORDER = "#E2E8F0"         # spines + grid + treemap strokes (Ref1 thin gray, Ref2 outer border)
BORDER_STRONG = "#CBD5E1"  # treemap rect edge when you need slightly darker
INK    = "#0F172A"         # primary text / bar fill / tree ink (near-black, softer than #000)
SLATE  = "#334155"         # secondary text
MUTED  = "#64748B"         # tertiary / axis tick
FAINT  = "#94A3B8"         # grid, subtle dividers
SCHWARZMAN_RED = "#A51C30" # display titles, mean lines, highlight dot — Tsinghua/Schwarzman crimson
SCHWARZMAN_RED_SOFT = "#B91C2E"
ACCENT_CYAN = "#0EA5E9"    # tiny L-system baseline dot only — avoid elsewhere
ACCENT_AMBER = "#C17A3A"   # warm secondary accent if absolutely needed (rare)

# ── Typography ────────────────────────────────────────────────────
# Display titles (h1) → serif + crimson, as in Ref 2 "Schwarzman Scholars Open Data"
# Body / axis / legend → sans, as in Ref 1 treemap labels
SERIF = ["Garamond", "Georgia", "Times New Roman", "DejaVu Serif"]
SANS  = ["Helvetica Neue", "Inter", "DejaVu Sans", "Arial", "Helvetica"]

TITLE_SIZE = 12
SUBTITLE_SIZE = 9
LABEL_SIZE = 9
TICK_SIZE = 8
LEGEND_SIZE = 8

# ── Figure geometry ───────────────────────────────────────────────
FIGSIZE_WIDE = (11, 5)     # bars, lines, hist — spans the page, Ref2 generous whitespace
FIGSIZE_TALL = (11, 6.2)   # horizontal bars with many labels
FIGSIZE_SQUARE = (7, 5)    # donut, compact treemap cell
DPI = 300
SAVEDPI = 300

# ── Palettes ──────────────────────────────────────────────────────
# Monochrome slate ramp — the *only* sequential palette in the ensemble.
# Simulates treemap's "area, not color" encoding for bars/lines.
PALETTE_MONO_SEQ = ["#0F172A", "#1E293B", "#334155", "#475569", "#64748B", "#94A3B8", "#CBD5E1"]
# For discrete bars ordered by size: darkest → lightest (visual hierarchy, biggest darkest)
PALETTE_MONO_BAR = ["#0F172A", "#243447", "#334155", "#475569", "#64748B", "#94A3B8"]

# Categorical for the 4 archetypes: 3 slates + 1 crimson highlight
# Keeps Ref1 monochrome logic, Ref2 crimson hierarchy: the "highlight" door is red.
PALETTE_CAT4 = ["#0F172A", "#334155", "#64748B", "#A51C30"]
# Named for code readability
PALETTE_CAT4_DICT = {
    0: "#0F172A",   # Health-ish → ink
    1: "#334155",   # Climate & Bridge → slate
    2: "#64748B",   # Policy/Intl → muted
    3: "#A51C30",   # Tech-Business → crimson highlight (or any highlighted cluster)
}
# Alternate: muted-only (when you don't want red competing)
PALETTE_CAT4_MUTED = ["#0F172A", "#334155", "#475569", "#94A3B8"]

# Geographic / region palette (US/CN/Other) — still monochrome + red for CN bridge
PALETTE_REGION = {"US": "#0F172A", "CN": "#A51C30", "Other": "#94A3B8", "UK": "#334155", "CA": "#64748B"}

# Warmth / sentiment continuous — single-hue slate→red, not viridis/Blues
# Use for scatter: c = warmth, cmap = slate→crimson
CMAP_WARMTH = mpl.colors.LinearSegmentedColormap.from_list(
    "schwarzman_warmth", ["#F1F5F9", "#94A3B8", "#334155", "#A51C30"], N=256
)
# For matplotlib scatter fallback when cmap not needed: just use INK

# ── rcParams ensemble ─────────────────────────────────────────────
ENSEMBLE_RCPARAMS = {
    # canvas
    "figure.facecolor": CANVAS,
    "figure.edgecolor": CANVAS,
    "axes.facecolor": CANVAS,          # default pure white (treemap purity); bars may set PANEL per-ax
    "savefig.facecolor": CANVAS,
    "savefig.edgecolor": CANVAS,
    # ink & spines
    "axes.edgecolor": BORDER,
    "axes.linewidth": 0.9,
    "axes.grid": True,
    "grid.color": BORDER,
    "grid.linestyle": "--",
    "grid.linewidth": 0.6,
    "grid.alpha": 0.35,
    # typography
    "font.family": "sans-serif",
    "font.sans-serif": SANS,
    "font.serif": SERIF,
    "axes.titlesize": TITLE_SIZE,
    "axes.titleweight": "bold",
    "axes.titlecolor": INK,
    "axes.labelsize": LABEL_SIZE,
    "axes.labelcolor": SLATE,
    "axes.labelweight": "normal",
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelsize": TICK_SIZE,
    "ytick.labelsize": TICK_SIZE,
    "legend.fontsize": LEGEND_SIZE,
    "legend.facecolor": CANVAS,
    "legend.edgecolor": BORDER,
    "legend.framealpha": 0.95,
    # thin, elegant lines (L-system delicacy)
    "lines.linewidth": 1.4,
    "patch.linewidth": 0.7,
    "patch.edgecolor": CANVAS,  # bars get white edge → cut between bars
}

# Seaborn theme that mirrors the same tokens (if seaborn installed)
SEABORN_STYLE = {
    "style": "white",
    "rc": {
        "figure.facecolor": CANVAS,
        "axes.facecolor": CANVAS,
        "axes.edgecolor": BORDER,
        "grid.color": BORDER,
        "grid.linestyle": "--",
        "axes.grid": True,
        "text.color": INK,
        "axes.labelcolor": SLATE,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
    },
}


def apply_style(mode: str = "ensemble") -> None:
    """
    Call once at the top of a notebook or script.
    Sets mpl.rcParams + optionally seaborn theme so every later figure
    inherits the Ref1×Ref2 ensemble without per-plot boilerplate.
    """
    mpl.rcParams.update(ENSEMBLE_RCPARAMS)
    # try seaborn harmonisation — non-fatal if missing
    try:
        import seaborn as sns  # type: ignore
        if hasattr(sns, "set_theme"):
            sns.set_theme(style=SEABORN_STYLE["style"], rc=SEABORN_STYLE["rc"])
        else:
            sns.set_style("white", rc=SEABORN_STYLE["rc"])
    except Exception:
        pass
    # Make sure tight_layout doesn't clip the editorial subtitle
    mpl.rcParams["figure.autolayout"] = False


def style_axes(
    ax,
    *,
    title: str | None = None,
    subtitle: str | None = None,
    source: str | None = None,
    despine: bool = True,
    grid_axis: str = "y",
    title_color: str = INK,
    title_serif: bool = False,
    panel: bool = False,
):
    """
    Grammar-of-Graphics Themes step + Visual Hierarchy.
    Apply after plotting.

    - Minimal spines (despine top/right), y-grid only
    - Optional panel tint (#F8FAFC) for bar/line axes (not treemap)
    - Title block mimics Ref 2: serif crimson option, subtitle muted sans
    - Source footnote at bottom-right (6pt, FAINT)
    """
    if panel:
        ax.set_facecolor(PANEL)
    # spines
    if despine:
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        for spine in ["left", "bottom"]:
            ax.spines[spine].set_color(BORDER)
            ax.spines[spine].set_linewidth(0.9)
    # grid: y only for bars, both off for scatters (caller can override)
    ax.grid(True, axis=grid_axis if grid_axis else "both", color=BORDER, linestyle="--", linewidth=0.6, alpha=0.35)
    if grid_axis == "y":
        ax.grid(False, axis="x")
    elif grid_axis == "both":
        pass
    else:
        ax.grid(False)

    # title block: editorial hierarchy — title bold, subtitle muted, both left-aligned
    if title:
        # Optionally render display titles in serif + crimson (Ref 2). Default stays INK sans for data plots.
        fam = SERIF if title_serif else SANS
        ax.set_title(
            title,
            loc="left",
            pad=14,
            fontsize=TITLE_SIZE,
            fontweight="bold",
            color=title_color,
            fontfamily=fam[0],
        )
    if subtitle:
        # Render subtitle as a text box just above axes (like Ref 2 "Tsinghua · Schwarzman")
        # Use figure-level if axes title already used — here we add an axes text.
        ax.text(
            0, 1.02, subtitle,
            transform=ax.transAxes,
            ha="left", va="bottom",
            fontsize=SUBTITLE_SIZE - 1,
            color=MUTED,
            fontfamily=SANS[0],
        )
        # nudge title down slightly when subtitle present is handled by pad above
    if source:
        ax.text(
            1.0, -0.16, source,
            transform=ax.transAxes,
            ha="right", va="top",
            fontsize=6,
            color=FAINT,
            fontfamily=SANS[0],
            style="italic",
        )
    return ax


def add_display_title(fig, title: str, subtitle: str | None = None, x: float = 0.06, y: float = 0.90) -> None:
    """
    Ref 2 editorial title for standalone figures (outside axes), e.g. cover / hybrid treemap.
    Places a large serif crimson title + thin rule + muted sans subtitle.
    """
    fig.text(x, y, title, fontsize=18, color=SCHWARZMAN_RED, fontfamily=SERIF[0], va="bottom", ha="left", weight="bold")
    # thin rule — like the short crimson line under the title in Ref 2
    line_y = y - 0.018
    fig.add_artist(plt.Line2D([x, x + 0.045], [line_y, line_y], transform=fig.transFigure, color=SCHWARZMAN_RED, linewidth=1.4, solid_capstyle="round"))
    fig.add_artist(plt.Line2D([x + 0.050, x + 0.120], [line_y, line_y], transform=fig.transFigure, color=BORDER, linewidth=0.9, alpha=0.9))
    if subtitle:
        fig.text(x, line_y - 0.025, subtitle, fontsize=7, color=MUTED, fontfamily=SANS[0], va="top", ha="left")


def save(fig, path, dpi: int = SAVEDPI, **kw) -> None:
    """White-background save with tight bbox — mirrors Ref 2 generous white border."""
    kw.setdefault("facecolor", CANVAS)
    kw.setdefault("edgecolor", CANVAS)
    kw.setdefault("bbox_inches", "tight")
    fig.tight_layout()
    fig.savefig(path, dpi=dpi, **kw)
    plt.close(fig)


def despine(fig_or_ax=None):
    """Remove top/right spines — thin Ref 1/Ref 2 aesthetic."""
    if fig_or_ax is None:
        ax = plt.gca()
        for s in ["top", "right"]:
            ax.spines[s].set_visible(False)
    elif hasattr(fig_or_ax, "spines"):
        for s in ["top", "right"]:
            fig_or_ax.spines[s].set_visible(False)
    else:
        for ax in fig_or_ax.get_axes():
            for s in ["top", "right"]:
                ax.spines[s].set_visible(False)


def bar(ax, labels, values, orient: str = "v", palette=None, highlight_idx: int | None = None):
    """
    Monochrome bar helper — area/ length encodes value (Ref 1 logic), not hue.
    - orient "v" or "h"
    - palette defaults to slate ramp darkest→lightest
    - highlight_idx paints one bar crimson (Visual Hierarchy: color strategically for the finding)
    """
    if palette is None:
        # use darkest N for N bars, so largest bar can be darkest if caller sorted descending
        n = len(values)
        palette = (PALETTE_MONO_BAR * ((n // len(PALETTE_MONO_BAR)) + 1))[:n]
    import numpy as np
    colours = list(palette)
    if highlight_idx is not None and 0 <= highlight_idx < len(colours):
        colours[highlight_idx] = SCHWARZMAN_RED
    if orient == "h":
        ax.barh(labels, values, color=colours, edgecolor=CANVAS, linewidth=0.9, zorder=3)
        ax.invert_yaxis()
    else:
        ax.bar(labels, values, color=colours, edgecolor=CANVAS, linewidth=0.9, zorder=3)
    return ax


def preview_tokens(save_path=None):
    """Render a tiny token sheet — useful in the notebook to 'learn' the ensemble."""
    fig, axes = plt.subplots(1, 3, figsize=(11, 2.6), gridspec_kw={"width_ratios": [1.2, 1.1, 1]})
    fig.patch.set_facecolor(CANVAS)
    for ax in axes:
        ax.set_axis_off()
        ax.set_facecolor(CANVAS)
    # 1 — palette strip
    ax = axes[0]
    ax.set_title("Monochrome ramp — analysis", fontsize=8, color=INK, loc="left", pad=10, fontweight="bold")
    for i, c in enumerate(PALETTE_MONO_SEQ):
        ax.add_patch(plt.Rectangle((i / len(PALETTE_MONO_SEQ), 0.35), 1 / len(PALETTE_MONO_SEQ) - 0.015, 0.35, color=c, transform=ax.transAxes, clip_on=False))
        ax.text(i / len(PALETTE_MONO_SEQ) + 0.015, 0.28, c, transform=ax.transAxes, fontsize=5, color=MUTED, rotation=30, va="top", ha="left")
    ax.text(0, 0.82, "Bars, lines, heat — darkest = most. Color is not decoration.", transform=ax.transAxes, fontsize=7, color=SLATE, va="top", ha="left", wrap=True)
    ax.text(0, 0.70, "Ref 1 rule: area/length encodes; hue stays muted.", transform=ax.transAxes, fontsize=6, color=MUTED, va="top", ha="left", style="italic")

    # 2 — categorical 4
    ax = axes[1]
    ax.set_title("Categorical — 4 archetypes", fontsize=8, color=INK, loc="left", pad=10, fontweight="bold")
    labs = ["Health", "Climate", "Policy", "Tech"]
    for i, (lab, c) in enumerate(zip(labs, PALETTE_CAT4)):
        ax.add_patch(plt.Rectangle((0.02, 0.62 - i * 0.14), 0.08, 0.07, color=c, transform=ax.transAxes, clip_on=False))
        ax.text(0.14, 0.66 - i * 0.14, f"{lab}  {c}", transform=ax.transAxes, fontsize=7, color=SLATE, va="center", ha="left")
    ax.text(0, 0.18, "3 slates + 1 crimson highlight — use red sparingly, for the finding.", transform=ax.transAxes, fontsize=6, color=MUTED, va="top", ha="left", style="italic")

    # 3 — typography
    ax = axes[2]
    ax.set_title("Typography — Ref 2 editorial", fontsize=8, color=INK, loc="left", pad=10, fontweight="bold")
    ax.text(0.02, 0.72, "Schwarzman Scholars", transform=ax.transAxes, fontsize=13, color=SCHWARZMAN_RED, fontfamily=SERIF[0], weight="bold", va="center", ha="left")
    ax.add_artist(plt.Line2D([0.02, 0.10], [0.62, 0.62], transform=ax.transAxes, color=SCHWARZMAN_RED, linewidth=1.3))
    ax.add_artist(plt.Line2D([0.11, 0.30], [0.62, 0.62], transform=ax.transAxes, color=BORDER, linewidth=0.8))
    ax.text(0.02, 0.55, "Tsinghua University  ·  Schwarzman College", transform=ax.transAxes, fontsize=6, color=MUTED, fontfamily=SANS[0], va="center", ha="left")
    ax.text(0.02, 0.42, "Axis / body - Helvetica Neue, Inter, sans — 8-9pt, #334155", transform=ax.transAxes, fontsize=6, color=SLATE, va="center", ha="left")
    ax.text(0.02, 0.32, "Display - Garamond / Georgia serif — only for page titles", transform=ax.transAxes, fontsize=6, color=MUTED, va="center", ha="left", style="italic")
    ax.text(0.02, 0.18, "Grid — y only, --, #E2E8F0 @ 0.35, spines thin, white edge on bars", transform=ax.transAxes, fontsize=5.5, color=FAINT, va="center", ha="left")

    # outer border like Ref 2 — Figure has no spines, so annotate via Rectangle only
    fig.add_artist(plt.Rectangle((0.01, 0.03), 0.98, 0.94, fill=False, edgecolor=BORDER, linewidth=0.8, transform=fig.transFigure, clip_on=False))
    fig.tight_layout(pad=1.2)
    if save_path:
        fig.savefig(save_path, dpi=220, facecolor=CANVAS, bbox_inches="tight")
        plt.close(fig)
        return save_path
    return fig
