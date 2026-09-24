# HBI-CONSULTATION-VERTICAL-SLICE-001 — Evidence Package

| Field | Value |
|-------|--------|
| Mission | Issue #214 |
| Baseline Master | `3a8db5437d8febccc258c8bf2e85bed744716ece` |
| Implementation | Narrow tests + evidence doc proving existing runtime path |
| Not in scope | Home redesign, ProfileFact→Rec, Problem/Assessment entities, scoring changes, Evidence Gap API |

## Reality Audit (summary)

| Item | Classification | Evidence |
|------|----------------|----------|
| Customer + pilot JWT | FACT | `auth` pilot-token; `get_current_customer_id` |
| Case create/ownership | FACT | `POST /api/v1/cases/` 201/403 |
| Generate path | FACT | concerns → factors → needs → eligibility → list |
| Only ELIGIBLE persisted | FACT | `recommendation_service` continue if not ELIGIBLE |
| Empty list valid | FACT | generate returns `[]` |
| Feedback optional | FACT | `POST /api/v1/specialist/feedback` |
| ProfileFact in Rec | FACT not used | Phase 1 O1 |

## Contract Check

Aligned with Minimal Contract v0.1 + Phase 1 Decisions on master. No parallel domain stack.

## Tests

`tests/test_consultation_vertical_slice_001.py`

Local focused run (implementation agent):
`PYTHONPATH=. python -m pytest tests/test_consultation_vertical_slice_001.py -q` → **6 passed**

Related regression subset: recommendations_api + pilot_e2e + vertical_slice + gap04 + f2 → **29 passed**

## OPEN / UNKNOWN / CONFLICT

None blocking this slice. Home Case/Need-first remains DEFERRED (O5).
