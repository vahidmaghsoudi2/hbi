# PHASE 04 — Real Database Migration Evidence

**Status:** **CONDITIONAL PASS**  
**Owner:** Grok2 (gate) + Product Owner (local execution)  
**Baseline SHA:** `f4defd53b05e8be1bdbca6345f0ddb7f2ffbfba8`  
**Docs commit:** (this file)  
**Real `data/hbi.db` modified:** **YES** (on PO machine only; not in Git)

## Scope

Apply approved Phase 02 migration script to local production SQLite:

`E:\hbi\data\hbi.db`

No change to recommendation logic, Product A–D seed files, scoring, or evidence contracts.

## Pre-migration audit (PO machine — 2026-09-02)

| Item | Value |
|------|--------|
| HEAD | `f4defd53b05e8be1bdbca6345f0ddb7f2ffbfba8` |
| Path | `E:\hbi\data\hbi.db` |
| Size | 118784 bytes |
| MTime | 2026-09-01T23:51:45+04:30 |
| integrity_check | **ok** |
| foreign_key_check | 0 rows |
| Tables | Case, Customer, Evidence, Inventory, Product, ProductKnowledge, Recommendation, Sale, SaleItem |

### Pre row counts

| Table | Count |
|-------|------:|
| Case | 7 |
| Customer | 15 |
| Evidence | 30 |
| Inventory | 17 |
| Product | 19 |
| ProductKnowledge | 8 |
| Recommendation | 0 |
| Sale | 0 |
| SaleItem | 0 |

## Backup

| Item | Value |
|------|--------|
| Path | `E:\hbi_backups\hbi_pre_phase04_20260902_105538.db` (final run) |
| Earlier pre-gate backup | `E:\hbi_backups\hbi_pre_phase04_20260902_103342.db` |
| Size match (103342 run) | **PASS** (118784 = 118784) |
| Backup integrity (103342 run) | **ok** |

## Phase 02 regression (before migrate)

```text
python -m pytest tests/test_accounting_data_model.py -v   → 5 passed
python -m pytest tests/test_schema_migration_clone.py -v → 11 passed
```

**PASS** (16/16)

## Migration execution

```text
$env:HBI_ALLOW_REAL_DB = "1"
python scripts/accounting_phase02_migrate.py --db data\hbi.db
```

| Field | Result |
|-------|--------|
| MIGRATE_EXIT | **0** |
| status | **SUCCESS** |
| toman_preserved | **YES** |
| fk_check | **PASS** |
| product_category_fk_present | **True** |
| product_rebuild | **ALREADY_HAS_FK** |

Interpretation of `ALREADY_HAS_FK`: on this run the migrator reported Product already carried a real Category FK (no second table rebuild required). Tables/columns still ensured; categories seeded via script contract.

## Post-migration (from PO PHASE04_SUMMARY paste)

| Check | Result |
|-------|--------|
| Script SUCCESS | **PASS** |
| Toman preservation flag | **PASS** |
| FK check flag | **PASS** |
| Product→Category FK present | **PASS** |
| integrity_check (post, explicit line) | **NOT VERIFIED** (not in short summary paste) |
| Post row counts vs pre | **NOT VERIFIED** (not in short summary paste) |
| Category list EXACTLY 6 / BOOST≠HAIR | **NOT VERIFIED** (not in short summary paste) |
| Idempotent second run | **NOT VERIFIED** (not in short summary paste) |
| Restore drill on backup copy | **NOT VERIFIED** (not in short summary paste) |
| Full app startup against migrated DB | **NOT VERIFIED** |

## Frozen artifacts

| Artifact | Phase 04 change |
|----------|-----------------|
| `app/models/product.py` | not modified by this gate |
| recommendation / scoring / evidence contracts | not modified |
| `data/seed_products.json` | not modified |
| `data/hbi.db` | **not committed to Git** |

## Git safety

- Production database remains **local-only**.
- This evidence document is docs-only.
- No commit of `data/hbi.db` or `E:\hbi_backups\*`.

## Remaining limitations

1. Short PO summary omitted post integrity, counts, category dump, idempotence exit, restore drill.
2. Agent environment cannot open `E:\hbi\data\hbi.db`; gate relies on PO paste + pre-gate capture.
3. Optional one-liner confirmation recommended before elevating to unconditional CLOSED/PASS.

## Optional 30-second confirm (PO copy-paste)

```powershell
python -c "import sqlite3;c=sqlite3.connect(r'E:\hbi\data\hbi.db');c.execute('PRAGMA foreign_keys=ON');print(c.execute('PRAGMA integrity_check').fetchone());print(len(c.execute('PRAGMA foreign_key_check').fetchall()));print(c.execute('SELECT COUNT(*) FROM Product').fetchone()[0], c.execute('SELECT COUNT(*) FROM Category').fetchone()[0]);print(c.execute('SELECT category_id FROM Category ORDER BY sort_order').fetchall());c.close()"
```

Expected shape: `('ok',)` · `0` · `19 6` · six ids including BOOST and HAIR separate.

## Final gate decision

**CONDITIONAL PASS**

Critical migrator outcomes reported SUCCESS with Toman preserved and FK PASS.  
Elevate to **CLOSED / PASS** after optional confirm line above (or equivalent).

**Phase 05:** STOPPED until Phase 04 elevated or PO accepts conditional close.
