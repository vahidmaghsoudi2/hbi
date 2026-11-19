# Activity 43 — Implementation Phase Tracking & Dependency Matrix

**Project:** HBI Hair-Color Consultation  
**Status:** Completed as documentation baseline; does not authorize runtime implementation or merge.  
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
| H0 | PO gate and baseline | None | PO decision/scope, baseline refs, environment, merge strategy | PO review of documentation baseline and scope | Decision record with scope and owner; dependency chain reconciled | **Pending PO decision** |
| H1 | Domain/catalog foundation | H0 | Catalog identity, exact lookup, owner rules, typed intake/current-base/target/history/region data | H0 scope authorization; approved baseline | Code/contracts, unit tests, fail-closed tests, readback | Not started |
| H2 | Consultation engine controls | H1 | State machine, transitions, gaps, option controls, rejection suppression, version/dependency invalidation, stop/restart, acceptance/consent | H1 verified | State/contract tests and synthetic scenarios | Not started |
| H3 | Evidence and specialist review | H2 (evidence structures can be prepared earlier without claiming review) | Evidence ledger, topic mapping, review records, correction gates | Evidence/reviewer authority available; PO scope | Traceable actual review/evidence; pending remains pending | Pending external review; structural prep documented |
| H4 | API/persistence/UI integration | H1, H2, H3 | API schemas, versioned case persistence, append-only decisions/reviews, UI state/uncertainty/consent | Contracts accepted; H3 output gates defined | Integration tests, schema checks, synthetic fixtures, audit trace | Not started |
| H5 | Verification | H1–H4 | Unit, transition, contract, integration, regression, security/access checks; CI | Runnable environment and test suite | Actual run IDs/logs, results, defects/residual risks | Not started; prior tests/CI not run |
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

## 5. Chat 2 completion / next chat
Activity 43 is completed as a tracking matrix. Chat 2's baseline-contract specification is documented separately. Chat 3 may begin only after the H0 baseline/PO gate and the Chat 2 contract handoff are reviewed/authorized; Chat 3 must implement H1 only and stay in synthetic/test scope.
