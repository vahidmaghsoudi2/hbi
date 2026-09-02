# PHASE 05 — Inventory Management Evidence

**Status:** **CONDITIONAL PASS**  
**Owner:** Grok2  
**Baseline SHA:** `34f2e177832e952ae18b545524c894bfff572c94`  
**Implementation tip (pre-docs):** `be136ff32a08ed5bd1cb0523be807cc9a7c997d4`  
**Real `data/hbi.db` modified by Phase 05:** **NO**

## Reality audit

Existing (reused, not duplicated):

| Layer | Artifact |
|-------|----------|
| Model | `app/models/inventory.py` — Product FK, qty fields, toman + USD/FX columns |
| Model | `app/models/stock_movement.py` — ledger types STOCK_IN/SALE/ADJUSTMENT/… |
| Repository | `app/repositories/inventory_repository.py` |
| Service | `app/services/inventory_service.py` |
| API | `app/api/routers/inventory.py` |
| Facade | `InventoryFacade` in `app/interface/facades.py` |
| Availability in recommendations | `_get_availability` already consulted Inventory qty |

No parallel Product/Inventory entity created.

## Database

- Phase 04 migrated local DB remains authoritative on PO machine.
- Phase 05 tests use **in-memory SQLite only**.
- No write to `data/hbi.db` under this phase.

## Implementation summary

1. **Repository:** `find_available` uses `quantity_available > 0` and excludes `OUT_OF_STOCK` (fixes legacy mismatch with status `AVAILABLE` only).
2. **Service:** `list_all`, `is_available`, `sellable_quantity`, `increase_stock`, `decrease_stock` with:
   - positive delta validation
   - insufficient stock → `ValueError`, no movement row
   - atomic flush + rollback on error
   - paired `StockMovement` row
3. **API:**
   - `GET /api/v1/inventory/`
   - `GET /api/v1/inventory/available`
   - `GET /api/v1/inventory/product/{product_id}`
   - `GET /api/v1/inventory/availability/{product_id}`
   - `POST /api/v1/inventory/adjust` (auth required)
4. **Facade:** `list_all`; recommendation availability routes through `InventoryService.is_available`.
5. **Tests:** `tests/test_inventory_management.py` (9 tests).

## Files changed

- `app/repositories/inventory_repository.py`
- `app/services/inventory_service.py`
- `app/api/routers/inventory.py`
- `app/interface/facades.py`
- `tests/test_inventory_management.py`
- `docs/accounting/PHASE-05_INVENTORY_EVIDENCE.md`
- `docs/accounting/ACCOUNTING_EXECUTION_PLAN.md`

## Tests executed (agent environment)

```text
python -m pytest tests/test_inventory_management.py --noconftest -v     → 9 passed
python -m pytest tests/test_accounting_data_model.py --noconftest -v  → 5 passed
python -m pytest tests/test_schema_migration_clone.py --noconftest -v → 11 passed
Total relevant: 25 passed
```

## Not verified in agent environment

| Item | Status |
|------|--------|
| `npm ci` / `npm run build` | **NOT VERIFIED** |
| Live read of PO `E:\hbi\data\hbi.db` schema | **NOT VERIFIED** (no access) |
| Full `pytest` suite with root conftest/FastAPI deps | **NOT VERIFIED** |
| HTTP-level API test against running server | **NOT VERIFIED** |

## Frozen artifacts

| Artifact | Changed by Phase 05? |
|----------|----------------------|
| `app/models/product.py` | **NO** |
| `app/services/recommendation_service.py` | **NO** |
| `data/seed_products.json` | **NO** |
| scoring / evidence contracts | **NO** |
| Phase 03 Accounting Home UI files | **NO** |

## Known limitations

- Valuation methodology (FIFO/LIFO/WAVG) **not invented** — only existing toman/USD columns retained.
- Full Stock In / Sales / Returns UI flows remain Phase 06+.
- `confirm_sale` still returns bool; preferred path for audited adjust is `decrease_stock` / API adjust.
- Frontend Accounting Home still shows «در دسترس نیست» for unimplemented menus — no fake inventory UI numbers added.

## Acceptance matrix

| Criterion | Result |
|-----------|--------|
| Reality audit | **PASS** |
| Inventory contract reuse | **PASS** |
| Implementation | **PASS** |
| Persistence (tests) | **PASS** |
| Quantity validation | **PASS** |
| Negative-stock protection | **PASS** |
| Transaction safety (service rollback path) | **PASS** |
| StockMovement traceability | **PASS** |
| API surface | **PASS** (code + unit path) |
| Frontend build | **NOT VERIFIED** |
| Phase 02 regression | **PASS** (16) |
| Frozen artifacts | **PASS** |
| Real DB write safety | **PASS** (no write) |
| Documentation | **PASS** |

## Final verdict

**CONDITIONAL PASS** — backend inventory gate complete; frontend build pending PO local verification.

**Phase 06:** STOPPED
