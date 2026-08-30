# گزارش پیشرفت واحد پروفایل مشتری

| زمان | وضعیت | یادداشت |
|------|--------|----------|
| 2026-08-30 | Phase 0 + قرارداد Qwen1 | docs/11_customer_profile |
| 2026-08-30 | Decision-Log | دیدگاه مدیر گالری |
| 2026-08-30 | Service | register_guest، build_recommendation_profile، record_intake |
| 2026-08-30 | API فقط customers | POST /guest، POST /intake، GET /recommendation-profile |

**فایل‌های لمس‌شده این مأموریت:**
- `app/services/customer_service.py`
- `app/api/routers/customers.py`
- `docs/11_customer_profile/*`

**عمداً دست‌نخورده:** recommendation، reasoning، product_repository، seeds، cases، sales.

**جریان گالری:**
```
POST /customers/intake  →  customer + recommendation_profile
POST /cases/           →  case_id
POST /recommendations/generate  {case_id, customer_profile: recommendation_profile}
```
