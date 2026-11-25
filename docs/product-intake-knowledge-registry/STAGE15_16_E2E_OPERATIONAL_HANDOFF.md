# Stage 15–16 — End-to-End Verification and Operational Handoff

**Status:** Implementation package in PR; acceptance depends on the PR's exact-head CI evidence and PO merge.
**Scope:** The six-stage skin-consultation delivery only. This document does not certify production readiness, clinical efficacy, ProductKnowledge approval, or G8.

## 1. Baseline and provenance

- Repository: `vahidmaghsoudi2/hbi`
- Base branch: `master`
- Exact input commit: `08b769eab3bc9cf9365f1d7d4c22d5e7e433b409` (Stage 13–14 merge)
- Work branch: `agent/gpt6/stage15-16-e2e-handoff/202611251530`
- Agent: ChatGPT GPT-6, tool-assisted GitHub workflow
- GitHub operations: create branch from the exact input SHA; add the browser E2E spec and this handoff document on that branch.
- Local test execution: not performed by the agent runtime. The PR's GitHub Actions runs are the execution evidence.

## 2. End-to-end coverage

`tests/browser/consultation-explainability-e2e.spec.cjs` exercises the integrated customer path:

1. Open the HBI workspace and enter Consultation.
2. Create a customer and a skin consultation through the real UI.
3. Submit affected area, duration, customer-reported severity, aggravating factors, current products, and notes.
4. Verify the consultation PUT response and read the saved context back from the customer-owned API.
5. Open the Recommendation page and read the structured consultation output.
6. Request explainability for P17 and verify the computed-only, human-review-only contract.
7. Verify that an empty ProductProblemLink candidate set is not presented as a product-unsuitability decision.
8. Verify that context/reference-only P22 is rejected with HTTP 422.

The existing browser suite remains in place, including the full 61-record problem-bank test, pilot recommendation readback/fail-closed test, and other homepage/navigation proofs.

## 3. CI execution and evidence

The PR must pass the existing workflows on its final head SHA:

- **HBI CI:** Python compilation, G8 regression bundle, strict backend coverage tests, frontend typecheck/build, and isolated pilot smoke.
- **HBI Pilot Browser Proof:** 61-record parser conformance, disposable SQLite fixture preparation, real API/frontend startup, and all Playwright tests in `tests/browser`.
- **HBI Auto Tasks:** existing repository automation checks.

The browser workflow uploads the Playwright report, test-results, API/web logs, and parser conformance result under artifacts named with the tested commit SHA. A passing unit/service test alone is not a substitute for this real-browser proof.

## 4. Safe local reproduction

Use a disposable SQLite database only. The fixture-preparation script refuses a missing/non-SQLite URL, a non-absolute path, a path outside the dedicated temporary pilot directory, unexpected filenames, symlinks, and a pre-existing non-empty database.

From the repository root:

```bash
export HBI_ENV=development
export DATABASE_URL=sqlite:////tmp/hbi-g8-pilot/pilot-browser-proof.sqlite
export HBI_PILOT_FIXTURE_MODE=browser-fixture
mkdir -p /tmp/hbi-g8-pilot
python scripts/prepare_pilot_browser_db.py

# Terminal 1
uvicorn app.main:app --host 127.0.0.1 --port 8765

# Terminal 2
cd frontend
npm install --no-audit --no-fund --include=optional
npx playwright install chromium
VITE_API_BASE=http://127.0.0.1:8765/api/v1 npm run dev -- --host 127.0.0.1 --port 4173

# Terminal 3, from repository root
export HBI_TEST_API_URL=http://127.0.0.1:8765/api/v1
export HBI_TEST_WEB_URL=http://127.0.0.1:4173
NODE_PATH="$PWD/frontend/node_modules" ./frontend/node_modules/.bin/playwright test --config=playwright.config.cjs
```

The GitHub workflow installs Chromium with system dependencies and also runs parser conformance before browser tests. Local reproduction is optional; CI on the exact PR head is the merge evidence.

## 5. Operational boundaries

- Browser data is fixture data in a disposable SQLite database. It is not a production or shop database.
- The E2E path creates a test customer/case and consultation context only inside that fixture.
- It does not insert real ProductProblemLink rows, alter ProductKnowledge, approve evidence, change Product identity/QA/lifecycle/inventory, or create a business recommendation from a CANDIDATE relationship.
- Suitability remains computed-only and human-review-only. Recommendation eligibility is never inferred from a candidate.
- An empty candidate result means no current link was retrieved; it does not establish unsuitability.
- The E2E intentionally exercises the empty-candidate path. Non-empty candidate filtering, integrity checks, market/variant isolation, and revision supersession remain covered by Stage 11–14 service/API tests.
- Passing these checks does not make the seven intake products QA VALID, ACTIVE, or recommendation-eligible. Their separate PO authorization and product gates remain in force.
- No live pilot start, production deployment, clinical diagnosis, or efficacy claim is authorized by this test package.

## 6. Acceptance checklist

- [ ] New consultation-to-explainability browser test passes on final PR head.
- [ ] Existing 61-record browser and parser conformance tests pass.
- [ ] Backend CI and frontend typecheck/build pass.
- [ ] CI evidence artifacts are attached to the exact tested commit.
- [ ] PR reviewed and explicitly merged by the PO.

**Completion rule:** Stage 15–16 is complete only after the above evidence is green and its PR is merged. A drafted test or a green result on an earlier commit is not completion.
