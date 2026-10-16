# HBI Product Intake Roadmap and Phase 1 Execution Record

**Status:** Phase 0 = COMPLETE (SSOT files merged); Phase 1 = PREPARATION / real operator pilot NOT STARTED; G8 = **BLOCKED / NOT VERIFIED**  
**Source of truth:** GitHub repository `vahidmaghsoudi2/hbi`  
**Verified master baseline for this correction:** `310ce38f67c7f2c864e35bf78293cd3ad3b810cd` (current master after PR #369 merge; documentation branch still needs baseline reconciliation)  
**Last updated:** 2026-10-15

## 1. Purpose and authority

This document is the operational roadmap and evidence index for the Product Intake execution pilot. It does not replace or amend the approved Product Intake contract. If there is a conflict, the approved contract and explicit Product Owner decisions govern.

Primary references:
- [Skin Product Intake Execution Contract v1.1](SKIN_PRODUCT_INTAKE_EXECUTION_CONTRACT_v1.1.md)
- [P4 Product Intake Governance Contract V1](../P4_PRODUCT_INTAKE_GOVERNANCE_CONTRACT_V1.md)
- [Issue #283 — governing mission](https://github.com/vahidmaghsoudi2/hbi/issues/283)
- [PR #360 — claim integrity and evidence/UI consolidation](https://github.com/vahidmaghsoudi2/hbi/pull/360)
- [PR #361 — Product menu action grouping](https://github.com/vahidmaghsoudi2/hbi/pull/361)
- [PR #355 — disposable Numbuzin intake API test (draft; not G8 proof)](https://github.com/vahidmaghsoudi2/hbi/pull/355)

## 2. Current baseline and completed work

### Phase 0 — SSOT baseline on master: COMPLETE

Verified current master baseline: `310ce38f67c7f2c864e35bf78293cd3ad3b810cd` (includes PR #369).

Exact-SHA push checks:
- [HBI CI run 38396795619](https://github.com/vahidmaghsoudi2/hbi/actions/runs/38396795619) — success
- [HBI Auto Tasks / Live test evidence run 38396795733](https://github.com/vahidmaghsoudi2/hbi/actions/runs/38396795733) — success
- Exact-SHA checks `test`, `governance-tests`, and `Live test evidence` succeeded.

The SSOT files are present on master following PR #364, merged at `7d962720a60c1291b8c21360dff0cc95b6fc0d1a`; Phase 0 is COMPLETE for documentation placement only. The merge and green CI are not proof that the real G8 operator pilot passed. The Phase 0 outcome is recorded in [Issue #283 comment](https://github.com/vahidmaghsoudi2/hbi/issues/283#issuecomment-6145815790).

### Relevant merged work

- PR #360 merged at `0a2ec9b477f89954ba1865ec59e3701a5a0f3831`. The reviewed scope consolidated claim taxonomy/validation, manufacturer-claim destination guard, Skin candidate boundary and evidence-conflict UI while preserving scoring and Product A–D boundaries.
- PR #361 merged at `868fdbb1c0cee620a655eec06899043139e13428`. UI-only grouping of product actions under the Products menu.
- PR #369 merged at `310ce38f67c7f2c864e35bf78293cd3ad3b810cd`, adding fail-closed G8 isolated-runner evidence finalization. This is pilot infrastructure, not real-pilot acceptance.
- PRs #353 and #357 were closed as superseded, not merged. See the Issue #283 execution record.

## 3. Product Intake lifecycle

The governed target lifecycle is:

`INTRODUCE → DUPLICATE → RESEARCH → EVIDENCE → SAFETY → VALIDATE → REVIEW → APPROVE → ACTIVATE → PRODUCT MASTER → RECOMMENDATION-READY → REAL PRODUCT PILOT`

The pilot must demonstrate actual permitted transitions and persisted readback. A successful unit test, API test, or CI workflow is supporting evidence, not a substitute for operator execution and independent acceptance.

## 4. Phase 1 — isolated G8 execution pilot

**Status: PREPARATION; real operator pilot NOT STARTED.** Phase 0 is complete. Pilot execution remains blocked until the isolated runner, environment, and evidence-capture process are verified; no real operator session is claimed.

### Scope

Run the Skin candidate through the existing Product Intake flow in a disposable isolated environment, using explicit operator choices and real UI/API interactions where required by the contract. Use the temporary Numbuzin No.9 NAD+ BIO Lifting-sil Essence, 50 mL only as a test candidate. Do not treat manufacturer marketing statements as independently verified efficacy evidence.

### Hard safety and change-control boundaries

- No production database access or mutation.
- No schema changes or migrations.
- No Product A–D mutation.
- No stock receipt or fabricated inventory; stock must remain zero unless separately authorized and physically verified.
- No recommendation scoring, weighting, threshold, or EvidenceReadiness semantic changes.
- No inferred `product_line=SKIN`; the operator must explicitly select it.
- No activation or recommendation eligibility before the contract's required gates pass.
- No merge without explicit Product Owner authorization.
- Capture evidence in a disposable environment and prove cleanup afterward.

### A1–A9 acceptance ledger

Every row requires a raw artifact or reproducible log, timestamp/context, exact commit/environment identification, and an independent reviewer disposition. Mark a row PASS only when the evidence itself proves the requirement.

| ID | Required proof | Current disposition |
|---|---|---|
| A1 | Explicit product identity and operator-selected `product_line=SKIN`; no inference. Physical package/market identity unknowns remain explicit. | PARTIAL — API test only |
| A2 | DuplicateCheck executed before creation; duplicate and unknown-identity cases handled safely. | PARTIAL — NEW path tested; negative/edge cases not proven here |
| A3 | Initial lifecycle state persisted and read back; no premature state transition. | PARTIAL — draft state tested via ORM readback |
| A4 | Source-attributed research/evidence persisted; manufacturer claims remain claims, unknowns remain unknown. | PARTIAL — three draft assertions tested |
| A5 | Invalid claim types/mappings rejected; required FACT provenance rules preserved; conflict handling evidenced. | NOT VERIFIED by PR #355 |
| A6 | Safety, review, permissions, and approval gates enforced; unauthorized/premature transitions denied. | NOT VERIFIED by PR #355 |
| A7 | Authorized approval/activation only after prerequisites; resulting state and audit history read back. | NOT VERIFIED; current test intentionally stops before approval/activation |
| A8 | Recommendation eligibility/readback for the intended Skin case after authorized gates; product-line boundary enforced; scoring unchanged. | NOT VERIFIED |
| A9 | Disposable environment and test data cleanup independently proved; production isolation confirmed. | PARTIAL — fixture teardown in test; no independent post-run cleanup artifact |

### Existing PR #355 evidence

[PR #355](https://github.com/vahidmaghsoudi2/hbi/pull/355) is a draft test-only change at head `45db2a7fa5a818c9c48ca1520b615a09a6d76d0b). Both workflows succeeded on that head:
- [HBI CI run 38315913219](https://github.com/vahidmaghsoudi2/hbi/actions/runs/38315913219)
- [Pilot Browser Proof run 38315913216](https://github.com/vahidmaghsoudi2/hbi/actions/runs/38315913216)

The test covers duplicate check before creation, explicit Skin selection, persisted draft/review-pending state, zero inventory, three source-attributed draft assertions and evidence readback, and an in-memory fixture. It does **not** prove a real operator/customer-context browser session, the complete safety/review/approval/activation lifecycle, recommendation eligibility, negative guard tests for all A5/A6 cases, or independently evidenced cleanup. It must remain draft/unmerged absent separate authorization.

## 5. Phase 1 execution sequence

1. Freeze the baseline and record exact commit SHA, workflow runs, environment and operator identity/role.
2. Verify disposable isolation before creating any candidate data.
3. Execute duplicate check and explicitly create the candidate as Skin; record UI/API requests and responses.
4. Record research assertions with provenance and claim taxonomy; preserve manufacturer claims and explicit unknowns without upgrading them to facts.
5. Exercise evidence validation, invalid mappings, conflict resolution, safety/review permissions and blocked transitions.
6. Complete approval/activation only if each contract prerequisite is satisfied and the authorized role performs the transition.
7. Verify Product Master and recommendation eligibility/readback only after authorized activation; prove no scoring behavior was changed.
8. Export raw evidence and logs; prove test rows/environment are removed and production remains untouched.
9. Obtain independent Grok2 review against A1–A9. Record PASS/FAIL/NOT VERIFIED per criterion with artifact links.
10. Declare G8 complete only if every required criterion passes. Any missing evidence keeps G8 BLOCKED / NOT VERIFIED.

## 6. Phase 1 completion package

The execution owner must attach:
- exact baseline/head SHA and environment identification;
- operator session chronology with timestamps;
- raw requests/responses and UI/browser proof;
- evidence/provenance records and persisted readbacks;
- positive and negative gate-test results;
- Product Master and recommendation eligibility readbacks, if legitimately reached;
- cleanup and production-isolation proof;
- A1–A9 acceptance ledger;
- independent Grok2 review and final disposition.

Do not substitute a narrative summary for raw artifacts.

## 7. Current decision

Phase 0 SSOT placement is COMPLETE following merged PR #364. Phase 1 is in preparation; the real operator pilot has NOT STARTED. PR #355 is supporting API-test evidence only, not the real pilot and not G8 proof.

**Current gate: G8 = BLOCKED / NOT VERIFIED.**

The next action is to complete safe preparation for the isolated operator pilot and collect raw A1–A9 artifacts only in an approved disposable environment. G8 remains BLOCKED / NOT VERIFIED until the evidence package meets the contract and is independently reviewed. No production changes or merge are authorized by this document.
