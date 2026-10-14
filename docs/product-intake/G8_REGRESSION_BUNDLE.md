# G8 Automated Regression Bundle

**Purpose:** run a repeatable set of existing Product Intake regression tests without requiring the operator to navigate Swagger merely to execute this regression subset.

## Run

From the repository root with the project Python environment active:

```powershell
python scripts/run_g8_regression_bundle.py
```

The runner prints the result and retains a raw pytest log plus a Markdown report under the operating system temporary directory in `hbi-g8-regression-evidence`. The report records UTC session, current code SHA, branch, test list, exit status, and the interpretation boundary. The runner exits non-zero when pytest fails or required test files are missing.

## Included test modules

- `tests/test_wp01_intake_duplicate_gate.py`
- `tests/test_wp02_skin_safety_before_approve.py`
- `tests/test_catalog_intake_engine_ready_path.py`
- `tests/test_claim_taxonomy_contract.py`
- `tests/test_manufacturer_claim_mapping_guard.py`
- `tests/test_evidence_missing_hard_gate.py`
- `tests/test_product_intake_auth.py`
- `tests/test_gap04_recommendation_persistence.py`

## Acceptance boundary

This is supporting regression evidence, not a replacement for the G8 pilot. Current pytest fixtures use in-memory SQLite and synthetic records. A passing run does not establish real operator login, a real runtime session, production-database isolation, or complete A1–A9 acceptance. Keep G8 **BLOCKED / NOT VERIFIED** until each criterion has traceable evidence and independent review. This runner does not perform migrations, alter production data, or auto-activate products.
