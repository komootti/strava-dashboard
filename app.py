import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Strava Dashboard", page_icon="🏃", layout="wide")

# ── Data path — update this if running locally ────────────────────────────────
ACTIVITIES_CSV = "activities.csv"
# ─────────────────────────────────────────────────────────────────────────────

ENDURANCE = {"Run","Ride","Virtual Ride","Virtual Run","Walk","Hike",
             "Nordic Ski","Swim","Rowing","E-Bike Ride","Stand Up Paddling","Kayaking"}

@st.cache_data
def load_data():
    raw = pd.read_csv(ACTIVITIES_CSV, low_memory=False)
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
st.sidebar.title("🏃 Strava Dashboard")
st.sidebar.markdown("---")

all_sports = sorted(df["sport"].unique().tolist())
selected_sports = st.sidebar.multiselect("Sports", all_sports, default=all_sports)

min_date = df["date"].min().date()
max_date = df["date"].max().date()
date_range = st.sidebar.date_input("Date range",
    value=(min_date, max_date), min_value=min_date, max_value=max_date)

start_date, end_date = (date_range[0], date_range[1]) if len(date_range) == 2 else (min_date, max_date)

mask = (
    df["sport"].isin(selected_sports) &
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
)
fdf = df[mask].copy()

st.sidebar.markdown("---")
st.sidebar.metric("Activities shown", f"{len(fdf):,}")
if st.sidebar.button("🔄 Reload data"):
    st.cache_data.clear()
    st.rerun()

# ── Header metrics ────────────────────────────────────────────────────────────
st.title("🏃 Strava Training Dashboard")

end = fdf[fdf["is_endurance"]]
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Activities",   f"{len(fdf):,}")
c2.metric("Distance",     f"{end['dist_km'].sum():,.0f} km")
c3.metric("Elevation",    f"{end['elev_gain_m'].sum():,.0f} m")
c4.metric("Moving time",  f"{int(end['moving_min'].sum()//60):,}h")
c5.metric("Calories",     f"{fdf['calories'].sum():,.0f}")

st.markdown("---")

# ── 1. CTL / ATL / TSB ───────────────────────────────────────────────────────
st.subheader("Training Load — CTL · ATL · TSB")

end2 = df[df["is_endurance"]].copy()
end2["tss"] = end2["rel_effort"].fillna(
    end2["moving_min"] * (end2["avg_hr"].fillna(130) / 150) ** 2 * 0.5)

daily = (end2.groupby(end2["date"].dt.normalize())["tss"]
             .sum().reset_index())
daily.columns = ["date", "tss"]
daily["date"] = pd.to_datetime(daily["date"])
full = pd.date_range(daily["date"].min(), daily["date"].max(), freq="D")
daily = daily.set_index("date").reindex(full, fill_value=0).reset_index()
daily.columns = ["date", "tss"]
daily["ctl"] = daily["tss"].ewm(span=42, adjust=False).mean()
daily["atl"] = daily["tss"].ewm(span=7,  adjust=False).mean()
daily["tsb"] = daily["ctl"] - daily["atl"]

latest = daily.iloc[-1]
t1, t2, t3 = st.columns(3)
t1.metric("CTL — Fitness",   f"{latest['ctl']:.1f}")
t2.metric("ATL — Fatigue",   f"{latest['atl']:.1f}")
tsb_val = latest["tsb"]
tsb_label = "Fresh 🟢" if tsb_val > 5 else ("Tired 🔴" if tsb_val < -20 else "Training 🟡")
t3.metric("TSB — Freshness", f"{tsb_val:+.1f}", tsb_label)

days_back = st.slider("Days to show", 90, 1825, 365, step=90, key="ctl_slider")
plot = daily[daily["date"] >= daily["date"].max() - pd.Timedelta(days=days_back)]

fig1 = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.65, 0.35],
    subplot_titles=("CTL (fitness) vs ATL (fatigue)", "TSB — freshness"))
fig1.add_trace(go.Bar(x=plot["date"], y=plot["tss"],
    marker_color="rgba(180,180,180,0.35)", name="Daily load"), row=1, col=1)
fig1.add_trace(go.Scatter(x=plot["date"], y=plot["ctl"].round(1),
    mode="lines", line=dict(color="#e07b54", width=2.5), name="CTL fitness"), row=1, col=1)
fig1.add_trace(go.Scatter(x=plot["date"], y=plot["atl"].round(1),
    mode="lines", line=dict(color="#5b8dd9", width=2), name="ATL fatigue"), row=1, col=1)
fig1.add_trace(go.Bar(x=plot["date"], y=plot["tsb"].clip(lower=0).round(1),
    marker_color="rgba(80,180,120,0.6)", name="Fresh"), row=2, col=1)
fig1.add_trace(go.Bar(x=plot["date"], y=plot["tsb"].clip(upper=0).round(1),
    marker_color="rgba(220,80,80,0.5)", name="Fatigued"), row=2, col=1)
fig1.add_hline(y=0, line_width=1, line_color="gray", row=2, col=1)
fig1.update_layout(height=480, barmode="relative", plot_bgcolor="white",
    paper_bgcolor="white", legend=dict(orientation="h", y=1.05),
    margin=dict(t=40, b=20, l=50, r=20))
fig1.update_yaxes(gridcolor="#f0f0f0")
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ── 2. Weekly Volume ──────────────────────────────────────────────────────────
st.subheader("Weekly Volume by Sport")

weeks_back = st.slider("Weeks to show", 12, 156, 52, step=4, key="weekly_slider")
cutoff = fdf["date"].max() - pd.Timedelta(weeks=weeks_back)
recent = fdf[fdf["date"] >= cutoff].copy()
recent["week"] = recent["date"].dt.to_period("W").dt.start_time

SHOW = [s for s in ["Run","Ride","Virtual Ride","Walk","E-Bike Ride","Rowing"]
        if s in selected_sports]
weekly = (recent[recent["sport"].isin(SHOW)]
          .groupby(["week","sport"])["dist_km"].sum().reset_index())

colors = {"Run":"#e07b54","Ride":"#5b8dd9","Virtual Ride":"#8ab4f8",
          "Walk":"#7dc99e","E-Bike Ride":"#c49de8","Rowing":"#f0c36d"}

fig2 = go.Figure()
for sport in SHOW:
    s = weekly[weekly["sport"] == sport]
    if len(s) == 0: continue
    fig2.add_trace(go.Bar(x=s["week"], y=s["dist_km"].round(1),
        name=sport, marker_color=colors.get(sport, "#aaa")))
fig2.update_layout(barmode="stack", height=360, plot_bgcolor="white",
    paper_bgcolor="white", yaxis_title="km",
    legend=dict(orientation="h", y=1.05),
    margin=dict(t=20, b=20, l=50, r=20))
fig2.update_yaxes(gridcolor="#f0f0f0")
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── 3. Aerobic Efficiency ─────────────────────────────────────────────────────
st.subheader("Aerobic Efficiency — HR & Pace Trend by Year")

runs = fdf[(fdf["sport"] == "Run") & (fdf["dist_km"] > 3)].copy()
runs["pace_min_km"] = pd.to_numeric(runs["pace_min_km"], errors="coerce")
runs = runs[runs["pace_min_km"].between(4, 12) & runs["avg_hr"].notna()]

if len(runs) > 0:
    yearly_r = (runs.groupby("year")
                    .agg(avg_hr=("avg_hr","mean"), avg_pace=("pace_min_km","mean"))
                    .reset_index())
    fig3 = make_subplots(rows=1, cols=2,
        subplot_titles=("Avg HR per year — runs (lower = fitter)",
                        "Avg pace per year — runs (lower = faster)"))
    fig3.add_trace(go.Scatter(x=yearly_r["year"], y=yearly_r["avg_hr"].round(1),
        mode="lines+markers", line=dict(color="#e07b54", width=2.5),
        marker=dict(size=7)), row=1, col=1)
    fig3.add_trace(go.Scatter(x=yearly_r["year"], y=yearly_r["avg_pace"].round(2),
        mode="lines+markers", line=dict(color="#5b8dd9", width=2.5),
        marker=dict(size=7)), row=1, col=2)
    fig3.update_layout(height=340, showlegend=False, plot_bgcolor="white",
        paper_bgcolor="white", margin=dict(t=40, b=20, l=50, r=20))
    fig3.update_yaxes(gridcolor="#f0f0f0")
    fig3.update_yaxes(autorange="reversed", row=1, col=2)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No run data for selected filters.")

st.markdown("---")

# ── 4. Yearly Running Volume ──────────────────────────────────────────────────
st.subheader("Yearly Running Volume")

yearly_run = (fdf[fdf["sport"] == "Run"]
              .groupby("year").agg(km=("dist_km","sum")).reset_index())

if len(yearly_run) > 0:
    fig4 = go.Figure(go.Bar(
        x=yearly_run["year"], y=yearly_run["km"].round(),
        marker_color="#e07b54",
        text=yearly_run["km"].round().astype(int).astype(str) + " km",
        textposition="outside"))
    fig4.update_layout(height=340, plot_bgcolor="white", paper_bgcolor="white",
        yaxis_title="km", margin=dict(t=30, b=20, l=50, r=20))
    fig4.update_yaxes(gridcolor="#f0f0f0")
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("No run data for selected filters.")

st.markdown("---")

# ── 5. Yearly Cycling Volume ──────────────────────────────────────────────────
st.subheader("Yearly Cycling Volume")

cycling_types = ["Ride", "Virtual Ride", "E-Bike Ride"]
cycling = fdf[fdf["sport"].isin(cycling_types)].copy()
yearly_cyc = (cycling.groupby(["year","sport"])["dist_km"]
                     .sum().reset_index())

if len(yearly_cyc) > 0:
    cyc_colors = {"Ride":"#5b8dd9","Virtual Ride":"#8ab4f8","E-Bike Ride":"#c49de8"}
    fig5 = go.Figure()
    for ctype in cycling_types:
        s = yearly_cyc[yearly_cyc["sport"] == ctype]
        if len(s) == 0: continue
        fig5.add_trace(go.Bar(
            x=s["year"], y=s["dist_km"].round(),
            name=ctype, marker_color=cyc_colors[ctype],
            text=s["dist_km"].round().astype(int).astype(str) + " km",
            textposition="inside"))
    # Total label on top
    yearly_cyc_total = cycling.groupby("year")["dist_km"].sum().reset_index()
    fig5.add_trace(go.Scatter(
        x=yearly_cyc_total["year"],
        y=yearly_cyc_total["dist_km"].round(),
        mode="text",
        text=yearly_cyc_total["dist_km"].round().astype(int).astype(str) + " km",
        textposition="top center",
        textfont=dict(size=11, color="#444"),
        showlegend=False))
    fig5.update_layout(barmode="stack", height=360, plot_bgcolor="white",
        paper_bgcolor="white", yaxis_title="km",
        legend=dict(orientation="h", y=1.05),
        margin=dict(t=30, b=20, l=50, r=20))
    fig5.update_yaxes(gridcolor="#f0f0f0")
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.info("No cycling data for selected filters.")

st.markdown("---")

# ── 6. Recent Activities ──────────────────────────────────────────────────────
st.subheader("Recent Activities")

n_rows = st.slider("Activities to show", 10, 100, 20, step=10, key="recent_slider")
recent_acts = fdf.sort_values("date", ascending=False).head(n_rows).copy()

def fmt_pace(row):
    if row["sport"] not in ["Run","Walk","Virtual Run","Hike"] or row["dist_km"] == 0:
        return "—"
    p = row["moving_min"] / row["dist_km"]
    return f"{int(p)}:{int((p % 1) * 60):02d} /km"

recent_acts["Pace"] = recent_acts.apply(fmt_pace, axis=1)
recent_acts["Date"] = recent_acts["date"].dt.strftime("%d %b %Y")
recent_acts["Km"]   = recent_acts["dist_km"].round(1)
recent_acts["Time"] = recent_acts["moving_min"].apply(
    lambda m: f"{int(m//60)}h {int(m%60):02d}m" if not pd.isna(m) else "—")
recent_acts["HR"]   = recent_acts["avg_hr"].apply(
    lambda h: f"{int(h)} bpm" if not pd.isna(h) else "—")
recent_acts["Elev"] = recent_acts["elev_gain_m"].apply(
    lambda e: f"{int(e)} m" if not pd.isna(e) else "—")

st.dataframe(
    recent_acts[["Date","sport","name","Km","Time","Pace","HR","Elev"]]
    .rename(columns={"sport":"Sport","name":"Activity"}),
    use_container_width=True, hide_index=True)
