# گزارش پیشرفت واحد پروفایل مشتری

| زمان | وضعیت | یادداشت |
|------|--------|----------|
| 2026-08-30 | خودارزیابی | مسیر درست؛ هدف واضح؛ بدون خرابکاری واحدهای دیگر |
| 2026-08-30 | Intake کامل‌تر | open_case=true → case_id + recommendation_profile یکجا |

**جریان فروشنده گالری (یک شات):**
```
POST /api/v1/customers/intake
  { name, mobile?, concerns, consent, open_case: true }
→
{
  customer,
  case: { case_id },
  recommendation_profile: { concerns },
  generate_hint → POST /recommendations/generate
}
```

**محدوده:** فقط `customers` router/service + docs + تست واحد پروفایل.
