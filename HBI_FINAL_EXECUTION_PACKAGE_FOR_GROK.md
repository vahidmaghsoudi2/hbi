# HBI — FINAL EXECUTION PACKAGE

## V1 Vertical Slice — Cross-AI Findings → Grok Execution

**Product Owner:** مهندس مقصودی
**Repository:** vahidmaghsoudi2/hbi
**Branch:** master
**Role:** Grok1 + Grok2 = Executor / Integrator
**Commit/Push:** فقط Grok
**Scope:** V1 — Vertical Slice
**Rule:** مسائل غیرمسدودکننده برای V2 کنار گذاشته شوند.

---

## 1. هدف

چهار Workstream قبلی بررسی شده‌اند. اکنون دیگر Audit جدید انجام ندهید؛ یافته‌های زیر را روی Reality فعلی Repository اعمال و مسیر Vertical Slice را واقعاً قابل اجرا کنید.

هدف:

Product → Identity → Evidence → Eligibility → Reasoning → Scoring → Recommendation → Persistence → API → E2E

باید واقعاً اجرا شود.

---

# 2. DeepSeek1 — Security + Test Infrastructure

### نتیجه کلی

Infrastructure تست و Security بررسی شده‌اند.

موارد مهم V1:

- SQLite lifecycle
- Session lifecycle
- Fixture isolation
- DB cleanup
- Authentication
- Authorization
- Pilot Token
- Rate Limiting
- Brute-force Lockout
- Audit Logging

### اصل اجرایی

مشکلات واقعی Test Infrastructure که باعث Failure یا WinError 32 می‌شوند اصلاح شوند.

خصوصاً:

- SQLite file locking
- Session cleanup
- Engine lifecycle
- Fixture isolation

اما:

- Scoring
- Seed
- Product A–D
- Evidence Claims

نباید تغییر کنند.

---

# 3. DeepSeek2 — Product Intake

### هدف

محصول جدید باید بتواند بدون تغییر کد مخصوص هر محصول وارد سیستم شود.

مسیر:

New Product → Identity → Validation → Review → Verification → Evidence → Recommendation Eligibility

اصل مهم:

DRAFT / REVIEW → NOT eligible → VERIFIED / ACTIVE → eligible for Recommendation

اما Lifecycle جدید را فقط در صورتی اضافه کن که Reality فعلی واقعاً به آن نیاز داشته باشد.

Contract را برای زیبایی معماری تغییر نده.

---

# 4. Qwen1 — Data Contract Reality

Qwen1 نتیجه داده: READY_WITH_FINDINGS

### موارد مهم

#### A — status

در Database وجود دارد، ولی در Python Product model فعلی دیده نشده است.

باید Runtime Reality اصلاح شود تا:

DB schema = SQLAlchemy Model = Repository = Service

در این مورد با هم سازگار باشند.

#### B — Inventory fields

Contract قبلی شامل:

- inventory_confirmation
- inventory_confirmation_date

است.

اما Reality فعلی ظاهراً inventory را از مسیر دیگری مدیریت می‌کند.

در V1 فیلد جدید فقط در صورتی اضافه شود که برای اجرای واقعی Recommendation ضروری باشد.

از ایجاد فیلد صرفاً برای تطبیق ظاهری Contract خودداری کن.

#### C — qa_verdict

Qwen1 یک Conflict مهم پیدا کرد:

identity_status = VERIFIED + qa_verdict = INVALID

ممکن است هنوز وارد Recommendation شود.

این باید در V1 اصلاح شود:

INVALID QA → NOT ELIGIBLE

بدون دستکاری Scoring Formula.

#### D — API Product creation/update

Qwen1 این دو مورد را Failure گزارش کرده:

- Product creation API
- Identity status update API

اینها فقط اگر برای Vertical Slice واقعی Product Intake لازم باشند اصلاح شوند.

---

# 5. GPT-1 — Recommendation Reality Audit

GPT-1 Repository را مستقیماً بررسی کرد.

### Finding قطعی

RecommendationService این را صدا می‌زند:

self.product_repo.find_verified()

اما ProductRepository فعلی چنین متدی ندارد.

در Repository فعلی متدهایی مانند:

- find_by_brand()
- find_by_identity_status()
- find_by_qa_verdict()
- get_with_inventory()

وجود دارند، ولی find_verified() وجود ندارد.

این V1 BLOCKER است.

### اقدام

این mismatch را با کمترین تغییر معماری اصلاح کن.

ترجیح:

Repository → verified products → RecommendationService

نه اینکه منطق Repository را در Service تکرار کنی.

---

# 6. Scoring — ABSOLUTELY FROZEN

این قسمت را تغییر نده:

- scoring.py
- scoring_constants.py

وزن‌ها:

- Need = 0.50
- Evidence = 0.30
- Inventory = 0.20

Threshold:

- ELIGIBLE >= 0.70
- NEEDS_REVIEW >= 0.50
- INELIGIBLE < 0.50

Hard Gate:

- Evidence <= 0
- Inventory <= 0

منطق Scoring نباید برای حل Conflictهای Contract تغییر کند.

---

# 7. Reasoning Engine

Reality فعلی:

ReasoningEngine → ConflictAnalyzer → ClaimValidator → MatchScoringEngine

ReasoningResult: COMPUTED_ONLY

است و نباید مستقیماً DB را تغییر دهد.

این معماری را حفظ کن.

---

# 8. Frozen Assets

این موارد ABSOLUTELY FROZEN هستند:

- data/seed_products.json
- Product A, B, C, D
- Existing Evidence Claims
- app/reasoning/scoring.py
- app/reasoning/scoring_constants.py
- Recommendation Formula
- Thresholds
- Hard Gate

اگر تغییر آنها برای عبور تست لازم شد: STOP و آن را Conflict اعلام کن.

---

# 9. تست نهایی V1

پس از اصلاحات، این مسیر باید واقعاً اجرا شود:

Seed Product A–D → Evidence → Customer → Case → RecommendationService → Eligibility → Reasoning → Scoring → Recommendation Persistence → API → Pilot Authentication → E2E

سناریوهای ضروری:

### PASS

VERIFIED product + valid evidence + available inventory + final_score >= 0.70 → ELIGIBLE

### PASS

Evidence missing → Hard Gate → NEEDS_REVIEW

### PASS

Inventory unavailable → Hard Gate → NEEDS_REVIEW

### PASS

identity_status != VERIFIED → NOT eligible

### PASS

qa_verdict = INVALID → NOT eligible

### PASS

final_score < 0.50 → INELIGIBLE

---

# 10. Test Infrastructure Requirement

تست‌ها نباید به دلیل:

- WinError 32
- SQLite locked
- open Session
- open Engine
- fixture contamination

خراب شوند.

Cleanup باید تضمین کند:

- Session.close()
- Engine disposal
- SQLite file release
- DB cleanup

قبل از حذف فایل انجام شود.

---

# 11. Execution Protocol

Grok1/Grok2 اکنون اختیار اجرای این بسته را دارند.

ترتیب:

READ CURRENT REALITY → BACKUP → MINIMAL CODE CHANGES → TARGETED TESTS → FULL V1 TESTS → FROZEN FILE VERIFICATION → E2E → FINAL REALITY CHECK → COMMIT → PUSH

### مهم

قبل از Commit:

- git diff
- git status
- Frozen-file verification
- Test result

باید بررسی شود.

---

# 12. Commit Rule

فقط اگر:

- V1 tests PASS
- AND Frozen files unchanged
- AND No unresolved V1 blocker

آنگاه: COMMIT + PUSH مجاز است.

اگر Failure باقی ماند: NO COMMIT + NO PUSH

---

# 13. Final Deliverable

Grok باید در پایان یک گزارش تولید کند:

HBI_FINAL_V1_EXECUTION_REPORT.md

شامل:

- HEAD before
- HEAD after
- Files changed
- Tests before
- Tests after
- Frozen verification
- Remaining findings
- V1 blockers
- Commit SHA
- Push status
- FINAL VERDICT

Verdict فقط یکی از:

- V1 READY
- V1 READY_WITH_FINDINGS
- V1 BLOCKED

---

## دستور نهایی به Grok

دیگر این بسته را به یک AI دیگر ارجاع نده.

این مرحله، مرحله‌ی Execution است.

DO NOT RE-DESIGN
DO NOT RE-AUDIT
DO NOT CHANGE FROZEN SCORING
DO NOT CHANGE SEED
DO NOT CHANGE EVIDENCE CLAIMS

IMPLEMENT
TEST
VERIFY
COMMIT
PUSH

هدف: عبور واقعی HBI از این مرحله و رساندن Vertical Slice V1 به وضعیت قابل قبول است.