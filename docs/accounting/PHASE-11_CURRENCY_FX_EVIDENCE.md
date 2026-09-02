# PHASE 11 — Currency / FX Evidence

**Status:** **CLOSED / PASS**  
**Owner:** Grok2  
**Baseline SHA:** `a7c6c6db33c22c5fa66ba65bcb623d12fdb8811e`  
**Real `data/hbi.db` modified:** **NO**

## Reality audit

- `OperationalFxRate` table exists (operational only).
- Transaction snapshots already on Sale / SaleItem / Payment / SaleReturn / StockMovement / Inventory price fields.
- Workflows (stock-in, sale, payment, return) already required explicit FX — never invent rate.

## C-01 formulas

```text
R = fx_rate_usd_to_irr  (IRR per 1 USD)
amount_irr = amount_usd * R
amount_toman = amount_irr / 10
amount_usd = amount_irr / R
amount_irr = amount_toman * 10
```

## Implementation

- `app/services/currency_fx.py` — shared helpers + validation
- `app/services/operational_fx_service.py` — set/get current operational rate
- Stock-in reuses shared helpers (re-exports for legacy imports)
- Operational rate update does **not** rewrite historical snapshots

## API

```text
GET  /api/v1/fx/current
POST /api/v1/fx/operational   (auth)
```

## Schema changes

**NONE**

## Tests

```text
python -m pytest tests/test_currency_fx_workflow.py --noconftest -q
→ 5 passed

Full accounting regression:
→ 80 passed
```

## Known limitations

- Operational rate is optional for workflows that still require explicit FX on the request
- No external FX feed / auto-fetch
- Live HTTP suite not run in agent

## Verdict

**CLOSED / PASS** — Phase 12+ STOPPED
