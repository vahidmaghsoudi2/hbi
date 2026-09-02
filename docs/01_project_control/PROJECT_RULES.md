# HBI — قوانین پروژه / PROJECT RULES

**Status:** ACTIVE
**Authority:** Project-wide Mandatory Rule
**Source of Truth:** GitHub `master`
**Project:** HBI — Health & Beauty Intelligence
**Effective Date:** 2026-09-02

---

# 0. قانون ورود اجباری / ENTRY GATE

هر Human یا AI که وارد پروژه HBI می‌شود، قبل از هرگونه تحلیل، طراحی، کدنویسی، تغییر فایل، پیشنهاد معماری، اجرای Script، ایجاد Issue یا Commit باید این فایل را مطالعه و رعایت کند.

فایل رسمی قوانین:

`docs/01_project_control/PROJECT_RULES.md`

عدم مطالعه این فایل = عدم مجوز شروع کار.

ترتیب اجباری ورود:

1. خواندن PROJECT_RULES.md
2. شناسایی مأموریت / Unit
3. خواندن Roadmap و Ledger مربوطه
4. بررسی مستقیم origin/master
5. ثبت Current SHA
6. انجام Reality Audit
7. شناسایی Existing / Partial / Missing / Unknown / Conflict
8. سپس شروع اجرای کار

---

# 1. SOURCE OF TRUTH

منبع رسمی حقیقت پروژه GitHub repository در branch `master` است.

لپ‌تاپ، Notion، حافظه مدل، پیام‌های قدیمی، خلاصه مکالمات و گزارش‌های قدیمی به‌تنهایی Evidence محسوب نمی‌شوند.

در صورت اختلاف، وضعیت واقعی Repository باید مستقیماً بررسی و Conflict ثبت شود.

---

# 2. قانون NO ASSUMPTION

هیچ عضو پروژه مجاز نیست چیزی را که مستقیماً در Repository، Evidence یا منبع معتبر مشاهده نشده است، به‌عنوان واقعیت اعلام کند.

ممنوع:
- حدس درباره فایل
- حدس درباره API
- حدس درباره Schema
- حدس درباره Database
- حدس درباره UI
- حدس درباره Status
- حدس درباره Lifecycle
- حدس درباره Business Rule
- حدس درباره Integration
- حدس درباره اینکه کاری قبلاً انجام شده یا نشده

وضعیت‌های مجاز:
- VERIFIED EXISTING
- PARTIAL
- NOT FOUND
- CONFIRMED MISSING
- UNKNOWN
- CONFLICT
- DECIDED
- OPEN

---

# 3. قانون NO INVENTED DATA

هیچ داده، Product، Customer، Transaction، Evidence، Claim، API، Schema، Status، Endpoint، Business Rule یا Architecture نباید برای پر کردن خلأ ساخته شود.

UNKNOWN جای حدس را می‌گیرد.

Conflict باید به‌عنوان CONFLICT ثبت شود و بدون تصمیم معتبر حل نشود.

---

# 4. CURRENT SHA

هیچ AI یا Human مجاز نیست SHA قدیمی را Current SHA اعلام کند.

قبل از هر مأموریت:

`git fetch origin master`

`git rev-parse origin/master`

Current SHA باید از Repository واقعی گرفته شود.

---

# 5. REALITY AUDIT

قبل از Implementation باید Reality Audit انجام شود.

حداقل موارد:
- Repository structure
- Current branch
- Current origin/master SHA
- Frontend
- Backend
- APIs
- Models
- Database / Schema
- Documents
- Tests
- Scripts
- UI
- Data
- Integrations
- Business Rules
- Product Master
- Evidence
- Knowledge

خروجی Audit باید قابل ردیابی باشد.

---

# 6. قانون اول پیدا کن، بعد بساز

هیچ قابلیت موجودی نباید بدون بررسی دوباره ساخته شود.

قبل از ایجاد File، Component، API، Model، Table، Service، Product Catalog، Product Intake یا Product Master باید Repository بررسی شود.

Existing = تکمیل یا استفاده از همان قابلیت.

Rebuild بدون تصمیم رسمی ممنوع است.

---

# 7. HOME PAGE و PRODUCT GALLERY

Home Page و Gallery فعلی بخشی از Reality پروژه هستند.

قبل از هر تغییر باید حداقل موارد زیر بررسی شوند:
- frontend/src/pages/NewHomePage.tsx
- Product navigation
- Product Gallery
- Catalog
- Product Intake
- Product API
- Product Master integration
- Recommendation integration
- Sales integration
- Existing routes
- Existing styles

قابلیت موجود نباید دوباره ساخته شود.

---

# 8. ONE PRODUCT MASTER

HBI فقط یک Product Master دارد.

تمام بخش‌های مرتبط باید از همان `product_id` استفاده کنند.

این اصل برای Product Knowledge، Evidence، Inventory، Stock Movement، Sales، Returns، Recommendations و Accounting در صورت وجود اعمال می‌شود.

ایجاد Catalog یا Product database موازی بدون تصمیم رسمی ممنوع است.

---

# 9. PRODUCT INTAKE

Product Intake باید بر اساس Reality موجود تکمیل شود، نه با بازسازی از صفر.

Lifecycle هدف:

INTRODUCE → IDENTITY / DUPLICATE CHECK → RESEARCH → ENRICH → VALIDATE → PO REVIEW → APPROVE → REGISTER / ACTIVATE → CONTINUOUS UPDATE → RE-VALIDATE WHEN REQUIRED

AI مسئول Research و Research Draft است.

AI بدون Gate رسمی حق Approve کردن Product Master را ندارد.

PO مرجع نهایی Review / Edit / Approval است.

---

# 10. قانون صفر تا صد / 0 → 100

هر عضوی که یک Unit یا Phase را قبول می‌کند، مسئول انجام آن از صفر تا صد است.

صفر تا صد شامل:
1. Read Rules
2. Inspect Reality
3. Define baseline
4. Define scope
5. Identify dependencies
6. Identify gaps
7. Plan
8. Implement / Document
9. Test
10. Self-Audit
11. Evidence
12. Commit
13. Verify SHA
14. Update Ledger
15. Final Report
16. Handoff
17. Next Action

تحویل چند فایل بدون Test، Evidence و Handoff انجام کامل محسوب نمی‌شود.

---

# 11. EXECUTION PACKAGE اجباری

هیچ Unit جدیدی بدون Execution Package شروع نمی‌شود.

Execution Package باید شامل:
- Unit ID
- Owner
- Authority
- Purpose
- Objective
- Scope
- Out of Scope
- Baseline
- Current SHA
- Dependencies
- Decisions
- Open Decisions
- Inputs
- Outputs
- Artifacts
- Paths
- API / Data boundaries
- Execution steps
- Roadmap
- Acceptance Criteria
- Tests
- Evidence
- Safety / Rollback
- Completion Definition
- Handoff
- Next Unit

باشد.

---

# 12. قانون ردپا / TRACEABILITY

هر تغییر مهم باید ردپا داشته باشد:

REQUEST → WHY → OWNER → BASELINE → INSPECTION → DECISION → CHANGE → TEST → EVIDENCE → COMMIT → SHA → REMAINING → NEXT ACTION

هیچ تغییر مهمی نباید بدون امکان بازسازی تاریخچه آن باقی بماند.

---

# 13. POWERSELL SCRIPT RULE

هر Script اجرایی که برای کاربر تهیه می‌شود باید:
- کامل باشد
- یکپارچه باشد
- قابل Copy/Paste یک‌باره باشد
- وابسته به تکه‌های قبلی نباشد
- Error Handling داشته باشد
- قبل از تغییر وضعیت را بررسی کند
- از عملیات مخرب جلوگیری کند
- در پایان گزارش نتیجه بدهد

ارسال Script به‌صورت قطعات پراکنده ممنوع است، مگر کاربر صراحتاً بخواهد.

---

# 14. SET-CLIPBOARD

هر Script عملیاتی که خروجی مهم تولید می‌کند باید در پایان گزارش خلاصه یا کامل نتیجه را با `Set-Clipboard` در Clipboard ذخیره کند.

اطلاعات حساس مانند Password، Token، API Key و Credential نباید وارد Clipboard شوند.

---

# 15. SAFE GIT

در حالت عادی ممنوع:
- git reset --hard
- git clean -fd
- git push --force
- git push -f
- history rewrite
- حذف فایل‌های نامرتبط
- overwrite تغییرات دیگران

فقط فایل‌های مربوط به Unit باید Stage شوند.

تغییرات نامرتبط Worktree باید حفظ شوند.

---

# 16. EVIDENCE RULE

هر ادعای مهم باید Evidence داشته باشد.

Evidence می‌تواند شامل File Path، Code Location، API Route، Test Result، Git SHA، Command Output، Artifact ID یا External Source باشد.

عبارت «بررسی شد و درست است» بدون Evidence کافی نیست.

---

# 17. STATUS RULE

وضعیت‌های رسمی:

VERIFIED EXISTING = مستقیماً مشاهده و تأیید شده

PARTIAL = بخشی وجود دارد

NOT FOUND = در محدوده بررسی پیدا نشده

CONFIRMED MISSING = با بررسی کافی مشخصاً وجود ندارد

UNKNOWN = اطلاعات کافی نیست

CONFLICT = منابع متناقض هستند

DECIDED = تصمیم رسمی گرفته شده

OPEN = هنوز تصمیم یا اقدام لازم است

AI حق ندارد OPEN را با تفسیر شخصی DECIDED کند.

---

# 18. CONTRACT BEFORE IMPLEMENTATION

اگر Unit دارای API، Schema، Lifecycle، Data Contract یا Business Rule جدید است:

REALITY → GAP → DECISION → CONTRACT → IMPLEMENTATION → TEST → EVIDENCE → COMMIT

Implementation نباید جای Contract را بگیرد.

---

# 19. TEST RULE

کد بدون Test کامل محسوب نمی‌شود.

در صورت نیاز باید موارد زیر بررسی شوند:
- Static inspection
- Build
- Unit test
- API test
- Integration test
- Database test
- Browser / UI test
- End-to-end test
- Failure paths

Happy Path به‌تنهایی کافی نیست.

---

# 20. GATE RULE

هیچ Phase یا Gate فقط به دلیل وجود کد Complete نیست.

Completion نیازمند:
- Implementation / Documentation
- Tests
- Evidence
- Review
- Commit
- SHA verification
- Ledger update
- Remaining items
- Handoff

است.

---

# 21. PARALLEL EXECUTION

کارها می‌توانند موازی باشند فقط اگر Dependency اجازه دهد.

قبل از موازی‌سازی باید Shared File، Shared Schema، Contract Boundary و Owner مشخص شوند.

دو تیم نباید همزمان یک Contract یا Schema مشترک را بدون هماهنگی تغییر دهند.

---

# 22. CHANGE CONTROL

هر تغییر مهم نسبت به تصمیم قبلی باید ثبت شود:
- Previous Decision
- New Proposal
- Reason
- Impact
- Owner
- Approval
- Date
- Affected Artifacts

تصمیم قبلی نباید Silent Overwrite شود.

---

# 23. FROZEN / ACCEPTED AREAS

قابلیت‌های Freeze یا Accept شده بدون Change رسمی نباید شکسته یا بازطراحی شوند.

به‌طور خاص:
- Accounting V1
- Product Master
- Product A-D
- Existing Home capabilities

باید محافظت شوند.

---

# 24. AI ROLE BOUNDARY

AI می‌تواند Inspect، Research، Analyze، Implement، Test، Document و Report کند.

AI بدون Authority نباید Business Decision نهایی بگیرد، Product را Approve کند، Contract را silently تغییر دهد، Schema را بدون تصمیم تغییر دهد یا Data / Evidence ساختگی تولید کند.

---

# 25. PO AUTHORITY

PO مرجع نهایی تصمیمات Business است.

ChatGPT در نقش Integration Architect مسئول Contract Integrity، Cross-module consistency، Reality Check، Gate Control، Traceability و Conflict Detection است.

DeepSeek مسئول Technical Implementation است.

Qwen مسئول Knowledge / QA / Validation است.

---

# 26. FINAL REPORT STANDARD

هر Owner در پایان Unit باید گزارش دهد:

MISSION
OWNER
PHASE
GATE
START SHA
END SHA
REALITY AUDIT
EXISTING
PARTIAL
MISSING
UNKNOWN
CONFLICT
CHANGES
FILES
APIs
DATA / SCHEMA
TESTS
EVIDENCE
DECISIONS
OPEN DECISIONS
RISKS
BLOCKERS
PROTECTED AREAS CHECK
COMMIT
REMOTE VERIFICATION
REMAINING
HANDOFF
NEXT EXACT ACTION
FINAL VERDICT

---

# 27. STOP CONDITIONS

کار باید متوقف شود اگر:
- Current SHA مشخص نیست
- Repository قابل اعتماد نیست
- Conflict جدی وجود دارد
- Contract لازم وجود ندارد
- Decision ضروری OPEN است
- احتمال از دست رفتن تغییرات دیگران وجود دارد
- Test ضروری شکست خورده
- Evidence کافی وجود ندارد
- Implementation با تصمیم رسمی تناقض دارد

قاعده:

STOP + DOCUMENT + REPORT

نه:

GUESS + CONTINUE

---

# 28. CONTINUITY / HANDOFF

هر Phase باید دارای Roadmap، Ledger، Artifact List، Current Status، Current SHA، Decisions، Open Decisions، Risks و Next Action باشد.

نفر بعدی نباید مجبور شود وضعیت پروژه را با پرسیدن از نفر قبلی بازسازی کند.

---

# 29. PRODUCT INTAKE ROADMAP

Roadmap رسمی Product Intake:

Phase 0 — Reality & Baseline
Phase 1 — Product Intake Contract v1
Phase 2 — AI Research / Intake
Phase 3 — Validation & Enrichment
Phase 4 — PO Review & Approval
Phase 5 — Product Master Registration & Integration
Phase 6 — Update / Version / Re-validation
Phase 7 — Real Product Pilot & Acceptance

Acceptance Gates:
G1 Identity
G2 Research
G3 Validation
G4 Human Review
G5 Approval
G6 Integration
G7 Maintenance
G8 Real Product Pilot

---

# 30. MEMORY RULE

Memory و خلاصه مکالمات فقط برای Orientation هستند.

آنها Evidence نیستند.

اصل:

MEMORY MAY GUIDE SEARCH.
REPOSITORY MUST VERIFY REALITY.

---

# 31. NO PREMATURE GREEN

GREEN فقط زمانی مجاز است که Scope، Tests، Evidence، Commit، Remote SHA Verification، Handoff و عدم وجود Blocker تأیید شده باشد.

---

# 32. DEFINITION OF DONE

یک Unit زمانی Done است که:

[ ] Objective achieved
[ ] Scope completed
[ ] Existing capabilities protected
[ ] Tests passed
[ ] Evidence produced
[ ] Decisions recorded
[ ] Open items recorded
[ ] Git commit created
[ ] Remote SHA verified
[ ] Ledger updated
[ ] Handoff documented
[ ] Next action defined

---

# 33. MANDATORY ENTRY ACKNOWLEDGEMENT

هر AI یا Owner در شروع مأموریت باید تأیید کند:

PROJECT_RULES READ: YES
SOURCE OF TRUTH: GitHub master
CURRENT SHA VERIFIED: YES
REALITY AUDIT REQUIRED: YES
NO ASSUMPTION: ACCEPTED
NO INVENTED DATA: ACCEPTED
TRACEABILITY RULE: ACCEPTED
0→100 OWNERSHIP: ACCEPTED
EXECUTION PACKAGE REQUIRED: ACCEPTED
SAFE GIT RULES: ACCEPTED
EVIDENCE REQUIRED: ACCEPTED
HANDOFF REQUIRED: ACCEPTED

---

# 34. FINAL AUTHORITY

در صورت تعارض بین Memory، پیام قدیمی، گزارش قدیمی، حدس AI، فایل محلی، Notion و GitHub master، وضعیت فعلی GitHub و تصمیمات رسمی ثبت‌شده مبنا هستند.

در صورت تعارض واقعی:

CONFLICT

ثبت می‌شود تا تصمیم معتبر گرفته شود.

---

# END OF PROJECT RULES

این فایل یک سند زنده است و تغییر آن نیز مشمول همین قوانین است.

هیچ نسخه جدیدی از این سند نباید بدون Change Trace، دلیل تغییر و Commit قابل ردیابی جایگزین نسخه قبلی شود.
