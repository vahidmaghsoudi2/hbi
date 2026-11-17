# HP-06 — Target for Gallery Home Page 1 (Dashboard)

**Status:** OPEN  
**Authority:** Product Owner direction 2026-11-15 + previously supplied system diagram  
**Related:** HOMEPAGE_COMPLETION_LEDGER.md (HP-06)

## Goal

Make the first page of the HBI gallery homepage (the operational dashboard shown when the user enters «خانه و داشبورد») match the structure of the approved diagram:

1. **Top system map** (already largely reflected by the nine main-menu cards)
2. **Operational dashboard panel** containing:
   - KPI cards (live data only — sales today, consultations today if available, monthly sales, low-stock count)
   - Quick-action buttons (ثبت فروش مستقیم، مشاوره جدید، ثبت مشتری جدید، ثبت خرید / ورود کالا)
   - Attention / نیازمند توجه list (real items only: incomplete consultations, low stock, products waiting QA, etc.)
   - Recent activity table (fed from real recent movements / sales / consultations — no fake rows)
3. **Domain relationship map** (optional secondary view or collapsible section; not required for the first landing view)

## Constraints (from existing ADR)

- No fake data or placeholder counters.
- Only LIVE / PARTIALLY_CONNECTED / PLANNED states.
- Reuse existing backend contracts (`getSalesPeriod`, `getLowStockReport`, `getStockMovements`, etc.).
- Do not invent new status fields.

## Current baseline in `NewHomePage.tsx`

- Main menu cards already cover the seven top-level domains + encyclopedia + product management.
- Home panel already loads live sales / inventory / low-stock / movements.
- Quick actions for sales, customers and consultation exist.
- Missing or incomplete relative to the diagram: structured recent-activity table, clearer attention list, explicit “consultations today” KPI if a real endpoint exists, and visual hierarchy closer to the supplied mock.

## Implementation sequence (after HP-05 lands)

1. Apply the logout-removal patch (HP-05).
2. Strengthen the existing home panel layout to match the diagram sections without removing any live data paths.
3. Add a real recent-activity table driven by `dashboardMovements` (and any other already-available recent records).
4. Expand the attention list using only data that is already fetched or can be fetched with existing contracts.
5. Browser evidence + update this file and the Ledger when done.

## Non-goals for this stage

- Building the full domain-relationship interactive map as a separate page.
- Adding new backend endpoints solely for decorative KPIs.
- Changing the main-menu information architecture beyond what is already observed.
