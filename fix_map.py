"""
fix_map.py — fixes the Activity World Map in app.py

Root cause: the CFG color block used broken triple-quote string concatenation
  bg:    """" + _bg + """",
which Python parses as ending the string literal immediately — so _bg, _ocean,
_land etc. are NEVER interpolated. The JS receives empty strings for all colors,
rendering the map completely white.

Fix: replace the entire _map_html assignment with a version that uses
.format() to inject all Python color variables safely, and also adds
click-to-pin tooltip behaviour.
"""

import sys

PATH = "app.py"

with open(PATH, "r", encoding="utf-8") as fh:
    code = fh.read()

START = '        _map_html = """<!DOCTYPE html>'
END   = '</script></body></html>"""\n        st.components.v1.html(_map_html, height=500, scrolling=False)'

if START not in code:
    print("ERROR: could not find map section start")
    sys.exit(1)
if END not in code:
    print("ERROR: could not find map section end")
    sys.exit(1)

i_start = code.index(START)
i_end   = code.index(END) + len(END)

NEW_BLOCK = r'''        _map_html = (
            """<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:100%;overflow:hidden;font-family:-apple-system,sans-serif}
#wrap{position:relative;width:100%}
svg{display:block;width:100%;height:auto}
#tt{position:absolute;pointer-events:none;opacity:0;transition:opacity 0.15s;
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

const CFG = {
  bg:    "BG_PH",
  ocean: "OCEAN_PH",
  land:  "LAND_PH",
  bdr:   "BDR_PH",
  grid:  "GRID_PH",
  tbg:   "TBG_PH",
  tbrd:  "TBRD_PH",
  tc:    "TC_PH",
  ts:    "TS_PH",
  ds:    "DS_PH"
};

document.getElementById("body").style.background = CFG.bg;
const tt = document.getElementById("tt");
tt._pinned = false;
tt.style.background = CFG.tbg;
tt.style.border = "1px solid " + CFG.tbrd;
document.querySelector(".tt-n").style.color = CFG.tc;
document.querySelector(".tt-c").style.color = CFG.ts;

function showTip(nm, cd, ex, ey) {
  document.getElementById("tt-n").textContent = nm;
  document.getElementById("tt-c").textContent = cd.count.toLocaleString() + " GPS activities";
  const rect = document.getElementById("wrap").getBoundingClientRect();
  let x = ex - rect.left + 14;
  let y = ey - rect.top  - 10;
  if (x + 180 > rect.width)  x -= 200;
  if (y + 60  > rect.height) y -= 70;
  tt.style.left    = x + "px";
  tt.style.top     = y + "px";
  tt.style.opacity = "1";
}

function clr(name) {
  const d = DATA[name];
  if (!d) return null;
  if (name === "Finland") return "#fc4c02";
  const n = d.count;
  if (n >= 100) return "#ff6a1a";
  if (n >= 20)  return "#ff8c42";
  if (n >= 5)   return "#ffb07a";
  return "#ffd4b0";
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
        if (tt._pinned) return;
        const nm = NM[+d.id]; const cd = DATA[nm];
        if (!cd) return;
        showTip(nm, cd, event.clientX, event.clientY);
      })
      .on("mouseleave", () => { if (!tt._pinned) tt.style.opacity = "0"; })
      .on("click", function(event, d) {
        event.stopPropagation();
        const nm = NM[+d.id]; const cd = DATA[nm];
        if (!cd) { tt._pinned = false; tt.style.opacity = "0"; return; }
        showTip(nm, cd, event.clientX, event.clientY);
        tt._pinned = true;
      });

    svg.append("path").datum(mesh)
       .attr("fill","none").attr("stroke", CFG.bdr).attr("stroke-width","0.25").attr("d", gp);

    const fin = proj([25.0, 62.0]);
    const g = svg.append("g").attr("transform", `translate(${fin[0]},${fin[1]})`);
    g.append("circle").attr("class","hp").attr("r","4");
    g.append("circle").attr("class","hp hp2").attr("r","4");
    g.append("circle").attr("fill","#fc4c02").attr("stroke", CFG.ds)
     .attr("stroke-width","1.5").attr("r","4");
  });

document.addEventListener("click", () => { tt._pinned = false; tt.style.opacity = "0"; });
</script></body></html>"""
        )
        _map_html = (
            _map_html
            .replace("BG_PH",    _bg)
            .replace("OCEAN_PH", _ocean)
            .replace("LAND_PH",  _land)
            .replace("BDR_PH",   _bdr)
            .replace("GRID_PH",  _grid)
            .replace("TBG_PH",   _tbg)
            .replace("TBRD_PH",  _tbrd)
            .replace("TC_PH",    _tc)
            .replace("TS_PH",    _ts)
            .replace("DS_PH",    _ds)
        )
        st.components.v1.html(_map_html, height=500, scrolling=False)'''

code = code[:i_start] + NEW_BLOCK + code[i_end:]

with open(PATH, "w", encoding="utf-8") as fh:
    fh.write(code)

print("✅ Map HTML block replaced — CFG colors now injected via .replace()")
print("✅ Click-to-pin tooltip included")
