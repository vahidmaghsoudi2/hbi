# PHASE 09 — Payment Workflow Evidence

**Status:** **CLOSED / PASS**  
**Owner:** Grok2  
**Baseline SHA:** `74c6295f3acc25d2463bc911b35868ed93a00d1a`  
**Real `data/hbi.db` modified:** **NO**

## Reality audit

Existing `Payment` model reused. Methods constrained by DB CheckConstraint:  
`CASH | CARD | TRANSFER | OTHER`.  
No `payment_status` column → **no invented state machine**.

## Architecture

`PaymentService.record_payment`:
- Sale must exist
- method ∈ VALID_METHODS
- amount_usd > 0
- fx_rate_usd_to_irr > 0 (caller-supplied)
- C-01: amount_irr = usd * R; amount_toman = irr / 10 (stored as int)
- Does **not** mutate Sale totals / FX (historical sale preserved)
- Rollback on failure

## API

```text
POST /api/v1/payments/
GET  /api/v1/payments/sale/{sale_id}
GET  /api/v1/payments/{payment_id}
Auth: required
```

## Files

- `app/services/payment_service.py` (new)
- `app/api/routers/payments.py` (new)
- `app/api/routers/__init__.py`
- `app/main.py`
- `tests/test_payment_workflow.py` (new)
- `docs/accounting/PHASE-09_PAYMENT_EVIDENCE.md`
- `docs/accounting/ACCOUNTING_EXECUTION_PLAN.md`

## Schema changes

**NONE**

## Tests

```text
python -m pytest tests/test_payment_workflow.py --noconftest -q
→ 11 passed

Regression combined with prior accounting suite:
→ 68 passed total
```

## Frontend

Zero FE changes.

## Known limitations

- No paid/unpaid sale status field
- No overpayment/underpayment business rule beyond amount > 0
- No refund (out of scope)
- Live HTTP suite not run in agent

## Verdict

**CLOSED / PASS** — Phase 10+ STOPPED
