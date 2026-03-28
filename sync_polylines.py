#!/usr/bin/env python3
"""
Polyline sync — called from GitHub Actions after main Strava sync.
Fetches the summary_polyline for recent activities and saves to polylines.json on GitHub.
"""
import os, json, requests, base64
from datetime import datetime

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPO  = os.environ.get("GITHUB_REPO", "komootti/strava-dashboard")
ACCESS_TOKEN = os.environ["STRAVA_ACCESS_TOKEN"]   # set by main sync.py
JSON_PATH    = "polylines.json"

headers_gh = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept":        "application/vnd.github.v3+json",
}

# ── Fetch current polylines.json from GitHub ──────────────────────────────────
api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{JSON_PATH}"
r = requests.get(api_url, headers=headers_gh)
if r.status_code == 200:
    meta     = r.json()
    sha      = meta["sha"]
    existing = json.loads(base64.b64decode(meta["content"]).decode())
    print(f"Loaded {len(existing)} existing polylines")
else:
    sha      = None
    existing = {}
    print("No existing polylines.json — creating fresh")

# ── Fetch recent activities from Strava ───────────────────────────────────────
strava_headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
new_count = 0

# Fetch last 50 activities
acts = requests.get(
    "https://www.strava.com/api/v3/athlete/activities",
    headers=strava_headers,
    params={"per_page": 50, "page": 1}
).json()

for act in acts:
    act_id  = str(act["id"])
    polyline = act.get("map", {}).get("summary_polyline", "")
    if act_id not in existing and polyline:
        existing[act_id] = polyline
        new_count += 1

print(f"Added {new_count} new polylines. Total: {len(existing)}")

if new_count == 0:
    print("Nothing to update.")
    exit(0)

# ── Push updated polylines.json to GitHub ────────────────────────────────────
content = base64.b64encode(json.dumps(existing, indent=2).encode()).decode()
payload = {
    "message": f"Polyline sync: {len(existing)} activities ({datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC)",
    "content": content,
}
if sha:
    payload["sha"] = sha

r = requests.put(api_url, headers=headers_gh, json=payload)
r.raise_for_status()
print(f"✅ Pushed polylines.json — commit: {r.json()['commit']['sha'][:7]}")
