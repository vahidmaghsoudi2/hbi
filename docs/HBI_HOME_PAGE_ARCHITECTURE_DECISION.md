# HBI Home Page Architecture Decision Record (ADR)

**Status:** APPROVED  
**Date:** 5 Shahrivar 1405 (2026-08-27)  
**Product Owner:** مهندس مقصودی  
**Scope:** Home Page Operational Dashboard & System Expansion Roadmap  

---

## 1. Core Principles (اصول بنیادین)

1. **Operational Gateway:** صفحه اصلی (Home Page) دروازه‌ی عملیاتی برای مدیر/اپراتور سیستم است.
2. **Phased Expansion Roadmap (نقشه راه گسترش فازبندی‌شده):** 
   HBI به‌تدریج به یک سیستم یکپارچه مدیریت گالری تبدیل می‌شود. عجله در گسترش مجاز نیست، اما رشد تدریجی و تست‌شده تشویق می‌شود:
   - **فاز ۱ (کنونی):** Product Intake + Recommendation Engine + Home Page
   - **فاز ۲ (بعدی):** Customer Profile + Purchase History + Personalized Recommendations
   - **فاز ۳ (گسترش):** Inventory Management + Pricing + Batch/Expiry Tracking
   - **فاز ۴ (یکپارچگی):** POS Integration + Accounting + Advanced Analytics
3. **Separation of Concerns:** تجربه‌ی کاربری مشتری (Customer-facing) در آینده از صفحه‌ی عملیاتی داخلی جدا خواهد بود، اما می‌تواند به هسته‌ی HBI متصل شود.

## 2. Data Integrity & Honesty (صداقت داده‌ها)

4. **Data States:** صفحه اصلی فقط سه نوع داده نمایش می‌دهد: 
   - LIVE (زنده و متصل)
   - PARTIALLY_CONNECTED (اتصال ناقص)
   - PLANNED (در برنامه، با برچسب صریح)
5. **No Fake Data:** ممنوعیت مطلق شمارنده‌ها، صف‌ها، وضعیت‌ها یا اکشن‌های جعلی (Fake).
6. **Real User Paths:** هیچ ویژگی‌ای در صفحه اصلی نمایش داده نمی‌شود، مگر اینکه مسیر کامل کاربری و قرارداد بک‌اند آن واقعاً پیاده‌سازی شده باشد.

## 3. Technical Architecture (معماری فنی)

7. **Reuse Existing States:** باید از وضعیت‌های موجود محصول (VERIFIED, CONFLICT, NEEDS_REVIEW) استفاده شود. ایجاد فیلدهای وضعیت تکراری فقط برای زیبایی UI ممنوع است.
8. **Backend First:** وابستگی‌های بک‌اند (Backend dependencies) باید قبل از پیاده‌سازی ویژگی‌های فرانت‌اند، به‌صورت صریح نقشه‌برداری (Map) شوند.
9. **Attention Queue Contract:** صف توجه (Attention Queue) نیازمند یک قرارداد رسمی تجمیع داده در بک‌اند است.
10. **System Status Definition:** "وضعیت سیستم" به معنای وضعیت قابلیت‌های عملیاتی (مثلاً فعال بودن موتور توصیه) است، نه مانیتورینگ زیرساخت (CPU/RAM).

## 4. Scope Management (مدیریت محدوده)

11. **Lightweight Pilot Entry:** پایلوت باید یک نقطه‌ی ورود بسیار واضح، ساده و سبک داشته باشد.
12. **Product Workspace Evolution:** در این فاز، فضای کار محصول (Product Workspace) یک نقطه‌ی ورود است، اما طبق نقشه‌ی راه، به‌تدریج به ماژول مدیریت کامل محصول تکامل می‌یابد.
13. **Recent Activity:** نمایش "فعالیت‌های اخیر" در فاز ۱ خارج از محدوده‌ی فوری است، اما برای فاز ۲ در نظر گرفته شده است (Planned).

---

## 5. Strict Constraints (محدودیت‌های سخت‌گیرانه)

- ❌ NO modification to scoring.py or scoring_constants.py
- ❌ NO creation of duplicate status fields
- ❌ NO fake data or capabilities
- ❌ NO feature without a real backend contract

---

**Document Status:** REGISTERED IN GITHUB  
**Next Action:** Backend contract definition for Attention Queue and System Status  
**Decision Authority:** Product Owner (مهندس مقصودی)
