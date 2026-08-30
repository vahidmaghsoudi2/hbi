# CustomerProfile v1 — Implementation Contract

**وضعیت:** DRAFT for PO review  
**پایه کد فعلی:** `app/models/customer.py` + `Case` + `CustomerService`

## ۱. نگاشت Reality → هدف

| امروز در master | هدف v1 |
|-----------------|--------|
| `Customer.name` | first_name (+ last_name اختیاری در نسخه بعد) |
| `Customer.mobile` nullable | همان؛ Guest مجاز؛ uniqueness در سرویس |
| `consent_to_store_data` 0/1 | جدول `CustomerConsent` چندنوعی |
| `skin_profile`, `concerns`, `answers` رشته | Visit + ConsultationAnswer ساخت‌یافته |
| `Case` | معادل نزدیک Visit/Consultation؛ حفظ می‌شود |
| — | ProfileFact، PreferenceSignal، TimelineEvent |

## ۲. موجودیت‌های هدف Phase 2 (هنوز پیاده‌سازی نشده)
- Customer (تقویت‌شده)
- CustomerConsent
- CustomerVisit
- ConsultationSession / ConsultationAnswer
- CustomerProfileFact (state: CANDIDATE\|CONFIRMED\|STALE\|SUPERSEDED\|REVOKED)
- CustomerTimelineEvent
- CustomerDataAudit

## ۳. قواعد اجباری در API/UI/Schema
1. UNKNOWN / PREFER_NOT_TO_SAY / NOT_APPLICABLE معتبرند.
2. تهی ≠ FALSE.
3. Purchase ≠ Preference.
4. Operator Observation ≠ Customer Fact.
5. Derived Insight ≠ Confirmed Fact.
6. داده کهنه بدون بازبینی در توصیه استفاده نشود.
7. تعارض حذف یا با آخرین مقدار بی‌صدا جایگزین نشود.

## ۴. Decision Readiness (ساده)
`READY` | `READY_WITH_UNKNOWN` | `CAUTION` | `REVIEW_REQUIRED`

مسدودسازی خودکار فقط برای Safety CRITICAL / REVIEW_REQUIRED.

## ۵. ویرایش نسخه بعدی
- قراردادهای بعدی: `CustomerProfile-v2-...`
- فیلدهای جدید فقط از طریق Change Control و به‌روزرسانی Dictionary
- Migration Plan جدا قبل از هر ALTER اجباری

## ۶. Frozen
Product A–D، Seed، Scoring weights/thresholds، Hard Gate، Evidence claims — بدون تغییر در این واحد.
