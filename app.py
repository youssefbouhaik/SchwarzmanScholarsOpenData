"""Schwarzman Open Data — Streamlit explorer
Run: pip install -r requirements.txt && streamlit run app.py
"""
import pathlib, pandas as pd
import streamlit as st

ROOT = pathlib.Path(__file__).parent
CSV = ROOT / "data" / "schwarzman_scholars_dataset.csv"

st.set_page_config(page_title="Schwarzman Open Data 2017-2027", layout="wide")
st.title("Schwarzman Scholars Open Data — 1,497 scholars, 74 public videos")
st.caption("Hand-curated 2017–2027 + Whisper transcripts + scholar interviews. Filter to see cohort/country/feeder trends.")

@st.cache_data
def load():
    df = pd.read_csv(CSV, encoding="utf-8")
    df["cohort_year"] = df["cohort_year"].astype(str)
    return df

df = load()

with st.sidebar:
    st.header("Filters")
    cohorts = sorted(df["cohort_year"].unique())
    sel_cohorts = st.multiselect("Cohort", cohorts, default=cohorts)
    countries = sorted(df["country"].dropna().unique())
    sel_country = st.multiselect("Country", countries, default=[])
    has_video = st.checkbox("Only with public video (74)")

    q = st.text_input("Search name / university / bio")

f = df[df["cohort_year"].isin(sel_cohorts)]
if sel_country:
    f = f[f["country"].isin(sel_country)]
if has_video:
    f = f[f["has_intro_video"]==1]
if q:
    ql = q.lower()
    f = f[f.apply(lambda r: ql in str(r["name"]).lower() or ql in str(r["university"]).lower() or ql in str(r["bio"]).lower(), axis=1)]

c1,c2,c3,c4 = st.columns(4)
c1.metric("Scholars shown", len(f))
c2.metric("With video", int((f["has_intro_video"]==1).sum()))
c3.metric("With bio", int(f["bio"].notna().sum()))
c4.metric("Countries", f["country"].nunique())

st.dataframe(f[["name","country","university","cohort_year","youtube_video_id","has_intro_video"]].head(200), use_container_width=True, height=400)

colA, colB = st.columns(2)
with colA:
    st.subheader("Top countries (filtered)")
    st.bar_chart(f["country"].value_counts().head(10))
with colB:
    st.subheader("Cohort size (filtered)")
    st.bar_chart(f["cohort_year"].value_counts().sort_index())

st.divider()
sel = st.selectbox("Preview a scholar with video", f[f["youtube_video_id"]!=""].head(50)["name"].tolist() if not f.empty else [])
if sel:
    row = f[f["name"]==sel].iloc[0]
    st.write(f"**{row['name']}** — {row['country']} — {row['university']} — Cohort {row['cohort_year']}")
    if row["bio"]:
        st.write(row["bio"][:800] + ("..." if len(str(row["bio"]))>800 else ""))
    url = row["youtube_video_id"]
    if url:
        st.video(url)
        st.caption(f"[Open on YouTube]({url})")
    # transcript preview if exists
    import re
    vid = ""
    if "v=" in str(url):
        vid = str(url).split("v=")[-1].split("&")[0]
    elif "/shorts/" in str(url):
        vid = str(url).split("/shorts/")[1].split("?")[0]
    tpath = ROOT / "data" / "transcripts" / f"{vid}.txt"
    if vid and tpath.exists():
        st.subheader("Whisper transcript")
        st.text(tpath.read_text(encoding="utf-8")[:2000])

st.caption("Source: data/schwarzman_scholars_dataset.csv • Run `python batch_processor.py` to populate data/transcripts/ • See README.md for limitations (4.9% video sharing bias).")
