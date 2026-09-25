# HBI Consultation Follow-up Lifecycle Reality Gate v0.1

| Field | Value |
|---|---|
| Baseline | `3289d8c16ebf9a05a2e3c1ded2d1d3db345736bb` |
| Gate | HBI-CONSULTATION-FOLLOWUP-LIFECYCLE-REALITY-GATE-003 |
| Scope | Customer Response / Outcome → Follow-up Lifecycle |
| Implementation | **NOT AUTHORIZED BY THIS GATE** |
| Verdict | **READY FOR NEXT VERTICAL SLICE** |

## 1. Baseline

This gate is anchored to the actual Master after PR #238, which completed the explicit Customer Response Outcome Contract.

Current Master reality therefore includes:
- explicit Customer Response;
- server-controlled `source=CUSTOMER`;
- Recommendation-to-Case validation;
- four-value Customer Response outcome vocabulary;
- durable Feedback retrieval;
- optional `Feedback.follow_up_at`.

## 2. Files / Code Paths

Primary evidence inspected:
- `app/models/feedback.py`
- `app/services/feedback_service.py`
- `app/api/routers/specialist.py`
- `tests/test_consultation_vertical_slice_001.py`
- `docs/architecture/HBI_CONSULTATION_FOLLOWUP_OUTCOME_REALITY_GATE_v0.1.md`

Required evidence statuses:
**CONFIRMED IN CODE / CONFIRMED IN TEST / CONFIRMED IN DOC / NOT FOUND / CONFLICT / UNKNOWN**

## 3. Follow-up Data Reality

### Field
**CONFIRMED IN CODE**

`Feedback.follow_up_at` is a nullable DateTime column.

It is accepted by generic Feedback creation and by the explicit Customer Response action, and is returned by Case-scoped Feedback retrieval.

### Persistence
**CONFIRMED IN CODE**

The value is persisted directly on the Feedback row. No separate Follow-up record is created.

### Retrieval
**CONFIRMED IN CODE**

Current retrieval is through:

`GET /api/v1/specialist/feedback/case/{case_id}`

The serialized Feedback DTO includes `follow_up_at`.

### Audit
**CONFIRMED IN CODE**

Feedback creation audit records include `follow_up_at`. Explicit Customer Response audit also records the value.

## 4. Follow-up Lifecycle Reality

### Dedicated Follow-up entity
**NOT FOUND**

No dedicated Follow-up model/table was verified.

### Dedicated service
**NOT FOUND**

No Follow-up lifecycle service was verified.

### Scheduling / reminders
**NOT FOUND**

No scheduler, reminder worker, notification lifecycle or due-follow-up processor was verified in the inspected runtime.

### Completion
**NOT FOUND**

No durable follow-up completion state or completion endpoint was verified.

### Cancellation
**NOT FOUND**

No cancellation state or cancellation endpoint was verified.

### Rescheduling
**NOT FOUND**

No rescheduling operation or lifecycle state transition was verified.

### Active-follow-up invariant
**NOT FOUND**

Because `follow_up_at` belongs to individual Feedback rows, multiple Feedback rows can carry different dates. No single-active-follow-up invariant exists in the verified contract.

## 5. Ownership / Authorization

**CONFIRMED IN CODE**

Feedback creation and Case retrieval pass through authenticated customer identity and Case ownership validation.

The explicit Customer Response action also requires the authenticated customer to own the Case.

There is currently no separate Follow-up endpoint whose authorization boundary must be audited.

## 6. Recommendation / Case Traceability

**CONFIRMED IN CODE**

Current durable relation:

`Customer → owned Case → Recommendation → Feedback → follow_up_at`

When a Recommendation is supplied:
- it must exist;
- it must belong to the supplied Case;
- the Feedback row stores its Recommendation ID.

Follow-up metadata therefore remains attached to the Feedback event, not to an independent Follow-up object.

## 7. Outcome Boundary

**CONFIRMED IN CODE**

PR #238 now enforces the explicit Customer Response vocabulary:

- `ACCEPTED`
- `REJECTED`
- `PARTIAL`
- `FOLLOW_UP_NEEDED`

`FOLLOW_UP_NEEDED` is an outcome label. It does not itself create a Follow-up record, reminder, task or lifecycle state.

This distinction is important:

**reported outcome ≠ scheduled follow-up lifecycle**

## 8. Existing Tests

**CONFIRMED IN TEST**

The consultation vertical-slice tests verify Customer Response authentication, Case ownership, Recommendation linkage, persistence and retrieval.

The current inspected test suite does not establish a dedicated Follow-up lifecycle contract. That matches the runtime evidence: there is no such subsystem to test.

## 9. Documentation Consistency

**CONFIRMED IN DOC / CONFLICT WITH HISTORICAL BASELINE**

Older consultation documentation correctly described `follow_up_at` as Feedback metadata and deferred richer Follow-up lifecycle behavior.

Some historical documents were written before PR #238 and therefore describe Outcome as open runtime vocabulary. Current Master has since closed that vocabulary specifically for the explicit Customer Response action.

For Follow-up, however, the historical statement remains accurate:

**Feedback date metadata exists; a Follow-up lifecycle subsystem does not.**

## 10. Confirmed Gaps

1. No dedicated Follow-up entity.
2. No Follow-up lifecycle service.
3. No scheduler/reminder subsystem.
4. No completion state.
5. No cancellation state.
6. No rescheduling state.
7. No single-active-follow-up invariant.
8. No dedicated Follow-up retrieval/action API.
9. No dedicated Follow-up audit lifecycle.
10. No UI/runtime contract proving a Follow-up task lifecycle.

## 11. Smallest Next Vertical Slice

The evidence supports one narrow next boundary:

`Feedback.follow_up_at → Explicit Follow-up Record / Lifecycle`

However, this should **not** be implemented merely by adding another field or endpoint to Feedback.

The minimum coherent lifecycle requires a defined contract for:
- Follow-up identity;
- Case ownership;
- optional Recommendation/Feedback linkage;
- scheduled time;
- lifecycle state;
- completion;
- cancellation;
- rescheduling;
- audit;
- retrieval.

Until that contract is explicitly accepted, the current safe runtime remains:

**Feedback + optional follow_up_at metadata**

## 12. Implementation Constraints

If a Follow-up implementation is authorized later:
- begin with a dedicated contract/reality gate for lifecycle states;
- preserve existing Feedback semantics;
- do not reinterpret `FOLLOW_UP_NEEDED` as an automatic scheduled task;
- preserve Case ownership;
- preserve Recommendation/Feedback traceability;
- define audit for every lifecycle mutation;
- avoid automatic scheduling until a lifecycle state machine is explicitly defined;
- no changes to Recommendation scoring/ranking/eligibility/evidence;
- no ProfileFact writes;
- no Usage or CustomerChoice implementation hidden inside Follow-up;
- no schema change without an explicit implementation contract.

## 13. Final Gate Verdict

**READY FOR NEXT VERTICAL SLICE**

Reason: the repository has reliable follow-up **metadata**, but no Follow-up **lifecycle**. The next implementation boundary, if authorized, is therefore a dedicated Follow-up lifecycle contract rather than incremental mutation of Feedback.

**This gate authorizes no implementation by itself.**

*End of HBI Consultation Follow-up Lifecycle Reality Gate v0.1.*
