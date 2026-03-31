#!/usr/bin/env python3
"""
Fitbod Sync — GitHub Actions
Reads WorkoutExport.csv already committed to the repo.
Validates, normalises, and saves fitbod_data.json for the dashboard.
Run this after uploading a fresh WorkoutExport.csv to the repo.
"""

import os, json, base64, requests
import pandas as pd
from datetime import datetime
from io import StringIO

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPO  = os.environ.get("GITHUB_REPO", "komootti/strava-dashboard")
CSV_PATH     = "WorkoutExport.csv"
JSON_PATH    = "fitbod_data.json"

headers_gh = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept":        "application/vnd.github.v3+json",
}

# ── Load CSV from GitHub ──────────────────────────────────────────────────────
print("Loading WorkoutExport.csv from GitHub...")
raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{CSV_PATH}"
r = requests.get(raw_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
r.raise_for_status()
df = pd.read_csv(StringIO(r.text))
print(f"✅ {len(df):,} rows loaded")
print(f"   Columns: {df.columns.tolist()}")

# ── Normalise columns ─────────────────────────────────────────────────────────
# Fitbod export columns: Date, Exercise, Reps, Sets, Weight (lbs), Seconds,
# Distance (miles), Incline, isWarmup, Note, AutoStart
col_map = {
    "Date":          "date",
    "Exercise":      "exercise",
    "Reps":          "reps",
    "Sets":          "sets",
    "Weight (lbs)":  "weight_lbs",
    "Seconds":       "seconds",
    "Distance (miles)": "distance_miles",
    "isWarmup":      "is_warmup",
    "Note":          "note",
}
df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date", "exercise"])
df = df[df.get("is_warmup", False) != True]  # exclude warmup sets

# Convert weight to kg
if "weight_lbs" in df.columns:
    df["weight_kg"] = df["weight_lbs"].fillna(0) * 0.453592
else:
    df["weight_kg"] = 0

df["reps"]    = pd.to_numeric(df.get("reps",    0), errors="coerce").fillna(0).astype(int)
df["sets"]    = pd.to_numeric(df.get("sets",    1), errors="coerce").fillna(1).astype(int)
df["seconds"] = pd.to_numeric(df.get("seconds", 0), errors="coerce").fillna(0).astype(int)

# Volume = sets × reps × weight_kg
df["volume_kg"] = df["sets"] * df["reps"] * df["weight_kg"]

# ── Muscle group mapping ──────────────────────────────────────────────────────
UPPER = {
    "Bench Press","Incline Bench Press","Decline Bench Press",
    "Dumbbell Bench Press","Push Up","Chest Fly","Cable Fly",
    "Overhead Press","Arnold Press","Lateral Raise","Front Raise",
    "Shoulder Press","Military Press","Upright Row",
    "Pull Up","Chin Up","Lat Pulldown","Seated Row","Bent Over Row",
    "Barbell Row","Single Arm Row","Face Pull","Cable Row",
    "Bicep Curl","Hammer Curl","Preacher Curl","Cable Curl",
    "Tricep Pushdown","Skull Crusher","Tricep Dip","Close Grip Bench",
    "Dip","Diamond Push Up",
}
LOWER = {
    "Squat","Back Squat","Front Squat","Goblet Squat","Box Squat",
    "Leg Press","Hack Squat","Bulgarian Split Squat","Split Squat",
    "Deadlift","Romanian Deadlift","Sumo Deadlift","Stiff Leg Deadlift",
    "Leg Curl","Leg Extension","Calf Raise","Seated Calf Raise",
    "Lunge","Walking Lunge","Reverse Lunge","Step Up",
    "Hip Thrust","Glute Bridge","Leg Abduction","Leg Adduction",
}
CORE = {
    "Plank","Side Plank","Ab Wheel","Crunch","Sit Up",
    "Hanging Leg Raise","Cable Crunch","Russian Twist","Dead Bug",
    "Pallof Press","Bird Dog","Back Extension","Hyperextension",
}

def classify(exercise):
    ex = str(exercise).strip()
    if any(e.lower() in ex.lower() for e in UPPER): return "Upper"
    if any(e.lower() in ex.lower() for e in LOWER): return "Lower"
    if any(e.lower() in ex.lower() for e in CORE):  return "Core"
    return "Other"

df["muscle_group"] = df["exercise"].apply(classify)
df["week"]         = df["date"].dt.to_period("W").dt.start_time
df["month"]        = df["date"].dt.to_period("M").dt.start_time
df["year"]         = df["date"].dt.year

print(f"   Date range: {df['date'].min().date()} → {df['date'].max().date()}")
print(f"   Exercises: {df['exercise'].nunique()} unique")
print(f"   Muscle groups: {df['muscle_group'].value_counts().to_dict()}")

# ── Build output JSON ─────────────────────────────────────────────────────────
def ts(d):
    """Convert Timestamp/date to ISO string."""
    try: return d.isoformat()
    except: return str(d)

output = {
    "generated":     datetime.utcnow().isoformat(),
    "total_sets":    int(len(df)),
    "total_sessions":int(df["date"].dt.normalize().nunique()),
    "date_min":      ts(df["date"].min()),
    "date_max":      ts(df["date"].max()),

    # Raw rows for detailed views (last 365 days)
    "sets": df[df["date"] >= (df["date"].max() - pd.Timedelta(days=365))][
        ["date","exercise","sets","reps","weight_kg","weight_lbs","volume_kg","muscle_group","week","month","year"]
    ].assign(
        date=lambda x: x["date"].dt.strftime("%Y-%m-%d"),
        week=lambda x: x["week"].dt.strftime("%Y-%m-%d"),
        month=lambda x: x["month"].dt.strftime("%Y-%m-%d"),
    ).to_dict(orient="records"),

    # Weekly volume per muscle group
    "weekly_volume": df.groupby(["week","muscle_group"])["volume_kg"]
        .sum().reset_index()
        .assign(week=lambda x: x["week"].dt.strftime("%Y-%m-%d"))
        .rename(columns={"volume_kg":"volume"})
        .to_dict(orient="records"),

    # Per-exercise max weight over time (top 20 exercises by frequency)
    "top_exercises": df["exercise"].value_counts().head(20).index.tolist(),

    # Personal records per exercise
    "records": df.groupby("exercise").agg(
        max_weight_kg=("weight_kg","max"),
        max_reps=("reps","max"),
        total_sets=("sets","sum"),
        total_volume=("volume_kg","sum"),
        last_date=("date","max"),
    ).reset_index()
     .assign(last_date=lambda x: x["last_date"].dt.strftime("%Y-%m-%d"))
     .sort_values("total_volume", ascending=False)
     .to_dict(orient="records"),

    # Session list (most recent 90 days)
    "sessions": df.groupby(df["date"].dt.normalize()).agg(
        exercises=("exercise","nunique"),
        total_sets=("sets","sum"),
        total_volume=("volume_kg","sum"),
        muscle_groups=("muscle_group", lambda x: list(x.unique())),
    ).reset_index()
     .sort_values("date", ascending=False)
     .head(90)
     .assign(date=lambda x: x["date"].dt.strftime("%Y-%m-%d"))
     .to_dict(orient="records"),
}

print(f"✅ Built JSON: {len(output['sets'])} set records, {len(output['sessions'])} sessions")

# ── Push to GitHub ────────────────────────────────────────────────────────────
api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{JSON_PATH}"
r = requests.get(api_url, headers=headers_gh)
sha = r.json()["sha"] if r.status_code == 200 else None

content = base64.b64encode(json.dumps(output, indent=2).encode()).decode()
payload = {
    "message": f"Fitbod sync: {output['total_sessions']} sessions ({datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC)",
    "content": content,
}
if sha:
    payload["sha"] = sha

r = requests.put(api_url, headers=headers_gh, json=payload)
r.raise_for_status()
print(f"✅ Pushed fitbod_data.json — commit: {r.json()['commit']['sha'][:7]}")
print("🏁 Fitbod sync complete!")
