# Product Information Sources and Evidence

**Last Updated:** 2026-11-18  
**Architecture authority:** [HBI-PO-DEC-THREE-PART-001](../03_decision_log/HBI-PO-DEC-THREE-PART-001.md)

## Purpose

Sources and supporting evidence help establish where product information came from and allow important facts to be checked. They support the single ProductKnowledge bank. They are not a separate top-level HBI architecture part, a parallel product bank or an additional approval barrier after PO acceptance.

The Product Owner defines the required standards and acceptance criteria, AI research systems collect and organize information against those requirements, and the Product Owner approves the completed product information before it enters ProductKnowledge.

## Existing technical records

The repository currently contains the following implementation elements. Their presence does not require the product-intake process to expose them as separate user-facing stages:

| Component | Canonical location | Existing responsibility |
|---|---|---|
| Evidence record | app/models/evidence.py | Structured product claim and source reference |
| Claim taxonomy | app/domain/claim_taxonomy.py | Existing classification of claim types |
| Evidence service | app/services/evidence_service.py | Existing evidence-related operations and validation |
| Evidence mutation audit | app/models/evidence_mutation_log.py and app/services/evidence_mutation_log_service.py | Existing mutation traceability |
| ProductKnowledge aggregation | app/services/product_knowledge_service.py | Existing product-scoped knowledge aggregation; follow its current code contract |

## Practical rules

1. Retain source references for important product information where available and relevant.
2. Distinguish what the manufacturer states from independent findings or an inference; do not overstate a source.
3. Keep product variant, market, date and other scope limitations when they affect correctness.
4. Do not invent missing facts. Resolve material gaps against the PO's stated acceptance criteria before the product information is approved.
5. The PO's review and approval completes the product-information acceptance process. Do not add another Evidence or QA approval gate after that approval.
6. Existing technical Evidence records and audit history may support traceability. They do not create a second repository or change the three-part HBI architecture.
7. Do not claim that a technical evidence or versioning capability exists beyond what current code verifies.

## Historical note

The former CKER proposal treated Evidence as a separate named architecture layer and prescribed additional claim-level governance framing. That proposal is superseded and must not be used to add complexity to product intake. Evidence and source references remain useful supporting information within ProductKnowledge.
