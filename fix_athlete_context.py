#!/usr/bin/env python3
"""
fix_athlete_context.py
Patches app.py with accurate athlete profile across all three AI prompt locations:
  1. Activity Analysis (Overview tab) — main coaching prompt
  2. HR Zone calculation — uses actual max HR and zone boundaries
  3. Ask tab system prompt — chat coach context
"""

import re, sys
from pathlib import Path

APP = Path("app.py")
if not APP.exists():
    print("ERROR: app.py not found. Run this script from the repo root.")
    sys.exit(1)

src = APP.read_text(encoding="utf-8")
original = src

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 1 — Activity Analysis prompt: replace generic coach intro with full profile
# ─────────────────────────────────────────────────────────────────────────────
OLD_COACH_INTRO = 'prompt = f"""You are a personal endurance sports coach analysing an athlete\'s training data.'

NEW_COACH_INTRO = '''prompt = f"""You are a personal endurance sports coach analysing an athlete\'s training data.

ATHLETE PROFILE:
- Male, age 56, based in Finland
- Max HR: 175 bpm
- HR Zones: Z1 rest–120 bpm | Z2 121–140 bpm | Z3 141–158 bpm | Z4 159–165 bpm | Z5 166+ bpm
- Primary goals: (1) increase upper body muscle mass, (2) build solid running and cycling endurance
- Training mix: road/gravel cycling, running, gym/strength work
- Strength preference: upper body focus — avoids heavy lower body gym work to protect running and cycling legs
- Use actual zone boundaries above (not percentage-of-max estimates) when referencing HR zones'''

if OLD_COACH_INTRO not in src:
    print("WARN: Patch 1 target string not found — may already be patched or code changed.")
else:
    src = src.replace(OLD_COACH_INTRO, NEW_COACH_INTRO, 1)
    print("OK  Patch 1 applied — activity analysis prompt updated")

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 2 — HR Zone calculation: replace estimated max HR with real zones
# ─────────────────────────────────────────────────────────────────────────────
OLD_HR_CALC = '''    hr_insight = ""
    if la_hr_v > 0:
        max_hr_est = 220 - 35  # rough estimate, adjust if known
        hr_pct = la_hr_v / max_hr_est * 100
        if hr_pct < 60:    hr_insight = "Zone 1 · Recovery pace"
        elif hr_pct < 70:  hr_insight = "Zone 2 · Aerobic base"
        elif hr_pct < 80:  hr_insight = "Zone 3 · Aerobic power"
        elif hr_pct < 90:  hr_insight = "Zone 4 · Threshold"
        else:              hr_insight = "Zone 5 · Max effort"'''

NEW_HR_CALC = '''    hr_insight = ""
    if la_hr_v > 0:
        # Actual HR zones (male, 56, max HR 175)
        if la_hr_v <= 120:   hr_insight = "Zone 1 · Recovery"
        elif la_hr_v <= 140: hr_insight = "Zone 2 · Aerobic base"
        elif la_hr_v <= 158: hr_insight = "Zone 3 · Aerobic power"
        elif la_hr_v <= 165: hr_insight = "Zone 4 · Threshold"
        else:                hr_insight = "Zone 5 · Max effort"'''

if OLD_HR_CALC not in src:
    print("WARN: Patch 2 target string not found — may already be patched or code changed.")
else:
    src = src.replace(OLD_HR_CALC, NEW_HR_CALC, 1)
    print("OK  Patch 2 applied — HR zone calculation updated to real boundaries")

# ─────────────────────────────────────────────────────────────────────────────
# PATCH 3 — Ask tab system prompt: replace generic description with full profile
# ─────────────────────────────────────────────────────────────────────────────
OLD_SYSTEM = (
    '            "use a friendly coaching tone. The user trains cycling (road/gravel), running, "\n'
    '            "and gym work; they are based in Finland. "\n'
    '            "If something is not in the data, say so clearly."\n'
    '        )'
)

NEW_SYSTEM = (
    '            "use a friendly coaching tone. "\n'
    '            "Athlete profile: male, age 56, based in Finland. "\n'
    '            "Max HR 175 bpm. HR zones: Z1 rest-120, Z2 121-140, Z3 141-158, Z4 159-165, Z5 166+. "\n'
    '            "Primary goals: (1) increase upper body muscle mass, "\n'
    '            "(2) build solid running and cycling endurance. "\n'
    '            "Trains road/gravel cycling, running, and gym/strength (upper body focus — "\n'
    '            "avoids heavy lower body gym work to protect running and cycling performance). "\n'
    '            "Reference actual zone boundaries when discussing HR. "\n'
    '            "If something is not in the data, say so clearly."\n'
    '        )'
)

if OLD_SYSTEM not in src:
    print("WARN: Patch 3 target string not found — may already be patched or code changed.")
else:
    src = src.replace(OLD_SYSTEM, NEW_SYSTEM, 1)
    print("OK  Patch 3 applied — Ask tab system prompt updated")

# ─────────────────────────────────────────────────────────────────────────────
# Write result
# ─────────────────────────────────────────────────────────────────────────────
if src == original:
    print("\nNo changes made — all patches already applied or targets not found.")
    sys.exit(0)

APP.write_text(src, encoding="utf-8")
print(f"\n✓ app.py updated successfully ({APP.stat().st_size:,} bytes)")
