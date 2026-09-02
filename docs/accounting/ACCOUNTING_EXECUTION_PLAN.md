# HBI Accounting — Execution Plan (Tracking)
**Contract:** HBI ACCOUNTING MASTER EXECUTION CONTRACT V1.0  
**Implementation Owner:** Grok2  
**Phase 07 baseline:** `720043e16d53a516c77603d2f1acda83b5a89167`  
**Phase 08 baseline:** `623b5f65950531657ec59246d712b08e282cab23`  
**Last Updated:** 2026-09-02

## Frozen decisions

| ID | Decision | Status |
|----|----------|--------|
| C-01 | USD + FX Snapshot; formula `(toman×10)/R` | **APPROVED** |
| C-02 | Category entity; بوست≠مو | **APPROVED** |

## Phase Status Board

| Phase | Name | Status | Owner |
|-------|------|--------|-------|
| 00–04 | … | **CLOSED / PASS** | Grok2 |
| 05 | Inventory Management | **CLOSED / PASS** | Grok2 |
| 06 | Stock Movement Ledger | **CLOSED / PASS** | Grok2 |
| 07 | Stock-In Workflow | **CLOSED / PASS** | Grok2 |
| 08 | Sales Workflow | **CLOSED / PASS** | Grok2 |
| 09+ | Payments / Returns / Reports | **STOPPED** | — |

## Phase 08 summary

- Atomic sale: Customer + ACTIVE Product + Inventory → Sale/SaleItem → qty decrease → `SALE` StockMovement.
- FX rate required; C-01 USD/IRR/Toman on sale, items, movements.
- API: `POST /api/v1/sales/` with `fx_rate_usd_to_irr`.
- Tests: 10 dedicated + prior regression → **57 passed** total in combined run.
- Real DB not written.
- Evidence: `docs/accounting/PHASE-08_SALES_EVIDENCE.md`

**Phase 09 not started.**
