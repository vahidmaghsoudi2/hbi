# Customer Profile — Slice 1 Execution Reality Audit
Date: 2026-09-23
Status: PASS WITH REQUIRED PRE-IMPLEMENTATION CONTRACT ALIGNMENT

## 1. Audit objective

Verify the repository reality for the first executable slice after Contract v1.1 approval.

Slice 1 is intentionally limited to the contract/data-dictionary boundary:
- canonical vocabulary alignment
- value-state vocabulary alignment
- lifecycle status and freshness semantics
- controlled provenance
- promotion rules
- explicit distinction between Current Need, Profile Fact, Preference, Constraint/Safety Signal, Product Interaction, Outcome, and Derived Insight

This audit does not authorize any implementation. It first establishes whether a minimal additive slice is actually required after consumer and architecture analysis. It does not authorize recommendation, scoring, evidence-gate, seed, or product-rule changes.

## 2. Sources audited in master

- `docs/11_customer_profile/CustomerProfile-Contract-v1.1-2026-09.md`
- `docs/11_customer_profile/Data-Dictionary-v1.md`
- `docs/11_customer_profile/CustomerProfile-v1-Implementation-Contract.md`
- `app/models/customer.py`
- `app/models/case.py`
- `app/api/routers/customers.py`
- `app/services/customer_service.py`
- `app/repositories/customer_repository.py`
- `tests/test_customer_profile_unit.py`
- `tests/test_profile_consultation_recommendation_integration.py`

## 3. Current repository reality

### 3.1 Customer is still a compact legacy record

`Customer` currently stores:
- identity/contact
- one binary consent flag and date
- age/sex
- skin/hair/scalp strings
- concerns
- observations
- answers
- case history
- operator notes
- timestamps

There is no independent structured model for:
- Profile Fact
- Preference
- Constraint/Safety Signal
- Product Interaction
- Outcome
- Visit/Consultation Answer
- customer data audit/timeline

### 3.2 Case already supplies a usable visit-scoped anchor

`Case` contains `customer_id` and case context such as `case_type`, `identified_needs`, `evidence_gaps`, and reasoning metadata.

The current intake flow creates an OPEN Case and passes today's concerns separately into the recommendation profile. This is consistent with the approved rule that Current Need is visit/case scoped and must not automatically become a permanent customer fact.

### 3.3 Recommendation adapter is currently read-only from this profile perspective

`CustomerService.build_recommendation_profile()` reads existing customer fields and optional current concerns. The audited implementation does not require changing recommendation logic for Slice 1.

## 4. Confirmed contract mismatches

### A. Value-state vocabulary mismatch

Existing Data Dictionary uses:
- `ANSWERED`
- `UNKNOWN`
- `PREFER_NOT_TO_SAY`
- `NOT_APPLICABLE`

Approved Contract v1.1 defines:
- `KNOWN`
- `UNKNOWN`
- `PREFER_NOT_TO_SAY`
- `NOT_APPLICABLE`

Required action: `ANSWERED` must not remain a canonical value-state.

### B. Profile Fact lifecycle mismatch

Existing Data Dictionary proposes:
- `CANDIDATE`
- `CONFIRMED`
- `STALE`
- `SUPERSEDED`
- `REVOKED`

Approved Contract v1.1 defines lifecycle/status vocabulary:
- `ACTIVE`
- `STALE`
- `SUPERSEDED`
- `REVOKED`
- `CONFLICTED`
- `UNKNOWN`

Required action: Slice 1 must use the approved status vocabulary. Candidate/confirmed may be represented as value/provenance semantics or confirmation metadata, but must not silently become a second lifecycle vocabulary.

### C. Provenance mismatch

Approved Contract v1.1 uses controlled provenance:
- `CUSTOMER`
- `SELLER`
- `SYSTEM`
- `IMPORTED`
- `OTHER`

The repository's older dictionary uses:
- `CUSTOMER_SELF_REPORTED`
- `OPERATOR_RECORDED`

Required action: normalize to the approved vocabulary. `OTHER` remains reserved for a temporary explicitly documented source and requires review/normalization before it is treated as a durable provenance category.

### D. Freshness mismatch

The older dictionary proposes fixed TTL examples such as 6 months for skin type and 12 months for texture/scent.

Approved Contract v1.1 requires attribute-specific freshness and explicitly rejects a single universal TTL model. Historical interactions/outcomes do not expire.

Required action: Slice 1 must encode freshness as policy/semantics, not hard-code those old TTL values into the data model.

### E. Consent mismatch

The existing Customer model has a binary `consent_to_store_data` flag. Approved Contract v1.1 defines purpose-aware consent rules and makes applicable law/regulation and organizational policy authoritative for sensitive data.

Required action: Slice 1 may define the vocabulary/contract for consent, but must not silently reinterpret the existing binary flag as the complete future consent model. Consent schema expansion belongs to a separately audited minimal implementation slice.

## 5. Consumer Audit

Architecture is not selected from the vocabulary alone. Each candidate domain was traced through:

`Consumer → real use case → required data → required behavior → current capability → exact gap → minimum solution`

### 5.1 Current Need

- Consumer: Case / Recommendation
- Use case: current consultation need drives the current recommendation request.
- Required data: today's concerns / case context.
- Current capability: covered by Case plus the explicit consultation payload.
- Gap: none proven.
- Result: **CLOSED / remain Case-scoped**.

### 5.2 Profile Context

- Consumers: Customer profile retrieval/update and Recommendation profile construction.
- Use case: seller reuses customer context and may update the persistent profile.
- Current capability: Customer fields, customer search, profile retrieval, intake update, and read-only recommendation projection exist.
- Required missing behavior: provenance, lifecycle/freshness semantics, explicit confirmation, expiry/review, and conflict resolution.
- Gap: **CAPABILITY GAP confirmed**.
- Architectural conclusion: **model choice remains unproven**. Customer + Case still satisfies today's recommendation path.

### 5.3 Preference

- Current independent consumer: none proven.
- Purchase is linked to Customer and optionally Recommendation, but purchase is not evidence of a durable preference.
- Gap: **NO PROVEN GAP**.
- Result: do not introduce a Preference entity on current evidence.

### 5.4 Product Interaction / Outcome / Follow-up

- Consumer: previous-customer workflow and case-scoped Feedback.
- Purchase history is already represented by Sale → SaleItem → Product, with optional Recommendation linkage.
- Feedback already records outcome/comment/rating/follow_up_at against Case and optional Recommendation.
- Current capability: **PROVEN** for purchase history and case feedback.
- Missing consumer: no proven customer-wide follow-up queue, scheduler, or downstream decision that changes because of follow_up_at.
- Result: **no new Interaction, Outcome, or Follow-up entity is justified by current consumer evidence**.

### 5.5 Safety

- Product-side consumer: RecommendationService / ReasoningEngine consume QA-controlled Evidence and ProductKnowledge, including contraindications, existing conflicts, and medical-context handling.
- Customer-side Safety Signal consumer: none proven.
- Existing Customer observations/answers/operator_notes are generic and are not evidence of an independent safety domain.
- Gap: **business need exists; consumer behavior for a persistent customer Safety Signal is unproven**.
- Result: no new Safety entity and no new Recommendation safety gate.

### 5.6 Smart Summary

- Consumer: UI display.
- Source: existing customer/case/recommendation data.
- Required behavior: derived presentation.
- Gap: none proven.
- Result: **DERIVED / no persistence model**.

## 6. Architecture decision status

The Consumer Audit does **not** select A/B/C/D.

Current evidence yields:
- A — three independent tables: **not justified yet**
- B — one shared Record: **not justified yet**
- C — hybrid: **not justified yet**
- D — existing Customer/Case: **currently sufficient for proven recommendation and visit needs**

The unresolved Profile capability gap may require additional structure later, but the minimum structure must be proven by a subsequent architecture comparison. Preference, independent Outcome, and customer Safety Signal are not currently consumer-proven.


## 7. Explicit non-goals

This audit does not authorize:
- redesigning Customer
- replacing existing Customer fields
- schema-wide normalization
- new UI
- five-box implementation
- Smart Summary persistence
- recommendation scoring changes
- recommendation eligibility changes
- evidence-gate changes
- seed/product changes
- automatic promotion from purchase/recommendation to Preference
- automatic promotion from consultation input to Profile Fact

## 8. Required evidence before architecture selection

No model-specific implementation tests are authorized yet.

Before Architecture Selection, the next audit must compare the proven Profile capability gap against:
- existing Customer/Case only
- a shared record approach
- separate concepts
- a hybrid only where separation is behaviorally required

The comparison must explicitly measure:
- real consumer coverage
- duplication with Customer/Case
- provenance/lifecycle/freshness handling
- promotion/conflict risks
- migration and maintenance cost
- Recommendation dependency

## 9. Gate result

**CONSUMER AUDIT = IN PROGRESS / ARCHITECTURE BLOCKED**

Current disposition:
- Current Need → **CLOSED / Case**
- Preference → **NO PROVEN GAP**
- Smart Summary → **DERIVED / no persistence**
- Profile Context → **CAPABILITY GAP / architecture unknown**
- Product Interaction → **existing purchase-history capability; experience gap not consumer-proven**
- Outcome → **case-scoped Feedback exists; broader Outcome architecture not consumer-proven**
- Safety → **business need / persistent consumer unproven**

Therefore:
- **Architecture Selection = BLOCKED**
- **Schema Contract = BLOCKED**
- **Migration = BLOCKED**
- **Code = BLOCKED**
- **Recommendation / Scoring / Evidence Gates = FROZEN**

## 10. Acceptance evidence

The audit branch remains documentation-only. No application schema, model, migration, UI rewrite, or recommendation/scoring/evidence-gate code has been changed.
