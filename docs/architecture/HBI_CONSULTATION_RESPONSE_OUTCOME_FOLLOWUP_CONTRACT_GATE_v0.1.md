# HBI-CONSULTATION-RESPONSE-OUTCOME-FOLLOWUP-CONTRACT-GATE-001

## 1. Baseline

| Field | Value |
|---|---|
| Repository | `vahidmaghsoudi2/hbi` |
| Baseline Master | `a8f7c941496eb4ee5d1f5e64be2233763f1f2377` |
| Mission | Recommendation → Customer Response → Outcome → Follow-up Contract / Decision Gate |
| Implementation | **NOT AUTHORIZED / NOT PERFORMED** |
| Schema / Migration / API / UI | **NOT CHANGED** |

All repository facts below are anchored to the stated baseline. Earlier repository states are not used as current evidence.

## 2. Files / Code Paths Inspected

### Direct code inspection — CONFIRMED IN CODE

- `app/models/feedback.py`
- `app/services/feedback_service.py`
- `app/api/routers/specialist.py`
- `app/models/recommendation.py`
- `app/models/case.py`
- `app/models/specialist_override.py`
- `app/services/specialist_override_service.py`
- `app/models/sale.py`
- `app/models/sale_item.py`
- `app/services/sale_service.py`
- `app/interface/facades.py`
- `app/services/mutation_log_service.py`

### Direct documentation inspection — CONFIRMED IN DOC

- `docs/architecture/HBI_CONSULTATION_MINIMAL_CONTRACT_v0.1.md`
- `docs/architecture/HBI_CONSULTATION_PHASE1_DECISIONS_v0.1.md`
- `docs/architecture/HBI_CONSULTATION_VERTICAL_SLICE_001_EVIDENCE.md`
- `docs/architecture/HBI_CONSULTATION_NEXT_QUESTION_VERTICAL_SLICE_001_EVIDENCE.md`

### Test evidence

The inspected consultation evidence documents explicitly record Feedback as an existing optional follow-up capability. A dedicated repository-wide Feedback/Outcome test file was **NOT FOUND** at the inspected candidate paths. Therefore no stronger test claim is made here.

---

# 3. Current Feedback Contract

## 3.1 Model

`Feedback` is a real persisted entity.

Fields:

- `feedback_id`
- `case_id` — required FK to Case
- `recommendation_id` — optional FK to Recommendation, `SET NULL` on recommendation deletion
- `source` — required string
- `outcome` — nullable string
- `rating` — nullable string
- `comment` — nullable text
- `follow_up_at` — nullable datetime
- `created_at`

Relationships exist to Case and Recommendation.

**Status: CONFIRMED IN CODE.**

## 3.2 FeedbackService

`FeedbackService.create_feedback()` accepts:

`case_id, source, outcome, rating, comment, recommendation_id, follow_up_at`.

It validates:

1. `source ∈ {CUSTOMER, SPECIALIST, SYSTEM}`
2. Case exists.
3. If `recommendation_id` is supplied, Recommendation exists.
4. Supplied Recommendation belongs to the supplied Case.

It then persists one Feedback row.

**Status: CONFIRMED IN CODE.**

Important boundary: the service does **not** define an enum/validation contract for `outcome`. It stores the normalized uppercase string.

Therefore the following values are not merely assumed; they are the values explicitly documented in the model/comment and used by the current contract lineage:

- `ACCEPTED`
- `REJECTED`
- `PARTIAL`
- `FOLLOW_UP_NEEDED`

However, because the service does not enforce them, the set is **not a hard runtime enum**.

**Status: CONFIRMED IN CODE + CONFIRMED IN DOC; runtime enforcement = NOT FOUND.**

## 3.3 Customer source

`source=CUSTOMER` means the persisted Feedback record identifies the source actor/category as the customer.

What it does **not** currently prove by itself:

- that the customer selected a particular recommendation;
- that the customer purchased it;
- that the customer used it;
- that an outcome was observed;
- that the feedback is a formal Customer Choice event.

The API permits `recommendation_id` to be omitted even when `source=CUSTOMER`.

**Status: CONFIRMED IN CODE.**

---

# 4. Current Outcome Contract

## 4.1 There is no separate Outcome entity

No `Outcome` model/service/router was found among the inspected application paths.

The current outcome representation is the nullable `Feedback.outcome` string.

**Status: NOT FOUND for a dedicated Outcome domain.**

## 4.2 Actual values

| Value | Current location | What can be proved |
|---|---|---|
| `ACCEPTED` | Feedback model comment / consultation contract lineage | A Feedback outcome value; no runtime enum enforcement |
| `REJECTED` | Feedback model comment / consultation contract lineage | A Feedback outcome value; no runtime enum enforcement |
| `PARTIAL` | Feedback model comment / consultation contract lineage | A Feedback outcome value; no runtime enum enforcement |
| `FOLLOW_UP_NEEDED` | Feedback model comment / consultation contract lineage | A Feedback outcome value; no runtime enum enforcement |

These are **Feedback outcome labels**, not proven lifecycle states for Recommendation, Product, Sale, or product usage.

## 4.3 Do not collapse adjacent concepts

### `Presented`

A Recommendation can be generated and returned by the Recommendation API, but no durable presentation event/entity was found.

**Status: NOT FOUND as an event contract.**

### `Selected`

No independent persisted Customer Selection/Choice entity or field was found.

Specialist override has `action=MODIFY_SELECTION`, but that is a **specialist decision**, not customer selection.

**Status: NOT FOUND as Customer Choice.**

### `Accepted`

Exists as:

- Feedback outcome label.
- Specialist Override action.

These have different source semantics. Specialist `ACCEPT` is not Customer acceptance.

**Status: CONFIRMED IN CODE, semantics are source-dependent.**

### `Rejected`

Same distinction:

- Feedback `REJECTED` can be a customer/specialist/system-sourced outcome label.
- Specialist Override `REJECT` is explicitly a specialist decision.

**Status: CONFIRMED IN CODE; not a single universal event.**

### `Purchased`

Purchase is represented by Sale/SaleItem. SaleItem has optional `recommendation_id`.

**Status: CONFIRMED IN CODE as a transaction trace, not as Customer Response.**

### `Used`

No inspected Usage/ProductUsage entity, service, router, or field was found.

**Status: NOT FOUND.**

### `Outcome`

Current V1 uses `Feedback.outcome`; no separate Outcome domain was found.

**Status: CONFIRMED IN CODE as a field; dedicated domain = NOT FOUND.**

---

# 5. Customer Response / Choice Reality

## 5.1 Customer Response

The closest existing persisted construct is:

`Feedback(source=CUSTOMER)`

optionally linked to a specific Recommendation through `recommendation_id`.

This is sufficient to represent a **customer-sourced response record**, but the current implementation does not make it a formal Recommendation Choice contract.

**Status: CONFIRMED IN CODE as capability; NOT CONFIRMED as formal Customer Choice contract.**

## 5.2 Customer Choice

No independent Customer Choice entity, model, service, or router was found in the inspected paths.

The repository therefore currently distinguishes:

- Recommendation = system-produced suggestion artifact.
- Specialist Override = specialist decision artifact.
- Feedback = source-tagged response/outcome record.
- SaleItem = business transaction line.

It does not currently expose a dedicated durable customer selection event.

**Status: NOT FOUND.**

## 5.3 V1 implication

A new Customer Choice entity is **not justified by current evidence**.

The smallest V1 contract can use the existing Feedback row for a customer response, provided the response is explicitly linked to the Recommendation when it is intended to answer “what did the customer say about this recommendation?”.

That is a **contract proposal**, not a current runtime rule.

---

# 6. Recommendation → Feedback Trace

The durable relational path is:

```
Case
  └── Recommendation
          ↑
      Feedback.recommendation_id
          │
      Feedback.case_id
```

## 6.1 Recommendation identity

`Feedback.recommendation_id` is a nullable FK to Recommendation.

**Status: CONFIRMED IN CODE.**

## 6.2 Case identity

`Feedback.case_id` is required and FK-linked to Case.

**Status: CONFIRMED IN CODE.**

## 6.3 Cross-case validation

`FeedbackService.create_feedback()` verifies that a supplied Recommendation belongs to the supplied Case.

**Status: CONFIRMED IN CODE.**

## 6.4 Ownership

The feedback router first verifies:

`Case.customer_id == authenticated customer_id`.

The same ownership boundary is used for feedback retrieval.

**Status: CONFIRMED IN CODE.**

## 6.5 Retrieval

Existing endpoint:

`GET /api/v1/specialist/feedback/case/{case_id}`

returns Feedback rows for an owned Case.

There is no inspected dedicated “feedback by recommendation” endpoint.

**Status: CONFIRMED IN CODE.**

## 6.6 Audit

Feedback creation calls `audit_event("feedback_created", ...)` and rejected creation calls `audit_event("feedback_rejected", ...)`.

The audit payload records operator/customer identity, case/recommendation target, source/outcome/follow-up state, reason/comment where available, timestamp, and feedback ID as the detail.

**Status: CONFIRMED IN CODE.**

This is an application audit event, not the ProductMutationLogService.

## 6.7 V1 trace assessment

For a feedback row that carries `recommendation_id`, the durable Recommendation → Feedback trace is sufficient for a narrow V1 customer-response slice.

The remaining gap is semantic: the repository does not currently enforce that a CUSTOMER feedback record linked to a recommendation is specifically a “Customer Choice/Response” event.

**Status: READY at persistence/trace level; semantic contract needs explicit V1 definition.**

---

# 7. Follow-up Reality

## 7.1 Current implementation

`follow_up_at` is a nullable datetime column on Feedback.

It is accepted by `FeedbackService.create_feedback()` and returned by the feedback API.

**Status: CONFIRMED IN CODE.**

## 7.2 Is Follow-up an entity?

No dedicated Follow-up model/service/router/engine was found in the inspected application paths.

**Status: NOT FOUND.**

## 7.3 Is Follow-up a separate attribute?

Yes. It is currently one optional attribute on each Feedback row.

**Status: CONFIRMED IN CODE.**

## 7.4 One or multiple follow-ups?

The schema contains no uniqueness constraint on Case + Recommendation + follow-up date and Feedback creation can create multiple rows.

Therefore multiple Feedback rows can technically carry different `follow_up_at` values.

What is **not** proven is a formal scheduling contract such as:

- one active follow-up per case;
- multiple scheduled follow-ups;
- completion/cancellation/rescheduling;
- reminder execution;
- follow-up status.

So:

- Multiple persisted dates are **technically possible** through multiple Feedback rows.
- Multiple scheduled Follow-up events are **NOT a confirmed domain contract**.

## 7.5 V1 conclusion

A separate Follow-up entity/engine is not justified by current evidence.

For V1, `Feedback.follow_up_at` can remain an optional follow-up date attached to a Feedback record.

---

# 8. Recommendation → Sale Trace

The durable path is:

```
Recommendation
      ↑
SaleItem.recommendation_id
      │
SaleItem → Sale
      │
Sale.customer_id
```

## 8.1 Recommendation linkage

`SaleItem.recommendation_id` is an optional FK to Recommendation.

**Status: CONFIRMED IN CODE.**

## 8.2 Validation

During sale creation, when a recommendation ID is supplied:

- Recommendation must exist.
- Its Case must belong to the sale customer.
- Recommendation.product_id must match SaleItem.product_id.
- Recommendation.eligibility_status must be `ELIGIBLE`.

**Status: CONFIRMED IN CODE.**

## 8.3 Meaning

This proves:

**Recommendation → Purchase Transaction Trace**

It does not prove:

**Recommendation → Customer Decision**

A Sale is a business transaction. A Customer Decision is a consultation response.

They must remain separate.

## 8.4 Purchased vs Outcome

`Purchased` is therefore best treated as a transaction event in the current architecture.

It can be linked back to a Recommendation through SaleItem, but it should not silently be redefined as `Feedback.outcome`.

**Status: CONFIRMED IN CODE + CONTRACT PROPOSAL.**

---

# 9. Documentation Consistency

## 9.1 Consistent claims

The inspected consultation documents consistently support:

- Feedback exists.
- Feedback is optional in the existing consultation slice.
- Feedback can be linked to Case and optionally Recommendation.
- `follow_up_at` exists as an optional field.
- A rich Outcome/Product Usage domain is deferred.
- Recommendation scoring/ranking is outside this gate.

**Status: CONFIRMED IN DOC and aligned with code.**

## 9.2 Code capability not yet formalized as a narrow response contract

The code provides:

- CUSTOMER/SPECIALIST/SYSTEM source;
- optional Recommendation linkage;
- outcome/rating/comment;
- follow-up date;
- ownership;
- audit.

The consultation contract lineage does not yet define a precise semantic distinction between:

`Customer Response` → `Customer Choice` → `Purchased` → `Used` → `Observed Outcome`.

**Status: GAP / CONTRACT NOT YET EXPLICIT.**

## 9.3 Important consistency boundary

The existing documentation correctly avoids claiming a full Outcome/Product Usage domain. That remains consistent with the code.

No documentation should describe `Feedback.outcome` as a full clinical/product outcome assessment.

---

# 10. Confirmed Gaps

| Gap | Status | Evidence |
|---|---|---|
| Dedicated Customer Choice entity | **NOT FOUND** | inspected models/services/routers |
| Durable presentation event | **NOT FOUND** | no Presentation model/event found |
| Durable customer selection event | **NOT FOUND** | no Customer Choice model/event found |
| Separate Outcome domain | **NOT FOUND** | no Outcome model/service/router found |
| Product Usage / Used event | **NOT FOUND** | no inspected usage construct |
| Feedback outcome enum enforcement | **NOT FOUND** | service accepts arbitrary normalized string |
| Recommendation-specific Feedback retrieval endpoint | **NOT FOUND** | current retrieval is case-based |
| Formal Follow-up scheduler/engine | **NOT FOUND** | only Feedback.follow_up_at |
| Formal follow-up lifecycle | **NOT FOUND** | no status/completion/reschedule contract |
| Explicit semantic contract separating Customer Response / Choice / Purchase / Usage | **CONFIRMED GAP** | code has separate primitives but no complete V1 vocabulary contract |

No gap above justifies a new entity by itself.

---

# 11. V1 Contract Proposal

This section is **PROPOSAL**, not repository fact.

## 11.1 Recommendation

The existing Recommendation row remains the decision artifact.

No scoring/ranking/eligibility change.

## 11.2 Customer Response

For V1, use the existing Feedback entity:

```
source = CUSTOMER
case_id = target Case
recommendation_id = target Recommendation
```

when the response is specifically about a recommendation.

A Customer Response may carry:

- `outcome`
- `rating`
- `comment`
- optional `follow_up_at`

## 11.3 Customer Choice

Do **not** create a new entity for V1.

Define Customer Choice as a semantic interpretation of a CUSTOMER-sourced Feedback record linked to a Recommendation, only where the V1 action explicitly records a response to that Recommendation.

This proposal must remain distinct from Purchase.

## 11.4 Outcome

Keep `Feedback.outcome` as the V1 outcome field.

The currently documented labels remain:

- `ACCEPTED`
- `REJECTED`
- `PARTIAL`
- `FOLLOW_UP_NEEDED`

Their semantic meaning should be explicitly documented as **customer/specialist/system response outcome according to source**, rather than universal lifecycle states.

Do not add a separate Outcome entity in V1.

## 11.5 Purchase

Treat Purchase as a business transaction:

```
Sale → SaleItem → optional recommendation_id
```

Do not equate Purchase with Customer Choice or Feedback Outcome.

## 11.6 Usage

Keep Product Usage outside V1 until real repository evidence or a later mission establishes a need.

## 11.7 Follow-up

Use the existing optional `Feedback.follow_up_at`.

Do not introduce a Follow-up entity, scheduler, status machine, or reminder engine in V1.

---

# 12. Smallest Next Vertical Slice

## READY FOR NEXT VERTICAL SLICE

The smallest evidence-bound slice is:

```
Owned Case
  ↓
Existing Recommendation
  ↓
Customer Response
  ↓
Feedback(source=CUSTOMER, recommendation_id, outcome)
  ↓
Durable Feedback row
  ↓
Case retrieval + audit evidence
```

### Slice acceptance

1. Authenticated customer owns the Case.
2. Recommendation belongs to that Case.
3. Customer response is recorded with `source=CUSTOMER`.
4. The Feedback row carries the Recommendation ID.
5. Cross-case Recommendation linkage is rejected.
6. Feedback is durably retrievable through the owned Case.
7. Audit event identifies the Feedback creation and its Case/Recommendation target.
8. No Sale is required for the slice.
9. No Product Usage is required.
10. `follow_up_at` may remain optional; it is not a required success condition.
11. Recommendation scoring/ranking/eligibility remains unchanged.
12. No new entity/schema is required.

### Explicitly outside the slice

- Presentation tracking
- Separate Customer Choice entity
- Purchase creation
- Product Usage
- Outcome Assessment
- Follow-up scheduler
- Home/UI redesign
- Recommendation algorithm changes

### Why this is the smallest unit

The repository already has the durable primitives and validation boundaries. The remaining work is to make the **Customer Response contract explicit and testable**, not to create a new domain stack.

---

# 13. Implementation Constraints

If the next slice is separately authorized:

- Reuse `Feedback`, `FeedbackService`, existing specialist feedback endpoints, Case ownership, Recommendation FK validation, and `audit_event`.
- Keep `source=CUSTOMER` distinct from specialist override actions.
- Keep Purchase as Sale/SaleItem transaction data.
- Keep Product Usage outside the slice.
- Do not create Outcome/Choice/Follow-up tables.
- Do not change Recommendation scoring/ranking/eligibility.
- Do not automatically write ProfileFact.
- Do not redesign Home.
- Add only the minimum test coverage needed to prove the Customer Response contract.

---

# 14. Final Gate Verdict

## READY FOR NEXT VERTICAL SLICE

**Reason:** The repository already contains a durable Case → Recommendation → Feedback path with Case ownership, Recommendation-to-Case validation, retrieval, and creation audit. The remaining uncertainty is semantic contract definition, not missing persistence infrastructure.

The next slice should therefore make one narrow Customer Response contract explicit and observable using existing Feedback infrastructure.

**Implementation authorization is NOT granted by this Gate.**

---

## Evidence Status Summary

| Area | Status |
|---|---|
| Feedback persistence | **CONFIRMED IN CODE** |
| CUSTOMER source | **CONFIRMED IN CODE** |
| Feedback → Recommendation FK | **CONFIRMED IN CODE** |
| Case ownership | **CONFIRMED IN CODE** |
| Recommendation/Case validation | **CONFIRMED IN CODE** |
| Feedback retrieval | **CONFIRMED IN CODE** |
| Feedback audit | **CONFIRMED IN CODE** |
| Outcome field | **CONFIRMED IN CODE** |
| Dedicated Outcome entity | **NOT FOUND** |
| Customer Choice entity | **NOT FOUND** |
| Presented event | **NOT FOUND** |
| Selected event | **NOT FOUND** |
| Purchased trace | **CONFIRMED IN CODE** |
| Used event | **NOT FOUND** |
| Follow-up date | **CONFIRMED IN CODE** |
| Follow-up entity/engine | **NOT FOUND** |
| Full Customer Response semantic contract | **PROPOSED / NOT YET LOCKED** |

*End of Evidence Artifact v0.1*
