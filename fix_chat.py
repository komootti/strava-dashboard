"""
fix_chat.py — robust idempotent version.
Works whether tab5 exists already or not.
Directly rewrites the tab5 block in-place.
"""
import sys, py_compile, re
PATH = "app.py"

with open(PATH, "r", encoding="utf-8") as fh:
    code = fh.read()

# ── Ensure tabs line has tab5 ─────────────────────────────────────────────────
if 'tab1, tab2, tab3, tab4 = st.tabs' in code:
    code = code.replace(
        'tab1, tab2, tab3, tab4 = st.tabs(["📊  Overview", "🏃  Training", "💪  Strength", "📋  History"])',
        'tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊  Overview", "🏃  Training", "💪  Strength", "📋  History", "💬  Ask"])',
        1
    )
    print("✅ tab5 added to tabs line")
elif 'tab1, tab2, tab3, tab4, tab5 = st.tabs' in code:
    print("✅ tabs line already has tab5")
else:
    print("ERROR: could not find tabs line"); sys.exit(1)

# ── Remove any existing tab5 block ────────────────────────────────────────────
if 'with tab5:' in code:
    i = code.index('with tab5:')
    # tab5 runs to end of file (before footer or truly end)
    # Find next 0-indent 'with tab' or end of file
    rest = code[i+10:]
    # Find footer as end marker
    footer_marker = '    st.markdown("""\n    <div style="margin-top:3rem'
    if footer_marker in code:
        i_footer = code.index(footer_marker)
        code = code[:i].rstrip() + '\n\n' + code[i_footer:]
    else:
        code = code[:i].rstrip() + '\n'
    print("✅ old tab5 block removed")

# ── Build tab5 content ────────────────────────────────────────────────────────
# Use regular string concat for _SYSTEM (NOT f-string) to avoid 
# curly-brace conflicts with training data content
TAB5 = '''
with tab5:
    # ── AI Chat ───────────────────────────────────────────────────────────────
    # Always render something so the tab is visible
    st.markdown("## 💬 Ask your training data")
    st.caption("Chat with Claude about your Strava history")

    _api_key_chat = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""

    if not _api_key_chat:
        st.info("🔑 Add **ANTHROPIC_API_KEY** to your Streamlit secrets to enable AI chat.")
    else:
        def _build_summary(df):
            if df is None or df.empty:
                return "No activity data available."
            out = [
                "Total activities: " + str(len(df)),
                "Date range: " + str(df["date"].min().date()) + " to " + str(df["date"].max().date()),
            ]
            out.append("Activities by sport:")
            for sport, cnt in df["sport"].value_counts().head(10).items():
                out.append("  " + str(sport) + ": " + str(cnt))
            if "dist_km" in df.columns:
                out.append("Total distance: " + f"{df['dist_km'].sum():,.0f} km")
            if "moving_min" in df.columns:
                out.append("Total moving time: " + f"{df['moving_min'].sum()/60:,.0f} hours")
            if "elev_gain_m" in df.columns:
                out.append("Total elevation: " + f"{df['elev_gain_m'].sum():,.0f} m")
            out.append("Activities per year:")
            for yr, cnt in df.groupby("year").size().sort_index().items():
                out.append("  " + str(yr) + ": " + str(cnt))
            out.append("Most recent 10 activities:")
            for _, row in df.sort_values("date", ascending=False).head(10).iterrows():
                dist = (" - " + f"{row['dist_km']:.1f} km") if "dist_km" in df.columns and pd.notna(row.get("dist_km")) else ""
                out.append("  " + str(row["date"].date()) + " - " + str(row["sport"]) + dist + " - " + str(row["name"]))
            if "avg_hr" in df.columns:
                hr = df[df["avg_hr"].notna()]
                if not hr.empty:
                    out.append("Avg HR (" + str(len(hr)) + " activities): " + f"{hr['avg_hr'].mean():.0f} bpm")
            if "avg_watts" in df.columns:
                pw = df[(df["avg_watts"].notna()) & (df["avg_watts"] > 0)]
                if not pw.empty:
                    out.append("Cycling with power: " + str(len(pw)) + " sessions, avg " + f"{pw['avg_watts'].mean():.0f} W")
            return "\\n".join(out)

        _summary = _build_summary(df)

        # Use string concatenation — NOT f-string — to avoid { } conflicts
        _SYSTEM = (
            "You are a personal sports analyst with access to the user\'s complete Strava training history.\\n\\n"
            "Training data summary:\\n" + _summary + "\\n\\n"
            "Guidelines: be specific with numbers, keep answers to 2-4 paragraphs, "
            "use a friendly coaching tone. The user trains cycling (road/gravel), running, "
            "and gym work; they are based in Finland. "
            "If something is not in the data, say so clearly."
        )

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Quick-start chips
        _chips = [
            "What is my busiest training month ever?",
            "How has my yearly volume changed over time?",
            "Do I train more in summer or winter?",
            "Am I overtraining right now?",
            "What are my longest ever rides?",
            "How many hours did I train last year?",
        ]
        _cc = st.columns(3)
        for _i, _s in enumerate(_chips):
            with _cc[_i % 3]:
                if st.button(_s, key="chip_" + str(_i), use_container_width=True):
                    st.session_state["_pending_q"] = _s

        st.divider()

        for _msg in st.session_state.chat_history:
            with st.chat_message(_msg["role"]):
                st.markdown(_msg["content"])

        _pending = st.session_state.pop("_pending_q", None)
        _user_q  = st.chat_input("Ask anything about your training...")
        _q = _pending or _user_q

        if _q:
            st.session_state.chat_history.append({"role": "user", "content": _q})
            with st.chat_message("user"):
                st.markdown(_q)
            with st.chat_message("assistant"):
                with st.spinner("Analysing..."):
                    try:
                        import anthropic as _ac
                        _msgs = [{"role": m["role"], "content": m["content"]}
                                 for m in st.session_state.chat_history]
                        _resp = _ac.Anthropic(api_key=_api_key_chat).messages.create(
                            model="claude-sonnet-4-6",
                            max_tokens=1024,
                            system=_SYSTEM,
                            messages=_msgs,
                        )
                        _reply = _resp.content[0].text
                    except Exception as _e:
                        _reply = "Error reaching Claude: " + str(_e)
                st.markdown(_reply)
                st.session_state.chat_history.append({"role": "assistant", "content": _reply})

        if st.session_state.chat_history:
            if st.button("Clear conversation", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()

'''

# ── Insert tab5 before footer, or append if no footer ────────────────────────
footer_marker = '    st.markdown("""\n    <div style="margin-top:3rem'
if footer_marker in code:
    i_footer = code.index(footer_marker)
    code = code[:i_footer].rstrip() + '\n' + TAB5 + '\n' + code[i_footer:]
    print("✅ tab5 inserted before footer")
else:
    code = code.rstrip() + '\n' + TAB5
    print("✅ tab5 appended to end of file")

# ── Validate & write ──────────────────────────────────────────────────────────
with open(PATH, "w", encoding="utf-8") as fh:
    fh.write(code)

py_compile.compile(PATH, doraise=True)

# Verify
assert 'with tab5:' in code
assert 'st.markdown("## 💬 Ask your training data")' in code
print("✅ syntax valid, tab5 present with guaranteed visible content")
print("✅ Done — redeploy the app")
