"""
Run this via GitHub Actions to patch the world map in app.py.
Add as .github/workflows/fix_map.yml and run once.
"""
import re, ast, sys

code = open('app.py', encoding='utf-8').read()
original_len = len(code)

# ── Find the map section boundaries ──────────────────────────────────────────
MAP_START_MARKER = '        # Modern'
MAP_END_MARKER   = '        st.components.v1.html(_map_html,'

start = code.find(MAP_START_MARKER)
if start == -1:
    # Try older marker
    start = code.find('        # Color scale based on count')
if start == -1:
    print("ERROR: could not find map section start")
    sys.exit(1)

end_search = code.find(MAP_END_MARKER, start)
end = code.find('\n', end_search) + 1  # include the line
print(f"Map section found: chars {start}-{end}")

# ── New map code ──────────────────────────────────────────────────────────────
NEW_MAP = '''        # ── World map — modern minimal style ─────────────────────────────────
        _bg   = "#0a0a0a" if _dark else "#f4f4f2"
        _ocean= "#050a14" if _dark else "#c0d8e8"
        _land = "#222226" if _dark else "#d0d0cc"
        _bdr  = "#0a0a0a" if _dark else "#ffffff"
        _grid = "#141418" if _dark else "#dde8f0"
        _tbg  = "rgba(16,16,18,0.97)" if _dark else "rgba(255,255,255,0.97)"
        _tbrd = "#2a2a2a" if _dark else "#e0e0e0"
        _tc   = "#f0f0f0" if _dark else "#111111"
        _ts   = "#888888" if _dark else "#555555"
        _ds   = "#0a0a0a" if _dark else "#f4f4f2"

        _map_html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:100%;overflow:hidden;font-family:-apple-system,sans-serif}
#wrap{position:relative;width:100%}
svg{display:block;width:100%;height:auto}
#tt{position:absolute;pointer-events:none;opacity:0;transition:opacity 0.12s;
    padding:10px 14px;border-radius:10px;min-width:160px;
    box-shadow:0 8px 32px rgba(0,0,0,0.4)}
.tt-n{font-size:13px;font-weight:600;margin-bottom:2px}
.tt-c{font-size:12px}
.hp{fill:none;stroke:#fc4c02;stroke-width:1.5;opacity:0;animation:p 2.8s ease-out infinite}
.hp2{animation-delay:1.2s}
@keyframes p{0%{r:4;opacity:0.8}100%{r:18;opacity:0}}
</style></head>
<body id="body">
<div id="wrap">
  <div id="tt"><div class="tt-n" id="tt-n"></div><div class="tt-c" id="tt-c"></div></div>
</div>
<script>
const DATA=""" + _map_json + """;
const NM={840:"United States",246:"Finland",764:"Thailand",380:"Italy",826:"United Kingdom",
  250:"France",300:"Greece",784:"United Arab Emirates",480:"Mauritius",276:"Germany",
  392:"Japan",702:"Singapore",156:"China",76:"Brazil",104:"Myanmar",682:"Saudi Arabia",
  834:"Tanzania",356:"India",528:"Netherlands",792:"Turkey",170:"Colombia",404:"Kenya",
  124:"Canada",752:"Sweden",578:"Norway",208:"Denmark",233:"Estonia",724:"Spain",
  620:"Portugal",40:"Austria",756:"Switzerland",56:"Belgium",616:"Poland",203:"Czech Republic",
  348:"Hungary",36:"Australia",554:"New Zealand",710:"South Africa",504:"Morocco",
  484:"Mexico",32:"Argentina",352:"Iceland",372:"Ireland",360:"Indonesia",
  458:"Malaysia",704:"Vietnam",116:"Cambodia",144:"Sri Lanka",646:"Rwanda"};

// Apply theme colors from Python
const CFG = {
  bg:    \"""" + _bg    + """\",
  ocean: \"""" + _ocean + """\",
  land:  \"""" + _land  + """\",
  bdr:   \"""" + _bdr   + """\",
  grid:  \"""" + _grid  + """\",
  tbg:   \"""" + _tbg   + """\",
  tbrd:  \"""" + _tbrd  + """\",
  tc:    \"""" + _tc    + """\",
  ts:    \"""" + _ts    + """\",
  ds:    \"""" + _ds    + """\"
};

document.getElementById("body").style.background = CFG.bg;
const tt = document.getElementById("tt");
tt.style.background = CFG.tbg;
tt.style.border = "1px solid " + CFG.tbrd;
document.querySelector(".tt-n").style.color = CFG.tc;
document.querySelector(".tt-c").style.color = CFG.ts;

function clr(name) {
  const d = DATA[name];
  if (!d) return null;
  if (name === "Finland") return "#fc4c02";
  const n = d.count;
  if (n >= 100) return "#ff5a28";
  if (n >= 20)  return "#d86830";
  if (n >= 5)   return "#a85830";
  return "#784838";
}

const W = 960, H = 500;
const svg = d3.select("#wrap").append("svg")
  .attr("viewBox", `0 0 ${W} ${H}`)
  .attr("preserveAspectRatio", "xMidYMid meet");

const proj = d3.geoNaturalEarth1().scale(153).translate([W/2, H/2]);
const gp   = d3.geoPath().projection(proj);

svg.append("path").datum({type:"Sphere"})
   .attr("fill", CFG.ocean).attr("d", gp);
svg.append("path").datum(d3.geoGraticule().step([30,30])())
   .attr("fill","none").attr("stroke", CFG.grid).attr("stroke-width","0.25").attr("d", gp);

fetch("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json")
  .then(r => r.json())
  .then(world => {
    const feats = topojson.feature(world, world.objects.countries).features;
    const mesh  = topojson.mesh(world, world.objects.countries, (a,b) => a !== b);

    svg.append("g").selectAll("path").data(feats).join("path")
      .attr("fill",   d => clr(NM[+d.id]) || CFG.land)
      .attr("stroke", CFG.bdr)
      .attr("stroke-width", "0.4")
      .style("cursor", d => clr(NM[+d.id]) ? "pointer" : "default")
      .on("mousemove", function(event, d) {
        const nm = NM[+d.id];
        const cd = DATA[nm];
        if (!cd) return;
        document.getElementById("tt-n").textContent = nm;
        document.getElementById("tt-c").textContent = cd.count.toLocaleString() + " GPS activities";
        const rect = document.getElementById("wrap").getBoundingClientRect();
        let x = event.clientX - rect.left + 14;
        let y = event.clientY - rect.top  - 10;
        if (x + 180 > rect.width)  x -= 200;
        if (y + 60  > rect.height) y -= 70;
        tt.style.left    = x + "px";
        tt.style.top     = y + "px";
        tt.style.opacity = "1";
      })
      .on("mouseleave", () => { tt.style.opacity = "0"; });

    svg.append("path").datum(mesh)
       .attr("fill","none").attr("stroke", CFG.bdr).attr("stroke-width","0.25").attr("d", gp);

    // Home base pulse — Finland
    const fin = proj([25.0, 62.0]);
    const g = svg.append("g").attr("transform", `translate(${fin[0]},${fin[1]})`);
    g.append("circle").attr("class","hp").attr("r","4");
    g.append("circle").attr("class","hp hp2").attr("r","4");
    g.append("circle").attr("fill","#fc4c02").attr("stroke", CFG.ds)
     .attr("stroke-width","1.5").attr("r","4");
  });
</script></body></html>"""
        st.components.v1.html(_map_html, height=500, scrolling=False)
'''

code = code[:start] + NEW_MAP + code[end:]

try:
    ast.parse(code)
    open('app.py', 'w', encoding='utf-8').write(code)
    print(f"SUCCESS: {len(code)} chars (was {original_len})")
except SyntaxError as e:
    print(f"SYNTAX ERROR line {e.lineno}: {e.msg}")
    lines = code.split('\n')
    for i in range(max(0,e.lineno-3), min(len(lines),e.lineno+3)):
        print(f"  {i+1}: {lines[i][:80]}")
    sys.exit(1)
