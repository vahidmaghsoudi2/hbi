# HBI G2 — Research Draft / Evidence Enrichment — Reality Contract v0.1

**Status:** Implementation candidate on branch `gpt2/evidence-truth-g2-g4`  
**Baseline:** `master @ e110d2c46dfa966009118a0aee6d040ee932ea28`  
**Authority:** Product Intake Contract v1 + P4 Governance Contract v1  
**Scope:** Existing Product + existing Evidence + existing ProductKnowledge  
**Explicit boundary:** Research never approves or activates Product.

## 1. Reality confirmed

The repository already has:

- one governed Product Master keyed by `product_id`;
- P4 lifecycle and controlled Product transitions;
- Evidence attached to `product_id`;
- Evidence claim-boundary enforcement;
- explicit UNKNOWN/CONFLICT handling;
- Evidence QA statuses;
- ProductKnowledge rebuild from acceptable Evidence only;
- Recommendation consumption of the Product/Evidence/Knowledge surface.

The missing V1 workflow is the explicit **Research Draft** handoff into that existing Evidence boundary.

## 2. V1 decision

No new Product state and no second Product Master are introduced.

A Research Draft is a source-traceable collection of assertions that becomes Evidence rows with:

- `qa_status=PENDING`
- `evidence_status=UNKNOWN`
- explicit `claim_type`
- explicit `source_type`
- explicit `source_reference`

The research operation is additive. Repeating research creates new Evidence assertions; it does not silently overwrite earlier Evidence.

## 3. Assertion contract

Each non-empty assertion requires:

- claim
- source_type
- source_reference

Optional structured fields:

- field
- claim_type
- source_date
- evidence_strength
- market_region
- notes

Allowed claim classifications:

`FACT | MANUFACTURER_CLAIM | EVIDENCE | INFERENCE | UNKNOWN | CONFLICT`

Existing Evidence claim-boundary rules remain authoritative. In particular, a research assertion cannot bypass the existing FACT source restrictions.

## 4. Knowledge boundary

Research Draft output does **not** become ProductKnowledge merely because it was researched.

Only Evidence with acceptable QA (`VERIFIED` or `APPROVED`) participates in ProductKnowledge rebuild.

Therefore:

`Research → Evidence(PENDING) → Human review → Evidence(V&/or A) → ProductKnowledge`

UNKNOWN and CONFLICT remain visible and blocking where existing readiness rules require them.

## 5. Permissions

Research Draft creation is restricted to the existing Product/Evidence governance roles:

- Reviewer/QA
- PO
- Admin

AI research is not a P4 governance role and cannot approve, activate, or mutate Product governance fields.

## 6. Acceptance matrix

| Case | Expected result |
|---|---|
| Existing product_id | Research attaches to same Product |
| Unknown product_id | 404 |
| Empty assertion list | 422 |
| Missing claim | 422 |
| Missing source_type | 422 |
| Missing source_reference | 422 |
| UNKNOWN assertion | stored as UNKNOWN/PENDING |
| MANUFACTURER_CLAIM | stored as classified claim |
| INFERENCE | remains INFERENCE |
| unsupported claim type | 422 |
| research assertion | never changes Product status/identity/QA |
| repeated research | additive Evidence, no silent overwrite |
| pending Evidence | excluded from ProductKnowledge |
| verified Evidence | eligible for ProductKnowledge rebuild |
| conflict | explicit CONFLICT, never silently selected |

## 7. Explicit non-goals

- no P4 lifecycle state
- no Product Master duplication
- no parallel approval endpoint
- no autonomous verification
- no Recommendation scoring redesign
- no external research model/tier decision
- no dedicated research dossier table required for V1
- no silent conflict resolution

## 8. Implementation result

The implementation uses the existing Evidence and ProductKnowledge boundaries. The new Research Draft endpoint is an orchestration layer only.

This preserves the central HBI rule:

**NO ASSUMPTION / NO INVENTED DATA.**
