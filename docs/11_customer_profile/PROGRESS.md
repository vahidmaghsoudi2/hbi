# گزارش پیشرفت واحد پروفایل مشتری

| زمان | وضعیت | یادداشت |
|------|--------|----------|
| 2026-08-30 | Phase 0 + قرارداد Qwen1 | docs |
| 2026-08-30 | Service + API | guest / intake / recommendation-profile |
| 2026-08-30 | Smoke محلی | guest + intake update + profile OK |
| 2026-08-30 | تست واحد | tests/test_customer_profile_unit.py |

**محدوده مجاز:** فقط customers service/router + docs/11_customer_profile + این تست.

**جریان گالری:**
```
POST /api/v1/customers/intake
  → customer + recommendation_profile
POST /api/v1/cases/
  → case_id
POST /api/v1/recommendations/generate
  { case_id, customer_profile: recommendation_profile }
```
