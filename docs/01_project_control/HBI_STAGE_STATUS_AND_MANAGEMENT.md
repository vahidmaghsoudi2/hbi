# HBI Stage Status & Executive Management

**Canonical Status File**  
**Authority:** Product Owner (وحید) + Executive Manager (Grok)  
**Created:** 2026-11-20  
**Last updated:** 2026-11-20  
**Linked to:** [Issue #403 – HBI Unified Roadmap](https://github.com/vahidmaghsoudi2/hbi/issues/403)

---

## 1. Current Stage Snapshot (Quick Read)

| Stage | Title | Status | Notes |
|-------|-------|--------|-------|
| 1 | تثبیت مبنا و قرارداد دانش محصول | PARTIAL / Needs alignment | Base work done; formal status must match Issue #403 |
| 2 | تکمیل چرخه عمر محصول | **ACCEPTED** | PR #599 (unmerged) |
| 3 | ساختار مدیریت محصول و مستندات | **ACCEPTED** | PR #598 (unmerged) |
| 4 | پیاده‌سازی مدیریت محصول در Home Page | **IN PROGRESS** | PR #647 – Browser Proof currently failing (9 failures) |
| 5–16 | Snapshot هفت محصول → تحویل عملیاتی | **NOT STARTED** | Locked until Stage 4 is ACCEPTED |

**Current focus (non-negotiable):** Close Stage 4 only.

---

## 2. Executive Management Regime (from 2026-11-20)

- **Product Owner (PO):** وحید  
- **Executive Project Manager:** Grok  
- **Execution member:** GPT (and other agents as assigned)

### Core Rules
1. Every stage ends with a **large, executable product deliverable**, not reports or documentation alone.
2. Grok gives **decisive, large, professional orders**. No small busy-work. No tolerance for tangents.
3. GPT is kept under strict scope control. Side quests and premature stage jumping are forbidden.
4. Status claims must be backed by real GitHub evidence (PR, commit SHA, CI/browser run links).
5. No merge to master, no deploy, no schema/migration/API change outside approved scope without explicit PO permission.
6. When PO asks “اکنون نوبت چه مرحله‌ای است؟”, the Executive Manager must answer from this file + live GitHub state in one clear, decisive paragraph.

---

## 3. Stage Definitions (Summary)

- **Stage 4 (current):** Full product-management flow on Home Page (List → Create/Open Dossier → Knowledge/Evidence/QA view → Edit → back to List). Browser-proof required.
- **Stage 5:** Snapshot of seven products with stable IDs and current state.
- **Stage 6–7:** Research finalization + operational ProductKnowledge for the seven products.
- **Stage 8:** PO approval + inventory readiness for the seven.
- **Stage 9–14:** Consultation form, Skin Problem Bank P01–P61, ProductProblemLink, Candidate Retrieval, Explainable Suitability, Customer output template.
- **Stage 15–16:** End-to-end consultation proof for the seven products + operational handover.

Full definitions remain in Issue #403.

---

## 4. How Status Is Reported to PO

Whenever PO asks for current stage:

1. Read this file.
2. Cross-check live GitHub (PR #647 state, latest browser-proof run, Issue #403 comments).
3. Answer in this exact style:

> **وضعیت فعلی:** Stage X — STATUS  
> **مراحل تمام‌شده (ACCEPTED):** …  
> **مرحله در حال اجرا:** …  
> **شواهد کلیدی:** لینک PR / commit / CI run  
> **اقدام بعدی اجباری:** …

No long essays. No “almost done”.

---

## 5. Update Protocol

- This file is the single source of truth for stage status under the new management.
- After every material change (Stage 4 DONE/ACCEPTED, start of Stage 5, etc.) this file must be updated via PR.
- Executive Manager (Grok) is responsible for keeping the snapshot accurate.

---

**End of status file.**
