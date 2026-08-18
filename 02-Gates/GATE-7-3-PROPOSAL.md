# GATE 7-3 — Reasoning Engine Proposal

**Status:** PROPOSAL — **NOT APPROVED**  
**Gate:** GATE 7-3  
**Author (Architecture):** Integration Architect (GPT)  
**Repository Agent (Write):** Grok — Red Team / Critic (authorized write only)  
**Repository:** `vahidmaghsoudi2/hbi`  
**Branch target:** `master`  
**Date:** 2026-08-18  

---

## 0. Pre-Write Repository Review (Mandatory)

The following artifacts were inspected before this proposal was written.  
Repository evidence takes priority over assumptions.

| Artifact | Observation |
|----------|-------------|
| `01-Active/current-session.md` | GATE 7-2 **APPROVED**. Next Gate = GATE 7-3 (Reasoning Engine). |
| `03-Frameworks/Frameworks.md` | Contains **Framework 1, 3, 4, 5 only**. **Framework 2 is absent.** |
| `05-References/HBI_Handover.md` / `HBI_Handover.txt` | Historical; products A/B verified; scoring AD-1/AD-2/AD-4 noted. |
| `app/reasoning/` | Contains only `MatchScoringEngine` + `scoring_constants.py` (AD-1, AD-2, AD-4). |
| `app/services/` | EvidenceService (F3/F4/F5), ProductKnowledgeService, RecommendationService present. |
| `app/interface/` | facades, schemas, dto (AD-3 Recommendation contract). |
| `app/api/routers/` | auth, products, customers, cases, recommendations, inventory, sales, evidence. No reasoning router yet. |
| `app/core/auth.py` + `deps.py` | JWT + `get_current_customer_id` (existing auth). |
| Tests | Baseline referenced in session / GATE 7-1: **65 passed / 0 failed**. |

**Discrepancy / Open Input noted:**  
Framework 2 is referenced in older memory documents as “QA Checklist” but is **not defined** in `03-Frameworks/Frameworks.md`. This proposal does **not** invent Framework 2 requirements. It is listed under Open Decisions.

---

## 1. Purpose of GATE 7-3

Design a **Reasoning Engine** that:

1. Consumes **ProductKnowledge** produced by GATE 7-2.  
2. Uses the **Evidence Ledger** (Framework 3) as provenance.  
3. Detects and surfaces **claim conflicts** (scoped by `product_id + field`).  
4. Obeys **Framework 4** claim-boundary rules.  
5. Obeys **Framework 5** UNKNOWN / CONFLICT protocol.  
6. Respects **Framework 1** Product Identity boundaries.  
7. Prevents **cross-product evidence contamination**.  
8. Produces evidence-backed recommendation **reasoning** (not a second score).  
9. Integrates with existing FastAPI + service + facade patterns.  
10. Uses Pydantic schemas.  
11. **Does not replace** `MatchScoringEngine`.  
12. **Does not** introduce a competing scoring system.  
13. **Does not** require database schema changes (Schema v1.2 frozen for this Gate).

---

## 2. Layer Separation (Authoritative)

```
Evidence (Ledger)
    ↓  (aggregation — already GATE 7-1 / 7-2)
ProductKnowledge
    ↓  (NEW — Reasoning Engine)
Reasoning (conflicts, unknowns, claim validation, rationale)
    ↓  (inputs only)
MatchScoringEngine  ← remains the ONLY numerical scorer (AD-1, AD-2, AD-4)
    ↓
Recommendation (existing RecommendationService + AD-3 DTO)
```

| Layer | Responsibility | Authority |
|-------|----------------|-----------|
| Evidence | Provenance, claim_type, source, strength | EvidenceService (existing) |
| ProductKnowledge | Aggregated product facts + confidence | ProductKnowledgeService (existing) |
| **Reasoning** | Conflicts, unknowns, claim boundaries, human-readable rationale, evidence refs | **NEW — this Gate** |
| Scoring | `final_score`, `confidence`, `eligibility`, hard gates | **MatchScoringEngine only** |
| Recommendation | Case-level match list + AD-3 contract | RecommendationService (existing) |

---

## 3. Architectural Constraints (Frozen for this Proposal)

| Constraint | Rule |
|------------|------|
| Scoring | `MatchScoringEngine` remains authoritative. No parallel scoring engine. |
| Database | **No migration.** No new columns on Evidence / ProductKnowledge / Recommendation. Schema v1.2 unchanged. |
| Auth | Reuse existing JWT + `get_current_customer_id` / OAuth2PasswordBearer. No new auth mechanism. |
| Identity | Framework 1: no knowledge/reasoning attachment to UNIDENTIFIED products beyond existing rules. |
| Claim boundary | UNKNOWN ≠ FACT; INFERENCE ≠ FACT; MANUFACTURER_CLAIM ≠ FACT unless Framework 4 permits. |
| Unknown | Never guess. Critical unknowns → NEEDS_REVIEW / escalate. |
| Conflict | Scoped by `product_id + field`. Never silently discard. Preserve values, sources, rationale, state. |
| Cross-product | Evidence and reasoning evaluated only for the requested `product_id`. |
| Framework 2 | **OPEN INPUT** — not present in current Frameworks.md. |

---

## 4. Proposed Components (Implementation Scope — Future Gate Only)

**This section is design only. No code is created in this Gate write.**

```
app/reasoning/
    reasoning_engine.py      # Orchestrator: load PK + Evidence → produce ReasoningResult
    conflict_analyzer.py     # product_id + field conflict detection & register
    claim_validator.py       # Framework 4 boundary checks

app/services/
    reasoning_service.py     # Service layer (mirrors EvidenceService / PK patterns)

app/interface/
    (extend schemas.py or add reasoning schemas)
    # EvidenceReference, ConflictResult, UnknownResult, ReasoningResult, RecommendationResponse

app/api/routers/
    reasoning.py             # New router, registered like evidence_router
```

Compatibility requirements:

- Follow existing `BaseService` + Repository / Facade patterns where applicable.  
- Reasoning may call existing `EvidenceService.detect_conflicts` / `ProductKnowledgeService` rather than re-implementing ledger logic.  
- Facade layer preferred for API exposure (consistent with RecommendationFacade, EvidenceFacade).

---

## 5. API Design (Proposed Contract)

All endpoints under `/api/v1/reasoning/...`  
Authentication: existing project JWT (`Depends(get_current_customer_id)` or equivalent protected dependency).

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/reasoning/products/{product_id}` | Run / refresh reasoning for a product (compute + return ReasoningResult) |
| GET | `/api/v1/reasoning/products/{product_id}` | Retrieve last computed reasoning (if persisted in-memory/cache or recomputed; **persistence is OPEN**) |
| GET | `/api/v1/reasoning/products/{product_id}/conflicts` | List conflicts scoped to product |
| GET | `/api/v1/reasoning/products/{product_id}/evidence` | Evidence references used in reasoning (provenance view) |
| POST | `/api/v1/reasoning/recommendations` | Produce reasoning-enriched recommendation payload (calls existing scoring; does not replace it) |

**Note:** Exact request/response bodies are defined via Pydantic contracts below. No new auth scheme.

---

## 6. Pydantic Contracts (Minimum)

All outputs **must** preserve evidence provenance.

```text
EvidenceReference
  - evidence_id
  - claim_id
  - field
  - claim_type
  - source / source_type
  - evidence_strength
  - qa_status

ConflictResult
  - product_id
  - field
  - conflicting_values[]          # never silently dropped
  - evidence_refs[]               # EvidenceReference
  - sources[]
  - resolution_state              # UNRESOLVED | RESOLVED | NEEDS_REVIEW
  - resolution_rationale          # optional; required if RESOLVED
  - severity                      # OPEN decision

UnknownResult
  - product_id
  - field
  - severity                      # CRITICAL | HIGH | MEDIUM | LOW  (OPEN mapping)
  - action                        # LOG | ESCALATE_PO | NEEDS_REVIEW
  - notes

ReasoningResult
  - product_id
  - product_knowledge_snapshot    # summary, not a DB write
  - evidence_refs[]               # EvidenceReference
  - conflicts[]                   # ConflictResult
  - unknowns[]                    # UnknownResult
  - warnings[]
  - rationale                     # human-readable, evidence-backed
  - claim_boundary_violations[]   # if any attempted promotions blocked
  - generated_at
  - engine_version

RecommendationResponse  (reasoning-enriched; does NOT replace AD-3)
  - existing AD-3 Recommendation fields (from RecommendationService / DTO)
  - reasoning: ReasoningResult | null
  - scoring: { final_score, confidence, eligibility, hard_gate_* }  # from MatchScoringEngine only
```

---

## 7. Conflict Rule (Framework 5)

- Scope: **`product_id + field` only**.  
- Engine must **never** silently discard conflicting evidence.  
- Unresolved conflicts remain explicit (`resolution_state = UNRESOLVED` or `NEEDS_REVIEW`).  
- A resolution (if ever applied) must preserve:  
  - conflicting values  
  - evidence references  
  - source information  
  - resolution rationale  
  - resolution state  

Existing `EvidenceService.detect_conflicts` / `_log_conflict` already implement core ledger behaviour; Reasoning Engine should **consume and surface** them, not fork a second conflict model without justification.

---

## 8. Claim Boundary Rule (Framework 4)

Preserve explicitly:

| From | To | Allowed? |
|------|-----|----------|
| UNKNOWN | anything | **No** |
| INFERENCE | FACT | **No** (automatic) |
| MANUFACTURER_CLAIM | FACT | **No** without independent evidence |
| EVIDENCE_SUPPORTED | FACT | Only with multiple STRONG sources (per Framework 4) |

Reasoning Engine must **never** create unsupported product facts.

---

## 9. UNKNOWN Rule (Framework 5)

- Do not guess missing information.  
- Unknown remains explicitly UNKNOWN.  
- Critical unknowns → NEEDS_REVIEW / escalation behaviour (action mapping is OPEN — see Open Decisions).  
- Non-critical → log to Unknown Register.

---

## 10. Scoring Rule (AD-1 / AD-2 / AD-4)

| Concern | Owner |
|---------|--------|
| `final_score`, `confidence`, `eligibility`, hard gates | **MatchScoringEngine only** |
| Reasoning, evidence refs, conflicts, unknowns, warnings, rationale | **Reasoning Engine** |

Hard-gate behaviour currently implemented:

- `evidence_score ≤ 0` or `inventory_score ≤ 0` → `hard_gate_triggered = True` → eligibility = `NEEDS_REVIEW`.

Any change to that behaviour is **out of scope** for GATE 7-3 and requires separate Architecture / PO decision (previously flagged as RT-03).

---

## 11. Database Rule

- **No migration** for GATE 7-3.  
- Schema v1.2 unchanged.  
- Evidence schema unchanged.  
- ProductKnowledge schema unchanged.  
- No reasoning columns added to the database at this stage.  
- Reasoning results are computed responses (and optionally ephemeral cache). Persistence of reasoning artifacts is an **Open Decision**.

---

## 12. Open Decisions (Must Not Be Silently Frozen)

| ID | Topic | Why open |
|----|--------|----------|
| OD-01 | Framework 2 requirements | Not present in `Frameworks.md` |
| OD-02 | Evidence-strength weighting inside reasoning rationale | Framework 3 defines levels; numerical use in reasoning not fixed |
| OD-03 | Definition of “critical” fields for UNKNOWN escalation | Framework 5 requires severity; list not locked |
| OD-04 | Conflict severity scale | Not fully specified |
| OD-05 | Automatic vs manual conflict resolution | Framework 5 allows priority-based resolution; policy for auto-apply not decided |
| OD-06 | Recommendation persistence vs pure computed response | Affects GET endpoints |
| OD-07 | Customer-profile input contract for reasoning-enriched recommendations | Partial profile already used by RecommendationService; full contract TBD |
| OD-08 | Whether ReasoningResult is stored anywhere | Default proposal: computed only (no DB write) |

These must be resolved by team review **before** implementation starts.

---

## 13. Test Expectations (GATE 7-3 Implementation Phase)

When implementation is later authorized, the following are required:

- Unit tests (reasoning_engine, conflict_analyzer, claim_validator)  
- API tests (new reasoning router)  
- Conflict tests (product_id + field scope, no silent drop)  
- UNKNOWN tests (no guessing; critical escalation)  
- Claim-boundary tests (promotion forbidden cases)  
- Cross-product isolation tests  
- Regression tests against existing suite  

**Regression baseline (current):** 65 passed / 0 failed (GATE 7-1 / session).  
No GATE 7-3 implementation may regress this baseline.

---

## 14. Team Review Requirement

This document is a **team artifact**.  

**GATE 7-3 is NOT APPROVED.**

Mandatory reviewers before any implementation:

1. PM / Data QA (Qwen)  
2. Backend (DeepSeek or designated)  
3. Integration Architect (GPT)  
4. QA  
5. Product Owner (مهندس وحید مقصودی)

Purpose: prevent single-agent dependency and force explicit resolution of Open Decisions.

---

## 15. Out of Scope (This Write)

- Any implementation of `reasoning_engine.py`, services, routers, or schemas beyond this proposal file.  
- Any change to `MatchScoringEngine`, EvidenceService, ProductKnowledgeService, or RecommendationService.  
- Any database migration.  
- Any modification of Framework files.  
- Marking GATE 7-3 as APPROVED.  
- Resolving Open Decisions unilaterally.

---

## 16. Success Criteria for This Proposal Write

| Criterion | Status |
|-----------|--------|
| File exists at `02-Gates/GATE-7-3-PROPOSAL.md` | Target of this commit |
| No other files modified | Required |
| No implementation performed | Required |
| Framework 2 absence documented | Done |
| Scoring authority preserved | Done |
| No schema change proposed | Done |
| Team review required (explicit) | Done |
| Open decisions listed | Done |

---

## 17. Next Step After Team Approval

Only after **all** listed reviewers approve and Open Decisions are resolved (or explicitly deferred):

→ GATE 7-3 Implementation (separate Gate / task)  
→ Then GATE 7-4 Integration Testing  
→ Then GATE 7-5 Validation & Handover  

---

**End of GATE 7-3 Proposal**  
**Status remains: PROPOSAL — awaiting team review.**
