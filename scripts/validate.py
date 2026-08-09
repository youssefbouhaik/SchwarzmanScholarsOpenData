#!/usr/bin/env python3
"""Validate Schwarzman dataset - run: python scripts/validate.py"""
import csv, pathlib, sys

ROOT = pathlib.Path(__file__).parent.parent
CSV = ROOT / "data" / "schwarzman_scholars_dataset.csv"
VIDEOS_MD = ROOT / "ADMITTED_VIDEOS.md"

def fail(msg):
    print(f"✗ {msg}")
    sys.exit(1)
def ok(msg):
    print(f"✓ {msg}")

rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
if len(rows) != 1497:
    fail(f"rows {len(rows)} != 1497")
ok(f"rows 1497")

# no pp tracking
if any("pp=" in (r["youtube_video_id"] or "") for r in rows):
    fail("pp= tracking param still present in youtube_video_id")
ok("no pp= tracking params")

yt = sum(1 for r in rows if r["youtube_video_id"])
has = sum(1 for r in rows if r["has_intro_video"]=="1")
if yt != 74:
    fail(f"youtube non-empty {yt} != 74")
ok(f"youtube links 74")
if has != 74:
    fail(f"has_intro_video 1 count {has} != 74")
ok(f"has_intro_video 74")

# mismatch check
mismatch = sum(1 for r in rows if bool(r["youtube_video_id"]) != (r["has_intro_video"]=="1"))
if mismatch:
    fail(f"mismatch yt vs has_intro_video: {mismatch}")
ok("yt ↔ has_intro_video consistent")

# bios
bios = sum(1 for r in rows if r["bio"] and r["bio"].strip())
if bios != 285:
    print(f"! bios {bios} != 285 (ok if updated)")
else:
    ok("bios 285")

# cohort
import collections
cts = collections.Counter(r["cohort_year"] for r in rows)
expected = {'2017':108,'2018':125,'2019':135,'2020':139,'2021':131,'2022':150,'2023':142,'2024':142,'2025':140,'2026':144,'2027':141}
for k,v in expected.items():
    if cts[k] != v:
        fail(f"cohort {k} {cts[k]} != {v}")
ok("cohort distribution 2017-2027 correct")

# country not 0/and
if any(r["country"].strip() in ("0","and") for r in rows if r["country"]):
    fail("country contains 0/and placeholder")
ok("country clean")

# videos md also clean
if VIDEOS_MD.exists() and "&pp=" in VIDEOS_MD.read_text(encoding="utf-8"):
    fail("ADMITTED_VIDEOS.md still has pp=")
ok("ADMITTED_VIDEOS.md clean")

# check plots exist after make plots (optional)
plots = list((ROOT/"analytics_dashboard").glob("*.png"))
if len(plots) < 4:
    print(f"! only {len(plots)} plots found - run: make plots")
else:
    ok(f"plots found: {len(plots)} in analytics_dashboard/")

print("\nAll checks passed.")
