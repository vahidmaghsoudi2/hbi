# HBI Accounting — Execution Plan (Tracking)
**Contract:** HBI ACCOUNTING MASTER EXECUTION CONTRACT V1.0  
**Implementation Owner:** Grok2  
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
| 00–14 | … | **CLOSED / PASS** | Grok2 |
| 15 | Full Regression | **CLOSED / PASS** | Grok2 |
| 16+ | (next gated work) | **STOPPED** | — |

## Phase 15 summary

- Initial: CONDITIONAL (5 test failures).
- Remediation: **tests/fixtures only** (C-01 sale tests, rec API fixtures, pilot response contract).
- Accounting: **97 passed**.
- Full HBI: **211 passed, 0 failed, 2 skipped**.
- Production logic unchanged; real DB not written.
- Evidence: `docs/accounting/PHASE-15_REGRESSION_EVIDENCE.md`

**Phase 16 not started.**
