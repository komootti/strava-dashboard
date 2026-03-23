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
    background-color: #0f0f0f;
    color: #e8e4de;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #161616 !important;
    border-right: 1px solid #2a2a2a;
}
[data-testid="stSidebar"] * {
    color: #d4d0ca !important;
}

/* Main content padding */
.block-container {
    padding: 2rem 2.5rem 2rem 2.5rem !important;
    max-width: 1400px;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 1.2rem 1.4rem !important;
    transition: border-color 0.2s;
}
[data-testid="metric-container"]:hover {
    border-color: #fc4c02;
}
[data-testid="stMetricLabel"] {
    color: #aaa !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
[data-testid="stMetricValue"] {
    color: #eceae5 !important;
    font-size: 1.9rem !important;
    font-weight: 600 !important;
    line-height: 1.2;
}
[data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
}

/* Section headers */
h1 {
    color: #f0ede8 !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}
h2 {
    color: #f0ede8 !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 2rem !important;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #fc4c02;
    display: inline-block;
}
h3 {
    color: #c8c4be !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
}

/* Divider */
hr {
    border-color: #2a2a2a !important;
    margin: 1.5rem 0 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    overflow: hidden;
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

/* Record card style */
.record-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
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
GITHUB_RAW_URL = "https://raw.githubusercontent.com/komootti/strava-dashboard/main/activities.csv"

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
    plot_bgcolor="#161616",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#aaa", size=11),
    margin=dict(t=30, b=30, l=50, r=20),
    legend=dict(
        orientation="h", y=1.08,
        font=dict(color="#c8c4be", size=11),
        bgcolor="rgba(0,0,0,0)"
    ),
    hoverlabel=dict(
        bgcolor="#1e1e1e",
        bordercolor="#fc4c02",
        font=dict(color="#e8e4de", size=12, family="DM Sans"),
    ),
    hovermode="closest",
)

def axis_style():
    return dict(
        gridcolor="#222",
        linecolor="#333",
        tickcolor="#444",
        tickfont=dict(color="#666", size=10),
        zerolinecolor="#333",
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
        marker=dict(color=color, size=8, line=dict(color="#0f0f0f", width=2)),
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

# ── Sidebar ───────────────────────────────────────────────────────────────────
# ── Year filter state ────────────────────────────────────────────────────────
all_years = sorted(df["year"].dropna().unique().astype(int).tolist(), reverse=True)
if "selected_year" not in st.session_state:
    st.session_state["selected_year"] = "All"

with st.sidebar:
    st.markdown("## 🔥 Filters")
    st.markdown("---")

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
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 10px !important;
    color: #d4d0ca !important;
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

    st.markdown("---")
    all_sports = sorted(df["sport"].unique().tolist())
    selected_sports = st.multiselect("Sports", all_sports, default=all_sports)

    st.markdown("---")
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
  <h1 style="margin:0;font-size:2rem;font-weight:800;letter-spacing:-0.03em">
    Your Athletic Journey
  </h1>
  <div style="color:#888;font-size:0.85rem;margin-top:4px">
    {'📅 ' + selected_year if selected_year != 'All' else df['date'].min().strftime('%b %Y') + ' — ' + df['date'].max().strftime('%b %Y') + ' · ' + str(df['year'].nunique()) + ' years'}
  </div>
</div>
""", unsafe_allow_html=True)



# ── Latest activity card ─────────────────────────────────────────────────────
latest_act = df.sort_values("date", ascending=False).iloc[0]
la_sport   = latest_act["sport"]
la_date    = latest_act["date"].strftime("%a %d %b %Y")
la_name    = latest_act["name"] if pd.notna(latest_act["name"]) else la_sport
la_dist    = f"{latest_act['dist_km']:.1f} km" if latest_act["dist_km"] > 0 else ""
la_time    = f"{int(latest_act['moving_min']//60)}h {int(latest_act['moving_min']%60):02d}m" if latest_act["moving_min"] > 0 else ""
la_elev    = f"{int(latest_act['elev_gain_m'])} m↑" if pd.notna(latest_act["elev_gain_m"]) and latest_act["elev_gain_m"] > 0 else ""
la_hr      = f"{int(latest_act['avg_hr'])} bpm" if pd.notna(latest_act["avg_hr"]) and latest_act["avg_hr"] > 0 else ""

# Pace for runs, speed for rides
if la_sport in ["Run","Walk","Virtual Run","Hike"] and latest_act["dist_km"] > 0:
    p = latest_act["moving_min"] / latest_act["dist_km"]
    la_pace = f"{int(p)}:{int((p%1)*60):02d} /km"
elif la_sport in ["Ride","Virtual Ride","E-Bike Ride"] and latest_act["avg_speed_ms"] > 0:
    la_pace = f"{latest_act['avg_speed_ms']*3.6:.1f} km/h"
else:
    la_pace = ""

# Week comparison for this sport
this_week_start = latest_act["date"].normalize() - pd.Timedelta(days=latest_act["date"].dayofweek)
last_week_start = this_week_start - pd.Timedelta(weeks=1)
this_wk_acts = df[(df["date"] >= this_week_start) & (df["sport"]==la_sport)]
last_wk_acts = df[(df["date"] >= last_week_start) & (df["date"] < this_week_start) & (df["sport"]==la_sport)]
this_wk_km   = this_wk_acts["dist_km"].sum()
last_wk_km   = last_wk_acts["dist_km"].sum()
wk_delta     = this_wk_km - last_wk_km
wk_arrow     = "▲" if wk_delta >= 0 else "▼"
wk_col       = "#50c850" if wk_delta >= 0 else "#ff5555"
wk_badge     = f'<span style="color:{wk_col};font-weight:600">{wk_arrow} {abs(wk_delta):.1f} km vs last week</span>' if last_wk_km > 0 else ""

stats = " · ".join(filter(None, [la_dist, la_time, la_pace, la_elev, la_hr]))

st.markdown(f"""
<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-left:3px solid #fc4c02;
            border-radius:10px;padding:1rem 1.2rem;margin-bottom:1.2rem">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
    <div>
      <div style="color:#666;font-size:0.65rem;font-weight:600;text-transform:uppercase;
                  letter-spacing:0.1em;margin-bottom:3px">Latest activity · {la_date}</div>
      <div style="color:#e8e4de;font-size:1.1rem;font-weight:600;margin-bottom:4px">{la_name}</div>
      <div style="color:#aaa;font-size:0.82rem">{stats}</div>
    </div>
    <div style="text-align:right">
      <div style="background:#fc4c02;color:#fff;font-size:0.65rem;font-weight:700;
                  text-transform:uppercase;letter-spacing:0.08em;padding:3px 10px;
                  border-radius:999px;display:inline-block;margin-bottom:6px">{la_sport}</div>
      <div style="font-size:0.78rem">{wk_badge}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Headline metrics ──────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Activities",   f"{len(fdf):,}")
c2.metric("Distance",     f"{end['dist_km'].sum():,.0f} km")
c3.metric("Elevation",    f"{end['elev_gain_m'].sum()/1000:.1f}k m")
c4.metric("Moving time",  f"{int(end['moving_min'].sum()//60):,}h")
c5.metric("Calories",     f"{fdf['calories'].sum()/1000:.0f}k kcal")

st.markdown("---")

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
<div style="background:#111;border:1px solid #222;border-radius:8px;
            padding:0.75rem 1rem;margin-top:8px;font-size:0.78rem">
  <div style="display:flex;justify-content:space-between;align-items:flex-start">
    <div>
      <div style="color:#666;font-size:0.65rem;margin-bottom:2px">{date_str}</div>
      <div style="color:#d4d0ca;font-weight:600;margin-bottom:4px">{name}</div>
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
st.markdown("---")

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
st.markdown("""<style>
.hm-year-wrap div[data-testid="stRadio"] > div {
    flex-direction: row !important;
    flex-wrap: wrap;
    gap: 4px;
    background: transparent;
}
.hm-year-wrap div[data-testid="stRadio"] label {
    padding: 2px 10px !important;
    border-radius: 6px !important;
    border: 1px solid #252525 !important;
    background: transparent !important;
    color: #666 !important;
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    margin: 0 !important;
    cursor: pointer;
    letter-spacing: 0.04em;
    font-family: "DM Mono", monospace !important;
}
.hm-year-wrap div[data-testid="stRadio"] label:hover {
    border-color: #444 !important;
    color: #aaa !important;
}
.hm-year-wrap div[data-testid="stRadio"] label:has(input:checked) {
    background: rgba(252,76,2,0.15) !important;
    border-color: #fc4c02 !important;
    color: #fc4c02 !important;
    font-weight: 600 !important;
}
.hm-year-wrap div[data-testid="stRadio"] label > div:first-child { display: none !important; }
</style>""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="hm-year-wrap">', unsafe_allow_html=True)
    hm_year = st.radio("hm", hm_years,
        index=0, horizontal=True,
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
COLOURS = ["#1a1a1a","#7a2800","#c03000","#e85500","#fc4c02"]
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
legend_svg = [f'<text x="{legend_x}" y="{legend_y+11}" fill="#444" font-size="9" font-family="DM Sans">Less</text>']
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

st.markdown(f'<div style="background:#111;border:1px solid #1e1e1e;border-radius:10px;padding:1rem 1.2rem;overflow-x:auto">{svg}</div>', unsafe_allow_html=True)

st.markdown("<div style='font-size:0.72rem;color:#444;margin-top:4px'>Hover over any square to see the training load. Colour = training stress: dark = rest, orange = hard session.</div>", unsafe_allow_html=True)

st.markdown("---")

# ── CTL / ATL / TSB ───────────────────────────────────────────────────────────
st.markdown("## Training Load — CTL · ATL · TSB")

# CTL/ATL/TSB always computed on full history (needs all data for accuracy)
# but we show the snapshot at end of selected year/period
end2 = df[df["is_endurance"]].copy()
end2["tss"] = end2["rel_effort"].fillna(
    end2["moving_min"] * (end2["avg_hr"].fillna(130) / 150) ** 2 * 0.5)
daily = end2.groupby(end2["date"].dt.normalize())["tss"].sum().reset_index()
daily.columns = ["date","tss"]
daily["date"] = pd.to_datetime(daily["date"])
full = pd.date_range(daily["date"].min(), daily["date"].max(), freq="D")
daily = daily.set_index("date").reindex(full, fill_value=0).reset_index()
daily.columns = ["date","tss"]
daily["ctl"] = daily["tss"].ewm(span=42, adjust=False).mean()
daily["atl"] = daily["tss"].ewm(span=7,  adjust=False).mean()
daily["tsb"] = daily["ctl"] - daily["atl"]

# Show values at end of selected period, not always today
if selected_year == "All":
    latest = daily.iloc[-1]
    ctl_period_label = "Current"
else:
    yr_end = daily[daily["date"].dt.year == int(selected_year)]
    latest = yr_end.iloc[-1] if len(yr_end) > 0 else daily.iloc[-1]
    ctl_period_label = f"End of {selected_year}"
t1, t2, t3 = st.columns(3)
tsb = latest["tsb"]
ctl_val = latest["ctl"]
atl_val = latest["atl"]

# ── TSB interpretation ────────────────────────────────────────────────────────
if tsb > 15:
    tsb_label = "Peak form 🟢"
    tsb_advice = (
        "You are at peak freshness. This is the ideal window for racing or testing "
        "your fitness with a hard effort. Don't waste it on easy sessions."
    )
elif tsb > 5:
    tsb_label = "Fresh 🟢"
    tsb_advice = (
        "You're fresh and recovered. Good day for a quality session — intervals, "
        "tempo, or a long effort. Your body is ready to absorb hard training."
    )
elif tsb > -10:
    tsb_label = "Productive zone 🟡"
    tsb_advice = (
        "Light fatigue — this is the normal training zone where fitness is built. "
        "Continue your plan. Mix hard and easy days to keep progressing."
    )
elif tsb > -20:
    tsb_label = "Tired 🟠"
    tsb_advice = (
        "Meaningful fatigue is accumulating. Consider an easy day or rest. "
        "Avoid hard intervals until TSB recovers above -10. Sleep and nutrition matter now."
    )
elif tsb > -30:
    tsb_label = "Very tired 🔴"
    tsb_advice = (
        "High fatigue load. Take 1–2 easy days or full rest. "
        "Performance will suffer if you push hard here. Recovery is training too."
    )
else:
    tsb_label = "Overreaching ⛔"
    tsb_advice = (
        "Danger zone. Extended high fatigue risks illness, injury, or burnout. "
        "Take several easy days. Consider whether your training load is sustainable."
    )

# ── CTL interpretation ────────────────────────────────────────────────────────
if ctl_val < 20:
    ctl_advice = "Low fitness base. Build gradually — increase weekly load by no more than 10% per week."
elif ctl_val < 40:
    ctl_advice = "Moderate fitness. Consistent training is building your base. Keep the routine."
elif ctl_val < 60:
    ctl_advice = "Good fitness base. You can handle harder training blocks and longer events."
elif ctl_val < 80:
    ctl_advice = "Strong fitness. You are well-trained and capable of demanding races."
else:
    ctl_advice = "Elite-level fitness load. Maintain carefully — recovery becomes critical at this level."

# ── ATL interpretation ────────────────────────────────────────────────────────
if atl_val < 20:
    atl_advice = "Very low recent load. You are well rested — consider if you are training enough."
elif atl_val < 40:
    atl_advice = "Moderate recent load. Normal training week. You are not overextending."
elif atl_val < 60:
    atl_advice = "High recent load. Make sure easy days are genuinely easy."
else:
    atl_advice = "Very high recent load. Your body needs recovery. Prioritise sleep and easy sessions."

t1.metric("CTL — Fitness", f"{ctl_val:.1f}", "42-day fitness base")
t2.metric("ATL — Fatigue", f"{atl_val:.1f}", "7-day fatigue load")
t3.metric("TSB — Freshness", f"{tsb:+.1f}", tsb_label)

# ── Expandable guidance cards ─────────────────────────────────────────────────
with st.expander("📖 What do CTL · ATL · TSB mean? Click to read guidance", expanded=False):
    ga, gb, gc = st.columns(3)
    with ga:
        st.markdown(f"""
<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:1rem">
<div style="color:#fc4c02;font-size:0.7rem;font-weight:700;text-transform:uppercase;
            letter-spacing:0.1em;margin-bottom:6px">CTL — Chronic Training Load</div>
<div style="color:#f0ede8;font-size:1.4rem;font-weight:700;margin-bottom:8px">{ctl_val:.1f}</div>
<div style="color:#aaa;font-size:0.8rem;line-height:1.6;margin-bottom:10px">
Your <b style="color:#f0ede8">fitness</b>. A 42-day exponential average of your daily 
training stress. Higher = more fit. Builds slowly, drops slowly.
Takes 6+ weeks of consistent training to move significantly.
</div>
<div style="background:#111;border-left:3px solid #fc4c02;padding:8px 10px;
            border-radius:0 6px 6px 0;font-size:0.78rem;color:#ccc">
💡 {ctl_advice}
</div>
</div>""", unsafe_allow_html=True)

    with gb:
        st.markdown(f"""
<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:1rem">
<div style="color:#ffa500;font-size:0.7rem;font-weight:700;text-transform:uppercase;
            letter-spacing:0.1em;margin-bottom:6px">ATL — Acute Training Load</div>
<div style="color:#f0ede8;font-size:1.4rem;font-weight:700;margin-bottom:8px">{atl_val:.1f}</div>
<div style="color:#aaa;font-size:0.8rem;line-height:1.6;margin-bottom:10px">
Your <b style="color:#f0ede8">fatigue</b>. A 7-day exponential average of your daily 
training stress. Reacts quickly to what you did this week. 
One hard week spikes it; a few easy days drops it fast.
</div>
<div style="background:#111;border-left:3px solid #ffa500;padding:8px 10px;
            border-radius:0 6px 6px 0;font-size:0.78rem;color:#ccc">
💡 {atl_advice}
</div>
</div>""", unsafe_allow_html=True)

    with gc:
        tsb_color = "#50c850" if tsb > 5 else ("#ff6b35" if tsb < -20 else "#ffa500")
        st.markdown(f"""
<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:1rem">
<div style="color:{tsb_color};font-size:0.7rem;font-weight:700;text-transform:uppercase;
            letter-spacing:0.1em;margin-bottom:6px">TSB — Training Stress Balance</div>
<div style="color:#f0ede8;font-size:1.4rem;font-weight:700;margin-bottom:8px">{tsb:+.1f} — {tsb_label}</div>
<div style="color:#aaa;font-size:0.8rem;line-height:1.6;margin-bottom:10px">
Your <b style="color:#f0ede8">freshness</b>. CTL minus ATL. 
Positive = more fit than fatigued → race ready. 
Negative = more fatigued than fit → building phase.
</div>
<div style="background:#111;border-left:3px solid {tsb_color};padding:8px 10px;
            border-radius:0 6px 6px 0;font-size:0.78rem;color:#ccc">
💡 {tsb_advice}
</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""
<div style="margin-top:1rem;padding:0.75rem 1rem;background:#111;border-radius:8px;
            font-size:0.78rem;color:#666;line-height:1.7">
<b style="color:#888">How to use these numbers together:</b><br>
The goal is to raise CTL (fitness) over time while keeping TSB manageable. 
A typical training cycle builds ATL for 3 weeks (TSB goes negative), 
then eases for 1 week so TSB recovers to positive — then you race or test. 
Repeat. Never let TSB drop below −30 for extended periods.
</div>""", unsafe_allow_html=True)

if selected_year == "All":
    days_back = st.slider("Days to show", 90, 1825, 365, step=90, key="ctl_days")
    plot = daily[daily["date"] >= daily["date"].max() - pd.Timedelta(days=days_back)]
else:
    yr_int_ctl = int(selected_year)
    plot = daily[
        (daily["date"] >= pd.Timestamp(f"{yr_int_ctl-1}-10-01")) &
        (daily["date"] <= pd.Timestamp(f"{yr_int_ctl}-12-31"))
    ]

fig1 = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.65,0.35],
    vertical_spacing=0.06,
    subplot_titles=["CTL (fitness) vs ATL (fatigue)", "TSB — freshness"])
fig1.add_trace(go.Bar(x=plot["date"], y=plot["tss"],
    marker_color="rgba(255,255,255,0.06)", name="Daily load"), row=1, col=1)
fig1.add_trace(go.Scatter(x=plot["date"], y=plot["ctl"].round(1),
    mode="lines", line=dict(color="#fc4c02", width=2.5), name="CTL fitness"), row=1, col=1)
fig1.add_trace(go.Scatter(x=plot["date"], y=plot["atl"].round(1),
    mode="lines", line=dict(color="#ffa500", width=2, dash="dot"), name="ATL fatigue"), row=1, col=1)
fig1.add_trace(go.Bar(x=plot["date"], y=plot["tsb"].clip(lower=0).round(1),
    marker_color="rgba(80,200,120,0.5)", name="Fresh"), row=2, col=1)
fig1.add_trace(go.Bar(x=plot["date"], y=plot["tsb"].clip(upper=0).round(1),
    marker_color="rgba(255,80,80,0.45)", name="Fatigued"), row=2, col=1)
fig1.add_hline(y=0, line_width=1, line_color="#333", row=2, col=1)
fig1.update_layout(**CHART_LAYOUT, height=460, barmode="relative",
    title_font=dict(color="#666"))
for r in [1,2]:
    fig1.update_xaxes(**axis_style(), row=r, col=1)
    fig1.update_yaxes(**axis_style(), row=r, col=1)
for ann in fig1.layout.annotations:
    ann.font.color = "#555"
    ann.font.size  = 11
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ── Weekly Volume ─────────────────────────────────────────────────────────────
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
        <div style="color:#e8e4de;font-size:2rem;font-weight:700;
                    font-family:'DM Mono',monospace;line-height:1;min-width:120px">
          {this_h}h&nbsp;{this_m:02d}m
        </div>
        <div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;
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

st.markdown("---")

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
    cyc_colors = {"Ride":"#ffa500","Virtual Ride":"#ffcc44","E-Bike Ride":"#ce93d8"}
    if selected_year == "All":
        cyc = df[df["sport"].isin(cycling_types)].copy()
        yr_cyc = cyc.groupby(["year","sport"])["dist_km"].sum().reset_index()
        cyc_pivot = yr_cyc.pivot_table(index="year", columns="sport",
            values="dist_km", aggfunc="sum", fill_value=0).reset_index()
        fig_c = go.Figure()
        for ctype in cycling_types:
            if ctype not in cyc_pivot.columns: continue
            fig_c.add_trace(go.Bar(
                x=cyc_pivot["year"].astype(int), y=cyc_pivot[ctype].round(),
                name=ctype,
                marker=dict(color=cyc_colors[ctype], line=dict(width=0)),
                width=0.35,
                hovertemplate=ctype + ": <b>%{y:,.0f} km</b><extra></extra>"))
        fig_c.update_layout(**{**CHART_LAYOUT, "margin": dict(t=10,b=30,l=40,r=10)},
            barmode="stack", height=300, yaxis_title="km")
        fig_c.update_xaxes(**axis_style(), dtick=1, tickformat="d")
        fig_c.update_yaxes(**axis_style())
        st.plotly_chart(fig_c, use_container_width=True)
    else:
        cyc_m = fdf[fdf["sport"].isin(cycling_types)].copy()
        cyc_m["month_num"]  = cyc_m["date"].dt.month
        cyc_m["month_name"] = cyc_m["date"].dt.strftime("%b")
        mo_cyc = cyc_m.groupby(["month_num","month_name","sport"])["dist_km"].sum().reset_index()
        mo_cyc = mo_cyc.sort_values("month_num")
        if len(mo_cyc) > 0:
            fig_c = go.Figure()
            for ctype in cycling_types:
                s = mo_cyc[mo_cyc["sport"]==ctype]
                if len(s)==0: continue
                fig_c.add_trace(go.Bar(
                    x=s["month_name"], y=s["dist_km"].round(1),
                    name=ctype, marker_color=cyc_colors[ctype]))
            fig_c.update_layout(**{**CHART_LAYOUT, "margin": dict(t=10,b=30,l=40,r=10)},
                barmode="stack", height=300, yaxis_title="km")
            fig_c.update_xaxes(**axis_style())
            fig_c.update_yaxes(**axis_style())
            st.plotly_chart(fig_c, use_container_width=True)
        else:
            st.info("No cycling data for this year.")
st.markdown("---")

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
st.markdown("---")

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

st.dataframe(
    recent_acts[["Date","sport","name","Km","Time","Pace","HR","Elev"]]
    .rename(columns={"sport":"Sport","name":"Activity"}),
    use_container_width=True, hide_index=True,
    column_config={
        "Date":     st.column_config.TextColumn("Date", width="small"),
        "Sport":    st.column_config.TextColumn("Sport", width="small"),
        "Activity": st.column_config.TextColumn("Activity"),
        "Km":       st.column_config.NumberColumn("Km", format="%.1f"),
        "Time":     st.column_config.TextColumn("Time", width="small"),
        "Pace":     st.column_config.TextColumn("Pace", width="small"),
        "HR":       st.column_config.TextColumn("HR ♥", width="small"),
        "Elev":     st.column_config.TextColumn("Elev", width="small"),
    }
)

st.markdown("""
<div style="margin-top:3rem;padding-top:1rem;border-top:1px solid #222;
            color:#444;font-size:0.75rem;text-align:center">
  Built on Strava data · Powered by Streamlit
</div>
""", unsafe_allow_html=True)
st.markdown("---")

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
<div style="background:#111;border:1px solid #222;border-radius:8px;
            padding:0.75rem 1rem;margin-top:8px;font-size:0.78rem">
  <div style="display:flex;justify-content:space-between;align-items:flex-start">
    <div>
      <div style="color:#666;font-size:0.65rem;margin-bottom:2px">{date_str}</div>
      <div style="color:#d4d0ca;font-weight:600;margin-bottom:4px">{name}</div>
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

st.markdown("""
<div style="margin-top:3rem;padding-top:1rem;border-top:1px solid #222;
            color:#444;font-size:0.75rem;text-align:center">
  Built on Strava data · Powered by Streamlit
</div>
""", unsafe_allow_html=True)
