# HBI — قوانین پروژه / PROJECT RULES

**Status:** ACTIVE
**Authority:** Project-wide Mandatory Rule
**Source of Truth:** GitHub `master`
**Project:** HBI — Health & Beauty Intelligence
**Effective Date:** 2026-09-02
**Last Governance Update:** 2026-09-09 (Team Operational Directive pointer + prior rules retained)

---

# 0. قانون ورود اجباری / ENTRY GATE

هر Human یا AI که وارد پروژه HBI می‌شود، قبل از هرگونه تحلیل، طراحی، کدنویسی، تغییر فایل، پیشنهاد معماری، اجرای Script، ایجاد Issue یا Commit باید این فایل را مطالعه و رعایت کند.

فایل رسمی قوانین پایه:

`docs/01_project_control/PROJECT_RULES.md`

**دستورالعمل عملیاتی و ارتباطی تیم (مکمل اجباری از 2026-09-09):**

`docs/01_project_control/HBI_TEAM_OPERATIONAL_COMMUNICATION_DIRECTIVE_V1.md`  
**Document ID:** `HBI-TEAM-OPS-COM-001`

شامل: قالب پاسخ تیمی، استقلال فکری، Circuit Breaker فشرده، فازهای F0–F7، و **سیاست دسترسی GitHub** (مخزن عمومی `vahidmaghsoudi2/hbi` — خواندن برای همه اعضا؛ نوشتن فقط با دستور PO به Grokها/Owner مجاز).

عدم مطالعه قوانین پایه + دستورالعمل ارتباطی = عدم مجوز شروع کار.

ترتیب اجباری ورود:

1. خواندن PROJECT_RULES.md
2. خواندن HBI_TEAM_OPERATIONAL_COMMUNICATION_DIRECTIVE_V1.md
3. شناسایی مأموریت / Unit
4. خواندن Roadmap و Ledger مربوطه
5. بررسی مستقیم origin/master
6. ثبت Current SHA
7. انجام Reality Audit
8. شناسایی Existing / Partial / Missing / Unknown / Conflict
9. سپس شروع اجرای کار

---

# 0.1 دسترسی GitHub (خلاصه — جزئیات در TEAM-OPS-COM-001)

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

Owner مسئول Unit از صفر تا صد است (Rules → Reality → Scope → Implement/Document → Test → Evidence → Commit → Ledger → Handoff).

**ONE TASK = ONE OWNER = END-TO-END ACCOUNTABILITY**

---

# 11. EXECUTION PACKAGE اجباری

Unit جدید بدون Execution Package شروع نمی‌شود.

---

# 12. قانون ردپا / TRACEABILITY

REQUEST → WHY → OWNER → BASELINE → INSPECTION → DECISION → CHANGE → TEST → EVIDENCE → COMMIT → SHA → REMAINING → NEXT ACTION

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

وجود کد به‌تنهایی Complete نیست؛ Test، Evidence، Review، Commit، Ledger، Handoff لازم است.

---

# 21. PARALLEL EXECUTION

فقط با Dependency و Owner مشخص برای Shared Contract/Schema.

---

# 22. CHANGE CONTROL

تغییر تصمیم قبلی باید Previous/New/Reason/Impact/Owner/Approval داشته باشد. Silent overwrite ممنوع.

---

# 23. FROZEN / ACCEPTED AREAS

**FROZEN BY DEFAULT** — reopen فقط با Evidence، Impact Analysis و مجوز PO.  
Accounting V1، Product Master، و موارد اعلام‌شده محافظت‌شده‌اند. فرآیند Finding → PO → WP اجباری است.

---

# 24. AI ROLE BOUNDARY & END-TO-END ACCOUNTABILITY

Roles = specialization only. Ownership = end-to-end. کمک دیگران مالکیت را منتقل نمی‌کند.

AI بدون Authority: Business Decision نهایی، Approve محصول، silent Contract/Schema change، داده ساختگی — ممنوع.

---

# 25. PO AUTHORITY

PO مرجع نهایی Business است. نقش‌های تخصصی تیم (Integration / Implementation / QA و غیره) جایگزین PO نیستند.

---

# 26. FINAL REPORT STANDARD

گزارش پایانی Unit باید MISSION، SHAها، REALITY، CHANGES، TESTS، EVIDENCE، OPEN، HANDOFF، NEXT ACTION داشته باشد.

---

# 27. STOP CONDITIONS

STOP + DOCUMENT + REPORT — نه GUESS + CONTINUE.

---

# 28. CONTINUITY / HANDOFF

Roadmap، Ledger، Status، SHA، Decisions، Next Action باید نفر بعدی را بی‌نیاز از بازجویی کند.

---

# 29. PRODUCT INTAKE ROADMAP

Phase 0–7 و Gates G1–G8 مطابق سند Product Intake (جزئیات در docs مربوطه).

---

# 30. MEMORY RULE

MEMORY MAY GUIDE SEARCH. REPOSITORY MUST VERIFY REALITY.

---

# 31. NO PREMATURE GREEN

GREEN فقط با Scope، Tests، Evidence، Commit، Remote verify، Handoff، بدون Blocker.

---

# 32. DEFINITION OF DONE

Objective، Scope، Tests، Evidence، Decisions، Commit، Remote SHA، Ledger، Handoff، Next action.

---

# 33. MANDATORY ENTRY ACKNOWLEDGEMENT

PROJECT_RULES READ: YES  
TEAM-OPS-COM DIRECTIVE READ: YES  
SOURCE OF TRUTH: GitHub master  
CURRENT SHA VERIFIED: YES  
REALITY AUDIT REQUIRED: YES  
NO ASSUMPTION / NO INVENTED DATA: ACCEPTED  
0→100 OWNERSHIP: ACCEPTED  
EVIDENCE REQUIRED: ACCEPTED

---

# 34. FINAL AUTHORITY

تعارض Memory/چت قدیمی با GitHub master → Repository + تصمیم رسمی PO. Conflict واقعی ثبت شود.

---

# 35. RECORD — Team Operational Directive (2026-09-09)

**Source:** PO مقصودی  
**Document:** `HBI-TEAM-OPS-COM-001`  
**Path:** `docs/01_project_control/HBI_TEAM_OPERATIONAL_COMMUNICATION_DIRECTIVE_V1.md`  
**Effect:** مکمل ارتباطی/عملیاتی؛ جایگزین PROJECT_RULES نیست.

---

**END OF PROJECT_RULES (core retained; see full history for extended prior wording on PowerShell/clipboard examples if needed)**
