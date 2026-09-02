# HBI — PRODUCT INTAKE GOVERNANCE RECONCILIATION
## 2026-09-02

**Status:** ACTIVE  
**Authority:** Product Intake Governance Amendment  
**Source of Truth:** GitHub `master`  
**Parent Rules:** `docs/01_project_control/PROJECT_RULES.md`  
**Domain:** Product Intake  
**Purpose:** Reconcile existing Product Intake governance with verified current repository reality.

---

## 1. REASON FOR THIS AMENDMENT

The original Product Intake governance and execution roadmap were established before the current Home Page / Product Gallery / Product Intake implementation was fully reconciled against `master`.

A subsequent direct repository inspection established that Product Intake functionality already exists.

Therefore Product Intake must NOT be treated as a capability that needs to be rebuilt from zero.

This amendment preserves the existing governance decisions while correcting the execution baseline.

---

## 2. CURRENT VERIFIED REALITY

The current repository contains existing Product functionality including:

- Product model and identity fields;
- Product creation;
- Product update/edit;
- ProductKnowledge relationship;
- Evidence model/relationship;
- Inventory relationship and current inventory creation behavior;
- existing Product A-D records;
- Home Page Product navigation;
- Product Gallery / Product listing capability;
- Product Intake UI;
- `frontend/src/pages/ProductIntakePanel.tsx`;
- Home Page integration through `frontend/src/pages/NewHomePage.tsx`.

The complete governed Product Intake lifecycle is not yet implemented.

---

## 3. GOVERNANCE CORRECTION

The following interpretation is now authoritative:

> Product Intake is an existing partial capability that must be audited, formalized, completed and integrated into a governed Product Master lifecycle.

The following interpretation is NOT authoritative:

> Product Intake UI / Product Gallery / Product Catalog must be built from zero.

Any earlier roadmap wording implying a greenfield rebuild is superseded by this amendment.

---

## 4. EXECUTION PATH

The authoritative execution model is:

CURRENT REALITY
→ GAP IDENTIFICATION
→ CONTRACT
→ TECHNICAL DESIGN
→ IMPLEMENTATION
→ TEST
→ EVIDENCE
→ GATE
→ NEXT PHASE

Not:

REBUILD FROM ZERO

---

## 5. HOME PAGE / PRODUCT GALLERY RULE

The existing Home Page is part of the Product Intake baseline.

At minimum, future work must inspect:

- `frontend/src/pages/NewHomePage.tsx`
- `frontend/src/pages/ProductIntakePanel.tsx`
- Product navigation
- Product Gallery / listing
- Product API
- Product Master integration
- existing routes
- existing styles
- Recommendation integration
- Sales integration

Existing functionality must be extended or integrated where appropriate.

Duplicate Product Catalog, Product Intake or Product Master implementations are prohibited without explicit decision.

---

## 6. PRODUCT MASTER RULE

Existing Product A-D records and established `product_id` values are protected.

No migration, deletion, merge, rename or identity restructuring is authorized by this amendment.

Existing downstream relationships must remain intact.

---

## 7. STRATEGY DOCUMENT INTERPRETATION

`PRODUCT_INTAKE_STRATEGY_AND_GOVERNANCE.md` remains the strategic parent document.

This amendment does not replace its strategic decisions.

It clarifies the current implementation baseline and supersedes any conflicting assumption about Product Intake being absent or requiring greenfield construction.

---

## 8. ROADMAP CORRECTION

Phase 0 is now considered:

**REALITY & BASELINE — RECONCILED**

Phase 1 remains:

**PRODUCT INTAKE CONTRACT v1 — ACTIVE / CURRENT**

The immediate objective is NOT implementation.

The immediate objective is to finalize the operational contract using the verified current baseline.

---

## 9. CONTRACT BOUNDARY

Before implementation, Product Intake Contract v1 must explicitly distinguish:

- User Input;
- Product Master data;
- AI Research Output;
- Evidence;
- Product Knowledge;
- Approval data.

No current implementation behavior is automatically promoted to business rule.

---

## 10. OPEN DECISIONS

The following remain OPEN unless separately approved:

- duplicate matching algorithm;
- duplicate result semantics;
- default Product status;
- default inventory behavior;
- approval mechanism;
- approval state machine;
- provisional/shadow mechanism;
- Product/Variant technical model;
- source-tier taxonomy;
- research tier/cost strategy;
- history/version schema;
- Product Intake API Contract details.

---

## 11. IMPLEMENTATION FREEZE

Until Contract v1 is formally accepted:

- no new duplicate detection implementation;
- no new approval endpoint;
- no new lifecycle state machine;
- no Product status policy change;
- no inventory policy change;
- no Product Master redesign;
- no Product A-D modification.

---

## 12. AUTHORITY

If this amendment conflicts with an older Product Intake execution assumption, this amendment controls the implementation baseline.

If this amendment conflicts with `PROJECT_RULES.md`, `PROJECT_RULES.md` controls.

If a business decision is required, the matter remains OPEN until explicitly decided by the Product Owner.

---

## 13. CONTINUITY RULE

Any future Human or AI contributor must read:

1. `PROJECT_RULES.md`
2. `PRODUCT_INTAKE_STRATEGY_AND_GOVERNANCE.md`
3. this reconciliation amendment
4. `PRODUCT_INTAKE_MASTER_EXECUTION_ROADMAP.md`
5. `PRODUCT_INTAKE_LIVE_PROJECT_LEDGER.md`
6. current `master`
7. current Product Intake Contract, when available

No contributor may rely on an older Product Intake roadmap without checking this amendment.

---

## 14. RESULT

Product Intake is officially treated as:

**EXISTING PARTIAL CAPABILITY → FORMALIZE → COMPLETE → VALIDATE → APPROVE → INTEGRATE → MAINTAIN**

and not:

**GREENFIELD BUILD**

---

# END
