# HBI Seller Home — Wireframe & Reality Gap V1

Status: IMPLEMENTATION IN PROGRESS — NOT ACCEPTED
Base: branch `design/seller-home-wireframe-v1`, created from current `master`
Rule: KEEP → COMPLETE → CHANGE → BUILD. No direct master changes.

## 1. Product decision

The default operational home is the seller's daily work surface, not a management analytics dashboard. Primary flow:

Customer → Consultation / Valid Need → Evidence-aware Recommendation → Sale / Invoice

Secondary direct actions: Find product, direct sale where permitted, customer purchase history, return against an existing sale. Management reporting and accounting remain reachable by authorized roles but do not dominate the seller home.

## 2. Low-fidelity home wireframe

```text
┌──────────────────────────────────────────────────────────┐
│ HBI | Search customer / product / invoice       Alerts    │
├──────────────┬───────────────────────────────────────────┤
│ Navigation   │ TODAY'S WORK                              │
│ Home         │ [1 Customer] → [2 Consultation]            │
│ Customers    │              → [3 Recommendation] → [4 Sale]│
│ Consultation │                                           │
│ Products     │ QUICK ACTIONS                             │
│ Sales        │ [Find customer] [New consultation]         │
│ Returns      │ [Direct sale*] [Return from invoice]       │
│ Inventory*   │                                           │
│ Accounting*  │ NEEDS ATTENTION (only real API data)       │
│ Reports*     │ Follow-ups | Low stock | Pending returns   │
├──────────────┴───────────────────────────────────────────┤
│ Small verified indicators only: sales today / low stock  │
└──────────────────────────────────────────────────────────┘
*Visible only when supported by actual capability and role.
```

## 3. Consultation in progress — wireframe

```text
Customer: [selected customer]       Previous history: [open]
Line: [Skin] [Hair] [Beauty] [Perfume] [Tools] [Other]
Need / concern: [structured selection]   Notes: [optional]
Evidence gaps / unknowns: [visible, never guessed]
[Save consultation] → [Evaluate eligible products]
```

The six gallery lines are the desired product taxonomy. Do not enable a line in consultation until product taxonomy, need mapping, and recommendation behavior for that line are verified. Missing evidence must remain visible.

## 4. Return from sale — wireframe

```text
Find original invoice: [invoice / customer / sale ID] [Search]
Original sale: [verified sale details]
Items: [product] [sold qty] [already returned] [remaining]
Return qty: [input]   Reason: [required/defined by policy]
Financial effect: [API-calculated / explicitly pending]
[Validate] [Register return]
Result: [return document ID] [inventory effect] [financial status]
```

A return must reference a recorded sale and cannot exceed the remaining sold quantity. UI must show the financial/refund status honestly; current service documentation says payment refunds are not implemented.

## 5. Source-level reality findings

- `frontend/src/pages/NewHomePage.tsx` already combines customer search, consultation, recommendations, product intake/review, and sale panels. Prefer reorganizing and completing it over a rewrite.
- Current `CONSULTATION_LINES` contains only `SKIN`; the requested six lines are not yet reflected in this consultation selector.
- `app/api/routers/sales.py` sale creation requires `ROLE_ADMIN`. A new admin-only `GET /sales/detail/{sale_id}` returns the recorded invoice and product-level sold / already-returned / remaining quantities.
- `app/api/routers/returns.py` return creation and listing require `ROLE_ADMIN`.
- `app/services/return_service.py` validates the original sale, matching sale item, and remaining returnable quantity; it increases inventory and records a `SaleReturn`. Its module documentation explicitly says payment refunds are not implemented.
- The return panel now requires loading the original invoice, lets the operator select only products on that invoice, displays sold/already-returned/remaining quantities, and blocks quantities above the displayed remaining amount before submission. Backend validation remains authoritative.
- `SaleReturn` stores sale/product/quantity/reason and monetary amounts, but the existence of fields is not proof that a complete refund/accounting workflow exists.
- Current app route guard `AdminGate` checks a session token in the frontend; this is not, by itself, proof of backend authorization.

## 6. Gaps still open before acceptance

1. Role policy: seller permissions for consultation, direct sale, return registration, and exceptional return approval. Current sale/return write APIs are admin-only.
2. Return financial contract: refund/credit handling, document status, audit trail, idempotency, and inventory movement verification.
3. Customer flow: confirm which operational token and identity model are intended for seller-side customer lookup and consultation.
4. Taxonomy: canonical mapping for SKIN/BOOST and the six requested gallery lines; do not change schema/migrations by assumption.
5. Indicators: define authoritative API and time window for today's sales, low stock, pending recommendations/returns. Hide metrics without reliable data.
6. Runtime verification: test login, role enforcement at API, consultation → recommendation → sale, original-sale return, partial/full return limits, stock effect, financial effect, and responsive tablet use. CI is not a substitute for these persisted-runtime checks.

## 7. Acceptance gates

- Every visible action navigates to a real implemented capability or is clearly disabled with a reason.
- Seller cannot access management-only actions through direct API calls.
- Recommendation UI never treats unknown/ineligible products as sellable recommendations.
- Return cannot be created without an original sale or above remaining sold quantity.
- Inventory and financial effects are verified from persisted state, not inferred from a success toast.
- Desktop and tablet flows are tested.
- Independent verification is recorded separately from implementation completion.

## 8. Next work

Next: wait for CI on the latest commit; resolve any failures; then run the application against an isolated test database and record real end-to-end evidence. Obtain an independent review and a product decision for seller permissions/refund semantics. Keep the six-line taxonomy and management indicators disabled until their contracts and runtime behavior are verified. Do not merge to master until tests, runtime evidence, product decisions, and independent review are complete.
