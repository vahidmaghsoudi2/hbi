# HBI Consultation Outcome / Follow-up Reality Gate v0.2

| Field | Value |
|---|---|
| Baseline | `265e29c430631c428cd2e0abb47bb677fb8dc84f` |
| Gate | HBI-CONSULTATION-OUTCOME-FOLLOWUP-REALITY-GATE-002 |
| Scope | Customer Response → Outcome / Follow-up |
| Implementation | **NOT AUTHORIZED BY THIS GATE** |
| Verdict | **READY FOR NEXT VERTICAL SLICE** |

## 1. Baseline
Current Master is `265e29c430631c428cd2e0abb47bb677fb8dc84f`. The Customer Response slice is already present in Master through `POST /api/v1/customers/feedback`.

## 2. Files / Code Paths
Evidence inspected:
- `app/models/feedback.py`
- `app/services/feedback_service.py`
- `app/api/routers/customers.py`
- `app/api/routers/specialist.py`
- `tests/test_consultation_response_vertical_slice_001.py`
- `tests/test_consultation_vertical_slice_001.py`
- `docs/architecture/HBI_CONSULTATION_FOLLOWUP_OUTCOME_REALITY_GATE_v0.1.md`
- `docs/architecture/HBI_CONSULTATION_MINIMAL_CONTRACT_v0.1.md`

Evidence statuses: **CONFIRMED IN CODE / CONFIRMED IN TEST / CONFIRMED IN DOC / NOT FOUND / CONFLICT / UNKNOWN**.

## 3. Customer Response Reality
**CONFIRMED IN CODE / CONFIRMED IN TEST**

The explicit customer-response path already provides authenticated Case ownership, required Recommendation linkage, same-Case validation, server-controlled `source=CUSTOMER`, durable Feedback, Case-scoped retrieval and response-specific audit evidence.

Issue #232 proposed the same slice after it had already been merged. It is therefore superseded by repository reality.

## 4. Outcome Runtime Contract

### Carrier
**CONFIRMED IN CODE**

Outcome is nullable `Feedback.outcome`. No dedicated Outcome model/service exists.

### Vocabulary
**CONFIRMED IN DOC / PARTIAL IN CODE**

Documented labels:
- `ACCEPTED`
- `REJECTED`
- `PARTIAL`
- `FOLLOW_UP_NEEDED`

Runtime normalizes supplied text to uppercase but does not enforce this four-value vocabulary. Therefore the labels are documented vocabulary, not a proven closed runtime state machine.

### Persistence / retrieval
**CONFIRMED IN CODE / CONFIRMED IN TEST**

Outcome is persisted on Feedback and returned by retrieval. Existing tests exercise values including `ACCEPTED` and `PARTIAL`.

### Semantic boundary
**CONFIRMED IN CODE / CONFIRMED IN DOC**

A Feedback outcome is not proof of independent Customer Choice, purchase, product usage, observed outcome, or outcome assessment.

## 5. Customer Choice Reality
**NOT FOUND**

No independent CustomerChoice model, service, or persistence field was verified. Specialist override actions are operator actions. Purchase remains transaction evidence and is distinct from customer response.

## 6. Follow-up Runtime Reality

### Field
**CONFIRMED IN CODE**

`Feedback.follow_up_at` is nullable datetime, accepted by generic specialist Feedback creation and returned by retrieval.

### Explicit customer-response action
**CONFLICT / GAP**

The customer-response request currently carries case, recommendation, outcome, rating and comment. It does not expose `follow_up_at`. This is compatible with the narrow response slice because follow-up metadata remains optional and outside that action.

### Lifecycle
**NOT FOUND**

No Follow-up entity, scheduler, reminder, completion, cancellation or rescheduling contract was verified.

### Cardinality
**CONFIRMED IN CODE**

Each Feedback row can carry its own `follow_up_at`; no single-active-follow-up invariant was verified.

### Audit
**CONFIRMED IN CODE**

Generic specialist Feedback audit records outcome and follow-up metadata. Customer-response audit records the response target and outcome.

## 7. Usage / Observed Outcome Reality

| Concept | Reality |
|---|---|
| Product Usage entity/service | **NOT FOUND** |
| Customer usage confirmation | **NOT FOUND** |
| Observed Outcome entity/service | **NOT FOUND** |
| Outcome Assessment entity/service | **NOT FOUND** |
| Learning / automatic recommendation update | **NOT FOUND / OUT OF SCOPE** |

## 8. Traceability
**CONFIRMED IN CODE / CONFIRMED IN TEST**

Current durable path:

`Customer → owned Case → Recommendation → Feedback(source=CUSTOMER) → outcome`

Purchase remains separate:

`Recommendation → SaleItem → Sale`

No evidence supports collapsing purchase, reported outcome and product usage into one lifecycle.

## 9. Documentation Consistency
**CONFIRMED IN DOC**

The existing v0.1 gate and Minimal Consultation Contract defer richer Outcome, Usage and Follow-up domains. Framework wording is broader than current runtime, so the distinction must remain explicit.

## 10. Confirmed Gaps
1. Outcome vocabulary is documented but not runtime-closed.
2. Customer Choice persistence is absent.
3. Product Usage is absent.
4. Observed Outcome / Outcome Assessment are absent.
5. Follow-up has metadata but no lifecycle subsystem.
6. Customer-response API does not expose optional `follow_up_at`.
7. No Recommendation-scoped Feedback retrieval endpoint.
8. No automatic learning from Feedback.

## 11. Smallest Next Vertical Slice

The smallest evidence-bound next slice is:

`Customer Response → Explicit Outcome Contract → Durable Feedback → Existing Recommendation/Case Trace`

Boundary:
- keep Feedback as the carrier;
- keep `Feedback.outcome`;
- enforce the documented four-value vocabulary **only for the explicit Customer Response action**, if implementation acceptance confirms this contract;
- preserve generic specialist Feedback compatibility;
- preserve ownership, Recommendation linkage, audit and retrieval;
- introduce no Outcome entity;
- introduce no Usage entity;
- introduce no Follow-up engine.

## 12. Implementation Constraints
- Branch from current Master.
- Change only the explicit Customer Response outcome boundary.
- No Recommendation scoring/ranking/eligibility/evidence changes.
- No ProfileFact writes.
- No Sale/Usage/CustomerChoice/Follow-up entity or engine.
- No schema migration.
- Focused tests for accepted/rejected customer-response outcomes.
- Full regression and governance checks on exact PR HEAD.
- Independent verification before merge.
- Exact post-merge Master verification.

## 13. Final Gate Verdict

**READY FOR NEXT VERTICAL SLICE**

Reason: Customer Response already exists durably. The next narrow repository-backed boundary is explicit outcome vocabulary enforcement on the Customer Response action, while broader Outcome/Usage/Follow-up systems remain deferred.

*End of HBI Consultation Outcome / Follow-up Reality Gate v0.2.*
