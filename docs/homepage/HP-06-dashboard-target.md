# HP-06 — Target for Gallery Home Page 1 (Dashboard)

**Status:** OPEN — CURRENT PRIORITY  
**Authority:** Product Owner direction 2026-11-15 + previously supplied system diagram  
**Related:** HOMEPAGE_COMPLETION_LEDGER.md (HP-06)  
**Manager decision:** 2026-11-27 — HP-05 closed; this item is now the single highest-priority homepage work.

## Goal

Make the first page of the HBI gallery homepage (the operational dashboard shown when the user enters «خانه و داشبورد») match the structure of the approved diagram:

1. **Top system map** (already largely reflected by the nine main-menu cards)
2. **Operational dashboard panel** containing:
   - KPI cards (live data only — sales today, monthly sales, low-stock count; consultations today only if a real endpoint already exists)
   - Quick-action buttons (ثبت فروش مستقیم، مشاوره جدید، ثبت مشتری جدید، ثبت خرید / ورود کالا)
   - Attention / نیازمند توجه list (real items only: low stock, products waiting QA if available, incomplete consultations if available)
   - Recent activity table (fed from real recent movements / sales — no fake rows)
3. **Domain relationship map** (optional secondary view or collapsible section; not required for the first landing view)

## Constraints (mandatory)

- No fake data or placeholder counters.
- Only LIVE / PARTIALLY_CONNECTED / PLANNED states.
- Reuse existing backend contracts only (`getSalesPeriod`, `getLowStockReport`, `getStockMovements`, `getInventoryReport`, etc.).
- Do not invent new status fields or new API endpoints in this stage.
- Do not touch ProductKnowledge, Evidence, lifecycle, or recommendation logic.

## Current baseline (master `b2f6964bb76155eed0ac7aa9268f5948dc1b14bc`)

- Main menu cards already cover the required top-level domains.
- Home panel already loads live data via `refreshDashboard()`:
  - sales today / month
  - inventory report
  - low-stock report
  - stock movements (limit 8)
- Quick actions for sales, customers and consultation exist.
- HP-05 logout removal is already present in the code.

**Gaps remaining relative to the diagram:**
- Structured recent-activity table is incomplete or visually weak.
- Attention list is not clearly separated / prioritised.
- Visual hierarchy and section labelling still need tightening to match the approved mock.

## Executable acceptance criteria (must all pass)

- [ ] Dashboard shows only live data; zero fake numbers or placeholder rows.
- [ ] Four clear sections are visible and labelled: KPI strip → Quick Actions → Attention → Recent Activity.
- [ ] Recent Activity table is driven exclusively by `dashboardMovements` (or equivalent already-fetched live data).
- [ ] Attention list contains only real low-stock / QA-pending / incomplete items that the current contracts can supply.
- [ ] No new backend endpoints introduced.
- [ ] No regression in existing live KPI loading.
- [ ] Browser evidence (screenshot or Playwright) attached to the closing PR.
- [ ] This file and the Completion Ledger updated to VERIFIED / DONE when closed.

## Implementation sequence (this branch)

1. Strengthen layout and visual hierarchy of the existing home panel (no data invention).
2. Make Recent Activity a proper table driven by `dashboardMovements`.
3. Make Attention list a clear, prioritised block using only already-available data.
4. Add minimal, professional section labels and spacing so the page matches the approved diagram intent.
5. Capture browser evidence and close the item.

## Non-goals for this stage

- Building the full domain-relationship interactive map.
- Adding new backend endpoints solely for decorative KPIs.
- Changing the main-menu information architecture.
- Any Product Intake or Skin Template work (that is Priority 2).

## Closure rule

When all acceptance criteria are met, update this file Status to **DONE**, update the Ledger, and open the PR for review. No further homepage work is authorised until this item is closed.
