# HBI Consultation Outcome / Follow-up Reality Gate v0.2

| Field | Value |
|---|---|
| Baseline | `f31df40db18e7365eed096fc804a5aebc0fa6924` |
| Gate | HBI-CONSULTATION-OUTCOME-FOLLOWUP-REALITY-GATE-002 |
| Scope | Customer Response → Outcome / Follow-up |
| Implementation | **NOT AUTHORIZED BY THIS GATE** |
| Verdict | **READY FOR NEXT VERTICAL SLICE** |

## 1. Baseline

This audit is anchored to the actual current Master after PR #233:

`f31df40db18e7365eed096fc804a5aebc0fa6924`

PR #233 is merged and Issue #232 is completed. The explicit Customer Response action is current repository reality.

## 2. Files / Code Paths

Direct evidence inspected at this baseline:
- `app/models/feedback.py`
- `app/services/feedback_service.py`
- `app/api/routers/specialist.py`
- `tests/test_consultation_vertical_slice_001.py`
- `app/core/audit.py`
- `docs/architecture/HBI_CONSULTATION_FOLLOWUP_OUTCOME_REALITY_GATE_v0.1.md`

Current relevant API paths:
- `POST /api/v1/specialist/feedback`
- `POST /api/v1/specialist/feedback/customer-response`
- `GET /api/v1/specialist/feedback/case/{case_id}`

Evidence statuses: **CONFIRMED IN CODE / CONFIRMED IN TEST / CONFIRMED IN DOC / NOT FOUND / CONFLICT / UNKNOWN**

## 3. Customer Response Reality

**CONFIRMED IN CODE / CONFIRMED IN TEST**

Current runtime path:

`Authenticated Customer → Owned Case → Existing Recommendation → Customer Response → Feedback(source=CUSTOMER) → Case Retrieval → Audit`

The explicit endpoint requires authentication, verifies Case ownership, requires Recommendation linkage, forces `source=CUSTOMER`, reuses `FeedbackService`, validates Recommendation existence and Case linkage, persists Feedback, and emits response-specific audit events.

Focused tests cover unauthenticated access, foreign Case, missing Recommendation, foreign Recommendation/Case linkage, durable persistence, CUSTOMER source and retrieval.

## 4. Outcome Runtime Contract

### Carrier
**CONFIRMED IN CODE**

No dedicated Outcome entity/service exists. V1 uses nullable `Feedback.outcome`.

### Values
**CONFIRMED IN CODE / CONFIRMED IN DOC**

Documented labels:
- `ACCEPTED`
- `REJECTED`
- `PARTIAL`
- `FOLLOW_UP_NEEDED`

Runtime normalizes input to uppercase but does not enforce these four values through an enum or closed service validation. Therefore this is documented vocabulary, not a closed runtime state machine.

### Semantic boundary
**CONFIRMED IN CODE / CONFIRMED IN DOC**

Feedback outcome is reported response data. It is not proof of independent Customer Choice, purchase, product usage, observed outcome or outcome assessment.

## 5. Customer Choice Reality

**NOT FOUND**

No independent CustomerChoice model, service, persistence field or API was verified. Specialist Override is an operator action. Purchase remains transaction evidence.

## 6. Follow-up Runtime Reality

### Field
**CONFIRMED IN CODE**

`Feedback.follow_up_at` is nullable DateTime, accepted by Feedback creation and returned by Case-scoped retrieval. The explicit Customer Response request also carries this optional field.

### Lifecycle
**NOT FOUND**

No dedicated Follow-up entity, scheduler, reminder, completion, cancellation, rescheduling or single-active-follow-up contract was verified.

Current reality is **follow-up date metadata on Feedback, not a Follow-up subsystem**.

### Audit
**CONFIRMED IN CODE**

Feedback creation emits audit events. Customer Response emits response-specific audit evidence containing the Case and Recommendation target and response state.

## 7. Usage / Observed Outcome Reality

| Concept | Status |
|---|---|
| Product Usage entity/service | **NOT FOUND** |
| Customer usage confirmation | **NOT FOUND** |
| Observed Outcome entity/service | **NOT FOUND** |
| Outcome Assessment entity/service | **NOT FOUND** |
| Automatic recommendation learning/update | **NOT FOUND / OUT OF SCOPE** |

## 8. Traceability

**CONFIRMED IN CODE / CONFIRMED IN TEST**

Durable response path:

`Customer → owned Case → Recommendation → Feedback(source=CUSTOMER) → outcome`

Feedback carries both Case and Recommendation identifiers, and creation validates that the Recommendation belongs to the Case.

Purchase is separate:

`Recommendation → SaleItem → Sale`

This is transaction evidence, not independent Customer Choice evidence.

Retrieval boundary is Case-scoped. No dedicated Recommendation-scoped Feedback retrieval endpoint was verified.

## 9. Documentation Consistency

**CONFIRMED IN DOC / PARTIAL CONSISTENCY**

The v0.1 gate correctly deferred richer Outcome, Usage and Follow-up domains.

Older documentation that describes Customer Response as proposed is historical after PR #233. Current safe vocabulary is:
- Customer Response: implemented as explicit CUSTOMER-sourced Feedback;
- Outcome: nullable Feedback field with documented four-label vocabulary but open runtime values;
- Customer Choice: no independent persisted construct;
- Purchase: Recommendation → SaleItem transaction trace;
- Usage / Observed Outcome / Outcome Assessment: not implemented;
- Follow-up: optional Feedback date metadata, no lifecycle subsystem.

## 10. Confirmed Gaps

1. `Feedback.outcome` is documented but not runtime-closed.
2. Customer Choice has no independent persistence model.
3. Product Usage is absent.
4. Observed Outcome / Outcome Assessment are absent.
5. Follow-up has metadata but no lifecycle subsystem.
6. No Recommendation-scoped Feedback retrieval endpoint was verified.
7. No separate durable presentation event was verified.
8. Feedback does not automatically update recommendation learning or scoring.
9. Feedback routes remain under the specialist router although Customer ownership is enforced for the explicit customer action; this is route organization, not an authorization bypass.

## 11. Smallest Next Vertical Slice

The smallest evidence-bound next boundary is:

`Customer Response → Explicit Outcome Contract → Durable Feedback → Existing Case/Recommendation Trace`

The Customer Response slice already exists. The remaining narrow contract gap is the difference between documented outcome vocabulary and runtime acceptance.

Candidate implementation boundary:
- keep `Feedback.outcome` as carrier;
- define accepted outcome vocabulary for explicit Customer Response;
- reject invalid Customer Response outcome values at that action boundary;
- preserve generic Feedback compatibility;
- preserve ownership, Recommendation linkage, audit and retrieval;
- introduce no Outcome, CustomerChoice, Usage or Follow-up entity.

This boundary requires separate implementation authorization.

## 12. Implementation Constraints

If authorized:
- branch from then-current Master;
- change only the explicit Customer Response outcome contract;
- preserve server-controlled `source=CUSTOMER`;
- preserve Case ownership and Recommendation-to-Case validation;
- preserve Feedback persistence/retrieval and audit;
- add focused valid/invalid outcome tests;
- run full regression and governance on exact PR HEAD;
- independently verify diff;
- merge with exact-head verification;
- verify resulting Master SHA and observable post-merge evidence.

Excluded: CustomerChoice, Outcome entity, Follow-up engine, Product Usage, Observed Outcome, Sale changes, Recommendation scoring/ranking/eligibility/evidence changes, ProfileFact writes, Home/UI redesign, questionnaire, AI/image architecture, schema/migration.

## 13. Final Gate Verdict

**READY FOR NEXT VERTICAL SLICE**

Reason: current Master has a durable, authenticated, Recommendation-linked Customer Response path. The next smallest repository-backed boundary is the explicit Outcome contract; richer Customer Choice, Outcome, Usage and Follow-up lifecycle domains remain outside runtime reality.

**This gate authorizes no implementation by itself. Separate PO implementation authorization is required.**

*End of HBI Consultation Outcome / Follow-up Reality Gate v0.2.*
