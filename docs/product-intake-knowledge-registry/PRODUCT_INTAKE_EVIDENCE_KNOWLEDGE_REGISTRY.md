# HBI Product Intake — Evidence & Knowledge Registry

**Status:** EXECUTION REGISTRY — PO approved for consolidation work  
**Scope:** Skin Product Intake / Product Intelligence / Problem–Need connection  
**Last verified against master:** `fc1f8f585f4f9d6cfa487a4709a24b57c3026d4b` (2026-10-16; historical verification point, not a claim that this SHA remains HEAD after later merges)  
**Last reconciled:** 2026-10-16

## 1. Purpose

این سند سیاست جدید یا جایگزین قرارداد نیست. هدف آن جلوگیری از گم‌شدن، تکرار و اجرای ناخواسته اسناد قدیمی است.

طبقه‌بندی:
- **CANONICAL** — مرجع جاری همان موضوع
- **SUPPORTING** — مدرک/پیاده‌سازی پشتیبان
- **HISTORICAL** — فقط برای audit
- **SUPERSEDED** — جایگزین شده؛ اجرا نشود
- **DESIGN / NOT AUTHORIZED** — baseline طراحی، بدون مجوز implementation
- **RUNTIME EVIDENCE** — مدرک اجرای واقعی

اصل: یک مرجع برای هر منظور؛ تاریخچه حفظ شود ولی محتوای منسوخ اجرا نشود.

## 2. Canonical map

| حوزه | مرجع | وضعیت |
|---|---|---|
| Contract | `docs/product-intake-knowledge-registry/SKIN_PRODUCT_INTAKE_EXECUTION_CONTRACT_v1.1.md` | CANONICAL |
| Operational tracker | Issue #283 | CANONICAL |
| Phase roadmap | `docs/product-intake-knowledge-registry/PRODUCT_INTAKE_ROADMAP.md` | CANONICAL |
| Runtime execution log | `docs/product-intake-knowledge-registry/PRODUCT_INTAKE_EXECUTION_LOG.md` | CANONICAL |
| A1–A9 ledger | `docs/product-intake-knowledge-registry/G8_ACCEPTANCE_EVIDENCE.md` | CANONICAL |
| Execution-control | `docs/product-intake-knowledge-registry/ROADMAP_PRODUCT_INTAKE_G8.md` | CANONICAL |
| Strategic Skin baseline | `docs/product-intake-knowledge-registry/SKIN_PRODUCT_INTAKE_STRATEGIC_BASELINE_v0.1.md` | DESIGN / NOT AUTHORIZED |
| Skin Problem Space Map V0.1 | `docs/product-intake-knowledge-registry/SKIN_PROBLEM_SPACE_MAP_V0.1.md` | SUPPORTING — source artifact copied from Issue #293 comment 5972920377; later correction/acceptance records remain historical governance evidence |
| New Home IA | Issue #352 + current New Home code | CANONICAL for homepage only |

## 3. Two required angles

### A. Customer / Problem side

Supporting artifact: `SKIN_PROBLEM_SPACE_MAP_V0.1.md`. It structures the customer/problem side but is not a complete Problem Bank or Treatment Database; consult the historical governance records on Issue #293 for later corrections and acceptance status.
```
Customer language
 → Skin Problem Representation
 → Context + Provenance
 → Safety / Decision boundary
 → Need candidate
```

Need تشخیص پزشکی نیست و Need به‌تنهایی مجوز recommendation نیست.

### B. Product / Gallery side
```
Product identity
 → Research / Input
 → Evidence
 → QA / Conflict Resolution
 → ProductKnowledge
 → Product eligibility
 → Recommendation compatibility
```

### Connection
```
Customer Problem
 → Canonical Need
 → Eligible Gallery Product
 → Recommendation
 → Operator Decision
```

No-product recommendation یا referral نیز خروجی معتبر است.

## 3A. Canonical categorization — Skin problems

The problem-side catalog is maintained in `SKIN_PROBLEM_SPACE_MAP_V0.1.md`, not duplicated as a second list here. Its current draft groups the P01–P61 discovery stock into ten observational shelves:

| Shelf | Domain | Catalog handling |
|---|---|---|
| S01 | Barrier / Hydration / Surface | Dryness, hydration-related presentation, sensitivity and surface integrity |
| S02 | Oil / Sebum / Follicular Balance | Oiliness, sebum and related follicular characteristics |
| S03 | Acne / Follicular / Pore Presentation | Acne presentations, lesion subtypes and related follicular presentations |
| S04 | Pigmentation / Color | Hyperpigmentation, hypopigmentation and related presentations |
| S05 | Redness / Inflammation / Rash | Redness, flushing, rash and inflammatory presentations |
| S06 | Infection / Infestation | Infection- and infestation-related clinical presentations |
| S07 | Texture / Keratinization / Surface Growth | Texture, keratinization and selected surface growths |
| S08 | Lesions / Growths / Change | Moles, lesions and changes requiring careful safety boundaries |
| S09 | Sun / UV-Related Change | UV context and related findings |
| S10 | Systemic / Autoimmune / Clinically Significant Skin Presentation | Systemic-associated and clinically significant presentations |

**Boundary rule:** these shelves organize discovery information; they are not a diagnosis taxonomy, a treatment database, an accepted Need list, or authorization to recommend products. The map explicitly preserves distinctions among Problem/Presentation, Manifestation, Clinical Condition, Safety/Referral Signal, Context and Need. Its V0.1 status, source limitations, overlap register and UNKNOWN/GAP items remain in the map itself.

Do not flatten the following into duplicate problems without evidence: parent vs manifestation, presentation vs clinical condition, sequela vs original problem, contextual factor vs problem, and ordinary-care presentation vs safety/referral signal. Use the map's P-codes and boundary register as the stable working references until an approved later version supersedes them.

## 3B. Canonical categorization — products in the gallery

The available eight-document package does **not** establish a complete, verified inventory of all products currently present in the Gallery. Therefore this registry must not present a test candidate as an existing Gallery product or invent missing product records.

For each product record discovered in the repository, organize information under these groups, retaining source and status for every assertion:

1. **Identity and deduplication:** display name, brand, product line, variant/formulation, size, market, barcode/GTIN if known, packaging/identity source, duplicate-check result.
2. **Composition:** full ingredient/INCI list, active or notable ingredients, concentration only when explicitly sourced, and formulation/variant boundaries.
3. **Manufacturer statements:** intended use, directions, marketing claims and manufacturer-described target concerns. These remain `MANUFACTURER_CLAIM` unless independently supported.
4. **Evidence-supported knowledge:** claim, evidence type, source, date/version where available, applicability and limitations.
5. **Use and compatibility:** intended use, skin concern/Need relation, target skin/site where supported, suitability conditions and reasons.
6. **Safety and exclusions:** avoid/caution conditions, warnings, uncertainty and any safety/referral boundary supported by the evidence.
7. **Governance state:** source provenance, reviewer/approval status, lifecycle state, conflicts, unknowns and readback evidence.

Do not create a new schema or eligibility flag as a consequence of this documentation taxonomy. Existing contract, claim types and approval gates remain binding.

### Product identity discrepancy requiring resolution

The current package contains two differently worded Numbuzin references:
- `PRODUCT_INTAKE_ROADMAP.md` names the temporary test candidate as **Numbuzin No.9 NAD+ BIO Lifting-sil Essence, 50 mL**.
- The WP-Research-04 line in this registry names **Numbuzin 50 Peptides**.

The current documents do not prove these are the same product, the same variant, or two distinct products. Record this as **IDENTITY CONFLICT / UNRESOLVED** until an authoritative package/manufacturer identity source resolves it. Do not merge the names, infer an equivalence, or treat either reference as proof that the item is in the live Gallery. The roadmap explicitly limits its named candidate to a temporary test role.

### Product catalog status at this reconciliation

- Verified complete live Gallery inventory: **NOT PRESENT in this eight-document package**.
- Named temporary test candidate: **present in the roadmap; not proof of a live Gallery record**.
- Numbuzin name/variant equivalence: **UNKNOWN / CONFLICT**.
- Product-specific INCI, source-attributed claims, suitability and caution details: must be sourced and reviewed per product; do not infer them from a product name.
- Next cataloging rule: add only source-backed product identities found in authoritative repository/runtime evidence; retain uncertain matches as candidates for human review.

## 4. What is implemented

- Product Line برای intake باید صریحاً توسط اپراتور انتخاب شود؛ از نام/دسته/AI inference نشود.
- DuplicateCheck در مسیر create محصول enforce شده است.
- Product registration از stock receipt جداست؛ ایجاد محصول موجودی ایجاد نمی‌کند.
- شش claim type V1: `FACT`, `MANUFACTURER_CLAIM`, `EVIDENCE`, `INFERENCE`, `UNKNOWN`, `CONFLICT`.
- Evidence و ProductKnowledge مرز governed دارند.
- Research Draft orchestration موجود است، اما خودش web research engine نیست.
- AI اختیار approval/activation یا تبدیل inference به fact ندارد.
- New Home → Products → Product Intake در کد فعلی وجود دارد.

## 5. Verified code anchors

- `app/main.py`: Products/Evidence routers و G8 evidence middleware.
- `app/services/evidence_service.py`: evidence lifecycle و conflict handling.
- `app/services/product_knowledge_service.py`: ProductKnowledge از evidence مورد قبول.
- `app/services/research_draft_service.py`: Research Draft orchestration.
- `app/services/product_service.py`: product creation و evidence/knowledge seed.
- `frontend/src/pages/ProductIntakePanel.tsx`: intake UI و DuplicateCheck.
- `frontend/src/pages/NewHomePage.tsx`: New Home product-intake route.

## 6. Confirmed missing capability

### WP: Smart Product Research & Intelligence Enrichment

هدف:
```
Product identity
 → Automated research
 → Source collection
 → Structured extraction
 → Claim classification
 → Evidence-linked Research Draft
 → Human review / QA
 → ProductKnowledge
```

منابع پیشنهادی:
1. Official manufacturer/product page
2. Official ingredient/INCI information
3. Reliable scientific literature/databases
4. Reliable secondary corroboration
5. Public packaging/market information فقط برای identity corroboration، نه اثبات efficacy

هر assertion باید provenance داشته باشد؛ اختلاف منابع = CONFLICT، نه حدس سیستم.

## 7. Target research dossier

- Identity
- Variant / size / market
- Ingredients / INCI
- Active or notable ingredients
- Manufacturer claims
- Evidence-backed benefits
- Uses / intended use
- Target concerns / relevant needs
- Suitability
- Avoid / caution conditions
- Safety information
- Evidence strength/status
- Source references
- Unknowns
- Conflicts
- AI inference + rationale

وجود این fieldها به‌تنهایی مجوز schema/API change نیست.

## 8. Explicit exclusions

فعلاً وارد این کار نمی‌شوند مگر با تصمیم جدید:
- diagnosis engine
- full Customer × Product decision engine
- recommendation scoring/weights/threshold redesign
- full INCI ontology
- SKU/GTIN allocation
- full regulatory engine
- adverse-event management
- OCR/PDF ingestion
- supplier API ingestion
- uncontrolled independent AI ingestion pipeline
- new Product Eligibility table/boolean
- schema/migration صرفاً برای یک مفهوم تأییدنشده

## 9. Historical handling

محتوای قدیمی Homepage که با Issue #352 تعارض دارد، اجرا نشود. PRها/branches صراحتاً superseded در Issue #283 اجرا نشوند. Fixture/test-product evidence، proof محصول واقعی نیست. Chat summaries نیز در برابر repository evidence مرجع نیستند.

## 10. Evidence hierarchy

1. Current explicit PO decision
2. Binding approved contract
3. Current canonical roadmap/ledger
4. Current repository code at pinned SHA
5. Tests/CI
6. Runtime raw evidence
7. Historical issues/PRs/comments
8. Chat/agent recollection

## 11. Execution work packages

### WP-Research-01 — Reality & boundary
Inventory existing research/evidence APIs/models; reuse before creating anything; define source/provenance, unknown and conflict behavior.

### WP-Research-02 — Research Draft generation
برای محصول با هویت مشخص، منابع مجاز را جمع‌آوری و assertionهای source-attributed بسازد؛ بدون approval/activation خودکار.

### WP-Research-03 — New Home integration
در **محصولات → ورود محصول** یک action روشن برای «پژوهش / تکمیل هوشمند اطلاعات»؛ نمایش مقدار پیشنهادی همراه منبع؛ ویرایش توسط اپراتور؛ حفظ UNKNOWN/CONFLICT.

### WP-Research-04 — Acceptance
Numbuzin 50 Peptides؛ identity، provenance، claim taxonomy، Evidence→ProductKnowledge، Draft semantics، production isolation و independent review.

## 12. Current status

| Item | Status |
|---|---|
| New Home product menu | IMPLEMENTED |
| Product Intake UI | IMPLEMENTED |
| DuplicateCheck | IMPLEMENTED |
| Evidence / ProductKnowledge governance | IMPLEMENTED |
| Research Draft orchestration | IMPLEMENTED |
| Automated external research/enrichment | **NOT IMPLEMENTED / NOT VERIFIED** |
| G8 | **BLOCKED / NOT VERIFIED** |

## 13. Operating rule

```
Find canonical record
 → Check current code
 → Check existing PR/branch
 → Identify exact gap
 → One WP / one change path
 → Test
 → Independent verification
 → PO acceptance
```

این Registry index/cleanup map است و Contract یا canonical G8 records را override نمی‌کند.


## 14. Single-entry-point rule — anti-scatter control (2026-10-16)

**The only intended entry point for Product Intake documentation is this registry.** PR #393 has been merged. The consolidated destinations listed below are the intended working locations; the prior pre-merge claim that old paths remain on `master` is historical and no longer current. Treat the table as a relocation map, not as permission for an unreviewed deletion. Before any further cleanup, verify each legacy path against current `master`, validate inbound links, and preserve the Git history/audit trail. Any remaining legacy copy must be handled in a reviewed, item-specific change.

### 14.1 Canonical destination map and legacy paths

| Document (preserve original filename) | Consolidated destination | Legacy path recorded in pre-merge audit (verify current status before cleanup) | Handling |
|---|---|---|---|
| `SKIN_PRODUCT_INTAKE_EXECUTION_CONTRACT_v1.1.md` | `docs/product-intake-knowledge-registry/SKIN_PRODUCT_INTAKE_EXECUTION_CONTRACT_v1.1.md` | `docs/architecture/SKIN_PRODUCT_INTAKE_EXECUTION_CONTRACT_v1.1.md` | Preserve approved contract text; remove old path only in an explicitly reviewed move/cleanup change after destination is verified |
| `SKIN_PRODUCT_INTAKE_STRATEGIC_BASELINE_v0.1.md` | `docs/product-intake-knowledge-registry/SKIN_PRODUCT_INTAKE_STRATEGIC_BASELINE_v0.1.md` | `docs/architecture/SKIN_PRODUCT_INTAKE_STRATEGIC_BASELINE_v0.1.md` | Keep DESIGN / NOT AUTHORIZED |
| `PRODUCT_INTAKE_ROADMAP.md` | `docs/product-intake-knowledge-registry/PRODUCT_INTAKE_ROADMAP.md` | `docs/product-intake/PRODUCT_INTAKE_ROADMAP.md` | Canonical destination |
| `PRODUCT_INTAKE_EXECUTION_LOG.md` | `docs/product-intake-knowledge-registry/PRODUCT_INTAKE_EXECUTION_LOG.md` | `docs/product-intake/PRODUCT_INTAKE_EXECUTION_LOG.md` | Preserve history; append facts, do not rewrite historical results |
| `G8_ACCEPTANCE_EVIDENCE.md` | `docs/product-intake-knowledge-registry/G8_ACCEPTANCE_EVIDENCE.md` | `docs/product-intake/G8_ACCEPTANCE_EVIDENCE.md` | A1–A9 only from raw execution evidence; current G8 remains BLOCKED / NOT VERIFIED |
| `ROADMAP_PRODUCT_INTAKE_G8.md` | `docs/product-intake-knowledge-registry/ROADMAP_PRODUCT_INTAKE_G8.md` | `docs/01_project_control/ROADMAP_PRODUCT_INTAKE_G8.md` | Operational roadmap destination |
| `SKIN_PROBLEM_SPACE_MAP_V0.1.md` | `docs/product-intake-knowledge-registry/SKIN_PROBLEM_SPACE_MAP_V0.1.md` | No equivalent master destination verified in this audit | Structural map only; preserve its version and source caveats |

**Relocation status after PR #393:** the consolidated destinations listed above are the intended working locations. The original PR review recorded that legacy paths were removed on the PR #393 branch and destinations created/updated. Do not rely on the old pre-merge statement as current runtime fact. Before any additional cleanup, verify each legacy path and inbound link against the current base branch; preserve Git history and handle any remaining legacy copy in a reviewed, item-specific change. Do not delete legacy paths manually merely to enforce a single entry point.

### 14.2 Contract authority relationship — generic v1 vs skin execution v1.1

The older `docs/01_project_control/product_intake/PRODUCT_INTAKE_CONTRACT_v1.md` is retained as a **historical design/acceptance record**, not a parallel current authority for skin-specific execution. Its recorded PO acceptance is tied to baseline `42cc77ec` and date 2026-09-07. The later `SKIN_PRODUCT_INTAKE_EXECUTION_CONTRACT_v1.1.md` is the current PO-approved contract baseline for skin-product intake decisions and skin-specific requirements.

Apply the documents by scope:
- **P4 Product Intake Governance Contract** remains binding for the governed product lifecycle, roles, approval/activation transitions, and mutation/audit rules where applicable.
- **Skin Product Intake Execution Contract v1.1** is the current authority for skin-product intake, safety/UNKNOWN requirements, claim taxonomy, and skin-specific eligibility boundaries.
- **Generic Product Intake Contract v1** is historical context for its original design decisions. Do not use it to override v1.1 on skin-specific matters or to create a second approval/state machine.
- If a concrete clause appears to conflict and cannot be resolved by this scope split, record the exact clauses and obtain PO adjudication in a reviewed change; do not silently delete or rewrite the historical contract.

### 14.3 Problem Bank / Problem Space source register

These artifacts remain separate open/draft PRs and are **not** silently absorbed or authorized by PR #393. This register is the sole navigation point until a separately approved consolidation decision says otherwise.

| Source artifact | Scope | State / handling |
|---|---|---|
| [Issue #293 — Problem Space / Problem Bank governance](https://github.com/vahidmaghsoudi2/hbi/issues/293) | Governance, acceptance, corrections, audit trail | Historical governance source; decisions/comments remain authoritative evidence |
| [Issue #301](https://github.com/vahidmaghsoudi2/hbi/issues/301) | Customer Reality Capture Principles V0.1 | Supporting source |
| [Issue #302](https://github.com/vahidmaghsoudi2/hbi/issues/302) | Customer Reality Source Acquisition Planning V0.1 | Supporting source |
| [Issue #294](https://github.com/vahidmaghsoudi2/hbi/issues/294) | HBI Skin Discovery Foundation V1 | Supporting source |
| [PR #303](https://github.com/vahidmaghsoudi2/hbi/pull/303) | S03 | Open draft; not merged |
| [PR #304](https://github.com/vahidmaghsoudi2/hbi/pull/304) | S04 | Open draft; not merged |
| [PR #305](https://github.com/vahidmaghsoudi2/hbi/pull/305) | Old S05 | Closed unmerged; superseded by #306; do not use as current |
| [PR #306](https://github.com/vahidmaghsoudi2/hbi/pull/306) | Corrected S05 | Open draft; not merged |
| [PR #307](https://github.com/vahidmaghsoudi2/hbi/pull/307) | S06 | Open draft; not merged |
| [PR #308](https://github.com/vahidmaghsoudi2/hbi/pull/308) | S07 | Open draft; not merged |
| [PR #309](https://github.com/vahidmaghsoudi2/hbi/pull/309) | S08 | Open draft; not merged |
| [PR #310](https://github.com/vahidmaghsoudi2/hbi/pull/310) | S09 | Open draft; not merged |
| [PR #311](https://github.com/vahidmaghsoudi2/hbi/pull/311) | S10 | Open draft; not merged |
| [PR #312](https://github.com/vahidmaghsoudi2/hbi/pull/312) | Old cross-shelf audit | Superseded by corrected #313; do not use as current |
| [PR #313](https://github.com/vahidmaghsoudi2/hbi/pull/313) | Corrected P16 cross-shelf audit | Open draft; not merged |

**Do not misstate draft status as implementation or merge approval.** The current frozen Map V0.1 records P16 differently from the later correction/accepted audit. The later governance correction states P16 primary shelf is S03 and no cross-shelf relation; preserve the frozen Map unchanged and surface the discrepancy here. Relevant record: [Issue #293 correction comment](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5979025129). Also retain the management acceptance and pre-pilot audit trail: [acceptance with conditions](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5979222785), [pre-pilot readiness](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5982706812), [Customer Reality boundary](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5979521659), [L1/L2 evidence plan](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5979781170), [verified customer language = 0 / Phase 2.1 blocked](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5982622015).

### 14.4 Consultation and lifecycle implementation references

These are implementation/supporting references, not alternate Product Intake roadmaps:

- Consultation framework / reality / vertical slice: Issues [#208](https://github.com/vahidmaghsoudi2/hbi/issues/208), [#209](https://github.com/vahidmaghsoudi2/hbi/issues/209), [#214](https://github.com/vahidmaghsoudi2/hbi/issues/214), [#221](https://github.com/vahidmaghsoudi2/hbi/issues/221), [#223](https://github.com/vahidmaghsoudi2/hbi/issues/223), [#225](https://github.com/vahidmaghsoudi2/hbi/issues/225); merged PR [#226](https://github.com/vahidmaghsoudi2/hbi/pull/226).
- Customer response and outcomes: Issues [#232](https://github.com/vahidmaghsoudi2/hbi/issues/232), [#237](https://github.com/vahidmaghsoudi2/hbi/issues/237), [#249](https://github.com/vahidmaghsoudi2/hbi/issues/249), [#250](https://github.com/vahidmaghsoudi2/hbi/issues/250), [#252](https://github.com/vahidmaghsoudi2/hbi/issues/252), [#254](https://github.com/vahidmaghsoudi2/hbi/issues/254), [#255](https://github.com/vahidmaghsoudi2/hbi/issues/255); implementation PRs [#229](https://github.com/vahidmaghsoudi2/hbi/pull/229), [#233](https://github.com/vahidmaghsoudi2/hbi/pull/233), [#238](https://github.com/vahidmaghsoudi2/hbi/pull/238), [#246](https://github.com/vahidmaghsoudi2/hbi/pull/246), [#253](https://github.com/vahidmaghsoudi2/hbi/pull/253), [#259](https://github.com/vahidmaghsoudi2/hbi/pull/259).
- Purchase-history / traceability boundary: merged PRs [#141](https://github.com/vahidmaghsoudi2/hbi/pull/141) and [#152](https://github.com/vahidmaghsoudi2/hbi/pull/152); PR [#143](https://github.com/vahidmaghsoudi2/hbi/pull/143) remains unmerged and must not be treated as integrated.
- Recommendation/product-intake context: Issue [#37](https://github.com/vahidmaghsoudi2/hbi/issues/37) prohibits numeric weighting; Issue [#283](https://github.com/vahidmaghsoudi2/hbi/issues/283) is the operational tracker; merged PR [#393](https://github.com/vahidmaghsoudi2/hbi/pull/393) recorded the documentation consolidation change.

Historical issue/PR threads are preserved as provenance/audit evidence; do not copy them into new competing roadmap documents. The registry records their role and links to the source.

### 14.5 What “centralized” means — acceptance criteria

Before declaring consolidation complete, verify all of the following against the merged target branch:

1. Every canonical document listed in §2 exists at its designated destination with the expected filename and non-empty content.
2. Legacy duplicate paths listed in §14.1 are removed only after a byte/content and link audit; no approved contract is edited as part of the move.
3. Every still-open/draft Problem Bank PR and its current accepted/rejected/superseded status is indexed here, not copied into an unauthorized second canonical version.
4. The P16 discrepancy, P08/HBI relevance OPEN items, S01/S02 direct-artifact audit PARTIAL, and Customer Language Sources = 0 / Phase 2.1 BLOCKED are visible and not silently closed.
5. Links resolve; no claim is made that a draft PR is merged, that the live Gallery inventory is complete, or that G8 ran.
6. G8 stays **BLOCKED / NOT VERIFIED** until isolated-database preflight, real execution, A1–A9 raw evidence, cleanup, and independent review are documented.
7. One source of truth per purpose: Issue #283 for operational tracking; this registry for navigation and evidence mapping; the approved contract for binding behavior; the execution log and A1–A9 ledger for runtime facts.

Until those checks pass, status is **CONSOLIDATION IN PROGRESS — NOT YET SINGLE-LOCATION VERIFIED**.
