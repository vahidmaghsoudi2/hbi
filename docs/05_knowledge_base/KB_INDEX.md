# ProductKnowledge Index

**Last Updated:** 2026-11-18  
**Architecture authority:** [HBI-PO-DEC-THREE-PART-001](../03_decision_log/HBI-PO-DEC-THREE-PART-001.md)  
**Encyclopedia source-of-truth decision:** [HBI-PO-DEC-ENCYCLOPEDIA-PRIMARY-KB-001](https://github.com/vahidmaghsoudi2/hbi/issues/406#issuecomment-6989651765)

## Purpose

ProductKnowledge is HBI's **single operational runtime bank** of accepted product information. It supplies the product facts that the Intelligence & Response part connects with Customer Context.

The human-curated source of truth for approved product knowledge is the Encyclopedia. This is a division of responsibility, not a second product bank or a fourth architecture pillar.

## Product-information path

`Approved Encyclopedia → Evidence / Source Traceability → ProductKnowledge → Consultation`

1. The Product Owner defines the product, scope, standards and acceptance criteria.
2. Research and review organize the requested information through the Encyclopedia workflow.
3. Approved product knowledge is maintained in the Encyclopedia, with links to original manufacturer, package, technical and relevant scientific sources.
4. Original source documents are preserved and are not replaced by summaries.
5. Evidence and Source Traceability support provenance and checking; they do not form a separate repository or approval stage.
6. After PO approval, the accepted information is made available in ProductKnowledge for runtime use.

**PO approval completes content acceptance. Do not add another content approval or QA gate after it.** Existing safety and lifecycle controls remain separate and unchanged.

## Canonical locations

| Purpose | Canonical location | Responsibility |
|---|---|---|
| Architecture and intake decision | [HBI-PO-DEC-THREE-PART-001](../03_decision_log/HBI-PO-DEC-THREE-PART-001.md) | Governing three-part model |
| Human-curated approved product knowledge | `docs/homepage/encyclopedia/` | Primary, live, editable reference for approved knowledge |
| Skin product dossiers | [docs/homepage/encyclopedia/skin/PRODUCTS.md](../homepage/encyclopedia/skin/PRODUCTS.md) | Approved knowledge plus explicitly labeled research drafts and source links |
| Supporting source traceability | `docs/07_evidence/EVIDENCE_INDEX.md` and existing Evidence records | Provenance and source checking; not a parallel bank |
| Operational product knowledge | ProductKnowledge model and `app/services/product_knowledge_service.py` | Runtime representation consumed by HBI |
| Product identity | Existing Product Master / Product records | Canonical product identity; not replaced by this index |
| Original source documents | Manufacturer/package/technical/scientific source records | Primary evidence; preserve and link, never replace with a summary |

## Use rules

1. The Encyclopedia is the primary human-curated source for approved product knowledge.
2. ProductKnowledge is the one operational runtime bank; do not create another operational bank.
3. Keep original source documents and relevant limitations traceable from the Encyclopedia.
4. Distinguish `MANUFACTURER_CLAIM`, independent evidence, observation and inference; never silently upgrade a claim.
5. Do not invent missing facts. Keep `UNKNOWN`, `CONFLICT` and partial coverage explicit.
6. PO approval completes content acceptance; no duplicate post-approval content gate.
7. ProductKnowledge does not replace Product Master identity, inventory state, product lifecycle or other existing operational controls.
8. ProductKnowledge is one of the three HBI architecture parts; Customer Context and Intelligence & Response are defined in the governing decision.

## Historical note

The former CKER proposal is superseded. Its separate top-level framing and proposed additional stages are not current HBI architecture. See [the superseded decision notice](../03_decision_log/HBI-PO-DEC-CKER-001.md).
