# CUSTOMER → CONSULTATION REALITY AUDIT v1 — Corrections

## Baseline

- Repository: `vahidmaghsoudi2/hbi`
- Master baseline: `e110d2c46dfa966009118a0aee6d040ee932ea28`
- Scope: Reality Audit correction only
- Implementation: **NOT AUTHORIZED**
- Production code changes: **NONE**

## Purpose

This addendum corrects four factual points in the CUSTOMER → CONSULTATION REALITY AUDIT v1 while preserving its confirmed findings and GAP classification.

---

## Correction 1 — hair / scalp / age context

### Repository reality

`ProfileFactContextService` defines:

```
CONTEXT_KEYS = { "skin_profile", "concerns" }
```

Therefore only `skin_profile` and `concerns` are directly read from ProfileFact for consultation context.

However, the same service also reads legacy Customer fields:

- `hair_profile`
- `scalp_profile`
- `age_range`
- `skin_profile`
- `concerns`

Legacy `hair_profile` and `scalp_profile` are subsequently incorporated into the effective `concerns` string used by the recommendation input surface.

### Correct conclusion

The accurate statement is:

> hair/scalp are not ProfileFact projection keys, but legacy Customer hair/scalp values can still reach Recommendation through the derived concerns input. `age_range` is surfaced in context, but this audit does not establish an explicit Need/Factor path for age.

Therefore:

- **ProfileFact hair/scalp projection:** NOT PRESENT
- **Legacy hair/scalp → effective recommendation input:** PRESENT
- **Explicit age → Need/Factor path:** NOT PROVEN

This replaces the stronger statement that hair/scalp are simply absent from Recommendation context.

---

## Correction 2 — Consent boundary

### Repository reality

When `customer.consent_to_store_data == 1`, ProfileFact rows for the consultation context keys are read.

When consent is inactive:

```
ProfileFact
   ↓
excluded from context
```

The service still reads legacy Customer fields independently.

### Correct conclusion

> `consent_to_store_data` is a ProfileFact read gate, not a universal Customer-profile read gate.

Therefore:

```
Consent = inactive
    ↓
ProfileFact excluded
    ↓
Legacy Customer context may still be present
```

Current consultation input remains independently usable.

This distinction must be preserved in any future Consent Contract.

---

## Correction 3 — Outcome Assessment Context

### Repository reality

The current `POST /recommendations/generate` path builds:

1. current consultation input;
2. `ProfileFactContextService`;
3. `OutcomeAssessmentContextService`;
4. `RecommendationFacade.generate`.

The resulting recommendation profile contains:

```
_outcome_assessment_context
```

### Correct conclusion

The complete current runtime path is:

```
Customer
  ↓
Case
  ↓
Current Consultation
  ↓
ProfileFactContextService
  ↓
OutcomeAssessmentContextService
  ↓
RecommendationFacade
  ↓
Need / Factors
  ↓
Product Catalog
  ↓
Evidence + ProductKnowledge
  ↓
Reasoning / Eligibility
  ↓
Recommendation
```

Outcome Assessment is therefore part of the **consultation context surface**, but this does **not** establish that Outcome Assessment directly changes scoring, ranking, or eligibility.

Its role remains additive longitudinal context under the existing contract.

---

## Correction 4 — Case identified_needs / evidence_gaps

### Repository reality

The Case model contains:

- `identified_needs`
- `evidence_gaps`

But the current recommendation generation path does not establish these fields as the authoritative runtime source for Need.

Current Need formation is principally driven by current consultation `concerns`, with context projection contributing to the effective consultation profile.

### Correct conclusion

```
Case.identified_needs
Case.evidence_gaps
        ≠
authoritative runtime Need source
```

These fields exist in the Case model but their role as durable runtime decision state is not established by the current generate path.

This remains a confirmed architectural boundary/GAP and requires a separate evidence-bound decision before implementation.

---

## Corrected Current Reality

```
Customer
  │
  ├── identity / consent / legacy profile
  │
  ▼
Case
  │
  ├── current consultation input
  ├── identified_needs       [model field; not runtime Need SoT]
  └── evidence_gaps          [model field; not runtime Need SoT]
  │
  ▼
ProfileFactContextService
  │
  ├── CURRENT consultation
  ├── ProfileFact skin_profile / concerns
  └── legacy Customer fallback
  │
  ▼
OutcomeAssessmentContextService
  │
  └── additive longitudinal outcome context
  │
  ▼
Recommendation
  │
  ├── concerns → Need normalization
  ├── Product ACTIVE + VERIFIED + VALID + stock
  ├── ProductKnowledge
  ├── Evidence
  └── Reasoning / eligibility
```

## Final Classification

| Item | Corrected status |
|---|---|
| ProfileFact keys | skin_profile + concerns only |
| Legacy hair/scalp | Can reach recommendation input through derived concerns |
| age_range | Context surfaced; explicit Need/Factor use not proven |
| Consent | ProfileFact read gate, not universal Customer-profile gate |
| Outcome Assessment | Additive longitudinal context is present in generate |
| Outcome Assessment scoring change | Not established |
| Case.identified_needs | Exists, not runtime Need SoT |
| Case.evidence_gaps | Exists, not runtime Need SoT |
| Production implementation | NOT AUTHORIZED |
| Code changes in this correction | NONE |

## Evidence inspected

- `app/services/profile_fact_context_service.py`
- `app/api/routers/recommendations.py`
- `app/models/case.py`
- current Master: `e110d2c46dfa966009118a0aee6d040ee932ea28`

## Gate

```
CUSTOMER → CONSULTATION REALITY AUDIT v1
CORRECTIONS: COMPLETE
PRODUCTION CODE: UNCHANGED
IMPLEMENTATION: NOT AUTHORIZED
BASELINE: e110d2c46dfa966009118a0aee6d040ee932ea28
```
