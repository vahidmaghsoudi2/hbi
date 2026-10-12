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
    - **پیشنهاد محصول** → `/recommendation` (not AdminGate at router level; separate pilot/customer token flow)
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
- `/recommendation` — `RecommendationPage`, currently not router-guarded by AdminGate and uses a separate pilot/customer-token workflow. Role and placement require a product decision before presenting it as an Admin operation.
- `/pilot` — `PilotPage`, separate pilot/customer flow; not a customer-facing access path in the target operating model and must not be exposed as part of the manager's primary operational navigation without an explicit reason.
- `/login` — `AdminLoginPage`.

## First-priority sales findings
- The homepage sales link and router panel mapping are consistent: `/workspace?panel=sales` selects the sales panel.
- The sales panel's product dropdown is populated from `loadSellableProducts()`, which currently calls `listProducts()` with no Admin token. By contrast, the workspace product list calls `listManageableProducts()` after ensuring an Admin product-read session. This endpoint/auth/data-source mismatch is a concrete investigation target, but not yet proven to be the sole cause of an empty dropdown.
- Sale submit uses Admin session via `createSale`; customer search also uses Admin token. The selection path explicitly clears customer/pilot token and does not require consultation.
- Product choice drives inventory lookup; submit validates customer, Admin token, product ID, quantity, unit price, and available stock.
- The UI also allows manual product_id entry. This is an unsafe/poor operator experience and should be assessed for removal or replacement with a clear catalog-empty state after backend sale-eligibility semantics are confirmed.
- Do not simply replace `listProducts()` with `listManageableProducts()` until the API contracts and eligibility filters are inspected; a manageable product is not automatically a sale-eligible product.
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
| Recommendation direct link | REVIEW / likely REWORK | determine Admin operator flow; avoid pilot/customer-token requirement |
| Purchase | KEEP under Products & Inventory | runtime stock-in test with valid product and FX |
| Accounting | KEEP as separate area | runtime API data; preserve deferred gross profit |
| Pilot route | HIDE from manager IA unless explicitly needed | inspect inbound links and purpose |
| Settings | CREATE only after current settings/ logout capabilities are inventoried | avoid inventing non-existent settings pages |
| Logout | KEEP under account/session area | verify session cleanup and login redirect |

## Audit and test plan
1. Inspect backend routes and frontend API functions for product list/manageable products, inventory lookup, create sale, customer search, stock-in, and financial reports.
2. Inspect automated tests and route tests; add focused tests for any source changes.
3. Repair the narrowest proven defect first; avoid broad component rewrites before mapping dependencies.
4. Run frontend typecheck/build and targeted tests in CI or local environment; record exact result and commit.
5. User runs the branch on the laptop and verifies actual Admin login, sale picker, valid catalog item, price/stock lookup, sale submission, and accounting/inventory reflection. If there is no approved catalog/inventory data, report that as a data prerequisite rather than importing legacy test products.
6. Only after this, apply the final submenu tree and verify every moved route, quick link, back-navigation, and logout.
