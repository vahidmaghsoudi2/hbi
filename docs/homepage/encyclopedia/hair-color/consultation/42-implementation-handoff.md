# فعالیت ۴۲ — بستهٔ تحویل برای مرحلهٔ پیاده‌سازی

## وضعیت و اختیار
این بسته handoff است؛ **مجوز شروع پیاده‌سازی یا production deployment نیست**. PO acceptance Activity 41 pending است. PRهای documentation/domain-contract chain باز و Draft هستند؛ tests/CI این work sequence اجرا نشده.

## Scope of implementation handoff
Implement only approved architecture/domain contracts, in a synthetic/test environment first:
- structured intake + source/confidence/uncertainty/conflict;
- target preference/current base/history/regional map separation;
- catalog identity/numbering/owner rules, fail-closed matching;
- motor/response/workflow state machines and transition guards;
- data/knowledge/engine gap distinction;
- option validation/ranking/rejected-option control;
- versioning/dependency invalidation and stop/restart;
- separate acceptance and execution consent;
- evidence/review/correction records with audit trace.

## Dependency-based staged plan
### H0 — PO gate and baseline
- Record PO decision and scope (documentation only vs implementation).
- Confirm PR dependency/base chain and merge strategy; keep Drafts unmerged until reviewed.
- Select test/runtime environment; do not use customer data.

### H1 — Domain/catalog foundation
- Catalog raw identity and fail-closed lookup.
- Owner-defined rules and exact scope.
- Typed domain inputs for target/current base/history/regions.
- No fuzzy product equivalence or chemistry claims.

### H2 — Consultation engine controls
- Four motor states and five response states.
- Ten workflow states and allowed transitions.
- Missing/uncertain/conflicting inputs; dependency invalidation.
- Candidate validity, max-three policy and suppression.
- Stop request/restart and safety/scope guards.
- Client question/acceptance/execution consent separation.

### H3 — Evidence and specialist review
- Rule evidence audit and topic inventory.
- Review-record schema, evidence ledger reconciliation, correction gates.
- Keep review status pending until actual reviewer record/evidence is captured.
- No six PO-excluded product-document axes reintroduced as blockers.

### H4 — API/persistence/UI integration
- Only after H0–H3 are accepted.
- Persist versioned case and append-only decision/review records.
- API contract: validation, response states, explicit reasons, no internal control leakage.
- UI: clarification, question, reject/accept, consent separately; stop path; uncertainty/reason display.
- Synthetic fixtures only.

### H5 — Verification
- Unit tests per module, state transition tests, contract tests, dependency invalidation tests, fail-closed regression tests.
- Run lint/type checks and CI; report actual command/run IDs.
- Verify test coverage for DATA_GAP / KNOWLEDGE_GAP / ENGINE_FAIL distinct paths.
- Validate no suggestion appears after safety/engine stop; no rejected suggestion resurfaces.
- Runtime/DB integration tests and audit trail.
- Do not claim tests passed until execution evidence is read.

### H6 — PO release decision
- Reconcile implementation against acceptance matrix.
- Specialist review and evidence must be scoped and traceable.
- PO explicitly decides release scope; customer-facing advice/execution authorization remain separate.

## Deliverables for implementation phase
- Code modules with typed contracts and dependency graph.
- Test suites and synthetic fixtures.
- API/schema documentation.
- Versioned persistence/audit record model.
- UI interaction states and accessible error/uncertainty copy.
- Verification evidence and residual-risk register.
- PO decision/release record.

## Hard boundaries
- No exact outcome/formula from photo alone.
- No chemical compatibility or product performance inferred from shade-code similarity.
- No customer use or real service execution.
- No auto-resume after client stop.
- Acceptance does not authorize execution.
- Pending specialist/PO decisions do not get silently promoted.
- Internal failure suppresses run output.
- No PR merge, branch deletion, or release action from this handoff.

## Readiness
Implementation package is prepared for PO review. Implementation readiness remains **blocked by PO decision, review/merge strategy, actual tests/CI, specialist evidence, and runtime integration plan**.

## Next
Activity 43 — establish implementation-phase tracking matrix and owner/dependency tracking; no activity completion is inferred from PR creation alone.
