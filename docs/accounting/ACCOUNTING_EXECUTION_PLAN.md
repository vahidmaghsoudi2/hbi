# HBI Accounting — Execution Plan (Tracking)
**Contract:** HBI ACCOUNTING MASTER EXECUTION CONTRACT V1.0  
**Implementation Owner:** Grok2  
**Phase 14 baseline:** `07082e14a8cae150abc72382271684d8ca42f2ab`  
**Phase 15 baseline:** `144862c8a68df96eec966f7e05f091055fd3658e`  
**Last Updated:** 2026-09-02

## Frozen decisions

| ID | Decision | Status |
|----|----------|--------|
| C-01 | USD + FX Snapshot; formula `(toman×10)/R` | **APPROVED** |
| C-02 | Category entity; بوست≠مو | **APPROVED** |

## Phase Status Board

| Phase | Name | Status | Owner |
|-------|------|--------|-------|
| 00–13 | … | **CLOSED / PASS** | Grok2 |
| 14 | Comprehensive Tests | **CLOSED / PASS** | Grok2 |
| 15 | Full Regression | **CONDITIONAL PASS** | Grok2 |
| 16+ | (next gated work) | **STOPPED** | — |

## Phase 15 summary

- Accounting regression: **97 passed**.
- Full HBI pytest: **206 passed, 5 failed, 2 skipped**.
- Failures: interface FX kwarg test debt (2); pilot/recommendation token fixtures (3).
- No production code changes; real DB not written.
- Evidence: `docs/accounting/PHASE-15_REGRESSION_EVIDENCE.md`

**Phase 16 not started.**
