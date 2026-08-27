# HBI — Information Feeding & Customer Recommendation Roadmap

**Project:** HBI — Maqsoudi Gallery
**Repository:** vahidmaghsoudi2/hbi
**Product Owner:** مهندس وحید مقصودی
**Stage:** Information Feeding
**Primary Direction:** Customer → Case → Recommendation
**Document Type:** Stage Mission + Team Roadmap + Execution Plan
**Status:** ACTIVE — Initial Roadmap
**Date:** 2026-08-27

---

# 1. Purpose

این سند نقشه حرکت HBI در مرحله‌ای است که در پروژه با عنوان:

> **Information Feeding / تغذیه اطلاعات**

شناخته می‌شود.

هدف این مرحله، ساختن یک سیستم جدید از صفر نیست.

هدف این است که:

> **اطلاعات موجود HBI را به یک جریان واقعی، قابل اجرا، قابل مشاهده و قابل فهم برای تصمیم‌گیری مشتری تبدیل کنیم.**

مسیر اصلی:

Customer → Case / Current Need → Relevant Customer Information → Product Knowledge → Evidence / Knowledge → Eligibility / Elimination → Reasoning → Existing Scoring → Recommendation → Explanation → Product Owner Decision → Outcome

---

# 2. Current Architectural Position

معماری فعلی HBI از قبل مسیر زیر را تعریف کرده است:

Customer → Case → Evidence / Knowledge → Reasoning → Recommendation → Product / Inventory → Outcome

این مرحله این معماری را بازطراحی نمی‌کند. ما فقط باید قطعات موجود را به یک جریان عملی متصل کنیم.

Architecture = Existing
Schema = Existing
Product Knowledge = Existing + New Information Where Needed
Scoring = Existing
Recommendation = Integration / Activation

---

# 3. Important Architectural Decision

## Product Intake و Recommendation دو پروژه مستقل نیستند.

Product Intake وظیفه دارد Product Knowledge را وارد سیستم کند.
Recommendation وظیفه دارد همان Knowledge را در Case مشتری مصرف کند.

Product Intake → Product Knowledge → Evidence / Verification → Knowledge Core → Recommendation → Customer Decision Support

نباید برای Recommendation یک Product Schema موازی ساخته شود.
نباید اطلاعات یک محصول در چند محل مستقل و ناسازگار نگهداری شود.

---

# 4. Current Baseline

طبق وضعیت فعلی Repository:
- Schema v1.1 مبنای پروژه است
- معماری Customer → Case → Evidence/Knowledge → Reasoning → Recommendation → Product/Inventory → Outcome موجود است
- Backend شامل Models، Repositories، Services و Interface است
- Interface در وضعیت آماده Review قرار دارد
- چهار محصول A–D در Work Registry به‌عنوان Frozen ثبت شده‌اند
- data/seed_products.json نیز در وضعیت Frozen ثبت شده است
- Scoring موجود مبنای این مرحله است
- EVIDENCE_MISSING در Project State به‌عنوان Active ثبت شده است

**توجه:** در Repository بین بعضی Snapshotها و اسناد، اختلاف وضعیت وجود دارد. بنابراین این Roadmap هیچ Gate متناقضی را به‌صورت خودکار حل‌شده فرض نمی‌کند.

---

# 5. Mission

## مأموریت اصلی

ایجاد اولین مسیر End-to-End که بتواند یک Customer Case را دریافت کند، اطلاعات مرتبط را جمع‌آوری یا بازیابی کند، Product Knowledge موجود را مصرف کند و یک Recommendation رتبه‌بندی‌شده و توضیح‌پذیر ارائه دهد.

Customer Question → HBI Understanding → Relevant Information → Candidate Products → Reasoning → Ranking → Explanation → Human Decision

---

# 6. What "Information Feeding" Means

Information Feeding فقط به معنای وارد کردن چند محصول جدید نیست. این مرحله سه نوع اطلاعات را به یکدیگر متصل می‌کند:

## A. Product Information
Identity, INCI, Actives, Claims, Use Cases, Usage, Limitations, Inventory

## B. Evidence / Knowledge Information
What is known? What is supported? What is unknown? What conflicts? What source supports the information?

## C. Customer / Case Information
Who is asking? What does the customer need now? What constraints matter? What preferences matter? What information is missing?

این سه بخش باید در Recommendation Flow به هم برسند.

---

# 7. Product Knowledge Feeding

## Identity
Brand, Product Name, Category, Variant, Size / Unit, Barcode where available

## Product Knowledge
INCI, Active Ingredients, Claims, Relevant Use Cases, Usage Instructions where needed, Known limitations where supported

## Evidence
Claim → Evidence → Verification Status

Claim نباید خودکار به‌عنوان Evidence تلقی شود.
Unknown باید Unknown باقی بماند.
Conflict باید قابل مشاهده باشد.

---

# 8. Customer Information Feeding

Customer Intake باید حداقلی و تصمیم‌محور باشد.

Skin / Hair Type, Current Need, Relevant Constraints, Known Sensitivities / Limitations, Previous Products, Budget, Size / Volume Preference, Brand / Market Preference, Other Decision-Relevant Preferences

**اصل مهم:** هر سؤال Customer باید یک دلیل تصمیم‌گیری داشته باشد.

---

# 9. Customer ≠ Case

Customer = Person
Case = Current Need / Current Decision Context

یک Customer می‌تواند چند Case داشته باشد. Recommendation باید بر اساس Case فعلی انجام شود.

---

# 10. Recommendation Flow

1. Load / Create Customer
2. Load existing relevant customer information
3. Create Current Case
4. Identify current need
5. Identify relevant constraints
6. Identify missing information where necessary
7. Access Product Knowledge
8. Access Evidence / Knowledge
9. Determine candidate eligibility
10. Eliminate clearly unsuitable candidates according to existing logic
11. Apply existing Reasoning / Matching logic
12. Apply existing Scoring
13. Rank products
14. Generate Explanation
15. Present Recommendation
16. Product Owner / Operator makes final decision
17. Record Outcome when supported by the existing architecture

---

# 11. No New Scoring System

این مرحله محل بازطراحی Scoring نیست. منطق موجود Scoring باید ابتدا پیدا، بررسی و مصرف شود.

Eligible Candidates → Existing Scoring → Ranking

---

# 12. Explanation

Recommendation باید بیشتر از یک Score باشد.

حداقل خروجی مفهومی:
Product, Rank, Score, Why Recommended, Relevant Customer Need, Satisfied Constraints, Evidence Used, Unknowns, Warnings

---

# 13. Human Decision

HBI تصمیم‌گیرنده نهایی نیست.

HBI: Analyze → Filter → Rank → Explain
Product Owner / Operator: Final Decision

این مرحله همچنان Decision Support است.

---

# 14. Team Structure for This Stage

Product Owner: مهندس وحید مقصودی
ChatGPT: Integration Architect / Reality Checker / Roadmap Owner
Qwen1: Technical Lead / Gate Coordination / Backend Direction
DeepSeek1: Backend Implementation / Services / API / Tests
Grok1: Knowledge / Data / QA / Operational Documentation
Grok2: Recommendation / Backend Execution / Integration / Technical Validation

---

# 15-20. Roles (Summary)

- **Product Owner:** تصمیم‌های نهایی، هدف تجاری، تأیید Pilot
- **ChatGPT:** Reality Check، Architecture Alignment، Integration، Duplicate Prevention، Gap Identification
- **Qwen1:** هماهنگی فنی، بررسی Backend، Gate Coordination، Technical Acceptance
- **DeepSeek1:** Backend Engineer، Services، Repositories، API، Tests
- **Grok1:** Knowledge / Data / QA، Product Knowledge، Evidence، Unknown/Conflict
- **Grok2:** Recommendation Service، Matching، Scoring Integration، Explanation، Pilot Execution

---

# 21. How the Team Works Together

PRODUCT OWNER → CHATGPT (Reality / Integration) → [QWEN1 (Technical Lead) + GROK1 (Knowledge/QA)] → [DEEPSEEK1 (Backend) + GROK2 (Recommendation)]

---

# 22. Execution Sequence

STEP 0 — Reality Baseline
STEP 1 — Identify Existing Pieces
STEP 2 — Gap Analysis (EXISTS / PARTIAL / MISSING / CONFLICT / UNKNOWN)
STEP 3 — Customer / Case Flow
STEP 4 — Knowledge Connection
STEP 5 — Candidate Selection
STEP 6 — Existing Scoring
STEP 7 — Explanation
STEP 8 — Vertical Slice
STEP 9 — QA / Red Team
STEP 10 — Final Reality Check

---

# 23. Communication Protocol

TASK / OWNER / CURRENT REALITY / WHAT EXISTS / WHAT IS MISSING / WHAT I CHANGED / FILES / TESTS / RESULT / KNOWN LIMITATIONS / NEXT ACTION

---

# 24. How New Team Members Should Enter

1. Read this document
2. Read HBI_MANIFEST
3. Read HBI_PROJECT_STATE
4. Read HBI_ARCHITECTURE
5. Read WORK-REGISTRY
6. Inspect relevant code
7. Identify existing work
8. State what is missing
9. Propose contribution
10. Execute after ownership is clear

---

# 25. What We Are NOT Doing Now

No new architecture
No parallel Product Schema
No new scoring algorithm
No unnecessary Schema redesign
No Knowledge Graph requirement
No Embedding requirement
No Self-Learning requirement
No complex multi-agent orchestration
No unnecessary UI rebuild
No bulk-import system unless a real need appears
No unnecessary re-testing of frozen A–D products

---

# 26. What We DO Need

1. Understand current reality
2. Feed missing useful information
3. Connect Customer to Case
4. Connect Case to Knowledge
5. Connect Knowledge to Recommendation
6. Reuse existing scoring
7. Produce ranking
8. Explain ranking
9. Run a real Vertical Slice
10. Capture outcome

---

# 27. First Pilot Target

چهار محصول A–D به‌عنوان Pilot Product Set موجودند.

Customer Case → A–D Product Set → Eligibility → Scoring → Ranking → Explanation

---

# 28. Feedback Loop

Recommendation → Human Decision → Outcome → Observation → Future Improvement

---

# 29. Success Criteria

Customer → Case → Relevant Information → Existing Product Knowledge → Candidate Selection → Existing Scoring → Ranking → Explanation → Human Decision

---

# 30. Definition of Done — Initial Version

- [ ] Current Customer flow identified
- [ ] Current Case flow identified
- [ ] Existing Product Knowledge identified
- [ ] Relevant Evidence path identified
- [ ] Recommendation path identified
- [ ] Existing Scoring identified and reused
- [ ] Candidate selection works
- [ ] Ranking works
- [ ] Explanation exists
- [ ] Unknowns / limitations are visible
- [ ] One Pilot Case runs end-to-end
- [ ] Test evidence exists
- [ ] Current implementation is documented
- [ ] Reality Check completed
- [ ] Remaining gaps are registered

---

# 31. Definition of "Not Done"

- Only product data was entered but Recommendation does not consume it
- Recommendation exists but Customer / Case information does not affect it
- Ranking exists but the scoring source is unclear
- Explanation exists but does not correspond to the actual decision
- A successful demo exists but the underlying implementation is not verified
- The team reports success without repository/code/test evidence

---

# 32. Scope Management

سؤال اصلی: **«برای اینکه اطلاعات موجود HBI واقعاً به تصمیم مشتری تبدیل شود، چه چیزی کم است؟»**

Required for Vertical Slice / Useful but not required / Future / Unrelated

---

# 33. Decision Hierarchy

Product Owner Decision → Architecture / Existing Project Decisions → Verified Repository Evidence → Team Proposal

---

# 34. Reality Principle

NO INVENTED STATE

- UNKNOWN: اگر چیزی را نمی‌دانیم
- CONFLICT: اگر دو سند با هم اختلاف دارند
- NOT VERIFIED: اگر کد وجود دارد ولی رفتار آن هنوز بررسی نشده
- VERIFIED: اگر با Code + Test + Artifact تأیید شده

---

# 35. Expected Deliverables

### Documentation
Information Feeding Roadmap, Customer → Recommendation implementation notes, Pilot result, Reality Check, Remaining Gap Registry

### Technical
Customer / Case integration, Recommendation integration, Scoring integration, Explanation integration, Tests, Pilot execution evidence

### Knowledge
Product Knowledge updates, Evidence updates where needed, Unknown / Conflict records

---

# 36. First Action From This Document

**هیچ‌کس هنوز Feature جدید نسازد.**

ابتدا یک Reality Baseline مخصوص این Stage تهیه شود.

تمرکز: CUSTOMER, CASE, PRODUCT, KNOWLEDGE, EVIDENCE, REASONING, RECOMMENDATION, SCORING, INTERFACE, TESTS

برای هر مورد: EXISTS / PARTIAL / MISSING / CONFLICT / NOT VERIFIED

---

# 37. First Execution Wave

WAVE 1: Reality Baseline
WAVE 2: Gap Map
WAVE 3: Customer / Case Integration
WAVE 4: Knowledge → Recommendation Integration
WAVE 5: Scoring + Ranking
WAVE 6: Explanation
WAVE 7: Pilot Vertical Slice
WAVE 8: QA / Red Team
WAVE 9: Final Reality Check
WAVE 10: Product Owner Decision

---

# 38. Final Direction From Product Owner

> HBI اکنون وارد مرحله «تغذیه اطلاعات» می‌شود.
>
> هدف این مرحله، اضافه‌کردن Featureهای متعدد یا بازطراحی پروژه نیست.
>
> هدف این است که اطلاعاتی که HBI در اختیار دارد، در یک جریان واقعی Customer → Case → Recommendation مصرف شود.
>
> معماری موجود و Schema فعلی مبنا هستند.
>
> چهار محصول A–D به‌عنوان Pilot Product Set مبنا هستند و برای شروع این مرحله دوباره ساخته یا بازطراحی نمی‌شوند.
>
> تیم ابتدا Reality موجود را بررسی می‌کند، سپس Gapهای واقعی را مشخص می‌کند و فقط همان Gapها را تکمیل می‌کند.
>
> Recommendation باید از Product Knowledge موجود استفاده کند، از Scoring موجود بهره ببرد، Ranking تولید کند و دلیل Recommendation را برای انسان قابل فهم کند.
>
> HBI تصمیم نهایی را به جای Product Owner نمی‌گیرد.
>
> فعلاً قوانین سختگیرانه جدید اضافه نمی‌کنیم. هدف این مرحله ایجاد یک مسیر روشن، عملی، قابل آزمایش و قابل توسعه است.
>
> معیار موفقیت این نیست که «کد بیشتری نوشته شده باشد».
>
> معیار موفقیت این است که **یک Case واقعی بتواند از Customer تا Recommendation و Explanation عبور کند.**

---

# 39. Current Mission in One Sentence

> **Feed the right information, connect it to the right Case, use the existing knowledge and scoring, produce an explainable recommendation, and prove the whole path with a real Pilot Case.**

---

# 40. Status

STAGE: INFORMATION FEEDING
MISSION: Customer → Case → Recommendation
ARCHITECTURE: Existing
SCHEMA: Existing / v1.1 baseline
PILOT: A–D
PRIMARY OUTPUT: End-to-End Vertical Slice
CURRENT FIRST ACTION: Reality Baseline
FINAL TARGET: Verified Customer → Case → Recommendation → Explanation Flow

---

**Document Status:** REGISTERED IN GITHUB
**Decision Authority:** Product Owner (مهندس مقصودی)
**Stage:** ACTIVE — Information Feeding Begins