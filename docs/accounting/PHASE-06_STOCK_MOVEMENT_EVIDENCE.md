# PHASE 06 — Stock Movement Ledger Evidence

**Status:** **CLOSED / PASS**  
**Owner:** Grok2  
**Baseline SHA:** `8f7c437d15ee0304c44e2b5885a97cc0c823597c`  
**Real `data/hbi.db` modified:** **NO**

## Reality audit

| Artifact | Finding |
|----------|--------|
| `StockMovement` model | Existing; types STOCK_IN/PURCHASE/SALE/RETURN_IN/RETURN_OUT/ADJUSTMENT |
| Write path | Phase 05 `InventoryService.increase_stock` / `decrease_stock` already record movements |
| Prior repo | No `StockMovementRepository` — **added** (read/filter only) |
| Product Master | Reused; no parallel entity |

## Architecture

- **Repository:** `app/repositories/stock_movement_repository.py` — list + filter by product / type / optional created_at range; order newest first.
- **Service:** `app/services/stock_movement_service.py` — validates movement_type against existing enum set.
- **API:** under existing inventory router (no new workflow).
- **Writes:** still only via existing inventory mutation path (no Stock-In/Sales/Returns UI).

## API

```text
GET /api/v1/inventory/movements
    ?product_id=&movement_type=&limit=&offset=
GET /api/v1/inventory/movements/{movement_id}
```

## Files changed

- `app/repositories/stock_movement_repository.py` (new)
- `app/services/stock_movement_service.py` (new)
- `app/api/routers/inventory.py` (ledger endpoints)
- `tests/test_stock_movement_ledger.py` (new)
- `docs/accounting/PHASE-06_STOCK_MOVEMENT_EVIDENCE.md`
- `docs/accounting/ACCOUNTING_EXECUTION_PLAN.md`

## Tests

```text
python -m pytest tests/test_stock_movement_ledger.py --noconftest -q
→ 9 passed

python -m pytest tests/test_inventory_management.py --noconftest -q
→ 9 passed

python -m pytest tests/test_accounting_data_model.py tests/test_schema_migration_clone.py --noconftest -q
→ 16 passed

Combined relevant: 34 passed
```

Coverage includes: empty ledger, creation via existing mutation path, product filter, type filter, invalid type rejection, get-by-id, trace fields, negative stock still blocked, toman preserved.

## Frontend build

Phase 06 **zero frontend file changes**. Agent did not re-run npm (prior registry instability). Non-blocking for ledger backend gate.

## Real DB

**NO** modification. Tests in-memory only.

## Known limitations

- No Stock-In / Sales / Returns operational workflows (Phase 07+)
- No report aggregation UI
- Date filter supported in service when callers pass datetime; HTTP API currently exposes product_id + movement_type only
- Live HTTP server tests not run in agent

## Acceptance

| Criterion | Result |
|-----------|--------|
| Reality audit | PASS |
| Ledger list/filter/detail | PASS |
| Existing types only | PASS |
| Traceability fields | PASS |
| Mutation path + no negative stock | PASS |
| Phase 05 regression | PASS |
| Phase 02 regression | PASS |
| Real DB safety | PASS |
| Docs | PASS |

## Final verdict

**CLOSED / PASS**

**Phase 07:** STOPPED
