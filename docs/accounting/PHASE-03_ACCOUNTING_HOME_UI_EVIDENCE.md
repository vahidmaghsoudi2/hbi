# PHASE 03 — Accounting Home UI Evidence

**Status:** IMPLEMENTED + DOCUMENTED — **AWAITING GATE**  
**Owner:** Grok2  
**Baseline SHA:** `ec9c2ed83915859669889c6e1c67af6ff8357c01`  
**Real data/hbi.db touched:** **NO**

## Reality audit

| Item | Finding |
|------|--------|
| Frontend stack | Vite + React 18 + TypeScript + react-router-dom v6 |
| Entry | `frontend/src/main.tsx` → `App.tsx` |
| Home | `NewHomePage` at route `/` |
| Existing routes | `/`, `/catalog`, `/pilot`, `/recommendation` |
| Styles | `home.css`, `app.css` (dark RTL palette) |
| package scripts | `dev` / `build` / `preview` (vite) |
| HTML | `lang="fa" dir="rtl"` |

## Architecture decision

- **Route:** `/accounting` (same convention as `/catalog`, `/pilot`)
- **Page:** `frontend/src/pages/AccountingHomePage.tsx`
- **Styles:** `frontend/src/styles/accounting.css` (reuse CSS variables from app.css)
- **Entry from Home:** `Link` «حسابداری» in `NewHomePage` header nav
- **Back:** `Link` to `/`
- **Summary:** no invented numbers — shows «در دسترس نیست / هنوز متصل نشده» + TODO for Phase 05+ API
- **Menu items:** disabled placeholders labeled «مرحله بعد» (no fake routes)

## Files

| Path | Action |
|------|--------|
| `frontend/src/pages/AccountingHomePage.tsx` | added |
| `frontend/src/styles/accounting.css` | added |
| `frontend/src/App.tsx` | modified (route) |
| `frontend/src/main.tsx` | modified (css import) |
| `frontend/src/pages/NewHomePage.tsx` | modified (nav link) |
| `docs/accounting/ACCOUNTING_EXECUTION_PLAN.md` | modified |
| `docs/accounting/PHASE-03_ACCOUNTING_HOME_UI_EVIDENCE.md` | added |

## Verification notes

- No migration, no real DB access, no Phase 04+ business logic.
- Frozen Product A–D / scoring / evidence / recommendation artifacts untouched.
- Frontend build should be run with: `cd frontend && npm run build` (requires node_modules).
- Phase 02 migration tests remain separate and unchanged.

## Acceptance (implementer self-check)

- [x] Reality audited
- [x] Architecture reused
- [x] Home → Accounting link
- [x] Accounting Home exists (RTL/Persian)
- [x] Required menu labels present
- [x] Back to Home
- [x] No fake accounting data
- [x] No Phase 04+ logic
- [x] No real DB touched
- [ ] Full `npm run build` executed in CI/local agent environment — **NOT VERIFIED in this session** (node_modules not installed here)
- [ ] Browser UI click-path executed — **NOT VERIFIED in this session**

**Gate recommendation:** **CONDITIONAL PASS** pending local/CI frontend build and visual QA.
