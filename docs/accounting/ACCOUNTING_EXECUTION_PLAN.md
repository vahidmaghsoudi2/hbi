# HBI Accounting — Execution Plan (Tracking)
**Contract:** HBI ACCOUNTING MASTER EXECUTION CONTRACT V1.0  
**Implementation Owner:** Grok2  
**Baseline SHA (Phase 00):** `8be7a97c3a27c51e05652671e4a33bbe9dc308d0`  
**Audit commit:** `dec367fca52019ea08d1145bac3de24aac8335f4`  
**Last Updated:** 2026-09-01

## Phase Status Board

| Phase | Name | Status | Owner | Commit SHA | QA |
|-------|------|--------|-------|------------|-----|
| 00 | Repository Audit | **COMPLETE (AUDIT)** | Grok2 | `dec367fc` (audit doc) / baseline `8be7a97` | Pending Qwen2 |
| 01 | Accounting Architecture | NOT STARTED | Grok2 | — | — |
| 02 | Data Model | NOT STARTED | Grok2 | — | — |
| 03 | Accounting Home UI | NOT STARTED | Grok2 | — | — |
| 04 | Migration | NOT STARTED | Grok2 | — | — |
| 05 | Inventory | NOT STARTED | Grok2 | — | — |
| 06 | Stock Movement | NOT STARTED | Grok2 | — | — |
| 07 | Stock In | NOT STARTED | Grok2 | — | — |
| 08 | Sales | NOT STARTED | Grok2 | — | — |
| 09 | Payment | NOT STARTED | Grok2 | — | — |
| 10 | Returns | NOT STARTED | Grok2 | — | — |
| 11 | Currency / FX Snapshot | NOT STARTED | Grok2 | — | — |
| 12 | Reports | NOT STARTED | Grok2 | — | — |
| 13 | HBI Home Integration | NOT STARTED | Grok2 | — | — |
| 14 | Tests | NOT STARTED | Grok2 | — | — |
| 15 | Regression | NOT STARTED | Grok2 | — | — |
| 16 | Final Audit | NOT STARTED | Grok2 | — | — |
| 17 | PO Acceptance | NOT STARTED | PO | — | — |

## Open Blockers (Phase 00)

1. **C-01 Currency** — Contract USD+FX vs Toman-only code
2. **C-02 Category** — Contract entity vs free-text seed
3. **C-03 Barcode** — Inventory vs Product.barcode_gtin

## Evidence

- `docs/accounting/ACCOUNTING_REPOSITORY_AUDIT.md`

## Rule

No phase advances without Gate PASS on the previous phase.
