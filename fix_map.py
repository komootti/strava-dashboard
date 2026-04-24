"""
fix_map.py — replaces the broken polygon-based world map with a 
circle-marker approach. No external GeoJSON needed — just hardcoded
country centroids + Leaflet OSM tiles. Circles are sized and colored
by activity count. Hover tooltip shows country + count.
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

NEW_SECTION = '''    # ── Activity World Map ────────────────────────────────────────────────────────
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
        _cm4.metric("Years active", f"{df[\'date\'].dt.year.min()}\\u2013{df[\'date\'].dt.year.max()}")

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

print("✅ Map rebuilt: circle markers on CartoDB Positron tiles")
print("✅ Zero external GeoJSON dependency")
print("✅ Sizes/colors by activity count, hover tooltip, legend")
print("✅ Country names match bounding-box lookup keys exactly")
