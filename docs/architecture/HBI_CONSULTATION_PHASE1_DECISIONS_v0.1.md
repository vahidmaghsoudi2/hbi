# HBI Consultation — Phase 1 Decision Addendum v0.1

| Field | Value |
|-------|--------|
| Status | **DRAFT — CORRECTED AFTER INDEPENDENT REVIEW — AWAITING RE-ACCEPTANCE** |
| Mission | Issue #212 — HBI-CONSULTATION-PHASE1-DECISIONS-001 |
| Parent Framework | Issue #208 |
| Parent Contract | `docs/architecture/HBI_CONSULTATION_MINIMAL_CONTRACT_v0.1.md` (merged via #210) |
| Evidence Master baseline (entry) | `849b7ac0b5105526e65ea78a05bbee1f9c5f7269` |
| Implementation | **NOT AUTHORIZED by this document** |
| Schema / API / UI / Scoring / ProfileFact→Rec | **NOT AUTHORIZED** |

This addendum **does not replace** the Minimal Contract. It resolves OPEN items where repository evidence permits, and keeps residual OPEN/DEFERRED explicit.

---

## 1. Reality re-audit (current Master)

| Area | Classification | Evidence |
|------|----------------|----------|
| Master tip at audit start | **FACT** = `849b7ac0b5105526e65ea78a05bbee1f9c5f7269` | `git rev-parse` / Issue #212 |
| Contract v0.1 on master | **FACT** | `docs/architecture/HBI_CONSULTATION_MINIMAL_CONTRACT_v0.1.md` |
| Customer + legacy profile fields | **FACT** | `app/models/customer.py` |
| ProfileFact model/service | **FACT** | `profile_fact.py`, `profile_fact_service.py` |
| ProfileFact read by Recommendation | **FACT: not used** | no ProfileFact usage in `recommendation_service.py` / recommendations router |
| Rec profile merge | **FACT** | `recommendations.py` `_merge_profile_context` + `CustomerService.build_recommendation_profile` → concerns / skin / hair / scalp surfaces into `concerns` string |
| Case model | **FACT** | `case.py` including `identified_needs`, `evidence_gaps` columns |
| Writers of `Case.identified_needs` under `app/` | **FACT: none found** | repo search — only column definition |
| Writers of `Case.evidence_gaps` under `app/` | **FACT: none found** | only column + in-memory `decision_state["evidence_gaps"]=[]` |
| decision_state factors | **FACT** | `_build_decision_state`: concerns → `factors[]` |
| `decision_status = INSUFFICIENT` | **FACT (in-memory only)** | set in `_generate_needs_from_factors` / `generate_recommendations` when needs empty / unmapped path; **not** returned as a dedicated field by `POST /recommendations/generate` |
| Non-ELIGIBLE products | **FACT: not persisted** | `if eligibility != "ELIGIBLE": continue` before `_upsert_current_recommendation` |
| Generate API response shape | **FACT** | returns `List` of recommendation DTOs only (`recommendations.py`) |
| Need normalization | **FACT** | `need_normalization.py` from factors |
| Problem / Assessment entities | **FACT: not present** | no models |
| Feedback / follow_up_at | **FACT** | `feedback.py`, `FeedbackService.create_feedback` — `follow_up_at` optional |
| Home Case/Need-first IA | **FACT: mixed Home** | `NewHomePage.tsx` multi-panel |

---

## 2. Decision table (O / G / P)

| ID | Current Reality | Decision | Status | Evidence | Consequence for V1 |
|----|-----------------|----------|--------|----------|---------------------|
| **O1** | Generate path merges **legacy Customer fields** (+ current consultation payload). ProfileFact is **not** read by Recommendation. | **V1 read precedence for recommendation input = legacy Customer profile fields + current consultation merge only.** ProfileFact is out of the Rec read path until a separate adapter gate is authorized. | **RESOLVED-FACT** + **RESOLVED-CONTRACT** | `recommendations.py` `_merge_profile_context`; absence of ProfileFact in Rec service | No dual-source ambiguity in V1 Rec; ProfileFact may still be stored for other uses |
| **O2** | No verified automatic promotion of consultation answers → ProfileFact in generate/intake path. ProfileFact writes are explicit service operations. | **First Vertical Slice does NOT require writing consultation answers into ProfileFact.** Optional/manual ProfileFact use remains outside the VS success criteria. | **RESOLVED-CONTRACT** | ProfileFactService vs recommendations/customers intake paths | VS stays on existing Customer/Case/Rec APIs |
| **O3** | `Case.identified_needs` column exists; **no application writer found**. Needs live in decision_state / recommendation scores. | **V1 does not require durable update of `Case.identified_needs` on every generate.** In-memory decision_state + Recommendation rows are sufficient for V1. | **RESOLVED-CONTRACT** (from **FACT** no writers) | `case.py`; search `identified_needs` | No new Case persistence work for needs in V1 |
| **O4** | Feedback can be created with `case_id` + `source`; `outcome`, `rating`, `comment`, `follow_up_at` optional. | **Minimum Follow-up success for V1 = at least one Feedback row linked to the Case** (valid `source`). `follow_up_at` / rating / outcome are **optional**, not required for VS pass. | **RESOLVED-FACT** + **RESOLVED-CONTRACT** | `FeedbackService.create_feedback` | Simple post-recommendation feedback closes the loop |
| **O5** | Home is a mixed operational surface (consult, catalog, intake, sales, …). | **Case/Need-first Home information architecture remains DEFERRED.** No Home redesign in V1. | **RESOLVED-CONTRACT** | `NewHomePage.tsx`; Contract v0.1 CONFLICT note | UI IA out of scope |
| **G1** | No writer of durable Case evidence gaps found. | **No V1 writer authority is assigned** for `Case.evidence_gaps` because durable persistence is not required for V1 (see G4). Any future writer needs a new contract. | **DEFERRED** | search `evidence_gaps` | Do not implement gap writers in VS |
| **G2** | decision_state initializes `evidence_gaps` to `[]` at generate; no Case write timing exists. | **No V1 lifecycle timing for durable gap writes.** Computed signals during generate remain in-memory only unless a later contract adds persistence. | **DEFERRED** | `_build_decision_state` | — |
| **G3** | Column is unconstrained nullable String; no service format. | **No V1 structure standard for `Case.evidence_gaps`.** Do not invent JSON schema in docs as if runtime enforced it. | **DEFERRED** | `case.py` | — |
| **G4** | Durable gap persistence not used in consultation flow. `decision_status=INSUFFICIENT` is computed on the in-memory `decision_state`. Non-ELIGIBLE candidates are **not** written to Recommendation. `POST /recommendations/generate` returns a **list of recommendation objects only** — a stable, API-visible warning/payload dedicated to INSUFFICIENT / evidence-gap explanation is **not proven**. | **Durable Evidence Gap persistence on Case is NOT required for V1.** V1 must **not** claim that insufficient/unmapped states are exposed as durable Recommendation warnings or a first-class generate API error body. Observable V1 behavior is limited to: (1) in-memory decision_state during the generate call; (2) **absence** (or reduced set) of persisted ELIGIBLE Recommendation rows when nothing qualifies. Any richer gap UX/API is a **future** contract. | **RESOLVED-CONTRACT** | `generate_recommendations` eligibility continue; router returns DTO list only; Contract §2A | Unblocks VS without overclaiming API visibility of gaps |
| **P1** | Runtime path: concerns → factors → needs. No Problem/Assessment models. | **V1 does NOT require persisted Problem or Assessment entities.** Vocabulary may use “assessment” informally for decision_state outcomes, but that is **not** a domain entity claim. | **RESOLVED-CONTRACT** | `_build_decision_state`; no Problem/Assessment models | Avoid entity sprawl |

---

## 3. Explicit residual states

| Item | State | Note |
|------|-------|------|
| ProfileFact → Recommendation adapter | **DEFERRED** | Not authorized; separate Reality Gate required |
| Durable Case.evidence_gaps / identified_needs writers | **DEFERRED** | Not needed for V1 contract |
| API-visible durable INSUFFICIENT / evidence-gap payload | **NOT PROVEN / DEFERRED** | generate returns recommendation list only |
| Questionnaire / progressive question engine | **DEFERRED** | — |
| Home redesign | **DEFERRED** | O5 |
| Scoring / weights / thresholds | **NOT AUTHORIZED** | Issue #37 lineage remains outside this mission |
| OPEN requiring PO product preference (not blocked by missing code evidence) | **None material for starting VS** | O1–O5 and P1 closed from evidence; G1–G3 deferred with G4 resolved under corrected observability claims |

If PO later wants ProfileFact in Rec, durable gaps on Case, or an explicit insufficient response contract, that is a **new mission**, not a silent expansion of V1.

---

## 4. Distinction: runtime vs V1 contract vs future

| Layer | Content |
|-------|---------|
| **Current runtime capability** | Customer legacy profile + consultation merge → Case-owned generate → factors from concerns → needs → eligibility → **only ELIGIBLE** Recommendations persisted; optional Feedback; ProfileFact storage exists but unused by Rec; Case need/gap columns unused; `decision_status` including `INSUFFICIENT` is **in-memory during generate**, not a proven dedicated API field |
| **V1 contract (this addendum)** | Use the runtime path above; do not require ProfileFact in Rec; do not require Case need/gap persistence; do not require Problem/Assessment entities; do not require API-visible durable gap warnings; min follow-up = Feedback row; no Home redesign |
| **Future architecture** | Optional ProfileFact adapter, durable decision snapshots, explicit insufficient/gap API contract, richer outcome domain, Case/Need-first Home — only with separate authorization |

---

## 5. Smallest next Vertical Slice (implementation unit — not executed here)

One unit only:

```text
Input:
  Authenticated customer + existing or newly created Case
  + current consultation concerns/profile fields (legacy Customer path)

State:
  Case owned by customer
  Merged profile via existing generate API merge rules

Decision:
  RecommendationService.generate_recommendations
  (concerns → factors → needs → eligibility → rank)
  No ProfileFact read; no Case.evidence_gaps write required

Output:
  HTTP list of recommendation DTOs for ELIGIBLE products only
  (may be empty). Do not treat empty list alone as a structured
  Evidence Gap document; in-memory INSUFFICIENT is not API-exported
  as a first-class field on current generate endpoint.

Persistence:
  Recommendation rows only for ELIGIBLE products (existing behavior)
  Optional Feedback on Case (min success if follow-up step included)

Test:
  Existing ownership + generate + feedback tests as applicable;
  assert no requirement on Case.identified_needs / evidence_gaps population;
  do not require tests that assume durable gap warnings on generate response

Runtime Evidence:
  API recommendation list + DB rows for Case, Recommendation (if any), optional Feedback
```

**Out of this unit:** Home redesign, ProfileFact wiring, gap writers, new entities, scoring changes, new insufficient/gap API contract.

---

## 6. Acceptance criteria for *this* documentation mission

1. Evidence base is Master `849b7ac…` (or current master if advanced — re-state SHA in PR).  
2. Every O1–O5, G1–G4, P1 has explicit Status.  
3. No invented writers for Case need/gap fields.  
4. No claim of API-visible durable INSUFFICIENT / evidence-gap warnings beyond proven runtime.  
5. Docs-only PR; merge unauthorized until independent review + PO.  
6. Exactly one smallest VS specified without implementing it.  

---

## 7. Review response log

| Finding | Response |
|---------|----------|
| G4 / §4 / §5 over-claimed API-visible warnings for insufficient/unmapped via decision_status or recommendation warnings | **Accepted.** G4, §4, and §5 rewritten: INSUFFICIENT is in-memory; non-ELIGIBLE not persisted; generate returns recommendation list only; structured gap API **NOT PROVEN**. |

---

*End of Phase 1 Decision Addendum v0.1 (corrected)*
