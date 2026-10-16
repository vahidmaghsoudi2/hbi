# SKIN PRODUCT INTAKE — EXECUTION CONTRACT v1.1

**Status:** PO APPROVED — CONTRACT BASELINE  
**Scope:** Skin products only  
**Strategic anchor:** Issue #276  
**Execution consolidation:** Issue #278  
**Implementation authorization:** YES, for separately authorized implementation WPs only

## 1. PO decisions

| Decision | PO choice |
|---|---|
| Minimum data by stage | Option 1 — requirements increase by lifecycle stage |
| Minimum product safety | Option 1 — contraindications or explicit UNKNOWN |
| Variant semantics | Option 1 — adopt current DuplicateCheck rules |
| Product vs customer eligibility | Option 1 — keep them separate |
| Smart inference | Option 2 — inference may be stored separately with label, rationale and evidence provenance |
| Empty vs UNKNOWN | Option 1 — distinct states; neither means safe |

## 2. Lifecycle data rule

Product entry starts with the minimum identity required to create a DRAFT:
- product_id
- product_name
- brand

When known, capture size, variant, barcode/GTIN and other identity metadata.

Requirements increase as the product advances toward QA, APPROVE and ACTIVE. Optional fields do not block DRAFT.

Before approval/activation, existing lifecycle gates remain authoritative: identity verification, valid QA, Evidence Readiness and D3 requirements. Skin-specific safety requirements in this contract also apply.

## 3. Minimum skin-product safety

Before APPROVE, product-side contraindication status must be represented by:
- valid supported information; or
- an explicit UNKNOWN assertion.

Empty is not equivalent to safe.

Warnings, precautions, interactions, adverse effects, population restrictions and body-site restrictions remain evidence-driven enrichment unless a later PO decision makes one mandatory.

Product safety information, customer medical context, and Customer × Product Decision Safety remain separate concepts.

Customer medical context is outside the Product Master data model.

## 4. Duplicate and variant policy

V1 adopts the current DuplicateCheck behavior:
- exact product_id → EXISTING
- exact barcode/GTIN → EXISTING
- same brand/name with size or variant difference → distinct/new path
- packaging/name ambiguity without the above identity conflict → POSSIBLE_MATCH for operator review
- no automatic fuzzy-score identity engine

SKU entity, GTIN allocation, automatic POSSIBLE_MATCH merge, and formal shade/formulation identity keys are outside V1.

Changing these semantics requires a separate PO decision and implementation WP.

## 5. Research, Evidence and ProductKnowledge

The authoritative flow is:

Research/Input → Evidence → QA/Conflict Resolution → ProductKnowledge

Research drafts remain provisional. PENDING evidence does not become trusted ProductKnowledge.

Unresolved conflicts do not become trusted ProductKnowledge.

The current six claim types remain frozen for V1:
FACT, MANUFACTURER_CLAIM, EVIDENCE, INFERENCE, UNKNOWN, CONFLICT.

MANUFACTURER_CLAIM does not bypass QA.

AI output does not independently approve, activate, or create verified knowledge.

## 6. Smart inference

Inference may be retained as a separately identifiable assertion.

It must remain distinguishable from FACT and preserve:
- inference label/type
- supporting evidence/provenance
- rationale where available
- review/QA status

Inference must never silently become FACT.

## 7. EMPTY and UNKNOWN

EMPTY means the information has not been recorded or the relevant field has not been populated.

UNKNOWN means the system has an explicit assertion that the information is unknown/unresolved.

Therefore:
- EMPTY ≠ SAFE
- UNKNOWN ≠ SAFE
- UNKNOWN ≠ ELIGIBLE

Absence of a recorded risk must not be interpreted automatically as absence of risk.

## 8. Product Eligibility

V1 does not introduce a new Product Eligibility boolean/table.

Product-level eligibility is the named conjunction of the existing gates:

ACTIVE
AND identity VERIFIED
AND product QA VALID
AND Evidence Readiness PASS
AND D3 requirements satisfied
AND operational stock available

Need matching is separate.

Customer-specific eligibility is separate.

Final recommendation eligibility is downstream of product eligibility plus need/customer/engine checks.

## 9. AI boundary

AI may assist with research, enrichment, extraction proposals and inference.

AI has no independent authority to:
- approve
- activate
- bypass QA
- bypass Evidence Readiness
- convert inference to fact
- bypass human/governance gates

## 10. Duplicate intake boundary

DuplicateCheck capability exists in the repository, but capability is distinct from enforcement in the real intake save path.

Integration of duplicate evaluation into the actual Product Intake create flow is a separate implementation WP.

## 11. V1 exclusions

The following remain outside this contract:
- structured full INCI entity/ontology
- SKU model
- GTIN allocation
- full regulatory engine
- adverse-event management
- diagnosis engine
- full Customer × Product decision engine
- recommendation scoring redesign
- OCR/PDF ingestion
- supplier API ingestion
- independent AI ingestion pipeline
- rich skin-specific eligibility engine

## 12. Required implementation clarifications

The following are implementation details, not new PO decisions:
1. Exact representation and lifecycle of UNKNOWN assertions.
2. Evidence acceptance criteria for contraindication information.
3. UI representation of inference and provenance.
4. Enforcement point for DuplicateCheck before create.
5. Exact structured treatment of future skin attributes such as SPF, active percentage, formulation, target skin/site and structured ingredients.

These details require their own WP acceptance criteria before implementation.

## 13. Governance

Operating law:

EVIDENCE → RECONCILE → DECIDE → CONTRACT → AUTHORIZE → IMPLEMENT → TEST → VERIFY → ACCEPT

This contract authorizes implementation planning and separately approved WPs. It does not authorize unscoped schema, API, migration, scoring or architecture changes.

DONE ≠ VERIFIED ≠ ACCEPTED ≠ MERGED
