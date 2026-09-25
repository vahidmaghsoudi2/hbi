# HBI Consultation Outcome Context Contract v0.1

## Status

**CONTRACT ACCEPTED — IMPLEMENTATION AUTHORIZATION SEPARATE**

| Field | Value |
|-------|-------|
| Issue | #255 |
| Gate | HBI-CONSULTATION-OUTCOME-CONTEXT-CONTRACT-GATE-001 |
| Reality baseline | `e9df363ad80b16f0cf6524bad9f3134d1bf16082` |
| Independent review | ACCEPTED (Grok re-review after R1–R3) |
| Implementation | Not authorized by this document alone |

## 1. Purpose

Define the smallest safe boundary for exposing relevant longitudinal Outcome Assessment history to a future consultation as **read-only decision-support context**, without changing Recommendation scoring, ranking, eligibility, or evidence semantics.

## 2. Authority

- **Case** remains the Source of Truth for each OutcomeAssessment.
- **Profile History** (`/api/v1/outcome-assessments/profile-history`) is a longitudinal **projection**, not a second source of truth.
- Consultation context may read the projection but must preserve source identifiers so the originating Case and OutcomeAssessment remain traceable.

## 3. Eligible context fields

Only explicitly recorded OutcomeAssessment records are eligible. No inferred success or failure is permitted.

The read-only longitudinal context **MUST** carry:

- `outcome_assessment_id`
- `case_id`
- `result_state`
- `observed_at`
- `created_at`
- `provenance`
- `actor_id` when available
- optional `product_id`
- optional `recommendation_id`
- optional `feedback_id`
- optional `follow_up_id`

## 4. Result semantics

| State | Meaning |
|-------|---------|
| POSITIVE | Explicitly reported positive result |
| PARTIAL | Explicitly reported partial result |
| NO_BENEFIT | Explicitly reported lack of benefit |
| ADVERSE_REACTION | Explicitly reported adverse reaction |
| NOT_USED | Explicitly recorded non-use; **must not** be treated as treatment failure |
| UNKNOWN | Explicitly unknown; **must not** be converted to positive/negative evidence |

## 5. Temporal rule

Order for presentation/context only:

`observed_at DESC`, then `created_at DESC`.

Multiple assessments remain distinct. No overwrite and no arbitrary collapse.

**Recency alone never selects one assessment as authoritative and never suppresses another assessment.**

## 6. Relevance / scoping

A historical assessment is contextually relevant when:

- it is linked to the current customer, and
- its trace identifies the same product or recommendation, **or**
- the contractually exposed longitudinal history is requested as general context.

Product/recommendation linkage must remain explicit. Relevance must not be inferred solely from a Sale or from the mere existence of a Recommendation.

## 7. Precedence

OutcomeAssessment history is **strictly additive longitudinal context**. It does not occupy or populate ProfileFact consultation slots and does not participate in the ProfileFact precedence chain.

Explicit order:

1. **Current consultation input** — authoritative for the current Case.
2. **ProfileFact** — authoritative for durable customer attributes already represented through the ProfileFact pathway.
3. **Legacy Customer** — fallback where existing behavior supports it.
4. **OutcomeAssessment history** — additive historical outcome context only.

Historical outcomes must never overwrite, supersede, or silently fill a current-consultation or ProfileFact attribute.

## 8. Conflicts

Conflicting OutcomeAssessments are preserved and surfaced as conflicting historical observations.

Case remains the authority for each individual assessment.

## 9. Provenance and traceability

Any decision-support context derived from an OutcomeAssessment must carry at least:

- `outcome_assessment_id`
- originating `case_id`
- `provenance`

Customer-reported outcome remains an experience report, not an independent clinical determination.

## 10. Recommendation boundary

V1 may expose historical OutcomeAssessment context to the existing recommendation input/context boundary as **additive context only**.

Must **not** alter:

- scoring
- ranking
- eligibility
- evidence semantics
- recommendation vocabulary

## 11. ProfileFact boundary

No automatic promotion from OutcomeAssessment to ProfileFact.

A stable attribute may become ProfileFact only through the existing explicit ProfileFact pathway and rules.

## 12. Explicit V1 exclusions

This contract does **not** authorize:

- Product Usage subsystem
- automatic outcome creation
- automatic Follow-up creation
- scheduler / notifications / background jobs
- clinical outcome determination
- automatic ProfileFact promotion
- UI redesign
- recommendation algorithm redesign
- accounting / POS / PAY-AUTH changes

## 13. Candidate smallest vertical slice

```text
Authenticated customer
  → owned Case
  → read-only longitudinal OutcomeAssessment context projection
  → existing consultation context (additive)
  → existing recommendation path (unchanged scoring/ranking/eligibility)
  → trace (outcome_assessment_id + case_id + provenance)
```

## 14. Gate decision

**CONTRACT ACCEPTED** after independent re-review (R1–R3 resolved).

Implementation requires a separate PO authorization issue/PR and must prove the acceptance matrix against this contract.

*End of HBI Consultation Outcome Context Contract v0.1.*
