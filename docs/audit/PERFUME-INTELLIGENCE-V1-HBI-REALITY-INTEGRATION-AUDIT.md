# PERFUME INTELLIGENCE V1 — HBI REALITY INTEGRATION AUDIT

**Document type:** Repository Reality Audit (evidence registration only)  
**Mission type:** AUTHORIZED FOR AUDIT ONLY  
**Domain owner (mission):** Perplexity — Perfume Intelligence V1  
**Auditor:** Grok — Repository Access / GitHub Execution  

**Independent Verification = NOT COMPLETED**  
**Reason:** No independent verifier evidence submitted.

**Status ladder (this document):**

```text
Audit Evidence Collection: COMPLETED / PARTIAL (static repo + tests; runtime/CI-run incomplete)
Independent Verification: NOT COMPLETED
Architecture: NOT DECIDED
Contract: NOT AUTHORIZED
Implementation: NOT AUTHORIZED
```

---

## 1. Audit Metadata

| Field | Value |
|-------|--------|
| Repository URL | https://github.com/vahidmaghsoudi2/hbi |
| Inspected Branch | `master` (code analysis baseline) |
| Inspected Commit SHA | `bbe1a4eed81937fae1c7ecb7be5bb28af551458b` |
| Report Branch | `docs/perfume-v1-reality-integration-audit` |
| Audit Start Date | 2026-09-27 |
| Evidence Package update | 2026-09-27 |
| Auditor | Grok |
| Independent Verification | NOT COMPLETED — No independent verifier evidence submitted |
| Runtime Access Status | **NOT AVAILABLE** — no authorized production/pilot DB session for this mission |
| Report path | `docs/audit/PERFUME-INTELLIGENCE-V1-HBI-REALITY-INTEGRATION-AUDIT.md` |
| Path note | Requested `docs/11-meeting-room/fragrance/` does not exist. File under existing `docs/audit/`. |

**Core rules**

```text
Artifact Exists ≠ Capability Exists
Capability Exists ≠ Verified Behavior
Verified Behavior ≠ Accepted Architecture
```

No architecture design, contract, Reuse/Extend/New decision, or implementation recommendation is made in this document.

---

## 2. Scope and Non-Scope

### In scope

PI-V1-01 … PI-V1-10 only (see Evidence Package).

### Out of scope

Similarity; numeric scoring; automatic ranking/recommendation/learning; advanced customer event history; advanced fragrance performance model; derived olfactory profile engine; new product master / evidence / knowledge / lifecycle designs; cross-market equivalence; formula/reformulation intelligence.

---

## 3. Source-of-Truth Statement

Proof sources: repository files/symbols/tests/workflow paths at inspected SHA.  
Not proof: memory alone, chat summaries alone, filename-only inference, unproven runtime.

**Fragrance note:** No dedicated olfactory/sillage/longevity intelligence module found under `app/`. Category id `PERFUME` is catalog taxonomy only (`app/models/category.py`), not perfume intelligence.

---

## 4. Access and Runtime Limitations

| Resource | Status |
|----------|--------|
| Git file read | AVAILABLE |
| Test sources | AVAILABLE (static) |
| CI workflow YAML | AVAILABLE `.github/workflows/` |
| CI run bound to `bbe1a4ee…` | NOT VERIFIED in this audit |
| Authorized runtime DB | NOT AVAILABLE |

---

## 5. Audit Method

Static inspection of models/services/repos/tests at SHA above; separate presence from tested behavior; mark unknowns; no architecture decisions; independent verification not completed.

---

## 6. Audit Matrix (summary)

Full per-ID detail is in **Evidence Package** below. Summary: all ten areas **PARTIALLY_VERIFIED** at static/test level; none fully VERIFIED with runtime + CI-run + independent verification.

---

## 7. Verified Current HBI Capabilities (generic platform only)

1. `Product.product_id` PK with cross-module FKs  
2. Product lifecycle statuses + `ProductTransitionService`  
3. Inventory `quantity_available` + catalog stock filter  
4. Evidence model + Research Draft → PENDING  
5. ProductKnowledge flat projection from approved evidence  
6. DuplicateCheck (identity/barcode/size/variant)  
7. ProfileFact with value_state including UNKNOWN (constrained keys)  
8. Recommendation catalog load + `_map_eligibility`  
9. Category `PERFUME` in category constraint  

---

## 8. Partially Verified Capabilities

Runtime operator flows; CI green on exact SHA; full recommendation explanation payload; product-field EMPTY vs UNKNOWN enforcement everywhere.

---

## 9. Unknown / Not Verified Areas

Production PERFUME catalog contents; modules outside searched paths; live CI for exact SHA; independent verification of all rows.

---

## 10. Verified Gaps (observed absence)

| Gap | Evidence |
|-----|----------|
| No concentration column | `app/models/product.py` fields listed; no `concentration` |
| No olfactory PK fields | `app/models/product_knowledge.py` column list |
| No fragrance preference keys | `ProfileFact` attribute_key CheckConstraint |
| No perfume intelligence services | app search: no olfactory/sillage/longevity engine modules |

---

## 11. Contradictions

Category `PERFUME` ≠ Perfume Intelligence engine — not a logical contradiction; different concepts.

---

## 12. Independent Verification Result

```text
Independent Verification = NOT COMPLETED
Reason: No independent verifier evidence submitted.
```

Do not treat this audit as fully verified.

---

## 13. Deferred Items

Similarity; numeric scoring; automatic ranking/learning; advanced customer events; advanced performance model; derived olfactory profile; new masters/engines; cross-market equivalence; formula intelligence.

---

## 14. Explicit Non-Decisions

No Reuse/Extend/New; no Contract; no implementation recommendation; no Product Master / Evidence / Knowledge redesign; no scoring/similarity; no code/schema/API/Issue/PR beyond this documentation file on the docs branch.

---

## 15. Final Audit Verdict

**B. AUDIT PARTIAL — ADDITIONAL EVIDENCE REQUIRED**

Reasons: static evidence collected; runtime NOT AVAILABLE; CI outcome for exact SHA NOT VERIFIED; Independent Verification NOT COMPLETED.

---

## Evidence Package — PI-V1-01 to PI-V1-10

Shared header for all IDs unless overridden:

| Field | Value |
|-------|--------|
| Repository URL | https://github.com/vahidmaghsoudi2/hbi |
| Inspected Branch | master |
| Inspected Commit SHA | `bbe1a4eed81937fae1c7ecb7be5bb28af551458b` |
| Independent Verification | NOT COMPLETED — No independent verifier evidence submitted |

---

### PI-V1-01 — Canonical Product Identity

1. **Audit ID:** PI-V1-01  
2. **Repository URL:** https://github.com/vahidmaghsoudi2/hbi  
3. **Inspected Branch:** master  
4. **Inspected Commit SHA:** `bbe1a4eed81937fae1c7ecb7be5bb28af551458b`  
5. **Repository Path:** `app/models/product.py`  
6. **Artifact Type:** SQLAlchemy model  
7. **Exact Symbol:** `class Product` — `product_id` Column PK; `brand`; `product_name`; `status`; `identity_status`; `qa_verdict`  
8. **Observed Behavior:** String primary key; brand and product_name required (nullable=False); lifecycle and identity constrained by CheckConstraints  
9. **Caller Evidence:** `ProductService.create_product_with_inventory` (`app/services/product_service.py`); FKs from Evidence, ProductKnowledge, Inventory models  
10. **Test Evidence:** `tests/test_product_compliance.py` — `test_product_create_forces_draft`, lifecycle tests; `tests/test_intake_e2e_api_slice_001.py` — `test_intake_api_vertical_slice_reaches_active`  
11. **CI Evidence:** Workflow definitions `.github/workflows/test.yml`, `hbi_auto.yml` present; **run result for inspected SHA NOT VERIFIED**  
12. **Runtime Evidence:** None collected  
13. **Runtime Status:** NOT AVAILABLE  
14. **Verification Status:** PARTIALLY_VERIFIED  
15. **Current Capability:** PARTIALLY_VERIFIED (generic identity)  
16. **Explicit Unknowns:** Whether production data always uses stable external product_id conventions; fragrance-specific identity rules  
17. **Contradictions:** None  
18. **Audit Limitation:** No runtime; no independent verification; fragrance semantics not present in model  

---

### PI-V1-02 — Variant / Concentration / Volume

1. **Audit ID:** PI-V1-02  
2–4. Same repo/branch/SHA  
5. **Repository Path:** `app/models/product.py`; `app/services/duplicate_check_service.py`  
6. **Artifact Type:** Model columns + service  
7. **Exact Symbol:** `Product.variant`, `Product.size_value`, `Product.size_unit`, `Product.packaging_version`; `DuplicateCheckService.check`  
8. **Observed Behavior:** variant/size nullable attributes; size/variant differences treated as distinct in duplicate path; **no `concentration` column**; volume only if encoded in size_value/unit  
9. **Caller Evidence:** Create/duplicate intake paths; `ProductService.create_product_with_inventory`  
10. **Test Evidence:** `tests/test_intake_e2e_api_slice_001.py` — `test_duplicate_different_variant_or_size_is_distinct_not_possible_match`, `test_duplicate_exact_name_same_size_returns_possible_match`  
11. **CI Evidence:** Workflow files present; SHA-specific outcome NOT VERIFIED  
12. **Runtime Evidence:** None  
13. **Runtime Status:** NOT AVAILABLE  
14. **Verification Status:** PARTIALLY_VERIFIED  
15. **Current Capability:** PARTIALLY_VERIFIED  
16. **Explicit Unknowns:** Operator convention for encoding EDP/EDT in variant text  
17. **Contradictions:** None  
18. **Audit Limitation:** Concentration absence is structural; not a perfume engine  

---

### PI-V1-03 — Inventory Availability

1. **Audit ID:** PI-V1-03  
2–4. Same  
5. **Repository Path:** `app/models/inventory.py`; `app/repositories/product_repository.py`  
6. **Artifact Type:** Model + repository query  
7. **Exact Symbol:** `Inventory.quantity_available`; `ProductRepository.find_by_identity_status_and_active`  
8. **Observed Behavior:** Catalog query requires `Product.status == ACTIVE`, `identity_status` match, `qa_verdict == VALID`, `Inventory.quantity_available > 0`  
9. **Caller Evidence:** `RecommendationService.generate_recommendations` uses `find_by_identity_status_and_active("VERIFIED")`  
10. **Test Evidence:** Intake/compliance paths that create inventory; recommendation tests that depend on stock (generic)  
11. **CI Evidence:** Workflow files present; SHA-specific outcome NOT VERIFIED  
12. **Runtime Evidence:** None  
13. **Runtime Status:** NOT AVAILABLE  
14. **Verification Status:** PARTIALLY_VERIFIED  
15. **Current Capability:** PARTIALLY_VERIFIED  
16. **Explicit Unknowns:** Default seed quantity operational policy in production  
17. **Contradictions:** None  
18. **Audit Limitation:** Runtime stock behavior not observed  

---

### PI-V1-04 — ProductKnowledge / Product Information

1. **Audit ID:** PI-V1-04  
2–4. Same  
5. **Repository Path:** `app/models/product_knowledge.py`; `app/services/product_knowledge_service.py`  
6. **Artifact Type:** Model + service  
7. **Exact Symbol:** `class ProductKnowledge`; `ProductKnowledgeService.update_from_evidence`  
8. **Observed Behavior:** One row per product_id; text columns (ingredients, ingredient_roles, claimed_benefits, known_use_cases, contraindications, usage_instructions, manufacturer_claims, evidence_refs); rebuild from APPROVED/VERIFIED non-CONFLICT evidence; PENDING excluded  
9. **Caller Evidence:** Research draft path calls update_from_evidence after create; evidence verify flows  
10. **Test Evidence:** `tests/test_product_knowledge_qa_sync.py` — `test_pending_evidence_not_in_product_knowledge`, `test_verify_then_reject_then_reverify_rebuilds_knowledge`; `tests/test_g2_g4_evidence_truth.py`  
11. **CI Evidence:** Workflow files present; SHA-specific outcome NOT VERIFIED  
12. **Runtime Evidence:** None  
13. **Runtime Status:** NOT AVAILABLE  
14. **Verification Status:** PARTIALLY_VERIFIED  
15. **Current Capability:** PARTIALLY_VERIFIED  
16. **Explicit Unknowns:** Whether free-text is used ad hoc for fragrance notes in production data  
17. **Contradictions:** None  
18. **Audit Limitation:** No olfactory schema columns evidenced  

---

### PI-V1-05 — Evidence / Provenance

1. **Audit ID:** PI-V1-05  
2–4. Same  
5. **Repository Path:** `app/models/evidence.py`; `app/services/evidence_service.py`; `app/services/research_draft_service.py`; `app/api/routers/products.py`  
6. **Artifact Type:** Model + services + API route  
7. **Exact Symbol:** `class Evidence`; `ResearchDraftService.create_draft`; `POST /{product_id}/research-draft`  
8. **Observed Behavior:** Evidence stores source_type, source_reference, claim, field, claim_type, qa_status, conflict_status, dates; research draft requires claim + sources; sets qa_status PENDING  
9. **Caller Evidence:** Products router research-draft; evidence routers  
10. **Test Evidence:** `tests/test_g2_g4_evidence_truth.py`; `tests/test_evidence.py`  
11. **CI Evidence:** Workflow files present; SHA-specific outcome NOT VERIFIED  
12. **Runtime Evidence:** None  
13. **Runtime Status:** NOT AVAILABLE  
14. **Verification Status:** PARTIALLY_VERIFIED  
15. **Current Capability:** PARTIALLY_VERIFIED  
16. **Explicit Unknowns:** Perfume-specific claim vocabularies in live data  
17. **Contradictions:** None  
18. **Audit Limitation:** Provenance capability is generic, not fragrance-typed  

---

### PI-V1-06 — Unknown / Conflict Handling

1. **Audit ID:** PI-V1-06  
2–4. Same  
5. **Repository Path:** `app/services/research_draft_service.py`; `app/services/evidence_service.py`; `app/services/evidence_readiness_service.py`; `app/models/profile_fact.py`  
6. **Artifact Type:** Services + model constraints  
7. **Exact Symbol:** `_ALLOWED_CLAIM_TYPES` includes UNKNOWN, CONFLICT; `EvidenceService.resolve_conflict`; `EvidenceReadinessService.evaluate`; `ProfileFact.value_state`  
8. **Observed Behavior:** Explicit claim_type UNKNOWN/CONFLICT; conflict_status on evidence; readiness fails on CONFLICT / pending QA; ProfileFact distinguishes KNOWN vs UNKNOWN value_state; empty ProductKnowledge string is not the same mechanism as claim_type UNKNOWN  
9. **Caller Evidence:** Transition approve uses readiness; profile fact services  
10. **Test Evidence:** `test_readiness_conflict_blocks_approve` in `test_product_compliance.py`; `test_all_value_states_are_supported` in `test_profile_fact.py`; g2/g4 evidence tests  
11. **CI Evidence:** Workflow files present; SHA-specific outcome NOT VERIFIED  
12. **Runtime Evidence:** None  
13. **Runtime Status:** NOT AVAILABLE  
14. **Verification Status:** PARTIALLY_VERIFIED  
15. **Current Capability:** PARTIALLY_VERIFIED  
16. **Explicit Unknowns:** Uniform EMPTY vs UNKNOWN enforcement for every product text field at all gates  
17. **Contradictions:** None recorded  
18. **Audit Limitation:** Product-field EMPTY≠UNKNOWN policy not fully proven across all gates in this package  

---

### PI-V1-07 — Customer Input (Preference / Avoidance / Context)

1. **Audit ID:** PI-V1-07  
2–4. Same  
5. **Repository Path:** `app/models/profile_fact.py`; related profile services/tests  
6. **Artifact Type:** Model + tests  
7. **Exact Symbol:** `class ProfileFact`; CheckConstraint `attribute_key IN ('skin_profile', 'hair_profile', 'scalp_profile', 'age_range', 'concerns')`  
8. **Observed Behavior:** Customer facts versioned with provenance and value_state; **no fragrance preference/avoidance keys** in constraint; Case/consultation exist elsewhere but fragrance visit-context mapping not evidenced here  
9. **Caller Evidence:** Profile fact API/services (as covered by profile tests)  
10. **Test Evidence:** `tests/test_profile_fact.py` (create, supersession, value_states, consent)  
11. **CI Evidence:** Workflow files present; SHA-specific outcome NOT VERIFIED  
12. **Runtime Evidence:** None  
13. **Runtime Status:** NOT AVAILABLE  
14. **Verification Status:** PARTIALLY_VERIFIED  
15. **Current Capability:** PARTIALLY_VERIFIED for generic profile facts; **NOT PRESENT** for fragrance preference/avoidance model  
16. **Explicit Unknowns:** Whether concerns free-text is ever used for scent in production  
17. **Contradictions:** None  
18. **Audit Limitation:** Avoidance-as-first-class not evidenced  

---

### PI-V1-08 — Eligibility / Decision Boundary

1. **Audit ID:** PI-V1-08  
2–4. Same  
5. **Repository Path:** `app/repositories/product_repository.py`; `app/services/recommendation_service.py`  
6. **Artifact Type:** Repository + service  
7. **Exact Symbol:** `find_by_identity_status_and_active`; `RecommendationService._map_eligibility`; `generate_recommendations`  
8. **Observed Behavior:** Catalog excludes non-ACTIVE / non-VALID / non-VERIFIED / zero stock; eligibility mapping uses engine_result, decision_state, need_match, unknowns  
9. **Caller Evidence:** `generate_recommendations`  
10. **Test Evidence:** Recommendation-related tests under `tests/` (e.g. pipeline/medical gate suites present in repo); exact perfume eligibility tests **not** identified  
11. **CI Evidence:** Workflow files present; SHA-specific outcome NOT VERIFIED  
12. **Runtime Evidence:** None  
13. **Runtime Status:** NOT AVAILABLE  
14. **Verification Status:** PARTIALLY_VERIFIED  
15. **Current Capability:** PARTIALLY_VERIFIED (generic)  
16. **Explicit Unknowns:** Full set of eligibility string outcomes in production  
17. **Contradictions:** None  
18. **Audit Limitation:** Fragrance-specific eligibility rules NOT PRESENT  

---

### PI-V1-09 — Decision Trace / Auditability

1. **Audit ID:** PI-V1-09  
2–4. Same  
5. **Repository Path:** `app/models/recommendation.py`; `app/models/product_mutation_log.py`; `app/models/evidence_mutation_log.py`; `app/models/specialist_override.py`; outcome assessment modules  
6. **Artifact Type:** Models + related services  
7. **Exact Symbol:** `class Recommendation`; mutation log models; specialist override model  
8. **Observed Behavior:** Recommendation rows persisted on generate path; product/evidence mutation logs exist; override model exists; **complete human-readable decision explanation package not fully line-traced in this audit**  
9. **Caller Evidence:** `generate_recommendations`; mutation-log routes on products  
10. **Test Evidence:** `test_product_compliance.py` — `test_mutation_log_persists`; outcome assessment tests present in repo  
11. **CI Evidence:** Workflow files present; SHA-specific outcome NOT VERIFIED  
12. **Runtime Evidence:** None  
13. **Runtime Status:** NOT AVAILABLE  
14. **Verification Status:** PARTIALLY_VERIFIED  
15. **Current Capability:** PARTIALLY_VERIFIED  
16. **Explicit Unknowns:** Whether every recommendation stores full constraint/evidence snapshot  
17. **Contradictions:** None  
18. **Audit Limitation:** Trace completeness not exhaustively verified  

---

### PI-V1-10 — Documentation / QA / CI Governance

1. **Audit ID:** PI-V1-10  
2–4. Same  
5. **Repository Path:** `docs/`; `docs/audit/`; `docs/P4_PRODUCT_INTAKE_GOVERNANCE_CONTRACT_V1.md`; `.github/workflows/test.yml`; `.github/workflows/hbi_auto.yml`; `app/models/category.py`  
6. **Artifact Type:** Docs + workflows + category model  
7. **Exact Symbol:** workflow file names; `Category` CheckConstraint includes `'PERFUME'`  
8. **Observed Behavior:** Governance/docs tree and CI workflow YAML exist; category taxonomy includes PERFUME for catalog/reporting; **no perfume intelligence contract/audit doc prior to this file**  
9. **Caller Evidence:** N/A (governance artifacts)  
10. **Test Evidence:** governance-tests referenced in project history; not bound to run-id here  
11. **CI Evidence:** YAML present; **outcome for `bbe1a4ee…` NOT VERIFIED**  
12. **Runtime Evidence:** NOT REQUIRED for static presence of docs/workflows  
13. **Runtime Status:** NOT REQUIRED (for static governance inventory)  
14. **Verification Status:** PARTIALLY_VERIFIED  
15. **Current Capability:** PARTIALLY_VERIFIED  
16. **Explicit Unknowns:** CI conclusion on exact inspected SHA  
17. **Contradictions:** None  
18. **Audit Limitation:** Without run-id, CI cannot be claimed green for baseline SHA  

---

*End of Evidence Package and Audit document*
