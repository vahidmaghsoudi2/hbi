# HBI Active Session

## Current Operational Handoff — 2026-11-11

**Current master:** `a1176412717b13a680f62cf1b0fabc0e53337c69`  
**Primary roadmap:** [Issue #406](https://github.com/vahidmaghsoudi2/hbi/issues/406)  
**Completed runtime audit:** [Issue #74](https://github.com/vahidmaghsoudi2/hbi/issues/74) — closed as `COMPLETE_WITH_OPERATIONAL_BLOCKERS`.

### Latest code delivery
- [PR #533](https://github.com/vahidmaghsoudi2/hbi/pull/533) — fix stale ProductKnowledge conflict status after audited Evidence field reclassification.
- Branch: `fix/anua-reclassification-refresh-pk-conflict`.
- Implementation commit validated: `338e2e16fef70ae09ab879249ccca45438ec33e3`. A documentation-only handoff update is included in this PR; its new head must complete the same required checks before merge.
- PR is OPEN and mergeable; **not merged**. Merge requires explicit PO authorization.
- Exact implementation-head CI: [run 43073630350](https://github.com/vahidmaghsoudi2/hbi/actions/runs/43073630350) — SUCCESS, 755 passed, 88% coverage, compile/G8/governance/frontend build successful.
- Exact implementation-head Auto Tasks: [run 43073630307](https://github.com/vahidmaghsoudi2/hbi/actions/runs/43073630307) — SUCCESS, 755 passed, 88% coverage.
- Exact implementation-head Browser Proof: [run 43073630267](https://github.com/vahidmaghsoudi2/hbi/actions/runs/43073630267) — SUCCESS, 30/30 browser tests and 61/61 parser conformance records passed; isolated pilot smoke successful.
- PR #533 changes only derived ProductKnowledge conflict status after the final active Evidence conflict is removed. It preserves knowledge content/confidence and does not promote pending Evidence or QA.

### Product intake — unresolved operational gates
The latest user-provided read-only DB snapshot showed:
- Seven canonical skincare Products remain `DRAFT / NEEDS_REVIEW / PENDING`.
- ProductKnowledge content fields are empty; P7 Anua had `CONFLICT` status due concentration and INCI assertions sharing the `ingredients` field.
- 25 Evidence rows remain `PENDING / UNKNOWN`; Anua's two ingredient assertions were not QA-approved.
- All seven Inventory rows were `OUT_OF_STOCK`, with zero available quantity.
- No Recommendation or ProductProblemLink rows existed.
- Main DB was read-only, integrity `ok`, FK violations empty, and SHA256 before/after matched. No production DB mutation was performed.
- Treat this as the last supplied snapshot, **not proof of the present DB state**; obtain a fresh read-only snapshot before any acceptance decision.

### Seven canonical products
1. COSRX The 6 Peptide Skin Booster Serum
2. Neutrogena Clear & Defend 2% Salicylic Acid Face Wash
3. Garnier Vitamin C Brightening Gel Cleanser
4. SKIN1004 Madagascar Centella Hyalu-Cica Water-Fit Sun Serum
5. ISDIN FotoUltra 100 Active Unify SPF50+
6. Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter
7. Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum

### Remaining critical work, in order
1. PO decision: merge PR #533 after its updated exact-head CI/Auto Tasks/Browser checks are green.
2. Refresh the local DB snapshot read-only; do not run the unsafe PR #526 draft-import wrapper. PR #526 is closed and its expected draft Evidence rows were already present in the last snapshot.
3. Verify physical product identity/market/GTIN/formula from front/back/INCI/barcode package evidence for each of the seven products. Do not infer a formula from another market or variant.
4. Human QA review of source-bound Evidence; only approved Evidence may populate ProductKnowledge.
5. Confirm real stock and quantities before inventory adjustments.
6. Run isolated seven-product Home Page E2E and close the acceptance tracker only after PO acceptance.
7. PR #504 remains OPEN as the acceptance tracker only. Its implementation branch is stale/diverged and must not be merged or replayed; the older #513/#514/#516 fixes are already in master.
8. Keep Issue #406 open until the product intake and seven-product acceptance gates are actually complete.

### Safety and continuity rules
- No production DB writes, migrations, importer runs, lifecycle/QA promotion, inventory adjustment, or ProductProblemLink creation without explicit authorization and verified evidence.
- Never start the app against the main DB; app startup can initialize/migrate it. Use disposable SQLite for tests.
- Protect local modifications in `E:\HBI_GitHub_Current` and the other named worktrees; do not reset, overwrite, or clean them.
- For each PowerShell diagnostic, put all output in Clipboard via `Set-Clipboard` and also print it.
- After every six separate chats, append a concise six-chat summary to this same file; do not create parallel handoff documents.
- If connectivity is interrupted, resume from this file and Issue #406. PR #533 and exact-head run links above are the latest validated code checkpoint.

---


## Status
- **Last Updated:** 2026-08-20
- **Active Phase:** Technical Improvements (Post Phase-1 Hardening)
- **Previous:** GATE 9 / Phase 1 CLOSED successfully

## Official Kick-off (Qwen + PO) — 2026-08-20
Phase 1 closed successfully. Project now enters **Technical Improvements** phase to bullet-proof the system before production deployment.

### Locked PO Decisions (still in force)
- Products C & D remain **UNIDENTIFIED**
- No identity/evidence action for C/D until further PO instruction

---

## Technical Improvements — Assignments

### 1. DeepSeek (Backend)
- [ ] Fix StarletteDeprecationWarning (httpx related)
- [ ] Write Unit Tests for reasoning modules:
  - `app/reasoning/claim_validator.py`
  - `app/reasoning/reasoning_engine.py`
  - `app/reasoning/conflict_analyzer.py`
- [ ] Raise overall Coverage to **> 80%**

### 2. Perplexity (Evidence Steward / QA)
- [ ] Review new unit tests and confirm they strictly validate Framework 4 & 5 rules with **NO ASSUMPTION**
- [ ] Run final Coverage Report:
  ```bash
  pytest --cov=app --cov-report=term-missing
  ```
- [ ] Confirm threshold > 80% is met

### 3. All Members
- Strict **NO ASSUMPTION** principle
- Any conflict or missing information → Conflict Register + Source of Truth

---

## Current Reasoning Modules
| Module | Path | Test Coverage Status |
|---|---|---|
| claim_validator | app/reasoning/claim_validator.py | Needs dedicated unit tests |
| reasoning_engine | app/reasoning/reasoning_engine.py | Needs dedicated unit tests |
| conflict_analyzer | app/reasoning/conflict_analyzer.py | Needs dedicated unit tests |
| scoring | app/reasoning/scoring.py | Partial (test_scoring_engine.py exists) |

---

## Team Status

| Agent | Role | Current Task |
|---|---|---|
| DeepSeek | Backend | StarletteDeprecationWarning + Unit Tests for reasoning |
| Perplexity | QA / Evidence | Review tests + Final Coverage Report |
| Grok | Red Team / Support | Supporting Technical Improvements |
| Qwen | PM / Data QA | Coordination + receiving final reports |
| PO | Decision Maker | C/D locked UNIDENTIFIED |

---

## For AI Agent (Qwen)
1. Read this file first
2. Enforce NO ASSUMPTION
3. Accept only Artifact-based reports (especially full pytest --cov output)
4. Products C & D stay UNIDENTIFIED
5. Track DeepSeek unit tests + Perplexity coverage confirmation
