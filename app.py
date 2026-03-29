import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import io

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Training Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Strava-inspired dark theme ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* Global reset */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Dark background */
.stApp {
    background-color: #f7f5f2;
    color: #1a1a1a;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2ddd8;
}
[data-testid="stSidebar"] * {
    color: #333 !important;
}

/* Main content padding */
.block-container {
    padding: 1.2rem 2rem 1.2rem 2rem !important;
    max-width: 1400px;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e2ddd8;
    border-radius: 12px;
    padding: 1.2rem 1.4rem !important;
    transition: border-color 0.2s;
}
[data-testid="metric-container"]:hover {
    border-color: #fc4c02;
}
[data-testid="stMetricLabel"] {
    color: #666 !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
[data-testid="stMetricValue"] {
    color: #1a1a1a !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    line-height: 1.2;
}
[data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
}

/* Section headers */
h1 {
    color: #1a1a1a !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}
h2 {
    color: #1a1a1a !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.8rem !important;
    margin-bottom: 0.8rem !important;
    padding-bottom: 3px;
    border-bottom: 2px solid #fc4c02;
    display: table;
    line-height: 1.3;
}
h2::after {
    content: none;
}
h3 {
    color: #c8c4be !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
}

/* Divider */
hr {
    border-color: #e2ddd8 !important;
    margin: 1.5rem 0 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #e2ddd8;
    border-radius: 12px;
    overflow: hidden;
}
[data-testid="stDataFrame"] * {
    color: #1a1a1a !important;
    background: transparent !important;
    font-family: "DM Sans", sans-serif !important;
}
[data-testid="stDataFrame"] [class*="dvn-scroller"] {
    background: #ffffff !important;
}
[data-testid="stDataFrame"] canvas {
    filter: invert(0) !important;
}
/* Force the glide data grid to light mode */
.stDataFrame [data-testid="stDataFrame"] {
    --gdg-bg-cell: #ffffff !important;
    --gdg-bg-cell-medium: #f7f5f2 !important;
    --gdg-text-dark: #1a1a1a !important;
    --gdg-text-medium: #555 !important;
    --gdg-text-light: #888 !important;
    --gdg-border-color: #e8e4de !important;
    --gdg-bg-header: #f7f5f2 !important;
    --gdg-bg-header-has-focus: #f0ede8 !important;
}

/* Sliders */
[data-testid="stSlider"] > div > div > div {
    background-color: #fc4c02 !important;
}

/* Multiselect tags */
[data-baseweb="tag"] {
    background-color: #fc4c02 !important;
    border-radius: 6px !important;
}

/* Buttons */
.stButton > button {
    background: #fc4c02 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.2rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.85 !important;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
    }
    .record-value {
        font-size: 1.2rem !important;
    }
}

/* Record card style */
.record-card {
    background: #ffffff;
    border: 1px solid #e2ddd8;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
}
.record-label {
    color: #666;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.record-value {
    color: #fc4c02;
    font-size: 1.5rem;
    font-weight: 700;
    font-family: 'DM Mono', monospace;
    line-height: 1.2;
}
.record-sub {
    color: #888;
    font-size: 0.75rem;
    margin-top: 0.1rem;
}

/* Sport badge */
.sport-badge {
    display: inline-block;
    background: #fc4c02;
    color: white;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 2px 8px;
    border-radius: 4px;
    margin-right: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
GITHUB_RAW_URL    = "https://raw.githubusercontent.com/komootti/strava-dashboard/main/activities.csv"
POLYLINES_RAW_URL = "https://raw.githubusercontent.com/komootti/strava-dashboard/main/polylines.json"

@st.cache_data(ttl=300)
def load_polylines():
    try:
        r = requests.get(POLYLINES_RAW_URL, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}

OURA_RAW_URL = "https://raw.githubusercontent.com/komootti/strava-dashboard/main/oura_data.json"

@st.cache_data(ttl=300)
def load_oura():
    try:
        r = requests.get(OURA_RAW_URL, timeout=10)
        if r.status_code == 200:
            df_o = pd.DataFrame(r.json())
            df_o["date"] = pd.to_datetime(df_o["date"])
            return df_o.sort_values("date", ascending=False).reset_index(drop=True)
    except Exception:
        pass
    return pd.DataFrame()

def decode_polyline(encoded):
    coords = []
    idx = 0
    lat = lng = 0
    while idx < len(encoded):
        for coord in range(2):
            shift = result = 0
            while True:
                b = ord(encoded[idx]) - 63
                idx += 1
                result |= (b & 0x1F) << shift
                shift += 5
                if b < 0x20:
                    break
            val = ~(result >> 1) if result & 1 else result >> 1
            if coord == 0:
                lat += val
            else:
                lng += val
        coords.append((lat / 1e5, lng / 1e5))
    return coords

def make_folium_map(coords, height=280):
    import folium
    if not coords:
        return None
    clat = sum(c[0] for c in coords) / len(coords)
    clon = sum(c[1] for c in coords) / len(coords)
    m = folium.Map(location=[clat, clon], zoom_start=12,
                   tiles="OpenStreetMap", width="100%", height=height)
    folium.PolyLine(coords, color="#fc4c02", weight=4, opacity=0.85).add_to(m)
    folium.CircleMarker(coords[0],  radius=8, color="#ffffff",
                        fill=True, fill_color="#22c55e", fill_opacity=1,
                        weight=2, tooltip="Start").add_to(m)
    folium.CircleMarker(coords[-1], radius=8, color="#ffffff",
                        fill=True, fill_color="#fc4c02", fill_opacity=1,
                        weight=2, tooltip="Finish").add_to(m)
    return m

ENDURANCE = {"Run","Ride","Virtual Ride","Virtual Run","Walk","Hike",
             "Nordic Ski","Swim","Rowing","E-Bike Ride","Stand Up Paddling","Kayaking"}

SPORT_COLORS = {
    "Run":          "#fc4c02",
    "Ride":         "#ffa500",
    "Virtual Ride": "#ffcc44",
    "Walk":         "#4db6ac",
    "E-Bike Ride":  "#ce93d8",
    "Rowing":       "#4fc3f7",
    "Hike":         "#81c784",
    "Nordic Ski":   "#90caf9",
    "Swim":         "#26c6da",
    "Weight Training": "#78909c",
}

CHART_LAYOUT = dict(
    plot_bgcolor="#ffffff",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#666", size=11),
    margin=dict(t=30, b=30, l=50, r=20),
    legend=dict(
        orientation="h", y=1.08,
        font=dict(color="#555", size=11),
        bgcolor="rgba(0,0,0,0)"
    ),
    hoverlabel=dict(
        bgcolor="#ffffff",
        bordercolor="#fc4c02",
        font=dict(color="#1a1a1a", size=12, family="DM Sans"),
    ),
    hovermode="closest",
)

def axis_style():
    return dict(
        gridcolor="#f0ede8",
        linecolor="#e8e4de",
        tickcolor="#ddd",
        tickfont=dict(color="#888", size=11),
        zerolinecolor="#e8e4de",
        title_font=dict(color="#666", size=11),
    )

def lollipop(x, y, color="#fc4c02", name="", unit="km"):
    r,g,b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    tip = "%{y:,.0f} " + unit + "<extra></extra>"
    stem = go.Bar(
        x=x, y=y, name="",
        marker=dict(color="rgba({},{},{},0.18)".format(r,g,b), line=dict(width=0)),
        width=[0.28]*len(list(x)),
        showlegend=False,
        hoverinfo="skip",
    )
    dot = go.Scatter(
        x=x, y=y, mode="markers", name="",
        marker=dict(color=color, size=8, line=dict(color="#ffffff", width=2)),
        showlegend=False,
        hovertemplate=tip,
    )
    return stem, dot

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    r = requests.get(GITHUB_RAW_URL)
    r.raise_for_status()
    raw = pd.read_csv(io.StringIO(r.text), low_memory=False)

    df = pd.DataFrame()
    df["activity_id"]  = raw["Activity ID"]
    df["date"]         = pd.to_datetime(raw["Activity Date"],
                             format="%b %d, %Y, %I:%M:%S %p", errors="coerce")
    df["year"]         = df["date"].dt.year
    df["month"]        = df["date"].dt.month
    df["name"]         = raw["Activity Name"]
    df["sport"]        = raw["Activity Type"]
    df["dist_km"]      = raw["Distance.1"] / 1000
    df["moving_min"]   = raw["Moving Time"] / 60
    df["elev_gain_m"]  = raw["Elevation Gain"]
    df["avg_hr"]       = raw["Average Heart Rate"]
    df["max_hr"]       = raw["Max Heart Rate.1"]
    df["avg_watts"]    = raw["Average Watts"]
    df["avg_speed_ms"] = raw["Average Speed"]
    df["avg_speed_kmh"] = df["avg_speed_ms"] * 3.6
    df["calories"]     = raw["Calories"]
    df["rel_effort"]   = raw["Relative Effort"]
    pace_mask = df["sport"].isin(["Run","Walk","Virtual Run","Hike"])
    df["pace_min_km"] = None
    valid = pace_mask & (df["dist_km"] > 0)
    df.loc[valid, "pace_min_km"] = df.loc[valid, "moving_min"] / df.loc[valid, "dist_km"]
    # Normalise sport names — Strava API returns e.g. "VirtualRide",
    # but the bulk export uses "Virtual Ride". Map all API variants to export format.
    sport_map = {
        "VirtualRide":    "Virtual Ride",
        "VirtualRun":     "Virtual Run",
        "EBikeRide":      "E-Bike Ride",
        "WeightTraining": "Weight Training",
        "NordicSki":      "Nordic Ski",
        "RollerSki":      "Roller Ski",
        "IceSkate":       "Ice Skate",
        "StandUpPaddling":"Stand Up Paddling",
        "HandCycle":      "Hand Cycle",
        "RockClimbing":   "Rock Climbing",
    }
    df["sport"] = df["sport"].replace(sport_map)
    df["is_endurance"] = df["sport"].isin(ENDURANCE)
    return df

df = load_data()
_polylines = load_polylines()
oura_df    = load_oura()

# ── Sidebar ───────────────────────────────────────────────────────────────────
# ── Year filter state ────────────────────────────────────────────────────────
all_years = sorted(df["year"].dropna().unique().astype(int).tolist(), reverse=True)
if "selected_year" not in st.session_state:
    st.session_state["selected_year"] = "All"

with st.sidebar:
    st.markdown("## 🔥 Filters")
    st.markdown('<hr style="border:none;border-top:1px solid #e8e4de;margin:0.8rem 0">', unsafe_allow_html=True)

    # ── Year filter ──────────────────────────────────────────────────────────
    st.markdown("""<style>
div[data-testid='stSidebar'] .stSelectbox label {
    color: #666 !important;
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
div[data-testid='stSidebar'] .stSelectbox > div > div {
    background: #ffffff !important;
    border: 1px solid #e2ddd8 !important;
    border-radius: 10px !important;
    color: #333 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    transition: border-color 0.2s !important;
}
div[data-testid='stSidebar'] .stSelectbox > div > div:hover {
    border-color: #fc4c02 !important;
}
</style>""", unsafe_allow_html=True)
    year_options = ["All"] + [str(y) for y in all_years]
    current_idx  = year_options.index(st.session_state["selected_year"])
    chosen = st.selectbox("Year", year_options, index=current_idx,
                          key="year_select")
    if chosen != st.session_state["selected_year"]:
        st.session_state["selected_year"] = chosen
        st.rerun()

    st.markdown('<hr style="border:none;border-top:1px solid #e8e4de;margin:0.8rem 0">', unsafe_allow_html=True)
    all_sports = sorted(df["sport"].unique().tolist())
    selected_sports = st.multiselect("Sports", all_sports, default=all_sports)

    st.markdown('<hr style="border:none;border-top:1px solid #e8e4de;margin:0.8rem 0">', unsafe_allow_html=True)
    if st.button("🔄 Reload data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── Apply year filter ─────────────────────────────────────────────────────────
selected_year = st.session_state["selected_year"]
if selected_year == "All":
    start_date = df["date"].min().date()
    end_date   = df["date"].max().date()
else:
    yr_int     = int(selected_year)
    start_date = df[df["year"] == yr_int]["date"].min().date()
    end_date   = df[df["year"] == yr_int]["date"].max().date()

mask = (
    df["sport"].isin(selected_sports) &
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
)
fdf = df[mask].copy()
end = fdf[fdf["is_endurance"]]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-bottom:1.5rem">
  <div style="color:#fc4c02;font-size:0.75rem;font-weight:700;
              text-transform:uppercase;letter-spacing:0.12em;margin-bottom:4px">
    Personal Training Dashboard
  </div>
  <h1 style="margin:0;font-size:1.8rem;font-weight:800;letter-spacing:-0.03em;color:#1a1a1a">
    My Personal Fitness Dashboard
  </h1>
  <div style="color:#999;font-size:0.85rem;margin-top:4px">
    {'📅 ' + selected_year if selected_year != 'All' else df['date'].min().strftime('%b %Y') + ' — ' + df['date'].max().strftime('%b %Y') + ' · ' + str(df['year'].nunique()) + ' years'}
  </div>
</div>
""", unsafe_allow_html=True)



# ── Pre-compute CTL/ATL/TSB for use in AI section ───────────────────────────
_end2_pre = df[df["is_endurance"]].copy()
_end2_pre["tss"] = _end2_pre["rel_effort"].fillna(
    _end2_pre["moving_min"] * (_end2_pre["avg_hr"].fillna(130) / 150) ** 2 * 0.5)
_daily_pre = _end2_pre.groupby(_end2_pre["date"].dt.normalize())["tss"].sum().reset_index()
_daily_pre.columns = ["date","tss"]
_daily_pre["date"] = pd.to_datetime(_daily_pre["date"])
_full_pre = pd.date_range(_daily_pre["date"].min(), _daily_pre["date"].max(), freq="D")
_daily_pre = _daily_pre.set_index("date").reindex(_full_pre, fill_value=0).reset_index()
_daily_pre.columns = ["date","tss"]
_daily_pre["ctl"] = _daily_pre["tss"].ewm(span=42, adjust=False).mean()
_daily_pre["atl"] = _daily_pre["tss"].ewm(span=7,  adjust=False).mean()
_daily_pre["tsb"] = _daily_pre["ctl"] - _daily_pre["atl"]
_latest_pre = _daily_pre.iloc[-1]
_ctl = _latest_pre["ctl"]; _atl = _latest_pre["atl"]; _tsb = _latest_pre["tsb"]
if _tsb > 5:    _tsb_lbl = "Fresh"
elif _tsb > -10: _tsb_lbl = "Training"
elif _tsb > -20: _tsb_lbl = "Tired"
else:            _tsb_lbl = "Overloaded"

_ENDURANCE_PRE = {"Run","Ride","Virtual Ride","Virtual Run","Walk","Hike",
                  "Nordic Ski","Swim","Rowing","E-Bike Ride","Weight Training"}
_end_h_pre   = df[df["sport"].isin(_ENDURANCE_PRE)].copy()
_last_date_p = df["date"].max()
_wk_start_p  = _last_date_p.normalize() - pd.Timedelta(days=_last_date_p.dayofweek)
_prev_start_p= _wk_start_p - pd.Timedelta(weeks=1)
_this_h = _end_h_pre[_end_h_pre["date"] >= _wk_start_p]["moving_min"].sum() / 60
_last_h = _end_h_pre[(_end_h_pre["date"] >= _prev_start_p) &
                      (_end_h_pre["date"] < _wk_start_p)]["moving_min"].sum() / 60

# ── Latest activity card + analysis ──────────────────────────────────────────
latest_act = df.sort_values("date", ascending=False).iloc[0]
la_sport   = latest_act["sport"]
la_date    = latest_act["date"].strftime("%a %d %b %Y")
la_name    = latest_act["name"] if pd.notna(latest_act["name"]) else la_sport
la_dist    = latest_act["dist_km"]
la_mins    = latest_act["moving_min"]
la_elev_v  = latest_act["elev_gain_m"] if pd.notna(latest_act["elev_gain_m"]) else 0
la_hr_v    = latest_act["avg_hr"] if pd.notna(latest_act["avg_hr"]) else 0
la_effort  = latest_act["rel_effort"] if pd.notna(latest_act["rel_effort"]) else 0
la_cal     = latest_act["calories"] if pd.notna(latest_act["calories"]) else 0

la_dist_s  = f"{la_dist:.1f} km" if la_dist > 0 else ""
la_time_s  = f"{int(la_mins//60)}h {int(la_mins%60):02d}m" if la_mins > 0 else ""
la_elev_s  = f"{int(la_elev_v)} m↑" if la_elev_v > 0 else ""
la_hr_s    = f"{int(la_hr_v)} bpm" if la_hr_v > 0 else ""
la_cal_s   = f"{int(la_cal)} kcal" if la_cal > 0 else ""

# Pace / speed
if la_sport in ["Run","Walk","Virtual Run","Hike"] and la_dist > 0:
    _p = la_mins / la_dist
    la_pace_s = f"{int(_p)}:{int((_p%1)*60):02d} /km"
elif la_sport in ["Ride","Virtual Ride","E-Bike Ride"] and latest_act["avg_speed_ms"] > 0:
    la_pace_s = f"{latest_act['avg_speed_ms']*3.6:.1f} km/h"
else:
    la_pace_s = ""

stats_line = " · ".join(filter(None, [la_dist_s, la_time_s, la_pace_s, la_elev_s, la_hr_s, la_cal_s]))

# ── Historical comparisons for same sport ─────────────────────────────────────
same_sport = df[(df["sport"]==la_sport) & (df["dist_km"]>0)].copy()
same_runs  = df[(df["sport"]==la_sport) & (df["dist_km"]>1)].copy() if la_dist > 1 else same_sport

this_week_start = latest_act["date"].normalize() - pd.Timedelta(days=latest_act["date"].dayofweek)
last_week_start = this_week_start - pd.Timedelta(weeks=1)
month_ago_start = latest_act["date"] - pd.Timedelta(days=30)

# Week totals
this_wk_acts = df[df["date"] >= this_week_start]
last_wk_acts = df[(df["date"] >= last_week_start) & (df["date"] < this_week_start)]
this_wk_km   = this_wk_acts[this_wk_acts["sport"]==la_sport]["dist_km"].sum()
last_wk_km   = last_wk_acts[last_wk_acts["sport"]==la_sport]["dist_km"].sum()
this_wk_h    = this_wk_acts["moving_min"].sum() / 60
last_wk_h    = last_wk_acts["moving_min"].sum() / 60

# Recent 30-day avg session for this sport
recent_same  = same_sport[same_sport["date"] >= month_ago_start]
avg_dist_30  = recent_same["dist_km"].mean() if len(recent_same) > 0 else 0
avg_hr_30    = recent_same["avg_hr"].mean() if len(recent_same) > 0 else 0

# Effort intensity label
effort_lbl = ""
if la_effort > 0:
    if la_effort < 30:   effort_lbl, effort_col = "Easy", "#50c850"
    elif la_effort < 70: effort_lbl, effort_col = "Moderate", "#ffa500"
    elif la_effort < 120:effort_lbl, effort_col = "Hard", "#ff6b35"
    else:                effort_lbl, effort_col = "Max effort", "#ff4444"
else:
    effort_lbl, effort_col = "", "#888"

# Pace comparison vs 30-day avg (runs only)
pace_insight = ""
if la_sport in ["Run","Walk"] and la_dist > 1 and avg_dist_30 > 0:
    la_pace_v  = la_mins / la_dist if la_dist > 0 else 0
    recent_same["pace"] = recent_same["moving_min"] / recent_same["dist_km"].replace(0, np.nan)
    avg_pace_30 = recent_same["pace"].mean()
    if la_pace_v > 0 and avg_pace_30 > 0:
        pace_diff = la_pace_v - avg_pace_30
        if abs(pace_diff) > 0.1:
            faster = pace_diff < 0
            pace_insight = f"{'⚡ ' if faster else '🐢 '}{abs(pace_diff*60):.0f}s/km {'faster' if faster else 'slower'} than your 30-day avg"

# HR zone context
hr_insight = ""
if la_hr_v > 0:
    max_hr_est = 220 - 35  # rough estimate, adjust if known
    hr_pct = la_hr_v / max_hr_est * 100
    if hr_pct < 60:    hr_insight = "Zone 1 · Recovery pace"
    elif hr_pct < 70:  hr_insight = "Zone 2 · Aerobic base"
    elif hr_pct < 80:  hr_insight = "Zone 3 · Aerobic power"
    elif hr_pct < 90:  hr_insight = "Zone 4 · Threshold"
    else:              hr_insight = "Zone 5 · Max effort"

# Weekly context
wk_delta_km  = this_wk_km - last_wk_km
wk_arrow     = "▲" if wk_delta_km >= 0 else "▼"
wk_col       = "#50c850" if wk_delta_km >= 0 else "#ff5555"
wk_pct       = abs(wk_delta_km / last_wk_km * 100) if last_wk_km > 0 else 0

# Build insight bullets
insights = []
if pace_insight:               insights.append(("⚡", pace_insight))
if hr_insight and la_hr_v > 0:insights.append(("❤️", f"{int(la_hr_v)} bpm · {hr_insight}"))
if effort_lbl:                 insights.append(("💪", f"Effort: {effort_lbl}"))
if last_wk_km > 0:             insights.append(("📅", f"This week: {this_wk_km:.0f} km — {wk_arrow} {abs(wk_delta_km):.0f} km ({wk_pct:.0f}%) vs last week"))
if la_dist > 0 and avg_dist_30 > 0:
    vs = "longer" if la_dist > avg_dist_30 else "shorter"
    insights.append(("📏", f"{abs(la_dist - avg_dist_30):.1f} km {vs} than your 30-day avg session ({avg_dist_30:.1f} km)"))
if la_elev_v > 100:
    insights.append(("⛰️", f"{int(la_elev_v)} m elevation — {'hilly' if la_elev_v/la_dist > 15 else 'moderate climb'}" if la_dist > 0 else f"{int(la_elev_v)} m elevation"))

insight_html = "".join([
    f'<div style="display:flex;gap:8px;align-items:flex-start;margin-bottom:5px">'
    f'<span style="font-size:0.85rem;min-width:20px">{ico}</span>'
    f'<span style="color:#555555;font-size:0.78rem;line-height:1.4">{txt}</span>'
    f'</div>'
    for ico, txt in insights
]) if insights else '<div style="color:#555;font-size:0.78rem">No analysis data available</div>'

# Pre-compute values for the card to avoid quote conflicts in f-string
_la_id     = int(latest_act["activity_id"])
_la_spd    = f"{latest_act['avg_speed_ms']*3.6:.1f} km/h" if la_sport in ["Ride","Virtual Ride","E-Bike Ride"] and latest_act["avg_speed_ms"] > 0 else ""
_strava_url = f"https://www.strava.com/activities/{_la_id}"

# Rebuild stats line with precomputed speed
if _la_spd:
    stats_line = " · ".join(filter(None, [la_dist_s, la_time_s, _la_spd, la_elev_s, la_hr_s, la_cal_s]))
# (else stats_line already set above)

_wk_d    = this_wk_km - last_wk_km
_wk_arr  = "▲" if _wk_d >= 0 else "▼"
_wk_col  = "#50c850" if _wk_d >= 0 else "#ff5555"
_wk_badge = f'<span style="color:{_wk_col};font-weight:600">{_wk_arr} {abs(_wk_d):.1f} km vs last week</span>' if last_wk_km > 0 else ""

_insights = [i for i in [pace_insight, hr_insight] if i]

_effort_html = f'<div style="background:{effort_col}22;border:1px solid {effort_col}44;color:{effort_col};font-size:0.7rem;font-weight:600;padding:3px 10px;border-radius:999px">{effort_lbl}</div>' if effort_lbl else ""

# Pre-build HTML fragments to avoid nested f-strings/quotes
_ins_html = ""
for _ins in _insights:
    # Show full insight string — no character splitting
    _ins_html += (
        '<div style="display:flex;gap:8px;align-items:flex-start;margin-bottom:5px">' +
        f'<span style="color:#999;font-size:0.78rem;line-height:1.4">{_ins}</span></div>'
    )

_card_left = (
    f'<div style="color:#999;font-size:0.62rem;font-weight:600;text-transform:uppercase;' +
    f'letter-spacing:0.1em;margin-bottom:4px">Latest activity · {la_date}</div>' +
    f'<div style="color:#ffffff;font-size:1.15rem;font-weight:700;margin-bottom:6px">{la_name}</div>' +
    f'<div style="color:#888;font-size:0.82rem;margin-bottom:10px">{stats_line}</div>' +
    f'<div style="border-top:1px solid #e8e4de;padding-top:10px">{_ins_html}</div>'
)

_card_right = (
    f'<div style="background:#fc4c02;color:#fff;font-size:0.62rem;font-weight:700;' +
    f'text-transform:uppercase;letter-spacing:0.1em;padding:4px 12px;border-radius:999px">{la_sport}</div>' +
    (_effort_html) +
    f'<div style="font-size:0.78rem;text-align:right">{_wk_badge}</div>' +
    f'<a href="{_strava_url}" target="_blank" ' +
    f'style="color:#fc4c02;font-size:0.7rem;text-decoration:none;font-weight:600;' +
    f'border:1px solid #fc4c02;padding:3px 10px;border-radius:6px;margin-top:4px">View on Strava ↗</a>'
)

# (activity card now shown inline with map below)

# ── Latest activity map + info side by side ──────────────────────────────────
_la_poly = _polylines.get(str(int(latest_act["activity_id"])), "")
if _la_poly:
    _la_coords = decode_polyline(_la_poly)
    if _la_coords:
        try:
            import folium
            from streamlit_folium import st_folium
            _c1, _c2 = st.columns([1, 1])
            with _c1:
                _effort_tag = (
                    '<span style="background:#f0fdf0;border:1px solid #86efac;color:#16a34a;'
                    'font-size:0.7rem;font-weight:600;padding:2px 8px;border-radius:999px">'
                    + effort_lbl + '</span>'
                ) if effort_lbl else ""
                st.markdown(
                    '<div style="background:#ffffff;border:1px solid #e2ddd8;border-radius:12px;'
                    'padding:1.2rem;height:220px;display:flex;flex-direction:column;justify-content:space-between;'
                    'box-shadow:0 1px 4px rgba(0,0,0,0.06)">'
                    '<div>'
                    + f'<div style="color:#999;font-size:0.62rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px">{la_sport} · {la_date}</div>'
                    + f'<div style="color:#1a1a1a;font-size:1.2rem;font-weight:700;margin-bottom:8px">{la_name}</div>'
                    + f'<div style="color:#555;font-size:0.82rem;line-height:1.8">{stats_line}</div>'
                    + '</div>'
                    + f'<div style="display:flex;align-items:center;justify-content:space-between;margin-top:8px;padding-top:8px;border-top:1px solid #f0ede8">'
                    + _effort_tag
                    + f'<a href="{_strava_url}" target="_blank" style="color:#fc4c02;font-size:0.75rem;font-weight:600;text-decoration:none">View on Strava ↗</a>'
                    + '</div></div>',
                    unsafe_allow_html=True
                )
            with _c2:
                st_folium(make_folium_map(_la_coords, height=220),
                          use_container_width=True, height=220,
                          returned_objects=[], key="latest_map")
        except ImportError:
            st.caption("Add folium and streamlit-folium to requirements.txt for route maps.")

# ── AI Athlete Intelligence ──────────────────────────────────────────────────
def get_ai_analysis(api_key, sport, name, dist, mins, elev, hr, effort_lbl,
                    pace_s, ctl, atl, tsb, tsb_lbl,
                    wk_km, last_wk_km, avg_dist_30, this_wk_h, last_wk_h,
                    recent_sports_str, days_since_rest,
                    oura_readiness=None, oura_hrv=None, oura_hrv_avg=None,
                    oura_rhr=None, oura_sleep=None, oura_sleep_h=None, oura_temp=None):
    """Call Claude to generate activity analysis + next session recommendation."""
    import requests as _req
    import json as _json

    hrs  = int(mins // 60)
    mns  = int(mins % 60)
    time_str = f"{hrs}h {mns:02d}m" if hrs > 0 else f"{mns}m"
    wk_delta = wk_km - last_wk_km
    h_delta  = this_wk_h - last_wk_h

    prompt = f"""You are a personal endurance sports coach analysing an athlete's training data.

LATEST ACTIVITY:
- Sport: {sport}
- Name: {name}
- Distance: {dist:.1f} km
- Duration: {time_str}
- Elevation: {elev:.0f} m
- Avg HR: {hr:.0f} bpm
- Pace/Speed: {pace_s}
- Effort: {effort_lbl if effort_lbl else 'Unknown'}

TRAINING LOAD (right now):
- CTL (fitness, 42-day): {ctl:.1f}
- ATL (fatigue, 7-day): {atl:.1f}
- TSB (form): {tsb:+.1f} ({tsb_lbl})
- This week: {this_wk_h:.1f}h ({wk_delta:+.1f} km vs last week)
- 30-day avg session distance for {sport}: {avg_dist_30:.1f} km
- Days since last full rest day: {days_since_rest}
- Recent sports mix (last 14 days): {recent_sports_str}

Write TWO short sections:

1. ACTIVITY ANALYSIS (2-3 sentences): What does this specific activity tell us? Comment on effort level, how it compares to recent training, HR zone, and anything notable. Be specific and use the numbers.

2. RECOMMENDED NEXT SESSION (2-3 sentences): Based on TSB, fatigue, and training mix, what should this athlete do FOR THEIR NEXT SESSION (not tomorrow — the very next time they train)? Be specific — name the sport, rough duration, intensity zone, and the reason. Do not mention days of the week or "tomorrow" — say "next session" or "next workout" instead.

Keep both sections concise and direct. No bullet points. No headers in your response — just two paragraphs separated by a blank line. Write like a knowledgeable coach, not a generic fitness bot."""

    if any(v is not None for v in [oura_readiness, oura_hrv, oura_rhr, oura_sleep]):
        oura_ctx = "\n\nRECOVERY DATA (Oura Ring — last night):"
        if oura_readiness: oura_ctx += f"\n- Readiness: {oura_readiness:.0f}/100"
        if oura_hrv and oura_hrv_avg: oura_ctx += f"\n- HRV: {oura_hrv:.0f} ms (7d avg: {oura_hrv_avg:.0f} ms, {'above' if oura_hrv >= oura_hrv_avg else 'below'} average)"
        elif oura_hrv: oura_ctx += f"\n- HRV: {oura_hrv:.0f} ms"
        if oura_rhr:    oura_ctx += f"\n- Resting HR: {oura_rhr:.0f} bpm"
        if oura_sleep:  oura_ctx += f"\n- Sleep score: {oura_sleep:.0f}/100"
        if oura_sleep_h: oura_ctx += f"\n- Sleep: {int(oura_sleep_h//60)}h {int(oura_sleep_h%60):02d}m"
        if oura_temp:   oura_ctx += f"\n- Body temp: {oura_temp:+.2f}°C vs baseline"
        oura_ctx += "\n\nWeight the recovery data heavily. If readiness < 70 or HRV is below 7d average, recommend easy or rest regardless of TSB."
        prompt += oura_ctx

    try:
        resp = _req.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=20
        )
        if resp.status_code == 200:
            return resp.json()["content"][0]["text"].strip()
        else:
            return f"ERROR {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return f"EXCEPTION: {str(e)[:200]}"

# Compute inputs for AI
_recent_14 = df[df["date"] >= (df["date"].max() - pd.Timedelta(days=14))]
_recent_sports = _recent_14["sport"].value_counts().head(4)
_recent_sports_str = ", ".join([f"{s} ({c}x)" for s, c in _recent_sports.items()])

# Days since last rest (no activity)
_sorted_dates = sorted(df["date"].dt.normalize().unique(), reverse=True)
_days_since_rest = 0
_seen = set()
for _d in _sorted_dates:
    if _d in _seen:
        continue
    _seen.add(_d)
    if _days_since_rest == 0:
        _days_since_rest += 1
        continue
    _prev = _d + pd.Timedelta(days=1)
    if _prev in _seen:
        _days_since_rest += 1
    else:
        break

_ai_text = None

# Check API key is available
_api_key = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""

if not _api_key:
    st.markdown(
        '<div style="background:#fff8f5;border:1px solid #fce0d0;border-left:4px solid #fc4c02;' +
        'border-radius:10px;padding:1rem 1.2rem;margin-bottom:1rem;color:#888;font-size:0.82rem">' +
        '✦ Add <code>ANTHROPIC_API_KEY</code> to Streamlit secrets to enable athlete intelligence.' +
        '</div>',
        unsafe_allow_html=True
    )
else:
    # Use session state to cache only successful responses
    _cache_key = f"ai_{int(latest_act['activity_id'])}"
    if _cache_key not in st.session_state:
        with st.spinner("✦ Generating athlete intelligence..."):
            st.session_state[_cache_key] = get_ai_analysis(
                _api_key, la_sport, la_name, la_dist, la_mins, la_elev_v, la_hr_v,
                effort_lbl, la_pace_s,
                _ctl, _atl, _tsb, _tsb_lbl,
                this_wk_km, last_wk_km, avg_dist_30,
                _this_h, _last_h,
                _recent_sports_str, _days_since_rest
            )
            # Don't cache errors
            if st.session_state[_cache_key] and (
                st.session_state[_cache_key].startswith("ERROR") or
                st.session_state[_cache_key].startswith("EXCEPTION")):
                _ai_text = st.session_state[_cache_key]
                del st.session_state[_cache_key]
            else:
                _ai_text = st.session_state[_cache_key]
    else:
        _ai_text = st.session_state[_cache_key]
    if not _ai_text or _ai_text.startswith("ERROR") or _ai_text.startswith("EXCEPTION"):
        _err = _ai_text or "No response"
        st.markdown(
            '<div style="background:#ffffff;border:1px solid #e2ddd8;border-left:3px solid #ff5555;' +
            'border-radius:10px;padding:1rem 1.2rem;margin-bottom:1rem;color:#888;font-size:0.82rem">' +
            f'✦ API error: {_err}' +
            '</div>',
            unsafe_allow_html=True
        )
        _ai_text = None

if _api_key and _ai_text:
    _paras = [p.strip() for p in _ai_text.split("\n\n") if p.strip()]
    _analysis  = _paras[0] if len(_paras) > 0 else ""
    _recommend = _paras[1] if len(_paras) > 1 else ""

    st.markdown(
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:1rem">'
        + '<div style="background:#fff8f5;border:1px solid #fce0d0;border-left:4px solid #fc4c02;'
        + 'border-radius:10px;padding:1rem 1.2rem">'
        + '<div style="color:#fc4c02;font-size:0.62rem;font-weight:700;text-transform:uppercase;'
        + 'letter-spacing:0.1em;margin-bottom:8px">✦ Activity Analysis</div>'
        + f'<div style="color:#333;font-size:0.85rem;line-height:1.6">{_analysis}</div>'
        + '</div>'
        + '<div style="background:#f5fbf5;border:1px solid #c8ecc8;border-left:4px solid #50c850;'
        + 'border-radius:10px;padding:1rem 1.2rem">'
        + '<div style="color:#50c850;font-size:0.62rem;font-weight:700;text-transform:uppercase;'
        + 'letter-spacing:0.1em;margin-bottom:8px">▶ Recommended Next Session</div>'
        + f'<div style="color:#333;font-size:0.85rem;line-height:1.6">{_recommend}</div>'
        + '</div>'
        + '</div>',
        unsafe_allow_html=True
    )

# ══════════════════════════════════════════════════════════════════════════════
# TOP DASHBOARD — Two column summary + Progress rings
# ══════════════════════════════════════════════════════════════════════════════

# Compute CTL/ATL/TSB for summary
_end2 = df[df["is_endurance"]].copy()
_end2["tss"] = _end2["rel_effort"].fillna(
    _end2["moving_min"] * (_end2["avg_hr"].fillna(130) / 150) ** 2 * 0.5)
_daily = _end2.groupby(_end2["date"].dt.normalize())["tss"].sum().reset_index()
_daily.columns = ["date","tss"]
_daily["date"] = pd.to_datetime(_daily["date"])
_full = pd.date_range(_daily["date"].min(), _daily["date"].max(), freq="D")
_daily = _daily.set_index("date").reindex(_full, fill_value=0).reset_index()
_daily.columns = ["date","tss"]
_daily["ctl"] = _daily["tss"].ewm(span=42, adjust=False).mean()
_daily["atl"] = _daily["tss"].ewm(span=7,  adjust=False).mean()
_daily["tsb"] = _daily["ctl"] - _daily["atl"]
_latest = _daily.iloc[-1]
_ctl = _latest["ctl"]; _atl = _latest["atl"]; _tsb = _latest["tsb"]

# Week-over-week hours
_ENDURANCE_H = {"Run","Ride","Virtual Ride","Virtual Run","Walk","Hike",
                "Nordic Ski","Swim","Rowing","E-Bike Ride","Weight Training","Workout"}
_end_h = df[df["sport"].isin(_ENDURANCE_H)].copy()
_last_date  = df["date"].max()
_wk_start   = _last_date.normalize() - pd.Timedelta(days=_last_date.dayofweek)
_prev_start = _wk_start - pd.Timedelta(weeks=1)
_this_h = _end_h[_end_h["date"] >= _wk_start]["moving_min"].sum() / 60
_last_h = _end_h[(_end_h["date"] >= _prev_start) & (_end_h["date"] < _wk_start)]["moving_min"].sum() / 60
_dh = _this_h - _last_h
_dh_col = "#50c850" if _dh >= 0 else "#ff5555"
_dh_arrow = "▲" if _dh >= 0 else "▼"
_this_hm = int(_this_h); _this_mm = int((_this_h%1)*60)
_dh_hm   = int(abs(_dh)); _dh_mm   = int((abs(_dh)%1)*60)

# 2026 progress targets
RUN_TARGET  = 800   # km
RIDE_TARGET = 3000  # km
_run_2026  = df[(df["date"].dt.year==2026) & (df["sport"]=="Run")]["dist_km"].sum()
_ride_2026 = df[(df["date"].dt.year==2026) & df["sport"].isin(["Ride","Virtual Ride","E-Bike Ride"])]["dist_km"].sum()
_run_pct   = min(_run_2026 / RUN_TARGET * 100, 100)
_ride_pct  = min(_ride_2026 / RIDE_TARGET * 100, 100)

def _ring_svg(pct, label, current, target, unit, color="#fc4c02", r=72):
    """SVG progress ring — full height to match left cards."""
    circ  = 2 * 3.14159 * r
    dash  = circ * pct / 100
    gap   = circ - dash
    remaining = target - current
    remaining_str = f"{remaining:.0f} {unit} to go" if pct < 100 else "Goal reached! 🎉"
    return f"""
<svg width="100%" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg">
  <circle cx="90" cy="90" r="{r}" fill="none" stroke="#e8e4de" stroke-width="10"/>
  <circle cx="90" cy="90" r="{r}" fill="none" stroke="{color}" stroke-width="10"
    stroke-dasharray="{dash:.1f} {gap:.1f}"
    stroke-dashoffset="{circ*0.25:.1f}"
    stroke-linecap="round"/>
  <text x="90" y="80" text-anchor="middle" fill="#1a1a1a"
    font-size="26" font-weight="700" font-family="DM Mono,monospace">{current:.0f}</text>
  <text x="90" y="100" text-anchor="middle" fill="#666"
    font-size="13" font-family="DM Sans,sans-serif">{unit} of {target}</text>
  <text x="90" y="122" text-anchor="middle" fill="{color}"
    font-size="15" font-weight="700" font-family="DM Sans,sans-serif">{pct:.0f}%</text>
  <text x="90" y="143" text-anchor="middle" fill="#555"
    font-size="11" font-family="DM Sans,sans-serif">{remaining_str}</text>
</svg>"""

# TSB colour and label
if _tsb > 5:
    _tsb_col, _tsb_lbl = "#50c850", "Fresh"
elif _tsb > -10:
    _tsb_col, _tsb_lbl = "#ffa500", "Training"
elif _tsb > -20:
    _tsb_col, _tsb_lbl = "#ff6b35", "Tired"
else:
    _tsb_col, _tsb_lbl = "#ff4444", "Overloaded"

# ── Two column top dashboard ──────────────────────────────────────────────────
# Trend: compare today vs 7 days ago
_week_ago = _daily.iloc[-8] if len(_daily) >= 8 else _daily.iloc[0]
_ctl_d = _ctl - _week_ago["ctl"]
_atl_d = _atl - _week_ago["atl"]
_tsb_d = _tsb - _week_ago["tsb"]

def _trend(delta, invert=False):
    good = delta < 0 if invert else delta > 0
    col  = "#50c850" if good else "#ff5555"
    arr  = "▲" if delta > 0.05 else "▼" if delta < -0.05 else "—"
    return arr, col, abs(delta)

ctl_arr, ctl_col, ctl_chg = _trend(_ctl_d)
atl_arr, atl_col, atl_chg = _trend(_atl_d, invert=True)
tsb_arr, tsb_col, tsb_chg = _trend(_tsb_d)

ring_run  = _ring_svg(_run_pct,  "Running",  _run_2026,  RUN_TARGET,  "km", "#fc4c02")
ring_ride = _ring_svg(_ride_pct, "Cycling", _ride_2026, RIDE_TARGET, "km", "#ffa500")

# Single HTML block — all 6 cards in one CSS grid so heights match perfectly
st.markdown(f"""
<style>
.dash-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr 1.4fr 1.4fr;
    grid-template-rows: 145px 145px;
    gap: 10px;
    width: 100%;
}}
.dash-card {{
    background: #ffffff;
    border: 1px solid #e2ddd8;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    border-radius: 10px;
    padding: 18px 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
}}
.dash-card:hover .card-tooltip {{
    display: block;
}}
.card-label {{
    color: #bbb;
    font-size: 0.6rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}
.card-value {{
    font-size: 2.2rem;
    font-weight: 700;
    font-family: 'DM Mono', monospace;
    line-height: 1;
    color: #1a1a1a;
}}
.card-sub {{
    font-size: 0.7rem;
    color: #aaa;
    margin-top: 5px;
}}
.card-trend {{
    font-size: 0.7rem;
    font-weight: 600;
    position: absolute;
    top: 16px;
    right: 16px;
}}
.card-tooltip {{
    display: none;
    position: absolute;
    bottom: calc(100% + 8px);
    left: 50%;
    transform: translateX(-50%);
    background: #ffffff;
    border: 1px solid #fc4c02;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.75rem;
    color: #ffffff;
    width: 220px;
    z-index: 999;
    line-height: 1.5;
    text-align: left;
    box-shadow: 0 4px 20px rgba(0,0,0,0.12);
}}
.ring-card {{
    background: #ffffff;
    border: 1px solid #e8e4de;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 12px 8px 8px;
    grid-row: 1 / 3;
}}
.ring-label {{
    color: #bbb;
    font-size: 0.6rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 4px;
}}
</style>

<div class="dash-grid">

  
  <div class="dash-card" style="grid-column:1; grid-row:1">
    <div class="card-label">CTL · Fitness</div>
    <div class="card-trend" style="color:{ctl_col}">{ctl_arr} {ctl_chg:.1f}</div>
    <div>
      <div class="card-value">{_ctl:.1f}</div>
      <div class="card-sub">42-day fitness base</div>
    </div>
    <div class="card-tooltip">
      <b>Chronic Training Load</b><br>
      Your long-term fitness level.<br><br>
      {'🟢 Good base — ready to build on.' if _ctl >= 60 else '🟡 Moderate fitness — keep consistent.' if _ctl >= 30 else '🔴 Low base — focus on building volume.'}
    </div>
  </div>

  
  <div class="dash-card" style="grid-column:2; grid-row:1">
    <div class="card-label">ATL · Fatigue</div>
    <div class="card-trend" style="color:{atl_col}">{atl_arr} {atl_chg:.1f}</div>
    <div>
      <div class="card-value">{_atl:.1f}</div>
      <div class="card-sub">7-day fatigue load</div>
    </div>
    <div class="card-tooltip">
      <b>Acute Training Load</b><br>
      Your recent fatigue from training.<br><br>
      {'🔴 High fatigue — prioritise recovery.' if _atl > 80 else '🟡 Moderate fatigue — ease tomorrow.' if _atl > 40 else '🟢 Low fatigue — body is fresh.'}
    </div>
  </div>

  
  <div class="dash-card" style="grid-column:1; grid-row:2">
    <div class="card-label">TSB · Form</div>
    <div class="card-trend" style="color:{tsb_col}">{tsb_arr} {tsb_chg:.1f}</div>
    <div>
      <div class="card-value" style="color:{_tsb_col}">{_tsb:+.1f}</div>
      <div class="card-sub" style="color:{_tsb_col};font-weight:600">{_tsb_lbl}</div>
    </div>
    <div class="card-tooltip">
      <b>Training Stress Balance</b><br>
      Fitness minus fatigue = form.<br><br>
      {'🏆 Peaked — race or PB attempt.' if _tsb > 15 else '🟢 Fresh — ideal for hard session.' if _tsb > 5 else '🟡 Building — tempo or intervals ok.' if _tsb > -10 else '🟠 Tired — keep it easy today.' if _tsb > -20 else '🔴 Overloaded — rest day needed.'}
    </div>
  </div>

  
  <div class="dash-card" style="grid-column:2; grid-row:2">
    <div class="card-label">This week</div>
    <div>
      <div class="card-value">{_this_hm}h&nbsp;{_this_mm:02d}m</div>
      <div style="display:flex;align-items:center;gap:6px;margin-top:5px">
        <span style="color:{_dh_col};font-size:0.82rem;font-weight:700">{_dh_arrow} {_dh_hm}h {_dh_mm:02d}m</span>
        <span style="color:#999;font-size:0.72rem">vs last week</span>
      </div>
    </div>
  </div>

  
  <div class="ring-card" style="grid-column:3; grid-row:1/3">
    <div class="ring-label">🏃 2026 Running</div>
    {ring_run}
  </div>

  
  <div class="ring-card" style="grid-column:4; grid-row:1/3">
    <div class="ring-label">🚴 2026 Cycling</div>
    {ring_ride}
  </div>

</div>
""", unsafe_allow_html=True)
st.markdown('<hr style="border:none;border-top:1px solid #e8e4de;margin:0.5rem 0">', unsafe_allow_html=True)

# ── Oura Recovery ─────────────────────────────────────────────────────────────
if not oura_df.empty:
    st.markdown('<h2 style="margin-top:0.5rem!important">Recovery & Readiness</h2>', unsafe_allow_html=True)

    def osafe(row, col):
        try: v = row[col]; return float(v) if pd.notna(v) else None
        except: return None

    today_o  = oura_df.iloc[0]
    recent_7 = oura_df.head(7)
    recent_30= oura_df.head(30).sort_values("date")

    o_ready  = osafe(today_o, "readiness_score")
    o_hrv    = osafe(today_o, "hrv_avg")
    o_rhr    = osafe(today_o, "resting_hr")
    o_sleep  = osafe(today_o, "sleep_score")
    o_sleep_h= osafe(today_o, "total_sleep_min")
    o_deep   = osafe(today_o, "deep_sleep_min")
    o_temp   = osafe(today_o, "temperature_deviation")
    o_resp   = osafe(today_o, "respiratory_rate")

    hrv_7avg = recent_7["hrv_avg"].dropna().mean() if "hrv_avg" in recent_7.columns else None
    rhr_7avg = recent_7["resting_hr"].dropna().mean() if "resting_hr" in recent_7.columns else None
    hrv_d    = (o_hrv - hrv_7avg) if o_hrv and hrv_7avg else None
    rhr_d    = (o_rhr - rhr_7avg) if o_rhr and rhr_7avg else None

    def scol(v, hi=85, lo=70):
        if v is None: return "#666"
        return "#50c850" if v >= hi else "#ffa500" if v >= lo else "#ff5555"

    def trend_badge(delta, invert=False, unit=""):
        if delta is None: return ""
        good = delta < 0 if invert else delta > 0
        col  = "#50c850" if good else "#ff5555"
        arr  = "▲" if delta > 0.05 else "▼" if delta < -0.05 else "—"
        return f'<span style="color:{col};font-weight:600">{arr} {abs(delta):.1f}{unit}</span>'

    if o_ready is not None:
        if o_ready >= 85:   rmsg = "Optimal — peak performance window"
        elif o_ready >= 70: rmsg = "Good — normal training"
        elif o_ready >= 60: rmsg = "Fair — keep intensity moderate"
        else:               rmsg = "Low — prioritise recovery today"
    else: rmsg = ""

    sleep_str = f"{int(o_sleep_h//60)}h {int(o_sleep_h%60):02d}m" if o_sleep_h else "—"
    deep_str  = f"{int(o_deep//60)}h {int(o_deep%60):02d}m" if o_deep else "—"
    temp_col  = "#ff5555" if o_temp and abs(o_temp) > 0.5 else "#ffa500" if o_temp and abs(o_temp) > 0.2 else "#50c850"

    def sparkline_svg(values, color, width=90, height=36):
        """Inline SVG sparkline with all data points shown."""
        vals = [v for v in values if v is not None and not (isinstance(v, float) and v != v)]
        if len(vals) < 2:
            return ""
        mn, mx = min(vals), max(vals)
        rng = mx - mn if mx != mn else 1
        pts = []
        for i, v in enumerate(vals):
            x = round(i / (len(vals)-1) * width, 1)
            y = round((1 - (v - mn) / rng) * (height - 6)) + 3
            pts.append((x, y))
        path = " ".join(f"{x},{y}" for x,y in pts)
        # Area fill
        area = f"0,{height} " + path + f" {width},{height}"
        circles = "".join(
            f'<circle cx="{x}" cy="{y}" r="2" fill="#ffffff" stroke="{color}" stroke-width="1.2"/>' 
            for x,y in pts
        )
        # Last point larger + filled
        xn, yn = pts[-1]
        return (
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" ' +
            'xmlns="http://www.w3.org/2000/svg">' +
            f'<polygon points="{area}" fill="{color}" opacity="0.08"/>' +
            f'<polyline points="{path}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>' +
            circles +
            f'<circle cx="{xn}" cy="{yn}" r="3" fill="{color}"/>' +
            '</svg>'
        )

    # Build 7-day sparkline data
    _spark_ready = list(reversed(recent_7["readiness_score"].tolist())) if "readiness_score" in recent_7.columns else []
    _spark_hrv   = list(reversed(recent_7["hrv_avg"].tolist())) if "hrv_avg" in recent_7.columns else []
    _spark_rhr   = list(reversed(recent_7["resting_hr"].tolist())) if "resting_hr" in recent_7.columns else []
    _spark_sleep = list(reversed(recent_7["sleep_score"].tolist())) if "sleep_score" in recent_7.columns else []

    def oura_card(label, value_html, sub, spark_vals, spark_color, border_color=None):
        """Compact Oura card: label top-left, sparkline top-right, big value, sub text."""
        border = f"border-left:3px solid {border_color};" if border_color else ""
        spark  = sparkline_svg(spark_vals, spark_color, width=90, height=36)
        return (
            f'<div style="background:#ffffff;border:1px solid #e2ddd8;{border}border-radius:12px;padding:14px 16px;box-shadow:0 1px 4px rgba(0,0,0,0.05)">' +
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:2px">' +
            f'<div style="color:#999;font-size:0.6rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;padding-top:2px">{label}</div>' +
            f'<div>{spark}</div>' +
            '</div>' +
            f'<div style="margin:4px 0 6px">{value_html}</div>' +
            f'<div style="color:#999;font-size:0.7rem">{sub}</div>' +
            '</div>'
        )

    html_oura = (
        '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:10px">'
        + oura_card("Readiness",
            f'<span style="color:{scol(o_ready)};font-size:2rem;font-weight:700;font-family:DM Mono,monospace">{int(o_ready) if o_ready else "—"}</span>',
            rmsg, _spark_ready, scol(o_ready), border_color=None)
        + oura_card("HRV",
            f'<span style="color:#a78bfa;font-size:2rem;font-weight:700;font-family:DM Mono,monospace">{int(o_hrv) if o_hrv else "—"}</span><span style="color:#999;font-size:0.85rem"> ms</span>',
            f'{trend_badge(hrv_d, unit=" ms")} vs 7d avg', _spark_hrv, "#a78bfa")
        + oura_card("Resting HR",
            f'<span style="color:#1a1a1a;font-size:2rem;font-weight:700;font-family:DM Mono,monospace">{int(o_rhr) if o_rhr else "—"}</span><span style="color:#999;font-size:0.85rem"> bpm</span>',
            f'{trend_badge(rhr_d, invert=True, unit=" bpm")} vs 7d avg', _spark_rhr, "#fc4c02")
        + oura_card("Sleep",
            f'<span style="color:{scol(o_sleep)};font-size:2rem;font-weight:700;font-family:DM Mono,monospace">{int(o_sleep) if o_sleep else "—"}</span>',
            f'{sleep_str} · {deep_str} deep', _spark_sleep, scol(o_sleep))
        + '</div>'

        + '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">'
        + f'<div style="background:#ffffff;border:1px solid #e8e4de;border-radius:10px;padding:14px 16px">'
        + f'<div style="color:#999;font-size:0.6rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em">Body Temp</div>'
        + f'<div style="color:{temp_col};font-size:1.5rem;font-weight:700;font-family:DM Mono,monospace;margin-top:4px">{f"{o_temp:+.2f}°C" if o_temp is not None else "—"}</div>'
        + f'<div style="color:#888;font-size:0.7rem;margin-top:2px">deviation from baseline</div></div>'

        + f'<div style="background:#ffffff;border:1px solid #e8e4de;border-radius:10px;padding:14px 16px">'
        + f'<div style="color:#999;font-size:0.6rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em">Respiratory Rate</div>'
        + f'<div style="color:#1a1a1a;font-size:1.5rem;font-weight:700;font-family:DM Mono,monospace;margin-top:4px">{f"{o_resp:.1f}" if o_resp else "—"} br/min</div>'
        + f'<div style="color:#888;font-size:0.7rem;margin-top:2px">avg during sleep</div></div>'

        + f'<div style="background:#ffffff;border:1px solid #e8e4de;border-radius:10px;padding:14px 16px">'
        + f'<div style="color:#999;font-size:0.6rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em">Activity Score</div>'
        + f'<div style="color:{scol(osafe(today_o,"activity_score"))};font-size:1.5rem;font-weight:700;font-family:DM Mono,monospace;margin-top:4px">{int(osafe(today_o,"activity_score")) if osafe(today_o,"activity_score") is not None else "—"}</div>'
        + f'<div style="color:#888;font-size:0.7rem;margin-top:2px">Daily activity balance</div></div>'
        + '</div>'
    )

    st.markdown(html_oura, unsafe_allow_html=True)

    # 30-day HRV + RHR trend chart
    chart_o = recent_30[["date","hrv_avg","resting_hr"]].copy()
    chart_o = chart_o[chart_o["hrv_avg"].notna() | chart_o["resting_hr"].notna()]

    if len(chart_o) > 3:
        chart_o["hrv_roll"] = chart_o["hrv_avg"].rolling(7, min_periods=1).mean()
        fig_o = go.Figure()
        fig_o.add_trace(go.Bar(
            x=chart_o["date"], y=chart_o["hrv_avg"].round(1), name="HRV",
            marker=dict(color="rgba(167,139,250,0.4)", line=dict(width=0)),
            hovertemplate="<b>%{x|%d %b}</b><br>HRV: <b>%{y:.0f} ms</b><extra></extra>"))
        fig_o.add_trace(go.Scatter(
            x=chart_o["date"], y=chart_o["hrv_roll"].round(1), name="HRV 7d avg",
            mode="lines", line=dict(color="#a78bfa", width=2.5),
            hovertemplate="7d avg: <b>%{y:.0f} ms</b><extra></extra>"))
        if chart_o["resting_hr"].notna().sum() > 3:
            fig_o.add_trace(go.Scatter(
                x=chart_o["date"], y=chart_o["resting_hr"], name="Resting HR",
                mode="lines+markers", yaxis="y2",
                line=dict(color="#fc4c02", width=1.5, dash="dot"),
                marker=dict(size=4, color="#fc4c02"),
                hovertemplate="<b>%{x|%d %b}</b><br>RHR: <b>%{y:.0f} bpm</b><extra></extra>"))
        fig_o.update_layout(
            **{**CHART_LAYOUT, "margin": dict(t=10,b=30,l=50,r=50)},
            height=260,
            yaxis=dict(**axis_style(), title="HRV (ms)"),
            yaxis2=dict(**axis_style(), title="RHR (bpm)", overlaying="y",
                        side="right", showgrid=False),
        )
        fig_o.update_xaxes(**axis_style())
        st.plotly_chart(fig_o, use_container_width=True)

st.markdown('<hr style="border:none;border-top:1px solid #e8e4de;margin:0.8rem 0">', unsafe_allow_html=True)

# ── Headline metrics ──────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Activities",   f"{len(fdf):,}")
c2.metric("Distance",     f"{end['dist_km'].sum():,.0f} km")
c3.metric("Elevation",    f"{end['elev_gain_m'].sum()/1000:.1f}k m")
c4.metric("Moving time",  f"{int(end['moving_min'].sum()//60):,}h")
c5.metric("Calories",     f"{fdf['calories'].sum()/1000:.0f}k kcal")

st.markdown('<hr style="border:none;border-top:1px solid #e8e4de;margin:0.8rem 0">', unsafe_allow_html=True)

# ── Training Consistency Heatmap ─────────────────────────────────────────────
st.markdown("## Training Consistency")

ENDURANCE_H = {"Run","Ride","Virtual Ride","Virtual Run","Walk","Hike",
               "Nordic Ski","Swim","Rowing","E-Bike Ride"}

@st.cache_data
def build_heatmap_data(_df):
    end = _df[_df["sport"].isin(ENDURANCE_H)].copy()
    end["tss"] = end["rel_effort"].fillna(
        end["moving_min"] * (end["avg_hr"].fillna(130) / 150) ** 2 * 0.5)
    daily = end.groupby(end["date"].dt.normalize()).agg(
        tss=("tss","sum"), acts=("moving_min","count")).reset_index()
    daily.columns = ["date","tss","acts"]
    return daily

daily_data = build_heatmap_data(df)

# Year selector for heatmap
hm_years = sorted(df["year"].dropna().unique().astype(int).tolist(), reverse=True)
# Year selector using selectbox — reliable light theme, no CSS fighting
_hm_col, _ = st.columns([2, 5])
with _hm_col:
    st.markdown("""<style>
    div[data-testid="stSidebar"] ~ div .stSelectbox label { display: none; }
    .hm-select div[data-baseweb="select"] > div {
        background: #ffffff !important;
        border: 1px solid #e2ddd8 !important;
        border-radius: 8px !important;
        color: #1a1a1a !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        font-family: "DM Mono", monospace !important;
    }
    .hm-select div[data-baseweb="select"] > div:hover { border-color: #fc4c02 !important; }
    .hm-select div[data-baseweb="select"] span { color: #1a1a1a !important; }
    .hm-select li { color: #1a1a1a !important; background: #ffffff !important; font-size: 0.82rem !important; }
    .hm-select li:hover { background: #f7f5f2 !important; }
    </style>""", unsafe_allow_html=True)
    st.markdown('<div class="hm-select">', unsafe_allow_html=True)
    hm_year = st.selectbox("Year", hm_years, index=0,
        label_visibility="collapsed", key="hm_yr")
    st.markdown('</div>', unsafe_allow_html=True)

# Build calendar grid for selected year
import calendar
year_start = pd.Timestamp(f"{hm_year}-01-01")
year_end   = pd.Timestamp(f"{hm_year}-12-31")
all_days   = pd.date_range(year_start, year_end, freq="D")

# Merge with activity data
day_df = pd.DataFrame({"date": all_days})
day_df = day_df.merge(daily_data, on="date", how="left").fillna({"tss":0,"acts":0})
day_df["level"] = pd.cut(day_df["tss"],
    bins=[-0.1, 0, 25, 75, 150, 9999],
    labels=[0,1,2,3,4]).astype(int)
day_df["dow"]   = day_df["date"].dt.dayofweek  # 0=Mon
day_df["week"]  = (day_df["date"] - year_start).dt.days // 7

# Colours: dark bg → light orange gradient
COLOURS = ["#f0ede8","#ffd4b8","#ffaa77","#ff6622","#fc4c02"]
LABELS  = ["Rest","Light","Moderate","Hard","Very hard"]
DOW_LABELS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

# Build SVG heatmap
total_weeks = day_df["week"].max() + 1
cell_size   = 13
gap         = 2
pad_left    = 30  # space for day labels
pad_top     = 28  # space for month labels
svg_w       = pad_left + total_weeks * (cell_size + gap)
svg_h       = pad_top + 7 * (cell_size + gap) + 40  # +40 for legend

cells = []
for _, row in day_df.iterrows():
    x = pad_left + row["week"] * (cell_size + gap)
    y = pad_top  + row["dow"]  * (cell_size + gap)
    col = COLOURS[int(row["level"])]
    tss_v = f"{row['tss']:.0f}" if row["tss"] > 0 else "Rest"
    title = f"{row['date'].strftime('%a %d %b')} · {tss_v}"
    if row["tss"] > 0:
        title += " load"
    cells.append(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '                 f'rx="2" fill="{col}"><title>{title}</title></rect>')
    # Also add a visible label for today's cell if tss > 0
    if row["tss"] > 0 and row["date"].date() == pd.Timestamp.now().date():
        cells.append(f'<text x="{x+cell_size//2}" y="{y-3}" text-anchor="middle" fill="#fc4c02" font-size="7" font-family="DM Sans">{row["tss"]:.0f}</text>')

# Month labels
month_labels = []
for month in range(1, 13):
    first_day = pd.Timestamp(f"{hm_year}-{month:02d}-01")
    if first_day > year_end: break
    week_num  = (first_day - year_start).days // 7
    mx = pad_left + week_num * (cell_size + gap)
    month_labels.append(f'<text x="{mx}" y="{pad_top-6}" fill="#555" '                        f'font-size="10" font-family="DM Sans">'                        f'{first_day.strftime("%b")}</text>')

# Day of week labels
dow_label_svg = []
for i, d in enumerate(DOW_LABELS):
    if i % 2 == 0:  # only Mon, Wed, Fri, Sun
        y = pad_top + i * (cell_size + gap) + cell_size - 2
        dow_label_svg.append(f'<text x="{pad_left-4}" y="{y}" fill="#444" '                             f'font-size="9" font-family="DM Sans" text-anchor="end">{d}</text>')

# Legend
legend_x = pad_left
legend_y  = pad_top + 7*(cell_size+gap) + 12
legend_svg = [f'<text x="{legend_x}" y="{legend_y+11}" fill="#bbb" font-size="9" font-family="DM Sans">Less</text>']
for i, col in enumerate(COLOURS):
    lx = legend_x + 32 + i*(cell_size+gap)
    legend_svg.append(f'<rect x="{lx}" y="{legend_y}" width="{cell_size}" height="{cell_size}" rx="2" fill="{col}"><title>{LABELS[i]}</title></rect>')
legend_svg.append(f'<text x="{legend_x+32+len(COLOURS)*(cell_size+gap)+4}" y="{legend_y+11}" fill="#444" font-size="9" font-family="DM Sans">More</text>')

svg = f"""<svg width="100%" viewBox="0 0 {svg_w} {svg_h}" xmlns="http://www.w3.org/2000/svg">
{"".join(month_labels)}
{"".join(dow_label_svg)}
{"".join(cells)}
{"".join(legend_svg)}
</svg>"""

# Stats for this year
yr_data  = daily_data[daily_data["date"].dt.year == hm_year]
active_days = (yr_data["tss"] > 0).sum()
total_days  = len(all_days)
streak      = 0
max_streak  = 0
cur_streak  = 0
for _, row in day_df.iterrows():
    if row["tss"] > 0:
        cur_streak += 1
        max_streak  = max(max_streak, cur_streak)
    else:
        cur_streak = 0

s1, s2, s3, s4 = st.columns(4)
s1.metric("Active days",   f"{active_days}")
s2.metric("Rest days",     f"{total_days - active_days}")
s3.metric("Longest streak", f"{max_streak} days")
s4.metric("Consistency",   f"{active_days/total_days*100:.0f}%")

st.markdown(f'<div style="background:#ffffff;border:1px solid #e2ddd8;border-radius:12px;padding:1rem 1.2rem;overflow-x:auto;box-shadow:0 1px 4px rgba(0,0,0,0.06);-webkit-overflow-scrolling:touch">{svg}</div>', unsafe_allow_html=True)

st.markdown("<div style='font-size:0.72rem;color:#444;margin-top:4px'>Hover over any square to see the training load. Colour = training stress: dark = rest, orange = hard session.</div>", unsafe_allow_html=True)

st.markdown('<hr style="border:none;border-top:1px solid #e8e4de;margin:0.8rem 0">', unsafe_allow_html=True)

# ── Personal records ──────────────────────────────────────────────────────────
st.markdown("## Personal Records")

runs_valid = df[(df["sport"]=="Run") & (df["dist_km"]>1)].copy()
runs_valid["pace_min_km"] = pd.to_numeric(runs_valid["pace_min_km"], errors="coerce")
runs_valid = runs_valid[runs_valid["pace_min_km"].between(3,15)]
rides_all  = df[df["sport"].isin(["Ride","Virtual Ride"])]

def fmt_pace(v):
    if pd.isna(v): return "—"
    return f"{int(v)}:{int((v%1)*60):02d}"

def activity_detail_html(row, extra_stat="", extra_label=""):
    """Render a compact detail card for a record activity."""
    if row is None: return ""
    act_id   = int(row["activity_id"])
    strava   = f"https://www.strava.com/activities/{act_id}"
    date_str = row["date"].strftime("%d %b %Y")
    name     = str(row["name"])[:40] if pd.notna(row["name"]) else row["sport"]
    dist     = f"{row['dist_km']:.1f} km" if row["dist_km"] > 0 else ""
    hrs      = int(row["moving_min"]//60)
    mins     = int(row["moving_min"]%60)
    time_s   = f"{hrs}h {mins:02d}m" if hrs > 0 else f"{mins}m"
    elev     = f"{int(row['elev_gain_m'])} m↑" if pd.notna(row["elev_gain_m"]) and row["elev_gain_m"] > 0 else ""
    hr_s     = f"{int(row['avg_hr'])} bpm avg" if pd.notna(row["avg_hr"]) and row["avg_hr"] > 0 else ""
    cal_s    = f"{int(row['calories'])} kcal" if pd.notna(row["calories"]) and row["calories"] > 0 else ""
    stats    = " · ".join(filter(None, [dist, time_s, elev, hr_s, cal_s]))
    if extra_stat:
        stats = f"<b style='color:#fc4c02'>{extra_label}: {extra_stat}</b> · " + stats
    return f"""
<div style="background:#f7f5f2;border:1px solid #e2ddd8;border-radius:8px;
            padding:0.75rem 1rem;margin-top:8px;font-size:0.78rem">
  <div style="display:flex;justify-content:space-between;align-items:flex-start">
    <div>
      <div style="color:#666;font-size:0.65rem;margin-bottom:2px">{date_str}</div>
      <div style="color:#333;font-weight:600;margin-bottom:4px">{name}</div>
      <div style="color:#888">{stats}</div>
    </div>
    <a href="{strava}" target="_blank"
       style="background:#fc4c02;color:#fff;font-size:0.65rem;font-weight:700;
              text-decoration:none;padding:4px 10px;border-radius:6px;
              text-transform:uppercase;letter-spacing:0.06em;white-space:nowrap;
              margin-left:12px;flex-shrink:0">
      View on Strava ↗
    </a>
  </div>
</div>"""

# Compute record rows
lr_row  = runs_valid.loc[runs_valid["dist_km"].idxmax()]        if len(runs_valid) else None
bp_row  = runs_valid.loc[runs_valid["pace_min_km"].idxmin()]    if len(runs_valid) else None
mc_row  = runs_valid.loc[runs_valid["elev_gain_m"].idxmax()]    if len(runs_valid) else None
lride_r = rides_all.loc[rides_all["dist_km"].idxmax()]          if len(rides_all) else None

r1, r2, r3, r4, r5, r6 = st.columns(6)
with r1:
    v = lr_row["dist_km"] if lr_row is not None else 0
    st.markdown(f'<div class="record-card"><div class="record-label">Longest Run</div>'                f'<div class="record-value">{v:.1f}</div>'                f'<div class="record-sub">km</div></div>', unsafe_allow_html=True)
with r2:
    v = bp_row["pace_min_km"] if bp_row is not None else None
    st.markdown(f'<div class="record-card"><div class="record-label">Best Pace</div>'                f'<div class="record-value">{fmt_pace(v)}</div>'                f'<div class="record-sub">min/km</div></div>', unsafe_allow_html=True)
with r3:
    v = mc_row["elev_gain_m"] if mc_row is not None else 0
    st.markdown(f'<div class="record-card"><div class="record-label">Most Climbing</div>'                f'<div class="record-value">{v:,.0f}</div>'                f'<div class="record-sub">metres</div></div>', unsafe_allow_html=True)
with r4:
    v = lride_r["dist_km"] if lride_r is not None else 0
    st.markdown(f'<div class="record-card"><div class="record-label">Longest Ride</div>'                f'<div class="record-value">{v:.0f}</div>'                f'<div class="record-sub">km</div></div>', unsafe_allow_html=True)
with r5:
    v = len(df[df["sport"]=="Run"])
    st.markdown(f'<div class="record-card"><div class="record-label">Total Runs</div>'                f'<div class="record-value">{v:,}</div>'                f'<div class="record-sub">activities</div></div>', unsafe_allow_html=True)
with r6:
    v = df[df["sport"].isin(["Ride","Virtual Ride"])]["dist_km"].sum()
    st.markdown(f'<div class="record-card"><div class="record-label">Total Ride km</div>'                f'<div class="record-value">{v:,.0f}</div>'                f'<div class="record-sub">km</div></div>', unsafe_allow_html=True)

# ── Expandable record details ─────────────────────────────────────────────────
with st.expander("📋 View record activity details", expanded=False):
    d1, d2 = st.columns(2)
    with d1:
        st.markdown("**🏃 Longest Run**")
        if lr_row is not None:
            p = lr_row["moving_min"] / lr_row["dist_km"]
            st.markdown(activity_detail_html(lr_row,
                extra_stat=f"{lr_row['dist_km']:.1f} km",
                extra_label="Distance"), unsafe_allow_html=True)
        st.markdown("**⚡ Best Pace**")
        if bp_row is not None:
            p = bp_row["moving_min"] / bp_row["dist_km"]
            st.markdown(activity_detail_html(bp_row,
                extra_stat=f"{int(p)}:{int((p%1)*60):02d} /km",
                extra_label="Pace"), unsafe_allow_html=True)
    with d2:
        st.markdown("**⛰️ Most Climbing**")
        if mc_row is not None:
            st.markdown(activity_detail_html(mc_row,
                extra_stat=f"{int(mc_row['elev_gain_m'])} m",
                extra_label="Elevation"), unsafe_allow_html=True)
        st.markdown("**🚴 Longest Ride**")
        if lride_r is not None:
            st.markdown(activity_detail_html(lride_r,
                extra_stat=f"{lride_r['dist_km']:.1f} km",
                extra_label="Distance"), unsafe_allow_html=True)
st.markdown('<hr style="border:none;border-top:1px solid #e8e4de;margin:0.8rem 0">', unsafe_allow_html=True)

st.markdown("## Weekly Volume")

weeks_back = st.slider("Weeks to show", 12, 156, 52, step=4, key="wk_slider")
cutoff = fdf["date"].max() - pd.Timedelta(weeks=weeks_back)
recent_w = fdf[fdf["date"] >= cutoff].copy()
recent_w["week"] = recent_w["date"].dt.to_period("W").dt.start_time
SHOW = [s for s in ["Run","Ride","Virtual Ride","Walk","E-Bike Ride","Rowing","Hike"]
        if s in selected_sports]
weekly_raw = (recent_w[recent_w["sport"].isin(SHOW)]
               .groupby(["week","sport"])["dist_km"].sum().reset_index())
weekly_pivot = weekly_raw.pivot_table(index="week", columns="sport",
                                       values="dist_km", aggfunc="sum", fill_value=0).reset_index()

fig2 = go.Figure()
for sport in SHOW:
    if sport not in weekly_pivot.columns: continue
    fig2.add_trace(go.Bar(
        x=weekly_pivot["week"], y=weekly_pivot[sport].round(1),
        name=sport,
        marker=dict(color=SPORT_COLORS.get(sport,"#666"), line=dict(width=0)),
        hovertemplate=sport + ": <b>%{y:.1f} km</b><extra></extra>"))
fig2.update_layout(**CHART_LAYOUT, barmode="stack", height=320, yaxis_title="km")
fig2.update_xaxes(**axis_style())
fig2.update_yaxes(**axis_style())
st.plotly_chart(fig2, use_container_width=True)

# ── Weekly Volume — Hours ─────────────────────────────────────────────────────
st.markdown("## Weekly Training Hours")

# All endurance sports for hours
ENDURANCE_H = {"Run","Ride","Virtual Ride","Virtual Run","Walk","Hike",
               "Nordic Ski","Swim","Rowing","E-Bike Ride","Weight Training","Workout"}

hr_w = fdf[fdf["sport"].isin(ENDURANCE_H)].copy()
hr_w["week"] = hr_w["date"].dt.to_period("W").dt.start_time
hr_w["hours"] = hr_w["moving_min"] / 60

weekly_hrs = (hr_w.groupby("week")["hours"].sum().reset_index()
              .sort_values("week"))
weekly_hrs = weekly_hrs[weekly_hrs["week"] >= (fdf["date"].max() - pd.Timedelta(weeks=weeks_back))]

# Week-over-week delta
if len(weekly_hrs) >= 2:
    this_week = weekly_hrs["hours"].iloc[-1]
    last_week = weekly_hrs["hours"].iloc[-2]
    delta_h   = this_week - last_week
    delta_pct = (delta_h / last_week * 100) if last_week > 0 else 0
    arrow     = "▲" if delta_h >= 0 else "▼"
    delta_col = "#50c850" if delta_h >= 0 else "#ff5555"
    this_h = int(this_week)
    this_m = int((this_week % 1) * 60)
    dlt_h  = int(abs(delta_h))
    dlt_m  = int((abs(delta_h) % 1) * 60)
    trend_html = f"""
    <div style="margin-bottom:1.2rem">
      <div style="color:#666;font-size:0.68rem;font-weight:600;text-transform:uppercase;
                  letter-spacing:0.12em;margin-bottom:6px">This week</div>
      <div style="display:flex;align-items:center;gap:14px">
        <div style="color:#1a1a1a;font-size:2rem;font-weight:700;
                    font-family:'DM Mono',monospace;line-height:1;min-width:120px">
          {this_h}h&nbsp;{this_m:02d}m
        </div>
        <div style="background:#ffffff;border:1px solid #e2ddd8;border-radius:8px;
                    padding:6px 14px;display:inline-flex;align-items:center;gap:8px">
          <span style="color:{delta_col};font-size:0.95rem;font-weight:700">{arrow} {dlt_h}h {dlt_m:02d}m</span>
          <span style="color:#555;font-size:0.78rem">({abs(delta_pct):.0f}%) vs last week</span>
        </div>
      </div>
    </div>"""
    st.markdown(trend_html, unsafe_allow_html=True)

# Rolling 8-week average line
weekly_hrs["rolling"] = weekly_hrs["hours"].rolling(8, min_periods=1).mean()

fig_h = go.Figure()
fig_h.add_trace(go.Bar(
    x=weekly_hrs["week"], y=weekly_hrs["hours"].round(2),
    name="Hours",
    marker=dict(color="rgba(167,139,250,0.35)", line=dict(width=0)),
    hovertemplate="<b>%{y:.1f}h</b><extra></extra>",
))
fig_h.add_trace(go.Scatter(
    x=weekly_hrs["week"], y=weekly_hrs["rolling"].round(2),
    mode="lines", name="8-week avg",
    line=dict(color="#a78bfa", width=2.5),
    hovertemplate="Avg: <b>%{y:.1f}h</b><extra></extra>",
))
fig_h.update_layout(**CHART_LAYOUT, height=300, yaxis_title="hours")
fig_h.update_xaxes(**axis_style())
fig_h.update_yaxes(**axis_style())
st.plotly_chart(fig_h, use_container_width=True)

st.markdown('<hr style="border:none;border-top:1px solid #e8e4de;margin:0.8rem 0">', unsafe_allow_html=True)

# ── Yearly volumes side by side ───────────────────────────────────────────────
st.markdown("## Yearly Volume" if selected_year == "All" else f"## {selected_year} — Monthly Volume")
col_run, col_ride = st.columns(2)

with col_run:
    st.markdown("### 🏃 Running")
    if selected_year == "All":
        yr_run = df[df["sport"]=="Run"].groupby("year")["dist_km"].sum().reset_index()
        if len(yr_run) > 0:
            stem, dot = lollipop(yr_run["year"].astype(int), yr_run["dist_km"].round(), unit="km")
            fig_r = go.Figure([stem, dot])
            fig_r.update_layout(**{**CHART_LAYOUT, "margin": dict(t=10,b=30,l=40,r=10)},
                height=300, yaxis_title="km", barmode="overlay")
            fig_r.update_xaxes(**axis_style(), dtick=1, tickformat="d")
            fig_r.update_yaxes(**axis_style())
            st.plotly_chart(fig_r, use_container_width=True)
    else:
        mo_run = fdf[fdf["sport"]=="Run"].copy()
        mo_run["month_num"]  = mo_run["date"].dt.month
        mo_run["month_name"] = mo_run["date"].dt.strftime("%b")
        mo_grp = mo_run.groupby(["month_num","month_name"])["dist_km"].sum().reset_index()
        mo_grp = mo_grp.sort_values("month_num")
        if len(mo_grp) > 0:
            stem, dot = lollipop(mo_grp["month_name"], mo_grp["dist_km"].round(1), unit="km")
            fig_r = go.Figure([stem, dot])
            fig_r.update_layout(**{**CHART_LAYOUT, "margin": dict(t=10,b=30,l=40,r=10)},
                height=300, yaxis_title="km", barmode="overlay")
            fig_r.update_xaxes(**axis_style())
            fig_r.update_yaxes(**axis_style())
            st.plotly_chart(fig_r, use_container_width=True)
        else:
            st.info("No running data for this year.")

with col_ride:
    st.markdown("### 🚴 Cycling")
    cycling_types = ["Ride","Virtual Ride","E-Bike Ride"]
    if selected_year == "All":
        cyc_tot = (df[df["sport"].isin(cycling_types)]
                   .groupby("year")["dist_km"].sum().reset_index())
        if len(cyc_tot) > 0:
            stem, dot = lollipop(cyc_tot["year"].astype(int),
                                  cyc_tot["dist_km"].round(),
                                  color="#ffa500", unit="km")
            fig_c = go.Figure([stem, dot])
            fig_c.update_layout(**{**CHART_LAYOUT, "margin": dict(t=10,b=30,l=40,r=10)},
                height=300, yaxis_title="km", barmode="overlay")
            fig_c.update_xaxes(**axis_style(), dtick=1, tickformat="d")
            fig_c.update_yaxes(**axis_style())
            st.plotly_chart(fig_c, use_container_width=True)
    else:
        cyc_m = df[df["sport"].isin(cycling_types)].copy()
        cyc_m = cyc_m[cyc_m["date"].dt.year == int(selected_year)]
        cyc_m["month_num"]  = cyc_m["date"].dt.month
        cyc_m["month_name"] = cyc_m["date"].dt.strftime("%b")
        mo_cyc = cyc_m.groupby(["month_num","month_name"])["dist_km"].sum().reset_index()
        mo_cyc = mo_cyc.sort_values("month_num")
        if len(mo_cyc) > 0:
            stem, dot = lollipop(mo_cyc["month_name"],
                                  mo_cyc["dist_km"].round(1),
                                  color="#ffa500", unit="km")
            fig_c = go.Figure([stem, dot])
            fig_c.update_layout(**{**CHART_LAYOUT, "margin": dict(t=10,b=30,l=40,r=10)},
                height=300, yaxis_title="km", barmode="overlay")
            fig_c.update_xaxes(**axis_style())
            fig_c.update_yaxes(**axis_style())
            st.plotly_chart(fig_c, use_container_width=True)
        else:
            st.info("No cycling data for this year.")
st.markdown('<hr style="border:none;border-top:1px solid #e8e4de;margin:0.8rem 0">', unsafe_allow_html=True)

# ── Elevation Gain ───────────────────────────────────────────────────────────
if selected_year == "All":
    st.markdown("## Yearly Elevation Gain")
else:
    st.markdown(f"## {selected_year} — Monthly Elevation Gain")

col_run_elev, col_ride_elev = st.columns(2)

with col_run_elev:
    st.markdown("### 🏃 Running")
    if selected_year == "All":
        # Yearly bars — all time
        run_elev = (df[df["sport"] == "Run"]
                    .groupby("year")["elev_gain_m"].sum().reset_index())
        run_elev = run_elev[run_elev["elev_gain_m"] > 0]
        if len(run_elev) > 0:
            stem, dot = lollipop(run_elev["year"].astype(int), run_elev["elev_gain_m"].round(),
                                  color="#50c850", unit="m")
            fig_re = go.Figure([stem, dot])
            fig_re.update_layout(**{**CHART_LAYOUT, "margin": dict(t=10,b=30,l=50,r=10)},
                height=300, yaxis_title="metres", barmode="overlay")
            fig_re.update_xaxes(**axis_style(), dtick=1, tickformat="d")
            fig_re.update_yaxes(**axis_style())
            st.plotly_chart(fig_re, use_container_width=True)
    else:
        # Monthly bars — selected year
        run_elev_m = (fdf[fdf["sport"] == "Run"]
                      .groupby("month")["elev_gain_m"].sum().reset_index())
        month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                       7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
        run_elev_m["month_name"] = run_elev_m["month"].map(month_names)
        if len(run_elev_m) > 0:
            stem, dot = lollipop(run_elev_m["month_name"], run_elev_m["elev_gain_m"].round(),
                                  color="#50c850", unit="m")
            fig_re = go.Figure([stem, dot])
            fig_re.update_layout(**{**CHART_LAYOUT, "margin": dict(t=10,b=30,l=50,r=10)},
                height=300, yaxis_title="metres", barmode="overlay")
            fig_re.update_xaxes(**axis_style())
            fig_re.update_yaxes(**axis_style())
            st.plotly_chart(fig_re, use_container_width=True)
        else:
            st.info("No running data for this year.")

with col_ride_elev:
    st.markdown("### 🚴 Cycling")
    cycling_types_e = ["Ride", "Virtual Ride", "E-Bike Ride"]
    cyc_elev_colors = {"Ride":"#ffa500","Virtual Ride":"#ffcc44","E-Bike Ride":"#ce93d8"}
    if selected_year == "All":
        yr_ride_tot = (df[df["sport"].isin(cycling_types_e)]
                       .groupby("year")["elev_gain_m"].sum().reset_index())
        yr_ride_tot = yr_ride_tot[yr_ride_tot["elev_gain_m"] > 0]
        if len(yr_ride_tot) > 0:
            stem, dot = lollipop(yr_ride_tot["year"].astype(int),
                                  yr_ride_tot["elev_gain_m"].round(),
                                  color="#ffa500", unit="m")
            fig_ce = go.Figure([stem, dot])
            fig_ce.update_layout(**{**CHART_LAYOUT, "margin": dict(t=10,b=30,l=50,r=10)},
                height=300, yaxis_title="metres", barmode="overlay")
            fig_ce.update_xaxes(**axis_style(), dtick=1, tickformat="d")
            fig_ce.update_yaxes(**axis_style())
            st.plotly_chart(fig_ce, use_container_width=True)
    else:
        ride_elev_m = (fdf[fdf["sport"].isin(cycling_types_e)]
                       .groupby(["month","sport"])["elev_gain_m"].sum().reset_index())
        month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                       7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
        ride_elev_m["month_name"] = ride_elev_m["month"].map(month_names)
        if len(ride_elev_m) > 0:
            fig_ce = go.Figure()
            for ctype in cycling_types_e:
                s = ride_elev_m[ride_elev_m["sport"]==ctype]
                if len(s) == 0: continue
                fig_ce.add_trace(go.Bar(
                    x=s["month_name"], y=s["elev_gain_m"].round(),
                    name=ctype,
                    marker=dict(color=cyc_elev_colors[ctype], line=dict(width=0)),
                    width=0.45,
                    hovertemplate=ctype + ": <b>%{y:,.0f} m</b><extra></extra>"))
            fig_ce.update_layout(**{**CHART_LAYOUT, "margin": dict(t=10,b=30,l=50,r=10)},
                barmode="stack", height=300, yaxis_title="metres")
            fig_ce.update_xaxes(**axis_style())
            fig_ce.update_yaxes(**axis_style())
            st.plotly_chart(fig_ce, use_container_width=True)
        else:
            st.info("No cycling data for this year.")
st.markdown('<hr style="border:none;border-top:1px solid #e8e4de;margin:0.8rem 0">', unsafe_allow_html=True)

# ── Recent activities ─────────────────────────────────────────────────────────
st.markdown("## Recent Activities")

n_rows = st.slider("Show", 10, 100, 20, step=10, key="recent_n")
recent_acts = fdf.sort_values("date", ascending=False).head(n_rows).copy()

def fmt_pace_row(row):
    try:
        sport = row["sport"]
        if sport in ["Run","Walk","Virtual Run","Hike"] and row["dist_km"] > 0:
            p = row["moving_min"] / row["dist_km"]
            return f"{int(p)}:{int((p%1)*60):02d} /km"
        elif sport in ["Ride","Virtual Ride","E-Bike Ride","Rowing"]:
            kmh = row.get("avg_speed_kmh", 0)
            if pd.isna(kmh) or kmh == 0:
                # fallback: calculate from distance and time
                if row["moving_min"] > 0 and row["dist_km"] > 0:
                    kmh = row["dist_km"] / (row["moving_min"] / 60)
            if kmh and kmh > 0:
                return f"{kmh:.1f} km/h"
    except Exception:
        pass
    return "—"

recent_acts["Pace"] = recent_acts.apply(fmt_pace_row, axis=1)
recent_acts["Date"] = recent_acts["date"].dt.strftime("%d %b %Y")
recent_acts["Km"]   = recent_acts["dist_km"].round(1)
recent_acts["Time"] = recent_acts["moving_min"].apply(
    lambda m: f"{int(m//60)}h {int(m%60):02d}m" if not pd.isna(m) else "—")
recent_acts["HR"]   = recent_acts["avg_hr"].apply(
    lambda h: f"{int(h)}" if not pd.isna(h) else "—")
recent_acts["Elev"] = recent_acts["elev_gain_m"].apply(
    lambda e: f"{int(e)}m" if not pd.isna(e) else "—")

# Build HTML table — guaranteed light theme (st.dataframe uses canvas, ignores CSS)
_trows = ""
for _, r in recent_acts.iterrows():
    sport_color = SPORT_COLORS.get(r["sport"], "#888")
    _trows += (
        "<tr>"
        + f'<td style="color:#999;font-size:0.78rem">{r["Date"]}</td>'
        + f'<td><span style="background:{sport_color}22;color:{sport_color};font-size:0.65rem;font-weight:700;padding:2px 7px;border-radius:4px;text-transform:uppercase">{r["sport"]}</span></td>'
        + f'<td style="color:#1a1a1a;font-weight:500">{str(r["name"])[:35] if pd.notna(r["name"]) else r["sport"]}</td>'
        + f'<td style="color:#333">{r["Km"] if r["Km"] > 0 else "—"}</td>'
        + f'<td style="color:#333">{r["Time"]}</td>'
        + f'<td style="color:#333">{r["Pace"]}</td>'
        + f'<td style="color:#333">{r["HR"]}</td>'
        + f'<td style="color:#333">{r["Elev"]}</td>'
        + "</tr>"
    )
st.markdown(
    '<div style="background:#ffffff;border:1px solid #e2ddd8;border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,0.06)">' +
    '<table style="width:100%;border-collapse:collapse;font-family:DM Sans,sans-serif;font-size:0.83rem">' +
    '<thead><tr style="background:#f7f5f2;border-bottom:2px solid #e8e4de">' +
    '<th style="color:#888;font-size:0.68rem;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;padding:10px 14px;text-align:left">Date</th>' +
    '<th style="color:#888;font-size:0.68rem;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;padding:10px 8px;text-align:left">Sport</th>' +
    '<th style="color:#888;font-size:0.68rem;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;padding:10px 14px;text-align:left">Activity</th>' +
    '<th style="color:#888;font-size:0.68rem;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;padding:10px 8px;text-align:right">km</th>' +
    '<th style="color:#888;font-size:0.68rem;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;padding:10px 8px;text-align:left">Time</th>' +
    '<th style="color:#888;font-size:0.68rem;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;padding:10px 8px;text-align:left">Pace</th>' +
    '<th style="color:#888;font-size:0.68rem;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;padding:10px 8px;text-align:right">HR</th>' +
    '<th style="color:#888;font-size:0.68rem;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;padding:10px 8px;text-align:right">Elev</th>' +
    '</tr></thead>' +
    f'<tbody>{_trows}</tbody>' +
    '</table></div>',
    unsafe_allow_html=True
)

# ── Activity route map ────────────────────────────────────────────────────────
if _polylines:
    map_opts = []
    for _, row in recent_acts.iterrows():
        try:
            aid = str(int(row["activity_id"]))
        except Exception:
            continue
        if aid in _polylines:
            lbl = row["Date"] + " · " + (str(row["name"])[:30] if pd.notna(row["name"]) else str(row["sport"]))
            map_opts.append((lbl, aid))

    if map_opts:
        col_sel, _ = st.columns([3, 2])
        with col_sel:
            sel_lbl = st.selectbox("🗺️ View route map", [m[0] for m in map_opts], key="map_sel")
        sel_aid    = next(aid for lbl, aid in map_opts if lbl == sel_lbl)
        sel_coords = decode_polyline(_polylines[sel_aid])
        if sel_coords:
            try:
                import folium
                from streamlit_folium import st_folium
                st_folium(make_folium_map(sel_coords, height=350),
                          use_container_width=True, height=350,
                          returned_objects=[], key="recent_map")
            except ImportError:
                st.info("Add `folium` and `streamlit-folium` to requirements.txt to see route maps.")
    else:
        st.caption("No route data available yet — sync will populate maps after next run.")

st.markdown("""
<div style="margin-top:3rem;padding-top:1rem;border-top:1px solid #e2ddd8;
            color:#444;font-size:0.75rem;text-align:center">
  Built on Strava data · Powered by Streamlit
</div>
""", unsafe_allow_html=True)
