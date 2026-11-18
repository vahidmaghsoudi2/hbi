# HBI Product Intake — Stage 1 & 2 Reality Audit
**Audit date:** 2026-10-13  
**Mission:** [Issue #283](https://github.com/vahidmaghsoudi2/hbi/issues/283)  
**Consolidation source:** [Issue #278](https://github.com/vahidmaghsoudi2/hbi/issues/278)  
**Scope:** baseline/evidence reconciliation and end-to-end gap audit only.

## Executive disposition
- **Current master:** cc7848e472b837746e99103ea94ff4bb28eb0c2b — https://github.com/vahidmaghsoudi2/hbi/commit/cc7848e472b837746e99103ea94ff4bb28eb0c2b
- **Approved contract:** docs/architecture/SKIN_PRODUCT_INTAKE_EXECUTION_CONTRACT_v1.1.md — PO APPROVED.
- **G8:** BLOCKED / NOT VERIFIED. No independently reviewable non-fixture runtime package proves the same real Skin product through governed intake, approval/activation, stock/eligibility, and persisted recommendation readback.
- **No exact-master CI result verified** for the current SHA in the available Actions/status evidence. Green PR runs must not be transferred to master.
- **Highest-priority confirmed gap:** Product Review UI consumes a DTO that omits status and product_line, but the panel needs both to show lifecycle transitions and Skin-specific readiness.

## Stage 1 — Baseline and evidence integrity

### Current repo state
Current master is cc7848e472b837746e99103ea94ff4bb28eb0c2b. Issue #283 is open/reopened and its success condition explicitly says G8 is not accepted. The issue body still embeds the older 356f34f... SHA; later comment #6140128785 correctly records cc7848e... as current.

### Relevant PR states
| PR | State | Evidence boundary |
|---|---|---|
| #285 | Merged | Skin safety gate scoped to Product Line SKIN; not real pilot evidence |
| #332 | Merged | Product registration creates zero stock; separate Stock-In; Research Draft UI/API |
| #334 | Merged | Recommendation persistence/readback UI; not live runtime acceptance |
| #353 | Open/Draft/unmerged; head 22d327586b6c42125b25f21dfb746a2094138993 | Claim-integrity branch CI/browser proof green on this PR head only; not master |
| #355 | Open/Draft/unmerged; head 45db2a7fa5a818c9c48ca1520b615a09a6d76d0b | Disposable Numbuzin intake test; CI/browser proof green on PR head only |
| #347 | Open/Draft | Homepage Admin/session and Sales boundary |
| #354 | Open/Draft, stacked on #347 | Homepage navigation stage 1 |
| #348 | Open, not merged | Roadmap proposal, not implementation contract |
| #350 | Open/Draft/unmerged | Proposed warnings for nine historical documents; not yet on master |
| #351 | Open/Draft/unmerged | Proposed warnings for five historical pilot/gate reports; not yet on master |
| #289 | Open/Draft/unmerged | Old-base strategic roadmap proposal |

### Historical documents identified
These master files have stale status/next-action language and are now marked with warning banners on this audit branch; original text is retained:
- docs/01_project_control/product_intake/PRODUCT_INTAKE_MASTER_EXECUTION_ROADMAP.md — last reconciled 2026-09-07; says Contract v1 pending merge and phases not started.
- docs/01_project_control/product_intake/PRODUCT_INTAKE_LIVE_PROJECT_LEDGER.md — last reconciled 2026-09-07; records baseline 42cc77ec..., PR #33 as next action, and stale phase/gap statuses.

Other historical files still require the already-open warning proposals to be reviewed/merged: docs/01_project_state/HBI_PRODUCT_INTAKE_FORENSIC_REPORT.md (PR #351); strategy/generic contract/strategic baseline files (PR #350). Those draft PRs have not changed master.

### Browser proof boundary
- Master test: tests/browser/pilot-recommendation.spec.cjs.
- Fixture builder: scripts/prepare_pilot_browser_db.py seeds ISDIN-FOTOUTRA100-50ML, TEST-PILOT-BROWSER-FIXTURE evidence, and CUST-PILOT-1; it directly sets the fixture product ACTIVE and QA VALID.
- Workflow .github/workflows/pilot-browser-proof.yml uses disposable SQLite and uploads Playwright/log artifacts when present.
- User-reported local 1-pass result on cc7848e... has raw local artifacts not attached here.
- PR #355 CI artifacts are on 45db2a7..., not master. They are not current-master or real-product runtime proof.

## Stage 2 — End-to-end gap matrix

| Path item | Finding | Status |
|---|---|---|
| Intake entry / identity | Product Line is operator-selected/required; server creates DRAFT / NEEDS_REVIEW / PENDING and inventory anchor 0 / OUT_OF_STOCK. | Implemented in source; exact-master runtime not verified |
| Duplicate boundary | EXISTING blocks; POSSIBLE_MATCH requires operator decision NEW bound to the same identity snapshot. UI's RENAME decision does not auto-rename; operator must correct and re-check. | Implemented in source; known UX limitation |
| Research / provenance | Source-attributed Research Draft and PENDING/UNKNOWN evidence exist. | Partial |
| Claim taxonomy | Master schema accepts arbitrary claim_type strings; EvidenceService only enforces the FACT source gate. A master test uses BENEFIT although v1.1 freezes FACT, MANUFACTURER_CLAIM, EVIDENCE, INFERENCE, UNKNOWN, CONFLICT. | **Confirmed gap**; PR #353 unmerged |
| Skin safety | SKIN requires verified contraindication evidence or explicit UNKNOWN; untrusted/conflicting evidence does not satisfy the gate. | Implemented in source; no real-product runtime proof |
| Review/lifecycle UI | ProductFacade._to_product_dto omits status and product_line. Both /products/{id} and /products/manage use this DTO; ProductReviewPanel reads those fields to show status, Skin safety readiness and transition buttons. | **P0 confirmed UI/API contract gap**: status-based transition buttons cannot render; client-side Skin indicator cannot identify SKIN. Server-side governance remains authoritative |
| Evidence conflict resolution | Backend /evidence/{evidence_id}/resolve exists, but frontend client and ProductReview/ProductIntake panels expose no resolution action. Readiness blocks conflict rows. | **Confirmed operational gap** |
| Product Master / stock | Product registration does not invent stock. Stock-In API and PurchasePage implement explicit receipt and movement ledger. | Implemented in source; same-product real runtime/readback not verified |
| Eligibility / stock | Candidate query requires ACTIVE, identity VERIFIED, QA VALID, non-OUT_OF_STOCK and available minus reserved > 0; RecommendationService repeats sellable-quantity check. | Implemented in source. Earlier Issue #278 claim that reserved quantity was ignored is stale against current master |
| Product Line candidate boundary | Recommendation candidate query filters lifecycle/identity/QA/stock but does not filter product_line. | **Confirmed code gap / contract impact to resolve**: a non-SKIN product could enter a Skin-case candidate set if other gates/matching allow it. Any fix must not alter scoring/weights |
| Structured skin intelligence | ProductKnowledge has ingredients, ingredient_roles, claimed_benefits, known_use_cases, contraindications, usage_instructions and manufacturer_claims; no dedicated target_concerns, active_ingredients or avoid_conditions fields. | **Structured-data gap / separate WP required**; v1.1 defers future structured skin attributes to acceptance criteria |
| Recommendation persistence/readback | Master browser spec tests generate → persisted readback → reload without regeneration → fail-closed. Fixture is pre-seeded ACTIVE. | Fixture regression exists; real intake path not verified |
| Real operator/customer-context pilot | No independently reviewable non-fixture runtime package shows one real product through intake, review, ACTIVE, stock, eligibility and persisted recommendation readback. | **G8 BLOCKED / NOT VERIFIED**; PR #355 is disposable/in-memory and leaves the candidate DRAFT |

## Stage 3 planning order — not executed
1. P0: correct Product DTO/review-read contract and add tests for status + product_line without casually widening public data exposure.
2. P1: review/complete claim-integrity PR #353 against the frozen six-type contract and reconcile legacy BENEFIT usage.
3. P1: resolve the Skin-case product_line candidate boundary without scoring redesign.
4. P1: expose governed conflict resolution in operator UI and test audit/readiness consequences.
5. P2: define acceptance criteria for target concerns, active ingredients and avoid conditions before schema/API work.
6. G8 runtime gate: use a non-production runtime and operator session; capture exact SHA, screens/logs, duplicate result, persisted product/evidence readback, stock receipt, recommendation readback and cleanup proof.

## Explicit non-actions
- No code/schema/API/migration/scoring changes.
- No tests executed by this audit; test files and workflow artifacts were inspected as repository evidence.
- No real product created, approved, activated, stocked or recommended.
- No production data or Product A–D touched.
- No PR merged and no merge authorization implied.
- G8 remains **BLOCKED / NOT VERIFIED**.

**Stage 1 and Stage 2 audit complete.** Stage 3 is the next execution stage; it must remain bounded and use exact-SHA tests/evidence before independent verification.
