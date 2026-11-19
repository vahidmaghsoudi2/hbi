# فعالیت ۳۹ — تطبیق نظر متخصص با شواهد

## Purpose
Reconcile reviewer records from Activity 38 against the Activity 36 topic inventory and a topic-keyed evidence ledger. This checks traceability and status only; it is not scientific validation.

## Outcomes
- `pending_specialist_review`
- `reviewed_pending_PO`
- `revision_requested`
- `specialist_accepted_scope_pending_PO`
- `not_applicable_pending_PO`
- `evidence_trace_mismatch`
- `owner_rule_separate`
- duplicate/invalid records → reconciliation required

## Rules
- All 15 inventory topics are emitted, including topics with no review records.
- Evidence references in specialist records must exist in the evidence ledger for that topic before accepted-within-scope is reconciled.
- Revision requested/comments do not equal accepted.
- Owner-defined Natural Extra topic cannot be specialist-accepted as owner authority.
- Duplicate review records are flagged, not silently overwritten.
- PO acceptance remains separate; no record is fabricated.

## Implementation
`app/domain/hair_color_specialist_review_reconciliation.py` report generator; `tests/test_hair_color_specialist_review_reconciliation.py` covers pending, evidence mismatch, status mapping, duplicate, invalid, owner-rule boundary and full inventory. Test/CI not executed.

## Next
Activity 40 — reconcile the specialist review package against roadmap/version scope and prepare an owner decision matrix; do not accept pending items or claim external review.
