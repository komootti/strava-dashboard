"""
fix_chat.py — adds a "💬 Ask" chat tab to the Strava dashboard.

The chat uses the existing ANTHROPIC_API_KEY secret and injects a rich
data summary (totals, recent activities, top sports, PRs etc.) as system
context so Claude can answer questions about your training data.
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
print("✅ tab5 added to tabs")

# ── 2. Append tab5 block before the final footer ─────────────────────────────
FOOTER_MARKER = '    """, unsafe_allow_html=True)\n'
# Find the last occurrence (the footer)
i_footer = code.rfind(FOOTER_MARKER)
if i_footer < 0:
    print("ERROR: could not find footer marker")
    sys.exit(1)

TAB5_BLOCK = '''
with tab5:
    # ── AI Chat — Ask your data ───────────────────────────────────────────────
    _api_key_chat = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""

    if not _api_key_chat:
        st.warning("Add ANTHROPIC_API_KEY to your Streamlit secrets to enable the chat.")
    else:
        # Build a rich data summary to inject as system context
        import json as _chat_json

        def _build_data_summary(df):
            if df is None or df.empty:
                return "No activity data available."

            lines = []

            # Totals
            lines.append(f"Total activities: {len(df):,}")
            lines.append(f"Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")

            # By sport
            sport_counts = df['sport'].value_counts().head(10)
            lines.append("\\nActivities by sport type:")
            for sport, cnt in sport_counts.items():
                lines.append(f"  {sport}: {cnt:,}")

            # Distance/duration where available
            if 'dist_km' in df.columns:
                total_km = df['dist_km'].sum()
                lines.append(f"\\nTotal distance (all sports): {total_km:,.0f} km")
                by_sport_km = df.groupby('sport')['dist_km'].sum().sort_values(ascending=False).head(5)
                lines.append("Distance by sport (top 5):")
                for s, km in by_sport_km.items():
                    lines.append(f"  {s}: {km:,.0f} km")

            if 'moving_min' in df.columns:
                total_h = df['moving_min'].sum() / 60
                lines.append(f"\\nTotal moving time: {total_h:,.0f} hours")

            if 'elev_gain_m' in df.columns:
                total_elev = df['elev_gain_m'].sum()
                lines.append(f"Total elevation gain: {total_elev:,.0f} m")

            if 'calories' in df.columns:
                total_cal = df['calories'].sum()
                lines.append(f"Total calories: {total_cal:,.0f} kcal")

            # Yearly breakdown
            yearly = df.groupby('year').size().sort_index()
            lines.append("\\nActivities per year:")
            for yr, cnt in yearly.items():
                lines.append(f"  {yr}: {cnt}")

            # Recent 10 activities
            recent = df.sort_values('date', ascending=False).head(10)
            lines.append("\\nMost recent 10 activities:")
            for _, row in recent.iterrows():
                dist_str = f" · {row['dist_km']:.1f} km" if 'dist_km' in df.columns and pd.notna(row.get('dist_km')) else ""
                lines.append(f"  {row['date'].strftime('%Y-%m-%d')} · {row['sport']}{dist_str} · {row['name']}")

            # Training load if available
            if 'rel_effort' in df.columns:
                recent_effort = df[df['date'] >= df['date'].max() - pd.Timedelta(days=28)]['rel_effort'].sum()
                lines.append(f"\\nRelative effort last 28 days: {recent_effort:.0f}")

            # HR data
            if 'avg_hr' in df.columns:
                hr_acts = df[df['avg_hr'].notna()]
                if not hr_acts.empty:
                    lines.append(f"\\nAverage HR across {len(hr_acts):,} activities with HR data: {hr_acts['avg_hr'].mean():.0f} bpm")

            # Power data
            if 'avg_watts' in df.columns:
                pwr_acts = df[(df['avg_watts'].notna()) & (df['avg_watts'] > 0)]
                if not pwr_acts.empty:
                    lines.append(f"Cycling activities with power: {len(pwr_acts):,}")
                    lines.append(f"Average power: {pwr_acts['avg_watts'].mean():.0f} W")

            # CTL/ATL/TSB if present
            if 'ctl' in df.columns:
                latest_ctl = df.sort_values('date').iloc[-1]
                lines.append(f"\\nLatest fitness (CTL): {latest_ctl.get('ctl', 'n/a'):.1f}")
                lines.append(f"Latest fatigue (ATL): {latest_ctl.get('atl', 'n/a'):.1f}")
                lines.append(f"Latest form (TSB): {latest_ctl.get('tsb', 'n/a'):.1f}")

            return "\\n".join(lines)

        _data_summary = _build_data_summary(df)

        _SYSTEM_PROMPT = f"""You are a personal sports and fitness analyst assistant with access to the user's complete Strava training history. Your role is to provide insightful, data-driven analysis and coaching advice.

Here is the user's training data summary:

{_data_summary}

Guidelines:
- Answer questions about training patterns, performance trends, and fitness metrics
- Be specific — reference actual numbers from the data when relevant
- Provide actionable insights and coaching recommendations where appropriate
- If asked about something not in the data, say so clearly
- Keep answers concise but informative (2-4 paragraphs max unless asked for detail)
- Use a friendly, coach-like tone
- The user trains across cycling (road and gravel), running, and gym work
- They are based in Finland
"""

        # Init chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Layout
        st.markdown(
            f"""<div style="margin-bottom:1.5rem">
            <h2 style="margin:0 0 0.25rem;font-size:1.4rem;color:{_card_text}">Ask your training data</h2>
            <p style="margin:0;color:{_card_sub};font-size:0.85rem">
              Powered by Claude · {len(df):,} activities · {df['date'].min().year}–{df['date'].max().year}
            </p></div>""",
            unsafe_allow_html=True
        )

        # Suggestion chips
        _suggestions = [
            "What's my busiest training month ever?",
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

        st.markdown("<div style='margin-top:0.5rem'></div>", unsafe_allow_html=True)

        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Handle suggestion chip clicks
        _pre = st.session_state.pop("_pending_question", None)

        # Chat input
        _user_input = st.chat_input("Ask anything about your training…")
        _question = _pre or _user_input

        if _question:
            # Show user message
            st.session_state.chat_history.append({"role": "user", "content": _question})
            with st.chat_message("user"):
                st.markdown(_question)

            # Call Claude
            with st.chat_message("assistant"):
                with st.spinner("Analysing…"):
                    try:
                        import anthropic as _anthropic
                        _client = _anthropic.Anthropic(api_key=_api_key_chat)

                        _messages = [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.chat_history
                        ]

                        _response = _client.messages.create(
                            model="claude-opus-4-5",
                            max_tokens=1024,
                            system=_SYSTEM_PROMPT,
                            messages=_messages,
                        )
                        _reply = _response.content[0].text
                    except Exception as _e:
                        _reply = f"Sorry, couldn't reach Claude: {_e}"

                st.markdown(_reply)
                st.session_state.chat_history.append({"role": "assistant", "content": _reply})

        # Clear button
        if st.session_state.chat_history:
            if st.button("🗑 Clear conversation", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()

'''

code = code[:i_footer + len(FOOTER_MARKER)] + TAB5_BLOCK + code[i_footer + len(FOOTER_MARKER):]

with open(PATH, "w", encoding="utf-8") as fh:
    fh.write(code)

print("✅ Chat tab added")
print("✅ Data summary injected as system prompt")
print("✅ Suggestion chips for quick questions")
print("✅ Full conversation history maintained in session_state")
