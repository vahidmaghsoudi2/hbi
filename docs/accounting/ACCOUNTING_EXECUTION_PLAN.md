# HBI Accounting — Execution Plan (Tracking)
**Contract:** HBI ACCOUNTING MASTER EXECUTION CONTRACT V1.0  
**Implementation Owner:** Grok2  
**Baseline SHA (Phase 00):** `8be7a97c3a27c51e05652671e4a33bbe9dc308d0`  
**Phase 04 baseline:** `f4defd53b05e8be1bdbca6345f0ddb7f2ffbfba8`  
**Phase 05 baseline:** `34f2e177832e952ae18b545524c894bfff572c94`  
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
| 02 | Data Model + Schema Migration | **CLOSED / PASS** | Grok2 |
| 03 | Accounting Home UI | **CLOSED / PASS** | Grok2 |
| 04 | Real Database Migration | **CLOSED / PASS** | Grok2 + PO local |
| 05 | Inventory Management | **CONDITIONAL PASS** | Grok2 |
| 06+ | Stock/Sales expansion | **STOPPED** | — |

## Phase 05 summary

- Reused existing Inventory + StockMovement models (no parallel Product).
- Service: increase/decrease with negative-stock rejection + StockMovement rows.
- API: list, available, by product, availability, adjust (auth).
- Tests: 9 inventory + 16 Phase 02 regression = 25 passed (`--noconftest` in agent).
- Real DB not written.
- Frontend `npm run build`: **NOT VERIFIED** in agent → gate remains conditional until PO confirms build green.
- Evidence: `docs/accounting/PHASE-05_INVENTORY_EVIDENCE.md`
