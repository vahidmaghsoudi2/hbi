# HBI Homepage Navigation & Page Placement Audit — Stage 2

**Audit target:** `feat/homepage-dashboard-stage2` (current Stage 2 IA ownership patch)  
**Status:** inventory and placement review only; no IA redesign approved by this artifact.  
**Guardrails:** do not merge to `master`; do not change Product Intake/QA lifecycle or the other team's product data. Customer is a record, not a system user. Direct sale must remain possible without consultation.

Legend: **✓** belongs in the proposed location; **X** misplaced or duplicated; **?** requires product decision/evidence before moving.

## 1. Existing route/page inventory

| Route | Current page | Access guard | Navigation relationship |
|---|---|---|---|
| `/login` | AdminLoginPage | Public login entry | Entry to Admin workspace |
| `/` | NewHomePage | AdminGate | Main menu, dashboard and embedded operational panels |
| `/catalog` | CatalogPage | AdminGate | Read-only list via `listProducts`; NewHomePage product panel uses `listManageableProducts` and also exposes intake/edit and QA. Similar entry labels, but not proven functionally identical |
| `/accounting` | AccountingHomePage | AdminGate | Sales report and finance report only; `?section=` selects a report |\n| `/inventory` | InventoryHomePage | AdminGate | Inventory report, low-stock report, and stock-flow report; `?section=` selects the view |
| `/purchase` | PurchasePage | AdminGate | Stock-in/purchase form; links back Home and Inventory |
| `/pilot` | PilotPage | AdminGate; separate pilot session still required for API calls | Non-production pilot flow; direct browser entry redirects to Admin login |
| `/recommendation` | RecommendationPage | AdminGate; separate pilot session still required for API calls | Non-production recommendation flow; direct browser entry redirects to Admin login |

## 2. Existing homepage tree

```text
HBI Admin workspace (/)
├── Home & Dashboard
│   ├── Quick actions
│   │   ├── Direct sale
│   │   ├── Customer search
│   │   ├── New customer
│   │   ├── Consultation
│   │   ├── Product intake
│   │   ├── Product QA review
│   │   └── Purchase / stock-in
│   ├── Operational summary
│   │   ├── Sales today
│   │   ├── Inventory
│   │   └── Low-stock alerts
│   ├── Attention / error states
│   └── Latest stock movements
├── Customers
│   ├── Search & history
│   └── Customer profile
├── Consultation
│   ├── New consultation
│   └── Recommendations & operator decision
├── Sales
│   └── Register sale & sales total/history
│       ├── Optional customer search/selection
│       ├── Sellable product picker
│       ├── Quantity / unit price / stock
│       └── Submit sale
├── Product Management
│   ├── Product list
│   ├── Product intake/edit
│   └── QA review
├── Products & Inventory
│   ├── Inventory report
│   └── Stock movement report
├── Purchase
│   └── Purchase / stock-in
├── Reports
│   ├── Sales report
│   ├── Inventory report
│   ├── Stock movement report
│   └── Finance report
└── Settings
    ├── Admin account
    └── Logout
```

## 3. Placement verdict against the agreed operating model

| Item / relationship | Verdict | Reason / action |
|---|---|---|
| Home/Dashboard as a standalone main destination | ✓ | Keep summary, alerts, recent movements and quick actions here; do not turn it into a parent for unrelated modules |
| Customers as a standalone main destination | ✓ | Customer record/search/history belongs here; customer does not receive system access |
| Consultation separate from Product Management | ✓ | Consultation records the real problem/need and leads to eligible-product recommendation/operator decision |
| Sales separate from Consultation | ✓ | Direct sale is a valid path; customer and consultation are optional for a walk-in sale |
| Product Management owns product list, intake/edit, QA review | ✓ / ? | Grouping is coherent, but lifecycle actions must remain those owned by the Product Intake/QA team; do not change those internals in this homepage pass |
| Products & Inventory separate from Product Management | ✓ | Inventory quantity/movement is operational stock, not product knowledge/intake/QA |
| Purchase/stock-in as a separate destination | ✓ | It is a stock operation, independent of consultation and sales |
| Accounting / Reports separate from product management | ✓ | Sales, stock and finance reporting belong in accounting/reporting |
| Consultation form has no shortcut into product management | ✓ | Product review and intake are a separate module; consultation stays focused on customer reality, problem, need, recommendation, and operator decision. |
| Sales report has one canonical menu owner | ✓ | The main menu now uses “حسابداری و گزارش‌ها”; its submenu contains sales and finance reports only |
| Inventory and stock-flow are owned by Products & Inventory | ✓ | Report rendering is now in `InventoryHomePage` at `/inventory`; Accounting retains sales and finance reports only. Dashboard and section shortcuts target the inventory route |
| Dashboard quick actions for Intake, QA and Purchase | ? | Acceptable only as clearly labelled shortcuts. They must not imply those modules are dashboard children or replace their canonical menu location |
| Product list embedded in NewHomePage plus `/catalog` route | ? | Code inspection shows different APIs and purposes: `/catalog` is a read-only list; the embedded panel uses manageable products and provides intake/edit and QA. Decide whether the read-only catalog is a useful distinct destination or an unnecessary duplicate; do not remove either based on label similarity alone |
| Settings separate, logout inside Settings | ✓ | Keep account/logout out of the main operational menu and avoid an always-visible logout action |
| `/pilot` and `/recommendation` routes | ✓ | AdminGate now protects browser entry. The pilot/customer JWT remains separate and API authorization must still be tested independently |
| Dashboard API failure/empty states | ✓ | Keep unknown values unknown; do not fabricate sales, inventory, QA or profit values |
| Gross profit on Accounting page | ? | Current UI says deferred by PO; do not present gross profit as calculated until cost-of-goods policy is approved |

## 4. Relationship map — intended business flow

```text
Customer record / consultation reality
                 |
                 v
          Problem / valid need
                 |
                 v
  Eligible HBI Gallery product + evidence
                 |
                 v
       Recommendation for operator
                 |
                 v
        Operator decision / report

Independent operational path:
Product catalog + QA eligibility + available stock
                 |
                 v
            Direct sale
      (customer optional; consultation optional)
                 |
                 v
       Sale / inventory / accounting

Stock replenishment:
Purchase / stock-in ---> Inventory ---> Stock-flow and reports
```

## 5. Lightweight line-only placement sketches

These are placement sketches, not visual redesigns. ✓ = belongs; X = misplaced/duplicated; ? = decision required.

### A. Main navigation

```text
+---------------------------------------------+
| HBI / Admin workspace                       |
+---------------------------------------------+
| ✓ Home & Dashboard                          |
| ✓ Customers                                 |
| ✓ Consultation                              |
| ✓ Sales                                     |
| ✓ Product Management                        |
| ✓ Products & Inventory                      |
| ✓ Purchase                                  |
| ✓ Accounting / Reports                      |
| ✓ Settings                                  |
+---------------------------------------------+
| X Do not nest Consultation under Products   |
| X Do not nest Accounting under Products     |
| X Do not nest Dashboard under Products      |
+---------------------------------------------+
```

### B. Home & Dashboard

```text
+---------------------------------------------+
| ✓ Dashboard summary                         |
+----------------------+----------------------+
| ✓ Sales today        | ✓ Inventory          |
+----------------------+----------------------+
| ✓ Low-stock alerts   | ✓ Recent movements   |
+---------------------------------------------+
| ✓ Quick actions: Sale / Customer / Consult  |
| ? Intake / QA / Purchase shortcuts          |
| X Do not show duplicate full module menus   |
+---------------------------------------------+
```

### C. Customers and Consultation

```text
+----------------------+  +----------------------+
| ✓ CUSTOMERS          |  | ✓ CONSULTATION       |
+----------------------+  +----------------------+
| ✓ Search/history     |  | ✓ New consultation   |
| ✓ Customer profile   |  | ✓ Need/problem       |
| ✓ Purchase history   |  | ✓ Recommendation     |
|                      |  | ✓ Operator decision  |
+----------------------+  +----------------------+
| Customer is a record; no customer login/UI  |
+---------------------------------------------+
```

### D. Sales and Product Management

```text
+----------------------+  +----------------------+
| ✓ SALES              |  | ✓ PRODUCT MANAGEMENT |
+----------------------+  +----------------------+
| ✓ Direct sale        |  | ✓ Product list       |
| ✓ Optional customer  |  | ✓ Intake/edit        |
| ✓ Sellable picker    |  | ✓ QA review          |
| ✓ Quantity/price     |  | ? Catalog route dup. |
| X Consultation gate  |  | X Accounting here    |
+----------------------+  +----------------------+
```

### E. Inventory, Purchase and Accounting

```text
+----------------------+  +----------------------+
| ✓ INVENTORY          |  | ✓ PURCHASE           |
+----------------------+  +----------------------+
| ✓ Inventory report   |  | ✓ Purchase / stock-in|
| ✓ Stock movement     |  | ✓ Product + quantity |
+----------------------+  +----------------------+
| ✓ ACCOUNTING / REPORTS                       |
+---------------------------------------------+
| ✓ Sales | ✓ Finance (Accounting) · ✓ Inventory | ✓ Stock flow (Products & Inventory) |
| X Avoid duplicate full destinations in menus |
+---------------------------------------------+
```

### F. Settings

```text
+---------------------------------------------+
| ✓ SETTINGS                                  |
+---------------------------------------------+
| ✓ Admin account                             |
| ✓ Logout                                    |
| X No consultation, product or accounting    |
+---------------------------------------------+
```

## 6. Controls and boxes currently present (page-level checklist)

- **Global/home shell:** main-menu button, page heading, current section label, return-to-main-menu button.
- **Main menu:** nine section cards/buttons listed in section 2.
- **Customers:** search by family name/mobile, search button, result/customer-selection buttons, purchase-history list, profile form, save profile, new customer. Family name is now an explicit `Customer.family_name` field; existing SQLite schemas receive an additive nullable column, and historical `name` values are preserved without guessing family names. Existing-mobile intake requires an exact family-name match and returns 409 on missing/mismatched family name; mobile ownership is never transferred. Legacy records without a verified family name remain unverified until the operator confirms it.
- **Consultation:** customer/profile fields, consultation line, concern and skin-type choices, notes, start/generate consultation action, status/error feedback.
- **Recommendation/operator results:** eligible recommendation cards, evidence/score details, show-all action, rejected/internal records panel; rejected items are not sale choices.
- **Sales:** optional customer search/select/remove, sellable-product select, quantity, unit price, available stock, amount summary, submit sale, refresh sales total, last-sale result.
- **Product Management:** product list, refresh, edit action, QA review action, intake/edit panel, review panel.
- **Inventory:** inventory report shortcut, stock movement shortcut.
- **Purchase:** product selector, quantity, purchase unit price, FX rate, reference ID, note, submit purchase, refresh, result summary.
- **Reports:** sales, inventory, stock movement, finance report shortcuts.
- **Accounting page:** Admin-session status, refresh, sales/net-revenue/inventory/gross-profit summary cards, four section buttons, active section content, error state, Home link.
- **Settings:** Admin account entry and logout.
- **Cross-cutting:** loading, empty, error and success messages. Keep them local to the relevant operation rather than showing unrelated errors in another module.

## 7. Decisions needed before structural implementation

1. **Canonical reporting owner:** Implemented in this patch. Inventory, low-stock and stock-flow views render at `/inventory`; Accounting owns only sales and finance reporting. Dashboard shortcuts remain allowed.
2. **Catalog role:** Decide whether the read-only `/catalog` page has a distinct operator use case from the manageable product list/intake/QA panel. Rename or remove an entry only after the purpose is explicit; current code does not prove they are identical.
3. **Pilot routes:** Confirm deployment restrictions for `/pilot` and `/recommendation`.
4. **Dashboard shortcuts:** Keep only high-frequency actions; label Intake/QA/Purchase as shortcuts, not nested dashboard submodules.

**Verification boundary:** This patch moves the actual inventory/stock-flow views into `/inventory` and updates navigation tests. Exact-head CI and browser proof must pass before this structural change is considered verified. Keep `master` untouched.
