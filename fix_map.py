"""
fix_map.py — patches two bugs in the Activity World Map section of app.py:

  1. Invisible countries — color scale was too dark/muddy; replaced with
     high-contrast orange gradient that pops against the neutral land color.

  2. Tooltip only worked on hover — added a click handler that pins/unpins
     the tooltip so it stays visible after clicking a country.
"""

import sys

PATH = "app.py"

with open(PATH, "r", encoding="utf-8") as f:
    code = f.read()

# ── Fix 1: color scale ────────────────────────────────────────────────────────
OLD_CLR = """\
function clr(name) {
  const d = DATA[name];
  if (!d) return null;
  if (name === "Finland") return "#fc4c02";
  const n = d.count;
  if (n >= 100) return "#ff5a28";
  if (n >= 20)  return "#d86830";
  if (n >= 5)   return "#a85830";
  return "#784838";
}"""

NEW_CLR = """\
function clr(name) {
  const d = DATA[name];
  if (!d) return null;
  if (name === "Finland") return "#fc4c02";
  const n = d.count;
  if (n >= 100) return "#ff6a1a";
  if (n >= 20)  return "#ff8c42";
  if (n >= 5)   return "#ffb07a";
  return "#ffd4b0";
}"""

if OLD_CLR not in code:
    print("ERROR: could not find map color function")
    sys.exit(1)

code = code.replace(OLD_CLR, NEW_CLR, 1)
print("✅ Fix 1 applied: color scale updated")

# ── Fix 2: click-to-pin tooltip ───────────────────────────────────────────────
OLD_HANDLERS = """\
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
      .on("mouseleave", () => { tt.style.opacity = "0"; });"""

NEW_HANDLERS = """\
      .on("mousemove", function(event, d) {
        if (tt._pinned) return;
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
      .on("mouseleave", () => { if (!tt._pinned) tt.style.opacity = "0"; })
      .on("click", function(event, d) {
        const nm = NM[+d.id];
        const cd = DATA[nm];
        if (!cd) { tt._pinned = false; tt.style.opacity = "0"; return; }
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
        tt._pinned = true;
        event.stopPropagation();
      });
    // Click anywhere else unpins the tooltip
    document.addEventListener("click", () => {
      tt._pinned = false;
      tt.style.opacity = "0";
    });"""

if OLD_HANDLERS not in code:
    print("ERROR: could not find map section start")
    sys.exit(1)

code = code.replace(OLD_HANDLERS, NEW_HANDLERS, 1)
print("✅ Fix 2 applied: click-to-pin tooltip added")

# ── Write back ────────────────────────────────────────────────────────────────
with open(PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("✅ app.py updated successfully")
