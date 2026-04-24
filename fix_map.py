"""
fix_map.py — replaces the broken D3 world map with a Folium/Leaflet map.

Uses folium.Choropleth with the built-in GeoJSON world dataset so every
visited country gets a clean orange fill on real OpenStreetMap tiles.
Tooltip and click popup show country name + activity count natively.
"""

import sys
PATH = "app.py"

with open(PATH, "r", encoding="utf-8") as fh:
    code = fh.read()

START_MARKER = '    # ── Activity World Map'
END_MARKER   = 'st.info("No GPS polyline data found. Run the Strava sync to populate polylines.json.")\n'

if START_MARKER not in code:
    print("ERROR: could not find world map section start")
    sys.exit(1)
if END_MARKER not in code:
    print("ERROR: could not find world map section end")
    sys.exit(1)

i_start = code.find(START_MARKER)
i_end   = code.find(END_MARKER) + len(END_MARKER)

NEW_SECTION = '''\
    # ── Activity World Map ────────────────────────────────────────────────────────
    st.markdown("## Where I've Trained")

    # Compact bounding-box country lookup
    _COUNTRY_BOXES = {
        "Finland":         [(59.5,70.1,19.0,31.6)],
        "Iceland":         [(63.4,66.6,-24.5,-13.5)],
        "Norway":          [(57.9,71.2,4.5,14.9)],
        "Denmark":         [(54.5,57.8,8.0,12.7)],
        "Sweden":          [(55.3,69.1,11.0,24.2)],
        "Estonia":         [(57.5,59.7,21.8,28.2)],
        "Ireland":         [(51.4,55.4,-10.5,-5.9)],
        "United Kingdom":  [(49.9,60.9,-5.7,1.8)],
        "Portugal":        [(36.8,42.2,-9.5,-6.1)],
        "Morocco":         [(27.7,35.9,-13.2,-1.0)],
        "Spain":           [(35.9,43.8,-9.4,4.3)],
        "Belgium":         [(49.5,51.5,2.5,6.4)],
        "Netherlands":     [(50.7,53.6,3.3,7.2)],
        "Switzerland":     [(45.8,47.8,5.9,10.5)],
        "France":          [(41.3,51.1,-5.1,9.6)],
        "Czech Republic":  [(48.5,51.1,12.1,18.9)],
        "Germany":         [(47.3,55.1,5.9,15.0)],
        "Austria":         [(46.4,49.0,9.5,17.2)],
        "Poland":          [(49.0,54.9,14.1,24.2)],
        "Hungary":         [(45.7,48.6,16.1,22.9)],
        "Italy":           [(36.5,47.1,6.6,18.5)],
        "Greece":          [(34.8,41.8,19.4,28.3)],
        "Turkey":          [(35.8,42.1,25.7,44.8)],
        "Canada":          [(43.2,47.0,-80.0,-70.0),(43.0,47.5,-67.0,-52.6),
                            (47.0,83.1,-95.0,-52.6),(48.9,83.1,-141.0,-95.0)],
        "United States":   [(24.4,48.9,-125.0,-66.9),(51.0,71.5,-168.0,-141.0)],
        "Mexico":          [(14.5,32.7,-117.1,-86.7)],
        "Colombia":        [(-4.2,12.5,-79.0,-66.9)],
        "Brazil":          [(-33.8,5.3,-73.9,-34.8)],
        "Argentina":       [(-55.1,-21.8,-73.6,-53.6)],
        "UAE":             [(22.6,26.1,51.5,56.4)],
        "Qatar":           [(24.5,26.2,50.7,51.7)],
        "Oman":            [(16.6,26.4,52.0,59.9)],
        "Saudi Arabia":    [(16.4,32.2,34.6,55.7)],
        "Singapore":       [(1.1,1.5,103.6,104.0)],
        "Cambodia":        [(10.4,14.7,102.3,106.5)],
        "Vietnam":         [(8.4,23.4,102.1,109.5)],
        "Thailand":        [(5.5,20.5,97.5,105.6)],
        "Malaysia":        [(0.8,7.4,99.6,119.3)],
        "Indonesia":       [(-11.0,6.0,95.0,141.0)],
        "Myanmar":         [(9.5,28.5,92.2,101.2)],
        "Sri Lanka":       [(5.9,9.8,79.6,81.9)],
        "India":           [(8.0,37.1,68.1,97.5)],
        "Japan":           [(24.0,45.5,122.9,145.8)],
        "China":           [(18.0,53.5,97.6,135.1)],
        "Rwanda":          [(-2.9,-1.0,28.8,30.9)],
        "Kenya":           [(-4.7,5.0,33.9,41.9)],
        "Tanzania":        [(-11.7,-0.9,29.4,40.4)],
        "South Africa":    [(-34.8,-22.1,16.5,32.9)],
        "Mauritius":       [(-20.5,-19.9,57.3,57.8)],
        "Australia":       [(-43.6,-10.4,113.2,153.6)],
        "New Zealand":     [(-47.3,-34.4,166.5,178.6)],
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
        _cm4.metric("Years active", f"{df[\'date\'].dt.year.min()}\\u2013{df[\'date\'].dt.year.max()}")

        # ── Folium world map ──────────────────────────────────────────────────
        try:
            import folium
            import json as _json
            from streamlit_folium import st_folium

            # Fetch world GeoJSON (country polygons with "name" property)
            _GEO_URL = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
            @st.cache_data(ttl=86400, show_spinner=False)
            def _load_geojson(url):
                import requests as _req
                r = _req.get(url, timeout=15)
                if r.status_code == 200:
                    return r.json()
                return None

            _geo = _load_geojson(_GEO_URL)

            if _geo:
                # Build a name→count dict for choropleth
                _counts = {k: v["count"] for k, v in _country_map.items()}

                # Add count property to each GeoJSON feature for tooltip
                _name_key = "ADMIN"   # property name in this GeoJSON
                for _feat in _geo["features"]:
                    _n = _feat["properties"].get(_name_key, "")
                    _feat["properties"]["activity_count"] = _counts.get(_n, 0)

                # Create folium map — no tiles initially, we pick a clean style
                _fmap = folium.Map(
                    location=[20, 10],
                    zoom_start=2,
                    tiles="CartoDB positron",
                    width="100%",
                )

                # Choropleth layer — visited countries in orange gradient
                folium.Choropleth(
                    geo_data=_geo,
                    data=_counts,
                    columns=None,          # we pass a dict directly
                    key_on=f"feature.properties.{_name_key}",
                    fill_color="YlOrRd",
                    fill_opacity=0.75,
                    line_opacity=0.4,
                    nan_fill_color="#e8edf2",
                    nan_fill_opacity=0.4,
                    legend_name="GPS Activities",
                    highlight=True,
                    name="Activities",
                ).add_to(_fmap)

                # Transparent overlay for hover tooltip
                folium.GeoJson(
                    _geo,
                    style_function=lambda f: {
                        "fillColor": "transparent",
                        "color": "transparent",
                        "weight": 0,
                    },
                    highlight_function=lambda f: {
                        "fillColor": "#fc4c02",
                        "color": "#fc4c02",
                        "weight": 2,
                        "fillOpacity": 0.3,
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=[_name_key, "activity_count"],
                        aliases=["Country", "GPS Activities"],
                        style=(
                            "background-color: white; color: #111; "
                            "font-family: Inter, sans-serif; "
                            "font-size: 13px; padding: 8px 12px; "
                            "border-radius: 8px; border: 1px solid #ddd;"
                        ),
                        sticky=True,
                    ),
                    popup=folium.GeoJsonPopup(
                        fields=[_name_key, "activity_count"],
                        aliases=["Country", "GPS Activities"],
                    ),
                ).add_to(_fmap)

                # Finland home-base marker
                folium.CircleMarker(
                    location=[62.0, 25.0],
                    radius=7,
                    color="#fc4c02",
                    fill=True,
                    fill_color="#fc4c02",
                    fill_opacity=1.0,
                    tooltip="🏠 Home base — Finland",
                ).add_to(_fmap)

                st_folium(_fmap, use_container_width=True, height=480,
                          returned_objects=[], key="world_map")
            else:
                st.warning("Could not load world map GeoJSON. Check internet connectivity.")

        except ImportError:
            st.info("Add `folium` and `streamlit-folium` to requirements.txt to see the world map.")

        # Country breakdown table
        with st.expander("📍 All countries", expanded=False):
            _sorted_countries = sorted(_country_map.items(), key=lambda x: -x[1]["count"])
            _col_a, _col_b = st.columns(2)
            mid = len(_sorted_countries) // 2
            for _col, _items in [(_col_a, _sorted_countries[:mid]), (_col_b, _sorted_countries[mid:])]:
                with _col:
                    for _name, _cdata in _items:
                        st.markdown(
                            f\'<div style="display:flex;justify-content:space-between;\'
                            f\'padding:5px 0;border-bottom:1px solid {_card_border};">\'
                            f\'<span style="color:{_card_text};font-size:0.82rem">{_name}</span>\'
                            f\'<span style="color:#fc4c02;font-size:0.82rem;font-family:DM Mono,monospace;font-weight:600">{_cdata["count"]:,}</span>\'
                            f\'</div>\',
                            unsafe_allow_html=True
                        )
    else:
        st.info("No GPS polyline data found. Run the Strava sync to populate polylines.json.")
'''

code = code[:i_start] + NEW_SECTION + code[i_end:]

with open(PATH, "w", encoding="utf-8") as fh:
    fh.write(code)

print("✅ World map replaced with Folium/Leaflet choropleth")
print("✅ Hover tooltip and click popup included")
print("✅ Finland home-base marker included")
