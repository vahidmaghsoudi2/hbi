# HBI Homepage — Single Source of Truth

> **Authority:** This is the only active homepage specification, work ledger, and no-repeat control. After this consolidation PR is merged, all homepage work must use this document. Issue [#352](https://github.com/vahidmaghsoudi2/hbi/issues/352) is the pointer/decision history, not a second execution plan. Older homepage documents and PRs are historical records only and must not be used to start or repeat work.

**Last reconciled:** 2026-10-22
**Baseline:** `master @ 8b29ea2de702a4e3ec9b015989ea92b412b9e61f`
**Authoritative implementation:** `frontend/src/pages/NewHomePage.tsx` at route `/` (protected by AdminGate)
**Merged homepage integration:** [PR #363](https://github.com/vahidmaghsoudi2/hbi/pull/363), merge commit `0463044d7b49b4847b70d388766484fce5504392`
**Single active workstream:** [PR #395](https://github.com/vahidmaghsoudi2/hbi/pull/395), branch `fix/homepage-single-source-of-truth` (OPEN / DRAFT, not merged). The current commit SHA is read from the PR itself so this ledger cannot become stale each time it is updated.
**Governance pointer:** [Issue #352](https://github.com/vahidmaghsoudi2/hbi/issues/352). It points here; it is not a second execution ledger. All current homepage execution status, prior-work inventory, evidence links, blockers, and next actions belong in this file and this PR only.

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
| HP-05 | Isolate Sales customer search results from Customers workflow | Confirmed on current `master` `NewHomePage.tsx` that Sales search still writes to shared `customerSearchResults`. The fix is now ported directly onto the current `master` source in the reconciled PR branch; the dedicated regression test is included. Exact-head HBI CI, Auto Tasks, and Pilot Browser Proof all passed on `b40773a777982c156f1df4367e52687bb70e75c0` on 2026-10-22. This verifies the targeted HP-05 change on that exact head; it does not authorize merge. | PORTED ON PR #395 HEAD `41a49520d72d51e8a60badb4223927dcae56543a` — exact-head HBI CI, Auto Tasks, and Pilot Browser Proof succeeded on 2026-10-22; focused HP-05 regression test passed. PR remains Draft/unmerged pending explicit PO authorization. |
| HP-06 | Local Windows runtime/database acceptance | Local frontend production build succeeded on `cff6845`; user launched the app. Menu click-through was already known to work and is not to be repeated absent a specific regression. No claim is made that real sales/database mutations were verified in this pass. | PARTIAL — do not repeat generic menu check |
| HP-07 | Anonymous direct sale contract | Current homepage submits `customer_id: saleCustomerId`, which can be null; the API/schema/runtime acceptance of a truly anonymous sale has not been established in this consolidation. Former PR #344 instead asks for a buyer name and creates a guest customer, which conflicts with the PO rule that customer association is optional. Do not port that old implementation; verify the current backend contract before changing it. | BACKEND CONTRACT VERIFIED IN SOURCE/UNIT TEST — endpoint-level runtime remains unverified |

## 5. Targeted follow-ups only

**HP-05: isolate Sales customer-picker search state.** On current master, `searchSaleCustomers()` uses the same `customerSearchResults` state as Customers history/search. That can leak results between two independent workflows. The targeted fix introduces `saleCustomerSearchResults` and uses it only in Sales. A focused regression test, `tests/test_home_sales_customer_search_isolation.py`, now asserts that Sales search writes only to its dedicated state and that the Sales and Customers pickers render their own result lists. Exact-head automated gate passed on `b40773a777982c156f1df4367e52687bb70e75c0`; PO merge authorization remains required.

Do not expand this into a general navigation rewrite. Do not rerun generic menu checks to validate this state-isolation fix.

**HP-07: anonymous direct sale.** The approved rule is that customer and consultation are both optional. The homepage currently passes the selected customer ID, including null when no customer is selected. The current backend contract explicitly accepts `customer_id: Optional[str] = None`; `Sale.customer_id` is nullable; `SaleService.create_sale` validates a customer only when one is supplied; and `tests/test_sales_workflow.py::test_direct_sale_without_customer` verifies a sale with `customer_id=None` while stock is deducted and a stock movement is recorded. The API contract is verified in source and service-level tests. Endpoint-level authenticated runtime acceptance is not claimed. The closed PR #344 remains invalid because it forces a name and creates a guest customer.

## 6. What is explicitly historical / superseded

The following were inspected and their useful current decisions have been reconciled into this file. They are not active specifications and must not be used to reopen completed work:

- `docs/HOMEPAGE_COMPLETION_LEDGER.md` — completion evidence migrated here.
- `docs/HOMEPAGE_IA_AUDIT_STAGE2.md` — route/ownership findings reconciled here; older claims that conflict with the current approved menu are superseded.
- `docs/HBI_HOME_OPERATIONAL_ROADMAP.md` — old phased plan superseded.
- `docs/HBI_HOME_PAGE_ARCHITECTURE_DECISION.md` — old ADR and next-action text superseded.
- Issues #290 and #175, and older homepage PR descriptions/comments — retained as GitHub history, not execution instructions.
- PRs #339, #347, #354 and #362 — historical/overlapping proposals superseded by merged PR #363; closed as superseded.
- PR #341 — its dashboard-summary concept is already represented by the current NewHomePage and its real report API calls; closed as superseded by merged PR #363.
- PR #344 — closed as superseded/incompatible: its proposed guest-customer creation and mandatory buyer name conflict with the approved optional-customer rule. HP-07 tracks the remaining API-contract evidence gap.
- PR #392 — its isolated customer-search fix has been ported into HP-05 here and the old-branch PR is closed; do not maintain a parallel fix branch.

GitHub issue/PR history cannot be erased without destroying audit traceability. Historical records may remain visible, but they must point to this single active document and must not be treated as competing plans.

### Historical homepage work inventory (discovered and reconciled 2026-10-21)

This is the index of earlier homepage-related work discovered through repository Issue/PR search. The historical GitHub records remain the audit trail; their old instructions are not current work plans. Use the completion ledger above for current status and only reopen an item for regression, changed code, new evidence, or explicit PO direction.

- **Original single-page / pilot UI lineage:** PRs [#4](https://github.com/vahidmaghsoudi2/hbi/pull/4), [#8](https://github.com/vahidmaghsoudi2/hbi/pull/8), [#9](https://github.com/vahidmaghsoudi2/hbi/pull/9), [#10](https://github.com/vahidmaghsoudi2/hbi/pull/10). Historical foundations; not a reason to restore obsolete layouts.
- **Home sales, customer reuse, pricing, FX, and frontend CI:** PRs [#132](https://github.com/vahidmaghsoudi2/hbi/pull/132), [#133](https://github.com/vahidmaghsoudi2/hbi/pull/133), [#134](https://github.com/vahidmaghsoudi2/hbi/pull/134), [#135](https://github.com/vahidmaghsoudi2/hbi/pull/135), [#136](https://github.com/vahidmaghsoudi2/hbi/pull/136), [#143](https://github.com/vahidmaghsoudi2/hbi/pull/143), [#152](https://github.com/vahidmaghsoudi2/hbi/pull/152), [#156](https://github.com/vahidmaghsoudi2/hbi/pull/156), [#176](https://github.com/vahidmaghsoudi2/hbi/pull/176), [#177](https://github.com/vahidmaghsoudi2/hbi/pull/177), [#207](https://github.com/vahidmaghsoudi2/hbi/pull/207). Historical functional changes and evidence; verify current code before relying on any old branch-level claims.
- **Product Intake and product entry from Home:** PR [#256](https://github.com/vahidmaghsoudi2/hbi/pull/256) (Draft semantics), [#282](https://github.com/vahidmaghsoudi2/hbi/pull/282) (Product Line V1, adjacent product governance), [#361](https://github.com/vahidmaghsoudi2/hbi/pull/361) (Products menu), [#363](https://github.com/vahidmaghsoudi2/hbi/pull/363) (merged Home/Products menu and API-backed dashboard), and [#375](https://github.com/vahidmaghsoudi2/hbi/pull/375) (local-session workflow, adjacent local-launch behavior). The New Home Page entry-point handoff and its verification are recorded in Issue #352 comments; do not repeat completed menu click-through checks.
- **Dashboard/navigation proposals superseded by merged PR #363:** [#328](https://github.com/vahidmaghsoudi2/hbi/pull/328) (public landing page is distinct from operational dashboard), [#330](https://github.com/vahidmaghsoudi2/hbi/pull/330) (sales/returns UI), [#339](https://github.com/vahidmaghsoudi2/hbi/pull/339), [#341](https://github.com/vahidmaghsoudi2/hbi/pull/341), [#343](https://github.com/vahidmaghsoudi2/hbi/pull/343) (temporary CI validation only), [#346](https://github.com/vahidmaghsoudi2/hbi/pull/346), [#347](https://github.com/vahidmaghsoudi2/hbi/pull/347), [#354](https://github.com/vahidmaghsoudi2/hbi/pull/354), [#362](https://github.com/vahidmaghsoudi2/hbi/pull/362). Treat as historical evidence or superseded proposals, not parallel active work.
- **Approved dashboard/navigation integration:** [PR #363](https://github.com/vahidmaghsoudi2/hbi/pull/363) merged on 2026-10-16; merge commit `0463044d7b49b4847b70d388766484fce5504392`. It is the actual merged implementation baseline, not a currently active branch.
- **Superseded direct-sale/customer requirement:** [PR #344](https://github.com/vahidmaghsoudi2/hbi/pull/344) conflicts with the approved rule that both customer and consultation are optional. Do not restore mandatory buyer-name or guest-customer creation.
- **Stale Sales customer-search repair:** [PR #392](https://github.com/vahidmaghsoudi2/hbi/pull/392) is superseded; its targeted state-isolation repair was ported to the current-master-based PR #395. Do not continue the stale branch.
- **Completion-ledger consolidation:** [PR #394](https://github.com/vahidmaghsoudi2/hbi/pull/394) is historical evidence for the prior completion ledger and post-PR-363 checks. Its useful records are incorporated into HP-01 through HP-04 above.
- **Current single active integration:** [PR #395](https://github.com/vahidmaghsoudi2/hbi/pull/395) is the only active homepage integration/ledger PR. It contains the single source-of-truth file, the narrowly scoped HP-05 fix, and its regression test. Current exact-head workflow status must be read from GitHub, not inferred from older PR results.
- **Older mission anchors:** Issues [#175](https://github.com/vahidmaghsoudi2/hbi/issues/175), [#290](https://github.com/vahidmaghsoudi2/hbi/issues/290), and this governance pointer [#352](https://github.com/vahidmaghsoudi2/hbi/issues/352) are historical/product-decision references. Do not resurrect old phase plans from their comments; current execution belongs here.

**Coverage note:** this inventory captures the homepage-specific and closely coupled Home/Product Intake PRs returned by the repository searches. It does not claim that every unrelated feature PR touching a shared component is a homepage project. The actual source code on current `master` remains the authority for runtime behavior.

## 7. No-repeat execution protocol

Before taking any homepage action:
1. Read this document and check only the items marked pending above.
2. Inspect the current `master` SHA and the single active consolidation PR/head.
3. Run the relevant test/build for the changed behavior only.
4. Update this ledger in the same PR with exact evidence and status.
5. Do not create another homepage branch, checklist, audit document, or roadmap.
6. Do not merge or modify `master` until the exact-head checks pass and the Product Owner explicitly authorizes the merge.

## 8. Homepage submenu and smart skincare intake handoff (2026-10-22)

The requested menu review was checked against `frontend/src/pages/NewHomePage.tsx`. The approved section navigation and its action cards already exist; do not rebuild them as a parallel navigation system. Existing Product Management actions include the managed product list, product intake/edit, and QA review. Products & Inventory owns inventory status, low-stock and stock movement; Purchasing owns physical purchase/Stock-In. Keep these responsibilities separate.

The current Product Intake panel already has a button labelled “تکمیل هوشمند اطلاعات”, implemented by `completeFromIntro()`. This is deterministic text/regex extraction, not an evidence-backed AI research or visual-recognition pipeline. It extracts a limited set of identity hints (brand/name, size/unit, SPF, variant and category), constructs a provisional product ID from some of those hints, defaults market region to IR, and leaves `product_line` for explicit operator selection. Every proposed value still requires operator review. Market/version ambiguity must not be inferred from similar names.

The current save path is governed: Product creation runs DuplicateCheck, then creates a DRAFT with `identity_status=NEEDS_REVIEW` and `qa_verdict=PENDING`; the associated Inventory row starts at quantity zero and `OUT_OF_STOCK`. A knowledge/evidence seed is explicitly UNKNOWN/PENDING, not trusted knowledge. Physical stock is added separately through the Purchasing page and the admin-only Stock-In endpoint, requiring positive quantity, purchase price and an explicit operational FX rate; it records a `STOCK_IN` StockMovement. Do not conflate smart field completion with physical stock receipt.

Product-entry integration status: [PR #429](https://github.com/vahidmaghsoudi2/hbi/pull/429) supplies the merged read-only exact-GTIN backend; [PR #431](https://github.com/vahidmaghsoudi2/hbi/pull/431) supplies the open, unmerged manual GTIN lookup UI follow-through. Camera scanning and JPG/PNG barcode extraction remain unimplemented. Identification must not auto-create, approve, activate, or mutate inventory.

The next permitted step is the read-only field-by-field audit required by [Issue #402](https://github.com/vahidmaghsoudi2/hbi/issues/402) under [roadmap #403](https://github.com/vahidmaghsoudi2/hbi/issues/403): map identity, ProductKnowledge/Evidence, safety/QA, and physical stock fields to their current UI/API/model/tests; mark each VERIFIED/PARTIAL/NOT VERIFIED/BLOCKED. Do not implement new smart-enrichment, schema, API, or inventory automation until that matrix and the relevant Work Package gate are resolved. Keep all homepage-related findings in this canonical ledger; do not create a parallel homepage tracker.

**Next action (2026-10-22):** PR #395 is reconciled to current master and the exact-head HBI CI, Auto Tasks, and Pilot Browser Proof succeeded on `41a49520d72d51e8a60badb4223927dcae56543a`; the focused HP-05 regression test passed. PR #395 remains OPEN / DRAFT / UNMERGED pending explicit Product Owner authorization. Homepage section actions already exist; do not rebuild generic navigation. Continue the bounded field-by-field smart skincare intake / Stock-In reality audit through existing Issues #402/#403, keeping product registration, evidence/QA, and physical stock receipt distinct. PR #429 provides merged read-only exact-GTIN lookup; PR #431's manual Intake UI follow-through is open/unmerged. Camera scanning and image barcode extraction remain unimplemented. No schema/API/inventory automation or merge is authorized until its explicit Work Package gate and PO approval. Do not create another homepage tracker, issue, PR, branch, or ledger.

## 9. Field-by-field reality audit — skincare intake and stock-in (2026-10-23)

**Audit boundary:** read-only review of current `master` models/services/UI. This is not authorization to change schema, API, lifecycle, evidence policy, or inventory behavior. Work remains governed by [Issue #402](https://github.com/vahidmaghsoudi2/hbi/issues/402) under [roadmap #403](https://github.com/vahidmaghsoudi2/hbi/issues/403).

| Domain / field group | Current source of truth | Status | Finding / acceptance requirement |
|---|---|---|---|
| Product identity | `app/models/product.py` | VERIFIED for persisted columns | Brand/name required; variant, size/unit, GTIN, market region, origin, packaging version and category are represented. Same-name products/market variants must not be silently collapsed. |
| Product lifecycle and QA | Product model + `ProductService.create_product_with_inventory()` | VERIFIED for create defaults | Create path enforces DuplicateCheck and operator-supplied `product_line`; new Product starts `DRAFT` / `PENDING`. Intake must not auto-approve or activate. |
| Smart completion | `frontend/src/pages/ProductIntakePanel.tsx`, `completeFromIntro()` | PARTIAL | Deterministic text/regex extraction only. Suggested values need operator review; not evidence-backed research, not visual product recognition, and not proof of formula/market version. |
| Product knowledge | `app/models/product_knowledge.py` | PARTIAL | Existing fields cover ingredients, ingredient roles, claimed benefits, use cases, contraindications, instructions, manufacturer claims, evidence refs/status and confidence. This is not yet proof that all desired structured product characteristics are captured or exposed in the intake UI/API. |
| Evidence provenance and review | `app/models/evidence.py`, `EvidenceService`, `ResearchDraftService` | VERIFIED for draft/review boundary | Research drafts require a claim, source type and source reference; they are stored as `PENDING` / `UNKNOWN` and excluded from rebuilt ProductKnowledge until QA is APPROVED/VERIFIED and conflict is absent. `FACT` claims are restricted to peer-reviewed, clinical-trial or regulatory source types. |
| Knowledge rebuild | `ProductKnowledgeService.update_from_evidence()` | VERIFIED for gate behavior; PARTIAL for field coverage | Only approved, non-conflicting Evidence populates knowledge. The current mapper handles a bounded set of fields; broader structured attributes require an authorized field/API/UI work package. Do not treat an evidence draft as approved knowledge. |
| Product category | `app/models/category.py` and Product.category_id | PARTIAL | Existing category codes are constrained to BOOST, HAIR, BEAUTY, TOOLS, PERFUME, OTHER. Do not rename category labels or alter category taxonomy in this work without explicit scope approval. |
| Initial Inventory row | `ProductService.create_product_with_inventory()`, `app/models/inventory.py` | VERIFIED for current behavior | Product creation creates an Inventory row with zero available quantity and `OUT_OF_STOCK`; product registration is not physical stock receipt. |
| Physical Stock-In | `app/api/routers/inventory.py`, `app/services/stock_in_service.py`, `frontend/src/pages/PurchasePage.tsx` | VERIFIED for current contract | Admin-only Stock-In requires an existing Product and Inventory row, positive integer quantity, nonnegative purchase price and explicit positive operational FX rate; it increments quantity and records `STOCK_IN` movement. Never invent FX or infer physical quantity from product creation. |
| Exact GTIN identification | PR #429 merged; PR #431 open/unmerged per current ledger | PARTIAL end-to-end | Backend exact lookup is read-only; UI follow-through is not merged. Camera scanning and JPG/PNG barcode extraction are not implemented. Verify exact-head checks for #431 before relying on its status. |

### Audit conclusion and next bounded action

The repository has enough existing primitives for a governed workflow: Product Master identity, evidence drafts and QA-gated knowledge rebuilding, plus a separate physical Stock-In ledger. The gap is **end-to-end field coverage and user workflow**, not a need for a parallel Product Master or an automatic inventory writer.

1. Keep existing homepage navigation and route users to the official Product Intake and Purchasing/Stock-In paths.
2. Before any implementation, complete the remaining UI/API/test mapping for the desired skincare fields and record which fields are absent, merely text-only, or not exposed.
3. Propose a bounded Work Package through existing #402/#403 governance before adding fields, APIs, image recognition, or automation.
4. Acceptance for a future smart-enrichment slice must include source reference per assertion, explicit UNKNOWN/CONFLICT handling, QA gate, persisted-and-retrievable values, duplicate checks, tests, and proof that no Inventory/StockMovement mutation occurs during identification/enrichment.
5. Acceptance for stock receipt must separately prove quantity and a STOCK_IN movement are persisted for the same Product/Inventory identity, with an explicit FX input and no duplicate stock-in side effects.
6. All homepage-related outcomes remain in this ledger and PR #395. No parallel homepage tracker, issue, PR, branch, or ledger is authorized.

