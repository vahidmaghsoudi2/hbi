# HBI Homepage Stage 0 — Route and Action Inventory (Source Audit)

**Status:** source-level inventory, not runtime acceptance  
**Audit ref:** `feat/homepage-navigation-ia-stage1-final` at `859d625be941f8bbef7e88cc271e9757d351bf42` (navigation PR #362)  
**Related dashboard candidate:** PR #363, branch `feat/homepage-dashboard-stage2`  
**Authority:** Product Owner decision in Issue #352 comment 6144947310  
**Boundary:** no changes to `master`; no claim that CI, browser/runtime, API authorization, or transaction ledger behavior passed.

## 1. Approved target domains

1. Home / Dashboard
2. Product Intake & Product Management
3. Customers
4. Consultation
5. Sales
6. Products & Inventory
7. Purchasing
8. Reports
9. Persistent shell action: Logout

The code currently does not expose all these as clean, independent destinations. This inventory describes source evidence, not a declaration that the current UI is accepted.

## 2. Current routes and access gates

| Route | Component | Gate in App.tsx | Current role/purpose | Audit status |
|---|---|---|---|---|
| `/` | `NewHomePage` | `AdminGate` | Multi-domain workspace with internal panels | Code confirmed; route renders |
| `/login` | `AdminLoginPage` | Public login route | Creates Admin session via `/auth/login` | Code confirmed; runtime not tested |
| `/catalog` | `CatalogPage` | `AdminGate` | Standalone public-product-list view | Misleading risk: route is Admin-gated but calls unauthenticated `listProducts()` |
| `/accounting` | `AccountingHomePage` | `AdminGate` | Sales, inventory, stock flow, financial report | Source confirmed; API/runtime not verified |
| `/purchase` | `PurchasePage` | `AdminGate` | Purchase / physical stock-in | Source confirmed; API/runtime not verified |
| `/pilot` | `PilotPage` | No `AdminGate` in App.tsx | Pilot/customer-token workflow | Must not be advertised as an Admin destination until role intent is resolved |
| `/recommendation` | `RecommendationPage` | No `AdminGate` in App.tsx | Separate pilot-token recommendation/override/feedback workflow | Role and integration mismatch; not suitable as an unqualified Admin shortcut |

## 3. Workspace navigation and action map

The root workspace has three UI levels: main domain cards, domain-specific cards, and content panels. Most destinations are state changes inside `NewHomePage`, not separate routes.

| Visible domain / action | Current destination | Current content or operation | Classification |
|---|---|---|---|
| خانه و داشبورد | internal section `home` → panel `home` | Quick actions, sales summary, inventory rows, low-stock alert, recent stock movements | KEEP as standalone home destination; verify real APIs at runtime |
| مشتریان | section `customers` | Search/history → `previous`; profile/create → `profile` | KEEP separate from consultation; repair/verify identity and history flow |
| جست‌وجوی مشتری | panel `previous` | `searchCustomers`, select customer, then loads customer sales history | KEEP under Customers; selection currently also creates a pilot token and enters consultation, so the boundary is mixed |
| پروفایل مشتری / مشتری جدید | panel `profile` | customer intake/profile state | KEEP under Customers; verify mobile + family-name identity contract and no first-name identity shortcut |
| مشاوره | section `consultation` | new consultation → `consult`; suggestions/operator decision → `results` | KEEP separate from Customers and Sales; flow must remain coherent in-context |
| شروع مشاوره | panel `consult` | customer intake/case setup, concern/skin details, recommendation generation | KEEP under Consultation; runtime and eligible-product linkage unverified |
| پیشنهادها و تصمیم اپراتور | panel `results` | recommendation/evaluation results and operator decision | KEEP under Consultation; no shortcut from recommendation into sale |
| فروش | section `sales` → panel `sales` | Direct sale form and customer association when explicitly selected | KEEP as standalone domain; sale must not require consultation |
| مدیریت محصولات | section `products` | catalog, product intake/edit, QA review | SPLIT conceptually according to approved IA: Product Intake & Product Management is distinct from Products & Inventory |
| فهرست محصولات | panel `catalog` | managed product list via Admin-aware list path in workspace | KEEP in product management workflow; distinguish from public `/catalog` route |
| ورود و ویرایش محصول | panel `intake` | `ProductIntakePanel`: create/update product, duplicate checks, research/evidence draft | KEEP under Product Intake & Product Management |
| بررسی و تأیید QA | panel `review` | `ProductReviewPanel`: product dossier, evidence, identity status, QA verdict, reject reason | KEEP under Product Intake & Product Management; approval transitions are server-side |
| خرید / ورود موجودی | `/purchase` | `listManageableProducts`, FX rate, `stockInInventory` | KEEP under Purchasing; physical stock-in is not product intake |
| گزارش‌ها | `/accounting` | Sales, inventory, stock flow, financial report | KEEP under Reports; gross profit/COGS remain deferred |
| خروج از حساب مدیر | `logout()` → `/login` | Clears workspace/session values and navigates to login | KEEP as persistent shell action; verify browser back and protected-route behavior |

## 4. Key API and session dependencies confirmed in source

| Operation | Source-level dependency | Risk / evidence gap |
|---|---|---|
| Workspace product list | `listManageableProducts(adminToken)` → `GET /products/manage` | Runtime data and Admin authorization not verified |
| Sale product picker | `listProducts()` → `GET /products/` without token | Mismatch with Admin-managed product list; can appear empty even while manageable products exist |
| Sale inventory/price | `getInventoryByProduct(productId, operatorToken)`, `getCurrentFx()` | Must verify pricing/stock and error states in runtime |
| Sale submit | `createSale()` reads `hbi_admin_access_token` and posts `/sales/` | Source guard exists; end-to-end transaction + ledger not runtime-tested |
| Customer search | `searchCustomers(query, operatorToken)` | Search supports name/mobile in UI; identity rules require separate verification |
| Customer history | `listSalesByCustomer(customerId, token)` | Selection path obtains a pilot token; does not yet represent a clean Admin-only customer workflow |
| Product intake/review | create/update product, evidence, duplicate checks, identity/QA endpoints using operator session helpers | Must verify endpoint authorization and server transitions |
| Purchasing | `listManageableProducts(token)`, `getCurrentFx()`, `stockInInventory(..., token)` | FX and inventory ledger must be tested with real database |
| Dashboard reports | sales-period, inventory, low-stock threshold `<= 5`, stock movements | Source has empty/error states; API truth and browser rendering not verified |
| Accounting reports | sales period, financial summary, inventory, low-stock, stock movements | COGS/profit intentionally deferred; no profit claim allowed |

## 5. Misplacements, duplicates, and missing target areas

- **Products & Inventory is not a clean primary area yet.** Current root menu labels a broad card “مدیریت محصولات” and has a separate “خرید” card, but the approved IA distinguishes product-governance intake/QA, catalog/inventory visibility, and purchasing/stock-in.
- **Product catalog has two meanings.** Internal workspace `catalog` uses the Admin-managed product list; route `/catalog` uses public `listProducts()`. They must not be presented as interchangeable.
- **Customers and Consultation are visibly separate cards, but the selected-customer path crosses into consultation and uses a pilot token.** Audit this transition before splitting components or moving links.
- **Reports currently means the Accounting page.** Its actual sections are Sales Today, Inventory, Stock Flow, and Financial Report. Gross profit, COGS, and unsupported discount calculations remain deferred.
- **Settings is an approved target domain but no separate settings page/menu is confirmed in the reviewed root source.** Do not invent a destination; classify it as missing until a real settings capability is identified.
- **Product-intake dashboard counts are absent by design in the current source.** Do not add mock totals; first verify an authoritative Admin-backed lifecycle summary API.
- **Pilot and Recommendation routes are not Admin-gated.** Do not surface them as operator navigation until intended access and token model are corrected.
- **Legacy `HomePage.tsx` and `main.jsx` are not confirmed safe to delete.** They require a full-repository reference scan; this inventory does not authorize removal.

## 6. Ordered implementation decisions

1. Repair and test the sale product source mismatch in an isolated change: decide whether sale selection should use the Admin-managed list, then test product selection, inventory/price, direct sale with no consultation, and resulting ledger.
2. Reconcile navigation labels and destinations with the approved target tree. Do not split/delete components until all inbound/outbound links and route consumers are traced.
3. Make product-intake/QA discoverable under Product Intake & Product Management; keep catalog/inventory under Products & Inventory; keep physical stock-in under Purchasing.
4. Keep Customers and Consultation as distinct primary domains. Preserve consultation's in-context flow: reality/problem → valid need → eligible gallery products → recommendation → operator decision.
5. Keep Reports limited to backed sales/inventory/financial endpoints; profit stays deferred.
6. Resolve Settings as either an existing real capability or a documented missing item. Logout remains in the persistent shell.
7. Run tests/build, then verify the actual Windows/browser runtime and API behavior. Report each evidence level separately.

## 7. Verification boundary

- **Confirmed:** source routes, component responsibilities, visible labels and button targets cited above.
- **Not confirmed:** CI status for this audit, browser rendering, endpoint authorization, non-empty product catalog, direct-sale transaction, inventory-ledger consistency, customer identity edge cases, and cross-page browser history.
- **Not changed:** `master`; no route/file deletion or rename is authorized by this audit.
