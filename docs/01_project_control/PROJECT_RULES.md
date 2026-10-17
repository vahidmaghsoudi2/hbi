# HBI — قوانین پروژه / PROJECT RULES

**Status:** ACTIVE
**Authority:** Project-wide Mandatory Rule
**Source of Truth:** GitHub `master`
**Project:** HBI — Health & Beauty Intelligence
**Effective Date:** 2026-09-02
**Last Governance Update:** 2026-10-17 (AI execution protocol simplified per PO direction)

---

# 0. قانون ورود اجباری / ENTRY GATE

هر Human یا AI که وارد پروژه HBI می‌شود، قبل از هرگونه تحلیل، طراحی، کدنویسی، تغییر فایل، پیشنهاد معماری، اجرای Script، ایجاد Issue یا Commit باید این فایل را مطالعه و رعایت کند.

فایل رسمی قوانین پایه:

`docs/01_project_control/PROJECT_RULES.md`

**پروتکل اجرایی واحد و اجباری (پس از ادغام به master):**

`docs/01_project_control/HBI_AGENT_EXECUTION_PROTOCOL.md`

این سند مرجع اجرای دستور، جلوگیری از تکرار کار، ثبت شواهد و گزارش وضعیت است؛ نقش ثابت، بستهٔ تحویل اجباری یا نقش اجباری راستی‌آزمای مستقل ایجاد نمی‌کند. فایل‌های پروتکل اجرایی هم‌پوشان که در تغییر حاکمیتی مربوطه حذف شوند، دیگر مرجع فعال نیستند.

پیش از اقدام، وضعیت زندهٔ GitHub، تصمیم/قرارداد معتبر و شواهد مرتبط با همان کار را بررسی کنید. فقط اسناد و آزمون‌های مرتبط را بخوانید؛ از تشریفات یا تکرار بررسی‌های تکمیل‌شده پرهیز کنید.

---

# 0.1 دسترسی GitHub

- Repository: https://github.com/vahidmaghsoudi2/hbi (public)
- همه اعضای تیم: دسترسی **خواندن** از ابتدا تا اکنون — ادعای عدم دسترسی خواندن پذیرفته نیست
- نوشتن / PR / Merge: فقط طبق مجوز PO و فرآیند پروژه

---

# 1. SOURCE OF TRUTH

منبع رسمی حقیقت پروژه GitHub repository در branch `master` است.

لپ‌تاپ، Notion، حافظه مدل، پیام‌های قدیمی، خلاصه مکالمات و گزارش‌های قدیمی به‌تنهایی Evidence محسوب نمی‌شوند.

در صورت اختلاف، وضعیت واقعی Repository باید مستقیماً بررسی و Conflict ثبت شود.

---

# 2. قانون NO ASSUMPTION

هیچ عضو پروژه مجاز نیست چیزی را که مستقیماً در Repository، Evidence یا منبع معتبر مشاهده نشده است، به‌عنوان واقعیت اعلام کند.

ممنوع:
- حدس درباره فایل، API، Schema، Database، UI، Status، Lifecycle، Business Rule، Integration، یا انجام‌شدن قبلی کار

وضعیت‌های مجاز:
- VERIFIED EXISTING · PARTIAL · NOT FOUND · CONFIRMED MISSING · UNKNOWN · CONFLICT · DECIDED · OPEN

If data is missing, the AI must answer explicitly using one of:
UNKNOWN | I DON’T KNOW | NOT VERIFIED | CONFLICT DETECTED | EVIDENCE REQUIRED

---

# 3. قانون NO INVENTED DATA

هیچ داده، Product، Customer، Transaction، Evidence، Claim، API، Schema، Status، Endpoint، Business Rule یا Architecture نباید برای پر کردن خلأ ساخته شود.

UNKNOWN جای حدس را می‌گیرد. Conflict بدون تصمیم معتبر حل نشود.

---

# 4. CURRENT SHA

قبل از هر مأموریت: `git fetch origin master` و `git rev-parse origin/master`

SHA قدیمی را Current اعلام نکنید.

---

# 5. REALITY AUDIT

قبل از Implementation باید Reality Audit انجام شود (structure، branch، SHA، frontend، backend، APIs، models، schema، docs، tests، integrations، Product Master، Evidence، Knowledge، …).

خروجی باید قابل ردیابی باشد.

---

# 6. قانون اول پیدا کن، بعد بساز

قابلیت موجود را بدون بررسی دوباره نسازید. Rebuild بدون تصمیم رسمی ممنوع است.

---

# 7. HOME PAGE و PRODUCT GALLERY

Home Page و Gallery فعلی بخشی از Reality هستند؛ قبل از تغییر بررسی شوند. دوباره ساخته نشوند.

---

# 8. ONE PRODUCT MASTER

فقط یک Product Master و یک `product_id` مشترک. Catalog موازی بدون تصمیم رسمی ممنوع است.

---

# 9. PRODUCT INTAKE

بر اساس Reality موجود تکمیل شود. AI Research می‌کند؛ Approve نهایی با PO و Gate رسمی است.

---

# 10. قانون صفر تا صد / 0 → 100

هر AI می‌تواند هر کاری را که PO دستور می‌دهد از ابتدا تا پایان انجام دهد. نقش ثابت، نویسندهٔ ازپیش‌تعیین‌شده یا تقسیم اجباری کار وجود ندارد. آزمون، شواهد و ثبت تغییرات را متناسب با نوع و ریسک کار انجام دهید.

---

# 11. EXECUTION PACKAGE

No mandatory execution-package template; follow the PO's direct task instructions and inspect existing evidence.

---

# 12. قانون ردپا / TRACEABILITY

برای تغییرات معنادار، درخواست، مبنا، تغییر، آزمون/شواهد متناسب، SHA و موارد باقی‌مانده را قابل ردیابی نگه دارید؛ این فهرست قالب اجباری گزارش نیست.

---

# 13–14. POWERSELL SCRIPT / SET-CLIPBOARD

Scriptهای اجرایی کاربر: یکپارچه، قابل paste یک‌باره، با error handling. Clipboard بدون credential.

---

# 15. SAFE GIT

ممنوع در حالت عادی: reset --hard، clean -fd، force push، history rewrite، overwrite تغییرات دیگران.

---

# 16. EVIDENCE RULE

هر ادعای مهم Evidence می‌خواهد (path، SHA، test، command output). «بررسی شد» بدون Evidence کافی نیست.

---

# 17. STATUS RULE

VERIFIED EXISTING · PARTIAL · NOT FOUND · CONFIRMED MISSING · UNKNOWN · CONFLICT · DECIDED · OPEN  
AI حق ندارد OPEN را DECIDED کند.

---

# 18. CONTRACT BEFORE IMPLEMENTATION

REALITY → GAP → DECISION → CONTRACT → IMPLEMENTATION → TEST → EVIDENCE → COMMIT

---

# 19. TEST RULE

کد بدون Test کامل نیست. Happy Path کافی نیست.

---

# 20. GATE RULE

وجود کد به‌تنهایی اثبات تکمیل نیست؛ معیارهای پذیرش و آزمون/شواهد مرتبط با همان کار را بررسی کنید. قالب تحویل ثابت یا نقش اجباری بازبین ایجاد نکنید.

---

# 21. PARALLEL EXECUTION

هماهنگی موازی را متناسب با وابستگی واقعی انجام دهید؛ نقش یا مسئول ثابت از پیش تعیین‌شده الزامی نیست.

---

# 22. CHANGE CONTROL

تغییر تصمیم قبلی باید Previous/New/Reason/Impact/Owner/Approval داشته باشد. Silent overwrite ممنوع.

---

# 23. FROZEN / ACCEPTED AREAS

**FROZEN BY DEFAULT** — reopen فقط با Evidence، Impact Analysis و مجوز PO.  
Accounting V1، Product Master، و موارد اعلام‌شده محافظت‌شده‌اند. فرآیند Finding → PO → WP اجباری است.

---

# 24. AI EXECUTION AUTHORITY

هر AI می‌تواند هر کار پژوهشی، طراحی، نوشتن، پیاده‌سازی، آزمون، بررسی و اصلاح را که PO دستور می‌دهد انجام دهد؛ نقش تخصصی ثابت یا مسئول نوشتن/تأیید از پیش تعیین‌شده وجود ندارد. تصمیم‌های کسب‌وکار و تأیید محصول تابع مجوز و Gate مصوب‌اند؛ داده‌سازی و تغییر بی‌اجازه ممنوع است.

---

# 25. PO AUTHORITY

PO مرجع نهایی Business است. نقش‌های تخصصی تیم (Integration / Implementation / QA و غیره) جایگزین PO نیستند.

---

# 26. FINAL REPORT

نتیجه واقعی، مسیر/SHA و شواهد لازم، موارد باز و اقدام بعدی را مختصر گزارش کنید؛ قالب ثابت اجباری نیست.

---

# 27. STOP CONDITIONS

STOP + DOCUMENT + REPORT — نه GUESS + CONTINUE.

---

# 28. CONTINUITY

اطلاعات موجود در Repository را دوباره از PO نخواهید. بسته تحویل یا قالب handoff اجباری نیست؛ فقط اطلاعات لازم برای ادامه کار را ثبت کنید.

---

# 29. PRODUCT INTAKE ROADMAP

Phase 0–7 و Gates G1–G8 مطابق سند Product Intake (جزئیات در docs مربوطه).

---

# 30. MEMORY RULE

MEMORY MAY GUIDE SEARCH. REPOSITORY MUST VERIFY REALITY.

---

# 31. NO PREMATURE GREEN

وضعیت تکمیل را فقط با معیارهای پذیرش و شواهد واقعی اعلام کنید؛ گزارش یا قالب تحویل تشریفاتی شرط عمومی نیست.

---

# 32. DEFINITION OF DONE

معیار تکمیل تابع نوع کار و معیار پذیرش آن است؛ نتیجه و شواهد لازم را صادقانه ثبت کنید، بدون قالب تحویل اجباری.

---

# 33. ENTRY CHECK

قبل از اقدام، قوانین مرتبط، وضعیت واقعی GitHub، SHA جاری و شواهد موجود را بررسی کنید؛ تأییدیه تشریفاتی یا قالب پاسخ اجباری نیست.

---

# 34. FINAL AUTHORITY

تعارض Memory/چت قدیمی با GitHub master → Repository + تصمیم رسمی PO. Conflict واقعی ثبت شود.

---

# 35. RECORD — Unified Agent Execution Protocol

**Source:** Explicit Product Owner direction, 2026-10-17.  
**Canonical path:** `docs/01_project_control/HBI_AGENT_EXECUTION_PROTOCOL.md`  
**Effect:** واحدسازی قواعد اجرای دستور، عدم تکرار، شواهد و گزارش صادقانهٔ وضعیت؛ بدون نقش ثابت یا بستهٔ تحویل اجباری. پس از merge، پروتکل‌های اجرایی هم‌پوشان از درخت فعال حذف می‌شوند؛ قراردادهای تخصصی دامنه و راهنمای اسکریپت فقط در حوزه متمایز خود باقی می‌مانند.

---

**END OF PROJECT_RULES (core retained; see full history for extended prior wording on PowerShell/clipboard examples if needed)**
