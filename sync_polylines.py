#!/usr/bin/env python3
"""
Polyline sync — fetches its own Strava access token independently.
Run after main sync.py or standalone.
"""
import os, json, requests, base64
from datetime import datetime

GITHUB_TOKEN        = os.environ["GITHUB_TOKEN"]
GITHUB_REPO         = os.environ.get("GITHUB_REPO", "komootti/strava-dashboard")
STRAVA_CLIENT_ID    = os.environ["STRAVA_CLIENT_ID"]
STRAVA_CLIENT_SECRET= os.environ["STRAVA_CLIENT_SECRET"]
STRAVA_REFRESH_TOKEN= os.environ["STRAVA_REFRESH_TOKEN"]
JSON_PATH           = "polylines.json"

headers_gh = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept":        "application/vnd.github.v3+json",
}

# ── Step 1: Get fresh Strava access token ─────────────────────────────────────
print("Getting Strava access token...")
r = requests.post("https://www.strava.com/oauth/token", data={
    "client_id":     STRAVA_CLIENT_ID,
    "client_secret": STRAVA_CLIENT_SECRET,
    "refresh_token": STRAVA_REFRESH_TOKEN,
    "grant_type":    "refresh_token",
})
r.raise_for_status()
access_token = r.json()["access_token"]
print("✅ Got access token")

strava_headers = {"Authorization": f"Bearer {access_token}"}

# ── Step 2: Load existing polylines.json from GitHub ─────────────────────────
api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{JSON_PATH}"
r = requests.get(api_url, headers=headers_gh)
if r.status_code == 200:
    meta     = r.json()
    sha      = meta["sha"]
    existing = json.loads(base64.b64decode(meta["content"]).decode())
    print(f"✅ Loaded {len(existing)} existing polylines")
else:
    sha      = None
    existing = {}
    print("No existing polylines.json — creating fresh")

# ── Step 3: Fetch recent activities and extract polylines ─────────────────────
print("Fetching activities from Strava...")
new_count = 0

for page in range(1, 4):  # fetch up to 3 pages = 300 activities
    acts = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers=strava_headers,
        params={"per_page": 100, "page": page}
    ).json()

    if not acts:
        break

    for act in acts:
        act_id   = str(act["id"])
        polyline = act.get("map", {}).get("summary_polyline", "")
        if act_id not in existing and polyline:
            existing[act_id] = polyline
            new_count += 1

    print(f"  Page {page}: {len(acts)} activities")

print(f"Added {new_count} new polylines. Total: {len(existing)}")

if new_count == 0:
    print("Nothing to update.")
    exit(0)

# ── Step 4: Push updated polylines.json to GitHub ────────────────────────────
content = base64.b64encode(json.dumps(existing, indent=2).encode()).decode()
payload = {
    "message": f"Polyline sync: {len(existing)} routes ({datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC)",
    "content": content,
}
if sha:
    payload["sha"] = sha

r = requests.put(api_url, headers=headers_gh, json=payload)
r.raise_for_status()
print(f"✅ Pushed polylines.json — commit: {r.json()['commit']['sha'][:7]}")
