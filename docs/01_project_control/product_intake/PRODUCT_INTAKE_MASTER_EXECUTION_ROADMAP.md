# PRODUCT INTAKE — MASTER EXECUTION ROADMAP

**Project:** HBI — Health & Beauty Intelligence  
**Domain:** Product Intake / Product Information Feeding  
**Status:** ACTIVE  
**Source of Truth:** GitHub `master`  
**Owner:** Product Owner / Domain Architect  
**Last Reconciled:** 2026-09-02  
**Current Phase:** PHASE 1 — PRODUCT INTAKE CONTRACT v1

---

## AUTHORITY

This roadmap is subordinate to:

`docs/01_project_control/PROJECT_RULES.md`

It must be read with:

- `docs/01_project_control/PRODUCT_INTAKE_STRATEGY_AND_GOVERNANCE.md`
- `docs/01_project_control/product_intake/PRODUCT_INTAKE_GOVERNANCE_RECONCILIATION_2026-09-02.md`
- `docs/01_project_control/product_intake/PRODUCT_INTAKE_LIVE_PROJECT_LEDGER.md`
- `docs/01_project_control/product_intake/PRODUCT_INTAKE_EXECUTION_MISSION.md`

---

## PURPOSE

This roadmap provides one unambiguous execution path from the existing Product Intake capability to a governed Product Master lifecycle.

Product Intake is NOT a greenfield UI build.

The objective is:

**CURRENT REALITY → GAP IDENTIFICATION → CONTRACT → COMPLETION**

---

# PHASE 0 — REALITY & BASELINE

**Status:** RECONCILED

Direct repository inspection confirms existing Product functionality in:

- Product model;
- Product services/API;
- ProductKnowledge;
- Evidence;
- Inventory;
- Product A-D;
- Home Page;
- Product Gallery/listing;
- Product Intake UI.

Important frontend reality includes:

- `frontend/src/pages/NewHomePage.tsx`
- `frontend/src/pages/ProductIntakePanel.tsx`

Therefore no greenfield Product Intake rebuild is authorized.

Phase 0 completion means current implementation is explicitly separated from future proposed behavior.

---

# PHASE 1 — PRODUCT INTAKE CONTRACT v1

**Status:** ACTIVE / CURRENT

Purpose:

Convert approved governance into an exact operational contract.

Contract must define:

- User Inputs;
- Product Master boundary;
- AI Research Inputs;
- AI Research Outputs;
- Evidence boundary;
- Product Knowledge boundary;
- provenance;
- confidence;
- UNKNOWN handling;
- CONFLICT handling;
- duplicate detection result;
- validation;
- PO review/edit;
- approval;
- registration/activation;
- update behavior;
- error behavior;
- audit requirements;
- existing Home/Product Intake integration boundary.

**Output:**

`PRODUCT_INTAKE_CONTRACT_v1.md`

**Implementation authorization: NO**

No implementation of new Product Intake lifecycle behavior may begin before Contract v1 is formally accepted.

---

# PHASE 2 — AI RESEARCH / INTAKE

Use the existing Product Intake entry capability as the starting point.

Purpose:

Generate a structured, source-traceable Research Draft.

Status:

NOT STARTED.

---

# PHASE 3 — VALIDATION & ENRICHMENT

Purpose:

Validate and enrich research, Evidence and Knowledge while preserving:

FACT  
MANUFACTURER CLAIM  
EVIDENCE  
INFERENCE  
UNKNOWN  
CONFLICT

Status:

NOT STARTED.

---

# PHASE 4 — PO REVIEW & APPROVAL

Purpose:

Provide explicit human review and approval.

PO must be able to:

- inspect;
- edit;
- correct;
- review sources;
- inspect UNKNOWN;
- inspect CONFLICT;
- approve;
- reject.

Database creation is not equivalent to approval.

Status:

NOT STARTED.

---

# PHASE 5 — PRODUCT MASTER REGISTRATION & INTEGRATION

Purpose:

Register approved products as the governed Product Master.

Requirements:

- one authoritative `product_id`;
- ONE PRODUCT MASTER;
- downstream references use the same `product_id`.

Domains:

- Inventory;
- Sales;
- Accounting;
- Knowledge;
- Evidence;
- Recommendation.

Status:

NOT STARTED.

---

# PHASE 6 — UPDATE / VERSION / RE-VALIDATION

Purpose:

Maintain Product Master integrity after registration.

Required direction:

- correction;
- enrichment;
- manufacturer updates;
- packaging/formulation changes;
- evidence updates;
- commercial updates;
- safety updates;
- history/versioning;
- controlled re-validation.

Status:

NOT STARTED.

---

# PHASE 7 — REAL PRODUCT PILOT & ACCEPTANCE

Purpose:

Validate the complete lifecycle on real products.

Flow:

INTRODUCE
→ IDENTITY / DUPLICATE CHECK
→ RESEARCH
→ ENRICH
→ VALIDATE
→ PO REVIEW
→ APPROVE
→ REGISTER / ACTIVATE
→ UPDATE / RE-VALIDATE

Status:

NOT STARTED.

---

# PHASE STATUS

| Phase | Status |
|---|---|
| P0 Reality & Baseline | RECONCILED |
| P1 Contract v1 | ACTIVE / CURRENT |
| P2 AI Research / Intake | NOT STARTED |
| P3 Validation / Enrichment | NOT STARTED |
| P4 PO Review / Approval | NOT STARTED |
| P5 Product Master / Integration | NOT STARTED |
| P6 Version / Update / Re-validation | NOT STARTED |
| P7 Real Product Pilot / Acceptance | NOT STARTED |

---

# ACCEPTANCE GATES

These are Gates, not Phases.

G1 — Identity  
G2 — Research  
G3 — Validation  
G4 — Human Review  
G5 — Approval  
G6 — Integration  
G7 — Maintenance  
G8 — Real Product Pilot

---

# NON-NEGOTIABLE RULES

1. GitHub `master` is Source of Truth.
2. `PROJECT_RULES.md` is the mandatory Entry Gate.
3. NO ASSUMPTION.
4. NO INVENTED DATA.
5. Find existing capability before building.
6. Product Intake must not be rebuilt from zero.
7. ONE PRODUCT MASTER.
8. Same `product_id` downstream.
9. Existing Product A-D are protected.
10. AI researches but does not approve.
11. PO is final Product Master approver.
12. OPEN decisions remain OPEN.
13. Current implementation is not automatically a business rule.
14. Contract precedes new implementation.
15. Every completed unit requires evidence, test, commit/SHA and Ledger update.
16. Accounting V1 remains outside this workstream and frozen.

---

# CURRENT POSITION

**CURRENT PHASE:**  
PHASE 1 — PRODUCT INTAKE CONTRACT v1

**CURRENT OBJECTIVE:**  
Finalize the operational contract against the verified existing implementation.

**CURRENT AUTHORIZED ACTION:**  
Reality reconciliation → Contract finalization.

**NOT AUTHORIZED:**  
Implementation of new duplicate detection, approval workflow, lifecycle state machine, inventory policy or versioning.

---

# CONTINUITY

On every resume:

1. Read `PROJECT_RULES.md`.
2. Read Strategy & Governance.
3. Read Governance Reconciliation Amendment.
4. Read this Roadmap.
5. Read Live Ledger.
6. Inspect current `origin/master`.
7. Record actual SHA.
8. Inspect current Product Intake and Home Product functionality.
9. Resume only from the recorded authorized action.

# END
