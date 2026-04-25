"""
fix_chat.py — adds the 💬 Ask chat tab to the Strava dashboard.

Fixes two issues:
1. The Leaflet map HTML string closing was at 0-indent, breaking tab4's
   scope and making everything after it invisible to Streamlit's tab system.
2. Adds tab5 with a full Claude-powered chat interface.

Run against the ORIGINAL app.py.
"""
import sys, py_compile
PATH = "app.py"

with open(PATH, "r", encoding="utf-8") as fh:
    code = fh.read()

# ── Fix 1: re-indent the broken HTML string closing in the Leaflet map ───────
OLD_HTML_CLOSE = '</script></body></html>"""\n        st.components.v1.html(_map_html, height=500, scrolling=False)'
NEW_HTML_CLOSE = '        </script></body></html>"""\n        st.components.v1.html(_map_html, height=500, scrolling=False)'

if OLD_HTML_CLOSE not in code:
    print("ERROR: could not find Leaflet HTML string closing")
    sys.exit(1)

code = code.replace(OLD_HTML_CLOSE, NEW_HTML_CLOSE, 1)
print("✅ Fix 1: Leaflet HTML string closing re-indented (tab4 scope restored)")

# ── Fix 2: add tab5 to the tabs declaration ───────────────────────────────────
OLD_TABS = 'tab1, tab2, tab3, tab4 = st.tabs(["📊  Overview", "🏃  Training", "💪  Strength", "📋  History"])'
NEW_TABS = 'tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊  Overview", "🏃  Training", "💪  Strength", "📋  History", "💬  Ask"])'

if OLD_TABS not in code:
    print("ERROR: could not find tabs line")
    sys.exit(1)

code = code.replace(OLD_TABS, NEW_TABS, 1)
print("✅ Fix 2: tab5 added to tabs declaration")

# ── Fix 3: insert tab5 block before the footer ────────────────────────────────
FOOTER = '    st.markdown("""\n    <div style="margin-top:3rem;padding-top:1rem;border-top:1px solid #e2ddd8;\n                color:#444;font-size:0.75rem;text-align:center">\n      Built on Strava · Oura · Fitbod data · Powered by Streamlit\n    </div>\n    """, unsafe_allow_html=True)'

if FOOTER not in code:
    print("ERROR: could not find footer")
    sys.exit(1)

TAB5 = '''with tab5:
    # ── AI Chat — Ask your data ───────────────────────────────────────────────
    _api_key_chat = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""

    if not _api_key_chat:
        st.warning("Add ANTHROPIC_API_KEY to your Streamlit secrets to enable the chat.")
    else:
        def _build_data_summary(df):
            if df is None or df.empty:
                return "No activity data available."
            out = []
            out.append(f"Total activities: {len(df):,}")
            out.append(f"Date range: {df[\'date\'].min().strftime(\'%Y-%m-%d\')} to {df[\'date\'].max().strftime(\'%Y-%m-%d\')}")
            out.append("\\nActivities by sport:")
            for sport, cnt in df["sport"].value_counts().head(10).items():
                out.append(f"  {sport}: {cnt:,}")
            if "dist_km" in df.columns:
                out.append(f"\\nTotal distance: {df[\'dist_km\'].sum():,.0f} km")
                for s, km in df.groupby("sport")["dist_km"].sum().sort_values(ascending=False).head(5).items():
                    out.append(f"  {s}: {km:,.0f} km")
            if "moving_min" in df.columns:
                out.append(f"Total moving time: {df[\'moving_min\'].sum()/60:,.0f} hours")
            if "elev_gain_m" in df.columns:
                out.append(f"Total elevation: {df[\'elev_gain_m\'].sum():,.0f} m")
            if "calories" in df.columns:
                out.append(f"Total calories: {df[\'calories\'].sum():,.0f} kcal")
            out.append("\\nActivities per year:")
            for yr, cnt in df.groupby("year").size().sort_index().items():
                out.append(f"  {yr}: {cnt}")
            out.append("\\nMost recent 10 activities:")
            for _, row in df.sort_values("date", ascending=False).head(10).iterrows():
                d = f" · {row[\'dist_km\']:.1f} km" if "dist_km" in df.columns and pd.notna(row.get("dist_km")) else ""
                out.append(f"  {row[\'date\'].strftime(\'%Y-%m-%d\')} · {row[\'sport\']}{d} · {row[\'name\']}")
            if "avg_hr" in df.columns:
                hr = df[df["avg_hr"].notna()]
                if not hr.empty:
                    out.append(f"\\nAvg HR ({len(hr):,} activities): {hr[\'avg_hr\'].mean():.0f} bpm")
            if "avg_watts" in df.columns:
                pw = df[(df["avg_watts"].notna()) & (df["avg_watts"] > 0)]
                if not pw.empty:
                    out.append(f"Cycling with power: {len(pw):,} sessions · avg {pw[\'avg_watts\'].mean():.0f} W")
            return "\\n".join(out)

        _data_summary = _build_data_summary(df)
        _SYSTEM = f"""You are a personal sports analyst with access to the user\'s complete Strava training history.

Training data:
{_data_summary}

Be specific with numbers, concise (2-4 paragraphs), coaching tone. User trains cycling (road/gravel), running, gym. Based in Finland. Say clearly if something isn\'t in the data."""

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        st.markdown(f\'\'\'<div style="margin-bottom:1.2rem">
            <h2 style="margin:0 0 0.2rem;font-size:1.35rem">Ask your training data</h2>
            <p style="margin:0;color:#888;font-size:0.83rem">Claude · {len(df):,} activities · {df[\'date\'].min().year}–{df[\'date\'].max().year}</p>
        </div>\'\'\', unsafe_allow_html=True)

        _chips = ["What\'s my busiest training month?","How has yearly volume changed?",
                  "Winter vs summer sport split?","Am I overtraining right now?",
                  "What are my longest ever rides?","How many hours last year?"]
        _cc = st.columns(3)
        for _i, _s in enumerate(_chips):
            with _cc[_i % 3]:
                if st.button(_s, key=f"chip_{_i}", use_container_width=True):
                    st.session_state._pending_q = _s

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        _q = st.session_state.pop("_pending_q", None) or st.chat_input("Ask anything about your training…")

        if _q:
            st.session_state.chat_history.append({"role": "user", "content": _q})
            with st.chat_message("user"):
                st.markdown(_q)
            with st.chat_message("assistant"):
                with st.spinner("Analysing…"):
                    try:
                        import anthropic as _ac
                        _r = _ac.Anthropic(api_key=_api_key_chat).messages.create(
                            model="claude-sonnet-4-6",
                            max_tokens=1024,
                            system=_SYSTEM,
                            messages=[{"role": m["role"], "content": m["content"]}
                                      for m in st.session_state.chat_history],
                        )
                        _reply = _r.content[0].text
                    except Exception as _e:
                        _reply = f"Error: {_e}"
                st.markdown(_reply)
                st.session_state.chat_history.append({"role": "assistant", "content": _reply})

        if st.session_state.chat_history:
            if st.button("🗑 Clear", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()

'''

i = code.index(FOOTER)
code = code[:i].rstrip() + '\n\n' + TAB5 + '\n' + FOOTER + code[i + len(FOOTER):]

with open(PATH, "w", encoding="utf-8") as fh:
    fh.write(code)

py_compile.compile(PATH, doraise=True)
print("✅ Fix 3: tab5 chat block inserted correctly before footer")
print("✅ Python syntax valid — ready to deploy")
