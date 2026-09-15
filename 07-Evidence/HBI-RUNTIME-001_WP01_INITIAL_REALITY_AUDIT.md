# HBI-RUNTIME-001 / WP-01 — Initial Reality Audit

**Owner:** GPT-2
**Baseline:** `master` @ `f1e3af0c9c864ef41317ff71277abb24946f4b65`
**Audit date:** 2026-09-15
**Status:** INITIAL AUDIT IN PROGRESS

## 1. Scope

Trace the current decision runtime from the API entry point through Case ownership, RecommendationFacade, RecommendationService, Need normalization, Product/ProductKnowledge/Evidence/Inventory inputs, ReasoningEngine, scoring, persistence, and API DTO output.

This is a code/document reality audit only. No implementation change is authorized by this artifact.

## 2. Confirmed runtime path

Current API entry point is `POST /generate` in `app/api/routers/recommendations.py`. It first verifies that the Case exists and belongs to the authenticated customer, then invokes `RecommendationFacade.generate(case_id, customer_profile)`. The facade delegates to `RecommendationService.generate_recommendations(...)`, then maps persisted Recommendation rows into `RecommendationDTO` objects.

Within `RecommendationService.generate_recommendations`:

1. A Decision State dictionary is constructed from `customer_profile`.
2. Concerns become Decision State factors with `source=customer_input` and `validity=DECLARED`.
3. Needs are derived through `normalize_needs_from_factors`.
4. Candidate products are selected by `identity_status == VERIFIED`, non-DRAFT status, and positive inventory quantity.
5. For each candidate, ProductKnowledge, all product Evidence, and Inventory are loaded.
6. Need match and an evidence score are computed.
7. `ReasoningEngine.run(...)` receives ProductKnowledge, Evidence, need match, evidence score, and inventory score.
8. The engine computes conflicts/unknowns/claim-boundary violations and invokes `MatchScoringEngine` when all three numeric signals are present.
9. RecommendationService maps engine eligibility, upserts one current Recommendation per Case/Product, and finally sorts all persisted recommendations by `ranking_score` descending.
10. The API serializes the resulting DTOs.

## 3. Confirmed findings

### F01 — Decision State is computed but not persisted

The Decision Contract explicitly permits an in-memory Decision State for the MVP. The current service creates a dictionary containing case/customer/factors/needs/unknowns/conflicts/inferences/status/timestamp, but no Decision State model/entity appears in the current model inventory. Recommendation rows persist only a subset of the final decision surface.

**Classification:** OBSERVED FACT / contract-consistent MVP behavior.

### F02 — Product candidate filtering does enforce identity and positive stock before the per-product reasoning loop

`ProductRepository.find_by_identity_status_and_active("VERIFIED")` joins Inventory and filters `Product.identity_status == "VERIFIED"`, `Product.status != "DRAFT"`, and `Inventory.quantity_available > 0`. RecommendationService also checks inventory again before scoring.

**Classification:** OBSERVED FACT.

### F03 — Runtime Evidence input is not restricted to verified QA evidence

`RecommendationService` calls `EvidenceRepository.find_by_product(product_id)`. That method returns all Evidence rows for the product. A separate `find_unverified()` method exists and filters QA status `PENDING` / `NEEDS_REVIEW`, but the recommendation generation path does not call it. The Evidence objects, including `qa_status`, are then passed to the ReasoningEngine and their source types contribute to `_compute_evidence_score`.

**Classification:** OBSERVED FACT.
**Potential impact:** evidence that is pending/needs review can participate in the evidence score and reasoning input unless another downstream rule excludes it. This requires independent verification against the full Evidence/QA contract before labeling it a confirmed policy violation.

### F04 — Evidence score is source-type weighted, not QA-status gated

`_compute_evidence_score` assigns weights based on `source_type` (`PEER_REVIEWED`, `CLINICAL_TRIAL`, `REGULATORY`, manufacturer, retailer, secondary) and averages them. It does not inspect `qa_status` or `evidence_status`.

**Classification:** OBSERVED FACT.
**Potential impact:** QA state is present in the evidence payload but is not used by this scoring function.

### F05 — Gate/Ranking separation is only partial in the current orchestration

The scoring engine can produce an eligibility result and a final score. RecommendationService converts engine eligibility to `ELIGIBLE` or `INELIGIBLE_PENDING_REVIEW`, but it still persists the Recommendation for the candidate and includes it in the final list, then sorts the entire list by `ranking_score`.

This does not by itself prove that an ineligible product is surfaced as a recommendation to the end user, because the DTO still exposes `eligibility_status`; however, it does show that the current runtime does not physically remove failed candidates from the ranking collection before sorting.

**Classification:** OBSERVED FACT / contract-conformance GAP candidate.

### F06 — Need normalization correctly preserves unresolved input rather than guessing

The GAP-05 L1 normalizer uses an explicit approved synonym/phrase map. Exact approved mappings produce canonical Needs. Partial token hits become `ambiguous`; unmapped input remains `no_approved_mapping`. RecommendationService marks the decision `INSUFFICIENT` when no usable Need exists and unresolved input remains.

**Classification:** OBSERVED FACT / aligned with Decision Contract minimum-meaning rule.

### F07 — Decision State unknown/conflict collections are initialized but are not populated from per-product engine results

`_build_decision_state` initializes `unknowns=[]` and `conflicts=[]`. Inside the product loop, the service creates separate `product_unknowns` and `product_conflicts` from the engine result. The code does not append these values back into `decision_state["unknowns"]` or `decision_state["conflicts"]`.

The existing end-of-loop log checks whether the case-level unknown count changed, which therefore does not capture product-level unknowns.

**Classification:** OBSERVED FACT.
**Potential impact:** the in-memory Case Decision State does not appear to accumulate product-level unknowns/conflicts despite the contract describing uncertainty/conflict as part of the decision object. This is a strong integration-gap candidate and needs independent review.

### F08 — Recommendation DTO derives confidence separately from the engine's confidence

`ReasoningEngine` computes confidence through `MatchScoringEngine`. The RecommendationFacade's `_to_recommendation_dto` instead computes `confidence = round(min(1.0, 0.4 * need + 0.6 * evidence), 2)` from Recommendation row fields.

The formulas appear numerically aligned with the current constants, but the DTO mapping is a second confidence calculation rather than consuming an explicitly persisted engine confidence value.

**Classification:** OBSERVED FACT / traceability observation.

### F09 — Recommendation persistence stores a reduced decision trace

The Recommendation model stores case/product IDs, need match, evidence score, eligibility status, ranking score/reasons, exclusion reasons, and timestamp. It does not store the engine's evidence references, warnings, hard-gate reasons, decision-state factors, normalized-Need mapping, unknowns, or conflicts.

The DTO additionally exposes `evidence_refs=[]` and `warnings=[]` in the current facade mapping, despite the engine producing evidence references and warnings.

**Classification:** OBSERVED FACT.
**Potential impact:** decision-time traceability is materially narrower at the persisted/API boundary than the computed ReasoningResult.

## 4. Contract alignment observations

The accepted Decision Contract requires the target trace:

`Customer → Case → Factor/Decision State → Need → Product Knowledge/Evidence → Gate → Ranking → Recommendation`

The repository contains recognizable components for each stage, but the current implementation combines gate and scoring/ranking in a way that merits explicit conformance review, and it does not persist the full Decision State by design.

The contract also requires Evidence/Unknown/Conflict boundaries to remain explicit. The current runtime does carry QA status into the ReasoningEngine input, but the evidence score itself ignores QA status, and product-level unknown/conflict results are not folded into the case-level Decision State dictionary.

## 5. Evidence inspected

- `app/api/routers/recommendations.py`
- `app/interface/facades.py`
- `app/services/recommendation_service.py`
- `app/services/need_normalization.py`
- `app/repositories/product_repository.py`
- `app/repositories/evidence_repository.py`
- `app/reasoning/reasoning_engine.py`
- `app/reasoning/scoring.py`
- `app/reasoning/scoring_constants.py`
- `app/models/recommendation.py`
- `app/models/product_knowledge.py`
- `docs/02_architecture/HBI_DECISION_CONTRACT_v1.0.md`

## 6. Initial conclusion

The runtime is not a missing chain. The major finding is that the chain exists but several semantic boundaries are weaker at integration points than the Decision Contract describes. The highest-priority WP-01 candidates for deeper verification are:

1. Evidence QA/readiness participation in decision scoring.
2. Gate-before-ranking behavior and whether ineligible candidates can appear in the returned recommendation set.
3. Loss of Decision State / engine provenance at Recommendation persistence and DTO boundaries.
4. Product-level unknown/conflict propagation into the decision state.

No implementation change is proposed by this initial audit.

## 7. Agent provenance

- Agent identifier: GPT-2
- Runtime: ChatGPT GPT-5.6 Luna
- Repository: `vahidmaghsoudi2/hbi`
- Input snapshot: `f1e3af0c9c864ef41317ff71277abb24946f4b65`
- Working branch: `agent/gpt-2/hbi-runtime-001-wp01/202609152215`
- Evidence retrieval method: GitHub repository file/tree/API reads at the declared baseline
- CI/test execution: NOT RUN in this audit step
- Confidence: HIGH for the listed code facts; MEDIUM for policy-conformance impact until independent verification and broader test/runtime evidence are available

## 8. Execution / Integration Addendum

**Status:** WP-01 INTEGRATION COMPLETE / READY FOR INDEPENDENT FINAL VERIFICATION

This addendum records the integration findings already established during WP-01 execution. It does not authorize or perform implementation changes.

### 8.1 Confirmed integration trace

- Customer → Case ownership is enforced at the `/generate` entry point.
- `generate` does not automatically load the stored Customer profile; it consumes the `customer_profile` supplied by the caller.
- Decision State is constructed from the caller-supplied profile.
- Need normalization is controlled through the approved GAP-05 mapping and does not silently guess unresolved input.
- Recommendation reasoning and Recommendation upsert are connected through the current runtime path.
- CP-01 helper path `build_recommendation_profile` → `generate_hint` was confirmed as the existing profile/hint path relevant to the integration audit.

### 8.2 Candidate API authority gap

The `/generate` contract currently permits a caller-supplied `customer_profile` rather than deriving the authoritative profile from the authenticated Customer record. This remains a **CANDIDATE GAP**, not an approved implementation change or confirmed policy violation.

### 8.3 Verification handoff

WP-01 is now packaged for independent final verification against the repository state. The final verifier must treat the GitHub branch/file state as the source of truth and independently verify the integration claims and candidate gaps.

**Implementation:** NOT PERFORMED.
**Master:** UNCHANGED.
**Final acceptance:** NOT YET GRANTED.
