# HBI — INFORMATION FEEDING MASTER REGISTER

**Project:** HBI — Maqsoudi Gallery
**Repository:** vahidmaghsoudi2/hbi
**Product Owner:** مهندس وحید مقصودی
**Workstream:** INFORMATION FEEDING
**Primary Flow:** Customer → Case → Recommendation
**Archive Created:** 20260828_010017

---

# 1. PURPOSE

این پرونده، Master Archive جریان Information Feeding است.

هدف:
- حفظ تاریخچه مأموریت‌ها
- حفظ گزارش‌های اعضای تیم
- ثبت تصمیم‌ها
- ثبت تضادها
- ثبت وضعیت تحویل‌ها
- ثبت شواهد Repository
- جلوگیری از گم‌شدن کارهای انجام‌شده یا ادعاشده

اصل مدیریتی:

> اگر تحویل اثبات نشده باشد، CLOSED محسوب نمی‌شود.

> اگر Commit پیدا نشود، ادعای Commit به‌عنوان VERIFIED ثبت نمی‌شود.

> اگر وضعیت نامعلوم باشد، UNKNOWN / NOT VERIFIED باقی می‌ماند.

> هیچ گزارش قبلی، حتی گزارش اشتباه، از تاریخچه حذف نمی‌شود.

---

# 2. OFFICIAL ROADMAP

سند رسمی موجود در Repository:

HBI_INFORMATION_FEEDING_ROADMAP.md

Stage:
Information Feeding

Primary Direction:
Customer → Case → Recommendation

Architecture:
Existing

Schema:
v1.1 baseline

Pilot:
Products A-D (Frozen)

Scoring:
Existing / No redesign

Qwen1:
APPROVED — Compatible with existing architecture

---

# 3. ARCHITECTURAL DIRECTION

Customer
→ Case / Current Need
→ Relevant Customer Information
→ Product Knowledge
→ Evidence / Knowledge
→ Eligibility / Elimination
→ Reasoning
→ Existing Scoring
→ Recommendation
→ Explanation
→ Product Owner Decision
→ Outcome

اصل:
HBI سیستم تصمیم‌گیر نهایی نیست؛ Decision Support است.

HBI:
Analyze → Filter → Rank → Explain

Human / Product Owner:
Final Decision

---

# 4. TEAM

## Product Owner
مهندس وحید مقصودی

## ChatGPT
Integration Architect
Reality Checker
Roadmap Owner
Team Mirror / Management of this Workstream

## Qwen1
Technical Lead
Gate Coordination
Knowledge / Evidence Audit
Acceptance

## DeepSeek1
Backend Engineer
Services
Repositories
API
Tests
Implementation Verification

## Grok1
Knowledge / Data / QA
Product Knowledge
Evidence
Unknown / Conflict
Operational Documentation

## Grok2
Recommendation
Backend Execution
Integration
Technical Validation
Red Team

NOTE:
در وضعیت فعلی Conversation گزارش شده که Grok1 و Grok2 دیگر در دسترس نیستند.
گزارش‌های قبلی آنها باید به‌عنوان Historical Evidence حفظ شوند.

---

# 5. MANAGEMENT RULE

هر مأموریت باید دارای این وضعیت‌ها باشد:

OPEN
IN_PROGRESS
DELIVERED
VERIFIED
BLOCKED
CLOSED

تحویل صرفاً با پیام «انجام شد» بسته نمی‌شود.

برای CLOSED شدن باید حداقل Evidence قابل بررسی وجود داشته باشد:
- Commit
- File
- Test
- Artifact
- یا Repository evidence

---

# 6. WAVE HISTORY

WAVE 1:
Reality Baseline

WAVE 2:
Gap / Vertical Slice Implementation

WAVE 3:
Knowledge / Evidence Audit

سپس:
QA / Red Team
Final Reality Check
Product Owner Decision

---

# 7. DEEPSEEK1 WAVE 1

DeepSeek1 گزارش کرد:

WAVE1_REALITY_RECONCILIATION.md

یافته‌های اصلی گزارش:
- Customer VERIFIED
- Case VERIFIED
- Recommendation Request VERIFIED
- Candidate Products VERIFIED
- Product Model VERIFIED
- Product Knowledge موجود
- Evidence Model/Service موجود
- Evidence consumption در scoring نیازمند verification
- Explanation در ابتدا missing
- DRAFT filtering gap
- Tests ناقص

---

# 8. DEEPSEEK1 CLAIMED WAVE 2

DeepSeek1 بعداً گزارشی ارائه کرد که مدعی بود:

- DRAFT filtering implemented
- Explanation DTO implemented
- reasoning capture implemented
- DRAFT test added
- Needs Review test added
- idempotency added
- 12 tests passed
- Commit:
  d3f8a9c2b1e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8

IMPORTANT:
این Commit در Repository پیدا نشد.

بنابراین این گزارش:

REPORTED
NOT VERIFIED

و Wave 2 بر اساس Repository Reality بسته نشد.

---

# 9. ACTUAL DELIVERY VERIFICATION

در بررسی بعدی DeepSeek1:

Actual local HEAD reported:
9fd3328eff1d73a0aaf03786a5b54e539acaa2e1

Reported GitHub HEAD:
8439a3fbb8c983e80b77aa807624f0c805be1cd4

Reported Wave 2 SHA:
d3f8a9c2b1e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8

Verdict:
CORRECTIVE ACTION REQUIRED

Reason:
Wave 2 claimed implementation was not verified in Repository.

---

# 10. QWEN1 KNOWLEDGE / EVIDENCE AUDIT

Qwen1 reported:

Product Model:
VERIFIED

Product Knowledge:
PARTIAL

Evidence Model:
VERIFIED

Evidence → Reasoning:
CONFLICT / NOT VERIFIED

Main finding:
Recommendation Service did not demonstrably retrieve Evidence for each candidate and pass real evidence information into scoring.

Qwen1 identified:

1. Evidence must be actively consumed.
2. DRAFT / non-active products must be hard-gated.
3. Recommendation explanation must correspond to actual reasoning.

Qwen1 verdict:
READY FOR DEEPSEEK1 IMPLEMENTATION

No new schema.
No new scoring.
No invented data.

---

# 11. IMPORTANT REPOSITORY CONFLICT

A later reconciliation identified:

RecommendationService approximately line 71:
an intended VERIFIED + ACTIVE filter existed.

But approximately line 81:
products = self.product_repo.find_verified()

Reality:
find_verified() does NOT exist on ProductRepository.
It does NOT exist on BaseRepository.

Therefore:
the intended filter is overwritten by an unconditional call to a missing method.

Runtime consequence:
AttributeError during recommendation generation.

Status:
REAL EXECUTABLE DEFECT
NOT RESOLVED

---

# 12. QA_VERDICT CONFLICT

The Information Feeding documentation identified:

qa_verdict = INVALID

was not clearly excluded from candidate selection.

This remains a candidate-filtering concern requiring verified implementation evidence.

---

# 13. PRODUCT LIFECYCLE

The intended lifecycle is:

DRAFT → ACTIVE

DRAFT products must not enter the Recommendation candidate pool.

The project explicitly avoids assuming that a newly entered product is recommendation-ready before QA.

---

# 14. PILOT

Pilot Product Set:

Product A
Product B
Product C
Product D

These are recorded as Frozen Pilot data.

Rules:
- Do not alter frozen seed data without explicit authorization.
- Do not invent product information.
- Do not redesign scoring to compensate for missing information.

---

# 15. SCORING

Existing scoring is the baseline.

Known thresholds:

Hard Gate:
0.50

Eligible:
0.70

Range:
0.50–0.69
→ NEEDS_REVIEW

Important:
No new scoring algorithm is authorized merely to solve integration problems.

---

# 16. EXPLANATION

Required conceptual output:

Product
Rank
Score
Why Recommended
Relevant Customer Need
Satisfied Constraints
Evidence Used
Unknowns
Warnings

Explanation must reflect actual decision logic.

A fabricated explanation is not acceptable.

---

# 17. TEST REALITY

A local full pytest run produced:

ModuleNotFoundError:
No module named 'app.services.product_intake_service'

Failing test:
tests/test_product_intake_service.py

Therefore:
full test suite could not complete collection.

This must remain recorded as actual evidence.

It must not be silently converted to PASS.

---

# 18. GIT STATUS REALITY

The local repository contained numerous untracked artifacts, including:

.hbi_executor_*
.hbi_intake_impl_*
.hbi_minimal_intake_*
.hbi_vertical_slice_*
HBI_* reports
TASK016_RECON_RAW.txt
frontend/package-lock.json
hbi_auto_check.py
tests/test_product_intake_service.py
uvicorn_startup.log.err
and additional files.

These must be archived before any cleanup decision.

NO DELETE operation is authorized by this archive.

---

# 19. VERIFIED / NOT VERIFIED PRINCIPLE

VERIFIED:
supported by actual repository/code/test/artifact evidence.

REPORTED:
someone claimed it.

NOT VERIFIED:
claim exists but evidence is insufficient.

CONFLICT:
two pieces of evidence disagree.

UNKNOWN:
insufficient information.

These labels must never be collapsed into one another.

---

# 20. CURRENT MANAGEMENT POSITION

No new implementation task should be issued merely because a previous task was reported complete.

First:
1. Locate delivery.
2. Verify repository.
3. Verify tests.
4. Reconcile conflicts.
5. Close or reopen task.
6. Only then issue next mission.

---

# 21. CURRENT OPEN ISSUES

OPEN / NOT CLOSED:

- Wave 2 implementation
- Evidence → Recommendation active integration
- Product candidate filtering
- DRAFT → ACTIVE enforcement
- qa_verdict handling
- Explanation verification
- Product Intake test/module mismatch
- Grok1 historical reconciliation
- Grok2 historical reconciliation
- Complete team archive
- Final Gate

---

# 22. HISTORICAL PRESERVATION

No previous report should be deleted because it was later found incorrect.

Example:

DeepSeek1 claimed:
d3f8a9c2...

Repository reality:
SHA not found.

Correct archival treatment:

REPORTED → NOT FOUND → NOT VERIFIED

NOT:
DELETE

---

# 23. OFFICIAL NEXT MANAGEMENT PRINCIPLE

Before issuing new engineering work:

MASTER ARCHIVE
→ Repository reconciliation
→ Task ledger
→ Delivery verification
→ Gate status
→ Next command

---

# 24. SOURCE PRIORITY

1. Verified Repository Evidence
2. Verified Test Evidence
3. Verified Git Commit / Artifact
4. Approved Project Documents
5. Team Reports
6. Chat history
7. Unverified claims

When sources conflict:
do not guess.
Record CONFLICT and investigate.

---

# 25. ARCHIVE STATUS

This file is an archival register.

It does not itself declare unresolved work CLOSED.

It preserves both:
- what was reported
- what was actually verified

END OF MASTER REGISTER