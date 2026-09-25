# HBI Consultation Follow-up Lifecycle — Reality Gate v0.2

| Field | Value |
|---|---|
| Issue | #247 |
| Audit baseline | `1175b6ad49794704b1cacf89b25ce8c7469cc57a` |
| Implementation | PR #246 |
| Implementation HEAD | `fe3d7d432cd4cb3c363b75ee16d72919ce4fb219` |
| Verdict | **ACCEPTED — READY FOR NEXT VERTICAL SLICE** |

## 1. Executive Verdict

The first-class Follow-up implementation is present on current Master and materially conforms to the accepted Lifecycle Contract v0.1.

No critical contract violation was identified within the audited boundary.

## 2. Durable Object

**CONFIRMED IN CODE**

Current Master contains a dedicated `FollowUp` model with:

- `follow_up_id`
- `case_id`
- nullable `recommendation_id`
- nullable `feedback_id`
- `scheduled_at`
- `status`
- creation/update actor and timestamps
- completion/cancellation timestamps

This establishes Follow-up as a durable object rather than Feedback metadata.

## 3. Lifecycle

**CONFIRMED IN CODE / TEST**

The implemented state machine is:

`SCHEDULED → COMPLETED`  
`SCHEDULED → CANCELLED`

Reschedule updates `scheduled_at` while preserving `SCHEDULED`.

Terminal states reject further lifecycle mutation with a conflict response.

## 4. Authorization

**CONFIRMED IN CODE / TEST**

Follow-up operations establish authenticated customer ownership of the target Case.

Observed acceptance coverage includes:

- unauthenticated access → 401;
- non-owner Case → 403;
- missing Case → 404;
- cross-Case Follow-up mutation → 403.

The authorization boundary remains Case-centered.

## 5. Traceability

**CONFIRMED IN CODE / TEST**

When supplied, Recommendation and Feedback references are validated before Follow-up creation.

Both must belong to the same Case as the Follow-up.

Therefore the durable trace is:

`Customer → Case → FollowUp`

with optional:

`Case → Recommendation / Feedback → FollowUp`

## 6. API Surface

**CONFIRMED IN CODE / TEST**

The implementation provides dedicated operations for:

1. Create
2. Case-scoped Retrieve
3. Reschedule
4. Complete
5. Cancel

The lifecycle is therefore explicit rather than encoded through arbitrary Feedback mutations.

## 7. Audit

**CONFIRMED IN CODE**

Dedicated lifecycle audit events are emitted for:

- creation;
- rescheduling;
- completion;
- cancellation.

Events contain target and actor information sufficient for the V1 lifecycle boundary.

## 8. Feedback Compatibility

**CONFIRMED IN CODE**

`Feedback.follow_up_at` remains available.

The implementation does not silently rewrite or backfill existing Feedback metadata.

This preserves backward compatibility while allowing new Follow-up records to carry their own lifecycle.

## 9. Explicit Exclusions

The audited implementation does not introduce, as part of this Slice:

- scheduler;
- notification worker;
- background jobs;
- automatic Follow-up creation;
- Usage;
- Outcome Assessment;
- Learning integration;
- Recommendation scoring/ranking/eligibility changes;
- ProfileFact changes;
- UI redesign.

These remain separate boundaries.

## 10. CI / Merge Evidence

- PR #246 exact HEAD: `fe3d7d432cd4cb3c363b75ee16d72919ce4fb219`
- HBI CI #841 / run `36112215809`: `test` SUCCESS; `governance-tests` SUCCESS.
- Independent verification was recorded before merge.
- Post-merge Master: `1175b6ad49794704b1cacf89b25ce8c7469cc57a`
- FollowUp model/API presence was verified on Master.

## 11. Contract-vs-Reality Result

| Contract requirement | Reality |
|---|---|
| Dedicated identity | CONFIRMED |
| Durable persistence | CONFIRMED |
| Case ownership | CONFIRMED |
| Same-Case Recommendation trace | CONFIRMED |
| Same-Case Feedback trace | CONFIRMED |
| SCHEDULED state | CONFIRMED |
| COMPLETED transition | CONFIRMED |
| CANCELLED transition | CONFIRMED |
| Reschedule without state change | CONFIRMED |
| Terminal mutation guard | CONFIRMED |
| Create/Retrieve/Reschedule/Complete/Cancel | CONFIRMED |
| Lifecycle audit | CONFIRMED |
| Feedback.follow_up_at compatibility | CONFIRMED |
| Scheduler/Notification V1 exclusion | CONFIRMED |
| Recommendation/ProfileFact/Learning isolation | CONFIRMED |

## 12. Gate Decision

**ACCEPTED — READY FOR NEXT VERTICAL SLICE**

The Follow-up lifecycle boundary is now sufficiently represented in code, persistence, authorization, tests, and audit to move forward.

Any next capability must receive its own explicit boundary and reality verification rather than being appended informally to Follow-up.

*End of HBI Consultation Follow-up Lifecycle Reality Gate v0.2.*
