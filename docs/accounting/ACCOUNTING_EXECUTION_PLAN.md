# HBI Accounting — Execution Plan (Tracking)
**Contract:** HBI ACCOUNTING MASTER EXECUTION CONTRACT V1.0  
**Implementation Owner:** Grok2  
**Phase 08 baseline:** `623b5f65950531657ec59246d712b08e282cab23`  
**Phase 09 baseline:** `74c6295f3acc25d2463bc911b35868ed93a00d1a`  
**Last Updated:** 2026-09-02

## Frozen decisions

| ID | Decision | Status |
|----|----------|--------|
| C-01 | USD + FX Snapshot; formula `(toman×10)/R` | **APPROVED** |
| C-02 | Category entity; بوست≠مو | **APPROVED** |

## Phase Status Board

| Phase | Name | Status | Owner |
|-------|------|--------|-------|
| 00–07 | … | **CLOSED / PASS** | Grok2 |
| 08 | Sales Workflow | **CLOSED / PASS** | Grok2 |
| 09 | Payment Workflow | **CLOSED / PASS** | Grok2 |
| 10+ | Returns / Reports / … | **STOPPED** | — |

## Phase 09 summary

- Existing `Payment` entity; methods CASH/CARD/TRANSFER/OTHER only.
- `PaymentService` + API under `/api/v1/payments`.
- Sale totals not mutated; FX on payment is snapshot.
- Tests: 11 dedicated; combined accounting suite **68 passed**.
- Real DB not written.
- Evidence: `docs/accounting/PHASE-09_PAYMENT_EVIDENCE.md`

**Phase 10 not started.**
