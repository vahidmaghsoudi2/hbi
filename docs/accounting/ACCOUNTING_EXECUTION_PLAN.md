# HBI Accounting — Execution Plan (Tracking)
**Contract:** HBI ACCOUNTING MASTER EXECUTION CONTRACT V1.0  
**Implementation Owner:** Grok2  
**Baseline SHA (Phase 00):** `8be7a97c3a27c51e05652671e4a33bbe9dc308d0`  
**Phase 01 PASS:** `66f4338aa9fcf320cac5ac402522501d50c3a179`  
**Last Updated:** 2026-09-02

## Frozen decisions

| ID | Decision | Status |
|----|----------|--------|
| C-01 | USD + FX Snapshot; formula `(toman×10)/R` | **APPROVED** |
| C-02 | Category entity; بوست≠مو | **APPROVED** |

## Phase Status Board

| Phase | Name | Status | Owner |
|-------|------|--------|-------|
| 00 | Repository Audit | COMPLETE | Grok2 |
| 01 | Accounting Architecture | **CLOSED / PASS** | Grok2 |
| 02 | Data Model + Schema Migration (real SQLite FK) | **CLOSED / PASS** (prior gate) | Grok2 |
| 03 | Accounting Home UI | **IMPLEMENTED + DOCUMENTED — AWAITING GATE** | Grok2 |
| 04+ | … | **STOPPED** | — |

## Evidence

### Phase 02
- `docs/accounting/PHASE-02_DATA_MODEL.md`
- `scripts/accounting_phase02_migrate.py`
- `tests/test_schema_migration_clone.py`
- `docs/accounting/PHASE-02_MIGRATION_PLAN_EVIDENCE.md`

### Phase 03
- `frontend/src/pages/AccountingHomePage.tsx`
- `frontend/src/styles/accounting.css`
- Route: `/accounting`
- Home entry: «حسابداری» on `NewHomePage`
- `docs/accounting/PHASE-03_ACCOUNTING_HOME_UI_EVIDENCE.md`

Real `data/hbi.db` was **not** touched. Phase 04+ remains STOPPED.
