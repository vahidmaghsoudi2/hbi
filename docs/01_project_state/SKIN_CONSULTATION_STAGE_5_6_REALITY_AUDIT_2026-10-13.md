# Skin Consultation Intelligence — Stage 5–6 Reality Audit

**Audit date:** 2026-10-13  
**Repository:** `vahidmaghsoudi2/hbi`  
**Audited baseline:** `cc7848e472b837746e99103ea94ff4bb28eb0c2b` (the base pinned by PR #357)  
**Scope:** Roadmap Phase 5 — Human review and decision checkpoint; Phase 6 — Need formulation and ProductKnowledge/evidence readiness.  
**Authority:** Reality audit and bounded-WP definition only. No schema/API/migration/clinical rule/scoring change or merge is included.

## Executive decision

- **Phase 5 — Human review:** **PARTIAL / NOT VERIFIED**. The repository has a Case-level `operator_override`, `reasoning_status`, and `confidence` surface, and the Product Intake evidence conflict API exists. The audited evidence does not establish an auditable consultation-hypothesis review flow that records which hypotheses were retained/removed, the actor, rationale, supporting/contradicting evidence, and the resulting decision state.
- **Phase 6 — Need + ProductKnowledge:** **PARTIAL**. Existing canonical need normalization, Evidence records, QA/conflict checks, ProductKnowledge aggregation, and evidence references provide real building blocks. However, the audited ProductKnowledge representation is largely flattened string fields; the inspected rebuild path does not set `ProductKnowledge.evidence_status`, and dedicated structured `target_concerns`, `active_ingredients`, and `avoid_conditions` fields are not established by the inspected model.
- **No implementation claim:** this document records repository-level evidence only. No live browser/operator session was executed as part of this audit.

## Evidence and reality matrix

| Capability | Current repository evidence | Status | Gap / boundary |
|---|---|---|---|
| Case stores current consultation state | `app/models/case.py`: `identified_needs`, `evidence_gaps`, `operator_override`, `reasoning_status`, `confidence` | PARTIAL | These generic fields do not themselves prove a per-hypothesis review/decision history or actor/reason audit trail. |
| Profile context preserves current input precedence and provenance | `app/services/profile_fact_context_service.py`: current consultation input takes precedence when present; active ProfileFacts include provenance; multiple active facts are surfaced as `CONFLICTED`; unknown states are recorded separately | VERIFIED EXISTING at service level | This is a read-only projection; it is not a human hypothesis-review workflow and does not write durable ProfileFacts. Runtime/browser behavior not re-executed here. |
| Evidence can be created and reviewed | `app/api/routers/evidence.py`; `app/models/evidence.py`; `app/services/evidence_service.py` | VERIFIED EXISTING at code level | Evidence QA/conflict operations concern product evidence; they are not equivalent to consultation hypothesis selection. Current-master claim-taxonomy enforcement must not be inferred from unmerged PRs. |
| ProductKnowledge rebuild respects QA/conflict boundary | `app/services/product_knowledge_service.py:update_from_evidence` includes only QA `APPROVED`/`VERIFIED` rows and excludes `CONFLICT` rows | VERIFIED EXISTING at service level | Does not by itself prove the entire Research → Evidence → QA → ProductKnowledge path in a live runtime. |
| ProductKnowledge captures ingredient/use/claim information | `app/models/product_knowledge.py` and `ProductKnowledgeService.update_from_evidence` include ingredients, ingredient roles, claimed benefits, known use cases, contraindications, usage instructions, manufacturer claims, evidence refs, confidence | PARTIAL | Mostly flattened string aggregates; not a per-ingredient source/concentration/formulation model. Ingredient presence alone is not efficacy evidence. |
| ProductKnowledge evidence readiness status | Model has constrained `evidence_status` values (`SUPPORTED`, `PARTIAL`, `CONFLICT`, `UNKNOWN`) | PARTIAL / NOT VERIFIED | The inspected `update_from_evidence` `update_data` does not assign `evidence_status`. Confirm intended writer/reader and existing tests before proposing a minimal fix. |
| Structured concern/active/avoid fields | Not present in the inspected `ProductKnowledge` model | NOT VERIFIED / candidate gap | Do not add fields or migration before a bounded field contract and explicit implementation WP. |
| Human review UI for consultation hypotheses | No audited source evidence found that connects hypothesis keep/remove decisions to a persisted actor/reason/state transition | NOT VERIFIED | Do not treat Product Intake's evidence conflict-resolution UI (proposed on unmerged PR #357) as consultation hypothesis review. |
| Existing recommendation boundary | `app/services/recommendation_service.py` is the existing downstream service; roadmap requires reuse without score/rank redesign | VERIFIED EXISTING at code level | This audit authorizes no recommendation scoring, ranking, or eligibility change. |
| Automated/runtime proof for these phases | Not run as part of this documentation audit | NOT VERIFIED | A future implementation WP must provide exact-head CI plus focused runtime/browser evidence for the bounded behavior. |

## Stage 5 — Human review and decision checkpoint

### What exists
1. Case-level fields can represent some current state (`operator_override`, `reasoning_status`, `confidence`).
2. ProfileFact context projection preserves source distinctions, current-consultation precedence, unknowns, and conflicts.
3. Product Evidence has a separate QA/conflict review boundary.

### What is not established
The inspected sources do not prove a complete consultation review action that:
- displays remaining hypotheses with supporting, weakening, missing, and conflicting evidence;
- records explicit retain/remove decisions per hypothesis;
- requires and persists a decision reason;
- records the acting reviewer and review timestamp;
- reconstructs the before/after decision state;
- keeps human assessment separate from a medical diagnosis.

### Smallest proposed WP — `WP-SKIN-HUMAN-REVIEW-001`
**First step:** inspect existing hypothesis/consultation models, endpoints, UI and audit logs, then define an acceptance contract before coding. Reuse existing Case and audit facilities where adequate. Do not add a parallel lifecycle or diagnosis engine.

**Acceptance tests required before implementation is considered complete:**
1. A reviewer can view the current bounded candidate paths and their evidence/uncertainty.
2. Retain/remove requires an explicit action and non-empty rationale.
3. Actor, timestamp, prior state, resulting state, and rationale are reconstructable.
4. Unknown/conflicting/insufficient evidence remains visible; review cannot silently promote inference to fact.
5. A reviewer decision is not represented as a medical diagnosis.
6. Persistence and readback are proven through the actual API and operator UI.
7. No recommendation scoring/ranking changes; no automatic ProfileFact write.
8. Tests and runtime evidence are pinned to the exact tested SHA.

## Stage 6 — Need formulation and ProductKnowledge/evidence readiness

### What exists
1. `app/services/need_normalization.py` is imported by the existing RecommendationService for canonical needs.
2. Evidence rows carry source reference, claim type, field, QA/conflict status, and evidence strength.
3. ProductKnowledge aggregation filters to approved/verified, non-conflicting Evidence and stores aggregated product attributes plus evidence references.
4. The product knowledge model has an `evidence_status` column with a constrained vocabulary.

### Gaps requiring reconciliation
1. **Evidence status writer:** the inspected `update_from_evidence` method does not set `evidence_status`. Trace all writers/readers and tests before deciding whether this is a confirmed implementation gap or a separate status-maintenance path.
2. **Claim taxonomy baseline:** PR #353 and PR #357 are unmerged at this audit baseline. Their branch-level claim-taxonomy work must not be represented as current-master behavior. Stage 6 must be tested against the chosen integration head and must not duplicate or silently conflict with either PR.
3. **Structured skin intelligence:** `target_concerns`, `active_ingredients`, and `avoid_conditions` are not present in the inspected ProductKnowledge model. A field contract must define semantics, source/provenance, empty-vs-unknown, lifecycle/readiness, and consumers before any schema change.
4. **Finished-product efficacy:** ingredient presence or manufacturer claims alone cannot be treated as independent proof of finished-product efficacy.
5. **Traceability:** a joined ProductKnowledge value must remain traceable to its evidence source and review state; the current aggregated strings do not prove per-attribute provenance in the UI.

### Smallest proposed WP — `WP-SKIN-PRODUCT-KNOWLEDGE-READINESS-001`
**First step:** write a field/readiness contract and a source-to-consumer trace matrix; verify every writer, reader, test and endpoint for `evidence_status`; reconcile the integration dependency on PR #353/#357. Do not create new schema or migration in this audit.

**Acceptance tests required before implementation is considered complete:**
1. PENDING, REJECTED, and unresolved CONFLICT evidence cannot populate trusted ProductKnowledge.
2. Approved/verified evidence retains claim type and source provenance at the authoritative Evidence boundary.
3. `evidence_status` has a documented deterministic derivation and is persisted/read back, or the contract explicitly explains why another authoritative status path is used.
4. EMPTY, UNKNOWN, CONFLICT, and supported/verified values remain distinct.
5. Manufacturer claim, independent evidence, and inference remain distinguishable; inference never silently becomes FACT.
6. Ingredient presence does not automatically assert finished-product efficacy.
7. Need formulation remains separate from product eligibility, customer suitability, inventory, and recommendation ranking.
8. No new field/schema/migration until its contract and exact WP scope are accepted.
9. Focused tests, regression CI, and actual API/UI readback are pinned to the tested SHA.

## Dependencies and non-goals

- PR #357: Draft/unmerged at head `66b6f686b2f846267371a164093f86b9b97576c9`; its stages 3–4 acceptance is not merge authorization and its branch changes are not current-master behavior.
- PR #353: Draft/unmerged claim-integrity work; do not duplicate its implementation or assume its changes are present in master.
- Approved contract `docs/architecture/SKIN_PRODUCT_INTAKE_EXECUTION_CONTRACT_v1.1.md` remains authoritative for product intake.
- No new schema, migration, ontology, questionnaire engine, diagnosis engine, AI pipeline, product-comparison subsystem, or scoring/ranking/eligibility redesign.
- No Product A–D changes, no production-data mutation, and no merge.

## Audit provenance

- Baseline SHA: `cc7848e472b837746e99103ea94ff4bb28eb0c2b`, as pinned by PR #357 base metadata.
- Inspected sources:
  - `app/models/case.py`
  - `app/services/profile_fact_context_service.py`
  - `app/models/evidence.py`
  - `app/services/evidence_service.py`
  - `app/models/product_knowledge.py`
  - `app/services/product_knowledge_service.py`
  - `app/services/recommendation_service.py`
  - `app/api/routers/evidence.py`
  - `docs/architecture/HBI_SKIN_CONSULTATION_INTELLIGENCE_ROADMAP_v1.0.md` on PR #348 head `1e8697b70380b03309c6bace5edacf6954842e10` (roadmap proposal; not merged).
- Test execution: none; documentation-only audit.
- Runtime/browser execution: none.
- Production behavior: unchanged.
- Merge authorization: none.

**Decision:** Stage 5 and Stage 6 reality audit recorded. Proceed next by authorizing one bounded implementation WP at a time after its exact data/behavior contract is settled. G8 remains BLOCKED / NOT VERIFIED.
