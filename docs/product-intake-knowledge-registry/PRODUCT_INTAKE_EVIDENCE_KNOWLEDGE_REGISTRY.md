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
| Contract | `docs/architecture/SKIN_PRODUCT_INTAKE_EXECUTION_CONTRACT_v1.1.md` | CANONICAL |
| Operational tracker | Issue #283 | CANONICAL |
| Phase roadmap | `docs/product-intake/PRODUCT_INTAKE_ROADMAP.md` | CANONICAL |
| Runtime execution log | `docs/product-intake/PRODUCT_INTAKE_EXECUTION_LOG.md` | CANONICAL |
| A1–A9 ledger | `docs/product-intake/G8_ACCEPTANCE_EVIDENCE.md` | CANONICAL |
| Execution-control | `docs/01_project_control/ROADMAP_PRODUCT_INTAKE_G8.md` | CANONICAL |
| Strategic Skin baseline | `docs/architecture/SKIN_PRODUCT_INTAKE_STRATEGIC_BASELINE_v0.1.md` | DESIGN / NOT AUTHORIZED |
| New Home IA | Issue #352 + current New Home code | CANONICAL for homepage only |

## 3. Two required angles

### A. Customer / Problem side
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
