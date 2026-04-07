#!/usr/bin/env python3
"""
Strava Auto Sync — GitHub Actions
Pulls new activities from Strava, appends to activities.csv, commits to GitHub.
Uses a 7-day lookback window to catch late-uploaded activities.
"""

import os, time, requests, base64, io
import pandas as pd
from datetime import datetime

# ── Credentials from GitHub Secrets ──────────────────────────────────────────
CLIENT_ID     = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["STRAVA_REFRESH_TOKEN"]
GITHUB_TOKEN  = os.environ["GITHUB_TOKEN"]
GITHUB_REPO   = os.environ.get("GITHUB_REPO", "komootti/strava-dashboard")
CSV_PATH      = "activities.csv"

# ── Step 1: Get fresh Strava access token ─────────────────────────────────────
print("Refreshing Strava access token...")
r = requests.post("https://www.strava.com/oauth/token", data={
    "client_id":     CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type":    "refresh_token",
    "refresh_token": REFRESH_TOKEN,
})
r.raise_for_status()
ACCESS_TOKEN = r.json()["access_token"]
print("✅ Authenticated with Strava")

# ── Step 2: Load existing CSV ─────────────────────────────────────────────────
print("Loading activities.csv from GitHub...")
headers_gh = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept":        "application/vnd.github.v3+json",
}
api_url  = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CSV_PATH}"
r        = requests.get(api_url, headers=headers_gh)
r.raise_for_status()
sha      = r.json()["sha"]

raw_url  = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{CSV_PATH}"
r        = requests.get(raw_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
r.raise_for_status()
existing = pd.read_csv(io.StringIO(r.text), low_memory=False)

existing["_date"] = pd.to_datetime(
    existing["Activity Date"],
    format="%b %d, %Y, %I:%M:%S %p", errors="coerce")
last_date = existing["_date"].max()

# 7-day lookback — catches activities uploaded late, out of order, or from watch sync delays
after_ts  = int(last_date.timestamp()) - (7 * 24 * 3600)
print(f"✅ {len(existing):,} existing — last: {last_date.strftime('%d %b %Y')} — fetching from {(last_date - pd.Timedelta(days=7)).strftime('%d %b %Y')}")

# ── Step 3: Fetch activities from Strava ──────────────────────────────────────
print("Fetching activities from Strava...")
headers_st = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
all_new    = []
page       = 1

while True:
    r = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers=headers_st,
        params={"after": after_ts, "per_page": 100, "page": page},
    )
    r.raise_for_status()
    batch = r.json()
    if not batch:
        break
    all_new.extend(batch)
    page += 1
    time.sleep(0.5)

print(f"✅ {len(all_new)} activities fetched from Strava (last 7 days)")

if len(all_new) == 0:
    print("Nothing to sync — done.")
    exit(0)

# ── Step 4: Convert to CSV rows ───────────────────────────────────────────────
rows = []
for a in all_new:
    start = datetime.fromisoformat(a["start_date_local"].replace("Z", ""))
    rows.append({
        "Activity ID":            a.get("id"),
        "Activity Date":          start.strftime("%b %-d, %Y, %I:%M:%S %p"),
        "Activity Name":          a.get("name"),
        "Activity Type":          a.get("type"),
        "Activity Description":   a.get("description", ""),
        "Elapsed Time":           a.get("elapsed_time"),
        "Distance":               round(a.get("distance", 0) / 1000, 2),
        "Moving Time":            a.get("moving_time"),
        "Distance.1":             a.get("distance", 0),
        "Elapsed Time.1":         a.get("elapsed_time"),
        "Max Speed":              a.get("max_speed"),
        "Average Speed":          a.get("average_speed"),
        "Elevation Gain":         a.get("total_elevation_gain"),
        "Elevation Loss":         a.get("elev_low"),
        "Elevation Low":          a.get("elev_low"),
        "Elevation High":         a.get("elev_high"),
        "Max Heart Rate":         a.get("max_heartrate"),
        "Max Heart Rate.1":       a.get("max_heartrate"),
        "Average Heart Rate":     a.get("average_heartrate"),
        "Average Watts":          a.get("average_watts"),
        "Weighted Average Power":  a.get("weighted_average_watts"),
        "Average Cadence":        a.get("average_cadence"),
        "Calories":               a.get("calories"),
        "Relative Effort":        a.get("suffer_score"),
    })

new_df = pd.DataFrame(rows)

# ── Step 5: Merge and deduplicate by Activity ID ──────────────────────────────
existing = existing.drop(columns=["_date"], errors="ignore")
for col in existing.columns:
    if col not in new_df.columns:
        new_df[col] = None
new_df   = new_df.reindex(columns=existing.columns)
combined = pd.concat([existing, new_df], ignore_index=True)
combined = combined.drop_duplicates(subset=["Activity ID"], keep="last")
combined = combined.sort_values("Activity Date").reset_index(drop=True)

added = len(combined) - (len(existing))
print(f"✅ {len(combined):,} total activities — {added} new added")

# ── Step 6: Push to GitHub ────────────────────────────────────────────────────
print("Pushing to GitHub...")
csv_content = combined.to_csv(index=False).encode("utf-8")
encoded     = base64.b64encode(csv_content).decode("utf-8")

payload = {
    "message": f"Auto-sync: {added} new activities ({datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC)",
    "content": encoded,
    "sha":     sha,
}
r = requests.put(api_url, headers=headers_gh, json=payload)
r.raise_for_status()
print(f"✅ Pushed — commit: {r.json()['commit']['sha'][:7]}")
print("✅ Dashboard will update within 5 minutes.")
print("\n🏁 Sync complete!")

# ── Step 7: Compute and push training_load.json ───────────────────────────────
print("Computing CTL/ATL/TSB and pushing training_load.json...")

import json, math
import numpy as np

ENDURANCE = {'Run','Ride','Virtual Ride','Virtual Run','Walk','Hike',
             'Nordic Ski','Swim','Rowing','E-Bike Ride','Stand Up Paddling','Kayaking'}

# Use the freshly combined CSV
tl_df = combined.copy()
tl_df['_date'] = pd.to_datetime(
    tl_df['Activity Date'],
    format='%b %d, %Y, %I:%M:%S %p', errors='coerce')
tl_df['_date'] = tl_df['_date'].fillna(
    pd.to_datetime(tl_df['Activity Date'], format='mixed', errors='coerce'))
tl_df['Moving Time']        = pd.to_numeric(tl_df['Moving Time'],        errors='coerce').fillna(0)
tl_df['Average Heart Rate'] = pd.to_numeric(tl_df['Average Heart Rate'], errors='coerce').fillna(130)
tl_df['Relative Effort']    = pd.to_numeric(tl_df['Relative Effort'],    errors='coerce')

end_df = tl_df[tl_df['Activity Type'].isin(ENDURANCE)].copy()
end_df['tss'] = end_df['Relative Effort'].fillna(
    end_df['Moving Time'] / 60 * (end_df['Average Heart Rate'] / 150) ** 2 * 0.5)

# Daily TSS
daily = end_df.groupby(end_df['_date'].dt.normalize())['tss'].sum().reset_index()
daily.columns = ['date', 'tss']
full_range = pd.date_range(daily['date'].min(), daily['date'].max(), freq='D')
daily = daily.set_index('date').reindex(full_range, fill_value=0).reset_index()
daily.columns = ['date', 'tss']

# EWM — pandas span formula matches app.py exactly
daily['ctl'] = daily['tss'].ewm(span=42, adjust=False).mean()
daily['atl'] = daily['tss'].ewm(span=7,  adjust=False).mean()
daily['tsb'] = daily['ctl'] - daily['atl']

latest = daily.iloc[-1]
ctl = round(float(latest['ctl']), 1)
atl = round(float(latest['atl']), 1)
tsb = round(float(latest['tsb']), 1)

# Last 42 days of daily CTL/ATL/TSB for sparklines
last_42 = daily.tail(42)[['date','ctl','atl','tsb','tss']].copy()
last_42['date'] = last_42['date'].dt.strftime('%Y-%m-%d')
last_42['ctl']  = last_42['ctl'].round(1)
last_42['atl']  = last_42['atl'].round(1)
last_42['tsb']  = last_42['tsb'].round(1)
last_42['tss']  = last_42['tss'].round(1)

payload_json = {
    'generated': datetime.utcnow().isoformat(),
    'ctl': ctl,
    'atl': atl,
    'tsb': tsb,
    'history': last_42.to_dict(orient='records'),
}

print(f"  CTL={ctl}  ATL={atl}  TSB={tsb}")

# Push training_load.json to GitHub
tl_path = 'training_load.json'
tl_api   = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{tl_path}"
r_tl     = requests.get(tl_api, headers=headers_gh)
tl_sha   = r_tl.json().get('sha') if r_tl.status_code == 200 else None

tl_content = base64.b64encode(
    json.dumps(payload_json, indent=2).encode()).decode()
tl_payload = {
    'message': f"Update training_load.json ({datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC)",
    'content': tl_content,
}
if tl_sha:
    tl_payload['sha'] = tl_sha

r_tl = requests.put(tl_api, headers=headers_gh, json=tl_payload)
r_tl.raise_for_status()
print(f"✅ Pushed training_load.json — CTL={ctl} ATL={atl} TSB={tsb}")
