# Information Feeding Flow — Repository Reality Map

**Project:** HBI (vahidmaghsoudi2/hbi)  
**Document:** `docs/INFORMATION_FEEDING_FLOW.md`  
**Mode:** Documentation / Read-Only mapping  
**Baseline HEAD:** `9fd3328eff1d73a0aaf03786a5b54e539acaa2e1`  
**Authority:** Code Reality over docs when they conflict  
**Date:** 2026-08-27  
**Owner:** Grok1  

---

## Purpose

This document explains **how product information actually enters HBI** and **how it reaches Recommendation**, based only on what exists in the current repository.

Labels used for each stage:

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
Recommendation Candidate      [PARTIAL — filter intended; find_verified() missing]
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
- Human-authored product records: `docs/01_product_records/PRODUCT_{A,B,C,D}_RECORD.md`
- Machine seed: `data/seed_products.json` (source note points at those records)
- Loader: `scripts/seed_products_from_records.py` → writes `Product`, `Inventory`, optional `ProductKnowledge`

**What does not exist**
- Operator UI / API for introducing arbitrary new products at runtime

**Entry point today:** file-based seed for frozen Pilot products A–D only.

---

### 2. Product Intake — **MISSING**

**What exists**
- Product model can store new rows if inserted programmatically
- `Product.status` allows `DRAFT` | `ACTIVE` (`app/models/product.py`)

**What does not exist**
- `POST /api/v1/products/intake` (or equivalent)
- Dedicated intake queue endpoint
- Lifecycle service that creates DRAFT products from operator payload

**Conflict note:** Roadmap docs describe Intake as a stage; **Code Reality has no intake API.**

---

### 3. Product Identity — **VERIFIED**

**Storage:** table `Product` (`app/models/product.py`)

| Field | Role |
|-------|------|
| `product_id` | Primary key |
| `brand`, `product_name`, `variant`, size fields | Identity surface |
| `barcode_gtin` | Unique when present |
| `identity_status` | `VERIFIED` \| `PARTIAL_IDENTITY` \| `CONFLICT` \| `NEEDS_REVIEW` |
| `identity_confidence` | 0.0–1.0 optional |
| `identity_source_refs` | Free text refs |

**Consumers**
- `ProductRepository.find_by_identity_status`
- `ProductService.get_verified_products()` → `identity_status == "VERIFIED"`
- Public list API uses verified products via facade

---

### 4. Product Knowledge — **PARTIAL**

**Storage:** table `ProductKnowledge` (`app/models/product_knowledge.py`)

Typical fields used downstream:
- `known_use_cases`, `claimed_benefits`, `ingredients`, `contraindications`
- `evidence_status`, `knowledge_confidence`, `evidence_refs`

**Writers**
- Seed script may set `known_use_cases` from seed `category`
- `ProductKnowledgeService.update_from_evidence()` aggregates Evidence claims by `field` into knowledge columns
- API: evidence router exposes knowledge refresh (`/knowledge/{product_id}/refresh`)

**Gap:** Knowledge is not a mandatory gate before Recommendation; generate path tolerates empty PK snapshot.

---

### 5. Claims / Actives / INCI — **PARTIAL**

**There is no separate Claim or INCI entity table.**

Claims live as rows in `Evidence`:
- `claim` (text)
- `field` (e.g. ingredients / claimed_benefits / known_use_cases / contraindications)
- `claim_type`, `claim_id` (unique when set)
- `source_type`, `source_reference`, `evidence_strength`

**INCI / actives:** only as unstructured claim text when `field` indicates ingredients—not a normalized INCI dictionary.

---

### 6. Evidence — **VERIFIED**

**Storage:** `Evidence` (`app/models/evidence.py`)  
**Seed:** `data/seed_evidence.json` via `seed_evidence()` in seed script  
**Services:** `EvidenceService`, repositories, API under `app/api/routers/evidence.py`  
**FK:** `product_id` → Product (RESTRICT)

Evidence is the provenance layer for claims and a primary input to scoring weight collection.

---

### 7. Verification / QA — **PARTIAL**

**On Product**
- `qa_verdict`: `PENDING` \| `VALID` \| `INVALID` \| `CONFLICT` \| `UNKNOWN` \| `NEEDS_REVIEW`
- `qa_reviewed_at`, `qa_notes`

**On Evidence**
- `qa_status`, `evidence_status`, `conflict_status`

**What is missing**
- Automated rule: `qa_verdict == INVALID` ⇒ exclude from Recommendation candidates (not enforced in generate loop as of this HEAD)
- API workflow: DRAFT → review → VERIFIED + VALID → ACTIVE

Seed Pilot products commonly have `identity_status=VERIFIED` and `qa_verdict=PENDING`.

---

### 8. ACTIVE Product — **VERIFIED** (field) / **PARTIAL** (lifecycle)

**Model**
```text
status IN ('DRAFT', 'ACTIVE')  — server_default 'ACTIVE'
```

**Runtime intent in RecommendationService (line ~71):**
```text
find_by_identity_status("VERIFIED") filtered by status == "ACTIVE"
```

**Gap:** No dedicated service method that *promotes* a product to ACTIVE after QA. Default ACTIVE means seeded products are eligible by default unless status is changed.

---

### 9. Recommendation Candidate — **PARTIAL**

**Intended path (code comments + early filter):**
1. Products with `identity_status == VERIFIED` and `status == ACTIVE`
2. Inventory with `quantity_available > 0`

**Code Reality conflict (critical):**
```text
products = [p for p in self.product_repo.find_by_identity_status("VERIFIED") if p.status == "ACTIVE"]
...
products = self.product_repo.find_verified()   # OVERWRITES previous list
```

`ProductRepository.find_verified()` **does not exist** in `app/repositories/product_repository.py`.

Closest real methods:
- `find_by_identity_status("VERIFIED")`
- `ProductService.get_verified_products()` (same filter; does not require ACTIVE or non-INVALID QA)

**Label rationale:** Candidate selection is designed but **not consistently implementable** until `find_verified` is aligned with repository reality.

---

### 10. Reasoning — **VERIFIED**

**Component:** `app/reasoning/reasoning_engine.py`  
Orchestrates conflict analysis, claim validation hooks, and scoring call.  
Result is **COMPUTED_ONLY** (does not write DB itself).

Inputs from RecommendationService:
- product_knowledge_snapshot
- evidence_list
- need_match, evidence_score, inventory_score

---

### 11. Scoring — **VERIFIED** (FROZEN)

**Components**
- `app/reasoning/scoring.py` — `MatchScoringEngine`
- `app/reasoning/scoring_constants.py` — weights & thresholds

| Constant | Value |
|----------|-------|
| Need weight | 0.50 |
| Evidence weight | 0.30 |
| Inventory weight | 0.20 |
| ELIGIBLE threshold | ≥ 0.70 |
| NEEDS_REVIEW band | ≥ 0.50 |
| Hard Gate | evidence_score ≤ 0 or inventory_score ≤ 0 → NEEDS_REVIEW |

Scoring emits eligibility including `NEEDS_REVIEW`.

---

### 12. Ranking — **VERIFIED**

On persist (`Recommendation` model + service):
- `ranking_score` ← engine `final_score`
- `ranking_reasons` ← engine rationale/reasoning text
- `eligibility_status` ← mapped eligibility
- `need_match_score`, `evidence_score`

**Persistence contract alignment (VERIFIED):**
```text
if eligibility == "NEEDS_REVIEW":
    eligibility = "INELIGIBLE_PENDING_REVIEW"
```
Required because DB CheckConstraint does not allow raw `NEEDS_REVIEW`.

Hard filter: `final_score < 0.5` → row not persisted.

---

### 13. Explanation — **VERIFIED**

Explanation is the human-readable string produced by scoring/reasoning:
- Stored as `Recommendation.ranking_reasons`
- Exposed on API DTOs as `reasoning` / ranking reasons via facade

Not a separate Explanation entity.

---

### 14. Product Owner Decision — **MISSING / FUTURE**

No runtime component implements a formal PO accept/reject gate on recommendations.  
PO decision is an operational/process step outside the executed API path (evaluation, not code).

---

## Answers to Required Questions

### 1. اطلاعات از کجا وارد می‌شود؟
**Today (Pilot):** from `docs/01_product_records/*` → `data/seed_products.json` + `data/seed_evidence.json` → `scripts/seed_products_from_records.py`.  
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
- Candidate products (intended: VERIFIED + ACTIVE; see `find_verified` conflict)
- Inventory availability
- ProductKnowledge snapshot (`known_use_cases` for need match)
- Evidence list (source_type weights → evidence_score)
- Customer profile `concerns` from generate request body

### 8. Explanation در کدام مرحله ایجاد می‌شود؟
During **Scoring / Reasoning** as the `reasoning` / rationale string; persisted as `ranking_reasons` when Recommendation is written.

### 9. کدام قسمت هنوز پیاده‌سازی نشده است؟
- Product Intake API and operator queue
- Formal QA → ACTIVE promotion workflow
- `ProductRepository.find_verified()` (called but absent)
- Hard exclusion of `qa_verdict == INVALID` in candidate selection
- Normalized INCI / Actives catalog
- Runtime Product Owner decision gate

---

## Doc vs Code Conflicts (recorded)

| Topic | Docs / Roadmap tendency | Code Reality |
|-------|-------------------------|--------------|
| Product Intake as active stage | Described as stage mission | No intake endpoint |
| Full Customer→…→PO Decision pipeline | End-to-end narrative | PO Decision not in code |
| Verified product helper | Assumed available | `find_verified()` missing on repository |
| QA INVALID exclusion | Implied by quality narrative | Not enforced in generate loop |
| Information Feeding Roadmap | `docs/01_project_state/HBI_INFORMATION_FEEDING_ROADMAP.md` | Directional; this file maps **implementation** |

---

## Component Index (repository paths)

| Concern | Path |
|---------|------|
| Product model | `app/models/product.py` |
| ProductKnowledge model | `app/models/product_knowledge.py` |
| Evidence model | `app/models/evidence.py` |
| Recommendation model | `app/models/recommendation.py` |
| Inventory model | `app/models/inventory.py` |
| Seed products | `data/seed_products.json` |
| Seed evidence | `data/seed_evidence.json` |
| Seed script | `scripts/seed_products_from_records.py` |
| Product records (SoT for A–D) | `docs/01_product_records/` |
| Recommendation service | `app/services/recommendation_service.py` |
| Product service | `app/services/product_service.py` |
| Evidence / PK services | `app/services/evidence_service.py`, `product_knowledge_service.py` |
| Reasoning / Scoring | `app/reasoning/reasoning_engine.py`, `scoring.py`, `scoring_constants.py` |
| Product API | `app/api/routers/products.py` |
| Evidence API | `app/api/routers/evidence.py` |
| Recommendation API | `app/api/routers/recommendations.py` |
| Prior roadmap (direction) | `docs/01_project_state/HBI_INFORMATION_FEEDING_ROADMAP.md` |

---

## WHAT A NEW TEAM MEMBER MUST UNDERSTAND

1. **Pilot data is file-fed, not intake-fed:** A–D enter via product records → JSON seed → seed script—not via an Intake API.
2. **Identity and QA are fields on Product**, not a separate workflow engine; values are constrained by CheckConstraints.
3. **Evidence rows are the claim store;** there is no separate Claim/INCI table—ingredients and benefits are claim text keyed by `field`.
4. **ProductKnowledge is a denormalized snapshot** that can be refreshed from Evidence but is optional at generate time.
5. **Recommendation is orchestration, not scoring:** `RecommendationService` gathers inputs; `ReasoningEngine`/`MatchScoringEngine` compute; service persists.
6. **Scoring is frozen architecture** (weights, thresholds, hard gate); do not “fix” contract issues by changing the formula.
7. **Eligibility strings from scoring are mapped** before DB write (`NEEDS_REVIEW` → `INELIGIBLE_PENDING_REVIEW`).
8. **ACTIVE is a real column** (`DRAFT`/`ACTIVE`) with default ACTIVE; lifecycle promotion APIs are not built.
9. **Candidate selection has a known code defect:** `find_verified()` is called but not defined on `ProductRepository`—prefer `find_by_identity_status("VERIFIED")` (+ ACTIVE filter) until fixed.
10. **PO Decision is outside the runtime path today;** Explanation is the scoring rationale string, not a separate decision module.

---

## Label Counts (this document)

| Label | Count (stages in primary map) |
|-------|-------------------------------|
| VERIFIED | 6 |
| PARTIAL | 5 |
| MISSING | 2 |
| UNKNOWN | 0 |
| FUTURE | 1 (PO Decision, also marked MISSING) |

Primary stages counted: 14 (PO Decision counted once as MISSING/FUTURE).

---

## Verdict

**DOCUMENTATION DELIVERED**

No code, schema, scoring, or product data was changed by this mission.
