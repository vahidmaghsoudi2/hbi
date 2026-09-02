# HBI Accounting — Execution Plan (Tracking)
**Contract:** HBI ACCOUNTING MASTER EXECUTION CONTRACT V1.0  
**Implementation Owner:** Grok2  
**Phase 09 baseline:** `74c6295f3acc25d2463bc911b35868ed93a00d1a`  
**Phase 10 baseline:** `4e59380c4395d41ea71073571e7794b2a7bcda37`  
**Last Updated:** 2026-09-02

## Frozen decisions

| ID | Decision | Status |
|----|----------|--------|
| C-01 | USD + FX Snapshot; formula `(toman×10)/R` | **APPROVED** |
| C-02 | Category entity; بوست≠مو | **APPROVED** |

## Phase Status Board

| Phase | Name | Status | Owner |
|-------|------|--------|-------|
| 00–08 | … | **CLOSED / PASS** | Grok2 |
| 09 | Payment Workflow | **CLOSED / PASS** | Grok2 |
| 10 | Returns Workflow | **CLOSED / PASS** | Grok2 |
| 11+ | Reports / … | **STOPPED** | — |

## Phase 10 summary

- Existing `SaleReturn`; product from original SaleItem only.
- Inventory increase + `RETURN_IN` StockMovement; Sale totals immutable.
- API: `/api/v1/returns/`.
- No refund payment workflow (documented limitation).
- Tests: 7 dedicated; combined suite **75 passed**.
- Real DB not written.
- Evidence: `docs/accounting/PHASE-10_RETURNS_EVIDENCE.md`

**Phase 11 not started.**
