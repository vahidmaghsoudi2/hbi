# Knowledge Base Index

**Last Updated:** 2026-11-18  
**Architecture authority:** [HBI-PO-DEC-CKER-001 — Central Knowledge & Evidence Repository](../03_decision_log/HBI-PO-DEC-CKER-001.md)

## Purpose

This index locates HBI's curated knowledge and its canonical domain records within the single logical **HBI Central Knowledge & Evidence Repository (CKER)**.

CKER is the shared source-of-truth boundary for HBI knowledge and supporting Evidence. It is not a new database or a second GitHub repository. The existing HBI repository and its governed runtime records remain the canonical project surfaces.

## Knowledge layers and canonical locations

| Layer / purpose | Canonical location | Responsibility |
|---|---|---|
| Curated knowledge / Encyclopedia | docs/homepage/encyclopedia/ | Human-readable, reviewed knowledge entries and navigation across knowledge domains |
| Skin product research dossiers | docs/homepage/encyclopedia/skin/PRODUCTS.md | Source-linked research dossiers; not Product Master records or automatic ProductKnowledge approval |
| Skin Problem Space | docs/product-intake-knowledge-registry/SKIN_PROBLEM_BANK_WORKSPACE_INDEX.md and its linked working records | Specialist canonical problem-bank records; referenced, not copied into the Encyclopedia |
| Product-scoped operational knowledge | ProductKnowledge model / app/services/product_knowledge_service.py | Runtime projection used by the product/recommendation path, governed by evaluated Evidence |
| Product identity | Existing Product Master / Product records | Canonical product identity; not owned or replaced by CKER |

## Knowledge-entry rules

1. The Encyclopedia is HBI's curated knowledge core. It may present approved synthesis, definitions, product characteristics and domain guidance.
2. The Encyclopedia does not replace or obscure the original manufacturer page, package label, scientific publication, regulatory source or other primary artifact. Link the source and retain enough provenance to identify the exact claim and scope.
3. Material factual assertions in a knowledge entry must be traceable to atomic Evidence claims. Keep manufacturer claims, independent evidence, inference, UNKNOWN and CONFLICT distinct.
4. Review has two separate dimensions: claim-level Evidence QA and editorial review of the knowledge entry. Editorial approval cannot silently promote an Evidence claim.
5. Do not create parallel product banks, Evidence ledgers or duplicate Problem Space records. Link to the canonical specialist record.
6. Do not treat an Encyclopedia entry as ProductMaster, ProductKnowledge, Product QA, lifecycle approval or recommendation eligibility.
7. Preserve existing product scope, market/variant boundaries and explicit UNKNOWN/CONFLICT states.

## Relationship to Evidence

Structured Evidence is an internal CKER layer indexed in [EVIDENCE_INDEX.md](../07_evidence/EVIDENCE_INDEX.md). It is not a competing knowledge repository. ProductKnowledge is populated only under the current Evidence evaluation and aggregation contract; a research draft or unreviewed article is not sufficient.

## Historical note

The previous A–D (ISDIN) freeze note belongs to an earlier project snapshot. It must not be generalized to the current seven-product Skin V1 scope or treated as a current statement of all Knowledge Base contents. Current product scope and permissions remain in their governing Issue/decision records.
