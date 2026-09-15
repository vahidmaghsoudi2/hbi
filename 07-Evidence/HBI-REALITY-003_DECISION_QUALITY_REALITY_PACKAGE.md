# HBI-REALITY-003 — Decision-Quality Reality Package

**Mission:** HBI-REALITY-003 / Issue #78  
**Audit baseline:** `master @ 7df2ba592e89b23d4f62e85a1520cb0997186360`  
**Audit mode:** repository reality only; no implementation; no scoring/weight changes  
**Team-2 boundary:** Issue #76 was not modified or implemented by this mission.

## Overall verdict

**CURRENT STATE: TECHNICALLY CONNECTED, BUT NOT YET A FULLY DEFENSIBLE CUSTOMER DECISION SYSTEM.**

The current master can execute the end-to-end recommendation path from authenticated Customer/Case ownership through controlled Need normalization, ProductKnowledge/Evidence/Inventory evaluation, ReasoningEngine scoring, eligibility pressure, persistence, ranking and API DTO presentation. However, two independently observable decision-quality gaps remain:

1. **REAL GAP — Decision traceability is lost at the Recommendation API boundary.** `RecommendationDTO` exposes `evidence_refs` and `warnings`, but `_to_recommendation_dto()` emits both as empty lists. The ReasoningEngine computes evidence references, conflicts, unknowns and warnings, and RecommendationService embeds some decision context into `ranking_reasons`, but the API contract does not expose the actual evidence/provenance and warning structures.
2. **REAL GAP — Gating is not cleanly separated from ranking/persistence.** Products with hard-gate conditions or insufficient information can still be persisted as Recommendation records and included in the ranking collection. Their `eligibility_status` is marked as `INELIGIBLE_PENDING_REVIEW`, but the pipeline still computes/stores a ranking score and returns the record through the recommendation API. This is weaker than the Decision Contract requirement that elimination/gating precede ranking and that ranking must not rescue a hard-gate failure.

These are decision-quality/runtime integration findings, not scoring-weight findings. No scoring weights were changed or proposed here.

## End-to-end reality classification

| Stage | Classification | Evidence-based finding |
|---|---|---|
| Customer / Case | 🟢 WORKS | Recommendation generation requires authenticated customer identity and verifies that the requested Case belongs to that customer. |
| Decision State | 🟡 QUALITY LIMIT | Decision State is computed in-memory from the request-supplied `customer_profile`; it is not persisted. In-memory MVP behavior is compatible with the current architecture, but the API caller remains the source of the profile payload used for decision construction. |
| L1 Need normalization | 🟢 WORKS | GAP-05 L1 is deterministic, curated and auditable; unmapped/ambiguous phrases are not silently guessed into Needs. |
| Evidence | 🟢 WORKS | Evidence score now uses only `qa_status == APPROVED`; zero approved evidence yields score 0. Existing source-type weights remain unchanged. |
| Unknown / Conflict | 🟢 WORKS | ReasoningEngine surfaces UNKNOWN evidence; current conflict propagation reaches `existing_conflicts` and applies eligibility pressure without changing frozen scoring weights. |
| ProductKnowledge | 🟢 WORKS | Recommendation runtime reads ProductKnowledge and passes a snapshot into ReasoningEngine; known use cases participate in Need matching. |
| Inventory / availability | 🟢 WORKS | Candidate selection requires positive available inventory; API also presents availability and price. |
| Eligibility / gating | 🔴 REAL GAP | Hard-gated/insufficient candidates can still be persisted and carried into ranking/API as Recommendation records with an ineligible/pending-review status. |
| Ranking | 🔴 REAL GAP | Ranking score is computed for candidates even when eligibility is already blocked by insufficient evidence, insufficient Need meaning, critical unknowns or other gating conditions. |
| Recommendation | 🔴 REAL GAP | The persisted/API-visible Recommendation object can represent a non-defensible candidate rather than a cleanly gated-out recommendation. The status communicates the block, but the object remains in the recommendation result set. |
| Traceability / explanation | 🔴 REAL GAP | API `evidence_refs=[]` and `warnings=[]` discard the computed provenance/warning data. A consumer therefore cannot reliably trace the returned recommendation back to Evidence, Unknown/Conflict and explicit hard-gate reasons. |
| Insufficient-information behavior | 🔴 REAL GAP | The service correctly detects unmapped/ambiguous Need input and marks the Decision State `INSUFFICIENT`, and missing approved Evidence produces an evidence hard gate. But the pipeline still creates/persists recommendation records and exposes them through the API rather than returning a clean insufficient-information outcome with the relevant reasons/provenance. |

## Cross-check evidence

### Customer → Case → API

`POST /recommendations/generate` authenticates the current customer and calls `_assert_case_owned()`, which rejects missing cases and cross-customer access. The request then passes `request.customer_profile` into `RecommendationFacade.generate()`. This confirms Case ownership enforcement but also confirms that the profile used to build Decision State is request-supplied rather than loaded from the stored Customer record.

### Decision State → Need

`RecommendationService._build_decision_state()` constructs factors from customer-declared concerns. `normalize_needs_from_factors()` uses only the approved deterministic mapping. Exact approved mappings become canonical Needs; ambiguous and unmapped phrases remain explicitly unresolved. When no Need is generated, RecommendationService marks the Decision State `INSUFFICIENT`.

### Evidence → score

`_compute_evidence_score()` filters to `qa_status == APPROVED` before scoring. If there are no approved Evidence rows, the score is `0.0`. Existing source-type weights are unchanged. This confirms the PO-approved RUNTIME-003 behavior is present on current master.

### Unknown / Conflict → Reasoning

ReasoningEngine receives evidence references, existing conflicts, and scoring inputs. Existing conflicts are analyzed and can force an otherwise eligible scoring result to `NEEDS_REVIEW`. UNKNOWN evidence is surfaced with severity/action metadata. This path is observed only; Team 1 did not alter it.

### Product / Inventory → candidate set

ProductRepository selects products with `identity_status == VERIFIED`, `status != DRAFT`, and positive available inventory. RecommendationService then reads ProductKnowledge and Evidence and computes the runtime decision signals.

### Gating → ranking → persistence

RecommendationService computes engine eligibility, maps additional Decision-State/Product-unknown conditions to `INELIGIBLE_PENDING_REVIEW`, then still calculates `final_score`, calls `_upsert_current_recommendation()`, appends the Recommendation, and finally sorts the recommendation collection by ranking score. This is the concrete basis for the gating/ranking GAP.

### Recommendation model → Facade → DTO → API

The API route calls `RecommendationFacade.generate()` and serializes each `RecommendationDTO`. `_to_recommendation_dto()` maps score, eligibility, rationale, availability and price, but explicitly sets `evidence_refs=[]` and `warnings=[]`. Therefore computed provenance and warning information are not available to the API consumer.

## Real GAPs only

### GAP-DQ-01 — Recommendation traceability loss

**Severity:** High for decision defensibility.  
**Observed behavior:** computed evidence references / warnings do not survive the DTO mapping.  
**Impact:** a returned recommendation cannot be independently traced to its Evidence, Unknown/Conflict findings or hard-gate reasons through the public recommendation payload.  
**Classification:** 🔴 REAL GAP.  
**No implementation performed in this audit.**

### GAP-DQ-02 — Gate-before-rank separation is incomplete

**Severity:** High for decision semantics.  
**Observed behavior:** hard-gated or insufficient candidates can be persisted as Recommendation records, assigned ranking scores, sorted, and returned with an ineligible/pending-review status.  
**Impact:** the API result set mixes decision candidates with candidates that have already failed a required gate. Ranking therefore exists for objects that should not be eligible for recommendation.  
**Classification:** 🔴 REAL GAP.  
**No scoring formula or weight change proposed. No implementation performed in this audit.

## Non-GAP / intentional MVP deferrals

- **Decision State persistence:** currently in-memory. This is consistent with the documented MVP architecture and is treated as 🔵 INTENTIONALLY DEFERRED, not a new GAP.
- **Scoring weights/formula:** unchanged and frozen. Issue #37 remains untouched.
- **Evidence QA policy:** approved-only Evidence scoring is implemented on current master and is not reopened.
- **Evidence conflict propagation:** observed as an existing Team-2 runtime behavior; not modified by Team 1.
- **New Problem/Assessment/FactorDefinition/CaseFactor entities:** not required by this audit and were not introduced.
- **Product identity/inventory candidate filtering:** current verified-identity and positive-stock selection is operationally present.

## PO decision required

**No PO decision is required to classify the two findings above.** The repository evidence is sufficient to classify both as real runtime decision-quality gaps. Any implementation authorization should be a separate, explicit PO action after independent verification, with the scope limited to the confirmed gaps and without changing scoring weights.

## Independent-verification status

This package is the Team-1 primary audit result and includes a second-pass repository cross-check across the API route, Facade/DTO, RecommendationService, ReasoningEngine, scoring engine, Need normalization, Case service and ProductRepository. It is **not** represented as Grok-1 independent verification. Independent verification remains a required governance gate before the package can be marked VERIFIED/ACCEPTED.

## Team-2 non-interference statement

Team 1 did **not** modify Team 2 code, did not create or alter a PR for Issue #76, did not change `Evidence.conflict_status` propagation, did not change ReasoningEngine conflict handling, did not change tests belonging to #76, did not alter scoring/weights, and did not reopen resolved GAP-01/03/04 or Issue #37.

## Recommended next action

1. Independent verifier reviews this package against current master.
2. If verified, PO decides whether to authorize implementation of **GAP-DQ-01** and **GAP-DQ-02** as a bounded follow-up mission.
3. No implementation should begin from this audit artifact alone.
