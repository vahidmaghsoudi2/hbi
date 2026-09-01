# HBI Accounting — Execution Plan (Tracking)
**Contract:** HBI ACCOUNTING MASTER EXECUTION CONTRACT V1.0  
**Implementation Owner:** Grok2  
**Baseline SHA (Phase 00 audit start):** `8be7a97c3a27c51e05652671e4a33bbe9dc308d0`  
**Phase 00 audit commit:** `dec367fca52019ea08d1145bac3de24aac8335f4`  
**Last Updated:** 2026-09-01

## Frozen decisions

| ID | Decision | Status | Recorded |
|----|----------|--------|----------|
| C-01 | Currency of Record = USD; FX Snapshot required; IRR/Toman display | **APPROVED by PO** | This plan + PHASE-01 architecture |
| C-02 | Category = data-driven entity; V1 set includes بوست/مو as independent | **APPROVED by PO** | This plan + PHASE-01 architecture |
| C-03 | Barcode remains on Product (identity) | Open design note from Phase 00 | Audit |

## Phase Status Board

| Phase | Name | Status | Owner | Commit SHA | QA |
|-------|------|--------|-------|------------|-----|
| 00 | Repository Audit | **COMPLETE** | Grok2 | `dec367fc` | Pending Qwen2 |
| 01 | Accounting Architecture | **COMPLETE — AWAITING GATE** | Grok2 | (see commit of this file) | Pending PO/Gate |
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

## Evidence index

- `docs/accounting/ACCOUNTING_REPOSITORY_AUDIT.md` (Phase 00)
- `docs/accounting/PHASE-01_ARCHITECTURE_PROPOSAL.md` (Phase 01)
- `docs/accounting/ACCOUNTING_EXECUTION_PLAN.md` (this file)

## Rule

No phase advances without Gate PASS on the previous phase.  
PHASE 02 must not start until PHASE 01 is formally gated by PO / Integration Governance.
