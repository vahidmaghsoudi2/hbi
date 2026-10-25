# Skin product intake — fixed template forms (V1)

**Status:** DRAFT specification for implementation planning  
**Date:** 2026-10-25  
**Canonical location:** `docs/homepage/product-management/SKIN_INTAKE_TEMPLATE_FORMS_V1.md`  
**User path:** منوی اصلی → مدیریت محصولات → ورود و ویرایش محصول  
**Authority:** Product Owner decisions and Gates remain in [Issue #406](https://github.com/vahidmaghsoudi2/hbi/issues/406). This file is the canonical operational field map, not a second decision register.  
**Research continuity:** [PR #411](https://github.com/vahidmaghsoudi2/hbi/pull/411) remains the subordinate seven-product research ledger; it is not the template specification.

## 1. Purpose and scope

Define fixed, type-specific boxes for skin-care product intake so future smart completion can fill structured fields rather than requiring operators to type every attribute freely. This document is **P0 documentation only**. It does not itself implement UI behavior or create/approve product records.

The V1 template decisions below are approved in [Issue #406, Product Owner decision](https://github.com/vahidmaghsoudi2/hbi/issues/406#issuecomment-6389070595).

## 2. Architecture boundaries

```text
product_line = SKIN (operator-selected; not inferred)
    └── skin_form_template (one of the nine V1 templates)
            ├── shared boxes
            ├── template-specific boxes
            └── extras box
```

| Layer | Role / boundary |
|---|---|
| `product_line = SKIN` | Existing product line; must be operator-selected |
| `skin_form_template` | Proposed discriminator for the selected fixed form; no schema implementation is authorized here |
| Existing protocol / identity fields | Existing intake flow remains authoritative |
| Template boxes | Proposed structured attributes and source-bound claims |
| Evidence / research draft | Claims remain pending research drafts; smart-fill never auto-verifies evidence |
| ProductKnowledge | Existing authorized QA path remains unchanged |
| Encyclopedia UI | Not the system of record for product intake boxes |

## 3. Approved V1 templates

The Product Owner approved nine templates and merged hydration + moisturizer into one template. See [Issue #406 decision](https://github.com/vahidmaghsoudi2/hbi/issues/406#issuecomment-6389070595).

| Code | Label (FA) |
|---|---|
| `HYDRATING_MOISTURIZER` | آبرسان / مرطوب‌کننده |
| `SUNSCREEN` | ضدآفتاب |
| `BRIGHTENING_SPOT` | روشن‌کننده / ضدلک |
| `MICELLAR` | میسلار واتر |
| `TONER` | تونر |
| `CLEANSING_GEL` | ژل شستشو |
| `ANTI_ACNE` | ضدجوش |
| `EXFOLIANT` | لایه‌بردار |
| `OTHER_SKIN` | سایر (پوست) |

V1 uses one primary template. No additional template category is in scope without a later explicit revision.

## 4. Shared boxes

| Box ID | Label (FA) | Intake rule |
|---|---|---|
| `source_ref` | منبع / لینک / برچسب | Capture the actual URL or label reference |
| `source_type` | نوع منبع | Identify manufacturer, package label, or other source |
| `market_region` | منطقه بازار | Record only when evidenced or supplied by operator |
| `stated_skin_goals` | اهداف پوستی اعلام‌شده (متنی) | Keep as text/candidate only; not a verified diagnosis or automatic P01–P61 link |
| `warnings_limits` | هشدارها و محدودیت‌ها | Transcribe source-bound warnings |
| `usage_directions` | روش مصرف | Transcribe directions from a source |
| `key_ingredients` | ترکیبات کلیدی اعلام‌شده | Capture only ingredients actually supplied by source |
| `extras` | سایر / اضافات | Preserve relevant information that has no dedicated box |

### Hard safety rules

1. Never invent ingredient concentrations, diagnoses, treatment outcomes, or cure claims.
2. Quantitative efficacy claims require a source and remain manufacturer/research claims unless separately verified through the authorized process.
3. Never automatically assign canonical skin-problem IDs (P01–P61).
4. Never infer `product_line`; the operator selects `SKIN`.
5. Similar product names do not establish identical formula, market, or version.
6. Evidence QA does not equal Product QA, approval, activation, safety clearance, or recommendation eligibility.

## 5. Template-specific boxes (minimum V1)

### 5.1 `HYDRATING_MOISTURIZER`
| Box ID | Label |
|---|---|
| `texture` | بافت (کرم / ژل / لوسیون / سرم / نامشخص) |
| `skin_feel` | حس پوستی اعلام‌شده |
| `day_night` | روز / شب / هر دو / نامشخص |
| `hydration_claim` | ادعای آبرسانی یا حفظ رطوبت (متن + منبع) |



#### 5.1.1 Detailed field contract — `HYDRATING_MOISTURIZER`

This subsection makes the first template reviewable field by field. It is a **conceptual contract for audit and PO review**, not a declaration that every key below already exists in the API, DTO, or database. Existing Product, ProductKnowledge, Evidence, DuplicateCheck, research-draft, and QA contracts remain authoritative.

| Concept / candidate key | Meaning and semantic class | Source / provenance requirement | Validation and unknown/conflict behavior | Consultation relevance |
|---|---|---|---|---|
| Brand / `Product.brand` | Product identity fact | Package label or manufacturer source tied to the exact product | Do not infer from retailer URL alone; unknown remains empty/unknown | Needed to identify the exact product |
| Exact product name / `Product.product_name` | Identity fact | Package or exact manufacturer product page | Preserve spelling and version wording; similar names are not identity proof | Needed to avoid evidence transfer between products |
| Product line / `Product.product_line` | Operator-selected classification | Explicit operator choice | Must be `SKIN` for this template; never inferred by smart-fill | Controls which form may be used |
| Variant / `Product.variant` | Identity/version fact | Package, exact SKU source, or operator-reviewed evidence | Do not default to “clear”, “tinted”, or another variant without evidence | Variant may change formula or intended use |
| Market / `Product.market_region` | Identity/version context | Package, regional manufacturer page, or verified SKU source | Unknown stays unknown; do not default to `IR` | Market-specific formulas and labels may differ |
| Size / `Product.size_value`, `Product.size_unit` | Identity/packaging fact | Package label or exact source | Number and unit must both be valid; no default 50 ml; do not infer from a sibling SKU | Helps distinguish pack sizes and duplicates |
| GTIN / `Product.barcode_gtin` | Product/package identifier | Barcode scan or verifiable package source | Preserve exact digits; no generated barcode | Strong identity clue, not a substitute for version checks |
| Packaging version / `Product.packaging_version` | Version context | Dated package image, manufacturer source, or documented operator observation | Record only what can be distinguished; unknown is allowed | Prevents old-label evidence being assigned to a new formula |
| Identity status / `Product.identity_status` | Existing workflow status | Existing identity-review path | Use only existing allowed values and transition rules | Must be resolved before exact-product claims are trusted |
| Full INCI / candidate detail over `ProductKnowledge.ingredients` | Source fact about the labelled formula | Full package INCI or exact manufacturer source, with market/version noted | Distinguish full INCI from selected key ingredients; partial list must be labelled partial | Enables ingredient review without claiming final-product efficacy |
| Key ingredients / `key_ingredients` | Source-reported subset, not full INCI | Explicitly named by manufacturer or visible on package | Store only ingredients actually named; no concentration inference | Useful for triage and research prioritization |
| Ingredient roles / `ProductKnowledge.ingredient_roles` | Scientific interpretation/inference | Ingredient identity plus a reliable technical reference where needed | Role may be multi-valued and context-dependent; mark as inference, not a manufacturer fact unless the source says so | Helps explain plausible mechanisms, not prove product outcomes |
| Texture / `texture` | Manufacturer claim or operator observation | Exact product description or clearly labelled observation | Allowed values may include cream, gel, lotion, serum, balm, emulsion, other, unknown; do not infer from name | May inform sensory preference, not clinical suitability by itself |
| Skin feel / `skin_feel` | Manufacturer claim or operator observation | Preserve whether it is marketing text or actual observed experience | Do not convert “lightweight” into a universal skin-type claim | May inform preference; not proof of tolerability |
| Day/night / `day_night` | Label instruction or manufacturer claim | Exact usage instructions | Values: day, night, both, unknown; do not infer from “hydrating” | Supports instruction fidelity |
| Hydration / moisture claim / `hydration_claim` | Manufacturer claim | Exact source URL or package reference; capture wording and market/version | Claim remains a claim until evaluated; numeric claims require their stated basis and units | Candidate relation to dryness/moisture needs, not automatic recommendation |
| Usage directions / `usage_directions` | Source fact / manufacturer instruction | Exact product label or manufacturer source | Preserve amount, frequency, rinse/leave-on, and area only when stated | Needed to avoid inventing usage advice |
| Warnings and limits / `warnings_limits` | Source fact and/or separately labelled reviewed limitation | Label/manufacturer source; independent limits need their own evidence | “Not stated” is not “none”; conflicting labels remain visible | Supports risk screening, not automatic safety clearance |
| Stated skin goals / `stated_skin_goals` | Manufacturer claim / free-text candidate | Exact source and market/version | Plain text only in V1; no auto-link to P01–P61 | Search/research lead only |
| Evidence record / existing `Evidence` | Claim/evidence/research assertion | Source type/reference, claim, field, claim type, market and dates where available | Preserve pending/rejected/QA state; no auto-verification | Allows reviewer to inspect support and limitations |
| Evidence strength / existing Evidence contract | Review assessment | Must follow current approved Evidence vocabulary | Do not invent a new scale or conflate source type with strength | Helps qualify confidence in a specific claim |
| Product-level knowledge status / `evidence_status` | Aggregated status, if/when semantics are approved | Must be reproducible from reviewed source Evidence under an approved rule | Semantics and NULL/UNKNOWN/CONFLICT handling remain a separate gate; this template does not define or set it | Must not imply completeness, safety, Product QA, activation, or recommendation eligibility |
| Knowledge confidence / `knowledge_confidence` | Existing confidence field | Basis and limitations must be explainable | Do not present as calibrated probability; do not derive from number of claims alone | Context only; not an approval signal |

#### 5.1.2 Shared semantic rules

1. **FACT** describes a source-bound fact, such as the exact package size.
2. **MANUFACTURER_CLAIM** records what the manufacturer says, without endorsing it.
3. **EVIDENCE** records a study or other evidence supporting or challenging a claim; identify whether it concerns the exact finished product, an ingredient, or a different formula.
4. **INFERENCE** is a bounded interpretation based on stated facts and cited support. Record its rationale and limitations.
5. **UNKNOWN** means the relevant value is explicitly not known; it is not a synonym for an empty field.
6. **CONFLICT** means relevant sources disagree. Preserve the conflicting assertions and do not silently choose one.

Use the existing claim-type vocabulary and Evidence/QA flow where supported. Do not create a second taxonomy or change enum/storage semantics as part of this documentation.

#### 5.1.3 Minimum evidence review for hydration claims

For each material claim about hydration, moisture retention, skin softness, or barrier support, record or explicitly mark unknown:

- exact product/market/version to which the claim applies;
- exact wording, source, and source date when available;
- whether the source is marketing copy, package text, ingredient-level research, instrumental testing, consumer self-assessment, or a product-specific study;
- tested population, conditions, duration, comparator, endpoint/measurement method, and numerical result when reported;
- relevant protocol/report limitations, missing information, or contradictory sources;
- whether the evidence supports only the narrow endpoint measured or a broader interpretation.

Do not transfer an ingredient study to the finished product as proof. Do not treat “contains hyaluronic acid/glycerin/ceramides” as proof of a particular hydration duration, concentration, barrier outcome, or suitability for a diagnosed condition.

#### 5.1.4 Candidate relationship to skin needs

A candidate relationship may be investigated for a precisely described need such as perceived dryness or need for moisturization only when the relevant product feature and its source are recorded. The relationship must retain:

- canonical existing need/problem identifier, if and only if a valid identifier and relationship mechanism are confirmed;
- the specific product feature and evidence reference;
- relationship basis: manufacturer claim, product-specific evidence, indirect evidence, or hypothesis;
- limitations, unresolved conflicts, and review status;
- the narrowest conclusion supported by the evidence.

No automatic P01–P61 mapping is permitted. A relationship candidate is not a diagnosis, a treatment claim, a safety clearance, or a recommendation to an individual. Suitability still depends on the person's reported needs, use context, known sensitivities, product directions, and appropriate professional judgement.

#### 5.1.5 Unknown, conflict, and acceptance behavior

- Missing size, market, variant, concentration, complete INCI, study details, or warning data must remain missing/unknown rather than be filled from a similar product.
- If two sources disagree, preserve both source-bound statements and mark the relevant fact/claim as conflicted under the existing workflow. Do not average numbers or silently prefer the newest marketing page.
- If the source only names selected ingredients, do not label the list as full INCI.
- If a product-specific study cannot be accessed, record the manufacturer-reported summary as such and note that independent protocol appraisal is incomplete.
- Smart-fill, when separately authorized in a future phase, may only create reviewable suggestions. It must not auto-verify Evidence, pass Product QA, activate a product, or make the product recommendation-eligible.

#### 5.1.6 Template-specific acceptance criteria

- [ ] Product identity fields are grounded in the exact market/version or explicitly marked unknown.
- [ ] No fabricated defaults (including 50 ml, `IR`, or a guessed variant) are presented as extracted facts.
- [ ] Full INCI and selected key ingredients are distinguishable.
- [ ] Ingredient roles are labelled as sourced fact or inference and are not treated as proof of finished-product efficacy.
- [ ] Each material hydration/moisturization claim has a traceable source and claim type.
- [ ] Evidence records identify product-specific versus ingredient-level evidence and preserve limitations.
- [ ] UNKNOWN and CONFLICT remain visible and do not enter trusted aggregate values without the approved rules.
- [ ] Candidate skin-need relationships have a specific basis and never auto-link to P01–P61.
- [ ] Existing DuplicateCheck, research-draft, Evidence QA, Product QA, and lifecycle controls remain authoritative.
- [ ] No schema/API/DB change or operational product registration is implied by completing this template specification.


### 5.2 `SUNSCREEN`
| Box ID | Label |
|---|---|
| `spf_value` | SPF |
| `pa_rating` | PA / ادعای UVA |
| `filter_type` | شیمیایی / فیزیکی / ترکیبی / نامشخص |
| `water_resistance` | مقاومت در برابر آب |
| `tint` | رنگی / بی‌رنگ / نامشخص |
| `face_body` | صورت / بدن / هر دو |

### 5.3 `BRIGHTENING_SPOT`
| Box ID | Label |
|---|---|
| `target_discoloration` | هدف اعلام‌شده |
| `actives_stated` | مواد فعال اعلام‌شده |
| `claim_timeline` | بازه زمانی ادعای سازنده |
| `claim_metrics` | اعداد ادعای سازنده فقط با منبع |

### 5.4 `MICELLAR`
| Box ID | Label |
|---|---|
| `makeup_removal` | پاک‌کنندگی آرایش: بله / خیر / نامشخص |
| `rinse_required` | نیاز به آبکشی |
| `eye_area` | مناسب اطراف چشم طبق برچسب |

### 5.5 `TONER`
| Box ID | Label |
|---|---|
| `toner_role` | نقش اعلام‌شده |
| `alcohol_stated` | الکل در فرمول اعلام شده |

### 5.6 `CLEANSING_GEL`
| Box ID | Label |
|---|---|
| `rinse_off` | آبکشی‌شونده |
| `surfactant_or_acid_focus` | تمرکز اعلام‌شده |
| `frequency_label` | تناوب مصرف طبق برچسب |

### 5.7 `ANTI_ACNE`
| Box ID | Label |
|---|---|
| `acne_focus` | تمرکز اعلام‌شده |
| `actives_stated` | مواد فعال اعلام‌شده |
| `leave_on_or_rinse` | ماندگار / آبکشی |

### 5.8 `EXFOLIANT`
| Box ID | Label |
|---|---|
| `exfoliant_type` | شیمیایی / فیزیکی / آنزیمی / نامشخص |
| `acids_or_grains_stated` | اسیدها یا ذرات اعلام‌شده |
| `frequency_label` | تناوب مصرف |
| `irritation_warning` | هشدار تحریک از برچسب |

### 5.9 `OTHER_SKIN`
| Box ID | Label |
|---|---|
| `why_other` | چرا در قالب‌های بالا جا نگرفت |
| `free_structured_notes` | یادداشت ساخت‌یافته اپراتور |

## 6. Intended operator flow (future UI target, not implemented by this document)

1. Open **مدیریت محصولات → ورود و ویرایش محصول**.
2. Use the existing intake fields and existing **تکمیل هوشمند** only as currently implemented.
3. Operator selects `product_line = SKIN`.
4. Operator selects one `skin_form_template`.
5. Future smart-fill may propose values from pasted text or package label; this step is not authorized in P0.
6. Operator reviews and edits all values; unsupported details remain blank/unknown.
7. Existing DuplicateCheck, Draft, and QA controls remain unchanged.
8. Any future Evidence draft path must preserve provenance and pending status.

## 7. Phases and authorization

| Phase | Scope | Authorization state |
|---|---|---|
| **P0** | Fixed-template specification and documentation links | Merged in PR #452; canonical document is maintained through reviewed documentation changes |
| **P1** | Template selector and empty shared/specific boxes inside the existing Product Intake UI, only under `product_line = SKIN` | Implemented and merged in PR #455; selection remains local UI state and no template values are persisted/sent |
| **P2** | Smart extraction | Not authorized by P1 |
| **P3** | Evidence mapping / research-draft creation | Not authorized by P1 |
| **P4** | Consultation bridge / problem mapping | Not authorized by P1; canonical problem links require separate rules |

No phase in this table authorizes schema/API/DB changes, product activation, QA bypass, or verified ProductKnowledge from smart-fill alone.

## 8. Acceptance checklist

- [x] Scope is restricted to `product_line = SKIN`.
- [x] Canonical location is under `docs/homepage/product-management/`.
- [x] Product Owner approved the merged hydration/moisturizer template and all nine V1 templates: [Issue #406 decision](https://github.com/vahidmaghsoudi2/hbi/issues/406#issuecomment-6389070595).
- [x] P1 is gated on P0 merge and remains limited to UI skeleton / empty boxes.
- [x] P0 documentation was merged via [PR #452](https://github.com/vahidmaghsoudi2/hbi/pull/452).
- [x] P1 UI skeleton was merged via [PR #455](https://github.com/vahidmaghsoudi2/hbi/pull/455); this does not authorize P2 smart-fill.
- [ ] Detailed field contract for `HYDRATING_MOISTURIZER` reviewed and accepted by PO.

## 9. Remaining boundaries (not unresolved template-count decisions)

- The storage representation for future template values (notes/JSON versus schema) is **not decided here** and is outside P0/P1 authorization; P1 must not add schema/API/DB.
- `stated_skin_goals` remains plain text/candidate only. No automatic linkage to P01–P61 is allowed. Any future linkage policy needs a separate explicit decision in Issue #406.
- Physical identity of each of the seven research dossiers remains separate from this template specification. No product is thereby registered as an operational record.

---

*Documentation contract only. P0 (#452) and P1 (#455) are merged. P2 smart-fill, P3 evidence mapping, and P4 consultation bridge remain unauthorized unless separately approved in Issue #406.*
