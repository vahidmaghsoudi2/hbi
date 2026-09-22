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

This audit authorizes a minimal additive backend slice only after the dictionary/contract mismatch identified below is corrected. It does not authorize recommendation, scoring, evidence-gate, seed, or product-rule changes.

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

## 5. What Slice 1 should implement

The smallest safe executable boundary is an additive structured-record foundation, not a Customer-table rewrite.

Minimum target concepts for the next implementation slice:
1. `ProfileFact`
2. `Preference`
3. `ConstraintSafetySignal`

Each record must support, at minimum:
- stable identifier
- customer identifier
- canonical attribute/key
- value or structured payload
- value state where applicable
- approved provenance
- approved lifecycle/status
- recorded timestamp
- optional effective/review metadata where required by freshness semantics
- audit-compatible actor/context fields

Current Need remains visit/case scoped and should continue to be carried by Case/consultation context rather than copied into a permanent Customer Fact.

Product Interaction and Outcome are intentionally outside this first backend slice unless a separate Slice 1A audit demonstrates they can be added without widening the boundary.

## 6. Explicit non-goals

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

## 7. Required tests for the minimal backend slice

At minimum, the implementation PR must prove:
- records are linked to the correct Customer
- allowed value states are accepted and invalid states are rejected
- only approved provenance values are accepted
- lifecycle/status values follow Contract v1.1
- Current Need is not auto-promoted to permanent Profile Fact
- purchase/recommendation does not auto-create Preference
- conflicting facts preserve both provenance/context rather than silently overwrite
- existing Customer → Case → recommendation integration remains green and unchanged

## 8. Gate result

**REALITY AUDIT FOR SLICE 1 = PASS WITH REQUIRED CONTRACT ALIGNMENT**

The repository is structurally ready for a small additive backend foundation, but the older Data Dictionary contains vocabulary and freshness semantics that conflict with the approved Contract v1.1.

Therefore the next action is:

**Contract/Data Dictionary alignment → minimal additive backend models → focused tests → CI → runtime verification**

No recommendation/scoring/evidence-gate work is in this slice.

## 9. Acceptance evidence

The audit branch contains documentation only. No application schema, UI, or recommendation code has been changed by this audit.
