# Information Feeding Flow — Repository Reality Map

**Project:** HBI (`vahidmaghsoudi2/hbi`)  
**Document:** `docs/INFORMATION_FEEDING_FLOW.md`  
**Mode:** Documentation / Read-Only mapping  
**Baseline HEAD (pre-update clone):** `d5e0ebc3c2bd8f2051f4fd3b4acd9c3fc87b81e6`  
**Authority:** Code Reality over docs when they conflict  
**Date:** 2026-08-27  
**Owner:** Grok1  

---

## Purpose

This document explains **how product information actually enters HBI** and **how it reaches Recommendation**, based only on what exists in the current repository.

| Label | Meaning |
|-------|---------|
| **VERIFIED** | Implemented in code/models/scripts and observable on the current path |
| **PARTIAL** | Structures or partial logic exist; end-to-end path incomplete or inconsistent |
| **MISSING** | Required for the named stage; not present in repository |
| **UNKNOWN** | Cannot be confirmed from repository contents alone |
| **FUTURE** | Documented/roadmap intent only; not runtime behavior |

---

## End-to-End Map (Code Reality)

```
Product Introduction          [PARTIAL — docs + seed only]
        ↓
Product Intake                [MISSING — no intake API]
        ↓
Product Identity              [VERIFIED — model fields + constraints]
        ↓
Product Knowledge             [PARTIAL — model + refresh-from-evidence]
        ↓
Claims / Actives / INCI       [PARTIAL — Evidence.field + claim text]
        ↓
Evidence                      [VERIFIED — model + seed + services/API]
        ↓
Verification / QA             [PARTIAL — fields exist; no promote workflow]
        ↓
ACTIVE Product                [VERIFIED — status DRAFT|ACTIVE on model]
        ↓
Recommendation Candidate      [PARTIAL — intended filter overwritten by missing find_verified()]
        ↓
Reasoning                     [VERIFIED — ReasoningEngine]
        ↓
Scoring                       [VERIFIED — MatchScoringEngine (FROZEN)]
        ↓
Ranking                       [VERIFIED — ranking_score / ranking_reasons]
        ↓
Explanation                   [VERIFIED — reasoning text → ranking_reasons]
        ↓
Product Owner Decision        [MISSING / FUTURE — no runtime PO gate]
```

---

## Stage-by-Stage Reality

### 1. Product Introduction — **PARTIAL**

**What exists**
- Human-authored records: `docs/01_product_records/PRODUCT_{A,B,C,D}_RECORD.md`
- Machine seed: `data/seed_products.json` (source note points at those records)
- Loader: `scripts/seed_products_from_records.py` → writes Product / Inventory / ProductKnowledge / Evidence

**What does not exist**
- Runtime “introduce product” UI/API for operators outside seed scripts

**Entry path today:** documentation → JSON seed → script → SQLite tables.

---

### 2. Product Intake — **MISSING**

No dedicated intake endpoint (e.g. `POST /api/v1/products/intake`) was found under `app/api/routers/`.

`app/api/routers/products.py` exposes list/get/by-brand style reads for verified products; not a full create-and-promote intake workflow.

---

### 3. Product Identity — **VERIFIED**

`app/models/product.py` stores and constrains identity:

| Field | Role |
|-------|------|
| `product_id` | Primary key |
| `brand`, `product_name`, `variant`, size fields | Identity surface |
| `barcode_gtin` | Optional, **unique=True** |
| `identity_status` | CheckConstraint: `VERIFIED`, `PARTIAL_IDENTITY`, `CONFLICT`, `NEEDS_REVIEW` |
| `identity_confidence` | 0.0–1.0 optional |
| `identity_source_refs` | Optional string refs |

Identity is a **data state on Product**, not a separate Identity service.

---

### 4. Product Knowledge — **PARTIAL**

**Model:** `app/models/product_knowledge.py`  
Fields include: `ingredients`, `ingredient_roles`, `claimed_benefits`, `known_use_cases`, `contraindications`, `usage_instructions`, `manufacturer_claims`, `evidence_refs`, `evidence_status`, `knowledge_confidence`.

**Service:** `app/services/product_knowledge_service.py`  
`update_from_evidence(product_id)` aggregates Evidence rows by `field` into knowledge columns.

**Gap:** Knowledge is not automatically rebuilt on every Recommendation call beyond snapshot read; pipeline depends on prior refresh/seed.

---

### 5. Claims / Actives / INCI — **PARTIAL**

There is **no separate Claim or INCI table**.

Claims live as rows in `Evidence`:
- `claim` (text)
- `field` (e.g. brand, product_name, ingredients, claimed_benefits, known_use_cases)
- `claim_type`, `claim_id` (unique when set)

Actives/INCI appear only when encoded in Evidence/ProductKnowledge string fields—not as structured ingredient entities.

---

### 6. Evidence — **VERIFIED**

| Aspect | Location |
|--------|----------|
| Model | `app/models/evidence.py` |
| Seed | `data/seed_evidence.json` ← ledger/docs notes |
| Repository / service | `evidence_repository.py`, `evidence_service.py` |
| API | `/api/v1/evidence` (authenticated) |

Key columns: `evidence_id`, `product_id` (FK RESTRICT), `claim_id` (unique), `source_type`, `source_reference`, `claim`, `field`, strength/status/qa fields.

---

### 7. Verification / QA — **PARTIAL**

**Present on Product**
- `qa_verdict`: PENDING | VALID | INVALID | CONFLICT | UNKNOWN | NEEDS_REVIEW
- `qa_reviewed_at`, `qa_notes`

**Present on Evidence**
- `qa_status` (default PENDING)

**Missing**
- API/workflow that requires QA success then flips product from DRAFT → ACTIVE
- Hard exclusion of `qa_verdict == INVALID` inside candidate selection (see Candidate stage)

---

### 8. ACTIVE Product — **VERIFIED** (field-level)

`Product.status` exists with CheckConstraint `'DRAFT' | 'ACTIVE'` and `server_default='ACTIVE'`.

**Activation reality**
- Schema default → new rows are ACTIVE unless set otherwise
- Seed path loads A–D without a DRAFT lifecycle ceremony
- No coded “promote after QA” transition service observed

---

### 9. Recommendation Candidate — **PARTIAL** (code conflict)

In `app/services/recommendation_service.py` → `generate_recommendations`:

1. **Line ~71 (intended filter):**  
   `products = [p for p in self.product_repo.find_by_identity_status("VERIFIED") if p.status == "ACTIVE"]`
2. **Line ~81 (overwrite):**  
   `products = self.product_repo.find_verified()`

**Code Reality conflict**
- `ProductRepository` defines: `find_by_brand`, `find_by_identity_status`, `find_by_qa_verdict`, `get_with_inventory`
- **`find_verified()` is NOT defined** on `ProductRepository`

The VERIFIED+ACTIVE list comprehension is **overwritten** and does not remain the final candidate source.

**Also not filtered at candidate list:** `qa_verdict == INVALID`.

Inventory gate remains: skip if no inventory or `quantity_available <= 0`.

---

### 10. Reasoning — **VERIFIED**

`ReasoningEngine` is invoked from RecommendationService with product knowledge snapshot, evidence list, need_match, evidence_score, inventory_score.

Architecture intent: compute-only (does not own persistence of Product/Evidence).

---

### 11. Scoring — **VERIFIED** (FROZEN)

`MatchScoringEngine` / `scoring_constants.py`:
- Weights: Need 0.50, Evidence 0.30, Inventory 0.20
- Thresholds: ELIGIBLE ≥ 0.70, NEEDS_REVIEW ≥ 0.50, else INELIGIBLE
- Hard Gate when evidence_score ≤ 0 or inventory_score ≤ 0

This layer is project-frozen; feeding docs must not imply formula changes.

---

### 12. Ranking — **VERIFIED**

Persisted on `Recommendation`:
- `ranking_score` (from engine final_score)
- `ranking_reasons`
- `eligibility_status` (after persistence mapping)

Persistence mapping observed:
```text
if eligibility == "NEEDS_REVIEW":
    eligibility = "INELIGIBLE_PENDING_REVIEW"
```
Required because DB CheckConstraint does not allow raw `NEEDS_REVIEW`.

Hard filter: `final_score < 0.5` → row not persisted.

---

### 13. Explanation — **VERIFIED**

Explanation is the human-readable string from scoring/reasoning:
- Stored as `Recommendation.ranking_reasons`
- Exposed on API DTOs as `reasoning` / ranking reasons via facade

Not a separate Explanation entity.

---

### 14. Product Owner Decision — **MISSING / FUTURE**

No runtime component implements a formal PO accept/reject gate on recommendations.  
PO decision is an operational/process step outside the executed API path.

---

## Answers to Required Questions

### 1. اطلاعات از کجا وارد می‌شود؟
**Today (Pilot):** `docs/01_product_records/*` → `data/seed_products.json` + `data/seed_evidence.json` → `scripts/seed_products_from_records.py`.  
**Not from** a live Product Intake API.

### 2. کجا ذخیره می‌شود؟
| Data | Table / location |
|------|------------------|
| Product identity & QA flags | `Product` |
| Knowledge snapshot | `ProductKnowledge` |
| Claims / evidence | `Evidence` |
| Stock | `Inventory` |
| Recommendation outputs | `Recommendation` |

### 3. چه Componentای آن را مصرف می‌کند؟
- `RecommendationService.generate_recommendations`
- `ReasoningEngine` + `MatchScoringEngine`
- `ProductKnowledgeService` (evidence → knowledge aggregation)
- API facades/routers for products, evidence, recommendations
- Frontend Pilot UI (consumes API only)

### 4. Evidence کجا قرار می‌گیرد؟
Table `Evidence`, keyed by `evidence_id`, FK to `Product.product_id`. Seeded from `data/seed_evidence.json`.

### 5. Verification کجا اتفاق می‌افتد؟
**Fields only** on Product (`qa_verdict`, `identity_status`) and Evidence (`qa_status`).  
No dedicated verification workflow service/API that flips lifecycle to ACTIVE after review.

### 6. چه چیزی باعث ACTIVE شدن محصول می‌شود؟
- Schema default: `status` server_default `'ACTIVE'`
- Seed path does not set DRAFT; products enter as ACTIVE unless explicitly set otherwise
- No coded promotion rule from DRAFT after QA success

### 7. Recommendation از کدام داده‌ها استفاده می‌کند؟
- Candidate products (intended: VERIFIED + ACTIVE; **runtime conflict with `find_verified()`**)
- Inventory availability
- ProductKnowledge snapshot (`known_use_cases` for need match)
- Evidence list (source_type weights → evidence_score)
- Customer profile `concerns` from generate request body

### 8. Explanation در کدام مرحله ایجاد می‌شود؟
Inside scoring/reasoning output; persisted as `ranking_reasons` at Recommendation create time.

### 9. کدام قسمت هنوز پیاده‌سازی نشده است؟
- Product Intake API / operator intake UI
- Formal QA → promote-to-ACTIVE workflow
- Reliable candidate API (`find_verified` missing; line overwrite)
- Exclusion of `qa_verdict=INVALID` at candidate selection
- Runtime Product Owner decision gate
- Structured INCI/Actives entities (beyond free-text fields)

---

## Code vs Docs Conflicts Registered

| Topic | Docs/roadmap tendency | Code Reality |
|-------|----------------------|--------------|
| Intake | Roadmap describes intake phase | **No intake API** on routers |
| `find_verified()` | Implied clean verified list | **Method absent** on `ProductRepository`; still called after a correct filter line |
| ACTIVE lifecycle | Conceptual DRAFT→ACTIVE after QA | **Default ACTIVE**; no promote service |
| Claims | Sometimes spoken as first-class | **Evidence rows only** |
| INVALID QA | Should block eligibility | **Not filtered** in candidate comprehension |

---

## Label Counts

| Label | Count |
|-------|-------|
| VERIFIED | 7 |
| PARTIAL | 5 |
| MISSING | 1 (Intake) |
| MISSING/FUTURE | 1 (PO Decision) |
| UNKNOWN | 0 |

Stages: Introduction, Intake, Identity, Knowledge, Claims/INCI, Evidence, Verification/QA, ACTIVE, Candidate, Reasoning, Scoring, Ranking, Explanation, PO Decision.

---

## WHAT A NEW TEAM MEMBER MUST UNDERSTAND

1. **Pilot products do not enter through an Intake API** — they are seeded from product records + JSON via scripts.
2. **Product A–D and their evidence seed are frozen operational inputs** for the current pilot path.
3. **Identity and QA are columns on `Product`**, not separate microservices.
4. **Evidence is the system of record for claims**; there is no independent Claim table.
5. **ProductKnowledge is a derived snapshot** that can be refreshed from Evidence fields.
6. **Recommendation eligibility is scored by a frozen engine**; do not change weights/thresholds to “fix” feeding gaps.
7. **ACTIVE is a model status with default ACTIVE** — it is not currently earned by a coded QA promotion workflow.
8. **Candidate selection has a live code conflict:** a correct VERIFIED+ACTIVE filter is overwritten by a call to missing `find_verified()`.
9. **Explanation is ranking_reasons text**, not a separate module.
10. **When docs and code disagree, trust code** — this map is intentionally code-first.

---

## Repository Sources Inspected

- `app/models/product.py`
- `app/models/product_knowledge.py`
- `app/models/evidence.py`
- `app/models/recommendation.py`
- `app/repositories/product_repository.py`
- `app/services/recommendation_service.py`
- `app/services/product_knowledge_service.py`
- `app/services/evidence_service.py`
- `app/api/routers/products.py`
- `data/seed_products.json`
- `data/seed_evidence.json`
- `scripts/seed_products_from_records.py`
- `docs/01_product_records/*`
- `docs/01_project_state/HBI_INFORMATION_FEEDING_ROADMAP.md` (roadmap context only)

---

## Summary Findings

- Information feeding for Pilot is **seed-driven**, not intake-driven.
- Storage model (Product / ProductKnowledge / Evidence / Inventory / Recommendation) is **real and connected**.
- Scoring/Reasoning/Ranking/Explanation path is **implemented and frozen at formula level**.
- Largest operational gaps: **Intake API**, **candidate selection bug (`find_verified`)**, **QA promotion workflow**, **INVALID QA not excluded at candidate list**.
- No UNKNOWN stages remained after repository inspection of the named path.

---

**VERDICT: DOCUMENTATION DELIVERED**
