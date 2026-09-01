# PHASE 02 — Migration Plan Evidence

**Status:** IMPLEMENTED + TESTED (clone) — **AWAITING GATE**  
**Owner:** Grok2  
**Contract:** HBI ACCOUNTING MASTER EXECUTION CONTRACT V1.0  
**C-01 (locked):** `amount_usd = (amount_toman × 10) / R` with `R = IRR per 1 USD`  
**Real data/hbi.db touched:** **NO**

## Repository baseline

| Item | Value |
|------|--------|
| Baseline SHA (pre-this-package) | `c5b3649a0ad3e8b5ffd84f9dcdc92a72d63d6878` |
| Implementation package | migration script + clone test suite + this evidence |
| Final SHA | see latest commit on master after this package |

## Files added / modified in this package

| Path | Role |
|------|------|
| `scripts/accounting_phase02_migrate.py` | Additive, idempotent schema migration (ALTER + CREATE IF NOT EXISTS + Category seed) |
| `tests/test_schema_migration_clone.py` | Disposable-clone proof suite (11 tests) |
| `docs/accounting/PHASE-02_MIGRATION_PLAN_EVIDENCE.md` | This evidence file |
| `docs/accounting/ACCOUNTING_EXECUTION_PLAN.md` | Status board update only |

Reused (not duplicated):

- `scripts/accounting_phase02_schema.sql` (reference additive DDL)
- `tests/test_accounting_data_model.py` (model/unit formula tests)
- ORM models under `app/models/*` (already carry target columns)

## Database / clone strategy

- Migration is **never** run against production `data/hbi.db` by default.
- Script refuses paths ending in `data/hbi.db` unless `HBI_ALLOW_REAL_DB=1`.
- Tests construct a **disposable legacy SQLite file** (temp path) with only pre-PHASE-02 columns and sample Toman rows, then run `migrate()`.
- No historical FX backfill; new USD/IRR columns remain NULL after migration.

## Pre-migration schema (legacy clone used in tests)

Tables: Customer, Product, Inventory, Sale, SaleItem  

Notable missing columns (pre):

- Product: no `category_id`
- Inventory: no `purchase_price_usd`, `sale_price_usd`, `price_fx_rate_usd_to_irr`, `purchase_price_irr`, `sale_price_irr`, `price_updated_at`
- Sale: no `total_amount_usd`, `fx_rate_usd_to_irr`, `total_amount_irr`
- SaleItem: no `unit_price_usd`, `fx_rate_usd_to_irr`, `unit_price_irr`
- No Category / StockMovement / Payment / SaleReturn / OperationalFxRate tables

Pre row counts (test clone):

```
Customer: 1
Product: 1
Inventory: 1
Sale: 1
SaleItem: 1
```

Pre Toman samples:

```
Inventory: [I1, 1500000, 2000000]
Sale: [S1, 2000000]
SaleItem: [SI1, 2000000]
```

## Migration execution (actual)

Command (test harness equivalent):

```bash
python -m pytest tests/test_schema_migration_clone.py -v
# or direct:
python scripts/accounting_phase02_migrate.py --db /tmp/disposable_clone.db
```

Observed on first run against legacy clone:

- **columns_added:**  
  `Product.category_id`,  
  `Inventory.purchase_price_usd`, `Inventory.sale_price_usd`, `Inventory.price_fx_rate_usd_to_irr`,  
  `Inventory.purchase_price_irr`, `Inventory.sale_price_irr`, `Inventory.price_updated_at`,  
  `Sale.total_amount_usd`, `Sale.fx_rate_usd_to_irr`, `Sale.total_amount_irr`,  
  `SaleItem.unit_price_usd`, `SaleItem.fx_rate_usd_to_irr`, `SaleItem.unit_price_irr`
- **tables_created:** Category, StockMovement, Payment, SaleReturn, OperationalFxRate
- **status:** SUCCESS
- **idempotent_re_run:** OK

## Post-migration schema

- All required accounting columns present on Product / Inventory / Sale / SaleItem.
- New tables present.
- Category rows (exact 6):

| category_id | name_fa | name_en | sort_order |
|-------------|---------|---------|------------|
| BOOST | بوست | Boost | 1 |
| HAIR | مو | Hair | 2 |
| BEAUTY | زیبایی | Beauty | 3 |
| TOOLS | ابزار | Tools | 4 |
| PERFUME | ادکلن | Perfume | 5 |
| OTHER | سایر | Other | 99 |

BOOST and HAIR remain independent codes.

Post row counts (existing tables unchanged; Category = 6):

```
Customer: 1
Product: 1
Inventory: 1
Sale: 1
SaleItem: 1
Category: 6
StockMovement: 0
Payment: 0
SaleReturn: 0
OperationalFxRate: 0
```

Post Toman samples: **identical** to pre (1500000 / 2000000).

USD/IRR snapshot columns on legacy rows: **NULL** (no historical conversion).

## FK check

`PRAGMA foreign_key_check` → **0 violations** (PASS).

## Tests

Command:

```bash
python -m pytest tests/test_schema_migration_clone.py -v
```

**Result (executed in isolated workdir, 2026-09-02):**

```
11 passed
```

Coverage mapped to requirements:

1. pre-migration schema capture — PASS  
2. pre-migration row counts — PASS  
3. pre-migration legacy Toman samples — PASS  
4. migration execution — PASS  
5. post-migration schema — PASS  
6. required columns exist — PASS  
7. required accounting tables exist — PASS  
8. Category contains exactly six official categories — PASS  
9. Product.category_id nullable — PASS  
10. Product → Category integrity (nullable + assignable) — PASS  
11. existing row counts unchanged — PASS  
12. existing Toman values unchanged — PASS  
13. no historical FX conversion — PASS  
14. migration idempotent — PASS  
15. PRAGMA foreign_key_check zero violations — PASS  
16. migration does not touch frozen artifacts (source scan + safety refuse) — PASS  

Also: real `data/hbi.db` path refused (exit 2) without override — PASS.

Regression note: `tests/test_accounting_data_model.py` remains the model/unit suite (prior PHASE 02 data-model evidence). Not re-executed in this isolated workdir (requires full app deps); treated as **NOT RE-VERIFIED in this package** but not modified.

## Startup / compatibility

Full application startup against a migrated clone: **NOT VERIFIED** in this package (no full FastAPI stack run here). ORM models already declare the target columns; `create_all` path continues to work for green-field DBs.

## Rollback / restore

- Additive only (ADD COLUMN + CREATE IF NOT EXISTS + INSERT OR IGNORE).
- No DROP / no value rewrite → restore = restore pre-migration DB file from backup.
- Explicit rollback SQL for column drop not supplied (SQLite limitation); restore-from-backup is the documented path.
- Rollback execution: **NOT VERIFIED** (no production file involved).

## Frozen-artifact verification

Migration module does not import or modify:

- Product A–D identity / seed records  
- scoring / evidence contracts  
- recommendation logic  
- UI  

Source scan in test asserts absence of forbidden identifiers (except the safety refusal string for `data/hbi.db`).

## Known limitations

1. SQLite cannot attach a formal FOREIGN KEY constraint to an existing `Product.category_id` column after ADD COLUMN; integrity is enforced when the column is populated and by `PRAGMA foreign_keys=ON` + application/ORM usage. Documented in migration evidence payload.
2. Payment / SaleReturn / StockMovement column adds apply only if those tables already exist; otherwise CREATE TABLE supplies full definition.
3. Full-app E2E against a migrated clone and production backup/restore drill remain **NOT VERIFIED**.
4. No Alembic; project uses explicit script + optional SQL file.

## Final implementation status

| Gate item | Result |
|-----------|--------|
| Migration artifact present & executable | YES |
| Clone migration | PASS |
| Row counts preserved | YES |
| Toman preserved | YES |
| No historical FX conversion | YES |
| Category seed (6, BOOST≠HAIR) | PASS |
| FK check | PASS |
| Real DB untouched | YES |
| Tests (clone suite) | 11 passed |
| PHASE 03 | STOPPED (no work) |

**Gate recommendation:** **CONDITIONAL PASS** — clone evidence complete; full-app startup and production backup drill still open for reviewer.

PHASE 03 remains **STOPPED** until ChatGPT Gate review.
