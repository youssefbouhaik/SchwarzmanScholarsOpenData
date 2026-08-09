#!/usr/bin/env python3
"""
Bios NLP — word cloud + sentiment + word treemap (like your Mark Twain figure)
Generates:
  analytics_dashboard/bios_wordcloud.png
  analytics_dashboard/bios_sentiment_hist.png
  analytics_dashboard/bios_word_treemap.png  (squarify, raw frequencies — matches your image)
  analytics_dashboard/bios_word_treemap_clean.png (stopwords removed — actually useful)
  data/bios_words.csv  (word, count)
  data/bios_sentiment.csv (id, name, sentiment, bio_len)

Run: python scripts/bios_nlp.py
Requires: pandas, matplotlib, wordcloud, textblob, squarify
"""
import pathlib, re, csv, collections
import pandas as pd
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).parent.parent
CSV = ROOT / "data" / "schwarzman_scholars_dataset.csv"
OUT = ROOT / "analytics_dashboard"
DATA_OUT = ROOT / "data"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CSV, encoding="utf-8")
bios = df[df["bio"].notna() & (df["bio"].str.strip() != "")].copy()
print(f"Bios with text: {len(bios)}/1497")

# --- 1. Sentiment for bios ---
try:
    from textblob import TextBlob
    has_tb = True
except: has_tb = False

sentiments = []
for _, r in bios.iterrows():
    txt = str(r["bio"])
    if has_tb:
        s = float(TextBlob(txt).sentiment.polarity)  # -1..1
    else:
        # fallback trivial
        s = 0.0
    sentiments.append({"id": r["id"], "name": r["name"], "cohort_year": r["cohort_year"], "country": r["country"], "sentiment": s, "bio_len": len(txt), "bio_words": len(txt.split())})

sent_df = pd.DataFrame(sentiments)
sent_df.to_csv(DATA_OUT / "bios_sentiment.csv", index=False)
print(f"Sentiment mean={sent_df['sentiment'].mean():.3f} median={sent_df['sentiment'].median():.3f} min={sent_df['sentiment'].min():.3f} max={sent_df['sentiment'].max():.3f}")
print(sent_df["sentiment"].describe().to_string())

# plot sentiment hist
plt.figure(figsize=(10,5))
plt.hist(sent_df["sentiment"], bins=30, edgecolor="white")
plt.axvline(sent_df["sentiment"].mean(), color="red", linestyle="--", label=f"mean {sent_df['sentiment'].mean():.2f}")
plt.title("Bio Sentiment Distribution (TextBlob polarity, -1 negative → 1 positive, n=285)")
plt.xlabel("Polarity")
plt.ylabel("Bios")
plt.legend()
plt.tight_layout()
plt.savefig(OUT / "bios_sentiment_hist.png", dpi=200)
plt.close()
print("✓ bios_sentiment_hist.png")

# --- 2. Word frequencies ---
# Keep raw + clean versions to explain your treemap question
all_text = " ".join(bios["bio"].astype(str)).lower()
# simple tokenize: keep letters only
tokens_raw = re.findall(r"[a-z']+", all_text)
# raw counts (includes stopwords) — this reproduces your Mark Twain figure where the/at/of dominate
counter_raw = collections.Counter(tokens_raw)
print(f"Raw tokens: {len(tokens_raw)}, unique: {len(counter_raw)}")
print("Top raw:", counter_raw.most_common(12))

# ACTIVE WORDS only — no connector words (articles, prepositions, conjunctions, auxiliaries)
# Base stopwords: articles, prepositions, conjunctions, pronouns, auxiliaries, plus your Java list
STOP = set("""
a an the and or but if while of at by for with about into through during before after above below
to from up down in out on off over under again further then once here there when where why how
all any both each few more most other some such no nor not only own same so than too very s t can will
just don should now is are was were be been being has have had do does did having i me my myself we our
ours ourselves you your yours yourself yourselves he him his himself she her hers herself it its itself they
them their theirs themselves what which who whom this that that'll these those am isn aren't wasn weren't
hasn haven hadn't ain aren haven won wouldn don didn should could would also including includes included
including across per via within between among throughout
""".split())

# NLTK stopwords
try:
    import nltk
    try: nltk.data.find("corpora/stopwords")
    except: nltk.download("stopwords", quiet=True)
    from nltk.corpus import stopwords
    STOP |= set(stopwords.words("english"))
except: pass

# Also drop single letters, possessive s, and very short tokens
tokens_nostop = [t for t in tokens_raw if t not in STOP and len(t) > 2 and t not in ("000","’","'","s","t","u")]

# POS-filter to ACTIVE words only (nouns/verbs/adjectives/adverbs) — matches your Java active-word logic
try:
    import nltk
    try: nltk.data.find("taggers/averaged_perceptron_tagger")
    except: nltk.download("averaged_perceptron_tagger", quiet=True)
    try: nltk.data.find("taggers/averaged_perceptron_tagger_eng")
    except: nltk.download("averaged_perceptron_tagger_eng", quiet=True)
    # tag unique words for speed
    uniq = list(set(tokens_nostop))
    pos = dict(nltk.pos_tag(uniq))
    # keep NN*, VB*, JJ*, RB*  (nouns, verbs, adjectives, adverbs) — drop DT, IN, CC, PRP, MD, WDT etc.
    ACTIVE_TAGS = ("NN","VB","JJ","RB")
    tokens_clean = [t for t in tokens_nostop if pos.get(t,"")[0:2] in ACTIVE_TAGS]
    # fallback if POS filtered too aggressively ( <30 words): use nostop
    if len(set(tokens_clean)) < 30:
        tokens_clean = tokens_nostop
except Exception as e:
    print(f"POS filter failed ({e}), using stopword-only clean")
    tokens_clean = tokens_nostop
counter_clean = collections.Counter(tokens_clean)
print("Top clean:", counter_clean.most_common(15))
# save
with open(DATA_OUT / "bios_words.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["word","count_raw","count_clean"])
    all_words=set(list(counter_raw.keys())[:0]) | set(counter_clean.keys())
    # actually write top 300 clean
    for word,c in counter_clean.most_common(300):
        w.writerow([word,c,counter_raw.get(word,0)])
print("✓ bios_words.csv (top 300 clean)")

# --- 3. Word cloud (clean) ---
try:
    from wordcloud import WordCloud
    wc = WordCloud(width=1600, height=800, background_color="white", colormap="viridis", max_words=200, collocations=False)
    wc.generate_from_frequencies(counter_clean)
    plt.figure(figsize=(16,8))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title("Bios Word Cloud — 285 Schwarzman bios (stopwords removed, top 200)", fontsize=14, pad=12)
    plt.tight_layout(pad=0)
    plt.savefig(OUT / "bios_wordcloud.png", dpi=200)
    plt.close()
    print("✓ bios_wordcloud.png")
except Exception as e:
    print(f"wordcloud failed: {e} — pip install wordcloud")

# --- 4. Treemap — raw (matches your image) + clean (useful) ---
try:
    import squarify
    # Raw treemap — 80 top raw words, grey like your Mark Twain figure
    top_raw = counter_raw.most_common(120)
    labels_raw = [w for w,c in top_raw]
    sizes_raw = [c for w,c in top_raw]
    # Normalize for squarify
    sizes_raw = [s for s in sizes_raw]  # already counts
    plt.figure(figsize=(16,10))
    # use light grey palette to match your screenshot
    cmap = plt.cm.Greys
    colors = [cmap(0.25 + 0.6*(i/len(sizes_raw))) for i in range(len(sizes_raw))]
    # squarify wants normalized sizes
    normed = squarify.normalize_sizes(sizes_raw, 100, 60)
    rects = squarify.squarify(normed, 0, 0, 100, 60)
    ax = plt.gca()
    for rect, label, size in zip(rects, labels_raw, sizes_raw):
        x,y,dx,dy = rect["x"], rect["y"], rect["dx"], rect["dy"]
        ax.add_patch(plt.Rectangle((x,y), dx, dy, facecolor=colors[labels_raw.index(label)%len(colors)], edgecolor="white", linewidth=0.7, alpha=0.9))
        # only label if rectangle big enough
        if dx > 4 and dy > 3:
            # font size scales with area
            fs = max(6, min(14, (dx*dy)**0.4))
            ax.text(x+dx/2, y+dy/2, label, ha="center", va="center", fontsize=fs, color="black", weight="normal")
    ax.set_xlim(0,100); ax.set_ylim(0,60); ax.axis("off")
    plt.title("Bios Word Treemap — RAW (stopwords kept, like your Mark Twain figure, n=285 bios)", fontsize=13)
    plt.tight_layout()
    plt.savefig(OUT / "bios_word_treemap.png", dpi=200)
    plt.close()
    print("✓ bios_word_treemap.png (raw — matches your image: the/of/and dominate)")

    # Clean treemap — stopwords removed, actually informative
    top_clean = counter_clean.most_common(80)
    labels = [w for w,c in top_clean]
    sizes = [c for w,c in top_clean]
    plt.figure(figsize=(16,10))
    cmap2 = plt.cm.viridis
    colors2 = [cmap2(i/len(sizes)) for i in range(len(sizes))]
    normed2 = squarify.normalize_sizes(sizes, 100, 60)
    rects2 = squarify.squarify(normed2, 0, 0, 100, 60)
    ax2 = plt.gca()
    for rect, label, size in zip(rects2, labels, sizes):
        x,y,dx,dy = rect["x"], rect["y"], rect["dx"], rect["dy"]
        ax2.add_patch(plt.Rectangle((x,y), dx, dy, facecolor=colors2[labels.index(label)%len(colors2)], edgecolor="white", linewidth=0.8))
        if dx > 5 and dy > 4:
            fs = max(7, min(13, (dx*dy)**0.42))
            ax2.text(x+dx/2, y+dy/2, f"{label}\n{size}", ha="center", va="center", fontsize=fs, color="white", weight="bold")
    ax2.set_xlim(0,100); ax2.set_ylim(0,60); ax2.axis("off")
    plt.title("Bios Word Treemap — CLEAN (stopwords removed, n=285 bios, size = frequency)", fontsize=13)
    plt.tight_layout()
    plt.savefig(OUT / "bios_word_treemap_clean.png", dpi=200)
    plt.close()
    print("✓ bios_word_treemap_clean.png")

except Exception as e:
    print(f"treemap failed: {e} — pip install squarify")
    import traceback; traceback.print_exc()
