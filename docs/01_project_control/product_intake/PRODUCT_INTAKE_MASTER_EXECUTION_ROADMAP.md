# PRODUCT INTAKE — MASTER EXECUTION ROADMAP

**Project:** HBI — Health & Beauty Intelligence  
**Domain:** Product Intake / Product Information Feeding  
**Status:** ACTIVE  
**Source of Truth:** GitHub `master`  
**Owner:** Product Owner / Domain Architect  
**Last Reconciled:** 2026-09-07  
**Current Phase:** PHASE 1 — PRODUCT INTAKE CONTRACT v1 (**PO ACCEPTED** on branch; merge pending)

---

## AUTHORITY

This roadmap is subordinate to:

`docs/01_project_control/PROJECT_RULES.md`

It must be read with:

- `docs/01_project_control/PRODUCT_INTAKE_STRATEGY_AND_GOVERNANCE.md`
- `docs/P4_PRODUCT_INTAKE_GOVERNANCE_CONTRACT_V1.md`
- `docs/01_project_control/product_intake/PRODUCT_INTAKE_GOVERNANCE_RECONCILIATION_2026-09-02.md`
- `docs/01_project_control/product_intake/PRODUCT_INTAKE_CONTRACT_v1.md`
- `docs/01_project_control/product_intake/PRODUCT_INTAKE_LIVE_PROJECT_LEDGER.md`
- `docs/01_project_control/product_intake/PRODUCT_INTAKE_EXECUTION_MISSION.md`

---

## PURPOSE

One execution path from existing Product Intake capability to a governed Product Master lifecycle.

Product Intake is NOT a greenfield UI build.

**CURRENT REALITY → GAP IDENTIFICATION → CONTRACT → COMPLETION**

P4 at `42cc77ec` already supplies the Product governance mutation machine. This roadmap must not schedule a second machine.

---

# PHASE 0 — REALITY & BASELINE

**Status:** RECONCILED (`42cc77ec`)

Existing: Product model/API/P4 transitions/mutation log, ProductKnowledge, Evidence, Inventory, Product A–D, Home, Gallery, `ProductIntakePanel.tsx`.

No greenfield Product Intake rebuild is authorized.

---

# PHASE 1 — PRODUCT INTAKE CONTRACT v1

**Status:** **PO ACCEPTED** (on branch head; merge to master pending)

**Output:** `PRODUCT_INTAKE_CONTRACT_v1.md`

**Implementation authorization: NO** until PO authorizes a named technical design / WP (PO acceptance of Contract alone does not authorize code).

---

# PHASE 2 — AI RESEARCH / INTAKE

Starts only after Contract v1 PO ACCEPTED and a research technical design.

Purpose: structured, source-traceable Research Draft. AI does not approve.

**Status:** NOT STARTED.

---

# PHASE 3 — VALIDATION & ENRICHMENT

Preserve FACT / MANUFACTURER CLAIM / EVIDENCE / INFERENCE / UNKNOWN / CONFLICT.

**Status:** NOT STARTED.

---

# PHASE 4 — PO REVIEW & APPROVAL (OPERATIONAL)

Reuse P4 transitions (`approve` / `reject` / `activate` / identity / QA). Do not rebuild them.

This phase is the intake dossier review experience on top of the existing machine.

Database creation is not approval.

**Status:** MACHINE EXISTS (P4). INTAKE UX NOT STARTED.

---

# PHASE 5 — PRODUCT MASTER REGISTRATION & INTEGRATION

ACTIVE via P4 activate is the governed Product Master. Same `product_id` downstream.

**Status:** PARTIAL (identity + relations exist; governed intake registration path not operationally used by UI).

---

# PHASE 6 — UPDATE / VERSION / RE-VALIDATION

V1 history = ProductMutationLog. Re-validation trigger matrix remains OPEN.

**Status:** PARTIAL.

---

# PHASE 7 — REAL PRODUCT PILOT & ACCEPTANCE

INTRODUCE → DUPLICATE CHECK → RESEARCH → ENRICH → VALIDATE → PO REVIEW → P4 APPROVE → P4 ACTIVATE → UPDATE

**Status:** NOT STARTED.

---

# PHASE STATUS

| Phase | Status |
|---|---|
| P0 Reality & Baseline | RECONCILED |
| P1 Contract v1 | **PO ACCEPTED** (on branch; merge pending) |
| P2 AI Research / Intake | NOT STARTED |
| P3 Validation / Enrichment | NOT STARTED |
| P4 PO Review / Approval | MACHINE EXISTS; UX NOT STARTED |
| P5 Product Master / Integration | PARTIAL |
| P6 Version / Update / Re-validation | PARTIAL |
| P7 Real Product Pilot / Acceptance | NOT STARTED |

---

# ACCEPTANCE GATES

G1 Identity · G2 Research · G3 Validation · G4 Human Review · G5 Approval · G6 Integration · G7 Maintenance · G8 Real Product Pilot

---

# NON-NEGOTIABLE RULES

1. GitHub `master` is Source of Truth.
2. `PROJECT_RULES.md` is the Entry Gate.
3. NO ASSUMPTION. NO INVENTED DATA.
4. Find existing capability before building.
5. Do not rebuild Product Intake from zero.
6. ONE PRODUCT MASTER. Same `product_id` downstream.
7. Product A-D protected.
8. AI researches; PO approves — via P4 only.
9. OPEN decisions remain OPEN.
10. Current implementation is not automatically a new business rule.
11. Contract precedes new implementation.
12. P4 lifecycle must not be duplicated.
13. Accounting V1 remains outside this workstream and frozen.

---

# CURRENT POSITION

**CURRENT PHASE:** PHASE 1 — CONTRACT v1 **PO ACCEPTED** (on branch)

**CURRENT AUTHORIZED ACTION:** Merge PR #33 to master; then only a PO-authorized named technical-design / WP (no implementation without that).

**NOT AUTHORIZED:** implementation of duplicate detector, AI research, new approval workflow, lifecycle rebuild, inventory policy change, versioning schema, Product A-D mutation.

---

# CONTINUITY

On every resume: read PROJECT_RULES, Strategy, P4 contract, Intake Contract v1, Reconciliation, this Roadmap, Ledger; fetch `origin/master`; record SHA; resume only from the authorized action.

# END
