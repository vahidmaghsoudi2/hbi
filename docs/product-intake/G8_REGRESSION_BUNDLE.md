# G8 Automated Regression Bundle

**Purpose:** run a repeatable, traceable set of existing Product Intake, duplicate-gate, skin-safety, evidence, and recommendation regression tests without requiring an operator to navigate Swagger.

## Run locally

From the repository root, with the project virtual environment active:

```powershell
python scripts/run_g8_regression_bundle.py
```

The runner prints a concise result and retains:
- the raw pytest output log;
- a Markdown report containing UTC session, current code SHA, branch, test list, exit status, and interpretation.

Both files are written under the operating system temporary directory in `hbi-g8-regression-evidence`. The runner exits with pytest's non-zero status on failure. It refuses to run if any expected test file is absent.

## Included tests

- `tests/test_wp01_intake_duplicate_gate.py`
- `tests/test_wp02_skin_safety_before_approve.py`
- `tests/test_catalog_intake_engine_ready_path.py`
- `tests/test_claim_taxonomy_contract.py`
- `tests/test_manufacturer_claim_mapping_guard.py`
- `tests/test_evidence_missing_hard_gate.py`
- `tests/test_product_intake_auth.py`
- `tests/test_gap04_recommendation_persistence.py`

## Important limits

This is a **regression bundle**, not a replacement for the G8 pilot. The existing pytest fixtures use an in-memory SQLite database and synthetic test records. Therefore a passing run does not establish real operator login, a real runtime session, production-database isolation, or complete A1–A9 acceptance. The G8 ledger must remain **BLOCKED / NOT VERIFIED** until each criterion has its own traceable evidence and independent review. This runner does not perform migrations, alter production data, seed the live pilot, or auto-activate products.
