# PHASE 07 — Stock-In Workflow Evidence

**Status:** **CLOSED / PASS**  
**Owner:** Grok2  
**Baseline SHA:** `720043e16d53a516c77603d2f1acda83b5a89167` (mission also cited `8f7c437…` as earlier baseline)  
**Real `data/hbi.db` modified:** **NO**

## Reality audit

| Item | Finding |
|------|--------|
| Product | Existing master only |
| Inventory | Existing row required (no auto-create) |
| StockMovement | Type `STOCK_IN` already in CheckConstraint |
| C-01 fields | `purchase_price_usd`, `price_fx_rate_usd_to_irr`, IRR/Toman columns present |

## Architecture

`StockInService.stock_in`:

1. Validate product exists  
2. Validate inventory exists  
3. Validate quantity > 0, purchase_price_usd >= 0, fx_rate_usd_to_irr > 0 (**caller-supplied only**)  
4. Compute unit/line IRR & Toman via locked formula  
5. Increase `quantity_available`  
6. Update current purchase price + FX on Inventory  
7. Insert `STOCK_IN` StockMovement with FX snapshot on the movement row  
8. Flush; rollback on failure  

Historical FX on **prior movement rows** remains unchanged when a later stock-in uses a different R.

## API

```text
POST /api/v1/inventory/stock-in
Auth: required (get_current_customer_id)
Body: product_id, quantity, purchase_price_usd, fx_rate_usd_to_irr, note?, reference_type?, reference_id?
```

## Files changed

- `app/services/stock_in_service.py` (new)
- `app/api/routers/inventory.py` (POST /stock-in)
- `tests/test_stock_in_workflow.py` (new)
- `docs/accounting/PHASE-07_STOCK_IN_EVIDENCE.md`
- `docs/accounting/ACCOUNTING_EXECUTION_PLAN.md`

## DB/schema changes

**NONE** — reused existing columns/tables.

## Tests

```text
python -m pytest tests/test_stock_in_workflow.py --noconftest -q
→ 13 passed

python -m pytest tests/test_inventory_management.py --noconftest -q
→ 9 passed

python -m pytest tests/test_stock_movement_ledger.py --noconftest -q
→ 9 passed

python -m pytest tests/test_accounting_data_model.py tests/test_schema_migration_clone.py --noconftest -q
→ 16 passed

Combined: 47 passed
```

## Frontend build

N/A — zero frontend file changes.

## Known limitations

- Does not auto-create Inventory for products without a row
- Sale price not recalculated on stock-in (only purchase fields updated)
- No supplier/PO entity beyond optional reference_type/id strings
- Live HTTP server tests not run in agent

## Final verdict

**CLOSED / PASS**  
**Phase 08:** STOPPED
