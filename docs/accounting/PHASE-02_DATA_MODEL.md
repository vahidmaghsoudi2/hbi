# PHASE 02 — Accounting Data Model

**Status:** IMPLEMENTED (models + unit tests + additive SQL script) — **AWAITING GATE**  
**Owner:** Grok2  
**Architecture baseline:** PHASE 01 PASS (`66f4338`)  
**C-01 formula (locked):** `amount_usd = (amount_toman × 10) / R` with `R = IRR per 1 USD`

## Reality check (before change)

- Product Master: existing `Product` — **reused** (`category_id` nullable FK).
- Inventory / Sale / SaleItem: **extended** with USD + FX snapshot; **toman retained**.
- No Alembic; `create_all` + `scripts/accounting_phase02_schema.sql`.
- No parallel Product catalog.

## New tables

Category, StockMovement, Payment, SaleReturn, OperationalFxRate

## Extended columns

Product.category_id; Inventory/Sale/SaleItem USD + fx_rate_usd_to_irr + IRR snapshot fields.

## Tests

`tests/test_accounting_data_model.py` — 5 passed (`--noconftest` due to unrelated FastAPI deps in root conftest).

## Out of scope

UI, sale service rewrite, stock movement service, reports, money migration job execution.
