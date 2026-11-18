# HBI OPERATIONAL REALITY AUDIT v1 — Seller to Accounting

## Baseline
- Repository: `vahidmaghsoudi2/hbi`
- Master: `e110d2c46dfa966009118a0aee6d040ee932ea28`
- Scope: operational store workflow from customer arrival through accounting and follow-up
- Production code changes: **NONE**
- Implementation: **NOT AUTHORIZED**

## 1. End-to-End Workflow

```
Customer arrives
  ↓
Customer lookup / guest or existing customer
  ↓
Customer + consent
  ↓
Case / current consultation input
  ↓
Recommendation context
  ├─ current consultation
  ├─ ProfileFact when consent permits
  └─ additive OutcomeAssessment history
  ↓
Need normalization
  ↓
Catalog eligibility
  ├─ Product ACTIVE
  ├─ identity VERIFIED
  ├─ QA VALID
  ├─ stock > 0
  └─ Evidence / ProductKnowledge / Reasoning gates
  ↓
Eligible Recommendation(s)
  ↓
Seller/customer product selection
  ↓
Sale
  ├─ ACTIVE product
  ├─ sufficient sellable stock
  ├─ authoritative Inventory sale price
  ├─ supplied FX rate
  └─ optional Recommendation linkage
  ↓
SaleItem + StockMovement
  ↓
Accounting / payment records
  ↓
Feedback / Outcome / Follow-up / Outcome Assessment
```

### Critical reality

The Recommendation → Sale bridge exists through `SaleItem.recommendation_id`.

A sale may also be created without a recommendation link. Therefore the system supports both:
- recommendation-originated sale trace;
- direct product sale.

The Sale layer does not itself prove product success or consultation outcome.

---

## 2. Role Matrix

| Role | Current responsibility | Reality |
|---|---|---|
| Customer | own identity, consultation input, customer response, follow-up, outcome assessment | **PROVEN** |
| Seller / Operator | operational customer lookup, consultation, recommendation viewing, product selection/sale support | **PARTIAL** |
| Manager | operational control | **PARTIAL / role surface depends on Admin/Editor permissions** |
| QA | Product identity/QA/evidence governance | **PROVEN in catalog governance; not a distinct store-floor workflow** |
| Accountant / Admin | sale/financial mutation, inventory financial control, void | **PROVEN** |
| System | context projection, recommendation, eligibility, inventory/accounting calculations, audit events | **PROVEN** |

### Important role reality

There is no single distinct `SELLER` / `MANAGER` / `ACCOUNTANT` operational role model covering every store action.

Financial mutation ownership is explicitly Admin in the current accounting contract.

Inventory read for operational selling is available to Admin/Editor, while inventory mutation is Admin-controlled.

---

## 3. Data Ownership

### Customer

Authoritative customer identity and legacy profile fields:

```
Customer
  ├─ customer_id
  ├─ name / mobile
  ├─ consent
  └─ legacy profile/context fields
```

### Case

Authoritative consultation container:

```
Case
  ├─ customer_id
  ├─ current consultation context
  ├─ identified_needs [model field; not runtime Need SoT]
  └─ evidence_gaps    [model field; not runtime Need SoT]
```

### ProfileFact

Longitudinal customer facts with lifecycle and MutationLog.

### Recommendation

Case-scoped decision artifact, with:
- product_id
- eligibility
- ranking score/reasons
- evidence refs
- warnings

Only eligible recommendations are persisted by the current generation path.

### Product / ProductKnowledge / Evidence

Catalog-side product truth and evidence.

### Inventory

Operational stock and authoritative sale price source.

### Sale / SaleItem

Financial transaction and product-level sale trace.

### Feedback / FollowUp / OutcomeAssessment

Post-consultation response and observed-result chain.

---

## 4. Duplicate Entry Points

### Confirmed duplicate-entry risks

#### A. Customer context
The same conceptual information can exist in:
- current Case consultation input;
- legacy Customer fields;
- ProfileFact.

Precedence exists for recommendation context, but this is still a multi-surface data model.

#### B. Product identity
Product identity information is distributed across Product fields and Evidence/ProductKnowledge references.

Duplicate Product detection is a known GAP/G1 mission.

#### C. Sale amount
Sale has historical/legacy Toman fields plus authoritative USD/FX/IRR fields.

This is governed, but increases reconciliation surface.

#### D. Follow-up metadata
Feedback retains `follow_up_at`, while FollowUp is now authoritative for lifecycle.

This is intentionally retained for compatibility but remains a dual-surface representation.

#### E. Product usage / outcome
OutcomeAssessment is explicit, while Feedback.outcome and FollowUp.status remain separate concepts.

The distinction is correct; the operator must not interpret one as another.

---

## 5. Failure Points

| Point | Failure / stop condition |
|---|---|
| Customer creation | validation / duplicate identity constraints / authorization |
| Case | ownership failure or missing Case |
| Recommendation | insufficient Need, medical context, product conflict/unknown, no eligible product |
| Product | inactive / identity not verified / QA not valid |
| Inventory | missing inventory / zero sellable stock |
| Sale | customer missing, product inactive, insufficient stock, missing sale price, invalid recommendation link, invalid FX |
| Payment/accounting | financial mutation permissions / validation |
| Sale cancellation | ACTIVE → VOIDED only; physical deletion prohibited |
| Follow-up | invalid ownership / terminal-state mutation |
| Outcome Assessment | ownership / cross-case trace / incomplete required context |
| Evidence | evidence governance/readiness can block recommendation |

### Operational reality

There is no single universal “stop reason” surface for the seller across all these stages. Stop reasons exist in their respective services/DTOs, but are not yet a unified Store Workflow state machine.

---

## 6. Audit Points

### Strong / proven

- Product lifecycle mutations
- Identity / QA changes
- ProfileFact lifecycle
- Sale VOID
- Stock movements
- Recommendation generation/feedback/follow-up API audit events
- Outcome Assessment create/audit
- Follow-up lifecycle audit

### Partial

- Evidence mutation audit parity
- A single end-to-end transaction trace visible to the seller/manager
- Unified customer → case → recommendation → sale → outcome timeline

---

## 7. Permission Points

| Operation | Current authority |
|---|---|
| Customer-owned Case / Recommendation | authenticated customer + ownership |
| ProfileFact mutation | authenticated customer / lifecycle controls |
| Product governance | governed operator/QA/Admin paths |
| Inventory mutation | Admin |
| Operational inventory product read | Admin / Editor |
| Sale creation | Admin |
| Sale void | Admin-owned financial mutation |
| Follow-up | authenticated customer / owned Case |
| Outcome Assessment | authenticated customer / owned Case |
| Recommendation generation | authenticated customer / owned Case |

### Main finding

The current runtime is strongly **customer-ownership oriented** in consultation APIs, while store-floor operations are **Admin/Editor oriented**.

That creates a role-boundary gap for a real seller workstation: the domain has the pieces, but the entire store workflow is not represented as one seller-operated authorization model.

---

## 8. Accounting Touchpoints

Current operational chain:

```
Product
  ↓
Inventory
  ↓
Inventory.sale_price_usd
  ↓
SaleService
  ├─ caller-supplied FX
  ├─ price snapshot
  ├─ Sale
  ├─ SaleItem
  └─ StockMovement(SALE)
  ↓
Payment / accounting records
```

### Confirmed Accounting V1 reality

- Currency of record: USD
- Final accounting amount: IRR
- Toman is derived/display-compatible
- FX is caller supplied; never invented
- Sale is durable financial history
- Cancellation uses `VOIDED`
- Sale physical deletion is not the correction mechanism
- Financial mutation ownership = ADMIN
- Stock movement is linked to the Sale

### Important bridge

`SaleItem.recommendation_id` provides the durable bridge:

```
Case
 ↓
Recommendation
 ↓
SaleItem
 ↓
Sale
```

This is a strong traceability point.

---

## 9. Customer Follow-up

Current post-sale / post-consultation path:

```
Recommendation
   ↓
Customer Response / Feedback
   ↓
FollowUp
   ↓
COMPLETED / CANCELLED
   ↓
OutcomeAssessment
```

### Reality

- FollowUp is a first-class durable lifecycle.
- It is not automatically created after sale/recommendation.
- There is no scheduler/reminder/background automation in this slice.
- Completion of FollowUp does not mean product success.
- OutcomeAssessment explicitly records observed/customer-reported result.
- OutcomeAssessment can link to Case, Recommendation, Feedback, FollowUp and Product.
- Product Usage is not an independent subsystem.

---

## 10. Required Scenarios

| Scenario | Reality |
|---|---|
| New Customer | **PROVEN**: guest/customer registration path exists; Case/current consultation can follow |
| Existing Customer | **PROVEN**: lookup/owned customer context and prior sales/history exist |
| Product unavailable | **PROVEN**: inventory gates recommendation and sale |
| Product not eligible | **PROVEN**: Recommendation eligibility gates persistence; sale only accepts linked ELIGIBLE recommendation |
| Recommendation available | **PROVEN** |
| Customer rejects recommendation | **PROVEN** via Customer Feedback outcome REJECTED |
| Sale completed | **PROVEN** |
| Sale cancelled | **PROVEN** as VOIDED financial document, not physical deletion |
| Inventory changed | **PROVEN** via stock-in/adjustment/stock movement |
| Follow-up required | **PROVEN** via explicit Feedback/FOLLOW_UP_NEEDED + first-class FollowUp creation; no automatic lifecycle bridge |

---

## 11. Where Human Decision Remains

The system automates evidence-based gating and recommendation, but the seller/customer still decides:

- whether to select a recommended product;
- whether to buy;
- whether to reject a recommendation;
- whether to schedule follow-up;
- whether and how to record an observed result.

The system does not automatically convert Recommendation into Sale.

That is a feature of the current boundary, not a missing automatic transaction.

---

## 12. Recommendation → Sale Disconnection

The bridge is **present but optional**.

```
Recommendation
     │
     ├── selected → SaleItem.recommendation_id → Sale
     │
     └── not selected → no sale link
```

Therefore:

- traceable when recommendation is selected;
- no guarantee that every sale originated from Recommendation;
- no automatic purchase conversion;
- no automatic Outcome from Sale.

This is consistent with the current architecture.

---

## 13. Confirmed Gaps

### GAP-O1 — Unified Seller Workflow

**Classification: UX GAP + CONTRACT GAP**

The system contains the required services, but there is no single durable operational workflow contract representing:

```
Customer
→ Consultation
→ Recommendation
→ Selection
→ Sale
→ Accounting
→ Follow-up
```

as one seller-facing transaction.

### GAP-O2 — Role Model Alignment

**Classification: CONTRACT GAP**

Customer-owned APIs and Admin/Editor store operations coexist, but a clean Seller/Manager/QA/Accountant responsibility matrix is not represented as one unified runtime role model.

### GAP-O3 — Unified End-to-End Audit Timeline

**Classification: IMPLEMENTATION GAP**

Individual audit mechanisms exist, but a single timeline joining:

```
Customer → Case → Recommendation → Sale → Inventory → FollowUp → Outcome
```

is not established.

### GAP-O4 — Evidence Audit Parity

**Classification: IMPLEMENTATION GAP**

Previously confirmed in the Product Catalog audit.

### GAP-O5 — Duplicate Product Detection

**Classification: IMPLEMENTATION GAP**

Previously confirmed G1 / #258.

### GAP-O6 — Research Draft

**Classification: IMPLEMENTATION GAP**

Previously confirmed Product Catalog gap.

### GAP-O7 — Automatic Follow-up Handoff

**Classification: CONTRACT GAP**

Current architecture deliberately requires explicit FollowUp creation. Whether sale/recommendation/customer response should automatically create a FollowUp is not authorized and requires a separate contract decision.

### GAP-O8 — Unified Seller Explanation

**Classification: UX GAP**

Recommendation has rationale, evidence refs and warnings, but there is not yet one stable seller-facing explanation package.

---

## 14. Priority

| Priority | Mission | Reason |
|---|---|---|
| P1 | Seller Operational Workflow Contract | establishes the real store-floor boundary before UI automation |
| P2 | Unified Seller Explanation | reduces manual interpretation at Recommendation stage |
| P3 | End-to-End Audit Timeline | connects already-existing audit fragments |
| P4 | Role / Permission Contract | resolves seller vs Admin vs QA vs Accountant boundary |
| P5 | Duplicate Detection G1 | protects Product Master integrity |
| P6 | Research Draft / Evidence Enrichment | completes Intake → Evidence path |
| P7 | Follow-up handoff contract | decide whether/when explicit events create follow-up |
| P8 | Budget / preference | business decision, not current technical blocker |

---

## 15. Final Conclusion

### What HBI can already do

The current Master supports the core store transaction chain:

```
Customer
→ Case / Consultation
→ Recommendation
→ Product Selection
→ Sale
→ Inventory movement
→ Accounting
→ Feedback / FollowUp / OutcomeAssessment
```

The important bridges are real:

- Recommendation → SaleItem
- SaleItem → Product
- Sale → Customer
- Sale → StockMovement
- Case → Recommendation
- Recommendation → Feedback
- Feedback → FollowUp
- FollowUp → OutcomeAssessment

### What is not yet one operational system

The pieces are connected technically, but not yet represented as one unified **Seller Operational Workflow**.

The largest remaining operational problem is therefore not “build another sales module.”

It is:

```
UNIFY THE EXISTING REALITY
      ↓
Seller Workflow Contract
      ↓
Role / Permission Boundary
      ↓
Seller Explanation
      ↓
End-to-End Audit Timeline
```

This should precede broad store-floor automation.

## Gate

```
HBI OPERATIONAL REALITY AUDIT v1
STATUS: COMPLETE
PRODUCTION CODE CHANGED: NO
IMPLEMENTATION AUTHORIZED: NO
BASELINE: e110d2c46dfa966009118a0aee6d040ee932ea28
```
