"""One-shot align of NewHomePage dashboard labels with navigation IA tests.

Run from repo root:
  python scripts/apply_dashboard_label_fix.py
"""
from pathlib import Path

path = Path("frontend/src/pages/NewHomePage.tsx")
t = path.read_text(encoding="utf-8")
replacements = [
    ("<h1>داشبورد HBI</h1>", "<h1>داشبورد عملیاتی</h1>"),
    (
        '<Link to="/inventory?section=inventory" className="pro-btn-secondary">مشاهدهٔ موجودی</Link>',
        '<Link to="/inventory?section=inventory" className="pro-btn-secondary">گزارش موجودی</Link>',
    ),
    (
        '''                <article className="pro-product-card">
                  <h3>هشدار موجودی کم</h3>
                  <p className="pro-summary">{dashboardLowStock ? dashboardLowStock.length.toLocaleString("fa-IR") : "—"} قلم</p>
                  <p className="pro-muted">آستانهٔ هشدار: موجودی قابل دسترس ≤ ۵؛ از گزارش رسمی موجودی کم.</p>
                </article>''',
        '''                <article className="pro-product-card">
                  <h3>هشدار موجودی کم</h3>
                  <p className="pro-summary">{dashboardLowStock ? dashboardLowStock.length.toLocaleString("fa-IR") : "—"} قلم</p>
                  <p className="pro-muted">آستانهٔ هشدار: موجودی قابل دسترس ≤ ۵؛ از گزارش رسمی موجودی کم.</p>
                  <Link to="/inventory?section=low-stock" className="pro-btn-secondary">کمبود موجودی</Link>
                </article>''',
    ),
    (
        '<Link to="/inventory?section=inventory" className="pro-btn-primary">بازکردن گزارش موجودی</Link>',
        '<Link to="/inventory?section=low-stock" className="pro-btn-primary">کمبود موجودی</Link>',
    ),
    (
        '<Link to="/inventory?section=stock-flow" className="pro-btn-secondary">همهٔ گردش‌ها</Link>',
        '<Link to="/inventory?section=stock-flow" className="pro-btn-secondary">گردش اخیر</Link>',
    ),
]
changed = 0
for old, new in replacements:
    if old in t:
        t = t.replace(old, new, 1)
        changed += 1
    elif new in t:
        print("already applied:", new[:60].replace("\n", " "))
    else:
        raise SystemExit(f"block not found:\n{old[:160]}")
path.write_text(t, encoding="utf-8")
print(f"OK: applied {changed} replacement(s) to {path}")
