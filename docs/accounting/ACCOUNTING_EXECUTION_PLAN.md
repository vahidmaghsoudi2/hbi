# HBI Accounting — Execution Plan (Tracking)
**Contract:** HBI ACCOUNTING MASTER EXECUTION CONTRACT V1.0  
**Implementation Owner:** Grok2  
**Phase 05 baseline:** `34f2e177832e952ae18b545524c894bfff572c94`  
**Phase 06 baseline:** `8f7c437d15ee0304c44e2b5885a97cc0c823597c`  
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
| 05 | Inventory Management | **CLOSED / PASS** | Grok2 |
| 06 | Stock Movement Ledger | **CLOSED / PASS** | Grok2 |
| 07+ | Stock-In / Sales / Returns workflows | **STOPPED** | — |

## Phase 06 summary

- Read ledger on existing `StockMovement` (no new entity).
- Repository + service filters: product_id, movement_type (schema types only).
- API: `GET /api/v1/inventory/movements`, `GET /api/v1/inventory/movements/{id}`.
- Writes remain Phase 05 inventory mutation path only.
- Tests: 9 Phase 06 + 9 Phase 05 + 16 Phase 02 = **34 passed**.
- Real DB not written.
- Evidence: `docs/accounting/PHASE-06_STOCK_MOVEMENT_EVIDENCE.md`

**Phase 07 not started.**
