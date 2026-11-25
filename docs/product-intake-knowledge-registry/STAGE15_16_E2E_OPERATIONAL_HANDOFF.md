# Stage 15–16 — E2E Verification and Operational Handoff

**Scope:** final roadmap slice, end-to-end verification and concise operator handoff.  
**Base:** `master` at `08b769eab3bc9cf9365f1d7d4c22d5e7e433b409`.  
**Safety:** all new E2E records are disposable test fixtures. No production database, canonical Product, ProductKnowledge, Evidence, Inventory, QA, lifecycle, or ProductProblemLink rows are changed.

## End-to-end coverage added

- `tests/test_stage15_16_e2e.py`: pilot authentication → customer-owned Case creation → consultation save/readback → consultation output → explainable suitability → P22 rejection → cross-customer access denial. Uses the shared in-memory pytest database.
- `tests/browser/consultation-suitability.spec.cjs`: real browser flow against the isolated pilot API/database. Confirms saved consultation details render, empty candidate results are not presented as product-unsuitability, and P22 is rejected.
- Existing `HBI CI` remains the backend/full-suite, coverage, frontend typecheck/build, and governance gate.
- Existing `HBI Pilot Browser Proof` discovers all `tests/browser/*.spec.cjs` tests, runs the 61-record parser conformance check, and exercises the disposable SQLite/API/frontend/Chromium stack.

## Run and verify

### Backend / API E2E

From repository root, with Python 3.12 and project dependencies installed:

```powershell
python -m pytest tests/test_stage15_16_e2e.py tests/test_consultation_context_service.py tests/test_explainable_suitability_consultation_output.py tests/test_explainable_suitability_consultation_api.py -q
```

Full backend suite and frontend checks:

```powershell
python -m pytest --cov=app --cov-report=term-missing -v
Set-Location frontend
npm install --no-audit --no-fund
npm run typecheck
npm run build
Set-Location ..
```

### Browser proof

Run GitHub Actions workflow **HBI Pilot Browser Proof** on the PR. It creates a disposable SQLite database under the OS temporary directory, seeds test-only fixtures, starts the API and frontend, installs Chromium, runs all Playwright specs and removes the database/services at the end. Do not point this workflow or these tests at `data/hbi.db` or any live database.

## Local operator startup

Follow the repository's Developer Setup in `README.md`:

- Python 3.12; install `requirements.txt`.
- Backend: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`.
- Frontend: from `frontend`, run `npm install` then `npm run dev -- --host 127.0.0.1 --port 5173`.
- API docs: `http://127.0.0.1:8000/docs`.

Default local SQLite path is `data/hbi.db`. Back it up before local operational use. Never run fixture seeding or E2E scripts against this database.

## Runtime boundaries and known gates

- Consultation context is visit-specific data attached to its Case; customer ownership is enforced on read/write.
- Consultation output is a read-only projection of stored Case context and already-eligible Recommendation rows.
- Explainable suitability is read-only. A ProductProblemLink `CANDIDATE` remains human-review-only; it never becomes `SUPPORTED` or recommendation-eligible through this workflow.
- P22 remains context/reference-only and is rejected by suitability evaluation.
- Empty ProductProblemLink candidate results mean no current candidate records were found, not that a product is unsuitable.
- The seven ProductKnowledge drafts have not been operationally written under the separate PO authorization gate. Product QA/lifecycle states remain unchanged.
- No real ProductProblemLink relationships were inserted. Candidate retrieval and explainability do not create them.
- No recommendation eligibility, stock, Product Master, Evidence, or schema state is changed by this stage.

## Completion evidence

This handoff is complete when the PR's exact head SHA has successful **HBI CI**, **HBI Auto Tasks**, and **HBI Pilot Browser Proof** checks, and the PR is merged. A successful test run is not Product acceptance, clinical validation, G8 certification, or authorization to write operational product data.
