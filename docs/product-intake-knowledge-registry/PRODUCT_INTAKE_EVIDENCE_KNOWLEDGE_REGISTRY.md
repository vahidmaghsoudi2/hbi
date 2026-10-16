# HBI Product Intake — Evidence & Knowledge Registry

**Status:** EXECUTION REGISTRY — PO approved for consolidation work  
**Scope:** Skin Product Intake / Product Intelligence / Problem–Need connection  
**Baseline:** `335fd6e472dde72b9907366acaa04db28ebed943`  
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
