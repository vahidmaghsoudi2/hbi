# HBI — Execution Ledger V1

**Document ID:** `HBI-LEDGER-EXEC-001`  
**Title:** HBI Execution Ledger V1  
**Filename:** `HBI_EXECUTION_LEDGER_V1.md`  
**Version:** V1.1  
**Status:** ACTIVE (operational dashboard — **not** a Contract; **not** an implementation license)  
**Date opened:** 2026-09-09  
**Baseline master (at open):** `90788e854e8205c1493f2dd41d876a1521f20fa7`  
**Owner:** Product Owner  
**Strategic reference:** `HBI-ROADMAP-CORE-001` — `docs/01_project_control/HBI_INTELLIGENT_CORE_ROADMAP_V1.md`

---

## نقش سند (تفکیک مراجع)

| مرجع | نقش |
|------|------|
| **Roadmap** (`HBI-ROADMAP-CORE-001`) | مسیر و جهت‌گیری کلان |
| **Execution Ledger** (این سند) | وضعیت زنده اجرای مسیر |
| **Repository** | مرجع واقعیت |
| **Evidence / Tests / Verification** | مرجع اثبات |

**قانون مجوز:** ایجاد Roadmap، Ledger، یا **PO ACCEPTED برای Domain Contract** به‌تنهایی **مجوز Implementation نیست.**

---

## قوانین عملیاتی

| قانون | متن |
|--------|------|
| Reality only | فقط وضعیت با ارجاع Repository / Evidence |
| NO ASSUMPTION | پیشرفت حدس زده نمی‌شود |
| Authorization | هر اقدام: **Authorized** یا **Not Authorized** |
| Blocker | Gate تأییدنشده = Blocker |

**وضعیت‌های مجاز:** `DONE` · `IN PROGRESS` · `BLOCKED` · `NOT STARTED` · `NOT AUTHORIZED`

---

## Snapshot فعلی

| Field | Value |
|--------|--------|
| **Current Phase (core path)** | F0 Reality Audit still required before broad core implementation |
| **WP-CORE-01 Domain Contract** | **PO ACCEPTED** (see `HBI-PO-DEC-WP-CORE-01-001`) |
| **WP-CORE-01 Implementation** | **NOT AUTHORIZED** |
| **WP-CORE-01 Next Authorized Step** | **Implementation Design** (no code) |
| **Implementation Authorization (general core)** | **NOT AUTHORIZED** |
| **Roadmap on master** | Yes — `HBI-ROADMAP-CORE-001` @ `90788e85…` |
| **Last Ledger update** | 2026-09-09 — PO decision WP-CORE-01 recorded |

---

## WP-CORE-01 (official)

| Field | Status |
|--------|--------|
| Domain Contract v1 | **PO ACCEPTED** |
| Implementation | **NOT AUTHORIZED** |
| Model / Migration / API / DTO / DB | **NOT AUTHORIZED** |
| Recommendation / Scoring / Weighting / Ranking / Eligibility | **Out of scope** |
| Next Authorized Step | **Implementation Design** |
| Decision record | `docs/03_decision_log/HBI-PO-DEC-WP-CORE-01-001.md` |

**PO ACCEPTED ≠ Implementation Authorized.**

---

## Completed (Evidence only)

| Item | Evidence |
|------|----------|
| Roadmap V1.0 on master | PR #39 · `90788e854e8205c1493f2dd41d876a1521f20fa7` |
| PO decision WP-CORE-01 Domain Contract accepted | This registration · `HBI-PO-DEC-WP-CORE-01-001` |

---

## In Progress

| Item | Notes |
|------|--------|
| — | None claimed as code/implementation |

---

## Blocked

| Item | Blocker |
|------|---------|
| WP-CORE-01 Implementation | Awaiting Implementation Design + **explicit PO Implementation Authorization** |
| General core feature build | F0 / design gates; no blanket authorization |

---

## Next Authorized Action

| For | Action | Authorized? |
|-----|--------|-------------|
| **WP-CORE-01** | Implementation Design package (Reality Audit on current master → Model/Impact/Migration/API/Test plan/Self-Critique/PO decisions) | **YES — design/docs only** |
| **WP-CORE-01** | Any code, migration, API, DTO, DB | **NO** |
| **Scoring / Ranking / Eligibility** | Changes under this WP | **NO — out of scope** |

---

## Change log

| Date | Event | Result |
|------|--------|--------|
| 2026-09-09 | Ledger opened (F0 path) | Draft / pending prior PRs |
| 2026-09-09 | PO: WP-CORE-01 Domain Contract = PO ACCEPTED; Implementation = NOT AUTHORIZED | Recorded |

---

**END OF HBI-LEDGER-EXEC-001**
