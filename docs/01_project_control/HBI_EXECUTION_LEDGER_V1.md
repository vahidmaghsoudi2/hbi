# HBI — Execution Ledger V1

**Document ID:** `HBI-LEDGER-EXEC-001`  
**Title:** HBI Execution Ledger V1  
**Filename:** `HBI_EXECUTION_LEDGER_V1.md`  
**Version:** V1.0  
**Status:** ACTIVE (operational dashboard — **not** a Contract; **not** an implementation license)  
**Date opened:** 2026-09-09  
**Baseline master (at open):** `90788e854e8205c1493f2dd41d876a1521f20fa7`  
**Owner:** Product Owner  
**Strategic reference:** `HBI-ROADMAP-CORE-001` — `docs/01_project_control/HBI_INTELLIGENT_CORE_ROADMAP_V1.md` (on master)

---

## نقش سند (تفکیک مراجع)

| مرجع | نقش |
|------|------|
| **Roadmap** (`HBI-ROADMAP-CORE-001`) | مسیر و جهت‌گیری کلان |
| **Execution Ledger** (این سند) | وضعیت زنده اجرای مسیر |
| **Repository** | مرجع واقعیت |
| **Evidence / Tests / Verification** | مرجع اثبات |

هیچ‌کدام جای دیگری را نمی‌گیرد.

**قانون مجوز:** ایجاد یا به‌روزرسانی Roadmap یا Ledger **به‌تنهایی مجوز Implementation نیست.**

---

## قوانین عملیاتی

| قانون | متن |
|--------|------|
| Reality only | فقط وضعیت با ارجاع Repository / Evidence |
| NO ASSUMPTION | پیشرفت، قابلیت، مالک، یا نتیجه حدس زده نمی‌شود |
| Authorization | هر اقدام: **Authorized** یا **Not Authorized** |
| Blocker | Gate/تصمیم تأییدنشده = Blocker؛ عبور فرضی ممنوع |

**وضعیت‌های مجاز:** `DONE` · `IN PROGRESS` · `BLOCKED` · `NOT STARTED` · `NOT AUTHORIZED`

---

## Snapshot فعلی (Reality-based)

| Field | Value |
|--------|--------|
| **Current Phase** | **F0 — HBI CORE BASELINE & REALITY AUDIT** |
| **Current Gate** | F0 Reality Audit |
| **Current Status** | **NOT STARTED** |
| **F0** | **NOT COMPLETED** |
| **Implementation Authorization** | **NOT AUTHORIZED** |
| **Roadmap on master** | Yes — `HBI-ROADMAP-CORE-001` @ `90788e85…` (V1.0) |
| **This Ledger on master** | **NO** until this registration is merged |
| **Last Ledger update** | 2026-09-09 — initial registration (defect fix: file was missing on master) |

---

## Completed (with Evidence only)

| Item | Evidence |
|------|----------|
| Roadmap V1.0 on master | PR #39 · commit `90788e854e8205c1493f2dd41d876a1521f20fa7` · path `docs/01_project_control/HBI_INTELLIGENT_CORE_ROADMAP_V1.md` |

*Note: Roadmap registration ≠ F0 completion.*

---

## In Progress

| Item | Notes |
|------|--------|
| — | None claimed |

---

## Blocked

| Item | Blocker |
|------|---------|
| Core / diagnosis Implementation | F0 not completed; no PO-authorized implementation package |
| Using Ledger/Roadmap as build license | Explicit governance rule |

---

## Open Gaps

فهرست Gap کامل **فقط پس از F0 Reality Audit** تولید می‌شود.  
تا آن زمان: **Gap List = NOT STARTED** (حدس زده نمی‌شود).

---

## Verification Status (F0 deliverables)

| Deliverable | Status |
|-------------|--------|
| Reality Audit (repository) | **NOT STARTED** |
| Capability Map | **NOT STARTED** |
| Gap List | **NOT STARTED** |
| Relation / Decision-Use Map | **NOT STARTED** |
| First Execution Package | **NOT STARTED** |
| Independent Verification of F0 | **NOT STARTED** |

---

## Next Authorized Action

| Field | Value |
|--------|--------|
| **Action** | Reality Audit واقعی Repository → Capability Map → Gap List → Relation / Decision-Use Map → First Execution Package |
| **Authorized** | **YES** — documentation / audit only |
| **Not authorized** | Implementation؛ تغییر production code؛ تغییر `calculate()`؛ وزن/فرمول جدید؛ Merge خودسرانه |
| **Owner** | Assign by PO when F0 execution starts |

---

## Change log

| Date | Event | Result |
|------|--------|--------|
| 2026-09-09 | Ledger file created to fix master absence | Pending merge to master |

---

**END OF HBI-LEDGER-EXEC-001**
