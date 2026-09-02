# HBI Accounting — Execution Plan (Tracking)
**Contract:** HBI ACCOUNTING MASTER EXECUTION CONTRACT V1.0  
**Implementation Owner:** Grok2  
**Baseline SHA (Phase 00):** `8be7a97c3a27c51e05652671e4a33bbe9dc308d0`  
**Phase 01 PASS:** `66f4338aa9fcf320cac5ac402522501d50c3a179`  
**Phase 02 PASS baseline:** `ec9c2ed83915859669889c6e1c67af6ff8357c01`  
**Phase 03 tip:** `b0489a8c3c7254f61fc614cb66b68e64687c7285`  
**Phase 04 baseline:** `f4defd53b05e8be1bdbca6345f0ddb7f2ffbfba8`  
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
| 02 | Data Model + Schema Migration (real SQLite FK) | **CLOSED / PASS** | Grok2 |
| 03 | Accounting Home UI | **CLOSED / PASS** | Grok2 |
| 04 | Real Database Migration | **CLOSED / PASS** | Grok2 + PO local |
| 05+ | … | **STOPPED** (not started) | — |

## Evidence

### Phase 02
- `scripts/accounting_phase02_migrate.py`
- `tests/test_schema_migration_clone.py` (11 passed)
- `tests/test_accounting_data_model.py` (5 passed)
- `docs/accounting/PHASE-02_MIGRATION_PLAN_EVIDENCE.md`

### Phase 03
- `frontend/src/pages/AccountingHomePage.tsx`
- Route: `/accounting`
- `docs/accounting/PHASE-03_ACCOUNTING_HOME_UI_EVIDENCE.md`

### Phase 04
- Local DB migrated: `E:\hbi\data\hbi.db` (not in Git)
- Backup: `E:\hbi_backups\hbi_pre_phase04_20260902_105538.db`
- Migrator: SUCCESS · toman YES · fk PASS · exit 0
- Post confirm: integrity ok · fk 0 · Product 19 · Category 6 · BOOST/HAIR/BEAUTY/TOOLS/PERFUME/OTHER
- Evidence: `docs/accounting/PHASE-04_REAL_DATABASE_MIGRATION_EVIDENCE.md`

**Phase 05 is not started.** Requires a separate execution mission.
