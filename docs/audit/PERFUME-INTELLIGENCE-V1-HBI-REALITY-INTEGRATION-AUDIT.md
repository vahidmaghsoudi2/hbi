# PERFUME INTELLIGENCE V1 — HBI REALITY INTEGRATION AUDIT

**Document type:** Repository Reality Audit (evidence registration only)  
**Mission type:** AUTHORIZED FOR AUDIT ONLY  
**Domain owner (mission):** Perplexity — Perfume Intelligence V1  
**Auditor:** Grok — Repository Access / GitHub Execution  
**Independent Verifier:** NOT ASSIGNED / NOT COMPLETED  

---

## 1. Audit Metadata

| Field | Value |
|-------|--------|
| Repository URL | https://github.com/vahidmaghsoudi2/hbi |
| Inspected Branch | `master` (analysis); report registered on `docs/perfume-v1-reality-integration-audit` |
| Inspected Commit SHA | `bbe1a4eed81937fae1c7ecb7be5bb28af551458b` |
| Audit Start Date | 2026-09-27 |
| Auditor | Grok |
| Independent Verifier | INDEPENDENT VERIFICATION NOT COMPLETED |
| Runtime Access Status | **NOT AVAILABLE** — no authorized production/pilot DB session for this mission |
| Report path chosen | `docs/audit/PERFUME-INTELLIGENCE-V1-HBI-REALITY-INTEGRATION-AUDIT.md` |
| Path note | Requested `docs/11-meeting-room/fragrance/` **does not exist** on inspected tree. Closest existing governance/audit location: `docs/audit/` (already used for gate/recon evidence). No new documentation architecture invented beyond placing this single file under `docs/audit/`. |

**Core rules applied**

```text
Artifact Exists ≠ Capability Exists
Capability Exists ≠ Verified Behavior
Verified Behavior ≠ Accepted Architecture
```

No architecture design, contract, Reuse/Extend/New decision, or implementation recommendation is made in this document.

---

## 2. Scope and Non-Scope

### In scope (ten V1 audit areas only)

- PI-V1-01 Canonical Product Identity  
- PI-V1-02 Product Variant / Concentration / Volume  
- PI-V1-03 Inventory Availability  
- PI-V1-04 ProductKnowledge / product information  
- PI-V1-05 Evidence / Provenance  
- PI-V1-06 Unknown / Conflict handling  
- PI-V1-07 Customer input (preference / avoidance / context)  
- PI-V1-08 Eligibility / decision boundary  
- PI-V1-09 Decision trace / auditability  
- PI-V1-10 Documentation / QA / CI governance  

### Explicitly out of scope (deferred; not audited as V1 capabilities)

Similarity; numeric scoring; automatic ranking/recommendation/learning; advanced customer event history; advanced fragrance performance model; derived olfactory profile engine; new product master / evidence / knowledge / lifecycle designs; cross-market equivalence; formula/reformulation intelligence.

---

## 3. Source-of-Truth Statement

Only the following were used as proof:

- GitHub repository `vahidmaghsoudi2/hbi`
- Branch `master` at SHA `bbe1a4eed81937fae1c7ecb7be5bb28af551458b`
- Files, symbols, schemas, tests, workflow file names under that tree

Not used as proof: memory, prior chat summaries alone, file-name inference without reading symbols, or unproven runtime.

**Fragrance-specific note:** Repository search for perfume/fragrance/olfactory/sillage/longevity product-intelligence modules did **not** show a dedicated perfume intelligence engine. Category id `PERFUME` appears as a **catalog category** constraint (see PI-V1-01/10), which is **not** the same as fragrance intelligence capability.

---

## 4. Access and Runtime Limitations

| Resource | Status |
|----------|--------|
| Git clone / file read | AVAILABLE |
| Test source files | AVAILABLE (static) |
| CI workflow definitions | AVAILABLE under `.github/workflows/` |
| CI outcome **for inspected SHA** `bbe1a4ee…` | **NOT VERIFIED in this audit** (no run-id bound to this SHA recorded here) |
| Authorized runtime / production DB | **NOT AVAILABLE** |

Where runtime would be material, **Runtime Status = NOT AVAILABLE**.

---

## 5. Audit Method

1. Record SHA and branch.  
2. Inspect models, services, repositories, routers, tests for each PI-V1-0x area.  
3. Separate static presence from tested behavior.  
4. Mark UNKNOWN / NOT VERIFIED when evidence is incomplete.  
5. No architecture or Reuse/Extend/New conclusions.  
6. Independent verification step: **not completed** (no second auditor assigned).

---

## 6. Audit Matrix

Statuses used only as allowed by the mission brief.

| ID | Foundation Requirement | Domain Meaning | Repository Artifact | Artifact SHA | Observed Behavior | Caller Evidence | Test Evidence | CI Evidence | Runtime Evidence | Runtime Status | Verification Status | Current Capability | Verified Gap | Architecture Impact | ADR Required | PO Decision Required | Auditor | Independent Verifier | Verification Date |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PI-V1-01 | Canonical product identity | Stable product id shared across modules | `app/models/product.py` `Product.product_id` PK; FKs from Evidence, ProductKnowledge, Inventory, etc. | `bbe1a4eed81937fae1c7ecb7be5bb28af551458b` | String PK; brand/name required; lifecycle `status`; `identity_status`; `qa_verdict` | Services/repos use `product_id` | `tests/test_product_compliance.py`, `tests/test_product_intake_auth.py`, intake e2e | Workflow files exist; **outcome for this SHA NOT VERIFIED here** | NOT AVAILABLE | NOT AVAILABLE | PARTIALLY_VERIFIED | PARTIALLY_VERIFIED | NO GAP VERIFIED for generic identity; fragrance-specific identity semantics NOT PRESENT | NOT ASSESSED — GAP NOT YET VERIFIED | NOT ASSESSED | NOT ASSESSED | Grok | NOT_CONFIRMED | 2026-09-27 |
| PI-V1-02 | Variant / concentration / volume | Represent sellable form differences | `Product.variant`, `size_value`, `size_unit`, `packaging_version`; `DuplicateCheckService` size/variant rules | same | Variant/size are nullable attributes; concentration **not** a dedicated field; volume only via size_value/unit if used that way | `duplicate_check_service.py`; product create paths | Duplicate/intake tests on master lineage | NOT VERIFIED for this SHA | NOT AVAILABLE | NOT AVAILABLE | PARTIALLY_VERIFIED | PARTIALLY_VERIFIED | GAP VERIFIED: no first-class concentration; fragrance volume/concentration semantics not evidenced | DEFERRED TO ARCHITECTURE REVIEW | POSSIBLY REQUIRED AFTER ARCHITECTURE REVIEW | POSSIBLY REQUIRED AFTER ARCHITECTURE REVIEW | Grok | NOT_CONFIRMED | 2026-09-27 |
| PI-V1-03 | Inventory availability | Stock affects availability | `app/models/inventory.py`; `quantity_available`; create seeds inventory | same | Catalog join requires `quantity_available > 0` | `ProductRepository.find_by_identity_status_and_active`; `RecommendationService.generate_recommendations` | Intake/catalog-related tests; recommendation path uses inventory_score | NOT VERIFIED for this SHA | NOT AVAILABLE | NOT AVAILABLE | PARTIALLY_VERIFIED | PARTIALLY_VERIFIED | NO GAP VERIFIED for generic stock gate | NOT ASSESSED | NOT ASSESSED | NOT ASSESSED | Grok | NOT_CONFIRMED | 2026-09-27 |
| PI-V1-04 | Product information / knowledge | Store product-facing knowledge | `app/models/product_knowledge.py` one row per `product_id`; text fields ingredients, roles, benefits, use_cases, contraindications, usage, manufacturer_claims, evidence_refs | same | Flat single-row projection; rebuild from approved evidence | `ProductKnowledgeService.update_from_evidence` | `test_product_knowledge_qa_sync.py`, `test_product_intake_knowledge_completion.py`, `test_g2_g4_evidence_truth.py` | NOT VERIFIED for this SHA | NOT AVAILABLE | NOT AVAILABLE | PARTIALLY_VERIFIED | PARTIALLY_VERIFIED | GAP VERIFIED: no olfactory/notes/accords/performance fragrance fields evidenced | DEFERRED TO ARCHITECTURE REVIEW | POSSIBLY REQUIRED AFTER ARCHITECTURE REVIEW | POSSIBLY REQUIRED AFTER ARCHITECTURE REVIEW | Grok | NOT_CONFIRMED | 2026-09-27 |
| PI-V1-05 | Evidence / provenance | Source-traceable claims | `app/models/evidence.py`; `EvidenceService`; `ResearchDraftService` | same | Requires source_type/source_reference/claim; claim_type; qa_status; conflict_status; research draft → PENDING | `POST .../research-draft`; evidence routers | `test_g2_g4_evidence_truth.py`, `test_evidence.py` | NOT VERIFIED for this SHA | NOT AVAILABLE | NOT AVAILABLE | PARTIALLY_VERIFIED | PARTIALLY_VERIFIED | NO GAP VERIFIED for generic evidence; perfume-specific evidence types NOT PRESENT | NOT ASSESSED | NOT ASSESSED | NOT ASSESSED | Grok | NOT_CONFIRMED | 2026-09-27 |
| PI-V1-06 | Unknown / conflict | Explicit unknown vs missing; conflict handling | Evidence `claim_type` includes UNKNOWN/CONFLICT; `conflict_status`; ProfileFact `value_state` | same | Research draft defaults evidence_status UNKNOWN; conflict resolution API path in EvidenceService; empty PK field ≠ explicit UNKNOWN | `EvidenceService.resolve_conflict`; readiness blocks CONFLICT | g2/g4 evidence tests; profile_fact value_state tests | NOT VERIFIED for this SHA | NOT AVAILABLE | NOT AVAILABLE | PARTIALLY_VERIFIED | PARTIALLY_VERIFIED | POSSIBLE GAP — INSUFFICIENT EVIDENCE that EMPTY vs UNKNOWN is enforced for all product fields | DEFERRED TO ARCHITECTURE REVIEW | POSSIBLY REQUIRED AFTER ARCHITECTURE REVIEW | POSSIBLY REQUIRED AFTER ARCHITECTURE REVIEW | Grok | NOT_CONFIRMED | 2026-09-27 |
| PI-V1-07 | Customer preference / avoidance / context | Customer-side inputs | `ProfileFact` attribute_key limited to skin/hair/scalp/age_range/concerns; Case/consultation paths exist | same | No fragrance preference/avoidance keys in ProfileFact constraint; visit context via Case not fully mapped here | profile_fact services/APIs | `test_profile_fact.py`, consultation tests | NOT VERIFIED for this SHA | NOT AVAILABLE | NOT AVAILABLE | PARTIALLY_VERIFIED | PARTIALLY_VERIFIED | GAP VERIFIED: no evidenced fragrance taste/avoidance model | DEFERRED TO ARCHITECTURE REVIEW | POSSIBLY REQUIRED AFTER ARCHITECTURE REVIEW | POSSIBLY REQUIRED AFTER ARCHITECTURE REVIEW | Grok | NOT_CONFIRMED | 2026-09-27 |
| PI-V1-08 | Eligibility / decision boundary | Gates before recommendation | Catalog filter ACTIVE+VERIFIED+VALID+stock; `_map_eligibility` | same | Unavailable stock excluded from catalog set; eligibility strings include INELIGIBLE paths; need_match used | `recommendation_service.py` | recommendation / f2 / medical gate tests (generic) | NOT VERIFIED for this SHA | NOT AVAILABLE | NOT AVAILABLE | PARTIALLY_VERIFIED | PARTIALLY_VERIFIED | NO GAP VERIFIED for generic gates; fragrance-specific eligibility NOT PRESENT | NOT ASSESSED | NOT ASSESSED | NOT ASSESSED | Grok | NOT_CONFIRMED | 2026-09-27 |
| PI-V1-09 | Decision trace / auditability | Trace inputs to output | `Recommendation` model; mutation logs product/evidence; specialist_override; outcome assessment | same | Recommendations persisted; product mutation log; evidence mutation log; override model present — **full explanation package NOT fully verified line-by-line in this pass** | recommendation generate; mutation log routes | various recommendation/outcome tests | NOT VERIFIED for this SHA | NOT AVAILABLE | NOT AVAILABLE | PARTIALLY_VERIFIED | PARTIALLY_VERIFIED | POSSIBLE GAP — INSUFFICIENT EVIDENCE for complete perfume decision explanation | DEFERRED TO ARCHITECTURE REVIEW | POSSIBLY REQUIRED AFTER ARCHITECTURE REVIEW | NOT ASSESSED | Grok | NOT_CONFIRMED | 2026-09-27 |
| PI-V1-10 | Docs / QA / CI governance | Governance artifacts | `docs/` contracts/audit; `.github/workflows/test.yml`, `hbi_auto.yml`, etc.; category includes PERFUME | same | P4/intake contracts, audit folder, workflow YAML present; category enum includes PERFUME for reporting/catalog | N/A | governance-tests job name used historically | **CI success for bbe1a4ee NOT VERIFIED in this audit** | NOT REQUIRED for static governance presence | NOT AVAILABLE | PARTIALLY_VERIFIED | PARTIALLY_VERIFIED | NO GAP VERIFIED for existence of CI/docs; perfume intelligence docs NOT PRESENT | NOT ASSESSED | NOT ASSESSED | NOT ASSESSED | Grok | NOT_CONFIRMED | 2026-09-27 |

---

## 7. Verified Current HBI Capabilities

(Generic platform capabilities evidenced at inspected SHA; **not** claimed as perfume intelligence.)

1. **Product identity:** `Product.product_id` as primary key with shared FKs.  
2. **Lifecycle vocabulary on Product:** DRAFT → … → ACTIVE (and reject/archive) via constraints + `ProductTransitionService`.  
3. **Inventory quantity and catalog stock filter:** `quantity_available > 0` in `find_by_identity_status_and_active`.  
4. **Evidence model with source fields, claim_type, qa_status, conflict_status.**  
5. **Research Draft → PENDING Evidence path.**  
6. **ProductKnowledge flat projection from approved/verified non-conflict evidence.**  
7. **Duplicate check service** (identity/barcode/size/variant behavior) on create path post–WP-01 lineage.  
8. **ProfileFact** with explicit value_state including UNKNOWN (customer attributes constrained to listed keys).  
9. **Recommendation generation** that loads ACTIVE∩VERIFIED∩VALID∩stock products and maps eligibility.  
10. **Category id `PERFUME`** allowed in category constraint (catalog taxonomy, not olfactory engine).

---

## 8. Partially Verified Capabilities

- End-to-end **runtime** operator flows (UI → production DB): NOT AVAILABLE.  
- CI **green on exact inspected SHA**: workflow files seen; run result for `bbe1a4ee…` not recorded in this audit.  
- Completeness of recommendation **explanation/trace** payload for all engine inputs.  
- Whether every product text field distinguishes EMPTY vs explicit UNKNOWN at approval gates (skin contract may differ; not re-validated here for perfume).

---

## 9. Unknown / Not Verified Areas

- Production catalog contents for category PERFUME.  
- Any hidden fragrance modules outside searched paths.  
- Live CI status of `bbe1a4eed81937fae1c7ecb7be5bb28af551458b`.  
- Independent verification of every matrix cell.

---

## 10. Verified Gaps (evidence of absence for fragrance V1 needs)

| Gap | Evidence of absence / limitation |
|-----|----------------------------------|
| Dedicated concentration field | No `concentration` column on Product; only generic variant/size |
| Olfactory structured knowledge | No notes/accords/family/sillage/longevity fields on ProductKnowledge |
| Fragrance preference/avoidance profile keys | ProfileFact `attribute_key` check constraint lists skin/hair/scalp/age_range/concerns only |
| Perfume-specific intelligence services | No matching modules in app search for olfactory/sillage/longevity engines |

These are **observed absences**, not architecture decisions.

---

## 11. Contradictions

| Topic | Notes |
|-------|--------|
| Category `PERFUME` vs Perfume Intelligence | Category exists for classification/reporting; does **not** contradict absence of fragrance intelligence engine — different concepts |
| File existence vs capability | Satisfied methodologically; no contradiction found that a name alone was treated as full capability |

---

## 12. Independent Verification Result

```text
INDEPENDENT VERIFICATION NOT COMPLETED
```

No second auditor confirmed matrix rows. All Independent Verifier cells: **NOT_CONFIRMED**.

This audit must **not** be treated as fully verified.

---

## 13. Deferred Items

(As required by mission non-scope — listed only, not designed.)

Similarity; numeric scoring; automatic ranking/recommendation/learning; advanced customer event history; advanced performance model; derived olfactory profile; new masters/engines; cross-market equivalence; formula intelligence.

---

## 14. Explicit Non-Decisions

This audit does **not**:

- Choose Reuse / Extend / New  
- Define a Contract  
- Recommend implementation  
- Propose Product Master, Evidence engine, or ProductKnowledge redesign  
- Propose scoring or similarity  
- Authorize code, schema, migration, API, Issue, or PR (beyond this single documentation file on a docs branch)

---

## 15. Final Audit Verdict

**B. AUDIT PARTIAL — ADDITIONAL EVIDENCE REQUIRED**

**Reasons (evidence-based):**

1. Static repository reality for the ten V1 areas was inspected at SHA `bbe1a4eed81937fae1c7ecb7be5bb28af551458b`.  
2. Runtime evidence was **NOT AVAILABLE**.  
3. CI outcome for the exact inspected SHA was **NOT VERIFIED** in this pass.  
4. **Independent verification was NOT COMPLETED.**  

Therefore the audit establishes a **partial, auditor-only** reality baseline suitable for Domain Owner review, not a fully verified closure.

---

*End of PERFUME-INTELLIGENCE-V1-HBI-REALITY-INTEGRATION-AUDIT*
