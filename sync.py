#!/usr/bin/env python3
"""
Strava Auto Sync — GitHub Actions
Pulls new activities from Strava, appends to activities.csv, commits to GitHub.
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
tokens       = r.json()
ACCESS_TOKEN = tokens["access_token"]
print("✅ Authenticated with Strava")

# ── Step 2: Load existing CSV via raw URL (handles large files correctly) ──────
print("Loading activities.csv from GitHub...")
headers_gh = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept":        "application/vnd.github.v3+json",
}

# Get file SHA via contents API (needed later for the commit)
api_url  = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CSV_PATH}"
r        = requests.get(api_url, headers=headers_gh)
r.raise_for_status()
sha = r.json()["sha"]

# Download actual content via raw URL — works for any file size
raw_url  = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{CSV_PATH}"
r        = requests.get(raw_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
r.raise_for_status()
existing = pd.read_csv(io.StringIO(r.text), low_memory=False)

existing["_date"] = pd.to_datetime(
    existing["Activity Date"],
    format="%b %d, %Y, %I:%M:%S %p", errors="coerce")
last_date = existing["_date"].max()
after_ts  = int(last_date.timestamp()) - (2 * 24 * 3600)  # look back 2 days to catch late uploads
print(f"✅ {len(existing):,} existing activities — last: {last_date.strftime('%d %b %Y')}")

# ── Step 3: Fetch new activities from Strava ──────────────────────────────────
print("Fetching new activities from Strava...")
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

print(f"✅ {len(all_new)} new activities fetched")

if len(all_new) == 0:
    print("Nothing new to sync — done.")
    exit(0)

# ── Step 4: Convert to CSV format ─────────────────────────────────────────────
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

# ── Step 5: Merge and deduplicate ─────────────────────────────────────────────
existing = existing.drop(columns=["_date"], errors="ignore")
for col in existing.columns:
    if col not in new_df.columns:
        new_df[col] = None
new_df   = new_df.reindex(columns=existing.columns)
combined = pd.concat([existing, new_df], ignore_index=True)
combined = combined.drop_duplicates(subset=["Activity ID"], keep="last")
combined = combined.sort_values("Activity Date").reset_index(drop=True)
print(f"✅ {len(combined):,} total activities after merge")

# ── Step 6: Push updated CSV back to GitHub ───────────────────────────────────
print("Pushing to GitHub...")
csv_content = combined.to_csv(index=False).encode("utf-8")
encoded     = base64.b64encode(csv_content).decode("utf-8")

payload = {
    "message": f"Auto-sync: +{len(new_df)} activities ({datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC)",
    "content": encoded,
    "sha":     sha,
}
r = requests.put(api_url, headers=headers_gh, json=payload)
r.raise_for_status()
print(f"✅ Pushed — commit: {r.json()['commit']['sha'][:7]}")
print("✅ Dashboard will update within 5 minutes.")
print("\n🏁 Sync complete!")
