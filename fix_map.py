"""
fix_map.py — fixes country name mismatches between our bounding-box lookup
and the GeoJSON ADMIN field names, and fixes bbox errors (Uganda was
catching coordinates meant for other countries).

Two changes:
1. _COUNTRY_BOXES keys renamed to match GeoJSON ADMIN names exactly
2. JS DATA dict built with the same corrected names
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

    # Keys must match GeoJSON ADMIN field exactly (Natural Earth names)
    _COUNTRY_BOXES = {
        "Finland":                    [(59.5, 70.1, 19.0, 31.6)],
        "Iceland":                    [(63.4, 66.6, -24.5, -13.5)],
        "Norway":                     [(57.9, 71.2, 4.5, 31.0)],
        "Denmark":                    [(54.5, 57.8, 8.0, 12.7)],
        "Sweden":                     [(55.3, 69.1, 11.0, 24.2)],
        "Estonia":                    [(57.5, 59.7, 21.8, 28.2)],
        "Ireland":                    [(51.4, 55.4, -10.5, -5.9)],
        "United Kingdom":             [(49.9, 60.9, -8.0, 2.0)],
        "Portugal":                   [(36.8, 42.2, -9.5, -6.1)],
        "Morocco":                    [(27.7, 35.9, -13.2, -1.0)],
        "Spain":                      [(35.9, 43.8, -9.4, 4.3)],
        "Belgium":                    [(49.5, 51.5, 2.5, 6.4)],
        "Netherlands":                [(50.7, 53.6, 3.3, 7.2)],
        "Switzerland":                [(45.8, 47.8, 5.9, 10.5)],
        "France":                     [(41.3, 51.1, -5.1, 9.6)],
        "Czechia":                    [(48.5, 51.1, 12.1, 18.9)],
        "Germany":                    [(47.3, 55.1, 5.9, 15.0)],
        "Austria":                    [(46.4, 49.0, 9.5, 17.2)],
        "Poland":                     [(49.0, 54.9, 14.1, 24.2)],
        "Hungary":                    [(45.7, 48.6, 16.1, 22.9)],
        "Italy":                      [(36.5, 47.1, 6.6, 18.5)],
        "Greece":                     [(34.8, 41.8, 19.4, 29.7)],
        "Turkey":                     [(35.8, 42.1, 25.7, 44.8)],
        "Canada":                     [(42.0, 83.1, -141.0, -52.6)],
        "United States of America":   [(24.4, 49.4, -125.0, -66.9),
                                       (51.0, 71.5, -168.0, -141.0)],
        "Mexico":                     [(14.5, 32.7, -117.1, -86.7)],
        "Colombia":                   [(-4.2, 12.5, -79.0, -66.9)],
        "Brazil":                     [(-33.8, 5.3, -73.9, -34.8)],
        "Argentina":                  [(-55.1, -21.8, -73.6, -53.6)],
        "United Arab Emirates":       [(22.6, 26.1, 51.5, 56.4)],
        "Qatar":                      [(24.5, 26.2, 50.7, 51.7)],
        "Oman":                       [(16.6, 26.4, 52.0, 59.9)],
        "Saudi Arabia":               [(16.4, 32.2, 34.6, 55.7)],
        "Singapore":                  [(1.1, 1.5, 103.6, 104.0)],
        "Cambodia":                   [(10.4, 14.7, 102.3, 107.6)],
        "Vietnam":                    [(8.4, 23.4, 102.1, 109.5)],
        "Thailand":                   [(5.5, 20.5, 97.5, 105.6)],
        "Malaysia":                   [(0.8, 7.4, 99.6, 119.3)],
        "Indonesia":                  [(-11.0, 6.0, 95.0, 141.0)],
        "Myanmar":                    [(9.5, 28.5, 92.2, 101.2)],
        "Sri Lanka":                  [(5.9, 9.8, 79.6, 81.9)],
        "India":                      [(6.0, 37.1, 68.1, 97.5)],
        "Japan":                      [(24.0, 45.5, 122.9, 145.8)],
        "China":                      [(18.0, 53.5, 73.5, 135.1)],
        "Rwanda":                     [(-2.9, -1.0, 28.8, 30.9)],
        "Kenya":                      [(-4.7, 5.0, 33.9, 41.9)],
        "Tanzania":                   [(-11.7, -0.9, 29.4, 40.4)],
        "South Africa":               [(-34.8, -22.1, 16.5, 32.9)],
        "Mauritius":                  [(-20.5, -19.9, 57.3, 57.8)],
        "Australia":                  [(-43.6, -10.4, 113.2, 153.6)],
        "New Zealand":                [(-47.3, -34.4, 166.5, 178.6)],
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

        def _count_to_color(n):
            if n >= 500: return "#b03020"
            if n >= 100: return "#d94f30"
            if n >= 20:  return "#f07030"
            if n >= 5:   return "#f5a050"
            return "#fad090"

        _js_data = {
            name: {"count": d["count"], "color": _count_to_color(d["count"])}
            for name, d in _country_map.items()
        }
        _js_data_json = _json.dumps(_js_data)

        _map_html = """<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html,body,#map{margin:0;padding:0;width:100%;height:500px;font-family:Inter,sans-serif}
  .leaflet-container{background:#cdd9e0}
  .info-box{
    background:white;padding:10px 14px;border-radius:10px;
    border:1px solid #ddd;box-shadow:0 4px 16px rgba(0,0,0,0.15);
    font-size:13px;min-width:160px;pointer-events:none;
  }
  .info-box b{font-size:14px;display:block;margin-bottom:3px;color:#111}
  .info-box .cnt{color:#fc4c02;font-weight:700;font-size:16px;font-family:monospace}
  .info-box .lbl{color:#888;font-size:11px}
</style>
</head><body>
<div id="map"></div>
<script>
const DATA = """ + _js_data_json + """;

const map = L.map('map',{center:[25,10],zoom:2,minZoom:1,maxZoom:7,zoomSnap:0.5});

L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png',{
  attribution:'&copy; OpenStreetMap contributors &copy; CARTO',
  subdomains:'abcd', maxZoom:20
}).addTo(map);

const info = L.control({position:'topright'});
info.onAdd = function(){
  this._div = L.DomUtil.create('div','info-box');
  this._div.innerHTML = '<b style="color:#888;font-size:12px">Hover a country</b>';
  return this._div;
};
info.addTo(map);

function setInfo(nm, d){
  if(d){
    info._div.innerHTML =
      '<b>'+nm+'</b>' +
      '<div class="cnt">'+d.count.toLocaleString()+'</div>' +
      '<div class="lbl">GPS activities</div>';
  } else {
    info._div.innerHTML = '<b>'+nm+'</b><div class="lbl" style="margin-top:3px">No activities recorded</div>';
  }
}

let gl;
function hl(e){
  e.target.setStyle({weight:2,color:'#fc4c02',fillOpacity:0.95});
  e.target.bringToFront();
  const nm = e.target.feature.properties.ADMIN||'';
  setInfo(nm, DATA[nm]);
}
function reset(e){ gl.resetStyle(e.target); info._div.innerHTML='<b style="color:#888;font-size:12px">Hover a country</b>'; }
function styleFn(f){
  const nm = f.properties.ADMIN||'';
  const d  = DATA[nm];
  if(!d) return {fillColor:'#dce8f0',color:'#aabbc8',weight:0.5,fillOpacity:0.4};
  return {fillColor:d.color,color:'#888',weight:0.5,fillOpacity:0.82};
}

fetch('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
  .then(r=>r.json())
  .then(topo=>{
    // Convert TopoJSON → GeoJSON inline via a minimal decoder
    // Use a different source that returns GeoJSON directly
    return fetch('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson');
  })
  .then(r=>r.json())
  .then(gj=>{
    gl = L.geoJson(gj,{
      style:styleFn,
      onEachFeature:function(f,l){
        l.on({mouseover:hl, mouseout:reset, click:hl});
      }
    }).addTo(map);

    // Finland home marker
    const icon = L.divIcon({
      html:'<div style="width:14px;height:14px;border-radius:50%;background:#fc4c02;border:2.5px solid white;box-shadow:0 0 0 4px rgba(252,76,2,0.25)"></div>',
      className:'',iconSize:[14,14],iconAnchor:[7,7]
    });
    L.marker([62.0,25.0],{icon})
      .bindTooltip('🏠 Home — Finland',{direction:'right'})
      .addTo(map);
  })
  .catch(e=>{ document.getElementById('map').innerHTML='<div style="padding:20px;color:#c00">Map failed to load: '+e+'</div>'; });
</script></body></html>"""

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

print("✅ Country names corrected to match Natural Earth / GeoJSON ADMIN field")
print("   Key fixes:")
print("   'United States' → 'United States of America'")
print("   'UAE'           → 'United Arab Emirates'")
print("   'Czech Republic'→ 'Czechia'")
print("   Canada bbox expanded to single full bbox")
print("   GeoJSON source switched to Natural Earth (same ADMIN names)")
