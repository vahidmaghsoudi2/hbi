# S01 Decision Matrix and Acceptance Gates — Proposal v0.1

**Date:** 2026-10-20  
**Status:** PROPOSED / NOT APPROVED  
**Parent work:** [PR #416](https://github.com/vahidmaghsoudi2/hbi/pull/416)  
**Purpose:** Convert the current S01 evidence and intake draft into explicit decisions, ownership boundaries, and testable gates. This document does not accept a skin problem, authorize clinical action, or approve product matching.

## 1. Decision matrix

| ID | Decision / question | Current evidence-based position | Decision owner | Gate to proceed |
|---|---|---|---|---|
| D01 | Is P01 (dry skin/xerosis) a concept distinct from P02? | Keep separate concepts; relationship does not prove equivalence. Preserve the already approved P01 status. | PO + designated medical reviewer | Record explicit decision and rationale in canonical records. |
| D02 | Is P02 operationally classifiable from customer answers alone? | No. Candidate definition is not an accepted operational criterion. Keep `Identified + Linked / Undetermined`. | PO + designated medical reviewer | Either validate a non-instrument intake rule independently, or declare P02 non-classifiable in initial release. |
| D03 | Will initial S01 intake support instrument measurements? | Unresolved. No instrument or threshold is assumed. | PO + implementation owner + medical reviewer | Decide yes/no. If yes, specify device/method, site, unit, quality checks, validation and ownership before implementation. |
| D04 | Are draft Q1–Q6 ready for customers? | No; they are draft prompts only. | PO + medical reviewer + user-experience reviewer | Comprehension test, revisions, documented approval, versioned question IDs. |
| D05 | How are customer report and operator observation separated? | They must be stored as different source types and must not silently overwrite each other. | Product/operations owner | Demonstrate separate entry and display paths, including disagreements and unknown values. |
| D06 | What creates a clinical interpretation? | Only a separately documented rule/review process with traceable evidence; not a raw answer or manufacturer claim. | Medical reviewer + evidence owner | Approved interpretation criteria and review trail exist. |
| D07 | What authorizes a referral or safety decision? | This proposal creates no thresholds or referral rules. | Medical/safety owner | A separate approved protocol exists and is tested; otherwise no new rule is activated. |
| D08 | When can a problem be related to a product? | Not during this S01 intake proposal. Problem-to-product links belong to a distinct evidence-backed relationship layer. | Product-knowledge owner + medical reviewer | Relationship type, direction, evidence, applicability, limitations and review state are defined in a separate artifact. |
| D09 | Can a problem or product relation trigger a recommendation automatically? | No. No scoring, confidence weighting, best/worst ranking, or automatic acceptance is introduced here. | PO | Separate recommendation contract and explicit approval are required. |
| D10 | What happens to unanswered or conflicting data? | Preserve `SKIPPED`, `NOT_ASKED`, `UNKNOWN`, and `CONFLICTING` distinctly. Do not infer “no”. | Data/implementation owner | Tests prove each state survives storage, display and export without being collapsed. |

## 2. Boundary between the three workstreams

### A. Skin-problem intake (this workstream)
Owns: customer-reported experience, versioned questions, operator-observation fields, provenance, uncertainty, and the status of each problem concept.

Does not own: product catalog entry, manufacturer-claim approval, product efficacy conclusions, product ranking, or treatment authorization.

### B. Product entry and product knowledge
Owns: product identity and catalog attributes; ingredient/claim data with source and origin; distinction between manufacturer claims and independently supported evidence.

Does not own: diagnosing the customer's skin problem from product text or silently converting an ingredient match into a suitability conclusion.

### C. Problem-to-product relationship layer (later, separate workstream)
Owns: explicit relationship records linking a defined problem or customer need to a product attribute or evidence-backed claim. A relationship must specify its semantic type; a shared ingredient or similar wording alone is insufficient.

Minimum proposed relationship fields:
- `relationship_id`
- `source_concept_id` and `target_product_or_attribute_id`
- `relationship_type` (controlled vocabulary, not free-text similarity)
- `direction` and `scope/applicability`
- `evidence_refs` and `evidence_kind` (manufacturer claim vs independent evidence)
- `limitations_or_contraindications` (or explicit unknown)
- `review_status`, reviewer role, review date and rationale
- `validity_status` (proposed, active, superseded, rejected)

These are design candidates only. Do not create product relations until their controlled vocabulary and acceptance rules are separately reviewed. A relation is not automatically a recommendation.

## 3. Acceptance gates — sequence

1. **Gate S01-A — Concept boundary:** settle D01–D02; record whether P02 is deliberately non-classifiable in the first release.
2. **Gate S01-B — Intake wording:** user-comprehension review and approval for Q1–Q6; retain a versioned change history.
3. **Gate S01-C — Data contract:** approve the field contract, enumerations, unknown/conflict handling, and audit requirements.
4. **Gate S01-D — Operational boundary:** identify the approved safety/referral protocol or explicitly state that this work does not implement one.
5. **Gate S01-E — Separation test:** verify that customer statements, operator observations, instrument readings, scientific interpretations, and operational decisions cannot be confused in stored records or UI.
6. **Gate S01-F — Product relationship handoff:** create a separate proposal for relationship types and evidence rules only after the intake concept boundary is settled.
7. **Gate S01-G — Release review:** PO and designated reviewers explicitly accept the scoped deliverable; CI success alone does not constitute clinical or product-knowledge approval.

## 4. Minimum test scenarios for future implementation

| Scenario | Expected behavior |
|---|---|
| Customer reports tightness after washing | Store as customer report; do not auto-accept P01/P02. |
| Customer says “unsure” | Store `UNKNOWN`; do not translate to “no”. |
| Customer skips a question | Store `SKIPPED`; do not treat as absent symptom. |
| Operator observation differs from customer report | Keep both with separate provenance; flag for review if needed. |
| Instrument value has no unit or method | Mark measurement incomplete/not interpretable; do not compare to a threshold. |
| Product marketing says “hydrates” | Store as manufacturer claim with source; do not infer proven efficacy or suitability. |
| Product shares an ingredient with a product discussed for P02 | Do not create a problem relation from ingredient overlap alone. |
| No approved referral protocol exists | Do not invent a threshold or silently create a referral decision. |
| A reviewer changes an interpretation | Preserve old value, new value, reviewer role, timestamp and rationale. |

## 5. Explicit non-goals

- No migration or production database change.
- No new clinical diagnosis or medical advice rule.
- No P01/P02 merge or status change.
- No numeric confidence score or product-ranking formula.
- No automatic product suitability or recommendation.
- No new referral threshold.
- No declaration that CI or browser proof establishes clinical validity.

## 6. Current status

All gates remain **OPEN** until the named decision/approval evidence is recorded. The current PR contributes documentation and design proposals only. P02 remains `Identified + Linked / Undetermined`; draft questions remain unapproved for deployment.
