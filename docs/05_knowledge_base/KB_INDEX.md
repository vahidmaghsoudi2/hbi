# ProductKnowledge Index

**Last Updated:** 2026-11-18  
**Architecture authority:** [HBI-PO-DEC-THREE-PART-001](../03_decision_log/HBI-PO-DEC-THREE-PART-001.md)

## Purpose

ProductKnowledge is HBI's single bank of reliable, approved product information. It supplies the product facts that the Intelligence & Response part connects with Customer Context.

This index locates the current product-information and related specialist records. It does not create a second product bank or change existing Product Master ownership.

## Product-information intake

The Product Owner supplies the product and defines the required information, standards, scope and acceptance criteria. Multiple AI research systems collect and organize the requested information. Material that fails the stated requirements is corrected or rejected before acceptance. The Product Owner reviews and approves the completed information. Once approved, the product information is ready for entry into ProductKnowledge and use by HBI.

Sources and supporting evidence remain traceable where relevant. They support the reliability of product information; they are not separate repositories or additional approval stages after PO approval.

## Canonical locations

| Purpose | Canonical location | Responsibility |
|---|---|---|
| ProductKnowledge architecture and intake decision | [HBI-PO-DEC-THREE-PART-001](../03_decision_log/HBI-PO-DEC-THREE-PART-001.md) | Governing three-part model and simple product-intake path |
| Curated product and domain knowledge | docs/homepage/encyclopedia/ | Human-readable organization and navigation of approved knowledge |
| Skin product research dossiers | docs/homepage/encyclopedia/skin/PRODUCTS.md | Source-linked product research records; follow the governing product-intake acceptance direction |
| Skin Problem Space | docs/product-intake-knowledge-registry/SKIN_PROBLEM_BANK_WORKSPACE_INDEX.md and linked working records | Specialist customer/problem-domain knowledge; do not duplicate it into ProductKnowledge |
| Operational product knowledge | ProductKnowledge model and app/services/product_knowledge_service.py | Existing product-scoped runtime representation; current implementation status must be verified in code |
| Product identity | Existing Product Master / Product records | Canonical product identity; not replaced by this index |

## Use rules

1. ProductKnowledge is the product-information bank. Do not split it into parallel Evidence, Encyclopedia and QA repositories.
2. Information must meet the PO's stated requirements and receive PO approval before it is accepted into ProductKnowledge.
3. Keep source references and relevant limitations with the information so that important product facts can be traced and checked.
4. Do not add a second approval or QA gate after the PO has accepted the prepared product information.
5. Do not invent missing product facts. Mark uncertainty clearly and resolve it during research and review before acceptance.
6. ProductKnowledge does not replace Product Master identity, inventory state, product lifecycle or other existing operational controls.
7. ProductKnowledge is one of the three HBI architecture parts; Customer Context and Intelligence & Response are defined in the governing decision.

## Historical note

The former CKER proposal is superseded. Its separate top-level framing and proposed additional stages are not current HBI architecture. See [the superseded decision notice](../03_decision_log/HBI-PO-DEC-CKER-001.md).
