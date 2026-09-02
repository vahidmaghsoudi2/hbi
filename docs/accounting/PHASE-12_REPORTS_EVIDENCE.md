# PHASE 12 — Accounting Reports Evidence

**Status:** **CLOSED / PASS**  
**Owner:** Grok2  
**Baseline SHA:** `ef9b44e87cc3a81bfe6033f2c853d7d23b8d2294`  
**Real `data/hbi.db` modified:** **NO**

## Reality audit

Reports are pure reads over Sale, SaleReturn, Inventory, Product, Category.  
No discount column; SaleItem has no unit-cost snapshot → COGS/gross profit **UNSUPPORTED**.

## Supported reports

| Report | Notes |
|--------|-------|
| Sales today/week/month | via period bounds |
| Sales custom range | `[start, end)` on `Sale.created_at` |
| Inventory all | |
| Inventory by category | BOOST/HAIR/BEAUTY/TOOLS/PERFUME/OTHER |
| Low-stock inventory | threshold (default 5) |
| Revenue USD/IRR/Toman | sum of sale totals in range |
| Returns USD/IRR/Toman | sum of SaleReturn amounts |
| Net revenue | revenue − returns |

## Unsupported

| Metric | Reason |
|--------|--------|
| Discounts | no schema field |
| COGS | no unit cost on SaleItem |
| Gross profit | depends on COGS |

## API

```text
GET /api/v1/reports/sales/period/{today|week|month}
GET /api/v1/reports/sales/range?start=&end=
GET /api/v1/reports/inventory
GET /api/v1/reports/inventory/category/{category_id}
GET /api/v1/reports/inventory/low-stock?threshold=
GET /api/v1/reports/financial?start=&end=
GET /api/v1/reports/categories
```

## Files

- `app/services/report_service.py`
- `app/api/routers/reports.py`
- `app/api/routers/__init__.py`
- `app/main.py`
- `tests/test_accounting_reports.py`
- `docs/accounting/PHASE-12_REPORTS_EVIDENCE.md`
- `docs/accounting/ACCOUNTING_EXECUTION_PLAN.md`

## Schema changes

**NONE**

## Tests

```text
python -m pytest tests/test_accounting_reports.py --noconftest -q
→ 6 passed

Full accounting regression:
→ 86 passed
```

## Frontend

Zero FE changes (API-only reports).

## Verdict

**CLOSED / PASS** — Phase 13+ STOPPED
