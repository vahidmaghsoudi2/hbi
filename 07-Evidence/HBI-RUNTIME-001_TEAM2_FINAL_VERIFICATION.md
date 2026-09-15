# HBI-RUNTIME-001 — Team 2 Final Independent Verification

**Mission:** HBI-RUNTIME-001 / A2A-COM-007  
**Repository:** `vahidmaghsoudi2/hbi`  
**Verification branch:** `audit/hbi-runtime-001-final-verification/20260915`  
**Verified master:** `8d0c7dfff7de5f332c867d0808302b01cc7e1616`  
**Declared WP-01 baseline:** `f1e3af0c9c864ef41317ff71277abb24946f4b65`  
**Verification date:** 2026-09-15  
**Implementation authorization:** NOT GRANTED  
**Master modification:** NONE by this verification artifact

## 1. Verification purpose

This artifact independently verifies the Team-2 WP-02 handoff and integrates it with the previously recorded WP-01 runtime trace. The verification is against the repository as it exists now, not only against the WP-02 handoff baseline.

The current master moved forward after the original WP-01/WP-02 baseline through HBI-RUNTIME-002 (`PR #77`), merged as `8d0c7dfff7de5f332c867d0808302b01cc7e1616`. Therefore, claims affected by that change were re-checked against current master.

No implementation was performed as part of this verification.

## 2. Independent verification result

### WP-02 — VERIFIED WITH ONE CONFIRMED RUNTIME GAP

The major WP-02 claims are supported by current repository evidence:

- Recommendation API ownership enforcement is real: `/generate` and case-listing require authenticated customer identity and verify Case ownership.
- Recommendation runtime is connected through Facade → Service → Product/ProductKnowledge/Evidence/Inventory repositories → ReasoningEngine → Recommendation upsert.
- ProductKnowledge is actually consumed in the decision runtime. `known_use_cases` participates in `need_match`; other ProductKnowledge fields are passed as the reasoning snapshot.
- Evidence is actually consumed by the runtime, but the scoring path uses all rows returned by `find_by_product()` and does not filter by `qa_status`.
- Inventory participates before reasoning. Candidate selection joins Inventory and requires positive available quantity; the service also skips zero inventory before reasoning.
- Current Recommendation persistence is an upsert keyed by Case/Product and is covered by the existing persistence test path. There is no separate Recommendation history table in the current model path.
- The current Recommendation API is customer-scoped rather than staff-role-scoped. This is an access-surface distinction, not a verified defect by itself.
- Product-side mutation logging exists; Recommendation generation does not have a dedicated historical decision/audit record.

### WP-02 GAP-WP02-01 — CONFIRMED

**Finding:** Recommendation evidence scoring is not QA/readiness filtered.

**Repository evidence:**
- `EvidenceRepository.find_by_product()` returns all Evidence rows for the product.
- `EvidenceRepository.find_unverified()` exists for `PENDING` / `NEEDS_REVIEW` rows but is not called by RecommendationService generation.
- `RecommendationService._compute_evidence_score()` weights evidence by `source_type` only and does not inspect `qa_status` or `evidence_status`.
- The resulting `evidence_score` is passed into `ReasoningEngine` and then `MatchScoringEngine`.

**Impact:** Pending/unverified Evidence can affect the evidence score and therefore the downstream eligibility/scoring path.

**Classification:** Runtime integration/quality GAP. This is not an authorization to implement a fix and does not change the frozen scoring weights.

## 3. Current-master update: HBI-RUNTIME-002

The original WP-02 handoff predates the current master merge. Current master includes HBI-RUNTIME-002 (`PR #77`, merged as `8d0c7dfff7de5f332c867d0808302b01cc7e1616`).

That change is independently visible in `RecommendationService` and `ReasoningEngine`:

- Evidence rows now carry `conflict_status` into the reasoning input.
- `RecommendationService._existing_conflicts_from_evidence()` constructs existing conflicts from Evidence rows marked `CONFLICT`.
- `ReasoningEngine` analyzes those conflicts.
- If conflicts exist and the frozen score would otherwise be `ELIGIBLE`, the engine changes eligibility to `NEEDS_REVIEW` without changing score weights.
- RecommendationService maps `NEEDS_REVIEW` to `INELIGIBLE_PENDING_REVIEW`.
- Dedicated tests for this propagation exist in `tests/test_runtime_002_evidence_conflict_wiring.py`.

Therefore the older WP-02 handoff statement that the Evidence conflict path was merely absent is stale; the current repository has that integration.

## 4. WP-01 independent verification

The WP-01 package is substantively consistent with current repository reality on the core runtime path:

`Customer/Case ownership → Recommendation API → RecommendationFacade → RecommendationService → Decision State → GAP-05 Need normalization → verified/active/stocked candidate selection → ProductKnowledge + Evidence + Inventory → ReasoningEngine → scoring/eligibility → Recommendation upsert → DTO`

The following WP-01 findings remain verified:

1. Decision State is computed in memory in the current MVP and is not persisted as a separate Decision State entity. The accepted Decision Contract explicitly permits this for MVP.
2. Need normalization is controlled and does not silently convert unresolved input into a canonical Need.
3. ProductKnowledge, Evidence, and Inventory are real runtime inputs.
4. Recommendation persistence retains the current recommendation row but not the complete ReasoningResult/provenance surface.
5. DTO mapping reconstructs confidence from persisted `need_match_score` and `evidence_score`; it does not persist the engine's complete confidence/provenance result.
6. Product-level unknown/conflict results remain local to the product evaluation path rather than being appended to the shared Case Decision State dictionary.
7. Candidate Recommendations can be persisted with an eligibility status and then sorted by ranking score. This is a runtime conformance concern because the accepted Decision Contract says failed hard gates must not be rescued by ranking. The present evidence establishes the ordering behavior, but not that an ineligible item is necessarily surfaced to the end customer as an eligible recommendation.

## 5. End-to-end runtime map

```text
Authenticated Customer
        |
        v
Case ownership check
        |
        v
POST /api/v1/recommendations/generate
        |
        v
RecommendationFacade.generate
        |
        v
RecommendationService.generate_recommendations
        |
        +--> Decision State from caller-supplied customer_profile
        |       |
        |       +--> GAP-05 Need normalization
        |
        +--> ProductRepository candidate selection
        |       +--> identity VERIFIED
        |       +--> non-DRAFT
        |       +--> positive Inventory
        |
        +--> ProductKnowledgeRepository
        |       +--> known_use_cases -> need_match
        |       +--> knowledge snapshot -> ReasoningEngine
        |
        +--> EvidenceRepository.find_by_product
        |       +--> all Evidence rows
        |       +--> source_type -> evidence_score
        |       +--> conflict_status -> existing_conflicts
        |
        +--> InventoryRepository
        |       +--> inventory_score / OOS guard
        |
        +--> ReasoningEngine
        |       +--> Unknown / Conflict / Claim validation
        |       +--> MatchScoringEngine
        |       +--> eligibility pressure from conflicts
        |
        +--> Recommendation upsert (Case/Product current row)
        |
        +--> ranking_score sort
        |
        v
RecommendationDTO
        |
        +--> API response
```

## 6. Verified facts vs unresolved items

### VERIFIED

- The decision runtime is an actual connected chain, not a set of unused components.
- Customer-to-Case ownership is enforced on the Recommendation API.
- ProductKnowledge participates in need matching and reasoning input.
- Evidence participates in scoring and reasoning input.
- Inventory gates the candidate path before reasoning for zero stock.
- Recommendation current-row upsert is implemented.
- Evidence conflict status now reaches the reasoning/eligibility path on current master.
- Need normalization rejects unresolved meaning rather than silently guessing.

### CONFIRMED GAP

- `GAP-WP02-01`: unfiltered Evidence consumption in evidence scoring. QA/readiness state is not a scoring filter.

### OBSERVATIONS, NOT CONFIRMED GAPS

- No Recommendation history/snapshot table. This remains outside the prior GAP-04 scope.
- Double OOS protection exists at repository and service layers. Redundant, but not a correctness failure.
- ProductKnowledge ingredients are passed to ReasoningEngine but are not an independent numeric input to the frozen MatchScoringEngine formula. This is not a new policy decision.
- Recommendation API uses customer ownership rather than staff role matrix. This is consistent with a customer-facing decision surface unless a separate staff-only requirement is introduced.
- Full Decision State persistence is absent, but the accepted MVP contract explicitly permits in-memory Decision State.

### UNKNOWN / NOT RE-ASSERTED

- Live full-suite CI status for current master was not executable from this verification environment. Repository test files were inspected, but no claim of a fresh local full-suite pass is made.
- Whether products without an Inventory row should be candidates is not determined by the current code. The current inner join excludes them.
- Whether the DTO should expose the full computed evidence references/warnings is a traceability/product-contract decision, not proven solely by the current code.

## 7. Governance result

| State | Result |
|---|---|
| WP-02 work | DONE by original owner, independently re-checked here |
| WP-02 verification | VERIFIED with GAP-WP02-01 confirmed |
| WP-01 | VERIFIED on core runtime trace |
| Integrated Team-2 package | DONE / VERIFIED |
| Implementation authorization | NOT GRANTED |
| PO acceptance | NOT GRANTED by this artifact |
| Master merge | NOT PERFORMED by this artifact |

## 8. Required next decision

The only clearly evidence-backed runtime GAP that requires a product/governance decision before implementation is:

**GAP-WP02-01: Should Recommendation evidence scoring consume only QA/readiness-approved Evidence?**

If PO approves that semantic requirement, it becomes a separate implementation authorization item. This verification does not implement it.

## 9. Evidence index

- `app/api/routers/recommendations.py`
- `app/interface/facades.py`
- `app/services/recommendation_service.py`
- `app/repositories/product_repository.py`
- `app/repositories/evidence_repository.py`
- `app/reasoning/reasoning_engine.py`
- `app/models/product.py`
- `docs/02_architecture/HBI_DECISION_CONTRACT_v1.0.md`
- `tests/test_runtime_002_evidence_conflict_wiring.py`
- Issue #70 WP-02 handoff comment
- Issue #73 WP-01 execution/handoff state
- PR #77 / merge commit `8d0c7dfff7de5f332c867d0808302b01cc7e1616`

**Final statement:** Team 2 runtime/product audit is independently verified at the current repository state. The repository evidence supports one confirmed runtime GAP concerning unfiltered Evidence scoring. No implementation has been authorized or performed by this verification.
