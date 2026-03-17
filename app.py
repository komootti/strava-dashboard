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
    color: #f0ede8;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #161616 !important;
    border-right: 1px solid #2a2a2a;
}
[data-testid="stSidebar"] * {
    color: #c8c4be !important;
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
    color: #888 !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
[data-testid="stMetricValue"] {
    color: #f0ede8 !important;
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
    font=dict(family="DM Sans", color="#888", size=11),
    margin=dict(t=30, b=30, l=50, r=20),
    legend=dict(
        orientation="h", y=1.08,
        font=dict(color="#c8c4be", size=11),
        bgcolor="rgba(0,0,0,0)"
    ),
)

def axis_style():
    return dict(
        gridcolor="#222",
        linecolor="#333",
        tickcolor="#444",
        tickfont=dict(color="#666", size=10),
        zerolinecolor="#333",
    )

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

    # ── Year pills ────────────────────────────────────────────────────────────
    st.markdown("**Year**")
    year_options = ["All"] + [str(y) for y in all_years]
    cols_per_row = 3
    for row_start in range(0, len(year_options), cols_per_row):
        row_opts = year_options[row_start:row_start + cols_per_row]
        row_cols = st.columns(len(row_opts))
        for col, yr in zip(row_cols, row_opts):
            is_active = st.session_state["selected_year"] == yr
            if col.button(yr, key=f"yr_{yr}", use_container_width=True,
                          type="primary" if is_active else "secondary"):
                st.session_state["selected_year"] = yr
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
  <div style="color:#555;font-size:0.85rem;margin-top:4px">
    {'📅 ' + selected_year if selected_year != 'All' else df['date'].min().strftime('%b %Y') + ' — ' + df['date'].max().strftime('%b %Y') + ' · ' + str(df['year'].nunique()) + ' years'}
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

r1, r2, r3, r4, r5, r6 = st.columns(6)
with r1:
    v = runs_valid["dist_km"].max() if len(runs_valid) else 0
    st.markdown(f'<div class="record-card"><div class="record-label">Longest Run</div>'
                f'<div class="record-value">{v:.1f}</div>'
                f'<div class="record-sub">km</div></div>', unsafe_allow_html=True)
with r2:
    v = runs_valid["pace_min_km"].min() if len(runs_valid) else None
    st.markdown(f'<div class="record-card"><div class="record-label">Best Pace</div>'
                f'<div class="record-value">{fmt_pace(v)}</div>'
                f'<div class="record-sub">min/km</div></div>', unsafe_allow_html=True)
with r3:
    v = runs_valid["elev_gain_m"].max() if len(runs_valid) else 0
    st.markdown(f'<div class="record-card"><div class="record-label">Most Climbing</div>'
                f'<div class="record-value">{v:,.0f}</div>'
                f'<div class="record-sub">metres</div></div>', unsafe_allow_html=True)
with r4:
    v = rides_all["dist_km"].max() if len(rides_all) else 0
    st.markdown(f'<div class="record-card"><div class="record-label">Longest Ride</div>'
                f'<div class="record-value">{v:.0f}</div>'
                f'<div class="record-sub">km</div></div>', unsafe_allow_html=True)
with r5:
    v = len(df[df["sport"]=="Run"])
    st.markdown(f'<div class="record-card"><div class="record-label">Total Runs</div>'
                f'<div class="record-value">{v:,}</div>'
                f'<div class="record-sub">activities</div></div>', unsafe_allow_html=True)
with r6:
    v = df[df["sport"].isin(["Ride","Virtual Ride"])]["dist_km"].sum()
    st.markdown(f'<div class="record-card"><div class="record-label">Total Ride km</div>'
                f'<div class="record-value">{v:,.0f}</div>'
                f'<div class="record-sub">km</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── CTL / ATL / TSB ───────────────────────────────────────────────────────────
st.markdown("## Training Load — CTL · ATL · TSB")

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

latest = daily.iloc[-1]
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

days_back = st.slider("Days to show", 90, 1825, 365, step=90, key="ctl_days")
plot = daily[daily["date"] >= daily["date"].max() - pd.Timedelta(days=days_back)]

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
    fig2.add_trace(go.Bar(x=weekly_pivot["week"], y=weekly_pivot[sport].round(1),
        name=sport, marker_color=SPORT_COLORS.get(sport,"#666")))
fig2.update_layout(**CHART_LAYOUT, barmode="stack", height=320, yaxis_title="km")
fig2.update_xaxes(**axis_style())
fig2.update_yaxes(**axis_style())
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── Yearly volumes side by side ───────────────────────────────────────────────
st.markdown("## Yearly Volume")
col_run, col_ride = st.columns(2)

with col_run:
    st.markdown("### 🏃 Running")
    yr_run = fdf[fdf["sport"]=="Run"].groupby("year")["dist_km"].sum().reset_index()
    fig_r = go.Figure(go.Bar(
        x=yr_run["year"], y=yr_run["dist_km"],
        marker=dict(
            color=yr_run["dist_km"],
            colorscale=[[0,"#3a1a0a"],[0.5,"#c03000"],[1,"#fc4c02"]],
            showscale=False),
        text=yr_run["dist_km"].round().astype(int).astype(str)+" km",
        textposition="outside",
        textfont=dict(color="#888", size=10)))
    fig_r.update_layout(**{**CHART_LAYOUT, 'margin': dict(t=10,b=30,l=40,r=10)},
        height=300, yaxis_title="km")
    fig_r.update_xaxes(**axis_style())
    fig_r.update_yaxes(**axis_style())
    st.plotly_chart(fig_r, use_container_width=True)

with col_ride:
    st.markdown("### 🚴 Cycling")
    cycling_types = ["Ride","Virtual Ride","E-Bike Ride"]
    # Use full df filtered only by date so sport filter never hides cycling types
    cyc = df[(df["sport"].isin(cycling_types)) &
             (df["date"].dt.date >= start_date) &
             (df["date"].dt.date <= end_date)]
    yr_cyc = cyc.groupby(["year","sport"])["dist_km"].sum().reset_index()
    cyc_colors = {"Ride":"#ffa500","Virtual Ride":"#ffcc44","E-Bike Ride":"#ce93d8"}
    # Pivot so every year gets a bar even if one type is missing that year
    cyc_pivot = yr_cyc.pivot_table(index="year", columns="sport",
                                    values="dist_km", aggfunc="sum", fill_value=0).reset_index()
    fig_c = go.Figure()
    for ctype in cycling_types:
        if ctype not in cyc_pivot.columns: continue
        fig_c.add_trace(go.Bar(x=cyc_pivot["year"], y=cyc_pivot[ctype].round(),
            name=ctype, marker_color=cyc_colors[ctype]))
    yr_cyc_tot = cyc.groupby("year")["dist_km"].sum().reset_index()
    fig_c.add_trace(go.Scatter(x=yr_cyc_tot["year"], y=yr_cyc_tot["dist_km"].round(),
        mode="text",
        text=yr_cyc_tot["dist_km"].round().astype(int).astype(str)+" km",
        textposition="top center",
        textfont=dict(size=10, color="#666"), showlegend=False))
    fig_c.update_layout(**{**CHART_LAYOUT, 'margin': dict(t=10,b=30,l=40,r=10)},
        barmode="stack", height=300, yaxis_title="km")
    fig_c.update_xaxes(**axis_style())
    fig_c.update_yaxes(**axis_style())
    st.plotly_chart(fig_c, use_container_width=True)

st.markdown("---")

# ── Yearly Elevation ──────────────────────────────────────────────────────────
st.markdown("## Yearly Elevation Gain")
col_run_elev, col_ride_elev = st.columns(2)

with col_run_elev:
    st.markdown("### 🏃 Running")
    yr_run_elev = (df[df["sport"] == "Run"]
                   .groupby("year")["elev_gain_m"].sum().reset_index())
    yr_run_elev = yr_run_elev[yr_run_elev["elev_gain_m"] > 0]
    if len(yr_run_elev) > 0:
        fig_re = go.Figure(go.Bar(
            x=yr_run_elev["year"],
            y=yr_run_elev["elev_gain_m"].round(),
            marker=dict(
                color=yr_run_elev["elev_gain_m"],
                colorscale=[[0,"#1a2a1a"],[0.5,"#2d7a2d"],[1,"#50c850"]],
                showscale=False),
            text=yr_run_elev["elev_gain_m"].round().astype(int).astype(str) + " m",
            textposition="outside",
            textfont=dict(color="#888", size=10)))
        if selected_year != "All":
            fig_re.add_vline(x=int(selected_year), line_color="#fc4c02",
                             line_width=2, line_dash="dot")
        fig_re.update_layout(**{**CHART_LAYOUT, "margin": dict(t=10,b=30,l=50,r=10)},
            height=300, yaxis_title="metres")
        fig_re.update_xaxes(**axis_style())
        fig_re.update_yaxes(**axis_style())
        st.plotly_chart(fig_re, use_container_width=True)

with col_ride_elev:
    st.markdown("### 🚴 Cycling")
    cycling_types_e = ["Ride", "Virtual Ride", "E-Bike Ride"]
    yr_ride_elev = (df[df["sport"].isin(cycling_types_e)]
                    .groupby(["year","sport"])["elev_gain_m"].sum().reset_index())
    yr_ride_elev = yr_ride_elev[yr_ride_elev["elev_gain_m"] > 0]
    if len(yr_ride_elev) > 0:
        cyc_elev_colors = {"Ride":"#ffa500","Virtual Ride":"#ffcc44","E-Bike Ride":"#ce93d8"}
        elev_pivot = yr_ride_elev.pivot_table(index="year", columns="sport",
            values="elev_gain_m", aggfunc="sum", fill_value=0).reset_index()
        fig_ce = go.Figure()
        for ctype in cycling_types_e:
            if ctype not in elev_pivot.columns: continue
            fig_ce.add_trace(go.Bar(
                x=elev_pivot["year"], y=elev_pivot[ctype].round(),
                name=ctype, marker_color=cyc_elev_colors[ctype]))
        yr_ride_tot = (df[df["sport"].isin(cycling_types_e)]
                       .groupby("year")["elev_gain_m"].sum().reset_index())
        fig_ce.add_trace(go.Scatter(
            x=yr_ride_tot["year"], y=yr_ride_tot["elev_gain_m"].round(),
            mode="text",
            text=yr_ride_tot["elev_gain_m"].round().astype(int).astype(str) + " m",
            textposition="top center",
            textfont=dict(size=10, color="#666"), showlegend=False))
        if selected_year != "All":
            fig_ce.add_vline(x=int(selected_year), line_color="#fc4c02",
                             line_width=2, line_dash="dot")
        fig_ce.update_layout(**{**CHART_LAYOUT, "margin": dict(t=10,b=30,l=50,r=10)},
            barmode="stack", height=300, yaxis_title="metres")
        fig_ce.update_xaxes(**axis_style())
        fig_ce.update_yaxes(**axis_style())
        st.plotly_chart(fig_ce, use_container_width=True)

st.markdown("---")

# ── Aerobic efficiency ────────────────────────────────────────────────────────
st.markdown("## Aerobic Efficiency")

run_eff = fdf[(fdf["sport"]=="Run") & (fdf["dist_km"]>3)].copy()
run_eff["pace_min_km"] = pd.to_numeric(run_eff["pace_min_km"], errors="coerce")
run_eff = run_eff[run_eff["pace_min_km"].between(4,12) & run_eff["avg_hr"].notna()]

if len(run_eff) > 0:
    yr_eff = run_eff.groupby("year").agg(
        avg_hr=("avg_hr","mean"), avg_pace=("pace_min_km","mean")).reset_index()
    fig3 = make_subplots(rows=1, cols=2, horizontal_spacing=0.1,
        subplot_titles=["Avg HR per year (lower = fitter)",
                        "Avg pace per year (lower = faster)"])
    fig3.add_trace(go.Scatter(x=yr_eff["year"], y=yr_eff["avg_hr"].round(1),
        mode="lines+markers", line=dict(color="#fc4c02", width=2.5),
        marker=dict(size=7, color="#fc4c02",
                    line=dict(color="#0f0f0f", width=2))), row=1, col=1)
    fig3.add_trace(go.Scatter(x=yr_eff["year"], y=yr_eff["avg_pace"].round(2),
        mode="lines+markers", line=dict(color="#ffa500", width=2.5),
        marker=dict(size=7, color="#ffa500",
                    line=dict(color="#0f0f0f", width=2))), row=1, col=2)
    fig3.update_layout(**CHART_LAYOUT, height=300, showlegend=False)
    for r in [1,2]:
        fig3.update_xaxes(**axis_style(), row=r, col=1)
        fig3.update_yaxes(**axis_style(), row=r, col=1)
    fig3.update_yaxes(autorange="reversed", row=1, col=2)
    for ann in fig3.layout.annotations:
        ann.font.color = "#555"; ann.font.size = 11
    st.plotly_chart(fig3, use_container_width=True)

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
