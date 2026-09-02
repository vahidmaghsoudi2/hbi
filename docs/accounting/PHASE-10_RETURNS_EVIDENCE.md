# PHASE 10 — Returns Workflow Evidence

**Status:** **CLOSED / PASS**  
**Owner:** Grok2  
**Baseline SHA:** `4e59380c4395d41ea71073571e7794b2a7bcda37`  
**Real `data/hbi.db` modified:** **NO**

## Reality audit

Existing `SaleReturn` model reused. Product must come from original `SaleItem`.  
Movement type: `RETURN_IN` (schema).  
Payment refund: **not implemented** (no existing refund architecture).

## Architecture

`ReturnService.create_return`:
1. Sale exists  
2. SaleItem for product on that sale exists  
3. quantity > 0 and ≤ (sold − already returned)  
4. Inventory exists; quantity increases  
5. SaleReturn row + RETURN_IN StockMovement (reference_type=SALE_RETURN)  
6. Sale monetary totals unchanged  
7. Atomic rollback on failure  

FX: from sale/item snapshot or optional caller-supplied rate (never invented).

## API

```text
POST /api/v1/returns/
GET  /api/v1/returns/sale/{sale_id}
Auth: required
```

## Files

- `app/services/return_service.py`
- `app/api/routers/returns.py`
- `app/api/routers/__init__.py`
- `app/main.py`
- `tests/test_returns_workflow.py`
- `docs/accounting/PHASE-10_RETURNS_EVIDENCE.md`
- `docs/accounting/ACCOUNTING_EXECUTION_PLAN.md`

## Schema changes

**NONE**

## Tests

```text
python -m pytest tests/test_returns_workflow.py --noconftest -q
→ 7 passed

Full accounting regression (incl. returns):
→ 75 passed
```

## Frontend

Zero FE changes.

## Known limitations

- No payment refund / money reversal
- No multi-item bulk return in one call (per product_id)
- Live HTTP suite not run in agent

## Verdict

**CLOSED / PASS** — Phase 11+ STOPPED
