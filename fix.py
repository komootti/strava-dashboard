# Run once: python fix.py
# Then delete this file
import re, sys

try:
    code = open('app.py', encoding='utf-8').read()
except:
    sys.exit("ERROR: app.py not found in current folder")

n = 0

# 1. Effort labels
for old, new in [
    ('"Easy", "#50c850"',     '"Recovery", "#50c850"'),
    ('"Moderate", "#ffa500"', '"Base",     "#ffa500"'),
    ('"Hard", "#ff6b35"',     '"Quality",  "#ff6b35"'),
    ('"Max effort", "#fc4c02"','"Peak",     "#fc4c02"'),
]:
    if old in code: code = code.replace(old, new); n += 1; print(f"✓ {old[:20]}")

# 2. Effort tag colour
old = """'<span style="background:#f0fdf0;border:1px solid #86efac;color:#16a34a;'
                    'font-size:0.7rem;font-weight:600;padding:2px 8px;border-radius:999px">'"""
new = """f'<span style="background:{effort_col}22;border:1px solid {effort_col}55;color:{effort_col};'
                    f'font-size:0.7rem;font-weight:600;padding:2px 8px;border-radius:999px">'"""
if old in code: code = code.replace(old, new); n += 1; print("✓ effort tag colour")

# 3. Effort column in table
marker = '# Build HTML table'
if '_eff_label' not in code and marker in code:
    insert = '''def _eff_label(v):
    if __import__('pandas').isna(v) or v<=0: return "","#aaa"
    elif v<30:  return "Recovery","#50c850"
    elif v<70:  return "Base","#ffa500"
    elif v<120: return "Quality","#ff6b35"
    else:       return "Peak","#fc4c02"
recent_acts["_eff_lbl"]=recent_acts["rel_effort"].apply(lambda v:_eff_label(v)[0])
recent_acts["_eff_col"]=recent_acts["rel_effort"].apply(lambda v:_eff_label(v)[1])

'''
    code = code.replace(marker, insert + marker); n += 1; print("✓ effort column calc")

# 4. Effort header in table
old_h = re.search(r"'<th [^>]*>Elev</th>'", code)
if old_h and 'Effort</th>' not in code:
    effort_h = '<th style="color:#888;font-size:0.68rem;font-weight:600;text-transform:uppercase;padding:10px 8px;text-align:left">Effort</th>\' +\n    \''
    code = code[:old_h.start()] + effort_h + code[old_h.start():]
    n += 1; print("✓ effort table header")

# 5. Effort cell in rows
old_c = re.search(r'\+ f\'<td style="color:\{_card_text\}">\{r\["Elev"\]\}</td>\'', code)
if old_c and '_eff_lbl' not in code[old_c.start()-500:old_c.start()]:
    effort_c = ('+ (f\'<td style="padding:8px"><span style="background:{r[\\"_eff_col\\"]}22;'
                'color:{r[\\"_eff_col\\"]};font-size:0.62rem;font-weight:700;padding:3px 8px;'
                'border-radius:999px">{r[\\"_eff_lbl\\"]}</span></td>\' if r["_eff_lbl"] else \'<td>—</td>\')\n        ')
    code = code[:old_c.start()] + effort_c + code[old_c.start():]
    n += 1; print("✓ effort cell in rows")

if n == 0:
    print("Nothing to patch - may already be applied or patterns not found")
else:
    open('app.py', 'w', encoding='utf-8').write(code)
    print(f"\nDone: {n} changes. app.py saved.")
