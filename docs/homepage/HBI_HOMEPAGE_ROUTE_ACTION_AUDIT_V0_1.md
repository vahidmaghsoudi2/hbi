# HBI Homepage Route and Action Audit — Working Baseline

**Status:** source audit in progress; not runtime-verified.  
**Branch:** `agent/chatgpt/homepage-admin-gate/202610112355`  
**Scope:** homepage, direct-sale entry, product/catalog, purchasing, customer/consultation, recommendation, accounting, settings/logout.  
**Safety:** no master changes; PR #347 stays Draft and unmerged until local runtime proof and PO acceptance.

## Product rules
1. Home is a standalone daily dashboard; quick links may point to operations owned by another section.
2. Primary navigation domains: Home; Products & Inventory; Customer & Consultation; Sales; Accounting & Finance; Settings/Logout.
3. Direct sale must not require a prior consultation.
4. A visible label must match both the destination and the actual operation.
5. Moving/merging/removing an item requires checking inbound/outbound links, route/query consumers, API calls, token/role requirements, and data dependencies.
6. The only system operator is Admin/manager. Customers are records, not system users.
7. Do not claim a feature is operational based only on mocked tests or a route existing.
8. Keep unsupported gross-profit/COGS calculations deferred. Do not use old test product imports as proof of a validated catalog.
9. Keep product intake/catalog governance in its current scope; do not silently broaden this homepage task into a product-import project.

## Current route tree (source-derived)
- `/` — `NewDashboardGalleryHome`, guarded by `AdminGate`
  - Quick action: **ثبت فروش** → `/workspace?panel=sales`
  - Quick action: **مشتری و مشاوره** → `/workspace?panel=consult`
  - Quick action: **گالری محصولات** → `/catalog`
  - Quick action: **خرید و موجودی** → `/purchase`
  - Other direct links:
    - **بررسی پرونده کالا** → `/workspace?panel=review`
    - **نتایج مشاوره** → `/workspace?panel=results`
    - **سوابق مراجعه** → `/workspace?panel=previous`
    - **پرونده مشتری** → `/workspace?panel=profile`
    - **محیط کاری کامل** → `/workspace`
    - **مالی و حسابداری** → `/accounting`
  - Sidebar: Home, Products & Inventory (currently routes to `/catalog`), Customer & Consultation (consult panel), Sales (sales panel), Accounting & Finance.
  - Logout clears session storage keys and routes to `/login`.
- `/workspace` — `NewHomePage`, guarded by `AdminGate`; panel is selected from `?panel=`:
  - `consult`: consultation form, customer identity inputs, need/skin inputs, creates consultation/recommendation flow.
  - `previous`: customer search and purchase history; selecting a customer for consultation obtains a pilot token.
  - `profile`: customer profile fields and save action; “new customer” action.
  - `catalog`: manageable products list; edit routes internally to `intake`, review routes internally to `review`.
  - `review`: ProductReviewPanel.
  - `intake`: ProductIntakePanel.
  - `results`: eligible/rejected recommendation display.
  - `sales`: direct sale panel; Admin token required by sale submission; customer is searched/selected without requiring consultation.
  - `about`: workflow explanation.
  - Workspace header additionally links to `/purchase` and `/accounting`.
- `/catalog` — `CatalogPage`, guarded by `AdminGate`. Must audit actual list endpoint and product eligibility.
- `/purchase` — `PurchasePage`, guarded by `AdminGate`; loads manageable products using Admin token, obtains FX rate, submits stock-in, updates inventory.
- `/accounting` — `AccountingHomePage`, guarded by `AdminGate`; four sections: today's sales, inventory, stock flow, financial report. Gross profit remains deferred pending approved COGS policy.
- `/recommendation` — `RecommendationPage`, now guarded by `AdminGate`. The page still consumes the internal pilot/customer token and is not linked from the operational homepage; treat it as a restricted internal/non-production workflow until its operator-owned end-to-end flow is redesigned and verified.
- `/pilot` — `PilotPage`, now guarded by `AdminGate`. It is an internal/non-production case-creation utility, not a customer login or a primary navigation destination.
- `/login` — `AdminLoginPage`.

## First-priority sales findings
- The homepage sales link and router panel mapping are consistent: `/workspace?panel=sales` selects the sales panel.
- The sales panel's product dropdown now calls `listManageableProducts()` with the Admin session and filters to `ACTIVE` products with readable inventory, positive unreserved quantity, and a non-null authoritative `sale_price_usd`. This is source-level implementation, not yet local-runtime proof.
- Sale submit uses the Admin session via `createSale`; customer search also uses the Admin token. Selecting a buyer for direct sale clears customer/pilot tokens and does not require a consultation.
- The manual product-ID bypass has been removed. If no eligible catalog/inventory rows exist, the UI should show an empty/error state rather than accepting an arbitrary ID.
- The browser test covers eligible vs draft/out-of-stock/unpriced products, but mocked API responses do not prove that the local backend and database provide the expected records.
- Local environment previously had a default SQLite database with zero products. If still empty, a blank dropdown may reflect missing validated data, and must not be “fixed” by silently importing old test products.

## Disposition matrix (provisional)
| Item | Provisional disposition | Required proof |
|---|---|---|
| Home dashboard | KEEP | visual/runtime check |
| Direct sale quick action | KEEP + VERIFY/REPAIR | actual sale panel, Admin auth, catalog load, stock/price, create-sale result |
| Products & Inventory sidebar | REPAIR navigation grouping | map catalog, product review/intake, purchase/stock movements |
| Customer & Consultation | KEEP but split by task within its section | customer search/profile/consultation/history/results links and identity rules |
| Sales panel inside general workspace | REPAIR placement, then decide separate page | inspect route consumers, API contracts, tests; preserve deep links |
| Product intake/review | MOVE/KEEP under Products & Inventory (provisional) | identify all consumers and permissions |
| Recommendation direct link | REMOVED from homepage; route Admin-gated | redesign/verify operator-owned flow before restoring a shortcut |
| Purchase | KEEP under Products & Inventory | runtime stock-in test with valid product and FX |
| Accounting | KEEP as separate area | runtime API data; preserve deferred gross profit |
| Pilot route | REMOVED from homepage; route Admin-gated | retain only as restricted internal/non-production utility |
| Settings | CREATE only after current settings/ logout capabilities are inventoried | avoid inventing non-existent settings pages |
| Logout | KEEP under account/session area | verify session cleanup and login redirect |

## Audit and test plan
1. Source-check the API contracts and frontend calls for product management, inventory lookup, create sale, customer search, stock-in, and financial reports.
2. Add focused browser coverage for Admin route gates and sale-picker eligibility.
3. Keep the recommendation/pilot utilities out of homepage navigation and require Admin session at the router while their internal token workflow remains non-production.
4. Run frontend typecheck/build and targeted tests in CI; record the exact head SHA and results.
5. User runs the branch on the laptop and verifies actual Admin login, sale picker, valid catalog item, price/stock lookup, sale submission, and accounting/inventory reflection. If there is no approved catalog/inventory data, report that as a data prerequisite rather than importing legacy test products.
6. Only after this, apply the final submenu tree and verify every moved route, quick link, back-navigation, and logout.
