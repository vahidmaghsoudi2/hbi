#!/usr/bin/env python3
"""Apply POS-style sales form (items first, optional party, no mobile field) to NewHomePage."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
page = root / "frontend/src/pages/NewHomePage.tsx"
frag = root / "scripts/sales_pos_panel.fragment.tsx"
t = page.read_text(encoding="utf-8")
panel = frag.read_text(encoding="utf-8")

old_err = 'setError("برای جست‌وجوی مشتری، شماره موبایل یا نام خانوادگی را وارد کنید.");'
new_err = 'setError("برای اتصال طرف‌حساب، نام خانوادگی را وارد کنید.");'
if old_err in t:
    t = t.replace(old_err, new_err, 1)

old_choose_needle = 'setSaleCustomerLabel(`${customer.family_name ?? "نام خانوادگی ثبت نشده"} · ${customer.mobile ?? "بدون موبایل"}`);'
new_choose_label = 'setSaleCustomerLabel(customer.family_name?.trim() || customer.customer_id);'
if old_choose_needle in t:
    t = t.replace(old_choose_needle, new_choose_label, 1)
if 'مشتری فقط برای این فروش انتخاب شد؛ نشست مشاوره تغییر نکرد.' in t:
    t = t.replace(
        'مشتری فقط برای این فروش انتخاب شد؛ نشست مشاوره تغییر نکرد.',
        'طرف‌حساب فقط به این فاکتور متصل شد؛ مشاوره شروع نشد.',
        1,
    )

start = t.find('{pageView === "content" && active === "sales" && (')
end = t.find('{pageView === "content" && active === "about"')
if start < 0 or end < 0:
    raise SystemExit("sales/about bounds not found")
t = t[:start] + panel + t[end:]
page.write_text(t, encoding="utf-8")
print("OK: sales form is now POS-style (no mobile field on invoice)")
