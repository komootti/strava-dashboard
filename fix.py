# Run via GitHub Actions - patches app.py
import re, sys

code = open('app.py', encoding='utf-8').read()
original = code
n = 0

# 1. Fix any variation of effort labels
for old, new in [
    ('"Easy"',        '"Recovery"'),
    ('"Moderate"',    '"Base"'),
    ('"Hard"',        '"Quality"'),
    ('"Max effort"',  '"Peak"'),
    ('"Max Effort"',  '"Peak"'),
]:
    if old in code:
        code = code.replace(old, new)
        n += 1
        print(f"✓ replaced {old} with {new}")

# 2. Fix effort tag - hardcoded green → dynamic colour
old2 = "'background:#f0fdf0;border:1px solid #86efac;color:#16a34a;"
new2 = "f'background:{effort_col}22;border:1px solid {effort_col}55;color:{effort_col};"
if old2 in code:
    code = code.replace(old2, new2)
    n += 1
    print("✓ effort tag colour fixed")

# Also fix the next line of the tag (font-size line) to be f-string too
old2b = "    'font-size:0.7rem;font-weight:600;padding:2px 8px;border-radius:999px\">'\n                    + effort_lbl"
new2b = "    f'font-size:0.7rem;font-weight:600;padding:2px 8px;border-radius:999px\">'\n                    + effort_lbl"
if old2b in code:
    code = code.replace(old2b, new2b)
    n += 1
    print("✓ effort tag f-string fixed")

# 3. Add effort column calculation before table build
if '_eff_label' not in code:
    marker = '# Build HTML table'
    if marker in code:
        insert = (
            'def _eff_label(v):\n'
            '    import pandas as _pd\n'
            '    if _pd.isna(v) or v<=0: return "","#aaa"\n'
            '    elif v<30:  return "Recovery","#50c850"\n'
            '    elif v<70:  return "Base","#ffa500"\n'
            '    elif v<120: return "Quality","#ff6b35"\n'
            '    else:       return "Peak","#fc4c02"\n'
            'recent_acts["_eff_lbl"]=recent_acts["rel_effort"].apply(lambda v:_eff_label(v)[0])\n'
            'recent_acts["_eff_col"]=recent_acts["rel_effort"].apply(lambda v:_eff_label(v)[1])\n'
            '\n'
        )
        code = code.replace(marker, insert + marker)
        n += 1
        print("✓ effort column calculation added")

# 4. Add Effort header before Elev in table
if 'Effort</th>' not in code:
    m = re.search(r"'<th [^>]*text-align:right[^>]*>Elev</th>'", code)
    if m:
        effort_th = "'<th style=\"color:#888;font-size:0.68rem;font-weight:600;text-transform:uppercase;padding:10px 8px;text-align:left\">Effort</th>' +\n    "
        code = code[:m.start()] + effort_th + code[m.start():]
        n += 1
        print("✓ Effort column header added")

# 5. Add Effort cell before Elev cell in rows
if '_eff_lbl' not in code:
    m2 = re.search(r'\+ f\'<td style="color:\{_card_text\}">\{r\["Elev"\]\}</td>\'', code)
    if m2:
        effort_cell = (
            '+ (f\'<td style="padding:8px"><span style="background:{r[\\"_eff_col\\"]}22;'
            'color:{r[\\"_eff_col\\"]};font-size:0.62rem;font-weight:700;'
            'padding:3px 8px;border-radius:999px">{r[\\"_eff_lbl\\"]}</span></td>\''
            ' if r["_eff_lbl"] else \'<td>—</td>\')\n        '
        )
        code = code[:m2.start()] + effort_cell + code[m2.start():]
        n += 1
        print("✓ Effort cell added to table rows")

print(f"\nTotal changes: {n}")
if code != original:
    open('app.py', 'w', encoding='utf-8').write(code)
    print("app.py saved successfully")
else:
    print("WARNING: No changes made - patterns may not match")
    # Print context around effort labels to debug
    for i, line in enumerate(code.split('\n')):
        if 'effort_lbl' in line and ('Easy' in line or 'Recovery' in line or 'effort_col' in line):
            print(f"  Line {i+1}: {line[:100]}")
