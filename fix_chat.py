"""
fix_chat.py — adds a "💬 Ask" chat tab to the Strava dashboard.
Run against the ORIGINAL app.py (before any previous fix_chat attempts).
"""
import sys
PATH = "app.py"

with open(PATH, "r", encoding="utf-8") as fh:
    code = fh.read()

# ── 1. Add tab5 to the tabs line ─────────────────────────────────────────────
OLD_TABS = 'tab1, tab2, tab3, tab4 = st.tabs(["📊  Overview", "🏃  Training", "💪  Strength", "📋  History"])'
NEW_TABS = 'tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊  Overview", "🏃  Training", "💪  Strength", "📋  History", "💬  Ask"])'

if OLD_TABS not in code:
    print("ERROR: could not find tabs line")
    sys.exit(1)

code = code.replace(OLD_TABS, NEW_TABS, 1)
print("✅ tab5 added to tabs line")

# ── 2. Find footer and insert tab5 block BEFORE it ───────────────────────────
FOOTER = '    st.markdown("""\n    <div style="margin-top:3rem;padding-top:1rem;border-top:1px solid #e2ddd8;\n                color:#444;font-size:0.75rem;text-align:center">\n      Built on Strava · Oura · Fitbod data · Powered by Streamlit\n    </div>\n    """, unsafe_allow_html=True)'

if FOOTER not in code:
    print("ERROR: could not find footer block")
    sys.exit(1)

TAB5_BLOCK = '''with tab5:
    # ── AI Chat — Ask your data ───────────────────────────────────────────────
    _api_key_chat = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""

    if not _api_key_chat:
        st.warning("Add ANTHROPIC_API_KEY to your Streamlit secrets to enable the chat.")
    else:
        import json as _chat_json

        def _build_data_summary(df):
            if df is None or df.empty:
                return "No activity data available."
            lines = []
            lines.append(f"Total activities: {len(df):,}")
            lines.append(f"Date range: {df[\'date\'].min().strftime(\'%Y-%m-%d\')} to {df[\'date\'].max().strftime(\'%Y-%m-%d\')}")
            sport_counts = df["sport"].value_counts().head(10)
            lines.append("\\nActivities by sport:")
            for sport, cnt in sport_counts.items():
                lines.append(f"  {sport}: {cnt:,}")
            if "dist_km" in df.columns:
                lines.append(f"\\nTotal distance: {df[\'dist_km\'].sum():,.0f} km")
                for s, km in df.groupby("sport")["dist_km"].sum().sort_values(ascending=False).head(5).items():
                    lines.append(f"  {s}: {km:,.0f} km")
            if "moving_min" in df.columns:
                lines.append(f"Total moving time: {df[\'moving_min\'].sum()/60:,.0f} hours")
            if "elev_gain_m" in df.columns:
                lines.append(f"Total elevation gain: {df[\'elev_gain_m\'].sum():,.0f} m")
            if "calories" in df.columns:
                lines.append(f"Total calories: {df[\'calories\'].sum():,.0f} kcal")
            lines.append("\\nActivities per year:")
            for yr, cnt in df.groupby("year").size().sort_index().items():
                lines.append(f"  {yr}: {cnt}")
            recent = df.sort_values("date", ascending=False).head(10)
            lines.append("\\nMost recent 10 activities:")
            for _, row in recent.iterrows():
                dist_str = f" · {row[\'dist_km\']:.1f} km" if "dist_km" in df.columns and pd.notna(row.get("dist_km")) else ""
                lines.append(f"  {row[\'date\'].strftime(\'%Y-%m-%d\')} · {row[\'sport\']}{dist_str} · {row[\'name\']}")
            if "avg_hr" in df.columns:
                hr = df[df["avg_hr"].notna()]
                if not hr.empty:
                    lines.append(f"\\nAvg HR ({len(hr):,} activities with data): {hr[\'avg_hr\'].mean():.0f} bpm")
            if "avg_watts" in df.columns:
                pw = df[(df["avg_watts"].notna()) & (df["avg_watts"] > 0)]
                if not pw.empty:
                    lines.append(f"Cycling with power: {len(pw):,} activities · avg {pw[\'avg_watts\'].mean():.0f} W")
            return "\\n".join(lines)

        _data_summary = _build_data_summary(df)

        _SYSTEM_PROMPT = f"""You are a personal sports and fitness analyst with access to the user\'s complete Strava training history. Provide insightful, data-driven analysis and coaching advice.

Training data summary:
{_data_summary}

Guidelines:
- Be specific — reference actual numbers from the data
- Provide actionable coaching recommendations where relevant  
- Keep answers concise (2-4 paragraphs unless asked for detail)
- Friendly, coach-like tone
- User trains cycling (road/gravel), running, and gym work; based in Finland
- If something isn\'t in the data, say so clearly
"""

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        st.markdown(
            f\'\'\'<div style="margin-bottom:1.5rem">
            <h2 style="margin:0 0 0.25rem;font-size:1.4rem">Ask your training data</h2>
            <p style="margin:0;color:#888;font-size:0.85rem">
              Claude · {len(df):,} activities · {df[\'date\'].min().year}–{df[\'date\'].max().year}
            </p></div>\'\'\',
            unsafe_allow_html=True
        )

        _suggestions = [
            "What\'s my busiest training month ever?",
            "How has my weekly volume changed year over year?",
            "What sport do I train most in winter vs summer?",
            "Am I overtraining right now?",
            "What are my longest ever rides?",
            "How many hours did I train last year?",
        ]
        _chip_cols = st.columns(3)
        for _i, _sug in enumerate(_suggestions):
            with _chip_cols[_i % 3]:
                if st.button(_sug, key=f"chip_{_i}", use_container_width=True):
                    st.session_state._pending_question = _sug

        st.markdown("<div style=\'margin-top:0.5rem\'></div>", unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        _pre = st.session_state.pop("_pending_question", None)
        _user_input = st.chat_input("Ask anything about your training…")
        _question = _pre or _user_input

        if _question:
            st.session_state.chat_history.append({"role": "user", "content": _question})
            with st.chat_message("user"):
                st.markdown(_question)
            with st.chat_message("assistant"):
                with st.spinner("Analysing…"):
                    try:
                        import anthropic as _anthropic
                        _client = _anthropic.Anthropic(api_key=_api_key_chat)
                        _messages = [{"role": m["role"], "content": m["content"]}
                                     for m in st.session_state.chat_history]
                        _response = _client.messages.create(
                            model="claude-sonnet-4-6",
                            max_tokens=1024,
                            system=_SYSTEM_PROMPT,
                            messages=_messages,
                        )
                        _reply = _response.content[0].text
                    except Exception as _e:
                        _reply = f"Sorry, couldn\'t reach Claude: {_e}"
                st.markdown(_reply)
                st.session_state.chat_history.append({"role": "assistant", "content": _reply})

        if st.session_state.chat_history:
            if st.button("🗑 Clear conversation", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()

'''

i_footer = code.index(FOOTER)
code = code[:i_footer].rstrip() + '\n\n' + TAB5_BLOCK + '\n' + FOOTER + code[i_footer + len(FOOTER):]

with open(PATH, "w", encoding="utf-8") as fh:
    fh.write(code)

import py_compile
py_compile.compile(PATH, doraise=True)
print("✅ tab5 block inserted before footer")
print("✅ Python syntax valid")
