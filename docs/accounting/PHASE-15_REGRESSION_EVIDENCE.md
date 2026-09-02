# PHASE 15 — Full Regression Evidence

**Status:** **CONDITIONAL PASS**  
**Owner:** Grok2  
**Baseline SHA:** `144862c8a68df96eec966f7e05f091055fd3658e`  
**Real `data/hbi.db` modified:** **NO**

## Git state

- HEAD matched baseline at start.
- No production code changes in Phase 15 (evidence/docs only).

## Accounting regression

```text
python -m pytest tests/test_accounting_comprehensive.py ... test_schema_migration_clone.py --noconftest -q
→ 97 passed in 2.09s
```

## Full HBI regression (with conftest)

```text
python -m pytest -q
→ 206 passed, 5 failed, 2 skipped, 1 warning in 2.61s
```

### Failures (exact)

1. `tests/test_interface.py::test_sale_facade_create_sale`  
   TypeError: `SaleFacade.create_sale()` missing `fx_rate_usd_to_irr`  
   **Class B — test defect** (tests not updated for C-01 explicit FX contract).

2. `tests/test_interface.py::test_sale_facade_insufficient_stock`  
   Same TypeError.  
   **Class B — test defect**.

3. `tests/test_pilot_e2e_recommendation.py::test_pilot_token_and_generate_persist`  
   Token not received / assert count.  
   **Class C/E — fixture/env** (pilot_token denied for fixture customer in some paths).

4. `tests/test_recommendations_api.py::test_draft_products_excluded`  
   Token not received.  
   **Class C/E — fixture/auth setup**.

5. `tests/test_recommendations_api.py::test_inventory_zero_excluded`  
   Token not received.  
   **Class C/E — fixture/auth setup**.

No Accounting suite failures. No silent production fixes applied.

## Cross-system validation

- Models import: Product, Inventory, Customer, Case, Recommendation, Evidence — OK after deps installed.
- `app.main` loads; routers included under `/api/v1/{auth,products,customers,cases,recommendations,inventory,sales,payments,returns,fx,reports,evidence}`.
- Home `/` + `/accounting` static integration tests remain in Accounting suite (pass).

## Frozen artifacts

Phase 15 made **no** changes to Product A–D records, scoring, recommendation contracts, or seed identity files.

## Database

`data/hbi.db` not present in agent clone; not modified.

## Frontend

npm build not re-run (known Phase 13 environment timeout). Static route tests green.

## Why not full PASS

Full repository pytest is not 100% green (5 failures). Failures classified as test debt / fixture issues, not new Accounting implementation defects. Gate honesty → **CONDITIONAL PASS**.

## Verdict

**CONDITIONAL PASS** — Accounting green; 5 non-Accounting test failures documented, not fixed in Phase 15.  
Phase 16+ STOPPED.
