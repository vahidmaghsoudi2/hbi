# HBI — Execution Ledger V1

**Document ID:** `HBI-LEDGER-EXEC-001`  
**Title:** HBI Execution Ledger V1  
**Version:** V1.0  
**Status:** ACTIVE (operational dashboard — not a Contract)  
**Date opened:** 2026-09-09  
**Baseline master (at open):** `90788e854e8205c1493f2dd41d876a1521f20fa7`  
**Owner:** Product Owner  
**Strategic reference:** `HBI-ROADMAP-CORE-001` (`HBI_INTELLIGENT_CORE_ROADMAP_V1.md`)

---

## قانون سند

| قانون | متن |
|--------|------|
| نقش | داشبورد زنده اجرا — **نه** مجوز توسعه |
| Reality | فقط وضعیت قابل ارجاع به Repository / Evidence |
| NO ASSUMPTION | پیشرفت، مالک، یا قابلیت حدس زده نمی‌شود |
| Authorization | هر اقدام: **Authorized** یا **Not Authorized** |
| Blocker | Gate/تصمیم تأییدنشده = Blocker ثبت‌شده؛ عبور فرضی ممنوع |

**وضعیت‌های مجاز:**  
`DONE` · `IN PROGRESS` · `BLOCKED` · `NOT STARTED` · `NOT AUTHORIZED`

**تفکیک مراجع:**

```
Roadmap     = جهت و فازهای کلان
Ledger      = وضعیت زنده و اقدام بعدی
Repository  = واقعیت
Evidence    = اثبات
```

---

## Snapshot فعلی

| Field | Value |
|--------|--------|
| **Current Phase** | **F0 — HBI CORE BASELINE & REALITY AUDIT** |
| **Current Gate** | F0 Reality Audit / Capability Map |
| **Current Status** | **NOT STARTED** (F0 **NOT COMPLETED**) |
| **Implementation Authorization** | **NOT AUTHORIZED** for new core features |
| **Roadmap on master** | V1.0 merged (`90788e85…`); V1.1 amendment pending merge of this PR if applicable |
| **Last Ledger update** | 2026-09-09 — initial open |

---

## Completed

| Item | Evidence | Notes |
|------|----------|--------|
| Roadmap V1.0 registered & merged | PR #39 · SHA `90788e85…` · `HBI-ROADMAP-CORE-001` | Direction locked; **not** F0 completion |
| (other items) | — | Only add with Repository Evidence |

---

## In Progress

| Item | Owner | Notes |
|------|--------|--------|
| — | — | None claimed without Evidence |

---

## Blocked

| Item | Blocker | Required to unblock |
|------|---------|---------------------|
| Core Implementation (diagnosis chain, new scoring, etc.) | F0 not completed; no PO authorization for implementation package | Complete F0 + explicit PO authorize named work |
| Treating Roadmap/Ledger as build license | Governance rule | Keep Authorization = NOT AUTHORIZED until PO says otherwise |

---

## Open Gaps (pre-F0 — not a substitute for F0)

تا تکمیل F0، فهرست Gap **کامل اعلام نمی‌شود**.  
فقط یادآوری غیرحدسی از کار قبلی تیم (نیازمند تأیید مجدد در F0):

| Topic | Prior note | F0 required? |
|--------|------------|--------------|
| Recommendation input score Contract (need/evidence/inventory) | ADR proposed; PR #36 HOLD class issues | Yes — status must be Reality-checked |
| Factor Discovery round (team lists) | Discussion / not formal Contract | Optional input to later phases; not F0 done |
| Capability Map with Relation/Decision Use columns | **Missing as formal F0 deliverable** | **Yes — primary F0 output** |

---

## Verification Status

| Deliverable | Status |
|-------------|--------|
| F0 Capability Map | **NOT STARTED** |
| F0 Gap List | **NOT STARTED** |
| F0 Execution Package | **NOT STARTED** |
| Independent Verification of F0 | **NOT STARTED** |

---

## Next Authorized Action

| Field | Value |
|--------|--------|
| **Action** | انجام **F0 Reality Audit** کامل روی Repository واقعی |
| **Outputs** | Capability Map (ستون‌ها: Capability/Data · Status · Owner · Relation · Decision Use · Evidence) + Gap List + Execution Package اولیه |
| **Authorized** | **YES** — audit/documentation only |
| **Not authorized** | Implementation، تغییر `calculate()`، فرمول/وزن جدید، Merge خودسرانه PRهای HOLD |
| **Owner** | To be assigned by PO when starting F0 execution |

---

## Change log

| Date | Event | Result |
|------|--------|--------|
| 2026-09-09 | Ledger opened with F0 = NOT COMPLETED | ACTIVE |
| 2026-09-09 | Roadmap V1.1 principles (traceability + ledger split) drafted | Pending merge |

---

**END OF HBI-LEDGER-EXEC-001**
