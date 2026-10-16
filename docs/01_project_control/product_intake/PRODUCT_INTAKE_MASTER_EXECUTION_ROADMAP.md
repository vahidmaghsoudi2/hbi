# PRODUCT INTAKE — MASTER EXECUTION ROADMAP

**Project:** HBI — Health & Beauty Intelligence  
**Domain:** Product Intake / Product Information Feeding  
**Status:** ACTIVE  
**Source of Truth:** GitHub `master`  
**Owner:** Product Owner / Domain Architect  
**Last Reconciled:** 2026-09-25  
**Reality baseline:** `96fa13853edb9f3eb13fa7455920640f50049a45`

---

## AUTHORITY

This roadmap is subordinate to:

- `docs/01_project_control/PROJECT_RULES.md`
- `docs/01_project_control/PRODUCT_INTAKE_STRATEGY_AND_GOVERNANCE.md`
- `docs/P4_PRODUCT_INTAKE_GOVERNANCE_CONTRACT_V1.md`
- `docs/01_project_control/product_intake/PRODUCT_INTAKE_GOVERNANCE_RECONCILIATION_2026-09-02.md`
- `docs/01_project_control/product_intake/PRODUCT_INTAKE_CONTRACT_v1.md`
- `docs/01_project_control/product_intake/PRODUCT_INTAKE_LIVE_PROJECT_LEDGER.md`

Strategy remains the broader strategic source. Contract v1 is the operational boundary. This roadmap records current execution reality.

---

## CURRENT REALITY

Product Intake is **existing infrastructure, not greenfield**.

Current governed chain:

`INTRODUCE → DRAFT → DUPLICATE CHECK → RESEARCH DRAFT / EVIDENCE → QA / IDENTITY → EVIDENCE READINESS / D3 → PO APPROVE → ACTIVE → RECOMMENDATION`

The repository now contains G1 Duplicate Check, G2 Research Draft, G4 Evidence Governance Parity, and G5 Recommendation Trust Trace on master.

Important boundary: the presence of Research Draft is **not** equivalent to a complete AI Research / Product Research Dossier pipeline.

---

# PHASE 0 — REALITY & BASELINE

**Status:** RECONCILED — 2026-09-25

Verified current surfaces include Product, ProductKnowledge, Evidence, Product Transition/QA, Duplicate Check, Research Draft, Recommendation Trust Trace, Product Intake UI/API and downstream `product_id` relationships.

No greenfield Product Intake rebuild is authorized.

---

# PHASE 1 — PRODUCT INTAKE CONTRACT v1

**Status:** PO ACCEPTED — historical contract remains authoritative for V1 operational boundaries.

Contract v1 was accepted on 2026-09-07. Acceptance does not authorize implementation by itself; a named technical-design/WP requires explicit PO authorization.

---

# PHASE 2 — AI RESEARCH / INTAKE

**Status:** GAP — actual AI acquisition/orchestration is not implemented.

Existing Research Draft is a governed assertion boundary. It supports source-traceable assertions and classification, but it is not itself web/source acquisition, OCR/document extraction, LLM research orchestration, or a complete Research Dossier.

Required historical scope remains:

- Identity
- Composition / INCI
- Ingredient roles
- Functional information
- Suitability
- Safety
- Usage
- Evidence
- Commercial information
- source comparison
- UNKNOWN / CONFLICT handling

AI remains unable to approve or activate Product Master.

---

# PHASE 3 — VALIDATION & ENRICHMENT

**Status:** PARTIAL

Existing QA, Evidence readiness, conflict handling, ProductKnowledge and D3 gates are operational.

Remaining gap: complete research-to-enrichment mapping across the historical dossier, with source traceability and governed promotion into trusted Knowledge.

---

# PHASE 4 — PO REVIEW & APPROVAL

**Status:** MACHINE EXISTS; INTAKE DOSSIER REVIEW UX PARTIAL/GAP

P4 supplies the approval/activation machine. Intake must reuse it.

Remaining gap: one coherent review surface that lets PO inspect the product dossier, evidence, UNKNOWN/CONFLICT, make informational corrections, and then invoke the existing P4 transitions.

No second approval state machine.

---

# PHASE 5 — PRODUCT MASTER / INTEGRATION

**Status:** IMPLEMENTED FOUNDATION / INTAKE ORCHESTRATION PARTIAL

ACTIVE Product is the governed Product Master and downstream domains use the same `product_id`.

Remaining gap: current Intake UI does not yet orchestrate the complete governed path from introduction through duplicate/research/enrichment/review to P4 activation.

---

# PHASE 6 — UPDATE / VERSION / RE-VALIDATION

**Status:** PARTIAL

V1 mutation history exists through ProductMutationLog.

Remaining OPEN policy/design:

- re-validation trigger matrix;
- complex version/history schema beyond V1 mutation log;
- treatment of critical identity/safety/evidence changes.

---

# PHASE 7 — REAL PRODUCT PILOT & ACCEPTANCE

**Status:** NOT PASSED

Target flow:

`INTRODUCE → IDENTITY/DUPLICATE → RESEARCH → ENRICH → VALIDATE → PO REVIEW → P4 APPROVE → P4 ACTIVATE → UPDATE / RE-VALIDATE`

Acceptance must use real products and protect Product A–D and all downstream references.

---

# CURRENT GAP REGISTER

| Gap | Status | Classification |
|---|---|---|
| Duplicate-check integration into intake create flow | GAP / OPEN POLICY | Existing G1 service/API; orchestration boundary remains |
| Complete Research Dossier | GAP | Historical scope exceeds current free-text Knowledge |
| AI Research acquisition/orchestration | GAP | Research Draft exists; AI acquisition layer absent |
| Structured Composition/INCI enrichment | PARTIAL | `ingredients` exists; complete governed enrichment absent |
| Ingredient Roles enrichment | PARTIAL | field exists; structured population absent |
| Functional enrichment | PARTIAL | fields/compatibility exist; full provenance workflow absent |
| Suitability dossier | PARTIAL | limited use-case compatibility exists; full dossier absent |
| Safety dossier | PARTIAL | contraindications exists; broader governed safety data absent |
| Usage enrichment | PARTIAL | usage field exists; source-traceable structured enrichment absent |
| Commercial research dossier | PARTIAL | operational price/availability exists; research fields incomplete |
| Source Comparison retention | OPEN | historical operation; persistence representation not decided |
| Full-dossier PO review surface | GAP | P4 machine exists; intake review experience incomplete |
| Re-validation workflow | GAP / OPEN POLICY | policy trigger matrix remains open |
| End-to-end Intake UI orchestration | GAP | stages are not one governed user flow |
| Real-product 0→100 acceptance package | GAP | G8 not passed |

---

# NON-NEGOTIABLES

1. GitHub `master` is Source of Truth.
2. NO ASSUMPTION / NO INVENTED DATA.
3. ONE PRODUCT MASTER and same `product_id` downstream.
4. Product A–D identities and references remain protected.
5. AI researches; PO approves through P4.
6. UNKNOWN and CONFLICT remain visible until governed resolution.
7. OPEN decisions remain OPEN until explicit PO decision.
8. Existing accepted capabilities are reused; no greenfield rebuild.
9. No parallel Product approval machine.
10. Accounting V1 remains outside this workstream.
11. Every implementation unit requires exact evidence, CI and post-merge Reality Gate.

---

# MANAGEMENT SEQUENCE

**Current management phase: REALITY → GAP RECONCILIATION**

1. Reconcile Mission 1 + Mission 2 + Mission 3 against current master.
2. Freeze the final GAP map.
3. Separate OPEN policy decisions from implementable GAPs.
4. Select one smallest dependency-safe implementation WP.
5. Obtain explicit PO authorization for that named WP.
6. Implement.
7. CI + post-merge Reality Gate.
8. Update this roadmap and ledger with exact SHA/evidence.
9. Repeat until G8 real-product acceptance.

**No implementation is authorized merely by this roadmap update.**

# END
