#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply desk/POS feel: CSS addon + sales + dashboard panels; fix literal \\n."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]

# CSS
css_path = root / "frontend/src/styles/home.css"
addon_path = root / "scripts/desk_feel.css.addon"
css = css_path.read_text(encoding="utf-8")
if ".pro-desk" not in css:
    addon = addon_path.read_text(encoding="utf-8")
    css_path.write_text(css.rstrip() + "\n\n" + addon, encoding="utf-8")
    print("CSS: desk styles added")
else:
    print("CSS: already present")

page = root / "frontend/src/pages/NewHomePage.tsx"
sales_frag = (root / "scripts/sales_desk_panel.fragment.tsx").read_text(encoding="utf-8")
dash_path = root / "scripts/dashboard_desk_panel.fragment.tsx"
if dash_path.exists():
    dash_frag = dash_path.read_text(encoding="utf-8")
else:
    dash_frag = (root / "scripts/dashboard_desk_panel.fragment.a.tsx").read_text(encoding="utf-8")
    dash_frag += (root / "scripts/dashboard_desk_panel.fragment.b.tsx").read_text(encoding="utf-8")
t = page.read_text(encoding="utf-8")

t = t.replace(
    'بر پایهٔ گزارش رسمی موجودی کم.</p>\\n                  <Link to="/inventory?section=low-stock"',
    'بر پایهٔ گزارش رسمی موجودی کم.</p>\n                  <Link to="/inventory?section=low-stock"',
)

s = t.find('{pageView === "content" && active === "sales" && (')
e = t.find('{pageView === "content" && active === "about"')
if s < 0 or e < 0:
    raise SystemExit("sales bounds not found")
t = t[:s] + sales_frag + t[e:]

hs = t.find('{pageView === "content" && active === "home" && (')
he = t.find('{pageView === "content" && active === "previous"')
if hs < 0 or he < 0:
    raise SystemExit("dashboard bounds not found")
t = t[:hs] + dash_frag + t[he:]

page.write_text(t, encoding="utf-8")
print("OK: sales desk + dashboard pulse applied")
