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
GDRIVE_FILE_ID = "1mgqa52ET2Ru7XIjUvMl4zgK1Zb1Idlmi"

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
@st.cache_data(ttl=3600)
def load_data():
    url = f"https://drive.google.com/uc?export=download&id={GDRIVE_FILE_ID}"
    r = requests.get(url)
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
    df["calories"]     = raw["Calories"]
    df["rel_effort"]   = raw["Relative Effort"]
    pace_mask = df["sport"].isin(["Run","Walk","Virtual Run","Hike"])
    df["pace_min_km"] = None
    valid = pace_mask & (df["dist_km"] > 0)
    df.loc[valid, "pace_min_km"] = df.loc[valid, "moving_min"] / df.loc[valid, "dist_km"]
    df["is_endurance"] = df["sport"].isin(ENDURANCE)
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔥 Filters")
    st.markdown("---")

    all_sports = sorted(df["sport"].unique().tolist())
    selected_sports = st.multiselect("Sports", all_sports, default=all_sports)

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    date_range = st.date_input("Date range",
        value=(min_date, max_date), min_value=min_date, max_value=max_date)

    start_date, end_date = (date_range[0], date_range[1]) \
        if len(date_range) == 2 else (min_date, max_date)

    st.markdown("---")
    if st.button("🔄 Reload data"):
        st.cache_data.clear()
        st.rerun()

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
    {df['date'].min().strftime('%b %Y')} — {df['date'].max().strftime('%b %Y')} 
    · {df['year'].nunique()} years
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
t1.metric("CTL — Fitness",   f"{latest['ctl']:.1f}", "42-day avg load")
t2.metric("ATL — Fatigue",   f"{latest['atl']:.1f}", "7-day avg load")
tsb = latest["tsb"]
tsb_str = "Fresh 🟢" if tsb > 5 else ("Tired 🔴" if tsb < -20 else "Training 🟡")
t3.metric("TSB — Freshness", f"{tsb:+.1f}", tsb_str)

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
weekly = (recent_w[recent_w["sport"].isin(SHOW)]
          .groupby(["week","sport"])["dist_km"].sum().reset_index())

fig2 = go.Figure()
for sport in SHOW:
    s = weekly[weekly["sport"]==sport]
    if len(s)==0: continue
    fig2.add_trace(go.Bar(x=s["week"], y=s["dist_km"].round(1),
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
        x=yr_run["year"], y=yr_run["dist_km"] if "km" in yr_run else yr_run["dist_km"],
        marker=dict(
            color=yr_run["dist_km"],
            colorscale=[[0,"#3a1a0a"],[0.5,"#c03000"],[1,"#fc4c02"]],
            showscale=False),
        text=yr_run["dist_km"].round().astype(int).astype(str)+" km",
        textposition="outside",
        textfont=dict(color="#888", size=10)))
    fig_r.update_layout(**CHART_LAYOUT, height=300, yaxis_title="dist_km",
        margin=dict(t=10,b=30,l=40,r=10))
    fig_r.update_xaxes(**axis_style())
    fig_r.update_yaxes(**axis_style())
    st.plotly_chart(fig_r, use_container_width=True)

with col_ride:
    st.markdown("### 🚴 Cycling")
    cycling_types = ["Ride","Virtual Ride","E-Bike Ride"]
    cyc = fdf[fdf["sport"].isin(cycling_types)]
    yr_cyc = cyc.groupby(["year","sport"])["dist_km"].sum().reset_index()
    cyc_colors = {"Ride":"#ffa500","Virtual Ride":"#ffcc44","E-Bike Ride":"#ce93d8"}
    fig_c = go.Figure()
    for ctype in cycling_types:
        s = yr_cyc[yr_cyc["sport"]==ctype]
        if len(s)==0: continue
        fig_c.add_trace(go.Bar(x=s["year"], y=s["dist_km"].round(),
            name=ctype, marker_color=cyc_colors[ctype]))
    yr_cyc_tot = cyc.groupby("year")["dist_km"].sum().reset_index()
    fig_c.add_trace(go.Scatter(x=yr_cyc_tot["year"], y=yr_cyc_tot["dist_km"].round(),
        mode="text",
        text=yr_cyc_tot["dist_km"].round().astype(int).astype(str)+" km",
        textposition="top center",
        textfont=dict(size=10, color="#666"), showlegend=False))
    fig_c.update_layout(**CHART_LAYOUT, barmode="stack", height=300,
        yaxis_title="km", margin=dict(t=10,b=30,l=40,r=10))
    fig_c.update_xaxes(**axis_style())
    fig_c.update_yaxes(**axis_style())
    st.plotly_chart(fig_c, use_container_width=True)

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
    if row["sport"] not in ["Run","Walk","Virtual Run","Hike"] or row["dist_km"]==0:
        return "—"
    p = row["moving_min"] / row["dist_km"]
    return f"{int(p)}:{int((p%1)*60):02d} /km"

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
