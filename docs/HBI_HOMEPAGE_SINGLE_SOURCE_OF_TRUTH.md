# HBI Homepage — Single Source of Truth

> **Authority:** This is the only active homepage specification, work ledger, and no-repeat control. After this consolidation PR is merged, all homepage work must use this document. Issue [#352](https://github.com/vahidmaghsoudi2/hbi/issues/352) is the pointer/decision history, not a second execution plan. Older homepage documents and PRs are historical records only and must not be used to start or repeat work.

**Last reconciled:** 2026-10-16  
**Baseline:** `master @ cff6845f78bb112af28847dbe1c6aa26b8264ec3`  
**Authoritative implementation:** `frontend/src/pages/NewHomePage.tsx` at route `/` (protected by AdminGate)  
**Merged homepage integration:** [PR #363](https://github.com/vahidmaghsoudi2/hbi/pull/363), merge commit `0463044d7b49b4847b70d388766484fce5504392`  
**Consolidation / outstanding targeted repair:** branch `fix/homepage-single-source-of-truth`; PR created from this branch will be the only active homepage implementation PR.

## 1. Non-negotiable operating rules

1. **One implementation:** New Home Page is authoritative. The legacy Home Page is obsolete; do not reopen, test, or modify it.
2. **One plan and ledger:** this file is the only active homepage plan, route/action inventory, completion ledger, and handoff. Do not create parallel homepage documents or duplicate audits.
3. **No repeat work:** do not revisit completed items unless new evidence demonstrates a regression, relevant code changed, or the Product Owner explicitly reopens the item.
4. **No unsupported claims:** code presence, green CI, browser tests, local runtime, PO acceptance, and merge are separate facts. Never treat one as proof of another.
5. **Branch discipline:** work on the single active consolidation branch/PR. Do not push directly to `master`; merge only after checks and PO authorization.
6. **No fake data/features:** dashboard values must come from authoritative APIs; unknown/error/empty states must remain explicit. No mock counts or invented financial metrics.
7. **Product model:** one system user only (Admin = Operator = Manager). Customers are records, not system users, and have no system access.
8. **Business boundaries:** Consultation and Sales are separate. Direct sale requires neither a consultation nor a customer. Product intake/QA is separate from physical purchase/stock-in.
9. **Product eligibility:** catalog visibility, QA approval, recommendation eligibility, and physical stock are distinct. Consultation product selection must respect the approved eligibility contract and positive stock requirement.
10. **Accounting:** keep sales/finance reports separate from inventory/stock-flow reports. Gross profit remains unavailable until the COGS policy and calculations are approved and verified.

## 2. Approved navigation and responsibilities

| Main area | Responsibility / included operations | Must not contain |
|---|---|---|
| Home / Dashboard | Quick actions first; real operational summary; actionable alerts; recent activity where backed by data | Full sales or consultation forms; invented Intake/QA counts |
| Customers | Search/list, create/update record, customer profile, available purchase/consultation history | Customer login or automatic consultation start on selection |
| Consultation | Start/history; customer reality → problem → valid need → eligible HBI Gallery product → recommendation/evidence → operator decision | Sales registration or “send recommendation to sale” shortcut |
| Sales | Direct sale, transaction details/history, sellable product selection, quantity/pricing/stock validation | Consultation prerequisite; mandatory customer; manual product-ID bypass |
| Product Management | Managed product list, product intake/edit, evidence completion, QA/review | Physical stock-in or accounting reports |
| Products & Inventory | Inventory status, low stock, stock movements/flow | Product knowledge intake/QA; purchase registration |
| Purchasing | Purchase and physical stock-in, purchase history/details | Product master/intake/QA lifecycle |
| Accounting & Reports | Supported sales and finance reports | Inventory/low-stock/stock-flow screens; unsupported profit claims |
| Fixed shell | Admin identity and logout | Fake Settings module or customer-facing system access |

The standalone `/catalog` entry is obsolete and redirects to the approved route. Do not recreate it without a new PO decision and evidence of a distinct use case.

## 3. Route and ownership baseline

| Route / component | Current responsibility | Rule |
|---|---|---|
| `/` → `NewHomePage` | Main menu and dashboard/operational sections | AdminGate; only authoritative homepage |
| `/login` | Admin login | Successful login enters the protected operational app |
| `/purchase` | Purchase / physical stock-in | Separate from product intake and direct sale |
| `/inventory` | Inventory, low-stock, stock-flow reports | Inventory/report ownership |
| `/accounting` | Sales and finance reports | Do not duplicate inventory reports here |
| `/catalog` | Legacy standalone catalog entry | Redirect; do not restore as a parallel main-menu destination |
| Product Intake / QA panels | Product Management-owned lifecycle | Do not alter lifecycle internals in homepage-only work without coordination |
| `/pilot`, `/recommendation` | Legacy/pilot routes with separate pilot-token dependencies | Do not advertise as normal Admin workflow unless the API/session contract is verified |

## 4. Completion ledger

| ID | Item | Evidence | Status |
|---|---|---|---|
| HP-01 | CI and browser evidence for merged homepage implementation | [CI 38872575903](https://github.com/actions/runs/38872575903), [browser proof 38872575898](https://github.com/actions/runs/38872575898), [auto evidence 38872575900](https://github.com/actions/runs/38872575900), final PR head `1b53fb7890e7671f404b33cdd857e26e1da34632` | COMPLETE — VERIFIED |
| HP-02 | Remove standalone catalog entry and redirect obsolete `/catalog` route | Commit `e16cccfc0d338d4ea61cca6a8648bc15dc34241d`; [CI](https://github.com/actions/runs/38868660433), [browser proof](https://github.com/actions/runs/38868660269) | COMPLETE — VERIFIED |
| HP-03 | Remove placeholder Settings and put Admin logout in fixed header | Commit `dd5648cec489f5e56be293720157be87ae2b49dd`; final browser proof on `1b53fb7890e7671f404b33cdd857e26e1da34632` | COMPLETE — VERIFIED |
| HP-04 | Reconcile and merge homepage integration | [PR #363](https://github.com/vahidmaghsoudi2/hbi/pull/363), merge `0463044d7b49b4847b70d388766484fce5504392` | MERGED |
| HP-05 | Isolate Sales customer search results from Customers workflow | Confirmed on master `NewHomePage.tsx` that Sales search still writes to the shared `customerSearchResults`; previous draft [PR #392](https://github.com/vahidmaghsoudi2/hbi/pull/392) contains the targeted fix but is based on an old Stage 2 branch. Fix has been ported to this consolidation branch. | IMPLEMENTED IN THIS BRANCH — CI/targeted verification PENDING |
| HP-06 | Local Windows runtime/database acceptance | Local frontend production build succeeded on `cff6845`; user launched the app. Menu click-through was already known to work and is not to be repeated absent a specific regression. No claim is made that real sales/database mutations were verified in this pass. | PARTIAL — do not repeat generic menu check |

## 5. The only currently identified code follow-up

**HP-05: isolate Sales customer-picker search state.** On current master, `searchSaleCustomers()` uses the same `customerSearchResults` state as Customers history/search. That can leak results between two independent workflows. The targeted fix introduces `saleCustomerSearchResults` and uses it only in Sales. It is included on the consolidation branch; exact-branch CI and appropriate test evidence are still required before acceptance.

Do not expand this into a general navigation rewrite. Do not rerun generic menu checks to validate this state-isolation fix.

## 6. What is explicitly historical / superseded

The following were inspected and their useful current decisions have been reconciled into this file. They are not active specifications and must not be used to reopen completed work:

- `docs/HOMEPAGE_COMPLETION_LEDGER.md` — completion evidence migrated here.
- `docs/HOMEPAGE_IA_AUDIT_STAGE2.md` — route/ownership findings reconciled here; older claims that conflict with the current approved menu are superseded.
- `docs/HBI_HOME_OPERATIONAL_ROADMAP.md` — old phased plan superseded.
- `docs/HBI_HOME_PAGE_ARCHITECTURE_DECISION.md` — old ADR and next-action text superseded.
- Issues #290 and #175, and older homepage PR descriptions/comments — retained as GitHub history, not execution instructions.
- PRs #339, #347, #354 and #362 — historical/overlapping proposals superseded by merged PR #363; close them as superseded rather than treating them as parallel workstreams.
- PR #392 — its isolated customer-search fix is being consolidated into HP-05 here; do not maintain a parallel fix branch after this PR is verified.

GitHub issue/PR history cannot be erased without destroying audit traceability. Historical records may remain visible, but they must point to this single active document and must not be treated as competing plans.

## 7. No-repeat execution protocol

Before taking any homepage action:
1. Read this document and check only the items marked pending above.
2. Inspect the current `master` SHA and the single active consolidation PR/head.
3. Run the relevant test/build for the changed behavior only.
4. Update this ledger in the same PR with exact evidence and status.
5. Do not create another homepage branch, checklist, audit document, or roadmap.
6. Do not merge or modify `master` until the exact-head checks pass and the Product Owner explicitly authorizes the merge.

**Next action:** complete exact-head CI and targeted verification for HP-05, then close superseded homepage PRs and make this document the sole active homepage source. No generic menu re-audit.
