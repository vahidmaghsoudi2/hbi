# HBI — PRODUCT INTAKE CONTRACT v1

**Contract ID:** HBI-PI-CONTRACT-001  
**Version:** V1.0-DRAFT  
**Status:** DRAFT — PENDING PO ACCEPTANCE  
**Baseline HEAD:** `42cc77ec5f8692407df58bb4be9d8a71fc93c52f`  
**Repository:** `vahidmaghsoudi2/hbi` @ `master`  
**Owner:** Product Owner  
**Drafted:** 2026-09-07  
**Implementation authorized by this document:** NO

---

## 0. AUTHORITY AND HIERARCHY

This is the operational contract for Product Intake (WHAT enters HBI and WHERE it sits).

Document order:

1. `docs/01_project_control/PROJECT_RULES.md`
2. `docs/01_project_control/PRODUCT_INTAKE_STRATEGY_AND_GOVERNANCE.md` (strategic parent)
3. `docs/P4_PRODUCT_INTAKE_GOVERNANCE_CONTRACT_V1.md` (governance mutation machine — PO APPROVED, LOCKED)
4. **this Contract** (operational intake path)
5. Live Ledger / Roadmap (execution position)

If this draft conflicts with P4 lifecycle, roles, or PATCH rules: **P4 wins**.  
If this draft conflicts with Strategy business rules (ONE PRODUCT MASTER, AI does not approve, PO is final approver): **Strategy wins** and the conflict must return to PO.  
This draft does not rewrite P4 and does not authorize rebuild of existing Product / Home / Intake UI.

**This file is not accepted until the Product Owner explicitly marks Status = PO ACCEPTED.**  
Until that mark: no Product Intake implementation, no new lifecycle, no parallel Approve API.

---

## 1. PURPOSE

Define the operational path:

> one real commercial item → one HBI `product_id` → research/enrichment without invented facts → human approval through P4 → governed Product Master used by all modules.

This contract converts Strategy into implementable boundaries **on top of existing repository capability at HEAD `42cc77ec`**.

---

## 2. RELATIONSHIP TO P4 (LOCKED)

P4 is the only V1 machine for Product governance mutation.

Inherited and **not reopenable by this contract**:

| Topic | Binding rule |
|---|---|
| Lifecycle vocabulary | DRAFT, SUBMITTED, QA_REVIEW, APPROVED, ACTIVE, REJECTED, ARCHIVED |
| Happy path | DRAFT → SUBMITTED → QA_REVIEW → APPROVED → ACTIVE |
| Reject | QA_REVIEW → REJECTED |
| Archive | ACTIVE → ARCHIVED |
| Create | server sets DRAFT / identity NEEDS_REVIEW / qa PENDING; client cannot inject governance |
| Generic PATCH | must not change `status`, `identity_status`, `qa_verdict` |
| Approve / Activate / Archive | PO only, via transition endpoints |
| QA / identity verify / reject | Reviewer-QA or PO, via transition endpoints |
| History V1 | append-only `ProductMutationLog` |
| Evidence readiness | gating condition for Approve and Activate |

**Mapping of Strategy stages onto P4 states:**

| Intake stage (Strategy) | P4 state / action |
|---|---|
| INTRODUCE | `POST /products` → DRAFT |
| IDENTITY / DUPLICATE CHECK | occurs at or before DRAFT; does not create a new P4 state |
| RESEARCH / ENRICH | work against DRAFT (and after Submit, against SUBMITTED/QA_REVIEW); writes Evidence/Knowledge, not governance fields |
| VALIDATE | QA_REVIEW |
| PO REVIEW | inspect/edit informational fields + P4 identity/QA transitions |
| APPROVE | P4 `approve` → APPROVED |
| REGISTER / ACTIVATE | P4 `activate` → ACTIVE = operational Product Master |
| CONTINUOUS UPDATE | informational PATCH and/or new Evidence/Knowledge; identity/safety/evidence-critical changes require re-entry to governed transitions |

**Forbidden:** a second approval state machine, a second Product Master, or treating UI «تأیید نهایی و ذخیره» as P4 Approve.

Creating a database row = **Introduce**.  
P4 Approve + Activate = **Product Master registration**.

---

## 3. DOMAIN SEPARATION (MANDATORY)

These domains must not be silently merged.

| Domain | What it is | What it is not |
|---|---|---|
| User Input | what the introducer typed or selected | not Research, not Approval |
| Product Master (identity/commercial) | governed Product row: `product_id`, brand, name, size, barcode, region, packaging | not Research Draft |
| Research Draft | structured AI output, source-traceable, editable | not Product status, not PO approval |
| Evidence | attached records on `product_id` with QA/conflict/status | not automatic Product QA |
| Product Knowledge | structured knowledge bound to `product_id` | not manufacturer marketing copy copied as fact |
| Approval data | P4 actor, timestamp, from/to, reason on mutation log | not a checkbox on create |

UI may simplify labels. Persistence and APIs must keep the distinction.

---

## 4. EXISTING ASSETS — DO NOT REBUILD

At HEAD `42cc77ec` the following are baseline and must be reused or extended:

- Product model, repository, service, transition service, mutation log
- Product API including P4 transition routes
- Evidence model and ProductKnowledge model
- Inventory / Sales / Accounting / Recommendation relations on the same `product_id`
- Seeded Product A–D (protected)
- `frontend/src/pages/NewHomePage.tsx`
- `frontend/src/pages/ProductIntakePanel.tsx`

Greenfield Home, Gallery, Catalog, Intake panel, Product Master, or TransitionService is **out of scope forever unless PO reopens**.

Known consumer gap (not a missing P4 machine): Intake UI still sends `status` / `identity_status` / `qa_verdict` and defaults to ACTIVE/VERIFIED. After **this contract is accepted**, the first implementation unit may align that consumer with P4. That unit is not authorization for Research implementation.

---

## 5. PRODUCT DEFINITION (BUSINESS RULE — LOCKED)

Any item independently purchased, stocked, and sold is an independent Product with its own `product_id`.

Tinted vs non-tinted of the same line, if stocked/sold separately, are two Products.

`product_id` is the HBI identity. GTIN/SKU/barcode are attributes, not substitutes.

Technical Product/Variant/SKU model remains **OPEN** (must not block V1 introduce/approve).

---

## 6. USER INPUT — INTRODUCE

### 6.1 Minimum to create DRAFT (must match existing Product create)

Required:

- `product_id`
- `brand`
- `product_name`

Optional (existing model; do not invent extra required columns in V1):

- `variant`
- `size_value` / `size_unit`
- `barcode_gtin`
- `market_region`
- `packaging_version`

Free-text introduction (as already used by the panel) is allowed as a **helper to fill User Input**. It is not Research Draft and must not invent medical claims.

### 6.2 Forbidden on create/update from Intake UI

Client must not send:

- `status`
- `identity_status`
- `qa_verdict`

Server remains source of create defaults (DRAFT / NEEDS_REVIEW / PENDING).

### 6.3 Incomplete introduce

A product may be created DRAFT with partial identity. Incomplete data must not by itself stop unrelated operations on **already ACTIVE** products. Mechanism for selling a DRAFT/provisional item remains **OPEN** (shadow/provisional). V1 default: operational Recommendation/trusted Knowledge consume ACTIVE Product Master, not DRAFT.

---

## 7. DUPLICATE CHECK

Before a **new** `product_id` is treated as a distinct Product Master, Intake must be able to return one of:

| Result | Meaning | V1 action |
|---|---|---|
| `NEW` | no credible existing match | allow DRAFT create |
| `POSSIBLE_MATCH` | human must review candidates | do not silently create a second master |
| `EXISTING` | same business product | reuse existing `product_id`; do not create a duplicate |

Exact matching algorithm, weights, and GTIN/name/size rules remain **OPEN**.  
Implementation of the detector is **not authorized** until this contract is PO-accepted **and** a later technical design chooses the algorithm.

Gate G1 (Identity) passes only when this result is produced and reviewed where not `NEW`.

---

## 8. AI RESEARCH

### 8.1 Authority

AI may research, collect, compare, structure, and flag UNKNOWN/CONFLICT.  
AI must not:

- approve or activate a Product
- change P4 governance fields
- invent missing facts
- convert inference into FACT
- silently resolve CONFLICT

### 8.2 Input to research

- User Input on the Product
- package/label text or photos when supplied (storage mechanism OPEN if not already in model)
- existing Evidence/Knowledge for that `product_id`
- external sources, classified by source governance (taxonomy detail OPEN)

### 8.3 Output — Research Draft (not Product row)

The draft must be able to carry, as **data-not-invented** slots (empty = UNKNOWN, not guessed):

Identity, Composition (INCI when available), Functional information, Suitability, Safety, Usage, Evidence references, Commercial information (kept distinct from clinical evidence).

Each non-empty assertion must be classifiable as:

`FACT` | `MANUFACTURER_CLAIM` | `EVIDENCE` | `INFERENCE` | `UNKNOWN` | `CONFLICT`

### 8.4 Persistence boundary

Research Draft is not a P4 status.  
V1 persistence: reuse Evidence and ProductKnowledge bound to `product_id` where they already exist; do not invent a second product identity.  
A dedicated research-dossier table is **OPEN** and not required to accept this contract.

### 8.5 Research tier / cost / model selection

**OPEN.** Not needed for Contract acceptance.

---

## 9. EVIDENCE AND KNOWLEDGE

- Evidence attaches to `product_id`.
- Evidence QA ≠ Product QA (P4 §7).
- Product Approve/Activate remain gated by Evidence readiness (P4 §8).
- Physical silent delete of Evidence that participated in approval is forbidden (P4 §15).
- Knowledge enrichment writes Knowledge, not `status`.

**Known V1 gap (do not pretend closed):** Evidence API role/audit is not yet at the same enforcement level as Product mutation. Closing it is a P4 remainder / separate WP, not a new Intake lifecycle.

---

## 10. VALIDATION AND CONFLICT

Validation must make visible:

- missing required identity for activation
- UNKNOWN slots
- CONFLICT slots
- Evidence not ready
- QA verdict not VALID where P4 requires it

Conflicts are not auto-resolved. PO or QA resolves through governed actions with reason.

---

## 11. PO REVIEW AND APPROVAL

PO may inspect the Product, User Input, Research Draft, Evidence, Knowledge, UNKNOWN, and CONFLICT.

PO may edit informational Product fields through existing update (non-governance).

Approval path is only:

1. identity verification transition as required by P4
2. QA path to VALID where required
3. Evidence readiness true
4. `approve` → APPROVED
5. `activate` → ACTIVE

Reject requires reason (P4 §12).

No Intake-specific approve endpoint will be designed.

---

## 12. REGISTRATION / INTEGRATION

ACTIVE Product is the governed Product Master.

Downstream modules (Inventory, Sales, Accounting, Knowledge, Evidence, Recommendation) already key on `product_id`. V1 must not create a competing key.

Inventory row created at Product create is **existing behavior**, not a new business rule. Default inventory policy for DRAFT vs ACTIVE remains **OPEN**; this contract does not change Accounting or Inventory policy.

---

## 13. UPDATE AFTER ACTIVE

Informational corrections: existing Product update + mutation log.  
Identity, safety, evidence, or recommendation-critical knowledge: stronger path — re-verify / QA / PO as applicable. Exact trigger matrix remains **OPEN** for a later QA policy; V1 minimum: do not use generic PATCH for governance fields.

History V1 = existing mutation log. Complex version-control schema remains **OPEN** and is not required.

---

## 14. ERROR BEHAVIOUR

| Situation | Required behaviour |
|---|---|
| Client injects governance fields | reject (schema 422 / equivalent); do not coerce |
| Invalid P4 transition | reject; no partial state write |
| Unauthenticated / unauthorized mutation | 401 / 403 |
| Duplicate `EXISTING` ignored | forbidden once detector is implemented |
| Invented medical/safety fact | forbidden; mark UNKNOWN |
| Silent conflict resolution | forbidden |

---

## 15. AUDIT

Product create, edit, submit, QA, identity, approve, reject, activate, archive: existing Product mutation log (P4 §13–§14).

Research assertions should retain source/class when implemented; dedicated research audit store is **OPEN**.

---

## 16. PROTECTED AND FROZEN

Protected:

- Product A–D identities and downstream references
- P4 services, schemas, and tests

Frozen / out of this workstream:

- Accounting V1
- P3 unaccepted functionality
- Recommendation scoring redesign
- Frontend rebuild

---

## 17. ROLES (REUSE P4 — NO NEW ROLES)

| Role | Intake-relevant authority |
|---|---|
| Editor | informational edit; introduce DRAFT (subject to P4 submit matrix) |
| Reviewer / QA | QA, identity verify, reject |
| PO | approve, activate, archive, exceptions |
| Admin | technical only; not Product governance |
| AI Research Agent | research draft only |

---

## 18. DECISION REGISTER

### LOCKED by Strategy or P4 (this contract restates, does not reopen)

- ONE PRODUCT MASTER / same `product_id`
- independently sold item = independent Product
- AI does not approve; PO does
- source traceability direction
- editable after registration
- P4 lifecycle, roles, PATCH denylist, create DRAFT, mutation log
- save row ≠ Product Master approval
- no greenfield Intake rebuild

### OPEN (must stay OPEN until PO decides)

- duplicate matching algorithm
- source-tier taxonomy detail
- AI research tier/cost/model
- Product/Variant/SKU technical model
- provisional/shadow operational mechanism
- dedicated research-dossier schema
- re-validation trigger matrix beyond V1 minimum
- complex history/version schema beyond mutation log
- default inventory behaviour for non-ACTIVE products

No implementer may silently close an OPEN item.

---

## 19. ACCEPTANCE GATES (UNCHANGED MEANING)

| Gate | V1 meaning |
|---|---|
| G1 Identity | duplicate result NEW / POSSIBLE_MATCH / EXISTING is produced and reviewed |
| G2 Research | source-traceable Research Draft without invented facts |
| G3 Validation | UNKNOWN/CONFLICT/missing/evidence unreadiness visible |
| G4 Human Review | PO can inspect and edit |
| G5 Approval | only P4 approve/activate |
| G6 Integration | downstream still uses same `product_id` |
| G7 Maintenance | updates leave mutation history |
| G8 Pilot | real products, no duplicate masters, A–D unharmed |

None of G1–G8 is passed by publication of this draft.

---

## 20. WHAT HAPPENS AFTER PO ACCEPTANCE

When Status on this file becomes **PO ACCEPTED**:

1. Technical Design for the **next implementation unit** (default candidate: align existing Intake UI/API client with P4 — stop governance injection; map «ذخیره» to create DRAFT and «تصویب» to P4 approve).
2. Only then: implementation of that unit, tests, evidence, Ledger update.
3. AI Research implementation remains a later phase (Roadmap Phase 2) and needs its own design after this contract.

Until PO ACCEPTED:

**NO implementation. NO Product A–D change. NO P4 rebuild. NO parallel workflow.**

---

## 21. CHANGE CONTROL

Changes to LOCKED items require PO decision + version bump.  
OPEN items may be closed only by PO.  
P4 contract changes follow P4 §22, not this file.

---

## 22. PO ACCEPTANCE BLOCK (TO BE SIGNED)

- [ ] I accept this Contract v1 as the operational intake contract on baseline `42cc77ec`.
- [ ] I confirm P4 remains the only V1 approval/activation machine.
- [ ] Implementation remains unauthorized until I authorize a named technical-design / WP.

**PO signature / date:** _pending_

---

**END OF CONTRACT v1 DRAFT**
