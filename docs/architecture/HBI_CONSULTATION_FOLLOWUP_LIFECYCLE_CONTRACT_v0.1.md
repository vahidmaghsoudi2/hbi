# HBI Consultation Follow-up Lifecycle Contract v0.1

**Status:** READY FOR IMPLEMENTATION REVIEW  
**Baseline:** `f35c85a63e1d3a2f3cbed660e9217ffac9f0c7b6`  
**Gate:** Issue #242  
**Scope:** Contract only. No implementation is authorized by this artifact.

## 1. Reality

The repository currently provides:

`Recommendation → Customer Response → Feedback(source=CUSTOMER) → outcome`

Follow-up is currently represented only by nullable `Feedback.follow_up_at`. The repository does not establish an independent Follow-up entity, lifecycle state machine, completion/cancellation/reschedule operations, scheduler, reminder engine, or follow-up retrieval boundary.

## 2. Decision

Follow-up becomes a first-class durable domain object because a date stored on Feedback cannot represent lifecycle state, completion, cancellation, or rescheduling without overloading Feedback semantics.

The smallest V1 contract is an owned, case-scoped Follow-up record. It references the originating Case and may reference the originating Recommendation and Customer Feedback.

No scheduler, notification delivery, usage tracking, outcome-assessment engine, or learning loop is part of V1.

## 3. Follow-up State Contract

Initial state:

- `SCHEDULED`

Terminal states:

- `COMPLETED`
- `CANCELLED`

Legal transitions:

- `SCHEDULED → COMPLETED`
- `SCHEDULED → CANCELLED`
- `SCHEDULED → SCHEDULED` only for rescheduling, represented by changing the scheduled time while retaining lifecycle state.

Terminal states are immutable except through an explicitly defined correction mechanism in a future contract.

A scheduled time is required for `SCHEDULED`. Completion and cancellation record their mutation time and audit actor.

## 4. Ownership and Trace

A Follow-up is owned through its Case:

`Customer → Case → Recommendation → Customer Response / Feedback → Follow-up`

Required identity/trace fields for V1:

- `follow_up_id`
- `case_id`
- `recommendation_id` nullable
- `feedback_id` nullable
- `scheduled_at`
- `status`
- `created_at`
- lifecycle mutation timestamps/actor metadata sufficient for audit

A referenced Recommendation must belong to the same Case. A referenced Feedback must belong to the same Case. Cross-case references are rejected.

## 5. V1 Operations

The implementation slice may expose only the minimum lifecycle operations:

1. Create a Follow-up for an owned Case.
2. Retrieve Follow-ups for an owned Case.
3. Reschedule an active Follow-up by changing `scheduled_at`.
4. Complete an active Follow-up.
5. Cancel an active Follow-up.

Every mutation is authenticated, ownership-checked, durable, and auditable.

No bulk operations, scheduler, reminders, notifications, automatic creation, or background jobs are included.

## 6. Compatibility with Feedback.follow_up_at

`Feedback.follow_up_at` remains readable for backward compatibility during V1.

New Follow-up records are the authoritative lifecycle representation.

No migration/backfill is implied by this contract. Existing metadata is not silently converted into Follow-up entities.

A future migration, if required, must be separately specified and authorized.

## 7. Boundaries

Explicitly unchanged:

- Recommendation scoring
- Recommendation ranking
- Eligibility
- Evidence scoring
- Product Knowledge
- ProfileFact persistence
- Customer Response semantics
- Outcome vocabulary
- Sales/POS
- Product Usage
- Learning/weight updates
- Questionnaire/AI question generation
- Home/UI redesign
- Scheduler/notification infrastructure

## 8. Acceptance Evidence for the Next Vertical Slice

The implementation must prove at minimum:

- unauthenticated access is rejected;
- non-owner Case access is rejected;
- missing Case is rejected;
- invalid/cross-case Recommendation is rejected;
- invalid/cross-case Feedback is rejected;
- creation persists a Follow-up;
- retrieval is ownership-aware;
- reschedule updates only the active Follow-up schedule;
- completion moves `SCHEDULED → COMPLETED`;
- cancellation moves `SCHEDULED → CANCELLED`;
- terminal Follow-ups reject further lifecycle mutation;
- audit evidence exists for create/reschedule/complete/cancel;
- existing Customer Response and Recommendation behavior remains unchanged;
- no automatic ProfileFact write occurs.

## 9. Gate Conclusion

The repository evidence supports a small first-class Follow-up Lifecycle contract.

**REALITY GATE VERDICT: READY FOR NEXT VERTICAL SLICE**

Implementation requires a separate explicit PO authorization after this contract is merged.
