# HBI Consultation Outcome Assessment Contract v0.1

## Status

**CONTRACT DRAFT — IMPLEMENTATION NOT AUTHORIZED**

Baseline Master: `d4bb05d3b576301c07e7298e2bc4d831544087c5`

Source Reality Gate: Issue #249 — Outcome Assessment Reality Audit

PO decisions:
- Build explicit Outcome Assessment: YES
- Use a first-class independent structure: YES
- Keep the originating Case as the source-of-truth context: YES
- Expose longitudinal history/summary in Customer Profile: YES
- Promote to ProfileFact only when a stable customer attribute is justified: YES
- Make outcome recording after FollowUp completion mandatory: NO; optional in V1

## 1. Purpose

Outcome Assessment records an explicit observed or customer-reported result of a consultation/recommendation experience.

It answers: **What happened after the recommendation, response, or follow-up?**

It is a durable event/result record. It is not a replacement for Customer Response, Feedback.outcome, FollowUp status, Sale, or ProfileFact.

## 2. Semantic Boundaries

| Construct | Meaning | Outcome Assessment? |
|---|---|---|
| Customer Response | Customer's explicit response to a recommendation | No |
| Feedback.outcome | V1 disposition of Customer Response | No |
| FollowUp.status | Operational lifecycle of a follow-up task | No |
| Sale | Recorded commercial transaction | No |
| Product Usage | Explicitly reported use | Only when explicitly recorded |
| Observed Result | Explicit reported/observed result | Yes |
| Outcome Assessment | Durable structured result record | Yes |
| ProfileFact | Durable customer attribute | No; separate promotion decision |

## 3. Identity and Ownership

Each assessment has a unique `outcome_assessment_id`.

Required:
- `case_id`

The assessment is owned through the Case and is accessible only within the authenticated actor's authorized Case boundary.

Optional trace links:
- `recommendation_id`
- `feedback_id`
- `follow_up_id`
- `product_id`

Every supplied optional trace must belong to the same Case. A FollowUp link is valid only when that FollowUp is `COMPLETED`.

## 4. Result Semantics

V1 result states:
- `POSITIVE` — reported/observed improvement or satisfactory result
- `PARTIAL` — some benefit or mixed result reported
- `NO_BENEFIT` — explicitly reported no meaningful benefit
- `ADVERSE_REACTION` — explicitly reported undesirable reaction/event
- `NOT_USED` — explicitly reported that the relevant product/service was not used
- `UNKNOWN` — result is not known or cannot be established

The system preserves what was reported, who reported it, when it was reported, and the structured result state.

The system must not infer a result from a sale, follow-up completion, rating, or missing data.

## 5. Provenance

Required provenance:
- `CUSTOMER`
- `SELLER`
- `SPECIALIST`
- `SYSTEM`

Preserve actor identity where available and the assessment timestamp.

A customer-reported result is a report of experience; it is not an independent clinical determination.

## 6. Optional Product Link

Product linkage is optional.

A product-specific assessment may link to `product_id` and must remain traceable to the Case.

No product link is created merely because a Recommendation or Sale exists.

**Recommendation ≠ Product Usage ≠ Outcome.**

## 7. Multiple Assessments

Multiple assessments may exist for the same Case, Recommendation, Product, or FollowUp when they represent distinct observations or reports over time.

Each remains independently identifiable by identity, timestamp, provenance/actor, and trace links.

A new assessment does not overwrite earlier history.

## 8. Profile History

Customer Profile should provide a concise longitudinal history/summary of relevant Outcome Assessments and Follow-ups.

The Profile view is a projection/summary. The originating Case remains authoritative for the complete event.

Profile history should let a seller/specialist understand previous experiences without reconstructing every Case manually.

## 9. ProfileFact Promotion

Outcome Assessment does not automatically create or mutate ProfileFact.

A separate explicit rule is required before promoting an assessment into a durable ProfileFact.

An individual product experience remains an Outcome Assessment. A stable preference or characteristic supported by sufficient evidence may later become a ProfileFact, while retaining traceability to the source Case.

## 10. Retrieval Boundary

V1 must support:
- retrieval by Case,
- tracing/filtering by Recommendation when supplied,
- tracing to Product, Feedback, or FollowUp when linked.

Customer Profile history may consume these Case-linked records as a read projection.

No Recommendation scoring, ranking, eligibility, or evidence behavior changes.

## 11. Audit

Create and subsequent lifecycle mutations must be auditable.

Audit records should identify:
- assessment ID,
- Case ID,
- relevant trace IDs,
- actor/source,
- result state,
- timestamp,
- mutation type.

The audit trail must distinguish Outcome Assessment events from Customer Response, Feedback, and FollowUp operations.

## 12. V1 Write Boundary

Smallest vertical slice:

`Authenticated actor → Owned Case → optional same-Case Recommendation / Feedback / COMPLETED FollowUp / Product → Outcome Assessment → persist → retrieve → audit`

V1 provides explicit create and retrieval behavior.

Outcome recording remains optional after FollowUp completion.

## 13. Explicit Exclusions

This contract does not authorize:
- automatic Outcome creation after FollowUp completion,
- scheduler or notifications,
- Product Usage subsystem,
- clinical outcome determination,
- automatic ProfileFact promotion,
- changes to Recommendation scoring/ranking/eligibility/evidence,
- changes to Customer Response semantics,
- changes to FollowUp lifecycle,
- accounting/POS changes,
- UI redesign.

## 14. Implementation Acceptance Preconditions

The implementation PR must prove:
1. Case ownership enforcement.
2. Same-Case validation for every optional trace.
3. FollowUp trace requires COMPLETED.
4. Explicit result state is persisted without inference.
5. Provenance, actor, and timestamp are persisted.
6. Multiple assessments remain independently retrievable.
7. Profile history consumes records without becoming source of truth.
8. ProfileFact is unchanged.
9. Recommendation behavior is unchanged.
10. Audit distinguishes Outcome Assessment events.
11. Targeted tests and full CI pass on the exact PR HEAD.

## Decision Gate

**CONTRACT READY FOR INDEPENDENT REVIEW**

Implementation remains unauthorized until this contract is accepted.
