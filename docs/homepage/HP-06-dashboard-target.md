# HP-06 — Target for Gallery Home Page 1 (Dashboard)

**Status:** DONE — implementation and exact-head verification complete on PR #674; master integration pending  
**Authority:** Product Owner direction 2026-11-15 + previously supplied system diagram  
**Related:** HOMEPAGE_COMPLETION_LEDGER.md (HP-06)

## Goal and section structure

The first gallery-home page has four operational sections in order:

1. KPI strip — live today/month sales, low-stock count, and inventory report rows.
2. Quick Actions — direct sale, new consultation, new customer, purchase/stock-in.
3. Attention — real low-stock rows from the existing endpoint only.
4. Recent Activity — latest real stock movements from the existing endpoint (up to eight).

The top system map is the existing nine main-menu cards. The full domain relationship map remains optional and outside this bounded completion.

## Constraints

- No fake data or placeholder counters/rows.
- Only existing live endpoints and data contracts; no new endpoints.
- No invented status fields.
- Consultation-incomplete and product-QA-pending counts are omitted because no approved aggregate endpoint exists.
- No ProductKnowledge, Evidence, lifecycle, or recommendation changes.

## Implemented

- Existing KPI refresh/live data loading retained.
- Quick-action section header and hierarchy clarified.
- Attention block shows total low-stock count and up to five product IDs with available quantity; remaining count shown when needed.
- Low-stock report failure renders UNKNOWN/unavailable rather than falsely asserting zero items.
- Recent Activity remains a real movements table driven only by `dashboardMovements`, with an explicit eight-record limit.
- Browser regression covers low-stock details, report destination, and unavailable-report state.
- A full-page dashboard screenshot is captured by Playwright as `test-results/hp06-dashboard-low-stock.png` and included in the workflow artifact.

## Acceptance — VERIFIED on PR #674 head

- [x] Live data only; no fabricated KPI or rows.
- [x] KPI strip → Quick Actions → Attention → Recent Activity are clearly labelled.
- [x] Recent Activity is driven only by existing live stock movements.
- [x] Attention is driven only by real low-stock data available from the existing report; unavailable is distinct from zero.
- [x] No backend endpoint added.
- [x] Existing KPI loading preserved.
- [x] Browser proof and screenshot evidence attached to workflow artifact.

## Exact verification

- Commit: `38bb45b42792afc0f133ec0a562ce451f1fd0d33`
- [HBI CI](https://github.com/vahidmaghsoudi2/hbi/actions/runs/46177982812): **1,076 passed, 829 warnings, 2 subtests passed; 89% coverage**, frontend build and G8 regression/governance jobs successful.
- [HBI Auto Tasks](https://github.com/vahidmaghsoudi2/hbi/actions/runs/46177982876): successful.
- [HBI Pilot Browser Proof](https://github.com/vahidmaghsoudi2/hbi/actions/runs/46177982828): **29 passed**, including HP-06 live-low-stock and unavailable-state checks; screenshot evidence uploaded.

## Integration boundary

This item is DONE on the verified PR branch. PR #674 remains open pending review/merge; this ledger does not authorize merging. Local Windows runtime/database validation is not claimed. No further homepage work is authorized until integration; next priority is the Skin Intake Template Forms V1 baseline.
