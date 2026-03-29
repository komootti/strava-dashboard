#!/usr/bin/env python3
"""
Oura Ring Sync — GitHub Actions
Fetches readiness, sleep, HRV, resting HR, body temp from Oura API v2
and saves to oura_data.json on GitHub.
"""

import os, json, requests, base64
from datetime import datetime, timedelta

OURA_TOKEN   = os.environ["OURA_ACCESS_TOKEN"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPO  = os.environ.get("GITHUB_REPO", "komootti/strava-dashboard")
JSON_PATH    = "oura_data.json"
DAYS_BACK    = 90

headers_oura = {"Authorization": f"Bearer {OURA_TOKEN}"}
headers_gh   = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept":        "application/vnd.github.v3+json",
}

end_date   = datetime.utcnow().date()
start_date = end_date - timedelta(days=DAYS_BACK)
params     = {"start_date": str(start_date), "end_date": str(end_date)}

def fetch(endpoint):
    r = requests.get(
        f"https://api.ouraring.com/v2/usercollection/{endpoint}",
        headers=headers_oura, params=params, timeout=15
    )
    r.raise_for_status()
    return r.json().get("data", [])

print("Fetching Oura data...")
readiness = fetch("daily_readiness")
sleep     = fetch("daily_sleep")
sleep_det = fetch("sleep")
activity  = fetch("daily_activity")

print(f"  Readiness: {len(readiness)} days")
print(f"  Sleep: {len(sleep)} days")
print(f"  Sleep details: {len(sleep_det)} periods")
print(f"  Activity: {len(activity)} days")

daily = {}

for r in readiness:
    d = r["day"]
    daily.setdefault(d, {})
    daily[d]["readiness_score"]           = r.get("score")
    daily[d]["readiness_contributors"]    = r.get("contributors", {})
    daily[d]["temperature_deviation"]     = r.get("temperature_deviation")
    daily[d]["temperature_trend_deviation"] = r.get("temperature_trend_deviation")

for s in sleep:
    d = s["day"]
    daily.setdefault(d, {})
    daily[d]["sleep_score"]        = s.get("score")
    daily[d]["sleep_contributors"] = s.get("contributors", {})

for s in sleep_det:
    d = s.get("day") or (s.get("bedtime_start") or "")[:10]
    if not d: continue
    daily.setdefault(d, {})
    if s.get("type") == "long_sleep" or "hrv_avg" not in daily[d]:
        hrv_data  = s.get("hrv", {})
        hrv_items = hrv_data.get("items", []) if isinstance(hrv_data, dict) else []
        hrv_vals  = [v for v in hrv_items if v is not None and v > 0]
        if hrv_vals:
            daily[d]["hrv_avg"] = round(sum(hrv_vals) / len(hrv_vals), 1)
            daily[d]["hrv_min"] = min(hrv_vals)
            daily[d]["hrv_max"] = max(hrv_vals)
        daily[d]["resting_hr"]      = s.get("lowest_heart_rate")
        daily[d]["avg_hr_sleep"]    = s.get("average_heart_rate")
        daily[d]["total_sleep_min"] = s.get("total_sleep_duration", 0) // 60 if s.get("total_sleep_duration") else None
        daily[d]["deep_sleep_min"]  = s.get("deep_sleep_duration", 0)  // 60 if s.get("deep_sleep_duration") else None
        daily[d]["rem_sleep_min"]   = s.get("rem_sleep_duration", 0)   // 60 if s.get("rem_sleep_duration") else None
        daily[d]["sleep_efficiency"]= s.get("efficiency")
        daily[d]["respiratory_rate"]= s.get("average_breath")
        if s.get("bedtime_start"): daily[d]["bedtime_start"] = s["bedtime_start"]
        if s.get("bedtime_end"):   daily[d]["waketime"]      = s["bedtime_end"]

for a in activity:
    d = a["day"]
    daily.setdefault(d, {})
    # Oura v2: 'score' is the activity score (0-100)
    score = a.get("score")
    daily[d]["activity_score"]  = score
    daily[d]["steps"]           = a.get("steps")
    daily[d]["active_calories"] = a.get("active_calories")
    daily[d]["total_calories"]  = a.get("total_calories")
    daily[d]["target_calories"] = a.get("target_calories")
    # Log for debugging
    if score is not None:
        print(f"  Activity score {d}: {score}")

# Build sorted list
data_list = [{"date": d, **v} for d, v in sorted(daily.items(), reverse=True)]

# Count how many have activity scores
with_score = sum(1 for x in data_list if x.get("activity_score") is not None)
print(f"✅ {len(data_list)} days total, {with_score} with activity score")

# Push to GitHub
api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{JSON_PATH}"
r = requests.get(api_url, headers=headers_gh)
sha = r.json()["sha"] if r.status_code == 200 else None

content = base64.b64encode(json.dumps(data_list, indent=2).encode()).decode()
payload = {
    "message": f"Oura sync: {len(data_list)} days ({datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC)",
    "content": content,
}
if sha:
    payload["sha"] = sha

r = requests.put(api_url, headers=headers_gh, json=payload)
r.raise_for_status()
print(f"✅ Pushed oura_data.json — commit: {r.json()['commit']['sha'][:7]}")
print("🏁 Oura sync complete!")
