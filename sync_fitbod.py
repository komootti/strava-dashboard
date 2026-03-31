#!/usr/bin/env python3
"""
Fitbod Sync — GitHub Actions
Reads WorkoutExport.csv from the repo and builds fitbod_data.json.
Handles Fitbod's actual export format: Date, Exercise, Reps, Weight(kg),
Duration(s), Distance(m), Incline, Resistance, isWarmup, Note, multiplier
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

# ── Normalise columns to internal names ──────────────────────────────────────
# Map whatever Fitbod exports to consistent internal names
col_map = {}
for col in df.columns:
    cl = col.lower().strip()
    if cl == "date":                           col_map[col] = "date"
    elif cl == "exercise":                     col_map[col] = "exercise"
    elif cl == "reps":                         col_map[col] = "reps"
    elif "weight" in cl and "kg" in cl:        col_map[col] = "weight_kg"
    elif "weight" in cl and "lb" in cl:        col_map[col] = "weight_lbs"
    elif "weight" in cl:                       col_map[col] = "weight_kg"
    elif cl in ("sets", "set"):                col_map[col] = "sets"
    elif "duration" in cl or cl == "seconds":  col_map[col] = "seconds"
    elif "distance" in cl:                     col_map[col] = "distance"
    elif "warmup" in cl or "iswarmup" in cl:   col_map[col] = "is_warmup"
    elif "multiplier" in cl:                   col_map[col] = "multiplier"
    elif cl == "note":                         col_map[col] = "note"

df = df.rename(columns=col_map)
print(f"   Mapped columns: {list(col_map.values())}")

# ── Convert weight to kg if needed ───────────────────────────────────────────
if "weight_lbs" in df.columns and "weight_kg" not in df.columns:
    df["weight_kg"] = pd.to_numeric(df["weight_lbs"], errors="coerce").fillna(0) * 0.453592
elif "weight_kg" not in df.columns:
    df["weight_kg"] = 0.0

df["weight_kg"] = pd.to_numeric(df["weight_kg"], errors="coerce").fillna(0)

# ── Sets: Fitbod may not have a sets column — default to 1 ───────────────────
if "sets" not in df.columns:
    df["sets"] = 1
else:
    df["sets"] = pd.to_numeric(df["sets"], errors="coerce").fillna(1)

# ── Reps ──────────────────────────────────────────────────────────────────────
df["reps"] = pd.to_numeric(df.get("reps", 0), errors="coerce").fillna(0)

# ── Multiplier (Fitbod uses this for sets sometimes) ─────────────────────────
if "multiplier" in df.columns:
    mult = pd.to_numeric(df["multiplier"], errors="coerce").fillna(1)
    # If sets column is missing/all 1s, use multiplier as sets
    if df["sets"].max() <= 1:
        df["sets"] = mult.clip(lower=1)

df["sets"] = df["sets"].astype(int)
df["reps"] = df["reps"].astype(int)

# ── Filter warmups ────────────────────────────────────────────────────────────
if "is_warmup" in df.columns:
    df = df[~df["is_warmup"].astype(str).str.lower().isin(["true","1","yes"])]

# ── Parse dates ───────────────────────────────────────────────────────────────
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date", "exercise"])
df = df.sort_values("date")

# ── Volume ────────────────────────────────────────────────────────────────────
df["volume_kg"] = df["sets"] * df["reps"] * df["weight_kg"]

# ── Muscle group classification ───────────────────────────────────────────────
UPPER_KW = ["bench","chest","fly","press","push","pull","row","lat","cable","curl",
            "tricep","bicep","dip","shoulder","military","arnold","upright","face pull",
            "pulldown","pullup","pull-up","chin","overhead","raise","extension arm"]
LOWER_KW = ["squat","deadlift","leg","lunge","calf","hip thrust","glute","step up",
            "hack","bulgarian","split squat","rdl","sumo","stiff","romanian"]
CORE_KW  = ["plank","crunch","ab ","core","sit up","russian","pallof","bird dog",
            "dead bug","hyperextension","back extension","oblique","hanging leg"]

def classify(exercise):
    ex = str(exercise).lower()
    if any(k in ex for k in LOWER_KW): return "Lower"
    if any(k in ex for k in UPPER_KW): return "Upper"
    if any(k in ex for k in CORE_KW):  return "Core"
    return "Other"

df["muscle_group"] = df["exercise"].apply(classify)
df["week"]         = df["date"].dt.to_period("W").dt.start_time
df["month"]        = df["date"].dt.to_period("M").dt.start_time
df["year"]         = df["date"].dt.year

print(f"   Date range: {df['date'].min().date()} → {df['date'].max().date()}")
print(f"   Exercises: {df['exercise'].nunique()} unique")
print(f"   Muscle groups: {df['muscle_group'].value_counts().to_dict()}")

def ts(d):
    try: return d.isoformat()
    except: return str(d)

# ── Build output JSON ─────────────────────────────────────────────────────────
output = {
    "generated":      datetime.utcnow().isoformat(),
    "total_sets":     int(len(df)),
    "total_sessions": int(df["date"].dt.normalize().nunique()),
    "date_min":       ts(df["date"].min()),
    "date_max":       ts(df["date"].max()),

    "sets": df[df["date"] >= (df["date"].max() - pd.Timedelta(days=365))][
        ["date","exercise","sets","reps","weight_kg","volume_kg","muscle_group","week","month","year"]
    ].assign(
        date=lambda x: x["date"].dt.strftime("%Y-%m-%d"),
        week=lambda x: x["week"].dt.strftime("%Y-%m-%d"),
        month=lambda x: x["month"].dt.strftime("%Y-%m-%d"),
    ).to_dict(orient="records"),

    "weekly_volume": df.groupby(["week","muscle_group"])["volume_kg"]
        .sum().reset_index()
        .assign(week=lambda x: x["week"].dt.strftime("%Y-%m-%d"))
        .rename(columns={"volume_kg":"volume"})
        .to_dict(orient="records"),

    "top_exercises": df["exercise"].value_counts().head(20).index.tolist(),

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
