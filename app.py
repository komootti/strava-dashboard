import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import io

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Petteri · Training",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Strava-inspired dark theme ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-weight: 400;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* ── Typography — lighter, more refined ── */
h1 {
    font-weight: 300 !important;
    letter-spacing: -0.03em !important;
    line-height: 1.1 !important;
}
h2 {
    font-weight: 300 !important;
    font-size: 1.6rem !important;
    letter-spacing: -0.03em !important;
    line-height: 1.2 !important;
}
h3 {
    font-weight: 400 !important;
    font-size: 1.25rem !important;
    letter-spacing: -0.02em !important;
}
h4 {
    font-weight: 500 !important;
    letter-spacing: -0.01em !important;
}
/* Streamlit markdown headers */
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-weight: 300 !important;
    letter-spacing: -0.03em !important;
}
.stMarkdown h2 { font-size: 1.6rem !important; }
.stMarkdown h3 { font-size: 1.25rem !important; }
/* Sidebar nav labels */
[data-testid="stSidebar"] label {
    font-weight: 400 !important;
    letter-spacing: 0.02em !important;
}
/* Metric labels */
[data-testid="stMetricLabel"] {
    font-weight: 400 !important;
    letter-spacing: 0.05em !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-weight: 300 !important;
    letter-spacing: -0.02em !important;
}
/* Selectbox and widget labels */
.stSelectbox label, .stMultiSelect label, .stSlider label {
    font-weight: 400 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}
/* Caption text */
.stCaption {
    font-weight: 300 !important;
    font-size: 0.78rem !important;
}
/* Tab labels */
.stTabs [data-baseweb="tab"] {
    font-weight: 400 !important;
    letter-spacing: 0.03em !important;
    font-size: 0.82rem !important;
}
/* Body paragraphs */
.stMarkdown p {
    font-weight: 300 !important;
    line-height: 1.65 !important;
}

/* ── Background — pure white, no off-white ── */
.stApp {
    background-color: #ffffff;
    color: #1a1a1a;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #fafafa !important;
    border-right: 1px solid #f0f0f0 !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.04) !important;
}
[data-testid="stSidebar"] * { color: #333 !important; }
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #ffffff !important;
    border: 1px solid #e8e8e8 !important;
    border-radius: 10px !important;
    color: #1a1a1a !important;
}

/* ── Main container ── */
.block-container {
    padding: 1.2rem 2rem 1.2rem 2rem !important;
    max-width: 1400px;
}

/* ── Metric cards — elevated with 3 shadow levels ── */
[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #f0f0f0;
    border-radius: 16px;
    padding: 1.2rem 1.4rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s, transform 0.2s;
}
[data-testid="metric-container"]:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.10);
    transform: translateY(-1px);
}
[data-testid="stMetricLabel"] {
    color: #999 !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
[data-testid="stMetricValue"] {
    color: #1a1a1a !important;
    font-size: 2.4rem !important;
    font-weight: 700 !important;
    font-family: 'DM Mono', monospace !important;
    line-height: 1.1;
}
[data-testid="stMetricDelta"] {
    font-size: 0.78rem !important;
}

/* ── Section headers — no underline, just weight + spacing ── */
h2 {
    color: #1a1a1a !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin-top: 2rem !important;
    margin-bottom: 1rem !important;
    padding-bottom: 0;
    border-bottom: none !important;
    display: block;
    color: #888 !important;
}

h3 {
    color: #1a1a1a !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
}

h1 {
    color: #1a1a1a !important;
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em;
}

/* ── Divider ── */
hr {
    border-color: #f0f0f0 !important;
    margin: 1rem 0 !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #f0f0f0;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* ── Buttons ── */
.stButton > button {
    background: #fc4c02 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.2rem !important;
    transition: opacity 0.2s, transform 0.15s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ── Record cards ── */
.record-card {
    background: #ffffff;
    border: 1px solid #f0f0f0;
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: box-shadow 0.2s;
}
.record-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.10); }
.record-label {
    color: #999;
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.record-value {
    color: #fc4c02;
    font-size: 1.8rem;
    font-weight: 700;
    font-family: 'DM Mono', monospace;
    line-height: 1.2;
}
.record-sub { color: #999; font-size: 0.75rem; margin-top: 0.1rem; }

/* ── Sport badge ── */
.sport-badge {
    display: inline-block;
    background: #fc4c02;
    color: white;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 2px 8px;
    border-radius: 6px;
    margin-right: 4px;
}

/* ── Selectbox ── */
[data-testid="stSidebar"] .stSelectbox > div > div:hover { border-color: #fc4c02 !important; }
[data-baseweb="tag"] { background-color: #fc4c02 !important; border-radius: 6px !important; }
[data-testid="stSlider"] > div > div > div { background-color: #fc4c02 !important; }

/* ── Dark mode support (activated via session state) ── */
.dark-mode .stApp { background: #0f0f0f !important; color: #e8e8e8 !important; }
.dark-mode [data-testid="metric-container"] { background: #1a1a1a !important; border-color: #2a2a2a !important; }

/* ── Mobile ── */
@media (max-width: 768px) {
    .block-container { padding: 1rem !important; }
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; }
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

OURA_RAW_URL   = "https://raw.githubusercontent.com/komootti/strava-dashboard/main/oura_data.json"
FITBOD_RAW_URL = "https://raw.githubusercontent.com/komootti/strava-dashboard/main/fitbod_data.json"

@st.cache_data(ttl=300)
def load_fitbod():
    try:
        r = requests.get(FITBOD_RAW_URL, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

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

MUSCLE_COLORS = {
    "Upper": "#fc4c02",
    "Lower": "#ffa500",
    "Core":  "#a78bfa",
    "Other": "#94a3b8",
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
        marker=dict(color=color, size=9, line=dict(color="#ffffff", width=2.5)),
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
oura_df     = load_oura()
fitbod_data = load_fitbod()

# ── Sidebar ───────────────────────────────────────────────────────────────────
# ── Year filter state ────────────────────────────────────────────────────────
all_years = sorted(df["year"].dropna().unique().astype(int).tolist(), reverse=True)
if "selected_year" not in st.session_state:
    st.session_state["selected_year"] = "All"

with st.sidebar:
    st.markdown("## 🔥 Filters")

    # Dark mode toggle
    _dark = st.toggle("🌙 Dark mode", value=False, key="dark_mode")
    # Card colors adapt to dark mode — used in all HTML card f-strings
    _card_bg     = "#161616" if _dark else "#ffffff"
    _card_border = "#2a2a2a" if _dark else "#e2ddd8"
    _card_bg2    = "#1e1e1e" if _dark else "#f7f7f7"
    _card_text   = "#e2e2e2" if _dark else "#1a1a1a"
    _card_sub    = "#666666" if _dark else "#888888"
    _card_tint_o = "#1e120e" if _dark else "#fff8f5"
    _card_tint_p = "#130f1e" if _dark else "#f5f0ff"
    _card_tint_g = "#0d1a0d" if _dark else "#f0fdf0"
    _border_o    = "#3d1f0e" if _dark else "#fce0d0"
    _border_p    = "#2a1f3d" if _dark else "#e2ddd8"
    _border_g    = "#1a3d1a" if _dark else "#c8ecc8"
    if _dark:
        st.markdown("""<style>
        /* ── Base ── */
        .stApp { background-color: #0d0d0d !important; color: #e2e2e2 !important; }
        .stApp > div { background-color: #0d0d0d !important; }
        [data-testid="stAppViewContainer"] { background-color: #0d0d0d !important; }
        [data-testid="stHeader"] { background-color: #0d0d0d !important; }
        [data-testid="stMain"] { background-color: #0d0d0d !important; }
        [data-testid="block-container"] { background-color: #0d0d0d !important; }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] { background-color: #111111 !important; border-right: 1px solid #222 !important; }
        [data-testid="stSidebar"] * { color: #aaa !important; }
        [data-testid="stSidebar"] .stSelectbox > div > div { background: #1a1a1a !important; border-color: #333 !important; color: #e2e2e2 !important; }

        /* ── Typography ── */
        h1,h2,h3,h4,p,span,div,label,td,th { color: #e2e2e2 !important; }
        hr { border-color: #222 !important; }

        /* ── ALL white/light background elements → dark ── */
        div[style*="background:{_card_bg}"],
        div[style*="background: #ffffff"],
        div[style*="background:white"],
        div[style*="background: white"],
        div[style*="background:#fff8f5"],
        div[style*="background:#f7f5f2"],
        div[style*="background:#f5f0ff"],
        div[style*="background:#f7f7f7"],
        div[style*="background:#f0fdf0"],
        div[style*="background:#f5fbf5"],
        span[style*="background:{_card_bg}"],
        span[style*="background:#f5f0ff"],
        span[style*="background:#f0fdf0"] {
            background: #1a1a1a !important;
        }
        /* Keep accent borders but darken bg */
        div[style*="border-left:4px solid #fc4c02"],
        div[style*="border-left: 4px solid #fc4c02"] { background: #1e120e !important; }
        div[style*="border-left:4px solid #a78bfa"],
        div[style*="border-left: 4px solid #a78bfa"] { background: #130f1e !important; }
        div[style*="border-left:4px solid #50c8"] { background: #0d1a0d !important; }

        /* ── All borders → dark ── */
        div[style*="border:1px solid #e"],
        div[style*="border: 1px solid #e"],
        div[style*="border:1px solid #f"],
        div[style*="border: 1px solid #f"] { border-color: #2a2a2a !important; }
        div[style*="border-bottom:1px solid #e"],
        div[style*="border-bottom: 1px solid #e"] { border-bottom-color: #2a2a2a !important; }

        /* ── Dash cards (CTL/ATL/TSB) ── */
        .dash-card { background: #161616 !important; border: 1px solid #252525 !important; box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important; }
        .card-label { color: #666 !important; }
        .card-value { color: #ffffff !important; }
        .card-sub   { color: #555 !important; }
        .card-tooltip { background: #1e1e1e !important; border-color: #333 !important; color: #ccc !important; }
        .card-tooltip * { color: #ccc !important; }

        /* ── Goal rings ── */
        .ring-card  { background: #161616 !important; border-color: #252525 !important; }
        .ring-label { color: #aaa !important; }

        /* ── Counter grid (all-time stats) ── */
        .ctr-card  { background: #161616 !important; border-color: #252525 !important; box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important; }
        .ctr-label { color: #666 !important; }
        .ctr-val   { color: #ffffff !important; }
        .ctr-unit  { color: #555 !important; }

        /* ── Record cards ── */
        .record-card  { background: #161616 !important; border: 1px solid #252525 !important; }
        .record-label { color: #666 !important; }
        .record-value { color: #fc4c02 !important; }
        .record-sub   { color: #555 !important; }

        /* ── Heatmap ── */
        .hm-cell { background: #1a1a1a !important; }
        .hm-select li:hover { background: #2a2a2a !important; }

        /* ── Tables ── */
        table { background: #161616 !important; }
        tr { border-bottom: 1px solid #222 !important; }
        tr:hover { background: #1e1e1e !important; }
        td, th { color: #aaa !important; border-color: #222 !important; }

        /* ── Plotly ── */
        .js-plotly-plot .bg { fill: #161616 !important; }
        .js-plotly-plot .gridlayer path { stroke: #2a2a2a !important; }

        /* ── Streamlit widgets ── */
        [data-testid="stSelectbox"] > div > div { background: #1a1a1a !important; border-color: #333 !important; color: #e2e2e2 !important; }
        [data-testid="stMetricValue"] { color: #ffffff !important; }
        [data-testid="stMetricLabel"] { color: #666 !important; }
        [data-testid="metric-container"] { background: #161616 !important; border-color: #252525 !important; }
        .stTabs [data-baseweb="tab-list"] { background: #111 !important; border-bottom: 1px solid #222 !important; }
        .stTabs [data-baseweb="tab"] { color: #666 !important; }
        .stTabs [aria-selected="true"] { color: #fc4c02 !important; border-bottom-color: #fc4c02 !important; }
        [data-testid="stDataFrame"] { background: #161616 !important; }
        .stMarkdown p { color: #aaa !important; }

        /* ── Force white text on dark backgrounds ── */
        [style*="color:{_card_text}"], [style*="color: #1a1a1a"] { color: #e2e2e2 !important; }
        [style*="color:#888"], [style*="color: #888"] { color: #666 !important; }
        [style*="color:{_card_text}"], [style*="color: #333"] { color: #ccc !important; }
        [style*="color:#555"], [style*="color: #555"] { color: #777 !important; }
        /* ── Override inline styles more aggressively ── */
        /* Activity card, oura cards, strength cards, table wrappers */
        .element-container div[style*="border:1px solid #e"],
        .element-container div[style*="border: 1px solid #e"],
        .element-container div[style*="border:1px solid #f"],
        .stMarkdown div[style*="background:{_card_bg}"],
        .stMarkdown div[style*="background: #ffffff"],
        .stMarkdown div[style*="background:#fff"],
        .element-container div[style*="background:{_card_bg}"],
        .element-container div[style*="background:#fff8f5"],
        .element-container div[style*="background:#f7f5f2"],
        .element-container div[style*="background:#f5fbf5"],
        .element-container div[style*="background:#f0fdf0"],
        .element-container div[style*="background:#f5f0ff"] {
            background: #161616 !important;
            border-color: #2a2a2a !important;
            color: #e2e2e2 !important;
        }
        /* Text colors inside dark cards */
        .element-container div[style*="background:{_card_bg}"] *,
        .element-container div[style*="background:#fff8f5"] *,
        .element-container div[style*="background:#f5fbf5"] * {
            color: #e2e2e2 !important;
        }
        /* Sub-labels stay dimmed */
        .element-container div[style*="color:#888"] { color: #666 !important; }
        .element-container div[style*="color:#aaa"] { color: #555 !important; }
        .element-container span[style*="color:#888"] { color: #666 !important; }
        .element-container span[style*="color:#aaa"] { color: #555 !important; }
        /* Section headers */
        .stMarkdown h2, .stMarkdown h3 { color: #e2e2e2 !important; }
        /* Streamlit columns */
        [data-testid="column"] { background: transparent !important; }
        </style>""", unsafe_allow_html=True)

    st.markdown('<hr style="border:none;border-top:1px solid #f0f0f0;margin:0.8rem 0">', unsafe_allow_html=True)

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
</div></div>
""", unsafe_allow_html=True)



# ── Pre-compute CTL/ATL/TSB for use in AI section ───────────────────────────
_end2_pre = df[df["is_endurance"]].copy()
_end2_pre["tss"] = _end2_pre["rel_effort"].fillna(
    _end2_pre["moving_min"] * (_end2_pre["avg_hr"].fillna(130) / 150) ** 2 * 0.5)
_daily_pre = _end2_pre.groupby(_end2_pre["date"].dt.normalize())["tss"].sum().reset_index()
_daily_pre.columns = ["date","tss"]
_daily_pre["date"] = pd.to_datetime(_daily_pre["date"])
_full_pre = pd.date_range(_daily_pre["date"].min(), pd.Timestamp.now().normalize(), freq="D")
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
_wk_start_p  = pd.Timestamp.now().normalize() - pd.Timedelta(days=pd.Timestamp.now().dayofweek)
_prev_start_p= _wk_start_p - pd.Timedelta(weeks=1)
_this_h = _end_h_pre[_end_h_pre["date"] >= _wk_start_p]["moving_min"].sum() / 60
_last_h = _end_h_pre[(_end_h_pre["date"] >= _prev_start_p) &
                      (_end_h_pre["date"] < _wk_start_p)]["moving_min"].sum() / 60


# ── Tab navigation ───────────────────────────────────────────────────────────

# ── Tab navigation ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊  Overview", "🏃  Training", "💪  Strength", "📋  History"])

with tab1:
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
        if la_effort < 8:    effort_lbl, effort_col = "Recovery", "#50c850"
        elif la_effort < 36: effort_lbl, effort_col = "Base",     "#ffa500"
        elif la_effort < 95: effort_lbl, effort_col = "Quality",  "#ff6b35"
        else:                effort_lbl, effort_col = "Peak",     "#fc4c02"
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
    _wk_bg    = '#e8f8e8' if _wk_d >= 0 else '#fef2f2'
    _wk_badge = (
        '<span style="background:' + _wk_bg + ';color:' + _wk_col + ';font-size:0.72rem;font-weight:600;padding:3px 10px;border-radius:999px">' + _wk_arr + ' ' + str(round(abs(_wk_d),1)) + ' km</span>'
        + '<span style="color:#aaa;font-size:0.72rem"> vs last week</span>'
    ) if last_wk_km > 0 else ''
    # next line placeholder

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
    if not _la_poly and fitbod_data:
        # No GPS activity — show Fitbod last session as fallback card
        _fb_sess_tmp = pd.DataFrame(fitbod_data.get("sessions",[]))
        _fb_sets_tmp = pd.DataFrame(fitbod_data.get("sets",[]))
        if len(_fb_sess_tmp) > 0 and len(_fb_sets_tmp) > 0:
            _fb_sess_tmp["date"] = pd.to_datetime(_fb_sess_tmp["date"])
            _fb_sets_tmp["date"] = pd.to_datetime(_fb_sets_tmp["date"])
            _last_fb = _fb_sess_tmp.iloc[0]
            _last_fb_date = _last_fb["date"].strftime("%a %d %b %Y")
            _last_fb_sets = _fb_sets_tmp[_fb_sets_tmp["date"].dt.date == _last_fb["date"].date()]
            _top_moves = _last_fb_sets.groupby("exercise")["sets"].sum().nlargest(5).reset_index()
            _move_pills = "".join([
                f'<span style="background:{_card_tint_p};color:#7c3aed;font-size:0.7rem;font-weight:600;padding:3px 10px;border-radius:999px;margin-right:6px;margin-bottom:4px;display:inline-block">'
                f'{r["exercise"][:22]} · {int(r["sets"])}×</span>'
                for _, r in _top_moves.iterrows()
            ])
            _fb_vol = f"{_last_fb['total_volume']/1000:.1f}t" if _last_fb.get("total_volume",0) > 0 else "—"
            _fb_grps = ", ".join(_last_fb["muscle_groups"]) if isinstance(_last_fb.get("muscle_groups"), list) else "—"
            st.markdown(
                '<div style="background:{_card_bg};border:1px solid {_card_border};border-left:4px solid #a78bfa;'
                'border-radius:12px;padding:1.2rem 1.4rem;margin-bottom:0.8rem;box-shadow:0 2px 8px rgba(0,0,0,0.06)">'
                '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px">'
                f'<div style="color:#888;font-size:0.62rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em">Latest Strength Session · {_last_fb_date}</div>'
                '<span style="background:{_card_tint_p};color:#7c3aed;font-size:0.62rem;font-weight:700;padding:3px 10px;border-radius:999px">STRENGTH</span>'
                '</div>'
                f'<div style="display:flex;gap:24px;margin-bottom:12px">'
                f'<div><div style="color:{_card_text};font-size:1.8rem;font-weight:700;font-family:DM Mono,monospace;line-height:1">{_fb_vol}</div><div style="color:#aaa;font-size:0.7rem">total volume</div></div>'
                f'<div><div style="color:{_card_text};font-size:1.8rem;font-weight:700;font-family:DM Mono,monospace;line-height:1">{int(_last_fb["total_sets"])}</div><div style="color:#aaa;font-size:0.7rem">sets</div></div>'
                f'<div><div style="color:{_card_text};font-size:1.8rem;font-weight:700;font-family:DM Mono,monospace;line-height:1">{int(_last_fb["exercises"])}</div><div style="color:#aaa;font-size:0.7rem">exercises</div></div>'
                f'<div><div style="color:#888;font-size:0.9rem;font-weight:600;margin-top:4px">{_fb_grps}</div><div style="color:#aaa;font-size:0.7rem">muscle groups</div></div>'
                '</div>'
                f'<div style="display:flex;flex-wrap:wrap;gap:4px">{_move_pills}</div>'
                '</div>',
                unsafe_allow_html=True
            )

    if _la_poly:
        _la_coords = decode_polyline(_la_poly)
        if _la_coords:
            try:
                import folium
                from streamlit_folium import st_folium
                _c1, _c2 = st.columns([1, 1])
                with _c1:
                    _effort_tag = (
                        f'<span style="background:{effort_col}22;border:1px solid {effort_col}55;color:{effort_col};'
                        f'font-size:0.7rem;font-weight:600;padding:2px 8px;border-radius:999px">'
                        + effort_lbl + '</span>'
                    ) if effort_lbl else ""
                    st.markdown(
                        f'<div style="background:{_card_bg};border:1px solid {_card_border};border-radius:12px;'
                        f'padding:1.4rem;height:220px;display:flex;flex-direction:column;justify-content:space-between;'
                        f'box-shadow:0 1px 4px rgba(0,0,0,0.06)">'
                        + f'<div>'
                        + f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">'
                        + f'<div style="color:#fc4c02;font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em">{la_sport} · {la_date}</div>'
                        + _effort_tag
                        + '</div>'
                        + f'<div style="color:{_card_text};font-size:1.1rem;font-weight:700;margin-bottom:14px;line-height:1.3">{la_name}</div>'
                        + f'<div style="display:flex;align-items:center;gap:0;flex-wrap:wrap;margin-top:4px">'
                        + (''.join(filter(None, [
                            (f'<div style="padding:0 14px 0 0;border-right:1px solid {_card_border}"><div style="color:{_card_text};font-size:1.6rem;font-weight:300;font-family:\"DM Mono\",monospace;line-height:1;letter-spacing:-0.02em">{la_dist:.1f}</div><div style="color:#888;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.08em;margin-top:3px">km</div></div>' if la_dist > 0 else None),
                            (f'<div style="padding:0 14px;border-right:1px solid {_card_border}"><div style="color:{_card_text};font-size:1.6rem;font-weight:300;font-family:\"DM Mono\",monospace;line-height:1;letter-spacing:-0.02em">{int(la_mins//60)}h {int(la_mins%60):02d}m</div><div style="color:#888;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.08em;margin-top:3px">time</div></div>' if la_mins > 0 else None),
                            (f'<div style="padding:0 14px;border-right:1px solid {_card_border}"><div style="color:{_card_text};font-size:1.6rem;font-weight:300;font-family:\"DM Mono\",monospace;line-height:1;letter-spacing:-0.02em">{la_pace_s}</div><div style="color:#888;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.08em;margin-top:3px">pace</div></div>' if la_pace_s else None),
                            (f'<div style="padding:0 14px;border-right:1px solid {_card_border}"><div style="color:{_card_text};font-size:1.6rem;font-weight:300;font-family:\"DM Mono\",monospace;line-height:1;letter-spacing:-0.02em">{int(la_elev_v)}</div><div style="color:#888;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.08em;margin-top:3px">m elev</div></div>' if la_elev_v > 10 else None),
                            (f'<div style="padding:0 0 0 14px"><div style="color:{_card_text};font-size:1.6rem;font-weight:300;font-family:\"DM Mono\",monospace;line-height:1;letter-spacing:-0.02em">{int(la_hr_v)}</div><div style="color:#888;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.08em;margin-top:3px">bpm</div></div>' if la_hr_v > 0 else None),
                        ])))
                        + '</div></div>'
                        + f'<a href="{_strava_url}" target="_blank" style="color:#fc4c02;font-size:0.72rem;font-weight:600;text-decoration:none">View on Strava ↗</a>'
                        + '</div>',
                        unsafe_allow_html=True
                    )
                with _c2:
                    st_folium(make_folium_map(_la_coords, height=220),
                              use_container_width=True, height=220,
                              returned_objects=[], key="latest_map")
            except ImportError:
                st.caption("Add folium and streamlit-folium to requirements.txt for route maps.")

    # ── AI Athlete Intelligence ──────────────────────────────────────────────────
    @st.cache_data(ttl=86400, show_spinner=False)  # cache 24h — persists across restarts
    def get_ai_analysis(api_key, sport, name, dist, mins, elev, hr, effort_lbl,
                        pace_s, ctl, atl, tsb, tsb_lbl,
                        wk_km, last_wk_km, avg_dist_30, this_wk_h, last_wk_h,
                        recent_sports_str, days_since_rest,
                        oura_readiness=None, oura_hrv=None, oura_hrv_avg=None,
                        oura_rhr=None, oura_sleep=None, oura_sleep_h=None, oura_temp=None):
        """Call Claude to generate activity analysis + next session recommendation.
        Cached by activity_id for 24h — won't re-call API on app restarts."""
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

        import time as _time
        for _attempt in range(3):  # retry up to 3 times
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
                    timeout=25
                )
                if resp.status_code == 200:
                    return resp.json()["content"][0]["text"].strip()
                elif resp.status_code in (529, 503, 502, 500):
                    # Transient server-side overload — wait and retry
                    if _attempt < 2:
                        _time.sleep(3 + _attempt * 2)
                        continue
                    return None  # Give up silently after 3 tries — not user's fault
                else:
                    return f"ERROR {resp.status_code}: {resp.text[:200]}"
            except Exception as e:
                if _attempt < 2:
                    _time.sleep(2)
                    continue
                return f"EXCEPTION: {str(e)[:200]}"
        return None

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
            '<div style="background:{_card_tint_o};border:1px solid {_border_o};border-left:4px solid #fc4c02;' +
            'border-radius:10px;padding:1rem 1.2rem;margin-bottom:1rem;color:#888;font-size:0.82rem">' +
            '✦ Add <code>ANTHROPIC_API_KEY</code> to Streamlit secrets to enable athlete intelligence.' +
            '</div>',
            unsafe_allow_html=True
        )
    else:
        with st.spinner("✦ Generating athlete intelligence..."):
            _o = oura_df.iloc[0] if not oura_df.empty else None
            def _og(c):
                try: v=_o[c]; return float(v) if pd.notna(v) else None
                except: return None
            _ai_text = get_ai_analysis(
                _api_key, la_sport, la_name, la_dist, la_mins, la_elev_v, la_hr_v,
                effort_lbl, la_pace_s,
                _ctl, _atl, _tsb, _tsb_lbl,
                this_wk_km, last_wk_km, avg_dist_30,
                _this_h, _last_h,
                _recent_sports_str, _days_since_rest,
                oura_readiness=_og("readiness_score") if _o is not None else None,
                oura_hrv=_og("hrv_avg") if _o is not None else None,
                oura_hrv_avg=oura_df.head(7)["hrv_avg"].dropna().mean() if not oura_df.empty else None,
                oura_rhr=_og("resting_hr") if _o is not None else None,
                oura_sleep=_og("sleep_score") if _o is not None else None,
                oura_sleep_h=_og("total_sleep_min") if _o is not None else None,
                oura_temp=_og("temperature_deviation") if _o is not None else None,
            )
        if _ai_text and (_ai_text.startswith("ERROR") or _ai_text.startswith("EXCEPTION")):
            # Only show error card for real errors, not silent retries (None)
            st.markdown(
                '<div style="background:{_card_tint_o};border:1px solid {_border_o};border-left:3px solid #ff9966;' +
                'border-radius:10px;padding:0.8rem 1.2rem;margin-bottom:1rem;color:#999;font-size:0.78rem">' +
                f'✦ Athlete intelligence unavailable: {_ai_text[:120]}' +
                '</div>',
                unsafe_allow_html=True
            )
            _ai_text = None
        elif not _ai_text:
            pass  # Silent fail (overload/timeout) — show nothing rather than an error card

    if _api_key and _ai_text:
        _paras = [p.strip() for p in _ai_text.split("\n\n") if p.strip()]
        _analysis  = _paras[0] if len(_paras) > 0 else ""
        _recommend = _paras[1] if len(_paras) > 1 else ""

        st.markdown(
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:1rem">'
            + '<div style="background:{_card_tint_o};border:1px solid {_border_o};border-left:4px solid #fc4c02;'
            + 'border-radius:10px;padding:1rem 1.2rem">'
            + '<div style="color:#fc4c02;font-size:0.62rem;font-weight:700;text-transform:uppercase;'
            + 'letter-spacing:0.1em;margin-bottom:8px">✦ Activity Analysis</div>'
            + f'<div style="color:{_card_text};font-size:0.85rem;line-height:1.6">{_analysis}</div>'
            + '</div>'
            + '<div style="background:{_card_tint_g};border:1px solid {_border_g};border-left:4px solid #50c850;'
            + 'border-radius:10px;padding:1rem 1.2rem">'
            + '<div style="color:#50c850;font-size:0.62rem;font-weight:700;text-transform:uppercase;'
            + 'letter-spacing:0.1em;margin-bottom:8px">▶ Recommended Next Session</div>'
            + f'<div style="color:{_card_text};font-size:0.85rem;line-height:1.6">{_recommend}</div>'
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
    _full = pd.date_range(_daily["date"].min(), pd.Timestamp.now().normalize(), freq="D")
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
    _wk_start   = pd.Timestamp.now().normalize() - pd.Timedelta(days=pd.Timestamp.now().dayofweek)
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
      <text x="90" y="80" text-anchor="middle" fill="{_card_text}"
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

    # 7-day sparkline data for CTL/ATL/TSB cards
    _spark_days = min(7, len(_daily))
    _ctl_spark = _daily["ctl"].iloc[-_spark_days:].round(1).tolist()
    _atl_spark = _daily["atl"].iloc[-_spark_days:].round(1).tolist()
    _tsb_spark = _daily["tsb"].iloc[-_spark_days:].round(1).tolist()

    def _mini_spark(vals, color, invert=False):
        """Build a compact inline SVG sparkline for CTL/ATL/TSB cards."""
        if len(vals) < 2: return ""
        mn, mx = min(vals), max(vals)
        rng = mx - mn if mx != mn else 1
        W, H, pt, pb = 190, 58, 16, 4
        pts = [(round(i/(len(vals)-1)*W,1), round(pt+(1-(v-mn)/rng)*(H-pt-pb),1), v)
               for i,v in enumerate(vals)]
        def sm(pts):
            d = f"M {pts[0][0]},{pts[0][1]}"
            for i in range(1,len(pts)):
                cx=(pts[i-1][0]+pts[i][0])/2
                d+=f" C {cx},{pts[i-1][1]} {cx},{pts[i][1]} {pts[i][0]},{pts[i][1]}"
            return d
        sp = sm(pts)
        area = f"M 0,{H} L "+sp[2:]+f" L {pts[-1][0]},{H} Z"
        hx=color.lstrip("#"); r,g,b=int(hx[0:2],16),int(hx[2:4],16),int(hx[4:6],16)
        dots = "".join(f'<circle cx="{x}" cy="{y}" r="2" fill="#fff" stroke="{color}" stroke-width="1.2"/>' for x,y,_ in pts)
        lbls = "".join(f'<text x="{x}" y="{max(y-4,10)}" text-anchor="middle" fill="{color}" font-size="7.5" font-weight="400" font-family="DM Mono,monospace">{v:.1f}</text>' for x,y,v in pts)
        xn,yn,_=pts[-1]
        return (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">' +
                f'<path d="{area}" fill="rgba({r},{g},{b},0.07)"/>' +
                f'<path d="{sp}" fill="none" stroke="{color}" stroke-width="1.6" stroke-linecap="round"/>' +
                lbls + dots +
                f'<circle cx="{xn}" cy="{yn}" r="3" fill="{color}"/>' +
                '</svg>')

    _ctl_svg = _mini_spark(_ctl_spark, "#fc4c02")
    _atl_svg = _mini_spark(_atl_spark, "#ffa500")
    _tsb_svg = _mini_spark(_tsb_spark, "#a78bfa")

    # Single HTML block — all 6 cards in one CSS grid so heights match perfectly
    st.markdown(f"""
    <style>
    .dash-grid-wrap {{
        background: transparent;
        border-radius: 0;
        padding: 0;
        margin-bottom: 8px;
    }}
    .dash-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr 1.4fr 1.4fr;
        grid-template-rows: 188px 188px;
        gap: 10px;
        width: 100%;
    }}
    .dash-card {{
        background: rgba(255,255,255,0.85);
        border: 1px solid rgba(255,255,255,0.6);
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
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
        color: #888;
        font-size: 0.6rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.14em;
    }}
    .card-value {{
        font-size: 2.2rem;
        font-weight: 700;
        font-family: 'DM Mono', monospace;
        line-height: 1;
        color: {_card_text};
    }}
    .card-sub {{
        font-size: 0.7rem;
        font-weight: 300;
        color: #999;
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
        background: #1a1a1a;
        border: 1px solid #fc4c02;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.75rem;
        color: #f0f0f0;
        width: 220px;
        z-index: 999;
        line-height: 1.5;
        text-align: left;
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }}
    .ring-card {{
        background: {_card_bg};
        border: 1px solid {_card_border};
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

    <div class="dash-grid-wrap"><div class="dash-grid">

  
      <div class="dash-card" style="grid-column:1; grid-row:1">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
          <div class="card-label">CTL · Fitness</div>
          <div class="card-trend" style="color:{ctl_col}">{ctl_arr} {ctl_chg:.1f}</div>
        </div>
        <div class="card-value" style="margin:4px 0 2px">{_ctl:.1f}</div>
        <div class="card-sub">42-day fitness base</div>
        <div style="margin-top:6px">{_ctl_svg}</div>
        <div class="card-tooltip">
          <b>Chronic Training Load</b><br>
          Your long-term fitness level.<br><br>
          {'🟢 Strong base — ready to build on.' if _ctl >= 33 else '🟡 Moderate fitness — keep consistent.' if _ctl >= 20 else '🔴 Low base — focus on building volume.'}
        </div>
      </div>

  
      <div class="dash-card" style="grid-column:2; grid-row:1">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
          <div class="card-label">ATL · Fatigue</div>
          <div class="card-trend" style="color:{atl_col}">{atl_arr} {atl_chg:.1f}</div>
        </div>
        <div class="card-value" style="margin:4px 0 2px">{_atl:.1f}</div>
        <div class="card-sub">7-day fatigue load</div>
        <div style="margin-top:6px">{_atl_svg}</div>
        <div class="card-tooltip">
          <b>Acute Training Load</b><br>
          Your recent fatigue from training.<br><br>
          {'🔴 High fatigue — prioritise recovery.' if _atl > 37 else '🟡 Moderate load — training zone.' if _atl > 13 else '🟢 Low recent load — body is fresh.'}
        </div>
      </div>

  
      <div class="dash-card" style="grid-column:1; grid-row:2">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
          <div class="card-label">TSB · Form</div>
          <div class="card-trend" style="color:{tsb_col}">{tsb_arr} {tsb_chg:.1f}</div>
        </div>
        <div class="card-value" style="color:{_tsb_col};margin:4px 0 2px">{_tsb:+.1f}</div>
        <div class="card-sub" style="color:{_tsb_col};font-weight:600">{_tsb_lbl}</div>
        <div style="margin-top:6px">{_tsb_svg}</div>
        <div class="card-tooltip">
          <b>Training Stress Balance</b><br>
          Fitness minus fatigue = form.<br><br>
          {'🏆 Peaked — race or PB attempt.' if _tsb > 15 else '🟢 Fresh — ideal for hard session.' if _tsb > 5 else '🟡 Normal training load — quality sessions ok.' if _tsb > -10 else '🟠 Tired — keep it easy today.' if _tsb > -20 else '🔴 Overloaded — rest day needed.'}
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
        o_resp      = osafe(today_o, "respiratory_rate")
        # Activity score fallback — often None for current day, use most recent available
        o_act_score = None
        for _oi in range(min(3, len(oura_df))):
            _v = osafe(oura_df.iloc[_oi], "activity_score")
            if _v is not None:
                o_act_score = _v
                break

        hrv_7avg = recent_7["hrv_avg"].dropna().mean() if "hrv_avg" in recent_7.columns else None
        rhr_7avg = recent_7["resting_hr"].dropna().mean() if "resting_hr" in recent_7.columns else None
        hrv_d    = (o_hrv - hrv_7avg) if o_hrv and hrv_7avg else None
        rhr_d    = (o_rhr - rhr_7avg) if o_rhr and rhr_7avg else None

        def scol(v, hi=85, lo=70):
            if v is None: return "#666"
            return "#50c850" if v >= hi else "#ffa500" if v >= lo else "#ff5555"

        def hrv_col(v):
            """HRV: 40+ green, 35-39 yellow, <35 red"""
            if v is None: return "#666"
            return "#50c850" if v >= 40 else "#ffa500" if v >= 35 else "#ff5555"

        def rhr_col(v):
            """RHR: ≤50 green, 51-55 yellow, 56+ red"""
            if v is None: return "#666"
            return "#50c850" if v <= 50 else "#ffa500" if v <= 55 else "#ff5555"

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

        def sparkline_svg(values, color, width=160, height=72, fmt=None):
            """Smooth bezier sparkline with value labels above each point."""
            vals = [v for v in values if v is not None and not (isinstance(v, float) and v != v)]
            if len(vals) < 2:
                return ""
            if fmt is None:
                fmt = lambda v: str(int(round(v)))
            mn, mx = min(vals), max(vals)
            rng = mx - mn if mx != mn else 1
            pt = 18; pb = 6  # top padding for value labels
            pts = []
            for i, v in enumerate(vals):
                x = round(i / (len(vals)-1) * width, 1)
                y = round(pt + (1 - (v - mn) / rng) * (height - pt - pb), 1)
                pts.append((x, y, v))
            def smooth(pts):
                d = f"M {pts[0][0]},{pts[0][1]}"
                for i in range(1, len(pts)):
                    x0,y0 = pts[i-1][0],pts[i-1][1]
                    x1,y1 = pts[i][0],pts[i][1]
                    cx = (x0+x1)/2
                    d += f" C {cx},{y0} {cx},{y1} {x1},{y1}"
                return d
            sp = smooth(pts)
            area = (f"M 0,{height} L {pts[0][0]},{pts[0][1]} " +
                    " ".join(f"C {(pts[i-1][0]+pts[i][0])/2},{pts[i-1][1]} {(pts[i-1][0]+pts[i][0])/2},{pts[i][1]} {pts[i][0]},{pts[i][1]}"
                             for i in range(1,len(pts))) +
                    f" L {pts[-1][0]},{height} Z")
            hx = color.lstrip("#")
            r,g,b = int(hx[0:2],16),int(hx[2:4],16),int(hx[4:6],16)
            # Circles at each point
            circles = "".join(
                f'<circle cx="{x}" cy="{y}" r="2.5" fill="#ffffff" stroke="{color}" stroke-width="1.5"/>' 
                for x,y,_ in pts
            )
            # Value labels above each point — thin, small
            labels = "".join(
                f'<text x="{x}" y="{max(y-5, 11)}" text-anchor="middle" ' +
                f'fill="{color}" font-size="8.5" font-weight="400" ' +
                f'font-family="DM Mono,monospace" opacity="0.9">{fmt(v)}</text>'
                for x,y,v in pts
            )
            # Last point larger + filled
            xn,yn,_ = pts[-1]
            return (
                f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" ' +
                'xmlns="http://www.w3.org/2000/svg">' +
                f'<path d="{area}" fill="rgba({r},{g},{b},0.07)"/>' +
                f'<path d="{sp}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/>' +
                labels + circles +
                f'<circle cx="{xn}" cy="{yn}" r="3.5" fill="{color}"/>' +
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
            spark  = sparkline_svg(spark_vals, spark_color, width=160, height=60)
            return (
                f'<div style="background:{_card_bg};border:1px solid {_card_border};{border}border-radius:12px;padding:14px 16px;box-shadow:0 1px 4px rgba(0,0,0,0.05)">' +
                f'<div style="color:{_card_sub};font-size:0.6rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px">{label}</div>' +
                f'<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:8px">' +
                f'<div><div style="margin-bottom:4px">{value_html}</div>' +
                f'<div style="color:#999;font-size:0.7rem">{sub}</div></div>' +
                f'<div style="flex-shrink:0">{spark}</div>' +
                '</div></div>'
            )

        html_oura = (
            '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:10px">'
            + oura_card("Readiness",
                f'<span style="color:{scol(o_ready)};font-size:2rem;font-weight:700;font-family:DM Mono,monospace">{int(o_ready) if o_ready else "—"}</span>',
                rmsg, _spark_ready, scol(o_ready), border_color=None)
            + oura_card("HRV",
                f'<span style="color:{hrv_col(o_hrv)};font-size:2rem;font-weight:700;font-family:DM Mono,monospace">{int(o_hrv) if o_hrv else "—"}</span><span style="color:#999;font-size:0.85rem"> ms</span>',
                f'{trend_badge(hrv_d, unit=" ms")} vs 7d avg', _spark_hrv, "#a78bfa")
            + oura_card("Resting HR",
                f'<span style="color:{rhr_col(o_rhr)};font-size:2rem;font-weight:700;font-family:DM Mono,monospace">{int(o_rhr) if o_rhr else "—"}</span><span style="color:#999;font-size:0.85rem"> bpm</span>',
                f'{trend_badge(rhr_d, invert=True, unit=" bpm")} vs 7d avg', _spark_rhr, "#fc4c02")
            + oura_card("Sleep",
                f'<span style="color:{scol(o_sleep)};font-size:2rem;font-weight:700;font-family:DM Mono,monospace">{int(o_sleep) if o_sleep else "—"}</span>',
                f'{sleep_str} · {deep_str} deep', _spark_sleep, scol(o_sleep))
            + '</div>'

            + '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">'
            + f'<div style="background:{_card_bg};border:1px solid {_card_border};border-radius:10px;padding:14px 16px">'
            + f'<div style="color:{_card_sub};font-size:0.6rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em">Body Temp</div>'
            + f'<div style="color:{temp_col};font-size:1.5rem;font-weight:700;font-family:DM Mono,monospace;margin-top:4px">{f"{o_temp:+.2f}°C" if o_temp is not None else "—"}</div>'
            + f'<div style="color:{_card_sub};font-size:0.7rem;margin-top:2px">deviation from baseline</div></div>'

            + f'<div style="background:{_card_bg};border:1px solid {_card_border};border-radius:10px;padding:14px 16px">'
            + f'<div style="color:{_card_sub};font-size:0.6rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em">Respiratory Rate</div>'
            + f'<div style="color:{_card_text};font-size:1.5rem;font-weight:700;font-family:DM Mono,monospace;margin-top:4px">{f"{o_resp:.1f}" if o_resp else "—"} br/min</div>'
            + f'<div style="color:{_card_sub};font-size:0.7rem;margin-top:2px">avg during sleep</div></div>'

            + f'<div style="background:{_card_bg};border:1px solid {_card_border};border-radius:10px;padding:14px 16px">'
            + f'<div style="color:{_card_sub};font-size:0.6rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em">Activity Score</div>'
            + f'<div style="color:{scol(o_act_score)};font-size:1.5rem;font-weight:700;font-family:DM Mono,monospace;margin-top:4px">{int(o_act_score) if o_act_score is not None else "—"}</div>'
            + f'<div style="color:{_card_sub};font-size:0.7rem;margin-top:2px">Daily activity balance</div></div>'
            + '</div>'
        )

        st.markdown(html_oura, unsafe_allow_html=True)

        # 30-day HRV + RHR trend chart — modern rounded bars + smooth lines
        chart_o = recent_30[["date","hrv_avg","resting_hr"]].copy()
        chart_o = chart_o[chart_o["hrv_avg"].notna() | chart_o["resting_hr"].notna()]

        if len(chart_o) > 3:
            chart_o["hrv_roll"] = chart_o["hrv_avg"].rolling(7, min_periods=1).mean()
            fig_o = go.Figure()

            # HRV bars — rounded top via marker line trick, soft purple
            fig_o.add_trace(go.Bar(
                x=chart_o["date"], y=chart_o["hrv_avg"].round(1), name="HRV",
                marker=dict(
                    color="rgba(167,139,250,0.25)",
                    line=dict(width=0),
                    cornerradius=6,
                ),
                hovertemplate="<b>%{x|%d %b}</b><br>HRV: <b>%{y:.0f} ms</b><extra></extra>",
            ))

            # HRV 7-day smooth line with gradient feel
            fig_o.add_trace(go.Scatter(
                x=chart_o["date"], y=chart_o["hrv_roll"].round(1), name="HRV 7d avg",
                mode="lines",
                line=dict(color="#a78bfa", width=3, shape="spline", smoothing=1.2),
                fill="tozeroy",
                fillcolor="rgba(167,139,250,0.06)",
                hovertemplate="7d avg: <b>%{y:.0f} ms</b><extra></extra>",
            ))

            # Resting HR — smooth spline, bold orange
            if chart_o["resting_hr"].notna().sum() > 3:
                fig_o.add_trace(go.Scatter(
                    x=chart_o["date"], y=chart_o["resting_hr"].round(1), name="Resting HR",
                    mode="lines+markers", yaxis="y2",
                    line=dict(color="#fc4c02", width=2.5, shape="spline", smoothing=1.0),
                    marker=dict(
                        size=5, color="#fc4c02",
                        line=dict(color="#ffffff", width=1.5),
                        symbol="circle",
                    ),
                    hovertemplate="<b>%{x|%d %b}</b><br>RHR: <b>%{y:.0f} bpm</b><extra></extra>",
                ))

            _oura_layout = {k:v for k,v in CHART_LAYOUT.items() if k != "legend"}
            fig_o.update_layout(
                **{**_oura_layout, "margin": dict(t=10,b=30,l=50,r=50)},
                height=260, barmode="overlay",
                yaxis=dict(**axis_style(), title="HRV (ms)"),
                yaxis2=dict(**axis_style(), title="RHR (bpm)", overlaying="y",
                            side="right", showgrid=False),
                legend=dict(orientation="h", y=1.08, font=dict(color="#888",size=11),
                            bgcolor="rgba(0,0,0,0)"),
            )
            fig_o.update_xaxes(**axis_style())
            st.plotly_chart(fig_o, use_container_width=True)


        st.markdown('<div style="margin-top:1rem"></div>', unsafe_allow_html=True)
        st.markdown("### Strength Intelligence")

        @st.cache_data(ttl=86400, show_spinner=False)
        def get_strength_analysis(api_key, upper_6w_json, lower_6w_json,
                                  top_exercises_json, total_sessions,
                                  upper_lower_ratio, last_session_date):
            import requests as _rq, time as _t
            prompt = f"""You are a strength and conditioning coach analysing training data.

    UPPER BODY — last 6 weeks volume (kg per week): {upper_6w_json}
    LOWER BODY — last 6 weeks volume (kg per week): {lower_6w_json}
    Upper:Lower ratio (all time): {upper_lower_ratio:.1f}:1
    Total sessions: {total_sessions} · Last session: {last_session_date}
    Top exercises by volume: {top_exercises_json}

    Write TWO short paragraphs (no headers, no bullets):
    1. PROGRESS (3-4 sentences): What do the 6-week trends show? Is volume up, down or flat? Any notable patterns?
    2. FOCUS (3-4 sentences): What muscle groups need more attention? Name specific exercises and targets.
    Write like a direct, knowledgeable coach. Use the numbers."""
            for attempt in range(3):
                try:
                    resp = _rq.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={"x-api-key": api_key,
                                 "anthropic-version": "2023-06-01",
                                 "Content-Type": "application/json"},
                        json={"model": "claude-sonnet-4-20250514",
                              "max_tokens": 350,
                              "messages": [{"role": "user", "content": prompt}]},
                        timeout=25
                    )
                    if resp.status_code == 200:
                        return resp.json()["content"][0]["text"].strip()
                    elif resp.status_code in (529, 503, 502, 500):
                        if attempt < 2: _t.sleep(3 + attempt * 2); continue
                        return None
                    else:
                        return f"ERROR {resp.status_code}"
                except Exception:
                    if attempt < 2: _t.sleep(2); continue
                    return None
            return None

        _sa_key = st.secrets.get("ANTHROPIC_API_KEY","") if hasattr(st,"secrets") else ""
        if _sa_key and fitbod_data:
            import json as _json
            _fbw2 = pd.DataFrame(fitbod_data.get("weekly_volume",[]))
            _fbs2 = pd.DataFrame(fitbod_data.get("sets",[]))
            if len(_fbw2) > 0 and len(_fbs2) > 0:
                _fbw2["week"] = pd.to_datetime(_fbw2["week"])
                _fbs2["date"] = pd.to_datetime(_fbs2["date"])
                _w6c2  = _fbw2["week"].max() - pd.Timedelta(weeks=6)
                _au6   = _fbw2[(_fbw2["muscle_group"]=="Upper")&(_fbw2["week"]>=_w6c2)].sort_values("week")
                _al6   = _fbw2[(_fbw2["muscle_group"]=="Lower")&(_fbw2["week"]>=_w6c2)].sort_values("week")
                _u6j   = _au6[["week","volume"]].assign(week=lambda x:x["week"].dt.strftime("%d %b"),volume=lambda x:x["volume"].round(0).astype(int)).to_dict(orient="records") if len(_au6)>0 else []
                _l6j   = _al6[["week","volume"]].assign(week=lambda x:x["week"].dt.strftime("%d %b"),volume=lambda x:x["volume"].round(0).astype(int)).to_dict(orient="records") if len(_al6)>0 else []
                _ut    = _fbs2[_fbs2["muscle_group"]=="Upper"]["volume_kg"].sum()
                _lt    = _fbs2[_fbs2["muscle_group"]=="Lower"]["volume_kg"].sum()
                _ratio2= _ut / max(_lt, 1)
                _topex = _fbs2.groupby("exercise")["volume_kg"].sum().nlargest(8).index.tolist()
                _sess2 = pd.DataFrame(fitbod_data.get("sessions",[]))
                _sess2["date"] = pd.to_datetime(_sess2["date"]) if len(_sess2)>0 else _sess2
                _lasts = _sess2["date"].max().strftime("%d %b %Y") if len(_sess2)>0 else "unknown"
                with st.spinner("✦ Generating strength insights..."):
                    _stext = get_strength_analysis(
                        _sa_key, _json.dumps(_u6j), _json.dumps(_l6j),
                        _json.dumps(_topex), fitbod_data["total_sessions"],
                        _ratio2, _lasts
                    )
                if _stext and not _stext.startswith("ERROR"):
                    _sp = [p.strip() for p in _stext.split("\n\n") if p.strip()]
                    _san = _sp[0] if len(_sp)>0 else ""
                    _sfo = _sp[1] if len(_sp)>1 else ""
                    st.markdown(
                        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:1rem">' +
                        f'<div style="background:{_card_bg};border:1px solid {_card_border};border-radius:12px;padding:1rem 1.2rem;box-shadow:0 1px 4px rgba(0,0,0,0.06)">' +
                        f'<div style="color:{_card_sub};font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px">✦ Progress Analysis</div>' +
                        f'<div style="color:{_card_text};font-size:0.85rem;line-height:1.6">{_san}</div></div>' +
                        f'<div style="background:{_card_bg};border:1px solid {_card_border};border-radius:12px;padding:1rem 1.2rem;box-shadow:0 1px 4px rgba(0,0,0,0.06)">' +
                        f'<div style="color:{_card_sub};font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px">▶ Focus Recommendations</div>' +
                        f'<div style="color:{_card_text};font-size:0.85rem;line-height:1.6">{_sfo}</div></div>' +
                        '</div>',
                        unsafe_allow_html=True
                    )
        elif not _sa_key:
            st.caption("Add ANTHROPIC_API_KEY to Streamlit secrets to enable strength insights.")









with tab2:
    # ── Headline metrics ──────────────────────────────────────────────────────────
    # Animated counters
    _n_acts  = len(fdf)
    _n_km    = int(end['dist_km'].sum())
    _n_elev  = int(end['elev_gain_m'].sum() / 1000)
    _n_h     = int(end['moving_min'].sum() // 60)
    _n_kcal  = int(fdf['calories'].sum() / 1000)

    st.components.v1.html(f"""
    <style>
    .ctr-grid {{ display:grid; grid-template-columns:repeat(5,1fr); gap:12px; font-family:'Inter',sans-serif; }}
    .ctr-card {{ background:{_card_bg}; border:1px solid {_card_border}; border-radius:16px; padding:1.1rem 1.3rem;
                 box-shadow:0 2px 8px rgba(0,0,0,0.06); transition:box-shadow 0.2s, transform 0.2s; }}
    .ctr-card:hover {{ box-shadow:0 8px 24px rgba(0,0,0,0.10); transform:translateY(-2px); }}
    .ctr-label {{ color:{_card_sub}; font-size:0.68rem; font-weight:600; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:6px; }}
    .ctr-val {{ color:{_card_text}; font-size:2rem; font-weight:700; font-family:'DM Mono',monospace; line-height:1; }}
    .ctr-unit {{ color:{_card_sub}; font-size:0.9rem; font-weight:400; margin-left:3px; }}
    </style>
    <div class="ctr-grid">
      <div class="ctr-card"><div class="ctr-label">Activities</div><div class="ctr-val" data-target="{_n_acts}" data-dec="0">0</div></div>
      <div class="ctr-card"><div class="ctr-label">Distance</div><div class="ctr-val" data-target="{_n_km}" data-dec="0">0<span class="ctr-unit">km</span></div></div>
      <div class="ctr-card"><div class="ctr-label">Elevation</div><div class="ctr-val" data-target="{_n_elev}" data-dec="0">0<span class="ctr-unit">k m</span></div></div>
      <div class="ctr-card"><div class="ctr-label">Moving Time</div><div class="ctr-val" data-target="{_n_h}" data-dec="0">0<span class="ctr-unit">h</span></div></div>
      <div class="ctr-card"><div class="ctr-label">Calories</div><div class="ctr-val" data-target="{_n_kcal}" data-dec="0">0<span class="ctr-unit">k kcal</span></div></div>
    </div>
    <script>
    document.querySelectorAll('.ctr-val[data-target]').forEach(el => {{
      const target = +el.dataset.target;
      const unit = el.querySelector('.ctr-unit') ? el.querySelector('.ctr-unit').outerHTML : '';
      const dec = +el.dataset.dec;
      let start = null;
      const dur = 1200;
      function step(ts) {{
        if (!start) start = ts;
        const p = Math.min((ts - start) / dur, 1);
        const ease = 1 - Math.pow(1 - p, 3);
        const val = (target * ease).toFixed(dec);
        el.innerHTML = (+val).toLocaleString() + unit;
        if (p < 1) requestAnimationFrame(step);
      }}
      requestAnimationFrame(step);
    }});
    </script>
    """, height=130)

    st.markdown('<hr style="border:none;border-top:1px solid #e8e4de;margin:0.8rem 0">', unsafe_allow_html=True)

    # ── Training Consistency Heatmap ─────────────────────────────────────────────
    st.markdown("## Training Consistency")

    ENDURANCE_H = {"Run","Ride","Virtual Ride","Virtual Run","Walk","Hike",
                   "Nordic Ski","Swim","Rowing","E-Bike Ride","Weight Training","Workout","Crossfit"}

    @st.cache_data(ttl=300)  # 5-min cache so today's activities appear
    def build_heatmap_data(_df):
        end = _df[_df["sport"].isin(ENDURANCE_H)].copy()
        end["tss"] = end["rel_effort"].fillna(
            end["moving_min"] * (end["avg_hr"].fillna(130) / 150) ** 2 * 0.5)
        # Ensure any activity shows at least a minimal TSS so it gets coloured
        end["tss"] = end["tss"].clip(lower=1)
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
    # Bins calibrated to Strava Relative Effort scale (typical session = 5-25)
    # Old TrainingPeaks TSS bins (25/75/150) were too high for this data
    day_df["level"] = pd.cut(day_df["tss"],
        bins=[-0.1, 0, 8, 36, 95, 9999],
        labels=[0,1,2,3,4]).astype(int)
    day_df["dow"]   = day_df["date"].dt.dayofweek  # 0=Mon
    day_df["week"]  = (day_df["date"] - year_start).dt.days // 7

    # Colours: dark bg → light orange gradient
    COLOURS = ["#f0ede8","#ffd4b8","#ffaa77","#ff6622","#fc4c02"]
    LABELS  = ["Rest","Easy","Moderate","Hard","Peak"]
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
        # today's cell highlighted via SVG title tooltip only

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
    s1.metric("Training days", f"{active_days}")
    s2.metric("Rest days",     f"{total_days - active_days}")
    # Avg days/week more useful than longest streak for balanced training
    _yr_weeks = max(1, total_days // 7)
    _avg_days_wk = round(active_days / _yr_weeks, 1)
    s3.metric("Avg days/week", f"{_avg_days_wk}")
    s4.metric("Active days",   f"{active_days/total_days*100:.0f}%")

    st.markdown(f'<div style="background:{_card_bg};border:1px solid {_card_border};border-radius:12px;padding:1rem 1.2rem;overflow-x:auto;box-shadow:0 1px 4px rgba(0,0,0,0.06);-webkit-overflow-scrolling:touch">{svg}</div>', unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.72rem;color:#444;margin-top:4px'>Hover over any square to see the training load. Colour = training stress: dark = rest, orange = hard session.</div>", unsafe_allow_html=True)

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
            marker=dict(color=SPORT_COLORS.get(sport,"#666"), line=dict(width=0), cornerradius=4),
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
    # Always include current week so 'this week' shows 0 if no activity yet
    _cur_week_start = pd.Timestamp.now().normalize() - pd.Timedelta(days=pd.Timestamp.now().dayofweek)
    if _cur_week_start not in weekly_hrs["week"].values:
        weekly_hrs = pd.concat([weekly_hrs, pd.DataFrame({"week":[_cur_week_start],"hours":[0.0]})], ignore_index=True).sort_values("week")
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
            <div style="color:{_card_text};font-size:2rem;font-weight:700;
                        font-family:'DM Mono',monospace;line-height:1;min-width:120px">
              {this_h}h&nbsp;{this_m:02d}m
            </div>
            <div style="background:{_card_bg};border:1px solid {_card_border};border-radius:8px;
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
        marker=dict(color="rgba(167,139,250,0.35)", line=dict(width=0), cornerradius=5),
        hovertemplate="<b>%{y:.1f}h</b><extra></extra>",
    ))
    fig_h.add_trace(go.Scatter(
        x=weekly_hrs["week"], y=weekly_hrs["rolling"].round(2),
        mode="lines", name="8-week avg",
        line=dict(color="#a78bfa", width=2.5, shape="spline", smoothing=1.0),
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

with tab3:
    # ── Strength Volume Cards — Upper + Lower (shown right after Oura cards) ──
    if fitbod_data:
        _fbw = pd.DataFrame(fitbod_data.get("weekly_volume", []))
        _fbs = pd.DataFrame(fitbod_data.get("sets", []))
        if len(_fbw) > 0 and len(_fbs) > 0:
            _fbw["week"] = pd.to_datetime(_fbw["week"])
            _fbs["date"] = pd.to_datetime(_fbs["date"])
            # Use current week start so 'This Week' reflects actual current week
            _now_wk = pd.Timestamp.now().normalize() - pd.Timedelta(days=pd.Timestamp.now().dayofweek)
            _w6c  = _now_wk - pd.Timedelta(weeks=6)
            _u6   = _fbw[(_fbw["muscle_group"]=="Upper") & (_fbw["week"]>=_w6c)].sort_values("week")
            _l6   = _fbw[(_fbw["muscle_group"]=="Lower") & (_fbw["week"]>=_w6c)].sort_values("week")

            def _sv(df, i): return int(df["volume"].iloc[i]) if len(df) > abs(i) else 0
            # Get current week's volume (may be 0 if not trained yet this week)
            _u_cur = _fbw[(_fbw["muscle_group"]=="Upper") & (_fbw["week"]==_now_wk)]
            _l_cur = _fbw[(_fbw["muscle_group"]=="Lower") & (_fbw["week"]==_now_wk)]
            _ul = int(_u_cur["volume"].iloc[0]) if len(_u_cur) > 0 else 0
            _ll = int(_l_cur["volume"].iloc[0]) if len(_l_cur) > 0 else 0
            _up = _sv(_u6,-2) if _ul > 0 else _sv(_u6,-1)
            _lp = _sv(_l6,-2) if _ll > 0 else _sv(_l6,-1)
            _ua6 = int(_u6["volume"].mean()) if len(_u6)>0 else 0
            _la6 = int(_l6["volume"].mean()) if len(_l6)>0 else 0
            _ud, _ld = _ul-_up, _ll-_lp
            def _va(d): return ("▲","#50c850") if d>0 else ("▼","#ff5555") if d<0 else ("—","#aaa")
            _uarr,_ucol = _va(_ud); _larr,_lcol = _va(_ld)
            def _str_spark(w6, lc):
                if len(w6)<2: return ""
                vs = w6["volume"].round(0).tolist()
                ds = w6["week"].dt.strftime("%-d %b").tolist()
                W,H,pb,pt = 240,90,22,18

                def _fmt_k(v):
                    return f"{v/1000:.1f}K" if v >= 1000 else str(int(v))

                mn,mx = min(vs),max(vs)
                rng = mx-mn if mx!=mn else 1
                pts = [(round(i/(len(vs)-1)*W,1), round(pt+(1-(v-mn)/rng)*(H-pt-pb),1), v, d)
                       for i,(v,d) in enumerate(zip(vs,ds))]
                path = " ".join(f"{x},{y}" for x,y,_,_ in pts)
                area = f"0,{H-pb} " + path + f" {W},{H-pb}"
                # Smooth curve using cubic bezier through points
                def _smooth(pts):
                    if len(pts) < 2: return ""
                    d = f"M {pts[0][0]},{pts[0][1]}"
                    for i in range(1, len(pts)):
                        x0,y0 = pts[i-1][0],pts[i-1][1]
                        x1,y1 = pts[i][0],pts[i][1]
                        cx = (x0+x1)/2
                        d += f" C {cx},{y0} {cx},{y1} {x1},{y1}"
                    return d
                smooth_path = _smooth(pts)
                smooth_area = f"M 0,{H-pb} L {pts[0][0]},{pts[0][1]} " + " ".join(
                    f"C {(pts[i-1][0]+pts[i][0])/2},{pts[i-1][1]} {(pts[i-1][0]+pts[i][0])/2},{pts[i][1]} {pts[i][0]},{pts[i][1]}"
                    for i in range(1,len(pts))
                ) + f" L {pts[-1][0]},{H-pb} Z"
                circ = "".join(f'<circle cx="{x}" cy="{y}" r="3.5" fill="{lc}" stroke="#fff" stroke-width="1.5"/>' for x,y,_,_ in pts)
                vals = "".join(f'<text x="{x}" y="{max(y-8,pt-2)}" text-anchor="middle" fill="{lc}" font-size="9" font-weight="400" font-family="DM Mono,monospace">{_fmt_k(v)}</text>' for x,y,v,_ in pts)
                dats = "".join(f'<text x="{x}" y="{H-5}" text-anchor="middle" fill="#bbb" font-size="7.5" font-family="DM Sans">{d}</text>' for x,y,_,d in pts)
                lc_rgba = lc.replace("#","")
                r,g,b = int(lc_rgba[0:2],16),int(lc_rgba[2:4],16),int(lc_rgba[4:6],16)
                return (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">' +
                        f'<path d="{smooth_area}" fill="rgba({r},{g},{b},0.08)"/>' +
                        f'<path d="{smooth_path}" fill="none" stroke="{lc}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>' +
                        circ + vals + dats + '</svg>')

            _su = _str_spark(_u6,"#fc4c02"); _sl = _str_spark(_l6,"#d97706")
            _usub = f'<span style="color:{_ucol};font-weight:600">{_uarr} {abs(_ud):,} kg</span> vs prev · 6w avg {_ua6:,} kg'
            _lsub = f'<span style="color:{_lcol};font-weight:600">{_larr} {abs(_ld):,} kg</span> vs prev · 6w avg {_la6:,} kg'

            st.markdown(
                f'<hr style="border:none;border-top:1px solid {_card_border};margin:24px 0">' +
                '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:16px 0">' +
                '<div style="background:{_card_bg};border:1px solid {_card_border};border-radius:12px;padding:16px 18px;box-shadow:0 1px 4px rgba(0,0,0,0.06)">' +
                '<div style="display:flex;justify-content:space-between;align-items:flex-start">' +
                '<div>' +
            f'<div style="color:{_card_sub};font-size:0.6rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px">Upper Body · This Week</div>' +
                f'<div style="color:{_card_text};font-size:2.4rem;font-weight:700;font-family:DM Mono,monospace;line-height:1">{_ul:,}<span style="color:#aaa;font-size:1rem;font-weight:400"> kg</span></div>' +
                f'<div style="color:#888;font-size:0.72rem;margin-top:6px">{_usub}</div>' +
                '</div>' +
                f'<div style="flex-shrink:0;margin-left:8px">{_su}</div>' +
                '</div></div>' +
                '<div style="background:{_card_bg};border:1px solid {_card_border};border-radius:12px;padding:16px 18px;box-shadow:0 1px 4px rgba(0,0,0,0.06)">' +
                '<div style="display:flex;justify-content:space-between;align-items:flex-start">' +
                '<div>' +
                f'<div style="color:{_card_sub};font-size:0.6rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px">Lower Body · This Week</div>' +
                f'<div style="color:{_card_text};font-size:2.4rem;font-weight:700;font-family:DM Mono,monospace;line-height:1">{_ll:,}<span style="color:#aaa;font-size:1rem;font-weight:400"> kg</span></div>' +
                f'<div style="color:#888;font-size:0.72rem;margin-top:6px">{_lsub}</div>' +
                '</div>' +
                f'<div style="flex-shrink:0;margin-left:8px">{_sl}</div>' +
                '</div></div>' +
                '</div>',
                unsafe_allow_html=True
            )










    if not fitbod_data:
        st.markdown(
            '<div style="background:#f7f5f2;border:1px solid #e2ddd8;border-radius:12px;padding:1.2rem 1.4rem;color:#999;font-size:0.85rem">'
            '🏋️ <b>Fitbod data not connected yet.</b> Upload <code>WorkoutExport.csv</code> to your GitHub repo '
            'and trigger the Fitbod sync to see your strength data here.'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        # ── Parse Fitbod data ─────────────────────────────────────────────────────
        fb_sets     = pd.DataFrame(fitbod_data.get("sets", []))
        fb_weekly   = pd.DataFrame(fitbod_data.get("weekly_volume", []))
        fb_records  = pd.DataFrame(fitbod_data.get("records", []))
        fb_sessions = pd.DataFrame(fitbod_data.get("sessions", []))

        if len(fb_sets) > 0:
            fb_sets["date"]  = pd.to_datetime(fb_sets["date"])
            fb_sets["week"]  = pd.to_datetime(fb_sets["week"])
            fb_sessions["date"] = pd.to_datetime(fb_sessions["date"])

            fb_date_min = pd.to_datetime(fitbod_data["date_min"]).strftime("%b %Y")
            fb_date_max = pd.to_datetime(fitbod_data["date_max"]).strftime("%b %Y")

            if len(fb_weekly) > 0:
                fb_weekly["week"] = pd.to_datetime(fb_weekly["week"])

            # ── Headline metrics ──────────────────────────────────────────────────
            fb_c1, fb_c2, fb_c3, fb_c4, fb_c5 = st.columns(5)
            fb_c1.metric("Sessions",      f"{fitbod_data['total_sessions']}")
            fb_c2.metric("Total sets",    f"{fitbod_data['total_sets']:,}")
            total_vol = fb_sets["volume_kg"].sum()
            fb_c3.metric("Total volume",  f"{total_vol/1000:.1f}t kg")
            fb_c4.metric("Exercises",     f"{fb_sets['exercise'].nunique()}")
            last_session = fb_sessions["date"].max().strftime("%d %b") if len(fb_sessions) > 0 else "—"
            fb_c5.metric("Last session",  last_session)

            st.markdown('<hr style="border:none;border-top:1px solid #e8e4de;margin:0.6rem 0">', unsafe_allow_html=True)

            # ── Weekly volume + Progressive overload side by side ──────────────────

            # ── Progressive overload — volume per session, top exercises ─────────
            st.markdown("### Progressive Overload")
            st.caption("Volume trend (sets × reps × weight) across last 8 sessions · top exercises by frequency")

            top_ex = fitbod_data.get("top_exercises", fb_sets["exercise"].value_counts().head(15).index.tolist())
            avail_ex = [e for e in top_ex if e in fb_sets["exercise"].values]

            if avail_ex:
                # Build per-exercise session volume for all top exercises
                po_rows = []
                for ex in avail_ex[:12]:
                    ex_data = fb_sets[fb_sets["exercise"] == ex].copy()
                    # Volume per session date
                    ex_sess = ex_data.groupby(ex_data["date"].dt.normalize()).agg(
                        volume=("volume_kg", "sum"),
                        max_weight=("weight_kg", "max"),
                        total_sets=("sets", "sum"),
                    ).reset_index().sort_values("date")
                    if len(ex_sess) < 2:
                        continue
                    last8 = ex_sess.tail(8)
                    vol_first = last8["volume"].iloc[0]
                    vol_latest = last8["volume"].iloc[-1]
                    change = vol_latest - vol_first
                    change_pct = (change / vol_first * 100) if vol_first > 0 else 0
                    po_rows.append({
                        "exercise": ex,
                        "sessions": last8,
                        "vol_latest": vol_latest,
                        "max_weight": last8["max_weight"].iloc[-1],
                        "change": change,
                        "change_pct": change_pct,
                        "n_sessions": len(ex_sess),
                    })

                if po_rows:
                    # Full-width grid: 3 columns, consistent card size
                    _po_cols_n = 3
                    for _pi in range(0, len(po_rows), _po_cols_n):
                        _pcols = st.columns(_po_cols_n, gap="small")
                        for _pci, _pcol in enumerate(_pcols):
                            if _pi + _pci >= len(po_rows):
                                _pcol.empty()
                                continue
                            p = po_rows[_pi + _pci]
                            with _pcol:
                                vols  = p["sessions"]["volume"].tolist()
                                dates = p["sessions"]["date"].dt.strftime("%-d %b").tolist()
                                # Per-bar color: green=up vs prev, red=down, gray=first/equal
                                _bc = []
                                for _bi in range(len(vols)):
                                    if _bi == 0: _bc.append("rgba(156,163,175,0.35)")
                                    elif vols[_bi] > vols[_bi-1]*1.02: _bc.append("#22c55e")
                                    elif vols[_bi] < vols[_bi-1]*0.98: _bc.append("#ef4444")
                                    else: _bc.append("rgba(156,163,175,0.35)")
                                _fig = go.Figure()
                                _fig.add_trace(go.Bar(
                                    x=dates, y=[round(v,0) for v in vols],
                                    marker=dict(color=_bc, cornerradius=3, line=dict(width=0)),
                                    hovertemplate="<b>%{x}</b><br>%{y:.0f} kg<extra></extra>",
                                ))
                                _po_layout = {**CHART_LAYOUT,
                                    "height": 160,
                                    "margin": dict(l=0, r=0, t=0, b=0),
                                    "showlegend": False,
                                    "plot_bgcolor": "rgba(0,0,0,0)",
                                    "paper_bgcolor": "rgba(0,0,0,0)",
                                }
                                _fig.update_layout(**_po_layout)
                                _fig.update_xaxes(showgrid=False, showline=False, zeroline=False,
                                    tickfont=dict(size=9, color="#999"), tickangle=0)
                                _fig.update_yaxes(showgrid=False, showline=False, zeroline=False,
                                    showticklabels=False)
                                arrow = "▲" if p["change"] >= 0 else "▼"
                                col_a = "#22c55e" if p["change"] >= 0 else "#ef4444"
                                st.markdown(
                                    f'<div style="background:{_card_bg};border:1px solid {_card_border};'
                                    f'border-radius:12px;padding:10px 12px 0px;box-shadow:0 1px 4px rgba(0,0,0,0.04)">'
                                    f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:4px">'
                                    f'<div style="color:{_card_text};font-size:0.82rem;font-weight:600;line-height:1.3">{p["exercise"]}</div>'
                                    f'<div style="text-align:right;flex-shrink:0;margin-left:8px">'
                                    f'<div style="color:{col_a};font-size:0.75rem;font-weight:700">{arrow} {abs(p["change_pct"]):.0f}%</div>'
                                    f'<div style="color:{_card_sub};font-size:0.62rem">{p["n_sessions"]} sessions</div>'
                                    f'</div></div>'
                                    f'<div style="display:flex;gap:10px;margin-bottom:2px">'
                                    f'<div><div style="color:{_card_text};font-size:1.2rem;font-weight:700;font-family:DM Mono,monospace;line-height:1">{p["vol_latest"]/1000:.2f}t</div>'
                                    f'<div style="color:{_card_sub};font-size:0.58rem;text-transform:uppercase;letter-spacing:0.06em">this session</div></div>'
                                    f'<div><div style="color:{_card_text};font-size:1.2rem;font-weight:700;font-family:DM Mono,monospace;line-height:1">{p["max_weight"]:.1f} kg</div>'
                                    f'<div style="color:{_card_sub};font-size:0.58rem;text-transform:uppercase;letter-spacing:0.06em">max weight</div></div>'
                                    f'</div>'
                                    f'</div>',
                                    unsafe_allow_html=True
                                )
                                st.plotly_chart(_fig, use_container_width=True)

            st.markdown("### All-time Balance")
            vol_grp = fb_sets.groupby("muscle_group")["volume_kg"].sum().reset_index()
            if len(vol_grp) > 0:
                fig_pie = go.Figure(go.Pie(
                    labels=vol_grp["muscle_group"],
                    values=vol_grp["volume_kg"].round(0),
                    marker=dict(
                        colors=[MUSCLE_COLORS.get(g,"#ccc") for g in vol_grp["muscle_group"]],
                        line=dict(color="#ffffff", width=2)
                    ),
                    textinfo="label+percent",
                    textfont=dict(size=11, color="#1a1a1a"),
                    hole=0.45,
                    hovertemplate="<b>%{label}</b><br>%{value:,.0f} kg · %{percent}<extra></extra>",
                ))
                fig_pie.update_layout(**CHART_LAYOUT, height=260,
                    annotations=[dict(
                        text=f"{total_vol/1000:.1f}t",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=14, color="#1a1a1a", family="DM Mono")
                    )])
                st.plotly_chart(fig_pie, use_container_width=True)



        else:
            st.info("Fitbod data found but empty — re-run sync after uploading WorkoutExport.csv.")





with tab4:
    # ── Activity World Map ────────────────────────────────────────────────────────
    st.markdown("## Where I've Trained")

    # Bounding-box country lookup — keys match display names used in JS centroids
    _COUNTRY_BOXES = {
        "Finland":          [(59.5, 70.1, 19.0, 31.6)],
        "Iceland":          [(63.4, 66.6, -24.5, -13.5)],
        "Norway":           [(57.9, 71.2, 4.5, 31.0)],
        "Denmark":          [(54.5, 57.8, 8.0, 12.7)],
        "Sweden":           [(55.3, 69.1, 11.0, 24.2)],
        "Estonia":          [(57.5, 59.7, 21.8, 28.2)],
        "Ireland":          [(51.4, 55.4, -10.5, -5.9)],
        "United Kingdom":   [(49.9, 60.9, -8.0, 2.0)],
        "Portugal":         [(36.8, 42.2, -9.5, -6.1)],
        "Morocco":          [(27.7, 35.9, -13.2, -1.0)],
        "Spain":            [(35.9, 43.8, -9.4, 4.3)],
        "Belgium":          [(49.5, 51.5, 2.5, 6.4)],
        "Netherlands":      [(50.7, 53.6, 3.3, 7.2)],
        "Switzerland":      [(45.8, 47.8, 5.9, 10.5)],
        "France":           [(41.3, 51.1, -5.1, 9.6)],
        "Czech Republic":   [(48.5, 51.1, 12.1, 18.9)],
        "Germany":          [(47.3, 55.1, 5.9, 15.0)],
        "Austria":          [(46.4, 49.0, 9.5, 17.2)],
        "Poland":           [(49.0, 54.9, 14.1, 24.2)],
        "Hungary":          [(45.7, 48.6, 16.1, 22.9)],
        "Italy":            [(36.5, 47.1, 6.6, 18.5)],
        "Greece":           [(34.8, 41.8, 19.4, 29.7)],
        "Turkey":           [(35.8, 42.1, 25.7, 44.8)],
        "Canada":           [(42.0, 83.1, -141.0, -52.6)],
        "United States":    [(24.4, 49.4, -125.0, -66.9),
                             (51.0, 71.5, -168.0, -141.0)],
        "Mexico":           [(14.5, 32.7, -117.1, -86.7)],
        "Colombia":         [(-4.2, 12.5, -79.0, -66.9)],
        "Brazil":           [(-33.8, 5.3, -73.9, -34.8)],
        "Argentina":        [(-55.1, -21.8, -73.6, -53.6)],
        "UAE":              [(22.6, 26.1, 51.5, 56.4)],
        "Qatar":            [(24.5, 26.2, 50.7, 51.7)],
        "Oman":             [(16.6, 26.4, 52.0, 59.9)],
        "Saudi Arabia":     [(16.4, 32.2, 34.6, 55.7)],
        "Singapore":        [(1.1, 1.5, 103.6, 104.0)],
        "Cambodia":         [(10.4, 14.7, 102.3, 107.6)],
        "Vietnam":          [(8.4, 23.4, 102.1, 109.5)],
        "Thailand":         [(5.5, 20.5, 97.5, 105.6)],
        "Malaysia":         [(0.8, 7.4, 99.6, 119.3)],
        "Indonesia":        [(-11.0, 6.0, 95.0, 141.0)],
        "Myanmar":          [(9.5, 28.5, 92.2, 101.2)],
        "Sri Lanka":        [(5.9, 9.8, 79.6, 81.9)],
        "India":            [(6.0, 37.1, 68.1, 97.5)],
        "Japan":            [(24.0, 45.5, 122.9, 145.8)],
        "China":            [(18.0, 53.5, 73.5, 135.1)],
        "Rwanda":           [(-2.9, -1.0, 28.8, 30.9)],
        "Kenya":            [(-4.7, 5.0, 33.9, 41.9)],
        "Tanzania":         [(-11.7, -0.9, 29.4, 40.4)],
        "South Africa":     [(-34.8, -22.1, 16.5, 32.9)],
        "Mauritius":        [(-20.5, -19.9, 57.3, 57.8)],
        "Australia":        [(-43.6, -10.4, 113.2, 153.6)],
        "New Zealand":      [(-47.3, -34.4, 166.5, 178.6)],
    }

    # Country centroids for marker placement
    _CENTROIDS = {
        "Finland":          (64.0,  26.0),
        "Iceland":          (65.0, -18.0),
        "Norway":           (65.0,  14.0),
        "Denmark":          (56.0,  10.0),
        "Sweden":           (62.0,  15.0),
        "Estonia":          (58.7,  25.5),
        "Ireland":          (53.2,  -8.0),
        "United Kingdom":   (54.0,  -2.0),
        "Portugal":         (39.5,  -8.0),
        "Morocco":          (32.0,  -5.0),
        "Spain":            (40.0,  -3.5),
        "Belgium":          (50.8,   4.5),
        "Netherlands":      (52.3,   5.3),
        "Switzerland":      (47.0,   8.2),
        "France":           (46.0,   2.0),
        "Czech Republic":   (49.8,  15.5),
        "Germany":          (51.2,  10.4),
        "Austria":          (47.5,  14.5),
        "Poland":           (52.0,  20.0),
        "Hungary":          (47.2,  19.4),
        "Italy":            (42.5,  12.5),
        "Greece":           (39.0,  22.0),
        "Turkey":           (39.0,  35.0),
        "Canada":           (56.0, -96.0),
        "United States":    (38.0, -97.0),
        "Mexico":           (23.0,-102.0),
        "Colombia":         ( 4.0, -72.0),
        "Brazil":           (-10.0,-53.0),
        "Argentina":        (-34.0,-64.0),
        "UAE":              (24.0,  54.0),
        "Qatar":            (25.3,  51.2),
        "Oman":             (21.0,  57.0),
        "Saudi Arabia":     (25.0,  45.0),
        "Singapore":        ( 1.35,103.8),
        "Cambodia":         (12.5, 105.0),
        "Vietnam":          (16.0, 108.0),
        "Thailand":         (15.0, 101.0),
        "Malaysia":         ( 4.0, 109.5),
        "Indonesia":        (-5.0, 120.0),
        "Myanmar":          (17.0,  96.0),
        "Sri Lanka":        ( 7.5,  80.7),
        "India":            (20.0,  77.0),
        "Japan":            (36.0, 138.0),
        "China":            (35.0, 105.0),
        "Rwanda":           (-2.0,  30.0),
        "Kenya":            ( 1.0,  38.0),
        "Tanzania":         (-6.0,  35.0),
        "South Africa":     (-29.0, 25.0),
        "Mauritius":        (-20.2, 57.5),
        "Australia":        (-25.0,133.0),
        "New Zealand":      (-41.0,174.0),
    }

    def _latlon_to_country(lat, lon):
        for country, boxes in _COUNTRY_BOXES.items():
            for la, lb, lo, lob in boxes:
                if la <= lat <= lb and lo <= lon <= lob:
                    return country
        return "Other"

    @st.cache_data(ttl=3600, show_spinner=False)
    def build_country_map(_polylines_data):
        if not _polylines_data:
            return {}
        from collections import defaultdict
        country_data = defaultdict(lambda: {"count": 0})
        for act_id, poly in _polylines_data.items():
            if not poly:
                continue
            try:
                decoded = decode_polyline(poly)
                if decoded:
                    lat, lon = decoded[0]
                    country = _latlon_to_country(lat, lon)
                    country_data[country]["count"] += 1
            except Exception:
                continue
        return {k: v for k, v in country_data.items() if k != "Other"}

    _country_map = build_country_map(_polylines)

    if _country_map:
        _total_countries = len(_country_map)
        _total_poly_acts = sum(v["count"] for v in _country_map.values())

        _cm1, _cm2, _cm3, _cm4 = st.columns(4)
        _cm1.metric("Countries visited", _total_countries)
        _cm2.metric("Activities with GPS", f"{_total_poly_acts:,}")
        _cm3.metric("Top country", max(_country_map, key=lambda k: _country_map[k]["count"]))
        _cm4.metric("Years active", f"{df['date'].dt.year.min()}\u2013{df['date'].dt.year.max()}")

        import json as _json

        # Build marker data: [{name, lat, lon, count, color, radius}]
        def _mk_color(n):
            if n >= 500: return "#b03020"
            if n >= 100: return "#d94f30"
            if n >= 20:  return "#f07030"
            if n >= 5:   return "#f5a050"
            return "#fad090"

        def _mk_radius(n):
            # 8px minimum, scale with sqrt up to ~40px
            import math
            return max(8, min(40, 8 + 10 * math.log10(n + 1)))

        _markers = []
        for name, d in _country_map.items():
            if name in _CENTROIDS:
                lat, lon = _CENTROIDS[name]
                _markers.append({
                    "name": name,
                    "lat": lat,
                    "lon": lon,
                    "count": d["count"],
                    "color": _mk_color(d["count"]),
                    "radius": round(_mk_radius(d["count"]), 1),
                })

        _markers_json = _json.dumps(_markers)

        _map_html = """<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html,body,#map { margin:0; padding:0; width:100%; height:500px; font-family:Inter,sans-serif; }
  .tip {
    background:white; padding:10px 14px; border-radius:10px;
    border:1px solid #e0e0e0; box-shadow:0 4px 16px rgba(0,0,0,0.12);
    font-size:13px; pointer-events:none; min-width:150px;
  }
  .tip-name { font-weight:700; font-size:14px; color:#111; margin-bottom:4px; }
  .tip-count { color:#fc4c02; font-weight:700; font-size:18px; font-family:monospace; }
  .tip-label { color:#888; font-size:11px; margin-top:1px; }
</style>
</head><body>
<div id="map"></div>
<script>
const MARKERS = """ + _markers_json + """;

const map = L.map('map', {
  center: [25, 15], zoom: 2,
  minZoom: 1, maxZoom: 8,
});

// CartoDB Positron — clean, no distracting labels
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
  subdomains: 'abcd', maxZoom: 20
}).addTo(map);

// Info box
const info = L.control({position: 'topright'});
info.onAdd = function() {
  this._div = L.DomUtil.create('div', 'tip');
  this._div.innerHTML = '<div class="tip-name" style="color:#aaa">Hover a marker</div>';
  return this._div;
};
info.addTo(map);

// Legend
const legend = L.control({position: 'bottomright'});
legend.onAdd = function() {
  const d = L.DomUtil.create('div', 'tip');
  d.style.minWidth = '130px';
  d.innerHTML =
    '<div style="font-size:11px;font-weight:700;color:#888;margin-bottom:6px;text-transform:uppercase;letter-spacing:.05em">Activities</div>' +
    ['500+','100–499','20–99','5–19','1–4'].map((lbl,i) => {
      const c = ['#b03020','#d94f30','#f07030','#f5a050','#fad090'][i];
      return `<div style="display:flex;align-items:center;gap:7px;margin-bottom:3px">
        <div style="width:12px;height:12px;border-radius:50%;background:${c};flex-shrink:0"></div>
        <span style="font-size:12px;color:#444">${lbl}</span></div>`;
    }).join('');
  return d;
};
legend.addTo(map);

// Draw markers
MARKERS.forEach(m => {
  const circle = L.circleMarker([m.lat, m.lon], {
    radius: m.radius,
    fillColor: m.color,
    color: 'white',
    weight: 2,
    opacity: 1,
    fillOpacity: 0.88,
  }).addTo(map);

  circle.on('mouseover', function() {
    this.setStyle({weight: 3, color: '#fc4c02'});
    info._div.innerHTML =
      '<div class="tip-name">' + m.name + '</div>' +
      '<div class="tip-count">' + m.count.toLocaleString() + '</div>' +
      '<div class="tip-label">GPS activities</div>';
  });
  circle.on('mouseout', function() {
    this.setStyle({weight: 2, color: 'white'});
    info._div.innerHTML = '<div class="tip-name" style="color:#aaa">Hover a marker</div>';
  });
  circle.on('click', function() {
    info._div.innerHTML =
      '<div class="tip-name">' + m.name + '</div>' +
      '<div class="tip-count">' + m.count.toLocaleString() + '</div>' +
      '<div class="tip-label">GPS activities</div>';
  });
});

// Finland home pulse
const homeIcon = L.divIcon({
  html: `<div style="position:relative;width:20px;height:20px">
    <div style="position:absolute;inset:0;border-radius:50%;background:rgba(252,76,2,0.2);animation:pulse 2s infinite"></div>
    <div style="position:absolute;inset:4px;border-radius:50%;background:#fc4c02;border:2px solid white"></div>
    <style>@keyframes pulse{0%,100%{transform:scale(1);opacity:.6}50%{transform:scale(1.8);opacity:0}}</style>
  </div>`,
  className: '', iconSize: [20, 20], iconAnchor: [10, 10]
});
L.marker([62.0, 25.0], {icon: homeIcon, zIndexOffset: 1000})
  .bindTooltip('🏠 Home base — Finland', {direction: 'right', offset: [12, 0]})
  .addTo(map);
</script>
</body></html>"""

        st.components.v1.html(_map_html, height=510, scrolling=False)

        with st.expander("📍 All countries", expanded=False):
            _sorted_countries = sorted(_country_map.items(), key=lambda x: -x[1]["count"])
            _col_a, _col_b = st.columns(2)
            mid = len(_sorted_countries) // 2
            for _col, _items in [(_col_a, _sorted_countries[:mid]), (_col_b, _sorted_countries[mid:])]:
                with _col:
                    for _name, _cdata in _items:
                        st.markdown(
                            f'<div style="display:flex;justify-content:space-between;'
                            f'padding:5px 0;border-bottom:1px solid {_card_border};">'
                            f'<span style="color:{_card_text};font-size:0.82rem">{_name}</span>'
                            f'<span style="color:#fc4c02;font-size:0.82rem;font-family:DM Mono,monospace;font-weight:600">{_cdata["count"]:,}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
    else:
        st.info("No GPS polyline data found. Run the Strava sync to populate polylines.json.")

    st.markdown('<hr style="border:none;border-top:1px solid #e8e4de;margin:1rem 0">', unsafe_allow_html=True)

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
          <div style="color:{_card_text};font-weight:600;margin-bottom:4px">{name}</div>
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


    if fitbod_data:
        fb_sets_local     = pd.DataFrame(fitbod_data.get("sets", []))
        fb_records_local  = pd.DataFrame(fitbod_data.get("records", []))
        fb_sessions_local = pd.DataFrame(fitbod_data.get("sessions", []))
        if len(fb_sets_local) > 0:
            fb_sets_local["date"] = pd.to_datetime(fb_sets_local["date"])
            if "volume_kg" not in fb_sets_local.columns:
                fb_sets_local["volume_kg"] = fb_sets_local["sets"] * fb_sets_local["reps"] * fb_sets_local["weight_kg"]
        if len(fb_sessions_local) > 0:
            fb_sessions_local["date"] = pd.to_datetime(fb_sessions_local["date"])
        fb_sets     = fb_sets_local
        fb_records  = fb_records_local
        fb_sessions = fb_sessions_local

        # ── Personal records table ────────────────────────────────────────────
        if len(fb_records) > 0:
            with st.expander("📋 Personal Records — all exercises", expanded=False):
                top_r = fb_records[fb_records["max_weight_kg"] > 0].head(25)
                rows_r = ""
                for _, row in top_r.iterrows():
                    grp = fb_sets[fb_sets["exercise"]==row["exercise"]]["muscle_group"].mode()
                    grp = grp.iloc[0] if len(grp) > 0 else "Other"
                    col = MUSCLE_COLORS.get(grp, "#888")
                    last = pd.to_datetime(row["last_date"]).strftime("%d %b %Y") if row.get("last_date") else "—"
                    rows_r += (
                        "<tr>"
                        + f'<td style="color:{_card_text};font-weight:500">{row["exercise"]}</td>'
                        + f'<td><span style="background:{col}22;color:{col};font-size:0.65rem;font-weight:700;padding:2px 6px;border-radius:4px">{grp}</span></td>'
                        + f'<td style="color:#fc4c02;font-weight:700;font-family:DM Mono,monospace">{row["max_weight_kg"]:.1f} kg</td>'
                        + f'<td style="color:{_card_text}">{int(row["max_reps"])}</td>'
                        + f'<td style="color:{_card_text}">{int(row["total_sets"]):,}</td>'
                        + f'<td style="color:#999;font-size:0.78rem">{last}</td>'
                        + "</tr>"
                    )
                st.markdown(
                    '<div style="background:{_card_bg};border:1px solid {_card_border};border-radius:12px;overflow:hidden">'
                    '<table style="width:100%;border-collapse:collapse;font-family:DM Sans,sans-serif;font-size:0.82rem">'
                    '<thead><tr style="background:#f7f5f2;border-bottom:2px solid #e8e4de">'
                    '<th style="color:#888;font-size:0.62rem;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;padding:10px 14px;text-align:left">Exercise</th>'
                    '<th style="color:#888;font-size:0.62rem;font-weight:600;text-transform:uppercase;padding:10px 8px;text-align:left">Group</th>'
                    '<th style="color:#888;font-size:0.62rem;font-weight:600;text-transform:uppercase;padding:10px 8px;text-align:left">PR</th>'
                    '<th style="color:#888;font-size:0.62rem;font-weight:600;text-transform:uppercase;padding:10px 8px;text-align:left">Max Reps</th>'
                    '<th style="color:#888;font-size:0.62rem;font-weight:600;text-transform:uppercase;padding:10px 8px;text-align:left">Total Sets</th>'
                    '<th style="color:#888;font-size:0.62rem;font-weight:600;text-transform:uppercase;padding:10px 8px;text-align:left">Last</th>'
                    f'</tr></thead><tbody>{rows_r}</tbody></table></div>',
                    unsafe_allow_html=True
                )


    # ── Recent sessions ────────────────────────────────────────────────────




    st.markdown("### Recent Strength Sessions")
    recent_fb = fb_sessions.head(10)
    if len(recent_fb) > 0:
        rows_sess = ""
        for _, row in recent_fb.iterrows():
            groups = ", ".join(row["muscle_groups"]) if isinstance(row["muscle_groups"], list) else str(row["muscle_groups"])
            rows_sess += (
                "<tr>"
                + f'<td style="color:#999;font-size:0.78rem">{row["date"].strftime("%d %b %Y")}</td>'
                + f'<td style="color:{_card_text};font-weight:500">{groups}</td>'
                + f'<td style="color:{_card_text}">{int(row["exercises"])} exercises · {int(row["total_sets"])} sets</td>'
                + f'<td style="color:#fc4c02;font-weight:600;font-family:DM Mono,monospace">{row["total_volume"]/1000:.2f}t</td>'
                + "</tr>"
            )
        st.markdown(
            '<div style="background:{_card_bg};border:1px solid {_card_border};border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,0.06)">'
            '<table style="width:100%;border-collapse:collapse;font-family:DM Sans,sans-serif;font-size:0.83rem">'
            '<thead><tr style="background:#f7f5f2;border-bottom:2px solid #e8e4de">'
            '<th style="color:#888;font-size:0.62rem;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;padding:10px 14px;text-align:left">Date</th>'
            '<th style="color:#888;font-size:0.62rem;font-weight:600;text-transform:uppercase;padding:10px 8px;text-align:left">Muscle Groups</th>'
            '<th style="color:#888;font-size:0.62rem;font-weight:600;text-transform:uppercase;padding:10px 8px;text-align:left">Exercises</th>'
            '<th style="color:#888;font-size:0.62rem;font-weight:600;text-transform:uppercase;padding:10px 8px;text-align:left">Volume</th>'
            f'</tr></thead><tbody>{rows_sess}</tbody></table></div>',
            unsafe_allow_html=True
        )


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

    def _eff_label(re_val):
        if pd.isna(re_val) or re_val <= 0: return "", "#aaa"
        elif re_val < 8:   return "Recovery", "#50c850"
        elif re_val < 36:  return "Base",     "#ffa500"
        elif re_val < 95:  return "Quality",  "#ff6b35"
        else:              return "Peak",     "#fc4c02"
    recent_acts["_eff_lbl"] = recent_acts["rel_effort"].apply(lambda v: _eff_label(v)[0])
    recent_acts["_eff_col"] = recent_acts["rel_effort"].apply(lambda v: _eff_label(v)[1])

    # Build HTML table — guaranteed light theme (st.dataframe uses canvas, ignores CSS)
    TH = 'color:#888;font-size:0.68rem;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;padding:10px 8px;'
    _trows = ""
    for _, r in recent_acts.iterrows():
        sport_color = SPORT_COLORS.get(r["sport"], "#888")
        _trows += (
            "<tr>"
            + f'<td style="color:#999;font-size:0.78rem">{r["Date"]}</td>'
            + f'<td><span style="background:{sport_color}18;color:{sport_color};font-size:0.62rem;font-weight:700;padding:3px 9px;border-radius:999px;text-transform:uppercase;letter-spacing:0.05em">{r["sport"]}</span></td>'
            + (f'<td style="padding:8px"><span style="background:{r["_eff_col"]}22;color:{r["_eff_col"]};font-size:0.62rem;font-weight:700;padding:3px 9px;border-radius:999px">{r["_eff_lbl"]}</span></td>' if r["_eff_lbl"] else '<td>—</td>')
            + f'<td style="color:{_card_text};font-weight:500">{str(r["name"])[:35] if pd.notna(r["name"]) else r["sport"]}</td>'
            + f'<td style="color:{_card_text};text-align:right;padding:10px 8px">{r["Km"] if r["Km"] > 0 else "—"}</td>'
            + f'<td style="color:{_card_text};padding:10px 8px">{r["Time"]}</td>'
            + f'<td style="color:{_card_text};padding:10px 8px">{r["Pace"]}</td>'
            + f'<td style="color:{_card_text};text-align:right;padding:10px 8px">{r["HR"]}</td>'
            + f'<td style="color:{_card_text};text-align:right;padding:10px 8px">{r["Elev"]}</td>'
            + "</tr>"
        )
    st.markdown(
        '<div style="background:{_card_bg};border:1px solid {_card_border};border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,0.06)">' +
        '<table style="width:100%;border-collapse:collapse;font-family:DM Sans,sans-serif;font-size:0.83rem">' +
        f'<thead><tr style="background:{_card_bg2};border-bottom:2px solid {_card_border}">' +
        f'<th style="{TH}text-align:left;padding:10px 14px">Date</th>' +
        f'<th style="{TH}text-align:left">Sport</th>' +
        f'<th style="{TH}text-align:left">Effort</th>' +
        f'<th style="{TH}text-align:left;padding:10px 14px">Activity</th>' +
        f'<th style="{TH}text-align:right">km</th>' +
        f'<th style="{TH}text-align:left">Time</th>' +
        f'<th style="{TH}text-align:left">Pace</th>' +
        f'<th style="{TH}text-align:right">HR</th>' +
        f'<th style="{TH}text-align:right">Elev</th>' +
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


    st.markdown('<hr style="border:none;border-top:1px solid #e8e4de;margin:0.8rem 0">', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════════
    # STRENGTH TRAINING (Fitbod)
    # ══════════════════════════════════════════════════════════════════════════════






    st.markdown("""
    <div style="margin-top:3rem;padding-top:1rem;border-top:1px solid #e2ddd8;
                color:#444;font-size:0.75rem;text-align:center">
      Built on Strava · Oura · Fitbod data · Powered by Streamlit
    </div>
    """, unsafe_allow_html=True)
