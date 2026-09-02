# HBI Accounting — Execution Plan (Tracking)
**Contract:** HBI ACCOUNTING MASTER EXECUTION CONTRACT V1.0  
**Implementation Owner:** Grok2  
**Phase 10 baseline:** `4e59380c4395d41ea71073571e7794b2a7bcda37`  
**Phase 11 baseline:** `a7c6c6db33c22c5fa66ba65bcb623d12fdb8811e`  
**Last Updated:** 2026-09-02

## Frozen decisions

| ID | Decision | Status |
|----|----------|--------|
| C-01 | USD + FX Snapshot; formula `(toman×10)/R` | **APPROVED** |
| C-02 | Category entity; بوست≠مو | **APPROVED** |

## Phase Status Board

| Phase | Name | Status | Owner |
|-------|------|--------|-------|
| 00–09 | … | **CLOSED / PASS** | Grok2 |
| 10 | Returns Workflow | **CLOSED / PASS** | Grok2 |
| 11 | Currency / FX Workflow | **CLOSED / PASS** | Grok2 |
| 12+ | Reports / … | **STOPPED** | — |

## Phase 11 summary

- Shared C-01 helpers in `currency_fx.py`.
- `OperationalFxService` for current rate; never mutates historical snapshots.
- API: `/api/v1/fx/current`, `/api/v1/fx/operational`.
- Tests: 5 dedicated; combined suite **80 passed**.
- Real DB not written.
- Evidence: `docs/accounting/PHASE-11_CURRENCY_FX_EVIDENCE.md`

**Phase 12 not started.**
