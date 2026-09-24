# HBI Consultation Follow-up / Outcome Reality Gate v0.1

| Field | Value |
|---|---|
| Baseline | `aaf0acfb22025255ee124e250719ec5b5eec33fc` |
| Gate | HBI-CONSULTATION-FOLLOWUP-OUTCOME-REALITY-GATE-001 |
| Scope | Recommendation → Customer Response → Outcome → Follow-up |
| Implementation | **NOT AUTHORIZED BY THIS GATE** |
| Verdict | **READY FOR NEXT VERTICAL SLICE** |

## 1. Baseline

All findings in this document are anchored to Master commit `aaf0acfb22025255ee124e250719ec5b5eec33fc`. This gate is a repository reality audit, not an implementation claim.

## 2. Files / Code Paths

Primary evidence inspected:

- `app/models/feedback.py`
- `app/services/feedback_service.py`
- `app/api/routers/specialist.py`
- `app/models/recommendation.py`
- `app/models/case.py`
- `app/models/sale.py`
- `app/models/sale_item.py`
- `app/services/sale_service.py`
- `app/services/mutation_log_service.py`
- `tests/test_consultation_vertical_slice_001.py`
- consultation architecture documents under `docs/architecture/`

Evidence status vocabulary used throughout:
**CONFIRMED IN CODE / CONFIRMED IN TEST / CONFIRMED IN DOC / NOT FOUND / CONFLICT / UNKNOWN**.

## 3. Current Feedback Contract

### 3.1 Entity

**CONFIRMED IN CODE**

`Feedback` is a persisted entity with:

- `feedback_id`
- required `case_id` FK to Case
- optional `recommendation_id` FK to Recommendation
- required `source`
- optional `outcome`
- optional `rating`
- optional `comment`
- optional `follow_up_at`
- `created_at`

`recommendation_id` uses `SET NULL` if the recommendation is deleted.

### 3.2 Service

**CONFIRMED IN CODE**

`FeedbackService.create_feedback()` validates:

1. source is one of `CUSTOMER`, `SPECIALIST`, `SYSTEM`;
2. Case exists;
3. supplied Recommendation exists;
4. supplied Recommendation belongs to the supplied Case.

It then creates one durable Feedback row.

### 3.3 API

**CONFIRMED IN CODE**

Existing endpoints:

- `POST /api/v1/specialist/feedback`
- `GET /api/v1/specialist/feedback/case/{case_id}`

The router checks authenticated ownership of the Case before creation or retrieval.

### 3.4 Meaning of source=CUSTOMER

**CONFIRMED IN CODE; SEMANTIC BOUNDARY PARTIAL**

`source=CUSTOMER` identifies the source category as the customer. It does **not**, by itself, prove:

- selection;
- purchase;
- product usage;
- observed outcome;
- outcome assessment.

The optional Recommendation link is what makes a Feedback row explicitly about a Recommendation.

## 4. Current Outcome Contract

### 4.1 Carrier

**CONFIRMED IN CODE**

There is no dedicated Outcome entity/service. V1 outcome information is carried by nullable `Feedback.outcome`.

### 4.2 Values

**CONFIRMED IN CODE / CONFIRMED IN DOC**

Current documented labels are:

- `ACCEPTED`
- `REJECTED`
- `PARTIAL`
- `FOLLOW_UP_NEEDED`

These are stored as strings, not enforced by a database enum or a closed service-level enum. The service normalizes supplied outcome text to uppercase but does not enforce this four-value set.

Therefore the four labels are the current documented vocabulary, not a proven exhaustive runtime state machine.

### 4.3 Semantic separation

**CONFIRMED IN CODE**

`ACCEPTED` / `REJECTED` can occur as Feedback outcomes, while Specialist Override also has decision actions with related names. Those concepts are source-specific and must not be collapsed into one universal lifecycle.

The following are not proven as dedicated outcome states:

- Presented — **NOT FOUND** as a durable presentation event/entity.
- Selected — **NOT FOUND** as an independent customer-choice entity.
- Used — **NOT FOUND** as a product-usage entity.
- Observed Outcome — **NOT FOUND** as a dedicated construct.
- Outcome Assessment — **NOT FOUND** as a dedicated construct.

## 5. Customer Response / Choice Reality

### Customer Response

**PARTIAL / CONFIRMED IN CODE**

A customer response can be durably represented through Feedback with `source=CUSTOMER`, especially when `recommendation_id` is supplied.

### Customer Choice

**NOT FOUND**

No independent CustomerChoice model, service, or persistence field was verified.

`SpecialistOverride.action=MODIFY_SELECTION` is a specialist/operator action and is not customer choice.

### V1 interpretation

**PROPOSED CONTRACT — NOT CURRENT FACT**

For the next narrow slice, Customer Response may be represented by a CUSTOMER-sourced Feedback linked to a Recommendation. Customer Choice remains a semantic interpretation only when the UI/action explicitly records a response to that Recommendation. No new entity is required.

## 6. Recommendation → Feedback Trace

**CONFIRMED IN CODE**

Durable relation:

`Case → Recommendation ← Feedback`

with Feedback also carrying required `case_id`.

Creation verifies:

`Feedback.case_id == Recommendation.case_id`

when a Recommendation is supplied.

The API first verifies:

`authenticated customer == Case.customer_id`

before allowing create or retrieval.

Retrieval is Case-scoped:

`GET /api/v1/specialist/feedback/case/{case_id}`

**CONFIRMED IN TEST**

The existing consultation vertical-slice test proves a generated Recommendation can be linked to CUSTOMER Feedback using the Recommendation ID and Case ID.

**Gap:** no dedicated “feedback by recommendation” endpoint was verified. Case retrieval is the current durable retrieval boundary.

## 7. Follow-up Reality

### Field

**CONFIRMED IN CODE**

`Feedback.follow_up_at` is a nullable datetime.

The field is accepted by Feedback creation and returned by Feedback retrieval.

### Cardinality

**CONFIRMED IN CODE**

Because each Feedback row can carry its own `follow_up_at`, multiple Feedback rows can technically contain different follow-up dates.

There is no verified single-active-follow-up invariant.

### Lifecycle

**NOT FOUND**

No dedicated Follow-up entity, service, scheduler, completion state, cancellation state, or rescheduling contract was verified.

Therefore the current capability is a **follow-up date attribute on Feedback**, not a Follow-up subsystem.

### Audit

**CONFIRMED IN CODE**

Feedback creation emits `feedback_created` through `audit_event`; rejected creation emits `feedback_rejected`. The creation audit identifies the Case and Recommendation target and records source/outcome/follow-up state.

## 8. Recommendation → Sale / Purchase Trace

**CONFIRMED IN CODE**

`SaleItem.recommendation_id` provides an optional durable Recommendation-to-sale-item relation.

Sale creation validates, when a Recommendation is supplied:

- Recommendation exists;
- its Case belongs to the sale customer;
- its product matches the sale product;
- Recommendation eligibility is `ELIGIBLE`.

This establishes a **Recommendation → Purchase Transaction Trace**.

It does not establish Customer Choice. Purchase is a transaction fact and must remain distinct from customer response.

## 9. Usage / Observed Outcome Reality

| Concept | Reality |
|---|---|
| Product Usage entity/service | **NOT FOUND** |
| Customer usage confirmation | **NOT FOUND** |
| Observed Outcome entity/service | **NOT FOUND** |
| Outcome Assessment entity/service | **NOT FOUND** |
| Learning/automatic recommendation update | **NOT FOUND / OUT OF SCOPE** |

Current Feedback can carry a reported outcome label, but that must not be presented as verified product usage or observed clinical/cosmetic outcome.

## 10. Documentation Consistency

**CONFIRMED IN DOC**

Existing consultation documents consistently treat Feedback as the current simple follow-up/outcome capability and defer richer Outcome/Product Usage domains.

**CONFLICT / GAP**

Some historical wording uses “Customer Choice” or “Follow-up” at framework level more broadly than the concrete runtime constructs support. The safe repository statement is:

- Feedback exists;
- Customer Choice is not an independent persisted construct;
- Follow-up is currently a nullable Feedback attribute;
- richer Outcome/Usage/Follow-up lifecycle is not implemented.

The documentation must preserve this distinction.

## 11. Confirmed Gaps

1. No dedicated Customer Choice persistence.
2. No dedicated Outcome domain.
3. No Product Usage construct.
4. No Observed Outcome / Outcome Assessment construct.
5. No Follow-up entity or lifecycle engine.
6. Feedback outcome vocabulary is documented but not runtime-closed.
7. No dedicated Recommendation-scoped Feedback retrieval endpoint.
8. Presentation tracking is not durable.
9. Purchase trace exists, but is not customer-choice evidence.
10. The current API is named under the specialist router even though authenticated customer ownership is enforced for the Case; semantic naming is therefore broader than the current route organization.

These gaps do not block a minimal next slice because the required durable Customer Response path already exists.

## 12. V1 Contract Proposal

**PROPOSED — requires separate implementation authorization**

Keep the current model and make the smallest semantic contract explicit:

1. Recommendation remains the existing Case decision artifact.
2. Customer Response is recorded as Feedback with `source=CUSTOMER`.
3. When response concerns a Recommendation, `recommendation_id` is required by the V1 response action.
4. `case_id` remains required and must match the Recommendation's Case.
5. Existing ownership checks remain authoritative.
6. `Feedback.outcome` remains the V1 outcome carrier.
7. Purchase remains Sale/SaleItem transaction evidence.
8. Usage remains outside V1.
9. `follow_up_at` remains optional metadata; no Follow-up engine is introduced.
10. No Recommendation scoring/ranking/eligibility/evidence logic changes.
11. No ProfileFact write is implied by a Customer Response.
12. No new entity or migration is required for the next slice.

## 13. Smallest Next Vertical Slice

The smallest evidence-bound implementation boundary is:

```
Authenticated Customer
        ↓
Owned Case
        ↓
Existing Recommendation
        ↓
Customer Response
        ↓
Feedback(source=CUSTOMER,
         recommendation_id,
         case_id,
         outcome)
        ↓
Durable Feedback
        ↓
Owned Case retrieval
        ↓
Audit evidence
```

Acceptance should prove:

1. authenticated customer can respond only on an owned Case;
2. Recommendation belongs to that Case;
3. source is fixed to CUSTOMER for the customer-response action;
4. recommendation_id is carried for recommendation-specific response;
5. foreign Recommendation/Case linkage is rejected;
6. Feedback is durable and retrievable;
7. audit evidence identifies Case + Recommendation + Feedback;
8. existing `outcome` carrier remains unchanged;
9. optional `follow_up_at` remains non-blocking;
10. Sale, Usage, CustomerChoice entity, Follow-up engine, and Outcome entity remain untouched.

## 14. Implementation Constraints

Any implementation following this gate must:

- branch from the current Master;
- reuse Feedback/FeedbackService;
- keep Case ownership enforcement;
- preserve Recommendation ownership relation;
- preserve existing Feedback persistence;
- preserve audit_event behavior;
- add only the minimum tests/API glue required to make Customer Response explicit;
- run targeted tests and full regression;
- pass `test` and `governance-tests` on the exact PR HEAD;
- receive independent verification before merge;
- update the branch with current Master if Master moves under strict required checks;
- verify the exact post-merge Master SHA and resulting tree.

Explicitly excluded:

- CustomerChoice entity;
- Outcome entity;
- Follow-up entity/engine;
- Sale changes;
- Usage;
- Presentation tracking;
- recommendation scoring/ranking/eligibility/evidence changes;
- ProfileFact integration;
- Home/UI redesign;
- questionnaire;
- AI/image architecture;
- schema/migration.

## 15. Final Gate Verdict

**READY FOR NEXT VERTICAL SLICE**

Reason: the repository already has a durable Case-linked Feedback capability, authenticated Case ownership, Recommendation-to-Case validation, Recommendation-to-Purchase transaction tracing, Feedback retrieval, and creation audit evidence. The next implementation can therefore remain narrow and reuse existing infrastructure without inventing a new Outcome, CustomerChoice, Usage, or Follow-up subsystem.

**This verdict authorizes no implementation by itself. A separate PO implementation authorization is required.**

*End of Reality Gate v0.1.*
