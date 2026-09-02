# PRODUCT INTAKE — MASTER EXECUTION ROADMAP

**Project:** HBI — Health & Beauty Intelligence
**Domain:** Product Intake / Product Information Feeding
**Status:** ACTIVE
**Source of Truth:** GitHub `master`
**Owner:** Product Owner / Domain Architect
**Last Updated:** 2026-09-02

---

## PURPOSE

This roadmap is the execution continuity map for the HBI Product Intake initiative.

It exists so that any future human or AI team member can determine:

1. Where the work currently stands.
2. What has already been decided.
3. What remains open.
4. What phase is currently active.
5. What the next action is.
6. What must NOT be changed.

This document is complementary to:

`docs/01_project_control/PRODUCT_INTAKE_STRATEGY_AND_GOVERNANCE.md`

The Strategy & Governance document defines WHAT and WHY.
This roadmap defines the execution sequence.

---

# EXECUTION ROADMAP

## PHASE 0 — REALITY & BASELINE

Purpose:
Establish the actual repository state before implementation.

Required inspection:
- Product model
- Product API
- Product Intake UI/API
- ProductKnowledge
- Evidence
- Inventory
- Sales
- Recommendation
- Existing Product Master records
- Existing downstream relationships
- Current implementation gaps

Output:
Reality Baseline.

Status:
PARTIALLY COMPLETED / BASELINE MUST BE VERIFIED AGAIN BEFORE CONTRACT FINALIZATION.

---

## PHASE 1 — PRODUCT INTAKE CONTRACT v1

Purpose:
Convert the approved Strategy & Governance into an exact operational contract.

Must define:
- user inputs
- AI research inputs
- AI research outputs
- field-level provenance
- confidence
- UNKNOWN handling
- CONFLICT handling
- duplicate detection result
- validation rules
- PO review
- approval transition
- Product Master registration
- update behavior
- error behavior
- audit requirements

Output:
`PRODUCT_INTAKE_CONTRACT_v1.md`

Status:
ACTIVE — CURRENT PHASE.

NEXT ACTION:
Complete and formally review Product Intake Contract v1 before implementation.

---

## PHASE 2 — AI RESEARCH / INTAKE

Purpose:
Allow a real introduced product to generate a structured research draft.

AI responsibilities:
- research
- source collection
- product information collection
- ingredient information
- claims
- use cases
- limitations
- safety information
- evidence discovery
- conflicts
- unknowns
- structured dossier

AI must NOT approve Product Master registration.

Output:
Research Draft / Product Research Dossier.

Status:
NOT STARTED.

---

## PHASE 3 — VALIDATION & ENRICHMENT

Purpose:
Validate and enrich the research output.

Information domains:
- Identity
- Composition / INCI
- Ingredient roles
- Functional claims
- Benefits
- Suitability
- Safety
- Usage
- Evidence
- Commercial information

Information classification:
FACT
MANUFACTURER CLAIM
EVIDENCE
INFERENCE
UNKNOWN
CONFLICT

Status:
NOT STARTED.

---

## PHASE 4 — PO REVIEW & APPROVAL

Purpose:
Provide an explicit human governance gate.

PO must be able to:
- inspect
- edit
- correct
- review sources
- inspect unknowns
- inspect conflicts
- approve
- reject

Critical rule:

Database creation is NOT equivalent to Product Master approval.

Only authorized human approval can complete the approval gate.

Status:
NOT STARTED.

---

## PHASE 5 — PRODUCT MASTER REGISTRATION & INTEGRATION

Purpose:
Register the approved product as the governed Product Master.

Requirements:
- authoritative `product_id`
- ONE PRODUCT MASTER identity
- downstream modules reference the same `product_id`

Downstream domains:
- Inventory
- Sales
- Accounting
- Knowledge
- Evidence
- Recommendation

Status:
NOT STARTED.

---

## PHASE 6 — UPDATE / VERSION / RE-VALIDATION

Purpose:
Maintain Product Master integrity after registration.

Required capabilities:
- correction
- enrichment
- manufacturer updates
- packaging/formulation updates
- evidence updates
- commercial updates
- safety updates
- version/history
- controlled re-validation

Status:
NOT STARTED.

---

## PHASE 7 — REAL PRODUCT PILOT & ACCEPTANCE

Purpose:
Validate the complete Product Intake lifecycle on real products.

Flow:

INTRODUCE
→ IDENTITY / DUPLICATE CHECK
→ RESEARCH
→ ENRICH
→ VALIDATE
→ PO REVIEW
→ APPROVE
→ REGISTER / ACTIVATE
→ UPDATE / RE-VALIDATE WHEN REQUIRED

Acceptance requirements:
- no duplicate identity
- no corruption of existing Product Master
- source traceability
- visible uncertainty
- AI cannot approve
- correct downstream `product_id`
- operational continuity
- auditable history

Final sequence:
QA → PO Acceptance → Production Readiness.

Status:
NOT STARTED.

---

# PHASE STATUS

| Phase | Name | Status |
|---|---|---|
| 0 | Reality & Baseline | PARTIAL |
| 1 | Product Intake Contract v1 | ACTIVE / CURRENT |
| 2 | AI Research / Intake | NOT STARTED |
| 3 | Validation & Enrichment | NOT STARTED |
| 4 | PO Review & Approval | NOT STARTED |
| 5 | Product Master / Integration | NOT STARTED |
| 6 | Update / Version / Re-validation | NOT STARTED |
| 7 | Real Product Pilot / Acceptance | NOT STARTED |

---

# ACCEPTANCE GATES

These are acceptance gates, NOT execution phases.

G1 — Identity
G2 — Research
G3 — Validation
G4 — Human Review
G5 — Approval
G6 — Integration
G7 — Maintenance
G8 — Real Product Pilot

A phase may contain one or more gates.

---

# NON-NEGOTIABLE RULES

1. GitHub `master` is the Source of Truth.
2. NO ASSUMPTION.
3. NO INVENTED DATA.
4. ONE PRODUCT MASTER.
5. Same `product_id` downstream.
6. AI researches but does not approve.
7. PO is final Product Master approver.
8. UNKNOWN remains UNKNOWN until established.
9. CONFLICT must remain visible until resolved.
10. Existing Product A-D identities are protected.
11. Existing downstream relationships must not be broken.
12. Do not rebuild accepted backend capabilities without explicit justification.
13. Do not change a DECIDED business rule through implementation.
14. OPEN decisions must remain OPEN until explicitly decided.
15. Every completed phase requires evidence and a recorded commit/SHA.
16. No phase is considered complete merely because code exists.

---

# CURRENT POSITION

CURRENT PHASE:
PHASE 1 — PRODUCT INTAKE CONTRACT v1

CURRENT OBJECTIVE:
Finalize the operational contract before implementation.

CURRENT NEXT ACTION:
Review the repository baseline and produce the formal Product Intake Contract v1.

DO NOT:
- start implementation before the contract is accepted
- redesign Product Master without explicit approval
- invent missing fields
- invent AI behavior
- invent approval states
- modify Accounting V1
- create a competing Product identity

---

# CONTINUITY RULE

When this project is resumed after interruption:

1. Read this roadmap.
2. Read `PRODUCT_INTAKE_STRATEGY_AND_GOVERNANCE.md`.
3. Inspect current GitHub `master`.
4. Verify the current SHA.
5. Check the Live Ledger.
6. Resume only from the recorded CURRENT PHASE.
7. Never infer that an OPEN decision has been resolved.
8. Never assume that previous implementation still matches current `master`.

This document is a continuity anchor, not a substitute for repository inspection.
