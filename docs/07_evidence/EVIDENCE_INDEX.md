# Product Information Sources and Evidence

**Last Updated:** 2026-11-18  
**Architecture authority:** [HBI-PO-DEC-THREE-PART-001](../03_decision_log/HBI-PO-DEC-THREE-PART-001.md)  
**Encyclopedia source-of-truth decision:** [HBI-PO-DEC-ENCYCLOPEDIA-PRIMARY-KB-001](https://github.com/vahidmaghsoudi2/hbi/issues/406#issuecomment-6989651765)

## Purpose

Evidence and Source Traceability support the **single ProductKnowledge bank** by preserving where important product statements came from and what their sources can or cannot establish.

They are supporting capabilities, not a separate top-level HBI architecture part, a parallel product bank, or an additional approval barrier after PO acceptance.

## Product-information path

`Approved Encyclopedia → Evidence / Source Traceability → ProductKnowledge → Consultation`

- The Encyclopedia is the primary, live and human-editable reference for approved product knowledge.
- Original manufacturer disclosures, physical package text, technical documents and relevant scientific sources remain primary source records. They must not be deleted or replaced by an Encyclopedia summary.
- Evidence/source references connect important Encyclopedia statements to their original sources and preserve relevant market, version, date and limitations.
- ProductKnowledge is the operational runtime bank that supplies accepted information to HBI.
- PO approval completes product-information acceptance. Do not add a second Evidence or QA approval gate after that decision.

## Existing technical records

The repository currently contains the following implementation elements. Their presence does not require the product-intake process to expose them as separate user-facing stages:

| Component | Canonical location | Existing responsibility |
|---|---|---|
| Evidence record | `app/models/evidence.py` | Structured product claim and source reference |
| Claim taxonomy | `app/domain/claim_taxonomy.py` | Existing classification of claim types |
| Evidence service | `app/services/evidence_service.py` | Existing evidence-related operations and validation |
| Evidence mutation audit | `app/models/evidence_mutation_log.py` and `app/services/evidence_mutation_log_service.py` | Existing mutation traceability |
| ProductKnowledge aggregation | `app/services/product_knowledge_service.py` | Existing product-scoped runtime aggregation; follow its current code contract |

## Practical rules

1. Retain the original source reference for every important product statement where available.
2. Preserve source type: manufacturer disclosure is not independent evidence; an inference is not a fact.
3. Keep product variant, market, package/version, date and other scope limitations when they affect correctness.
4. Do not invent missing facts. Use the existing vocabulary for UNKNOWN, CONFLICT, PARTIAL or unreviewed information.
5. The source record and its limitations remain accessible; a summary does not replace the original source.
6. Evidence/source traceability supports the Encyclopedia and ProductKnowledge; it does not create another bank or post-approval gate.
7. Do not claim that a technical evidence or versioning capability exists beyond what current code verifies.

## Historical note

The former CKER proposal treated Evidence as a separate named architecture layer and prescribed additional claim-level governance framing. That proposal is superseded. Evidence and source references remain useful supporting information within the approved Encyclopedia → ProductKnowledge path.
