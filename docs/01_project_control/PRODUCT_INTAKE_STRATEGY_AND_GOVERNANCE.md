# PRODUCT INTAKE — STRATEGY & GOVERNANCE

**Document Type:** Master Strategy / Policy / Governance  
**Status:** ACTIVE  
**Project:** HBI — Health & Beauty Intelligence  
**Owner:** Product Owner / Domain Architect  
**Source of Truth:** GitHub `master`

---

## 1. PURPOSE

Product Intake is the official controlled entry path by which a real-world product becomes a governed HBI Product Master record.

This document preserves the strategic decision, policy, objective, operating model, governance rules, implementation direction, current state, open decisions and continuation rules for Product Intake.

This is the MASTER GOVERNANCE document for the Product Intake initiative.

It defines WHAT and WHY.

It does not replace the future Product Intake Contract or technical implementation specifications, which define HOW.

---

## 2. BUSINESS PROBLEM

HBI must prevent the same real-world product from being independently recreated across:

- Inventory
- Sales
- Accounting
- Knowledge
- Evidence
- Recommendation
- Frontend
- Future operational modules

Multiple independent product identities create:

- duplicate products;
- inconsistent information;
- broken traceability;
- conflicting attributes;
- unreliable recommendations;
- difficult maintenance;
- loss of historical context.

Therefore HBI requires ONE governed Product Master identity.

---

## 3. STRATEGIC OBJECTIVE

The objective of Product Intake is:

> Introduce a real product once, research and enrich it systematically, validate the information, obtain explicit human approval, and register it as one governed Product Master that all HBI modules reference through the same `product_id`.

The product must remain editable and maintainable after registration.

Product Intake is therefore a governed lifecycle, not merely a data-entry form.

---

## 4. CORE GOVERNING PRINCIPLES

### 4.1 ONE PRODUCT MASTER

HBI must maintain one authoritative product identity.

Inventory, Sales, Accounting, Knowledge, Evidence and Recommendation must reference the same `product_id`.

No module may silently create an independent competing product identity.

### 4.2 NO ASSUMPTION

Missing information must never be invented.

If information cannot be established with sufficient confidence:

- mark it UNKNOWN;
- preserve the uncertainty;
- identify the missing information;
- do not convert inference into fact.

### 4.3 HUMAN APPROVAL

AI may research, collect, compare, structure and enrich information.

AI is NOT the final Product Master approver.

The Product Owner remains responsible for final approval.

### 4.4 SOURCE TRACEABILITY

Important factual or functional claims must be traceable to their source.

Research findings must remain distinguishable from:

- direct product facts;
- manufacturer claims;
- scientific evidence;
- inference;
- unknown information;
- conflicting information.

### 4.5 OPERATIONAL CONTINUITY

Incomplete information must not unnecessarily stop normal business operations.

A product may require additional research or review while operational processes continue.

However, incomplete or insufficiently validated information must not automatically become trusted Knowledge or Recommendation input.

The exact technical mechanism for provisional/shadow products remains an open design decision.

### 4.6 SINGLE IDENTITY

The HBI `product_id` is the central identity connecting the product across modules.

SKU, GTIN/barcode, internal identifiers and commercial identifiers must not be confused with the HBI `product_id`.

### 4.7 MAINTAINABILITY

Product information is not immutable.

Products may require:

- correction;
- enrichment;
- manufacturer updates;
- packaging updates;
- evidence updates;
- commercial updates;
- re-validation.

Controlled updates and history are therefore required.

---

## 5. BUSINESS DEFINITION OF A PRODUCT

For HBI business purposes:

> Any item that is independently purchased, stocked and sold as a distinct commercial item is an independent Product.

Two items may share many attributes and still be separate HBI Products.

Example:

- ISDIN FotoUltra 100 Active Unify SPF 50+ — non-tinted
- ISDIN FotoUltra 100 Active Unify SPF 50+ — tinted

If they are independently purchased, stocked and sold, they receive separate `product_id` values.

This is a BUSINESS RULE.

The final technical treatment of shared attributes, Product/Variant modeling, SKU and GTIN relationships remains an implementation/design decision.

---

## 6. TARGET PRODUCT INTAKE LIFECYCLE

The intended lifecycle is:

INTRODUCE
→ IDENTITY / DUPLICATE CHECK
→ RESEARCH
→ ENRICH
→ VALIDATE
→ PO REVIEW
→ APPROVE
→ REGISTER / ACTIVATE
→ CONTINUOUS UPDATE
→ RE-VALIDATE WHEN REQUIRED

The exact technical state machine will be defined separately.

---

## 7. OPERATING MODEL

### Stage 1 — PRODUCT INTRODUCTION

The user introduces ONE real product.

Available information may include:

- product/package photographs;
- brand;
- product name;
- size;
- color;
- form;
- barcode;
- country;
- manufacturer;
- visible label information;
- existing business information.

The user does not need to provide the complete knowledge dossier.

### Stage 2 — IDENTITY / DUPLICATE CHECK

Before creating a new Product Master, HBI must determine whether the product already exists or whether a possible duplicate exists.

Available identifiers and product identity attributes should be considered.

Potential matches must be reviewed before creating a new independent Product.

The exact matching algorithm remains an implementation decision.

### Stage 3 — AI RESEARCH

A designated AI research agent performs structured research.

The AI may:

- research manufacturer information;
- collect official product information;
- collect ingredient information;
- research product functions and claims;
- identify appropriate use cases;
- identify limitations and safety information;
- identify relevant evidence;
- compare sources;
- identify conflicts;
- identify unknowns;
- structure findings.

The AI produces a RESEARCH DRAFT.

The AI does NOT approve the Product Master.

---

## 8. PRODUCT RESEARCH DOSSIER

The intended research output should be capable of covering:

### Identity

- brand;
- canonical product name;
- product form;
- size;
- color;
- market/region;
- manufacturer;
- barcode/GTIN when available;
- packaging/version information when relevant.

### Composition

- full INCI / ingredient list when available;
- ingredient roles;
- relevant formulation information.

### Functional Information

- intended uses;
- manufacturer claims;
- claimed benefits;
- product characteristics.

### Suitability

- relevant skin/hair types;
- appropriate use cases;
- unsuitable cases when evidence supports them.

### Safety

- limitations;
- precautions;
- contraindications;
- relevant interactions;
- known adverse effects/risks.

### Usage

- manufacturer instructions;
- relevant usage guidance;
- precautions.

### Evidence

- supporting evidence;
- evidence quality/strength;
- source references;
- dates where relevant.

### Commercial Information

Where reliable information exists:

- price/reference price;
- availability;
- market position;
- popularity/demand indicators.

Commercial information must not be confused with scientific or clinical evidence.

---

## 9. INFORMATION CLASSIFICATION

Research output must distinguish conceptually between:

- FACT
- MANUFACTURER CLAIM
- EVIDENCE
- INFERENCE
- UNKNOWN
- CONFLICT

The UI may simplify presentation.

The underlying governance must preserve the distinction.

---

## 10. SOURCE GOVERNANCE

Preferred source hierarchy should prioritize:

1. official manufacturer / brand sources;
2. authoritative scientific and regulatory sources;
3. peer-reviewed scientific literature;
4. reliable specialist databases;
5. reputable commercial/retail sources;
6. unsupported or unofficial sources.

The exact source-tier taxonomy remains subject to formal technical/QA approval.

Source quality must be considered separately from the existence of a claim.

---

## 11. PO REVIEW AND APPROVAL

After research and enrichment:

1. the draft is presented for review;
2. the Product Owner reviews the information;
3. the Product Owner may edit/correct information;
4. unresolved uncertainty remains visible;
5. conflicts are not silently resolved;
6. the Product Owner explicitly approves or rejects Product Master registration.

Approval is a GOVERNANCE GATE.

Creation of a database row is NOT equivalent to Product Master approval.

---

## 12. PRODUCT MASTER REGISTRATION

Only after the required approval gate should the product become an officially governed Product Master.

Once registered:

- the product receives/retains one authoritative `product_id`;
- downstream modules reference that identity;
- duplicate independent records must not be created for the same business product.

---

## 13. CONTINUOUS UPDATE POLICY

Product Intake does not end permanently at first registration.

A registered product may later require:

- information correction;
- new evidence;
- changed manufacturer claims;
- new packaging;
- changed formulation;
- commercial updates;
- newly discovered safety information;
- additional knowledge enrichment.

Updates must be controlled.

Future implementation must provide an auditable history/version mechanism.

---

## 14. RE-VALIDATION POLICY

Not every update necessarily requires identical review.

Future design must define when changes require:

- simple update;
- source re-check;
- QA review;
- Product Owner review;
- full re-validation.

Changes affecting identity, safety, evidence or recommendation-critical knowledge should receive stronger validation than ordinary commercial changes.

Exact rules remain open for the Product Intake Contract and QA policy.

---

## 15. RELATIONSHIP WITH HBI MODULES

Product Intake is upstream of multiple HBI capabilities.

Conceptual dependency:

Product Intake
→ Product Master
→ Inventory
→ Sales
→ Accounting
→ Knowledge
→ Evidence
→ Recommendation

The Product Master remains the common identity anchor.

No downstream module should establish a competing product identity merely because it needs additional attributes.

---

## 16. CURRENT REPOSITORY REALITY

Repository audit established:

Product Master = PARTIAL.

Existing implementation already includes:

- Product model;
- product identity fields;
- Product API;
- product creation;
- product update/edit;
- ProductKnowledge relationship;
- Evidence relationship;
- Inventory relationship;
- Sales relationship;
- Recommendation relationship;
- existing seeded products.

Current Product Intake functionality also exists at frontend/API level.

However, the complete governed Product Intake lifecycle is NOT yet implemented.

---

## 17. CURRENT IMPLEMENTATION GAPS

Known gaps include:

- formal Product Intake lifecycle/state machine;
- formal PO approval transition;
- controlled approval gate;
- complete research workflow;
- integrated enrichment workflow;
- stronger source-traceability enforcement;
- systematic Evidence attachment during Intake;
- systematic Knowledge enrichment during Intake;
- version/history/change tracking;
- complete validation pipeline;
- mature duplicate detection;
- formal treatment of incomplete/provisional products;
- final technical Product/Variant/SKU/GTIN model.

These are implementation gaps.

They are NOT permission to rewrite existing Product Master structures without explicit review.

---

## 18. PROTECTED EXISTING PRODUCT MASTER

Existing Product A-D records and established `product_id` values are protected.

Existing downstream relationships in:

- Inventory;
- Sales;
- Accounting;
- Evidence;
- Knowledge;
- Recommendation

must not be broken.

Any migration, identity change, merge or restructuring requires explicit Product Owner approval.

---

## 19. ROLES AND RESPONSIBILITIES

### Product Owner / Domain Architect

Responsible for:

- business rules;
- final approval;
- governance decisions;
- business-level conflict resolution;
- scope;
- acceptance gates.

### AI Research Agent

Responsible for:

- research;
- source collection;
- structured draft;
- uncertainty identification;
- conflict identification;
- evidence discovery.

AI does not approve Product Masters.

### Engineering

Responsible for:

- technical design;
- APIs;
- workflow;
- persistence;
- integration;
- implementation.

Engineering must implement approved policy and must not silently redefine business rules.

### QA

Responsible for:

- validation;
- test coverage;
- gate verification;
- confirming implementation matches approved policy.

### Sales / Inventory / Operations

Responsible for:

- introducing real products;
- supplying real-world product information;
- confirming operational identity;
- reporting corrections and changes.

---

## 20. CURRENT DECISION STATE

| Decision | Status |
|---|---|
| Product Intake is the official product-entry strategy | DECIDED |
| ONE PRODUCT MASTER | DECIDED |
| Same `product_id` across downstream modules | DECIDED |
| Independently purchased/stocked/sold item = independent Product | DECIDED |
| Incomplete data must not unnecessarily stop operations | DECIDED |
| AI performs research but does not approve | DECIDED |
| PO is final Product Master approver | DECIDED |
| Source traceability is a mandatory strategic direction | DECIDED |
| Product remains editable after registration | DECIDED |
| Product history/versioning is required direction | DECIDED |
| Product/Variant technical architecture | OPEN |
| Exact provisional/shadow product mechanism | OPEN |
| Exact source-tier taxonomy | OPEN |
| Exact AI research tier/cost strategy | OPEN |
| Exact duplicate-matching algorithm | OPEN |
| Exact approval state machine | OPEN |
| Exact history/version schema | OPEN |
| Exact Product Intake API Contract | OPEN |
| Exact UI/UX implementation | OPEN |

---

## 21. IMPLEMENTATION GOVERNANCE

Implementation must proceed in this order:

PRODUCT INTAKE STRATEGY & GOVERNANCE
↓
PRODUCT INTAKE CONTRACT v1
↓
TECHNICAL DESIGN
↓
IMPLEMENTATION
↓
QA / VALIDATION
↓
REAL PRODUCT PILOT
↓
PRODUCTION ACCEPTANCE

No implementation should redefine a DECIDED business rule.

If implementation reveals a genuine architectural conflict, the issue must return to Product Owner / Integration Architecture for explicit decision.

---

## 22. PRODUCT INTAKE CONTRACT — NEXT ARTIFACT

The next formal artifact must define the exact operational contract.

It should specify:

- required user inputs;
- AI research inputs;
- AI research outputs;
- field-level provenance;
- confidence;
- unknown handling;
- conflict handling;
- duplicate detection result;
- validation rules;
- PO review structure;
- approval transition;
- Product Master registration;
- update behavior;
- error behavior;
- audit requirements.

This Strategy document remains the governing parent document.

---

## 23. ACCEPTANCE GATES

### Gate 1 — Identity

The system can identify or flag a possible existing product.

### Gate 2 — Research

The AI can produce a structured, source-traceable research dossier.

### Gate 3 — Validation

Missing, conflicting and unsupported information is visible.

### Gate 4 — Human Review

The PO can inspect and edit the draft.

### Gate 5 — Approval

Only authorized human approval creates the governed Product Master state.

### Gate 6 — Integration

Inventory, Sales, Accounting, Knowledge, Evidence and Recommendation reference the same `product_id`.

### Gate 7 — Maintenance

The Product Master can be updated with traceable history.

### Gate 8 — Real Product Pilot

The complete process works on real products without creating duplicate identities or corrupting existing operational data.

---

## 24. CHANGE CONTROL

This document is a controlled governance artifact.

Changes affecting:

- Product identity policy;
- Product definition;
- approval authority;
- ONE PRODUCT MASTER;
- downstream identity relationships;
- operational continuity;
- AI authority;
- source governance

require explicit Product Owner decision.

Technical implementation details may evolve without rewriting strategic principles.

---

## 25. CONTINUATION RULE

If this phase is resumed after interruption, any new human or AI team member must:

1. read this document first;
2. inspect current GitHub `master`;
3. inspect the Product model and existing Product Intake implementation;
4. compare implementation against this governance document;
5. read `PRODUCT_INTAKE_CONTRACT_v1.md` when available;
6. never assume an OPEN decision has already been resolved;
7. never overwrite protected Product Master records without explicit approval.

This document is the continuity anchor for Product Intake.

---

## 26. CURRENT PHASE

**Strategic Direction:** ESTABLISHED  
**Business Rules:** PARTIALLY LOCKED  
**Governance:** ESTABLISHED  
**Technical Contract:** NOT YET FINAL  
**Implementation:** PARTIAL  
**QA Acceptance:** NOT YET COMPLETE  
**Real Product Pilot:** PENDING

---

## 27. FINAL GOVERNANCE STATEMENT

HBI will treat Product Intake as a controlled lifecycle, not as a simple data-entry screen.

The strategic target is:

> One real business product → one governed HBI Product identity → one `product_id` → traceable knowledge/evidence → controlled approval → continuous maintainability.

The system must remain operationally practical while preserving data integrity, source traceability, human accountability and future extensibility.

---

**END OF DOCUMENT**
