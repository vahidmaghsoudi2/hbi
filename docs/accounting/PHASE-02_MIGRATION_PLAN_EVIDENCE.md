# PHASE 02 — Migration Plan Evidence (Corrective)

**Status:** IMPLEMENTED + TESTED (clone) + REAL SQLITE FK — **AWAITING GATE**  
**Owner:** Grok2  
**Baseline SHA (pre-corrective):** `73f250f6d7e8008fd9410bc98d0cd0a14885f55f`  
**Real data/hbi.db touched:** **NO**

## Root cause

1. `ALTER TABLE ... ADD COLUMN category_id` does **not** create a SQLite FOREIGN KEY constraint.  
   `PRAGMA foreign_key_list(Product)` was empty → no real `Product.category_id → Category.category_id`.
2. SQLite raises `foreign key mismatch - "SaleReturn" referencing "Product"` when the parent key is not a true PRIMARY KEY / UNIQUE.
3. `PRAGMA foreign_keys=OFF` is a **no-op inside an open transaction**; Product rebuild must `COMMIT` before toggling the pragma.

## Corrected implementation

- `scripts/accounting_phase02_migrate.py`  
  - Creates Category / Payment / SaleReturn / StockMovement / OperationalFxRate with **inline FOREIGN KEY** definitions.  
  - **Rebuilds Product** (copy → drop → rename) so `category_id` carries a real FK to `Category.category_id`, preserving all rows/IDs.  
  - Adds money columns via ALTER where FK is not required.  
  - Seeds six categories (BOOST/HAIR independent).  
  - Idempotent; refuses `data/hbi.db` without `HBI_ALLOW_REAL_DB=1`.  
  - No historical FX conversion; Toman untouched.

## Tests

```bash
python -m pytest tests/test_schema_migration_clone.py -v
```

**Result:** **11 passed**, 0 failed, 0 errors.

Assertions include `PRAGMA foreign_key_list(...)` for Product→Category, SaleReturn→Product/Sale, and all other Accounting FKs; invalid insert rejection; idempotence; Toman/IDs preserved.

## FK verification (post-migration clone)

| Relationship | Result |
|--------------|--------|
| Product → Category | PRESENT (foreign_key_list) |
| SaleReturn → Product | PRESENT |
| SaleReturn → Sale | PRESENT |
| Payment → Sale | PRESENT |
| StockMovement → Product | PRESENT |
| Inventory → Product | PRESENT |
| SaleItem → Product/Sale | PRESENT |
| Sale → Customer | PRESENT |
| foreign_key_check | PASS (0 violations) |
| invalid FK rejection | PASS (IntegrityError) |
| valid FK insertion | PASS |

## Clone migration / Backup-restore / Startup

- Clone migration: PASS  
- Backup/restore drill (disposable): PASS  
- Clone DB access with FK ON: PASS  
- Full FastAPI app.main startup: **NOT VERIFIED** (isolated workdir)  
- Real DB protection: YES  
- Frozen artifacts: unchanged  

## Final recommendation

**CONDITIONAL PASS** — real SQLite FKs proven; full-app process startup on migrated clone remains open.

PHASE 03 remains **STOPPED**.
