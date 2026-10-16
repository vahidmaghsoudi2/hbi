#!/usr/bin/env python3
"""Apply desk/POS feel to sales + dashboard panels and fix literal \\n bug."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
page = root / "frontend/src/pages/NewHomePage.tsx"
sales_frag = (root / "scripts/sales_desk_panel.fragment.tsx").read_text(encoding="utf-8")
dash_frag = (root / "scripts/dashboard_desk_panel.fragment.tsx").read_text(encoding="utf-8")
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
