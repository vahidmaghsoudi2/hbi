# Activity 43 — Implementation Phase Tracking & Dependency Matrix

**Project:** HBI Hair-Color Consultation  
**Status:** Documentation baseline completed; H0 authorized on 2026-11-20 for bounded H1 validation only. H1 focused tests executed twice; H1 acceptance remains PARTIAL. No H2, real-customer use, merge, or release authorization.  
**Source baseline:** Activity 42 handoff package (PR #643), roadmap reconciliation (PR #644), owner decisions captured in project context.

## 1. Tracking principles
- A stage is complete only when its deliverables and verification evidence are recorded; PR creation alone is not completion.
- Documentation, synthetic implementation, specialist review, tests, integration, and release are distinct evidence classes.
- Pending PO decisions and external specialist review remain pending; do not convert them into approvals.
- The six PO-excluded product-document axes remain out of scope and must not be reintroduced as blockers.
- Use synthetic/test data only until an explicit customer-use gate is approved.
- No PR merge or release is authorized by this matrix.

## 2. H0–H6 dependency and gate matrix

| Stage | Scope | Dependencies | Deliverables | Entry gate | Exit evidence | Current status |
|---|---|---|---|---|---|
| H0 | PO gate and baseline | None | PO decision/scope, baseline refs, environment, merge strategy | PO review of documentation baseline and scope | Decision record with scope and owner; dependency chain reconciled | **AUTHORIZED — 2026-11-20, limited to isolated H1 validation with synthetic data; baseline HEAD 3478f65e5ec2f28c0b4f5592c1abf62be31272b7** |
| H1 | Domain/catalog foundation | H0 | Catalog identity, exact lookup, owner rules, typed intake/current-base/target/history/region data | H0 scope authorization; approved baseline | Code/contracts, unit tests, fail-closed tests, readback, criterion-level acceptance | **PARTIAL — focused 11-file suite: 118 passed twice; 59-criterion disposition still open (preliminary: 32 PASS / 17 PARTIAL / 10 NOT TESTED)** |
| H2 | Consultation engine controls | H1 | State machine, transitions, gaps, option controls, rejection suppression, version/dependency invalidation, stop/restart, acceptance/consent | H1 verified and accepted | State/contract tests and synthetic scenarios | **Not started — blocked until H1 acceptance closes** |
| H3 | Evidence and specialist review | H2 (evidence structures can be prepared earlier without claiming review) | Evidence ledger, topic mapping, review records, correction gates | Evidence/reviewer authority available; PO scope | Traceable actual review/evidence; pending remains pending | **Structural preparation documented in Activities 36–39; actual specialist review and evidence-backed findings remain pending** |
| H4 | API/persistence/UI integration | H1, H2, H3 | API schemas, versioned case persistence, append-only decisions/reviews, UI state/uncertainty/consent | Contracts accepted; H3 output gates defined | Integration tests, schema checks, synthetic fixtures, audit trace | Not started |
| H5 | Verification | H1–H4 | Unit, transition, contract, integration, regression, security/access checks; CI | Runnable environment and test suite | Actual run IDs/logs, results, defects/residual risks | **PARTIAL — focused local H1 suite executed twice; H1–H4 full verification and CI for the two local corrections are not established** |
| H6 | PO release decision | H5 | Release scope decision, residual-risk disposition | Verification evidence and specialist scope approvals where required | Explicit Go/No-Go record | Pending PO decision |

## 3. Work that can proceed without external review
- Clarify data types, contract semantics, reason codes, dependency maps, and acceptance tests.
- Prepare synthetic test fixtures and documentation.
- Reconcile branch/PR dependencies and describe merge strategy; do not merge.
- Prepare review topics and evidence traceability without filling reviewer conclusions.
- Validate consistency of owner-defined rules within their approved scope.

## 4. Hard stops / non-authorized actions
- No customer-facing consultation or real service execution.
- No deterministic outcome from a photo alone; no inferred pigment, porosity, structure, or chemical history from image.
- No chemistry/performance equivalence based on brand or shade-code similarity.
- No automatic promotion of pending specialist/PO status.
- No auto-resume after stop.
- Acceptance is not execution consent.
- ENGINE_FAIL suppresses run output.
- No merge, deployment, release, or use of customer data.

## 5. Chat 2 completion / current H1 disposition

Activity 43 is completed as a tracking matrix. Chat 2's baseline-contract specification is documented separately. The original H0-pending statement was accurate when Chat 2/3 documents were first written; it is superseded for current-status purposes by the PO's limited authorization dated 2026-11-20.

H0 is now authorized only for isolated H1 validation with synthetic/test data. The baseline is `3478f65e5ec2f28c0b4f5592c1abf62be31272b7`. The focused 11-file H1 test suite ran twice with Python 3.14.6 / pytest 9.1.1: 118 passed, 0 failed, 0 skipped, 0 xfailed in each run. The two local corrections present during execution remain uncommitted and are not on this GitHub branch.

**H1 is not yet accepted.** The test run is successful evidence for the listed files only. The preliminary 59-criterion map (26 PASS / 19 PARTIAL / 14 NOT TESTED) must be reconciled to exact assertions. H2 remains blocked until H1 acceptance is closed.

**Next action:** Activity 45 — close the H1 acceptance matrix. Do not begin H2, real-customer data processing, customer-facing advice, service execution, merge, release, or production deployment under this authorization.


## 6. H0 authorization and H1 execution update — 2026-11-20

PO authorized the following bounded work:
- isolated H1 validation only;
- synthetic/test data only;
- baseline HEAD `3478f65e5ec2f28c0b4f5592c1abf62be31272b7`;
- no H2 implementation, real customer data, customer-facing advice, service execution, push, merge, release, or production deployment.

Focused H1 execution used Python 3.14.6 / pytest 9.1.1 and the 11-file command recorded in `chat-3-h1-focused-test-spec.md`. Two runs each reported 118 passed, 0 failed, 0 skipped, 0 xfailed (8.56 s and 6.01 s). Two local uncommitted corrections were present in the worktree; they are not in this GitHub branch.

H1 remains PARTIAL because test execution success is narrower than full acceptance. The 59-criterion preliminary mapping (26 PASS / 19 PARTIAL / 14 NOT TESTED) must be reconciled to exact assertions before H1 can be closed. H2 entry remains blocked until that closeout is complete.


### Activity 45 — criterion-level source coverage

The focused test source was mapped criterion by criterion. Corrected totals: **59 = 32 PASS / 17 PARTIAL / 10 NOT TESTED / 0 FAIL**. This supersedes the earlier provisional 26/19/14 mapping. PASS here means a direct assertion exists; it does not mean specialist acceptance. The 118-pass local execution remains separate evidence for the selected 11 files only. H1 remains PARTIAL; H2 remains blocked.
