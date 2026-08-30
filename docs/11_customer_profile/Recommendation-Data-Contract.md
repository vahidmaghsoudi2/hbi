# قرارداد اتصال پروفایل مشتری → موتور توصیه (Qwen1 × Grok1)

**منبع:** گزارش هماهنگی Qwen1 + Reality master `403848a`  
**وضعیت:** ACCEPTED by Customer Profile unit (Grok1)

## ۱. Input Contract (الزامی برای تیم پروفایل)

```text
RecommendationFacade.generate(case_id: str, customer_profile: Dict) -> List[RecommendationDTO]
```

| کلید | نوع | الزام | توضیح |
|------|-----|-------|--------|
| `concerns` | `str` یا `list[str]` | توصیه‌شده برای شخصی‌سازی | نیاز/دغدغه؛ رشته جدا با کاما یا لیست |
| سایر کلیدها | آزاد | اختیاری | فعلاً موتور عمدتاً `concerns` را می‌خواند |

**Null-safety (موجود در کد):**
- Facade: `customer_profile or {}`
- Service: `if customer_profile is None: customer_profile = {}`

تیم پروفایل باید در API/UI همیشه یک `dict` بفرستد (حتی `{}`) و حالت **No Match** را عادی بداند.

## ۲. خروجی مورد انتظار از توصیه
- لیست خالی یا امتیاز پایین **معتبر** است (بدون Evidence ساختگی).
- UI Intake / مشاوره: سناریوی «محصول منطبق یافت نشد» را به‌عنوان حالت عادی نمایش دهد.

## ۳. مرزهای ممنوعه (Do Not Touch) — تأیید شده
| مسیر | دلیل |
|------|------|
| `app/services/recommendation_service.py` | مالک Recommendation |
| `app/repositories/product_repository.py` | مالک Product repo |
| `app/reasoning/` (scoring + constants) | Frozen |
| `data/seed_products.json` | Frozen |
| `data/seed_evidence.json` | Frozen |

هر نیاز به تغییر در این‌ها فقط از مسیر Gate Manager (Qwen1).

## ۴. مسئولیت واحد پروفایل
1. جمع‌آوری پروفایل / Visit / نیازسنجی
2. ساخت یا اتصال `case_id` معتبر با ownership مشتری
3. ساخت `customer_profile` dict (حداقل `concerns` وقتی موجود است)
4. فراخوانی generate **بدون** دستکاری منطق scoring
5. مدیریت UX برای لیست خالی / READY_WITH_UNKNOWN

## ۵. جریان یکپارچه هدف
```
Customer Profile / Intake
    → case_id + customer_profile{"concerns": ...}
    → RecommendationFacade.generate
    → UI (نتایج یا No Match)
```

## ۶. تست هماهنگی بعدی
پس از آماده شدن ماژول Intake: Integration Test مشترک با تیم Recommendation (E2E: Profile → API → UI).

**ثبت:** Grok1 — 2026-08-30
