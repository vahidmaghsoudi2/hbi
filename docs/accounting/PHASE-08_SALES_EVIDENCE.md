# PHASE 08 — Sales Workflow Evidence

**Status:** **CLOSED / PASS**  
**Owner:** Grok2  
**Baseline SHA:** `623b5f65950531657ec59246d712b08e282cab23`  
**Real `data/hbi.db` modified:** **NO**

## Reality audit

Reused existing `Sale`, `SaleItem`, `Customer`, `Product`, `Inventory`, `StockMovement`.  
Prior `SaleService.create_sale` used reserve/confirm and toman-only; replaced with USD+FX atomic workflow.

## Architecture

1. Validate customer exists  
2. Each line: product exists + `status=ACTIVE`, inventory exists, qty > 0, sellable >= qty  
3. `unit_price_usd` from item or `inventory.sale_price_usd`  
4. `fx_rate_usd_to_irr` required (never invented)  
5. Create Sale + SaleItem rows  
6. Decrease inventory; insert `SALE` StockMovement (`reference_type=SALE`, `reference_id=sale_id`)  
7. C-01 totals on Sale and movement  
8. Rollback entire unit on any failure  

Discount: **not in schema** → not implemented.

## API

```text
POST /api/v1/sales/
Auth: JWT customer must match body.customer_id
Body: customer_id, items[{product_id, quantity, unit_price_usd?}], fx_rate_usd_to_irr
```

## Files

- `app/services/sale_service.py` (rewritten workflow)
- `app/api/routers/sales.py`
- `app/interface/facades.py`
- `tests/test_sales_workflow.py`
- `docs/accounting/PHASE-08_SALES_EVIDENCE.md`
- `docs/accounting/ACCOUNTING_EXECUTION_PLAN.md`

## Schema changes

**NONE**

## Tests

```text
python -m pytest tests/test_sales_workflow.py --noconftest -q
→ 10 passed

Regression:
tests/test_inventory_management.py → 9
tests/test_stock_movement_ledger.py → 9
tests/test_stock_in_workflow.py → 13
tests/test_accounting_data_model.py + test_schema_migration_clone.py → 16
Combined relevant: 57 passed
```

## Frontend

Zero FE changes.

## Known limitations

- No payment capture (Phase 09+)
- No discount fields in schema
- Guest sale requires existing Customer row (guest registration is separate)
- Live HTTP suite not run in agent

## Verdict

**CLOSED / PASS** — Phase 09+ STOPPED
