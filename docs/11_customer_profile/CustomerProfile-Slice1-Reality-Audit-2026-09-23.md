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

## 5. Consumer Audit — CLOSED

Each candidate domain was traced through:

`Consumer → real use case → required data → required behavior → current capability → exact gap → minimum solution`

### 5.1 Current Need

- Consumer: Case / Recommendation.
- Use case: today's consultation need drives the current recommendation request.
- Required data: today's concerns and case context.
- Current capability: Case plus explicit consultation payload.
- Gap: none proven.
- Decision: **remain Case-scoped**.

### 5.2 Profile Fact / reusable profile context

- Consumers: customer retrieval/update and Recommendation profile construction.
- Use case: reuse a customer attribute across visits and update it without confusing it with today's need.
- Current capability: Customer fields, search, retrieval, intake update, and read-only recommendation projection.
- Proven missing behavior: provenance, lifecycle/freshness semantics, explicit confirmation/promotion, expiry/review, and conflict handling.
- Gap: **confirmed capability gap**.
- Architectural implication: this is the only candidate domain for which a new structured capability is presently justified.

### 5.3 Preference

- Consumer: no independent executable consumer proven.
- Purchase history exists through Sale → SaleItem → Product and may reference a Recommendation.
- Purchase is not durable preference evidence.
- Gap: **not proven**.
- Decision: **no Preference entity**.

### 5.4 Product Interaction / Outcome / Follow-up

- Purchase interaction is already represented by Sale → SaleItem → Product.
- Case-scoped Feedback already records source, outcome, rating, comment and follow_up_at, with optional Recommendation linkage.
- Feedback is owner-bound through the Case.
- No proven customer-wide follow-up queue, scheduler, or downstream decision was found.
- Gap: experience/outcome aggregation across customer history is a possible future capability, but its consumer is not proven.
- Decision: **reuse current Sale/SaleItem/Feedback; no new Interaction/Outcome/Follow-up entity in this slice**.

### 5.5 Safety

- Product-side safety behavior is already consumed through QA-controlled Evidence/ProductKnowledge and the existing Reasoning/Recommendation path.
- Customer-side persistent Safety Signal has no proven executable consumer in the current repository.
- Customer observations/answers/operator_notes are generic fields and do not establish a separate safety contract.
- Decision: **no new Safety entity and no Recommendation safety-gate change**.

### 5.6 Smart Summary

- Consumer: presentation.
- Source: existing Customer/Case/Recommendation data.
- Behavior: derived projection.
- Decision: **no persistence model**.

## 6. Architecture Comparison

The evidence changes the question from "which three new models should be built?" to "what is the smallest structure required for the one proven capability gap?"

| Option | Real consumer coverage | Duplication risk | Provenance/lifecycle/freshness | Migration/maintenance | Decision |
|---|---|---|---|---|---|
| A — three independent tables | Low: only Profile Fact has a proven consumer | High | Good in theory, unnecessary for unproven domains | High | **Reject as overbuilt** |
| B — one shared Record | Medium in abstract; requires semantics for Preference/Safety that are not consumer-proven | Medium/High | Can support metadata, but risks semantic overload | Medium | **Reject for now** |
| C — hybrid | Medium; separation is not behaviorally required yet | Medium | Potentially good | Medium/High | **Reject for now** |
| D — existing Customer/Case only | High for current recommendation/visit behavior | Low | Insufficient for the proven Profile Fact capability gap | Low | **Insufficient alone** |

### 6.1 Architecture Selection

**Selected boundary: D-plus, narrowly scoped to the proven Profile Fact capability gap.**

Meaning:
- retain existing Customer as the customer identity/root;
- retain Case as the visit/current-need boundary;
- retain Sale/SaleItem for purchase interaction;
- retain Feedback for case-scoped outcome/follow-up recording;
- add structured Profile Fact capability only if the next Schema Contract proves that the required provenance/lifecycle/freshness behavior cannot be represented safely in existing Customer without semantic overload.

This is deliberately **not** authorization to create a generic Record, Preference, Safety, Outcome, or Follow-up model.

### 6.2 Why D-plus is the minimum justified architecture

The repository already has executable consumers for Customer and Case. The missing behavior is not "more profile fields"; it is the ability to distinguish a reusable profile fact from:
- today's Current Need,
- an observation,
- a purchase,
- a recommendation,
- or an unconfirmed statement,

while retaining controlled provenance and lifecycle/freshness semantics.

A separate Profile Fact structure is therefore a hypothesis justified by the proven behavior gap; its exact schema remains a separate gate.

## 7. Risk Review

### R1 — Semantic overload
Adding more meanings to Customer string fields would preserve today's simplicity but increase ambiguity between persistent facts, current needs, observations, and unconfirmed inputs.

**Disposition:** resolve through the next schema contract, not through ad-hoc fields.

### R2 — False promotion
Purchase, recommendation, or consultation input could be mistaken for durable preference/profile fact.

**Disposition:** preserve Contract v1.1 promotion rules.

### R3 — Freshness errors
Universal TTLs could incorrectly expire durable facts or retain volatile ones too long.

**Disposition:** attribute-specific freshness policy; no universal TTL.

### R4 — Consent overreach
The binary Customer consent flag cannot be treated as a complete purpose-aware future consent model.

**Disposition:** keep current field as current reality; separately contract any future expansion.

### R5 — Recommendation contamination
Profile architecture changes could accidentally alter recommendation scoring or eligibility.

**Disposition:** Recommendation/Scoring/Evidence Gates remain frozen; any adapter is read-only and separately tested.

### R6 — Unproven domain expansion
Building Preference/Safety/Outcome/Follow-up entities before an executable consumer exists creates schema without demonstrated operational value.

**Disposition:** defer.

## 8. Consumer Audit Gate

**CONSUMER AUDIT = COMPLETE**

Confirmed:
- Current Need → **Case**
- Profile Fact → **proven capability gap**
- Preference → **no proven gap**
- Product Interaction → **existing Sale/SaleItem capability**
- Outcome/Follow-up → **existing case-scoped Feedback capability**
- Safety Signal → **business need, consumer unproven**
- Smart Summary → **derived projection**

Architecture:
- A → **rejected as overbuilt**
- B → **rejected for now**
- C → **rejected for now**
- D → **insufficient alone**
- **D-plus / Profile Fact-only boundary → selected for next contract gate**

## 9. Next Gate — Schema Contract

The next artifact must define only the minimum Profile Fact contract and prove:
1. required fields for value, value_state, provenance, lifecycle/status, freshness/review metadata, timestamps and ownership;
2. confirmation/promotion semantics;
3. conflict and supersession semantics;
4. edit/delete/revoke behavior and audit requirements;
5. relationship to Customer and Case;
6. read-only mapping into Recommendation profile;
7. migration/backfill policy, including what happens to legacy Customer fields;
8. focused tests for persistence, update, stale/conflict handling, promotion rules, and recommendation non-regression.

No schema, migration, model, UI, or recommendation implementation is authorized by this document.

## 10. Acceptance evidence

The audit branch remains documentation-only. No application schema, model, migration, UI rewrite, or recommendation/scoring/evidence-gate code has been changed.
