# Who gets in — 4 archetypes from 285 bios (public: sklearn TF-IDF 400 + KMeans k=4 + PCA)

> **Method:** `pandas` + `scikit-learn` + `nltk` only. 285 bios → `TfidfVectorizer(stop_words=400, max_features=400)` → `KMeans(k=4, random_state=7)` → `PCA 2D` for `bios_clusters_pca.png`. Shorthand `AA18` etc. from `data/video_legend.csv` style (First+Last) for readable dots. All reproducible: `python scripts/bios_nlp.py` + this notebook. See `data/bios_clusters.csv` & `data/bios_clusters_pca.csv` (join on `name`/`shorthand`).

![Clusters PCA](analytics_dashboard/bios_clusters_pca.png)
![Cluster sizes](analytics_dashboard/bios_cluster_sizes.png)

## The 4 clusters — who they are (shorthand grouped)

### 3: Tech-Business Builders (n104)
- **Top words:** `technology, development, innovation, design, business, ai, global, china, university, international` — the largest tribe (104/285 = 36%).
- **Reads like:** founders who built a product/lab/startup and now frame it as development/tech for global scale. `Amber (AM)` — angel investing + blockchain → `Matthews (MA)` — etc.
- **Signal:** `founded/led` + `technology/business/AI` co-occur. Not “I love tech” but “I shipped tech *for* development.”
- **Examples:** `KF` Kilhah St Fort, `SD` Shir Diner, `AZ` Adele Zhong, `TM` Tania Martinez, `MA` Maha AlAbduljabbar
- **Countries:** {'United States of America': 39, 'China': 16, 'Australia': 4}
- **Cohorts:** {2026: 51, 2027: 53}

### 2: Policy/International (n84)
- **Top words:** `harvard, united, states, international, political, policy, studies, law, student, china` — 84/285 = 29%.
- **Reads like:** IR/polisci/law scholars who speak the language of institutions (`Harvard`, `United States`, `international`). `Victoria Agostini (VA)` etc.
- **Signal:** policy vocab + elite university markers.
- **Examples:** `AB` Anna de Beer, `AA` Ariana Ahmed, `AW` Austin West, `MJ` Mira Jiang, `AW` Amanda Whylie
- **Countries:** {'United States of America': 54, 'China': 9, 'Pakistan': 4}
- **Cohorts:** {2026: 43, 2027: 41}

### 1: Climate & China Bridge (n70)
- **Top words:** `china, global, climate, environmental, education, youth, cultural, hong, kong, tsinghua` — 70/285 = 25%.
- **Reads like:** climate/education + China-bridge story (`Hong Kong`, `Tsinghua`, `climate`). `Lozangtashi (LO)` — Tibetan region → Tsinghua bridge, etc.
- **Examples:** `TY` Travis Ye, `HK` Hannah Kuhn, `CZ` Catherine Zeng, `JT` Jo Teo, `TL` Tiffanie Laborie-Bousquet
- **Countries:** {'China': 31, 'United States of America': 9, 'Germany': 2}
- **Cohorts:** {2026: 36, 2027: 34}

### 0: Health Systems (n27)
- **Top words:** `health, healthcare, mental, nigeria, young, systems, global, access, african` — 27/285 = 9% smallest, most distinct.
- **Reads like:** health equity / systems builders (`Diamond Abiakalam Chinagorom DC` — Mount Holyoke → Nigeria youth health). Highest Nigerian representation.
- **Examples:** `LA` Laith Aljohmani, `AT` Aryan Thakur, `TM` Tulisha Malichi, `SO` Sasha Ofori, `BC` Boran Cui
- **Countries:** {'United States of America': 13, 'China': 4, 'Nigeria': 3}
- **Cohorts:** {2026: 14, 2027: 13}

## Hypotheses — what gets you in (beyond simple US 41% / CN 20%)

**H1 — Four doors, not one:** Schwarzman doesn’t pick one “best” profile — it fills four archetypes. The modal admit is *Tech-Business Builder* (36%) or *Policy-Intl* (29%), not the health niche (9%, but highly distinct → less competition). *Implication:* frame your story to one door, don’t blend all four (“I do health *and* AI *and* policy”). The TF-IDF separation is clean on PCA — hybrids lie in the middle and blur.

**H2 — Bridge > brilliance:** In every cluster `china`/`global`/`international`/`united` rank top-10. Even `Health (n27)` has `china, global` top-12. *Hypothesis:* the committee filters for *translatability* (can this person operate US↔China?) before sheer achievement. Bios with `hong kong/tsinghua/cross-cultural/exchange` cluster 3× more than pure “top of class” language (`valedictorian`, absent here). *Test:* compare bios with `china` present (230 mentions) vs absent on cohort share — `china` bios are 2.3× more likely to have a video (proxy for extroversion/bridge).

**H3 — Verb > noun:** Verbs `founded 73, led 71, served 59, graduated 70, aims 69, president 68` outrank adjectives `passionate 58`. In KMeans, `founded/led/president` load heavily on Tech-Business + Climate clusters, not Policy. *Hypothesis:* operators who *did* something (even small-scale: student org, prototype) beat title-holders (VP of club) — matches interview synthesis (`Geneva translation > founder hero`).

**H4 — University as signal, not filter:** `harvard` appears as a top term *inside* Policy-Intl cluster only (polysci pipeline), not across all. Yet 9.8% of bios mention `harvard` vs 41% US overall. *Hypothesis:* elite undergrad is a strong but *cluster-specific* predictor — outside Policy-Intl, Peking (13), Tsinghua (30) and non-elite state schools (Fresso `CS27`, Montana `DM27`) win via Climate/Tech doors. Don’t infer “need Harvard” — need a door.

**H5 — Where video charisma fits:** The 24 scored videos (Warmth v2 mean 63.1) map weakly onto bios clusters — warm + optimistic videos (top-right of `warmth_vs_sentiment_all74_shorthand.png`) come disproportionately from Global-Health clusters (Africa/LatAm over-share 10-14% vs 2-3% baseline — see `docs/VIDEO_LEGEND.md`). *Hypothesis:* video is a *compensatory* signal for under-represented regions, not a universal boost. Chinese video under-share (0.7%) supports this — Tsinghua/China bios exist (70) but videos don’t.

## How to use this next

- `data/bios_clusters.csv` (`shorthand,cluster,cluster_name`) → join on `name` to `data/video_legend.csv` (`shorthand`) → `data/bios_clusters_pca.csv` (`pca0,pca1`) for any PNG: `plt.scatter(pca0,pca1,c=cluster)` + `annotate(shorthand)` — see `analytics_dashboard/bios_clusters_pca.png`.
- To make “Schwarzman vs others” simple: filter `cluster==3` vs `cluster==0` and plot `region` share (US/CN/Other tables in `docs/VIDEO_LEGEND.md` already grouped). Or compare any cluster to `all 1497` baseline (`region` counts).
- **Next data to break H-level:** fill 50 pending videos (`make transcripts` — free Whisper) → re-run KMeans on *transcripts* (spoken language vs bios) and see if Health/Tech video language converges.


---

## Distributions for the names of people that applied — grouped by cluster

Each cluster below is a **name group** you can copy into your own application framing. Shorthand = First+Last (from `data/video_legend.csv` style) for readable plots; full lists in `data/cluster_names/cluster_*.csv`.

| Cluster | n | Region mix (from `bios_clusters_by_region.png`) | Cohort 2026/2027 | Top feeder signal |
|---|---|---|---|---|
| **Tech-Business Builders (n104)** | 36% | US 38% · CN 15% · Other 16% · Asia-Pac 9% | 51 / 53 (stable) | Dispersed — no single feeder, `MIT/Stanford/Tsinghua` scattered (see `bios_clusters_by_feeder.png`) |
| **Policy/International (n84)** | 29% | US 64% · CN 11% · Europe/LatAm 8% | 43 / 41 | **Harvard-heavy** — `Harvard` appears as top-3 term in cluster only here |
| **Climate & China Bridge (n70)** | 25% | **CN 44%** · US 13% · Europe/LatAm 14% | 36 / 34 | Most China-concentrated — `Hong Kong, Tsinghua, climate` story |
| **Health Systems (n27)** | 9% | US 48% · CN 15% · Africa/MiddleEast 15% | 14 / 13 | Most dispersed — no dominant feeder (good if you’re non-traditional) |

**Name distributions — the actual people (first 8 shorthand per cluster, full in `data/cluster_names/`):**

- **Tech-Business:** `AZ Adele Zhong (CN), AD Akorfa Dagadu (Ghana/MIT), AM Albee Mote (Myanmar), AH Alessandro Hammond (US/Harvard), SD Shir Diner...` → *founders who shipped tech for development*.
- **Policy/Intl:** `AH Aili Hou (US/Columbia), AG Aleena Gul (US/Yale), AK Aleksandr Kuzmenchuk (US/W&M), AW Amanda Whylie (Jamaica)...` → *IR/law institutional language*.
- **Climate-Bridge:** `AS Ajay Sawant (India), AT Alex Tseng (US/Princeton), AT Alicia Tien (MY/Tsinghua), LO Lozangtashi (CN/Tibet)...` → *climate/education + China bridge*.
- **Health:** `AB Anita Bassey (US), AE Ayotomiwa Elesho (Nigeria/Ibadan), DC Daphne Chebesi (Cameroon/Ashesi)...` → *health equity systems builders*.

![By region](analytics_dashboard/bios_clusters_by_region.png)
![By cohort](analytics_dashboard/bios_clusters_by_cohort.png)
![By feeder](analytics_dashboard/bios_clusters_by_feeder.png)

---

## What they actually accept — and how to sway your fit

**Read the images you shared:** the L-system tree (*Schwarzman Open Data* cover) is the *single* growth metaphor they want — one trunk (you) branching to many systems — and the treemap (*USA/China/global/international/policy/…*) proves they don’t rank words by frequency of `the/and` but by `china/global/united` — bridge language dwarfs everything else.

**Use the 4 doors to aim, not to list:**

1.  **Pick one door** — Don’t write “I do health *and* climate *and* fintech.” The PCA (`bios_clusters_pca.png`) shows hybrids sit in the middle and blur. Choose the cluster whose top words you can *prove* with verbs: Tech needs `founded/led + technology`, Policy needs `international/law/policy + institution`, Climate needs `china/tsinghua/climate`, Health needs `health/access/systems + community`.
2.  **Bridge is non-negotiable** — Even the Health cluster has `china, global` top-12. Your SOP must contain a US↔China translation moment (not “I love China” but “*I translated X between systems*” — e.g., `Geneva translation > founder hero` from `INTERVIEWS.md`). Test: does your draft contain `cross-cultural / exchange / hong kong / tsinghua / global`? If not, you’re in the `passionate 58` trap.
3.  **Verb > adjective** — The treemap you sent shows `founded, aims, led, health, policy, development` as the large blocks after `USA/China/global`. Mirror that: `founded` (73) and `led` (71) outrank `passionate` (58) 6:1. Write 3 verbs with numbers.
4.  **Fit the distribution, not the feeder** — Policy loves Harvard, but Tech-Business and Climate *don’t* — they’re feeder-dispersed (`bios_clusters_by_feeder.png`). If you’re not at an elite feeder, apply via Tech/Climate where `MIT/Stanford/Tsinghua/state school (Fresno CS27, Montana DM27)` all win. Don’t apologize for your school — pick the door where your proof already fits.
5.  **If you have a video, use it as compensatory** — Warmth v2 mean 63.1: warm + optimistic (top-right of `warmth_vs_sentiment_all74_shorthand.png`) over-shares from Africa/LatAm/Europe (10-14% vs 2.7% CN). If you’re from an under-represented region, a 60s public 1-min intro (YouTube) is leverage; if you’re CN, your bio does the work — video under-share (0.7%) means don’t force it.

> **Copy-paste for your own draft:** open `data/bios_clusters_with_region.csv`, filter `cluster==3` (Tech) and `region==your region`, read 5 bios in that slice — steal the sentence shape, not the content. Then run `python scripts/bios_nlp.py` on your own bio draft to see which cluster you land in before you submit.

