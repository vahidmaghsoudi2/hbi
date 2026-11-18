# Evidence Index

**Last Updated:** 2026-11-18  
**Architecture authority:** [HBI-PO-DEC-CKER-001 — Central Knowledge & Evidence Repository](../03_decision_log/HBI-PO-DEC-CKER-001.md)

## Purpose and repository boundary

Evidence is the structured, atomic claim layer **inside** the single logical HBI Central Knowledge & Evidence Repository (CKER). It is not a separate repository, a competing knowledge base, or a substitute for original source artifacts.

The Encyclopedia is CKER's curated knowledge core. Evidence records support, qualify, contradict or leave individual knowledge claims unknown. Original source documents and package artifacts remain independently identifiable and linked.

## Existing runtime locations

| Component | Canonical location | Verified responsibility |
|---|---|---|
| Evidence record | app/models/evidence.py | Atomic product claim, source reference/type, claim type, field and scope, QA/conflict/evidence states |
| Claim taxonomy | app/domain/claim_taxonomy.py | Canonical claim types: FACT, MANUFACTURER_CLAIM, EVIDENCE, INFERENCE, UNKNOWN, CONFLICT |
| Evidence service | app/services/evidence_service.py | Evidence creation, claim-boundary validation, conflict detection and verification |
| Evidence audit model | app/models/evidence_mutation_log.py | Append-only before/after mutation audit |
| Evidence audit service | app/services/evidence_mutation_log_service.py | Actor, role, timestamp, action, target, snapshots, diff, reason and correlation ID |
| ProductKnowledge aggregation | app/services/product_knowledge_service.py | Builds/refreshes product-scoped knowledge from evaluated Evidence under existing rules |
| Research source dossiers | docs/homepage/encyclopedia/skin/PRODUCTS.md | Human-readable, source-linked research; not itself a QA promotion or DB import |

## Atomic claim record

The current Evidence model exposes these relevant fields:

- Identity and linkage: evidence_id, claim_id, product_id.
- Claim: claim, field, claim_type.
- Source/provenance: source_type, source_reference, source_date, evidence_date, market_region, notes.
- Evaluation: evidence_strength, evidence_status, qa_status, conflict_status.

Keep source_type distinct from claim_type. The claim taxonomy is not a recommendation score or operational eligibility flag.

## Governance rules

1. Each independently assessable assertion should have its own traceable Evidence identity and source reference.
2. Keep the claim's product, field, market and version context where known; do not transfer claims across variants or markets without evidence.
3. Preserve manufacturer claims as manufacturer claims. A manufacturer source supports attribution of what the manufacturer states; it does not automatically establish independent truth.
4. Use primary sources wherever they directly support the proposition. Package text is authoritative for the specific physical package; regulatory sources for the relevant regulatory proposition; scientific sources for the specific scientific proposition.
5. QA and conflict status are evaluated per claim. Page-level Encyclopedia approval cannot promote or overwrite individual Evidence states.
6. Preserve conflicts and their lineage. Resolution must use the existing explicit, audited governance path; do not use majority vote or silent overwrite.
7. Only Evidence states accepted by the existing ProductKnowledge aggregation contract may contribute to operational ProductKnowledge. Pending, unverified, unknown or conflicted claims must not be treated as approved facts.
8. Evidence QA approval is not Product QA, lifecycle activation, inventory availability, G8 acceptance or Recommendation eligibility.
9. Do not create a parallel Evidence repository or duplicate ledger. The Encyclopedia and Evidence are linked layers within CKER.

## Audit and version-history boundary

EvidenceMutationLog is append-only and captures mutation actor, role, timestamp, action, before/after state, diff, reason and correlation ID. This provides mutation traceability.

The current model does not expose a dedicated immutable Evidence revision ID/version chain. Do not claim full immutable versioning is implemented. Any stronger versioning contract requires a separate reality audit, design and explicit authorization; no schema change is authorized by this index.

## Status boundary

UNKNOWN stays UNKNOWN. CONFLICT stays visible until explicitly resolved. The current seven-product Skin V1 evidence scope and permissions remain governed by the latest PO direction in [Issue #406](https://github.com/vahidmaghsoudi2/hbi/issues/406); this index does not broaden that scope or authorize any Evidence write or QA promotion.
