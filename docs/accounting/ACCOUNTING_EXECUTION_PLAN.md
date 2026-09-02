# HBI Accounting — Execution Plan (Tracking)
**Contract:** HBI ACCOUNTING MASTER EXECUTION CONTRACT V1.0  
**Implementation Owner:** Grok2  
**Phase 06 baseline:** `8f7c437d15ee0304c44e2b5885a97cc0c823597c`  
**Phase 07 baseline:** `720043e16d53a516c77603d2f1acda83b5a89167`  
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
| 07 | Stock-In Workflow | **CLOSED / PASS** | Grok2 |
| 08+ | Sales / Payments / Returns | **STOPPED** | — |

## Phase 07 summary

- `StockInService`: product + inventory required; qty > 0; USD price; **caller-supplied** FX rate R.
- C-01: `amount_irr = usd * R`, `amount_toman = irr / 10`.
- Inventory qty + purchase price fields updated; `STOCK_IN` movement with FX snapshot.
- API: `POST /api/v1/inventory/stock-in` (auth).
- Tests: 13 Phase 07 + 9 + 9 + 16 = **47 passed**.
- Real DB not written.
- Evidence: `docs/accounting/PHASE-07_STOCK_IN_EVIDENCE.md`

**Phase 08 not started.**
