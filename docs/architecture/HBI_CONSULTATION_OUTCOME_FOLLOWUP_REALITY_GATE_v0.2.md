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

PR #233 is merged. Issue #232 is completed. The explicit Customer Response action is therefore current repository reality, not a proposed feature.

The previous v0.1 gate used an earlier baseline and is historical evidence only.

## 2. Files / Code Paths

Directly inspected at the current Master baseline:

- `app/models/feedback.py`
- `app/services/feedback_service.py`
- `app/api/routers/specialist.py`
- `app/api/routers/recommendations.py` and related consultation paths as required by the existing slice
- `tests/test_consultation_vertical_slice_001.py`
- `app/core/audit.py`
- `docs/architecture/HBI_CONSULTATION_FOLLOWUP_OUTCOME_REALITY_GATE_v0.1.md`

Relevant current API paths:

- `POST /api/v1/specialist/feedback`
- `POST /api/v1/specialist/feedback/customer-response`
- `GET /api/v1/specialist/feedback/case/{case_id}`

Evidence status vocabulary:

**CONFIRMED IN CODE / CONFIRMED IN TEST / CONFIRMED IN DOC / NOT FOUND / CONFLICT / UNKNOWN**

## 3. Customer Response Reality

**CONFIRMED IN CODE / CONFIRMED IN TEST**

The current Master contains the explicit Customer Response vertical slice introduced by PR #233.

Runtime contract:

`Authenticated Customer → Owned Case → Existing Recommendation → Customer Response → Feedback(source=CUSTOMER) → Case-scoped Retrieval → Audit`

The endpoint:

`POST /api/v1/specialist/feedback/customer-response`

- requires authentication;
- verifies the authenticated customer owns the Case;
- requires `recommendation_id`;
- reuses `FeedbackService.create_feedback()`;
- forces `source="CUSTOMER"` server-side;
- validates that the Recommendation exists;
- validates that the Recommendation belongs to the supplied Case;
- persists Feedback;
- records a response-specific `customer_response_created` audit event;
- records `customer_response_rejected` for rejected service validation.

The current focused tests cover authentication, foreign Case, missing Recommendation, Recommendation from another Case, durable persistence, CUSTOMER source and Case-scoped retrieval.

## 4. Outcome Runtime Contract

### Carrier

**CONFIRMED IN CODE**

There is no dedicated Outcome entity or service.

The V1 carrier is nullable:

`Feedback.outcome`

### Values

**CONFIRMED IN CODE / CONFIRMED IN DOC**

The documented vocabulary is:

- `ACCEPTED`
- `REJECTED`
- `PARTIAL`
- `FOLLOW_UP_NEEDED`

Runtime behavior is broader than that documentation:

- supplied outcome text is normalized to uppercase;
- no database enum is enforced;
- `FeedbackService` does not reject values outside the four documented labels.

Therefore the four labels are **documented vocabulary, not a closed runtime state machine**.

### Semantic boundary

**CONFIRMED IN CODE / CONFIRMED IN DOC**

A Feedback outcome is a reported customer response value. It is not, by itself, proof of:

- Customer Choice as an independent domain event;
- purchase;
- product usage;
- observed outcome;
- outcome assessment.

Purchase remains represented separately through the existing Recommendation → SaleItem trace.

## 5. Customer Choice Reality

**NOT FOUND**

No independent `CustomerChoice` model, service, persistence field, or API was verified.

The current Customer Response action is explicit and Recommendation-linked, but its durable representation remains Feedback.

Specialist Override actions are operator actions and are not Customer Choice.

## 6. Follow-up Runtime Reality

### Field

**CONFIRMED IN CODE**

`Feedback.follow_up_at` is nullable `DateTime`.

Generic Feedback creation accepts it and Case-scoped Feedback retrieval returns it.

### Explicit Customer Response

**CONFIRMED IN CODE**

The explicit Customer Response request currently carries:

- `case_id`
- `recommendation_id`
- `outcome`
- `rating`
- `comment`
- `follow_up_at`

The field is therefore available as optional metadata in the explicit response path. Its presence does not create a Follow-up lifecycle.

### Lifecycle

**NOT FOUND**

No dedicated Follow-up entity, scheduler, reminder mechanism, completion state, cancellation state, rescheduling state, or active-follow-up invariant was verified.

Current reality is therefore:

**follow-up date metadata on Feedback, not a Follow-up subsystem.**

### Audit

**CONFIRMED IN CODE**

Generic Feedback creation records Feedback audit events. The explicit Customer Response path records a response-specific audit event containing the Case and Recommendation target and the persisted response state.

## 7. Usage / Observed Outcome Reality

| Concept | Status |
|---|---|
| Product Usage entity/service | **NOT FOUND** |
| Customer usage confirmation | **NOT FOUND** |
| Observed Outcome entity/service | **NOT FOUND** |
| Outcome Assessment entity/service | **NOT FOUND** |
| Automatic recommendation learning/update | **NOT FOUND / OUT OF SCOPE** |

The existing `Feedback.outcome` must remain interpreted as reported response data, not verified product-use or observed-result data.

## 8. Traceability

**CONFIRMED IN CODE / CONFIRMED IN TEST**

Current durable consultation response path:

`Customer → owned Case → Recommendation → Feedback(source=CUSTOMER) → outcome`

The Feedback row carries both `case_id` and `recommendation_id`, and creation verifies that the Recommendation belongs to the Case.

Current purchase trace is separate:

`Recommendation → SaleItem → Sale`

This is transaction evidence. It is not independent Customer Choice evidence.

Current retrieval boundary is:

`GET /api/v1/specialist/feedback/case/{case_id}`

No dedicated Recommendation-scoped Feedback retrieval endpoint was verified.

## 9. Documentation Consistency

**CONFIRMED IN DOC / PARTIAL CONSISTENCY**

The v0.1 gate correctly deferred richer Outcome, Usage and Follow-up domains.

The current repository now contains the explicit Customer Response slice, so any older document that describes that slice as merely proposed is historical and must not be treated as current Master reality.

The safe current vocabulary is:

- Customer Response: implemented as explicit CUSTOMER-sourced Feedback;
- Outcome: nullable Feedback field, documented four-label vocabulary but open runtime values;
- Customer Choice: not an independent persisted construct;
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
7. No presentation event is durably recorded as a separate construct.
8. Feedback does not automatically update recommendation learning or scoring.
9. The Feedback routes remain under the specialist router even though Customer ownership is enforced for the explicit customer action; this is a route-organization issue, not evidence of an authorization bypass.

## 11. Smallest Next Vertical Slice

The smallest evidence-bound next boundary is:

`Customer Response → Explicit Outcome Contract → Durable Feedback → Existing Case/Recommendation Trace`

The repository already has the Customer Response action. The remaining narrow contract gap is the difference between **documented outcome vocabulary** and **runtime acceptance**.

The candidate implementation boundary is therefore:

- keep `Feedback.outcome` as the carrier;
- define the accepted outcome vocabulary for the explicit Customer Response action;
- reject invalid Customer Response outcome values at that action boundary;
- preserve generic Feedback compatibility unless a separate contract authorizes changing it;
- preserve Case ownership, Recommendation linkage, audit and retrieval;
- introduce no Outcome entity;
- introduce no CustomerChoice entity;
- introduce no Usage entity;
- introduce no Follow-up engine.

This is the smallest boundary identified by the current evidence. It requires separate implementation authorization.

## 12. Implementation Constraints

If separately authorized:

- branch from the then-current Master;
- change only the explicit Customer Response outcome contract;
- preserve server-controlled `source=CUSTOMER`;
- preserve Case ownership and Recommendation-to-Case validation;
- preserve Feedback persistence and retrieval;
- preserve audit behavior;
- add focused valid/invalid outcome tests;
- run full regression and governance checks on the exact PR HEAD;
- independently verify the diff;
- merge only with exact-head verification;
- verify the resulting Master SHA and observable post-merge evidence.

Explicitly excluded:

- CustomerChoice entity;
- Outcome entity;
- Follow-up entity/engine;
- Product Usage;
- Observed Outcome;
- Sale changes;
- Recommendation scoring/ranking/eligibility/evidence changes;
- ProfileFact writes;
- Home/UI redesign;
- questionnaire;
- AI/image architecture;
- schema/migration.

## 13. Final Gate Verdict

**READY FOR NEXT VERTICAL SLICE**

Reason: the current Master has a durable, authenticated, Recommendation-linked Customer Response path. The next smallest repository-backed boundary is the explicit Outcome contract, while richer Customer Choice, Outcome, Usage and Follow-up lifecycle domains remain outside current runtime reality.

**This gate authorizes no implementation by itself. Separate PO implementation authorization is required.**

*End of HBI Consultation Outcome / Follow-up Reality Gate v0.2.*
