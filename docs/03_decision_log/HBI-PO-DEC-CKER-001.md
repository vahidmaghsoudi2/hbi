# HBI-PO-DEC-CKER-001 — Central Knowledge & Evidence Repository

**Decision ID:** HBI-PO-DEC-CKER-001  
**Decision date:** 2026-11-18  
**Authority:** Product Owner (PO)  
**Status:** **PO DECIDED — DOCUMENTATION PR DRAFT**  
**Decision scope:** Knowledge and Evidence architecture / governance  
**Implementation status:** Documentation decision only; no runtime, schema, API, UI, database, or data-write authorization is granted by this record.

## 1. Decision

HBI shall use one logical central repository and one governing source-of-truth boundary for curated knowledge and its supporting Evidence:

**HBI Central Knowledge & Evidence Repository (CKER)**

The CKER is the single governed home for HBI's curated, source-traceable knowledge and its structured Evidence. It is a logical architecture boundary over the existing canonical repository and runtime records. It is **not** a new standalone GitHub repository, a second Evidence database, a new ORM entity/table, or a replacement Product Master.

The existing **دانشنامه (Encyclopedia)** is the human-facing, curated knowledge core and primary knowledge-navigation surface of the CKER. The structured **Evidence** layer is an internal first-class component of the same CKER, not a competing repository.

No parallel Evidence repository shall be created.

## 2. Knowledge and Evidence are complementary, not competing sources

CKER contains two linked but distinct information layers:

1. **Curated Knowledge / Encyclopedia**
   - Human-readable, organized and reviewed knowledge entries.
   - Presents HBI's approved understanding in a usable form.
   - Every factual or product-specific assertion must remain traceable to its supporting Evidence and original source.
   - Editorial review of an entry checks synthesis, scope, clarity and internal consistency; it does not replace QA of the individual claims.

2. **Structured Evidence**
   - Atomic, source-bound claims that support, qualify, contradict or leave a knowledge assertion unknown.
   - Each Evidence record retains its own identity, claim text, source reference/type, claim type, QA state, conflict state and applicable product/field/market scope.
   - Evidence remains inside CKER as a structured layer. It is not a separate source-of-truth repository.

The encyclopedia may be the authoritative HBI knowledge synthesis, but it must never pretend to be the original manufacturer document, package label, scientific paper, regulatory record or other primary source. Original source artifacts remain independently identifiable and linked.

## 3. Source, claim and provenance rules

For each atomic claim, preserve the applicable existing Evidence contract and fields, including:

- evidence_id and claim_id;
- claim and field;
- source_type and source_reference;
- claim_type;
- qa_status, conflict_status, evidence_status and evidence_strength;
- source_date and evidence_date;
- market_region, where applicable;
- notes, where required to preserve context or limitations.

source_type and claim_type are different dimensions and must not be conflated. The current canonical claim taxonomy is:

- FACT
- MANUFACTURER_CLAIM
- EVIDENCE
- INFERENCE
- UNKNOWN
- CONFLICT

Use the current project vocabulary and validation rules; this decision does not introduce replacement enums or silently migrate existing values.

Source authority is claim-specific. A manufacturer page can substantiate what the manufacturer claims; it does not automatically establish independent scientific truth. A physical package supports claims about that specific package/variant. Scientific and regulatory sources support only the propositions within their scope. No universal source ranking or majority-vote conflict resolution is introduced here.

## 4. Atomic QA and knowledge-entry review

- QA is performed at the level of each independently assessable Evidence claim.
- A page-level or article-level approval must never promote all underlying claims implicitly.
- A knowledge entry may be marked reviewed/approved only when its material claims link to Evidence with explicit states; unresolved claims must remain visibly UNKNOWN, CONFLICT, PENDING or otherwise in their existing valid state.
- Conflicting claims are preserved with their lineage and scope. Resolution requires an explicit, reason-bearing action under the existing governance path.
- A claim's QA approval is not the same as permission to use it in a recommendation.

## 5. Audit history and versioning boundary

The current runtime includes EvidenceMutationLog, an append-only audit trail with actor, role, timestamp, action, target, before/after snapshots, diff, reason, resulting state and correlation ID.

This is verified mutation traceability. It must **not** be overstated as a complete immutable Evidence versioning system: the current Evidence model does not expose a dedicated immutable revision identifier or a separate version chain. Any stronger revision/version contract requires a later, evidence-based design and explicit authorization. No schema change is approved by this ADR.

## 6. Relationship to ProductKnowledge and operational gates

The canonical flow is:

Original source → atomic Evidence claim → curated CKER knowledge / Encyclopedia → ProductKnowledge projection → eligibility gates → Recommendation

The flow describes governance and derivation, not automatic activation.

- ProductKnowledge remains the product-scoped operational projection consumed by the runtime; it is not a second master knowledge repository.
- ProductMaster continues to own product identity.
- ProductKnowledge may be populated/rebuilt only through its existing evaluated-Evidence rules; draft, pending, unknown or conflicted claims must not be silently treated as approved knowledge.
- Product QA/lifecycle, Inventory availability, G8, consultation evidence and Recommendation eligibility remain independent gates.
- CKER approval, article publication or Evidence QA approval cannot bypass any of those gates.
- Problem Space and other specialist domain registries retain their canonical records. CKER provides the shared governance boundary and discoverability; it does not authorize copying those records into a parallel bank.

## 7. Existing implementation reality

The current repository already contains an Evidence model with atomic claim and provenance fields, a canonical claim taxonomy, Evidence services, ProductKnowledge aggregation, and an append-only Evidence mutation audit model/service.

The current model does not, by itself, prove that every encyclopedia article is linked claim-by-claim to Evidence, that every article has editorial QA metadata, or that full immutable Evidence versioning exists. Those are documented architecture requirements/gaps, not claims of completed implementation.

## 8. Scope and explicit non-goals

This decision is architectural and documentation-level only.

It does **not** authorize:
- a new database table/entity or schema migration;
- a second GitHub repository or separate Evidence store;
- code, API, UI or workflow changes;
- direct Product, Evidence, ProductKnowledge, Inventory, QA, lifecycle, G8, ProductProblemLink or Recommendation writes;
- Evidence QA promotion, conflict resolution, or automatic claim approval;
- changes to the seven-product Skin V1 scope or its manufacturer/package-only evidence boundary;
- changes to Issue #406, PR #411, PR #523, PR #594 or any other existing work item.

Any implementation gap must be assessed against the current repository and contracts first, then submitted as a separate scoped proposal for PO authorization.

## 9. Previous / New / Reason / Impact / Owner / Approval

| Dimension | Record |
|---|---|
| Previous | Knowledge/Encyclopedia and Evidence could be read as separate competing repositories or as though the encyclopedia merely navigates to evidence elsewhere. |
| New | One logical CKER; Encyclopedia is its curated knowledge core; atomic Evidence is an internal structured layer; no parallel Evidence repository. |
| Reason | Preserve one source-of-truth boundary while retaining claim-level QA, source provenance, conflict handling and auditability. |
| Impact | Aligns architecture, Knowledge Index, Evidence Index and Encyclopedia documentation. Does not change runtime data or operational gates. |
| Owner | Product Owner |
| Approval | PO direction recorded 2026-11-18; human review of this Draft PR remains required before merge. |

## 10. Acceptance checks for this documentation decision

- [x] One central CKER is named and defined.
- [x] Encyclopedia is identified as the curated knowledge core, not a primary-source substitute.
- [x] Evidence is an internal structured layer, not a parallel repository.
- [x] Claim-level QA and source provenance remain mandatory.
- [x] ProductKnowledge, ProductMaster and operational gates remain separate.
- [x] Existing implementation facts are distinguished from requirements and gaps.
- [x] No runtime/schema/data mutation is included.
- [ ] Human review and merge of the documentation PR.

---
**Baseline reviewed:** master @ 603247acbee5d4b978fcf6bca2430cc9fe3197e5  
**Agent:** GPT-6 (ChatGPT GitHub connector), 2026-11-18  
**Validation:** repository paths and current model/contract references inspected; documentation-only diff; no application tests or runtime database access performed.
