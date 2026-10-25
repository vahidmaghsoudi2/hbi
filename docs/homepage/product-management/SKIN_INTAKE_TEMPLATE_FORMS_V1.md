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



#### 5.2.1 Detailed field contract — `SUNSCREEN`

This is a **conceptual contract for review**, not a claim that each candidate field exists in Product, ProductKnowledge, Evidence, the API, or the database. The existing identity, evidence, draft, duplicate-check, and QA paths remain authoritative. Sunscreen claims are market- and test-method-dependent; a label from one jurisdiction must not be interpreted as a universal regulatory guarantee.

| Concept / candidate key | Meaning and semantic class | Source / provenance | Validation and unknown/conflict behavior | Consultation relevance |
|---|---|---|---|---|
| Brand and exact product name | Product identity fact | Exact package or manufacturer page | Preserve exact wording and version; similar name does not prove same formula | Identifies the product being assessed |
| Market / regional version | Identity and regulatory context | Package, region-specific manufacturer page, or verified SKU | Unknown remains unknown; preserve regional variants separately | Determines which claims, labels, and rules apply |
| Variant / tint / shade | Identity and version fact | Package and exact SKU | Record only a verified tint/shade/variant; do not infer from product photos alone | Tint, shade, and formula may affect use and identity |
| Size / GTIN / packaging version | Identity and package facts | Package label, barcode scan, dated packaging evidence | Never fabricate defaults; distinguish old packaging from a changed formula | Duplicate and version control |
| Full INCI / UV filters | Label fact | Full package ingredient list or exact manufacturer source for the same market/version | Distinguish full INCI from selected filters; do not infer filter concentration from ingredient order | Supports ingredient and version review, not proof of protection level |
| SPF value / `spf_value` | Labelled test-related claim | Exact package/manufacturer source, with market and version | Preserve stated value and context; never calculate SPF from ingredients or infer it from another version | Describes labelled UVB-related protection under the applicable test/label system, not every aspect of protection |
| UVA claim / `pa_rating` or equivalent | Label claim, exact scheme required | Package/manufacturer source; capture the actual notation (e.g. PA grade, UVA logo, or other regional wording) | Do not convert between schemes unless a validated rule and evidence are documented; missing UVA information stays unknown | UVA information is distinct from SPF |
| Broad-spectrum claim | Manufacturer/regulatory label claim | Exact regional label and source | Record only if explicitly stated and identify market/test scheme where available; do not infer from SPF or PA alone | Helps characterize the stated protection scope |
| Water-resistance claim / `water_resistance` | Label/test claim | Exact label and regional manufacturer source; retain stated duration/test wording | Values should distinguish not stated, not water-resistant, and a stated tested duration where the local system uses one; never translate “waterproof” marketing into validated resistance | Important for use context; does not mean protection is permanent or unaffected by towel drying |
| UV-filter type / `filter_type` | Classification/inference based on disclosed filters | Full INCI plus a reliable filter reference if classification is needed | Prefer “organic filters”, “inorganic filters”, “mixed”, or “unknown” when supported; “chemical/physical” wording may be ambiguous and must not imply safety ranking | Helps explain formulation, not determine suitability or safety by itself |
| Tint / `tint` | Identity/appearance fact | Package or manufacturer source | Values: tinted, untinted, unknown; shade-specific variants remain distinct | May affect cosmetic preference and visible-light claims only when those claims are evidenced |
| Face/body / `face_body` | Intended-use claim | Exact label or manufacturer instructions | Face, body, both, other, unknown; no inference from packaging size alone | Helps match the labelled use to the intended application area |
| Application amount and method | Manufacturer instruction | Exact package or manufacturer directions | Capture amount, coverage, application timing and reapplication frequency only as stated; no invented universal product-specific directions | Protection depends on use consistent with directions and tested conditions |
| Reapplication instruction | Manufacturer instruction / regional label direction | Exact regional label | Preserve exact instruction and context; do not replace it with a guessed interval | Relevant to practical use and maintaining labelled protection |
| Warnings / restrictions | Source-bound label facts | Exact package or regional manufacturer source | “Not stated” is not “no warning”; preserve age, eye-contact, damaged-skin, or other instructions only when present | Risk screening; not an automatic safety clearance |
| Claim about sensitive skin, acne, pregnancy, children, or non-comedogenicity | Manufacturer claim unless independently supported | Exact claim source and applicable market/version | Keep as a claim; identify the exact population or condition and the evidence basis; do not infer from “mineral” or “fragrance-free” alone | May prompt further review, but does not establish individual suitability |
| Product-specific protection study / test report | Evidence | Report, method, exact tested formula, market/version and source | Capture method/standard, sample/population where relevant, endpoint, date, limitations and access status; pending review stays pending | Helps assess a specific protection claim within the tested scope |
| Evidence about an individual filter | Ingredient-level evidence | Scientific source for that filter and the question studied | Do not treat as proof of the finished sunscreen's SPF/UVA performance, photostability, water resistance, or tolerability | Research context only |
| Evidence status / confidence | Existing Evidence and ProductKnowledge concepts | Existing review process and traceable source records | Do not create new enums or infer product QA, safety clearance, activation, or recommendation eligibility from this field | Context for reviewer, not an approval signal |
| Candidate relation to skin need | Proposed relationship concept | Specific claim/evidence plus canonical need identifier, if the existing relation path is confirmed | No automatic P01–P61 mapping; preserve basis, limitation, conflict and review state | Supports structured review, not diagnosis or guaranteed suitability |

#### 5.2.2 Sunscreen-specific evidence rules

For every material claim about SPF, UVA protection, broad-spectrum coverage, water resistance, photostability, or suitability for a particular population, record or explicitly mark unknown:

1. **Exact identity:** product, market, variant, packaging/formula version and the source to which the claim applies.
2. **Exact claim:** label wording and notation, not a paraphrase that drops qualifiers.
3. **Test basis:** method or standard when available, test date/report reference, endpoint, and whether the evidence applies to the finished product or only to an ingredient.
4. **Scope and limitations:** stated water-resistance duration where relevant, conditions tested, population or use conditions where reported, and missing protocol details.
5. **Regional context:** label conventions and claims can differ by market; retain the original notation and do not silently convert between regulatory schemes.
6. **Review state:** distinguish source capture from evidence appraisal and from formal QA.

SPF and UVA claims describe different aspects of protection. An SPF number alone must not be used to infer a particular UVA rating. A UVA mark or PA grade must not be inferred from SPF. Water resistance must not be inferred from a product being marketed as a sunscreen, and “waterproof” or “all-day protection” must not be treated as a validated test result unless the applicable source and test basis substantiate that exact claim.

The presence or absence of a particular UV filter in an ingredient list does not, by itself, establish the finished product's SPF, UVA protection, stability, water resistance, or suitability for an individual. Do not derive a protection rating from filter names, ingredient order, product category, or a similar product's testing.

#### 5.2.3 Market and terminology safeguards

- Store the original market-specific claim and notation. Any normalized value must retain a reference to the original statement and the approved conversion rule.
- Do not assume the same brand name means identical UV filters, formula, test result, label, or legal claim across regions.
- Do not treat “mineral/physical” as synonymous with safer, gentler, more effective, or suitable for sensitive skin. These are separate claims requiring their own basis.
- Do not treat “chemical/organic filter” as a safety judgement. Record filter identity and evaluate any specific safety claim separately.
- “Fragrance-free”, “non-comedogenic”, “for sensitive skin”, “reef-safe”, and similar terms remain source claims unless a defined evidence review supports a narrower conclusion. Do not silently upgrade marketing terms into verified facts.
- Do not invent universal age restrictions or pregnancy advice. Preserve label directions and escalate questions that require individualized clinical or regulatory interpretation.

#### 5.2.4 Unknown, conflict, and acceptance behavior

- Missing SPF, UVA notation, water-resistance information, full INCI, market, test method, or report details remain unknown; do not copy values from a similarly named product.
- If package and manufacturer page disagree, retain both source-bound assertions and mark the relevant claim/fact conflicted under the existing review process.
- If only selected filters are shown in a marketing summary, do not label them as a complete INCI list.
- If a manufacturer reports a test result but the full report is unavailable, record the result as manufacturer-reported and note that independent appraisal of the protocol is incomplete.
- A missing water-resistance statement must not be normalized to “not water-resistant” unless the applicable label/system and source support that conclusion.
- No smart-fill or extraction workflow may auto-verify evidence, approve Product QA, activate the product, clear a safety concern, or make a product recommendation-eligible.

#### 5.2.5 Template-specific acceptance criteria

- [ ] Exact product identity, market and variant are recorded or explicitly unknown.
- [ ] SPF is stored only as a source-bound claim for the exact product/version.
- [ ] UVA notation is captured as originally stated; no unapproved conversion between PA, UVA logo, or other schemes occurs.
- [ ] Broad-spectrum and water-resistance claims are separate from SPF and from each other.
- [ ] Water-resistance duration and wording are retained when stated; missing data is not silently interpreted as a negative claim.
- [ ] Full INCI and selected UV filters are distinguishable.
- [ ] Ingredient-level evidence is not treated as proof of finished-product protection performance.
- [ ] Test method, exact tested product/version, scope, limitations and source status are recorded or explicitly unknown.
- [ ] Market-specific labels and formulas are not merged solely because the product names match.
- [ ] Sensitive-skin, acne, pregnancy, child-use, non-comedogenicity, and similar claims are not automatically verified.
- [ ] Candidate skin-need relationships have a specific evidence basis and never auto-link to P01–P61.
- [ ] Existing DuplicateCheck, research-draft, Evidence QA, Product QA, and lifecycle controls remain authoritative.
- [ ] This specification does not authorize schema/API/DB changes, smart-fill, product registration, QA approval, activation, or recommendation behavior.


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


#### 5.3.1 Detailed field contract — `BRIGHTENING_SPOT`

This subsection is a **conceptual contract for audit and PO review**, not a declaration that every candidate key exists in Product, ProductKnowledge, Evidence, DTO, API, or database storage. It reuses the existing identity, ProductKnowledge, Evidence, research-draft, duplicate-check, and QA contracts. “Brightening”, “dark spot”, and similar labels describe intended positioning or claims; they do not establish a diagnosis, cause of discoloration, proven efficacy, or suitability for an individual.

| Concept / candidate key | Meaning and semantic class | Source / provenance requirement | Validation and UNKNOWN/CONFLICT behavior | Consultation relevance |
|---|---|---|---|---|
| Brand and exact product name | Product identity fact | Exact package or manufacturer source tied to the specific product | Preserve exact wording and version; similar names do not establish identity | Prevents transferring claims between products |
| Market / regional version | Identity and claim-context fact | Package, region-specific manufacturer page, or verified SKU source | Unknown remains unknown; do not merge regional formulas or label conventions | Formula, ingredient disclosure, and permitted claims may vary by market |
| Variant, shade, or formula version | Identity/version fact | Exact package, SKU, or manufacturer source | Do not infer from a product-family name or image alone; preserve conflicts | Distinguishes formula and shade variants |
| Size, GTIN, packaging version | Package identity facts | Package label, barcode, dated package image, or exact source | Never invent defaults; distinguish packaging change from formula change only when evidence supports it | Duplicate and version control |
| Full INCI | Label fact | Complete ingredient list for the same market/version from package or exact manufacturer source | Mark partial lists as partial; do not reconstruct missing ingredients from retailers or sibling products | Enables ingredient-level research, not proof of finished-product results |
| Selected active ingredients / `actives_stated` | Source-reported ingredient subset; may be marketing terminology | Exact label or manufacturer source; retain the source's own terminology | Do not assume every highlighted ingredient is pharmacologically active at an effective concentration; no concentration inference | Helps prioritize review of the exact disclosed formula |
| Ingredient concentration / strength | Quantitative formula fact, only if explicitly disclosed | Exact source for the exact product/version | Leave unknown when not disclosed; ingredient order is not a reliable numeric concentration; never infer percentages from marketing copy | May materially affect interpretation but must not be guessed |
| Target discoloration / `target_discoloration` | Manufacturer claim or operator-entered candidate | Exact source wording; distinguish terms such as dark spots, post-acne marks, uneven tone, melasma, or general radiance | Preserve the stated scope; do not turn a broad “brightening” claim into a claim for a specific condition | Candidate for later review only, not diagnosis or automatic problem linkage |
| Brightening / spot-reduction claim | Manufacturer claim | Exact package/manufacturer wording, market/version, source date where available | Keep the claim separate from verified outcome; do not rewrite “radiance” as “treats hyperpigmentation” | Requires claim-specific evidence review |
| Claim timeline / `claim_timeline` | Quantitative or time-bound manufacturer claim | Exact claim source and conditions, if stated | Capture stated duration verbatim and units; no default timeline; do not imply guaranteed results | Sets the scope of the claim that evidence would need to test |
| Claim metrics / `claim_metrics` | Quantitative manufacturer claim | Exact source, units, endpoint, population, duration, comparator and method where reported | Preserve numerator/denominator, percentage versus percentage points, baseline and qualifier when available; unknown details stay unknown | Prevents vague percentages from being treated as comparable clinical outcomes |
| Skin type / sensitivity / tolerability claim | Manufacturer claim or separately labelled evidence-based assessment | Exact product claim and source; tolerability evidence must identify population and method | “For sensitive skin”, “gentle”, “non-irritating” and similar wording are not universal safety facts; absence of a claim is not evidence of unsuitability | May prompt additional review but cannot guarantee individual tolerance |
| Use directions and application area | Manufacturer instruction | Exact label or manufacturer source for the same version | Preserve frequency, amount, leave-on/rinse-off status, application area, layering advice, and day/night instruction only when stated | Prevents invented directions; routine compatibility requires separate consideration |
| Sun-exposure / sunscreen instruction | Source-bound instruction or separately supported safety context | Exact label and applicable regional guidance; distinguish product label from external guidance | Do not invent product-specific SPF or reapplication advice; do not assume every brightening product has identical sun-related restrictions | Important where a product's label or evidence makes sun exposure relevant |
| Warnings, contraindications, and use restrictions | Label fact and/or separately reviewed limitation | Exact package/manufacturer source; independent medical limitations require their own credible evidence | “Not stated” is not “none”; preserve age, pregnancy, irritation, damaged-skin, eye-area, or other warnings only when supported; do not create blanket contraindications | Supports risk review, not automatic safety clearance |
| Finished-product efficacy study | Product-specific evidence | Accessible study/report or exact source summary tied to tested product, market/version and claim | Capture design, population, comparator, duration, endpoint, measurement method, result, uncertainty, conflicts and access limitations; manufacturer summary remains manufacturer-reported if the report is unavailable | Determines only the narrow outcome and population supported by the study |
| Ingredient-level evidence | Evidence about a named ingredient and specific question | Scientific source, ingredient identity/form, concentration/context if known, population/model, endpoint and limitations | Do not treat mechanistic, in-vitro, or ingredient studies as proof that the finished product reduces spots; do not transfer evidence across unverified formulations | Research context, not a product-level efficacy verdict |
| Before/after imagery or consumer review | Anecdotal or promotional material | Source, date, context, consent/access limitations where relevant, and whether image conditions are comparable | Not equivalent to a controlled study; do not infer causation, percentage efficacy, or a guaranteed result from images or testimonials | Low-strength context only unless an approved evidence rubric says otherwise |
| Evidence record / existing `Evidence` | Claim-evidence assertion and review state | Reuse existing source type/reference, claim, field, claim type, market, dates and QA fields where available | Keep source capture, evidence appraisal, conflict status, and QA distinct; no auto-verification | Lets reviewers trace why a specific claim is or is not supported |
| Evidence strength | Review assessment under the existing vocabulary | Follow the currently approved Evidence vocabulary and review process | Do not create a new strength scale or equate source type with evidence strength | Qualifies support for a specific claim, not the whole product |
| Product-level `evidence_status` | Aggregate status only if its semantics and derivation are approved | Must be reproducible from reviewed source evidence under a separately approved rule | This template neither defines nor sets the field; preserve unresolved UNKNOWN/CONFLICT semantics and existing implementation gap | Must not imply Product QA, safety clearance, activation, or recommendation eligibility |
| `knowledge_confidence` | Existing confidence concept | Basis, evidence scope and limitations must be explainable | Do not present as a calibrated probability or derive from the number of claims alone | Reviewer context only, never an approval signal |
| Candidate relationship to a skin need | Proposed relationship concept | Specific claim/evidence plus confirmed canonical need identifier and authorized relationship mechanism | Keep candidate text separate from canonical links; no automatic P01–P61 mapping | Search/research lead, not diagnosis or individualized recommendation |

#### 5.3.2 Claim and evidence boundaries for brightening products

For every material claim about reducing visible discoloration, dark spots, post-acne marks, uneven tone, radiance, or time to result, capture or explicitly mark unknown:

1. **Exact claim:** the source's wording, the particular outcome claimed, units and qualifiers.
2. **Exact product:** brand, product, market, variant, formula/packaging version, and whether evidence concerns the finished product or an ingredient.
3. **Evidence type:** marketing copy, package claim, consumer perception, before/after material, mechanistic/ingredient research, instrumental measurement, controlled clinical study, or other source.
4. **Study context:** population and relevant baseline characteristics when reported, study design, sample size, duration, comparator, endpoint, measurement method, numerical result and uncertainty.
5. **Claim-to-result fit:** whether the study measured the same outcome and timeline that the marketing claim states. “Improved radiance” does not by itself establish reduced melasma, post-inflammatory hyperpigmentation, or another specific condition.
6. **Limitations and conflicts:** missing protocol/report, small or unrepresentative population, uncontrolled image conditions, self-report, co-interventions, contradictory findings, or unavailable full text.
7. **Review state:** distinguish source capture from evidence appraisal and formal QA.

A plausible mechanism or the presence of an ingredient is not proof that the finished formula produces a particular result. Ingredient identity alone does not establish concentration, bioavailability, formulation stability, clinical effect, or tolerability. Do not infer treatment of a diagnosed pigmentary condition from generic brightening language.

#### 5.3.3 Ingredient and terminology safeguards

- Keep the full INCI, selected highlighted ingredients, manufacturer-described “actives”, and independently interpreted ingredient roles separate.
- Do not infer percentages from ingredient order, product name, marketing emphasis, or a similar formula.
- Preserve the manufacturer's exact terminology. If a source calls an ingredient an “active”, record that as source language rather than silently endorsing a pharmacological classification.
- Claims such as “brightening”, “spot corrector”, “radiance”, “even tone”, “clinical”, “dermatologist tested”, “natural”, or “gentle” must retain their exact scope and source. None is self-validating evidence of efficacy or safety.
- Do not assume that all discoloration has the same cause or that one cosmetic product is appropriate for every type of pigmentation or every skin tone.
- Do not invent medical advice, contraindications, pregnancy guidance, or a sunscreen regimen. Preserve the actual label and keep external clinical guidance separately sourced and scoped.
- A product's evidence for one endpoint, population, or duration must not be generalized to another endpoint, population, or duration without an explicit evidence-based rationale.

#### 5.3.4 UNKNOWN, CONFLICT, and acceptance behavior

- Missing market/version, full INCI, ingredient concentration, exact claim, timeline, metric denominator, study method, population, or warnings remain unknown; do not fill them from a similarly named product.
- If package, manufacturer page, retailer page, or study summary disagree, preserve each source-bound assertion and flag the relevant fact/claim as conflicted under the existing workflow. Do not silently choose the most favorable claim.
- If a source says only “brightening” or “radiance”, do not normalize it into a condition-specific treatment claim.
- If a percentage or timeline is stated without its endpoint, population, or measurement basis, preserve the wording and mark the missing context rather than treating it as a comparable clinical result.
- If only a study abstract or manufacturer summary is available, state that the full protocol/report could not be appraised; do not describe the evidence review as complete.
- Testimonials, retail star ratings, and uncontrolled before/after images must not be promoted to controlled product-specific evidence.
- Smart-fill, if separately authorized in a future phase, may propose source-linked values for human review only. It must not auto-verify Evidence, pass Product QA, activate a product, clear a safety concern, or make a product recommendation-eligible.

#### 5.3.5 Template-specific acceptance criteria

- [ ] Exact product identity, market, variant, and version are recorded or explicitly unknown.
- [ ] Full INCI is distinguished from selected key ingredients and manufacturer-highlighted “actives”.
- [ ] Ingredient concentration is recorded only when the exact source states it.
- [ ] The target discoloration and intended outcome preserve the source's exact scope; broad brightening language is not converted into a diagnosis-specific claim.
- [ ] Every quantitative or time-bound claim retains source wording, units, timeline, endpoint and reported context, with missing elements marked unknown.
- [ ] Finished-product studies are distinguished from ingredient-level, mechanistic, testimonial, and before/after evidence.
- [ ] Study design, population, comparator, duration, endpoint, measurement method, result and limitations are captured where reported.
- [ ] UNKNOWN and CONFLICT remain visible and are not silently converted into trusted values.
- [ ] Warnings and usage directions are source-bound; “not stated” is not interpreted as “none”.
- [ ] Candidate skin-need relationships include a specific basis and never auto-link to P01–P61.
- [ ] Existing DuplicateCheck, research-draft, Evidence QA, Product QA, and lifecycle controls remain authoritative.
- [ ] Completing this specification does not authorize schema/API/DB changes, smart-fill, evidence verification, product registration, QA approval, activation, or recommendation behavior.


#### 5.4.1 Detailed field contract — `MICELLAR`

This is a conceptual contract for review, not a claim that every candidate attribute exists in Product, ProductKnowledge, Evidence, DTO, API, or database storage. Use the existing identity, source provenance, research-draft, Evidence, DuplicateCheck, and QA workflows. Micellar water is a product format, not proof of suitability for every skin type or every eye area.

| Concept / candidate key | Meaning and semantic class | Source / provenance requirement | Validation and UNKNOWN/CONFLICT behavior | Consultation relevance |
|---|---|---|---|---|
| Exact product identity, market, variant, and version | Product/package identity facts | Exact package or manufacturer source for the specific regional SKU | Similar names, bottle designs, and retailer listings do not prove identical formula; unknown remains unknown | Prevents transferring ingredient and tolerability claims across versions |
| Size, GTIN, packaging version | Package identity facts | Package label, barcode, dated package image, or exact SKU source | Never fabricate defaults; distinguish packaging refresh from formula change only when evidence supports it | Duplicate and version control |
| Full INCI | Label fact about the formula | Complete package ingredient list or exact manufacturer source for the same market/version | Mark partial lists as partial; do not reconstruct from a sibling product; preserve source conflicts | Supports ingredient review, not finished-product performance claims |
| Key ingredients / `key_ingredients` | Source-reported subset | Exact package/manufacturer source | Keep distinct from full INCI; do not infer concentration or function solely from marketing emphasis | Research prioritization only |
| Makeup-removal claim / `makeup_removal` | Manufacturer claim or documented test result | Exact label/manufacturer wording; product-specific test if efficacy is asserted | Distinguish face makeup, long-wear makeup, and water-resistant makeup only where source specifies; do not infer universal removal ability from “micellar” | Helps characterize the stated cleansing purpose |
| Cleansing performance | Manufacturer claim or product-specific evidence | Exact claim source; any study/test tied to the exact product and stated soil/makeup type | Ingredient mechanism or product category alone does not prove removal efficiency; missing method and endpoint remain unknown | Evidence must match the type of material and outcome claimed |
| Rinse requirement / `rinse_required` | Label instruction | Exact product label or manufacturer directions for the same version | Values distinguish explicitly rinse, explicitly no-rinse, and not stated; do not infer from category or retailer routine advice | Avoids contradicting product-specific instructions |
| Eye-area use / `eye_area` | Label claim/instruction | Exact package/manufacturer source, including any stated restrictions | Record “suitable for eye area” only when stated; absence of a warning does not prove eye-area suitability; preserve contact-lens or irritation cautions only when sourced | Relevant to use-area review, not a guarantee against irritation |
| Face/lip/eye or other application areas | Label instruction | Exact directions and warnings | Record only stated areas; do not extend face-use directions to lips or eyes by analogy | Keeps intended use precise |
| Skin-type and sensitivity claims | Manufacturer claim or separately labelled evidence assessment | Exact source; product-specific tolerability evidence where claimed | “Sensitive skin”, “gentle”, “hypoallergenic”, or “non-irritating” are not universal guarantees; absence of claim is not evidence of unsuitability | Prompts review, does not guarantee individual tolerance |
| Fragrance, alcohol, and other ingredient presence | Formula fact based on INCI | Full INCI for exact version; use careful ingredient identity matching | Do not claim “alcohol-free”, “fragrance-free”, or absence of an ingredient from a partial list; distinguish ingredient names and chemical classes accurately | May inform user-specific review, but presence alone does not establish irritation |
| Post-use instructions and frequency | Label instruction | Exact product directions | Capture frequency, amount, cotton-pad/application method, rinse/leave-on, and follow-up cleansing only if stated; no invented routine | Maintains label fidelity |
| Warnings and restrictions | Label fact and/or separately sourced limitation | Exact label/manufacturer source; independent guidance needs its own credible source | “Not stated” is not “none”; do not invent contraindications or blanket safety claims | Risk screening only; not formal safety clearance |
| Finished-product evidence | Product-specific evidence | Study/report tied to exact formula/version and the claim being evaluated | Capture design, test conditions, sample/population, comparator, endpoint, method, results and limitations when available; manufacturer summary remains attributed if full report unavailable | Supports only the measured cleansing/tolerability outcome |
| Ingredient-level evidence | Evidence about a named ingredient or mechanism | Reliable technical/scientific source, with ingredient form and context where relevant | Do not treat ingredient evidence as proof of finished-product makeup removal, eye safety, or tolerability | Research context only |
| Evidence record / existing `Evidence` | Claim-evidence assertion and review state | Reuse current source type/reference, claim, field, claim type, market and date fields where available | Keep source capture, appraisal, conflict status, and QA separate; no auto-verification | Allows review of each material claim |
| Product-level `evidence_status` | Aggregate status only if separately approved | Must follow approved semantics and a reproducible derivation rule | This template does not define or set it; preserve unresolved UNKNOWN/CONFLICT semantics and known implementation gaps | Must not imply Product QA, safety clearance, activation, or recommendation eligibility |
| Candidate relationship to a skin need | Proposed relationship concept | Specific product feature, evidence/claim reference, confirmed canonical need identifier, and authorized relationship mechanism | Free-text goals remain candidates; no automatic P01–P61 mapping | Research lead only, not diagnosis or individualized recommendation |

#### 5.4.2 Claim and evidence boundaries for micellar water

For material claims about makeup removal, cleansing, residue, eye-area use, or skin tolerability, record or explicitly mark unknown:

1. The exact claim wording and the exact product/market/version.
2. The type of material tested or claimed to be removed, such as ordinary makeup versus long-wear or water-resistant makeup, when stated.
3. Whether the source is package wording, manufacturer marketing, a product-specific test, ingredient-level research, consumer feedback, or an independent study.
4. Test conditions and method, sample/population, comparator, endpoint, and results where reported.
5. Whether the evidence matches the exact use claim. A general cleansing test does not automatically establish eye-area suitability or performance on every makeup type.
6. Relevant limitations, missing protocol details, contradictory sources, and the current review state.

The word “micellar” does not itself establish rinse-free use, complete makeup removal, hypoallergenicity, non-comedogenicity, or suitability for sensitive skin. Do not turn a product category or an ingredient mechanism into a verified finished-product outcome.

#### 5.4.3 Ingredient and terminology safeguards

- Keep full INCI, selected key ingredients, manufacturer-highlighted ingredients, and independently interpreted ingredient roles separate.
- Do not infer concentration, formula completeness, or ingredient absence from a partial list or product-family page.
- Record “rinse-free”, “eye-safe”, “sensitive skin”, “hypoallergenic”, “fragrance-free”, and “non-comedogenic” only with exact source wording and scope; none is self-validating proof of universal suitability.
- Do not treat “contains micelles” or the presence of a surfactant as proof of a specific makeup-removal result or low irritation.
- Do not invent application frequency, whether a second cleanse is required, or instructions for contact-lens users. Preserve actual label directions and keep external guidance separately sourced.
- Individual tolerance may vary; a marketing claim does not guarantee absence of irritation or allergic reaction.

#### 5.4.4 UNKNOWN, CONFLICT, and acceptance behavior

- Missing market/version, full INCI, rinse requirement, application area, makeup type, test method, performance result, or warning data remains unknown rather than being filled from a similar product.
- If package, manufacturer, retailer, and research sources disagree, preserve each source-bound assertion and flag the relevant item as conflicted under the existing workflow.
- “Not stated” must remain distinct from “no”, “not required”, “fragrance-free”, “alcohol-free”, or “safe for eyes”.
- If only selected ingredients are published, do not label them full INCI.
- If only a marketing summary is accessible, attribute it to the manufacturer and note that the underlying test could not be appraised.
- Testimonials and uncontrolled demonstrations must not be promoted to controlled product-specific evidence.
- Any future smart-fill, if separately authorized, may create only source-linked suggestions for human review. It must not auto-verify Evidence, pass Product QA, activate a product, clear a safety concern, or make the product recommendation-eligible.

#### 5.4.5 Template-specific acceptance criteria

- [ ] Exact product identity, market, variant, and version are recorded or explicitly unknown.
- [ ] Full INCI is distinguished from selected key ingredients.
- [ ] Makeup-removal claims preserve the exact makeup type and scope stated by the source.
- [ ] Rinse requirement and application areas come from the exact label/manufacturer source; unknown remains distinct from no.
- [ ] Eye-area and sensitive-skin claims are not treated as universal safety guarantees.
- [ ] Ingredient presence is not used alone to prove performance, non-irritation, or finished-product efficacy.
- [ ] Evidence distinguishes finished-product testing from ingredient-level evidence, marketing, and testimonials.
- [ ] Study/test methods, conditions, endpoints, results, and limitations are captured where reported.
- [ ] UNKNOWN and CONFLICT remain visible and are not silently converted into trusted values.
- [ ] Warnings and usage directions remain source-bound; “not stated” is not “none”.
- [ ] Candidate skin-need relationships never auto-link to P01–P61.
- [ ] Existing DuplicateCheck, research-draft, Evidence QA, Product QA, and lifecycle controls remain authoritative.
- [ ] This documentation does not authorize schema/API/DB changes, smart-fill, evidence verification, operational product registration, QA approval, activation, or recommendation behavior.



#### 5.5.1 Detailed field contract — `TONER`

This is a conceptual contract for review, not a declaration that every candidate field exists in Product, ProductKnowledge, DTO, API, or database storage. Use the existing product identity, source provenance, research-draft, Evidence, DuplicateCheck, and QA workflows. “Toner” is a product-category label and does not, by itself, establish exfoliating action, hydration, acne treatment, or suitability for a particular skin type.

| Concept / candidate key | Meaning and semantic class | Source / provenance requirement | Validation and UNKNOWN/CONFLICT behavior | Consultation relevance |
|---|---|---|---|---|
| Exact product identity, market, variant, formula/version | Product identity facts | Exact package or manufacturer source for the specific regional SKU | Similar names and packaging do not prove identical formulas; unknown remains unknown | Prevents transferring ingredient and claim evidence across versions |
| Size, GTIN, packaging version | Package identity facts | Package label, barcode, dated package image, or exact SKU source | No fabricated defaults; distinguish a packaging refresh from a formula change only when evidence supports it | Duplicate and version control |
| Full INCI | Label fact about the formula | Complete package INCI or exact manufacturer source for the same market/version | Partial lists must be labelled partial; do not reconstruct from a sibling product | Supports ingredient review, not proof of efficacy |
| Key ingredients / `key_ingredients` | Source-reported subset | Exact package/manufacturer source | Keep separate from full INCI and manufacturer-highlighted “actives”; do not infer concentration | Research prioritization only |
| Toner format and texture | Product descriptor or manufacturer claim | Exact source; label direct observation separately from marketing | Do not infer liquid, essence, mist, or pad format from category alone; unknown is allowed | Describes form of use, not suitability |
| Intended function / `stated_skin_goals` | Manufacturer claim or free-text candidate | Exact claim and source reference | Preserve wording such as hydrating, soothing, balancing, or exfoliating; do not silently turn a broad claim into a verified outcome | Search/research lead, not automatic recommendation |
| Exfoliating ingredients or action | Ingredient fact and/or product claim, depending on source | Full INCI plus exact product claim; concentration, pH, and test context only if actually sourced | Do not infer exfoliating strength, concentration, pH, or frequency from ingredient presence or product name | May materially affect tolerance and use context |
| Hydration/soothing claims | Manufacturer claim or product-specific evidence | Exact source and, for efficacy conclusions, evidence matched to the exact product/version and endpoint | Ingredient mechanism is not proof of finished-product performance; preserve missing endpoint or study context | Candidate relevance only |
| Alcohol, fragrance, essential oils, acids, and other ingredient presence | Formula fact based on INCI | Full INCI for the exact version | Do not declare presence or absence from a partial list; distinguish ingredient identity from assumptions about irritation | May inform a specific user's review, but presence alone does not prove harm or safety |
| Skin-type/sensitivity claims | Manufacturer claim or separately labelled evidence assessment | Exact source; product-specific tolerability evidence where claimed | “Sensitive skin”, “gentle”, “hypoallergenic”, and “non-irritating” are not universal guarantees | Prompts review; does not guarantee individual tolerance |
| Application area and method | Label instruction | Exact product directions | Record face/body, hands, cotton pad, hands-only application, misting, and avoidance areas only where stated | Prevents invented instructions |
| Frequency, layering, rinse/leave-on | Label instruction | Exact product directions for the same version | Distinguish explicitly stated instructions from not stated; do not invent daily use or layering order | Instruction fidelity and tolerance review |
| Warnings and restrictions | Label fact and/or separately sourced limitation | Exact label/manufacturer source; external guidance needs its own credible source | “Not stated” is not “none”; preserve conflicting sources | Risk screening only, not safety clearance |
| Finished-product evidence | Evidence about the exact product/version | Study or test tied to the finished formula and the specific claim | Capture design, population, comparator, duration, endpoint, method, result, and limitations where reported | Supports only the outcome actually measured |
| Ingredient-level evidence | Evidence about a named ingredient or mechanism | Reliable scientific/technical source with ingredient form and context where relevant | Do not treat it as proof of finished-product efficacy, tolerability, or suitability | Research context only |
| Existing Evidence record and review status | Claim-evidence assertion and review state | Reuse existing source type/reference, claim, field, claim type, market, dates, conflict, and QA fields where available | Source capture, appraisal, conflict, and QA remain distinct; no auto-verification | Makes each material claim traceable |
| Product-level `evidence_status` | Aggregate status only if separately approved | Must follow approved semantics and a reproducible derivation rule | This template neither defines nor sets it; retain the known implementation gap and unresolved UNKNOWN/CONFLICT semantics | Must not imply Product QA, safety clearance, activation, or recommendation eligibility |
| Candidate relationship to a skin need | Proposed relationship concept | Specific feature/claim, evidence reference, confirmed canonical need identifier, and authorized relationship mechanism | Keep free-text goals separate; no automatic P01–P61 mapping | Research lead only, not diagnosis or individualized recommendation |

#### 5.5.2 Claim and evidence boundaries for toner

For material claims about hydration, soothing, oil control, pore appearance, exfoliation, redness, or acne-related outcomes, record or explicitly mark unknown:

1. Exact claim wording, intended endpoint, source, market, and formula/version.
2. Whether the statement is package text, manufacturer marketing, ingredient-level research, consumer feedback, instrumental testing, or a product-specific study.
3. For studies/tests, the population or test material, design, duration, comparator, endpoint, measurement method, numerical result, and limitations where reported.
4. Whether the measured endpoint actually matches the claim. A change in surface oil or skin feel does not automatically establish treatment of acne, reduced pore size, or improvement in a diagnosed condition.
5. For exfoliating claims, the exact source basis for the ingredient/action and any reported concentration, pH, frequency, or test conditions. Missing values stay unknown.
6. Conflicting statements, unavailable full reports, and the current review state.

The category name “toner” does not establish that a product is alcohol-based, alcohol-free, exfoliating, hydrating, pH-balancing, acne-treating, or safe for all skin types. Ingredient presence alone does not prove the finished formula's outcome.

#### 5.5.3 Ingredient and terminology safeguards

- Keep full INCI, selected key ingredients, manufacturer-highlighted ingredients, and independently interpreted ingredient roles distinct.
- Do not infer percentages, pH, exfoliation strength, or ingredient absence from ingredient order, marketing emphasis, or a similar product.
- Preserve the source's exact terms, including “pore minimizing”, “balancing”, “clarifying”, “soothing”, “alcohol-free”, and “for sensitive skin”; none is self-validating proof of efficacy or universal tolerance.
- Do not equate the presence of an acid or other potentially active ingredient with a verified exfoliating effect or a particular safe frequency.
- Do not invent application frequency, layering order, rinse instructions, contraindications, or pregnancy-related guidance. Transcribe the label and source external guidance separately when legitimately needed.
- A product-specific study, ingredient study, marketing claim, and user anecdote must not be represented as interchangeable evidence classes.

#### 5.5.4 UNKNOWN, CONFLICT, and acceptance behavior

- Missing market/version, complete INCI, concentration, pH, exact claim, application method, frequency, endpoint, test method, or warning data remains unknown; do not fill it from a similar product.
- If package, manufacturer, retailer, or research sources disagree, preserve each source-bound assertion and mark the relevant item conflicted under the existing workflow.
- “Not stated” must remain distinct from “no”, “alcohol-free”, “non-exfoliating”, “safe for sensitive skin”, or “use daily”.
- If only selected ingredients are published, do not label them full INCI.
- If only a manufacturer summary is accessible, attribute it to the manufacturer and note that the underlying protocol/report could not be appraised.
- Any future smart-fill, if separately authorized, may propose source-linked values for human review only. It must not auto-verify Evidence, pass Product QA, activate a product, clear a safety concern, or make the product recommendation-eligible.

#### 5.5.5 Template-specific acceptance criteria

- [ ] Exact product identity, market, variant, and version are recorded or explicitly unknown.
- [ ] Full INCI is distinguished from selected key ingredients and manufacturer-highlighted ingredients.
- [ ] Toner format and intended function are source-bound and not inferred from the category name.
- [ ] Exfoliating, hydrating, soothing, oil-control, and other material claims preserve exact scope and evidence type.
- [ ] Concentration, pH, strength, frequency, and other quantitative details are recorded only when supported by an exact source.
- [ ] Finished-product evidence is distinguished from ingredient-level research, marketing, and testimonials.
- [ ] Usage directions, application areas, and warnings are transcribed from the exact version; “not stated” is not “none”.
- [ ] UNKNOWN and CONFLICT remain visible and are not silently converted into trusted values.
- [ ] Candidate skin-need relationships have a specific basis and never auto-link to P01–P61.
- [ ] Existing DuplicateCheck, research-draft, Evidence QA, Product QA, and lifecycle controls remain authoritative.
- [ ] This documentation does not authorize schema/API/DB changes, smart-fill, evidence verification, operational product registration, QA approval, activation, or recommendation behavior.


#### 5.6.1 Detailed field contract — `CLEANSING_GEL`

This is a conceptual V1 contract for review, not a claim that every candidate field exists in Product, ProductKnowledge, DTO, API, or database storage. Existing identity, source provenance, research-draft, Evidence, DuplicateCheck, and QA workflows remain authoritative. “Cleansing gel” describes a product format; it does not by itself establish pH, surfactant mildness, acne treatment, non-comedogenicity, or suitability for every skin type.

| Concept / candidate key | Meaning and semantic class | Source / provenance requirement | Validation and UNKNOWN/CONFLICT behavior | Consultation relevance |
|---|---|---|---|---|
| Exact product identity, market, variant, formula/version | Product identity facts | Exact package or manufacturer source for the regional SKU | Similar names, packaging, or product-family pages do not prove identical formulas; unknown remains unknown | Prevents transferring formula or tolerability evidence across versions |
| Size, GTIN, packaging version | Package identity facts | Package label, barcode, dated package image, or exact SKU source | No fabricated defaults; do not infer formula change or continuity from packaging alone | Duplicate and version control |
| Full INCI | Label fact about the formula | Complete package ingredient list or exact manufacturer source for the same market/version | Partial lists must be labelled partial; do not reconstruct from a sibling product | Ingredient review, not proof of finished-product performance |
| Key ingredients / `key_ingredients` | Source-reported subset | Exact package/manufacturer source | Keep separate from full INCI and highlighted marketing ingredients; do not infer concentration | Research prioritization only |
| Product format and texture | Product descriptor or manufacturer claim | Exact source; distinguish label description from operator observation | Do not infer gel consistency or use method from the name alone | Describes form, not clinical suitability |
| Cleansing purpose / `stated_skin_goals` | Manufacturer claim or free-text candidate | Exact source wording and source reference | Preserve claims such as removing dirt, oil, sunscreen, or makeup separately; do not assume every claim applies | Search/research lead only |
| Cleansing performance | Manufacturer claim or product-specific evidence | Exact claim source; any test tied to exact product/version and target material | Do not infer removal of long-wear or water-resistant makeup from a generic cleansing claim; method and endpoint remain unknown if unstated | Helps characterize the specific cleansing claim |
| Surfactant and cleanser ingredient interpretation | Formula fact plus separately labelled scientific interpretation | Full INCI and reliable ingredient reference where role interpretation is needed | Do not infer surfactant concentration, blend mildness, or whole-formula irritation risk from ingredient names/order alone | Context for review, not a stand-alone suitability verdict |
| pH / `ph_value` candidate | Measured product attribute, if available | Reliable measurement or exact manufacturer technical source tied to the product/version | Do not infer pH from “gentle”, “balanced”, ingredient list, or category; record method/date when known; unknown is allowed | May inform formulation context, but pH alone does not prove mildness |
| Skin-type and sensitivity claims | Manufacturer claim or separately labelled evidence assessment | Exact source; product-specific tolerability evidence for substantiated outcome claims | “For oily skin”, “sensitive skin”, “gentle”, or “non-irritating” is not a universal guarantee | Prompts context-sensitive review, not an individual safety guarantee |
| Acne, pore, oil-control, or anti-bacterial claims | Manufacturer claim or product-specific evidence | Exact wording, source, market/version, and relevant product-specific evidence | Do not convert “deep clean” or oil removal into acne treatment; do not infer antimicrobial effect from an ingredient alone | Claims need endpoint-specific review; no diagnosis |
| Fragrance, essential oils, alcohols, and other ingredient presence | Formula fact based on INCI | Full INCI for the exact version | Do not claim presence/absence from a partial list; distinguish ingredient identity from assumptions about harm or benefit | May inform a user's known sensitivities but is not proof of reaction |
| Application area / `face_body` candidate | Label instruction | Exact package/manufacturer directions | Face, body, eye-area, or other use must be explicitly supported; do not extend directions by analogy | Avoids incorrect use assumptions |
| Amount, frequency, water/rinse directions | Label instruction | Exact directions for the same version | Preserve stated amount, frequency, wet/dry-skin instructions, rinse requirements, and contact time only when given; “not stated” remains distinct | Instruction fidelity |
| Warnings and restrictions | Label fact and/or separately sourced limitation | Exact label/manufacturer source; independent guidance requires its own source | “Not stated” is not “none”; preserve conflicting sources | Risk screening only, not safety clearance |
| Finished-product evidence | Evidence about exact product/version | Study or test tied to the finished formula and specific claim | Capture design, population/test material, comparator, duration, endpoint, method, result, and limitations where reported | Supports only the outcome actually measured |
| Ingredient-level evidence | Evidence about a named ingredient or mechanism | Reliable scientific/technical source and relevant ingredient context | Do not treat it as proof of whole-formula cleansing, mildness, acne benefit, or tolerability | Research context only |
| Existing Evidence record and review state | Claim-evidence assertion and review state | Reuse existing source type/reference, claim, field, claim type, market, dates, conflict, and QA fields where available | Source capture, appraisal, conflict, and QA remain distinct; no auto-verification | Makes claims traceable |
| Product-level `evidence_status` | Aggregate status only if separately approved | Approved semantics and reproducible derivation rule required | This template neither defines nor sets it; preserve unresolved UNKNOWN/CONFLICT semantics and the known implementation gap | Must not imply Product QA, safety clearance, activation, or recommendation eligibility |
| Candidate relationship to a skin need | Proposed relationship concept | Specific product feature/claim, evidence reference, confirmed canonical need identifier, and authorized relationship mechanism | Keep free-text goals separate; no automatic P01–P61 mapping | Research lead only, not diagnosis or individualized recommendation |

#### 5.6.2 Claim and evidence boundaries for cleansing gels

For material claims about cleansing, oil removal, sunscreen or makeup removal, pore appearance, acne, barrier effects, or tolerability, record or explicitly mark unknown:

1. Exact claim wording, intended endpoint, source, market, and formula/version.
2. The material or outcome actually addressed: ordinary dirt, sebum, sunscreen, makeup, water-resistant makeup, acne lesions, or another stated endpoint. Do not collapse them into one “cleansing” result.
3. Whether the source is package text, manufacturer marketing, ingredient-level research, consumer feedback, instrumental testing, or a product-specific study.
4. For studies/tests, design, test material/population, duration, comparator, endpoint, measurement method, results, and limitations where reported.
5. Whether the evidence matches the scope of the claim. Removal of surface oil does not establish acne treatment; a cleanser ingredient study does not establish the performance or mildness of the finished formula.
6. For pH or mildness claims, the exact measurement/test basis if available. “pH-balanced” or “gentle” alone is not a complete method or clinical result.
7. Missing protocol details, conflicting sources, and the current review state.

The product label “cleansing gel” does not prove a particular pH, surfactant system, low irritation, non-comedogenicity, barrier preservation, or suitability for a diagnosed skin condition. Rinse-off status also does not eliminate the possibility of irritation or allergy.

#### 5.6.3 Ingredient and terminology safeguards

- Keep full INCI, selected key ingredients, manufacturer-highlighted ingredients, and independently interpreted ingredient roles separate.
- Do not infer concentrations, pH, cleanser strength, or ingredient absence from ingredient order, product name, or a similar formula.
- Preserve exact claims such as “deep cleansing”, “pore cleansing”, “oil control”, “soap-free”, “sulfate-free”, “pH-balanced”, “non-comedogenic”, and “for sensitive skin”; none is self-validating proof of outcome or universal suitability.
- Do not assume that a named surfactant or ingredient makes the whole formula either harsh or gentle. The finished formula, use conditions, and evidence matter.
- Do not infer that an acne-marketed cleanser treats acne, or that cleansing claims imply antibacterial action.
- Do not invent frequency, contact time, double-cleansing routines, or instructions to avoid/target areas. Transcribe product-specific directions and keep external guidance separately sourced.
- User anecdotes, retailer ratings, and uncontrolled demonstrations must not be represented as controlled product-specific evidence.

#### 5.6.4 UNKNOWN, CONFLICT, and acceptance behavior

- Missing market/version, full INCI, pH, concentration, target material, test method, frequency, contact time, application area, or warning data remains unknown; do not fill it from a similar product.
- If package, manufacturer, retailer, and research sources disagree, preserve each source-bound assertion and mark the relevant item conflicted under the existing workflow.
- “Not stated” must remain distinct from “no”, “soap-free”, “sulfate-free”, “non-comedogenic”, “pH-balanced”, or “safe for sensitive skin”.
- If only selected ingredients are published, do not label them full INCI.
- If only a manufacturer summary is available, attribute it to the manufacturer and note that the underlying test/protocol could not be appraised.
- Any future smart-fill, if separately authorized, may propose source-linked values for human review only. It must not auto-verify Evidence, pass Product QA, activate a product, clear a safety concern, or make the product recommendation-eligible.

#### 5.6.5 Template-specific acceptance criteria

- [ ] Exact product identity, market, variant, and formula/version are recorded or explicitly unknown.
- [ ] Full INCI is distinguished from selected key ingredients and manufacturer-highlighted ingredients.
- [ ] Cleansing claims preserve the exact target material and outcome; makeup/sunscreen removal is not inferred from a generic claim.
- [ ] pH, concentrations, frequency, and contact time are recorded only when supported by an exact source or measurement.
- [ ] Ingredient presence is not used alone to prove mildness, acne benefit, non-comedogenicity, or finished-product efficacy.
- [ ] Finished-product evidence is distinguished from ingredient-level research, marketing, testimonials, and uncontrolled demonstrations.
- [ ] Application areas, rinse directions, frequency, and warnings remain source-bound; “not stated” is not “none”.
- [ ] UNKNOWN and CONFLICT remain visible and are not silently converted into trusted values.
- [ ] Candidate skin-need relationships have a specific basis and never auto-link to P01–P61.
- [ ] Existing DuplicateCheck, research-draft, Evidence QA, Product QA, and lifecycle controls remain authoritative.
- [ ] This documentation does not authorize schema/API/DB changes, smart-fill, evidence verification, operational product registration, QA approval, activation, or recommendation behavior.


### 5.7 `ANTI_ACNE`
| Box ID | Label |
|---|---|
| `acne_claim` | ادعای مرتبط با جوش (متن + منبع) |
| `active_ingredients` | مواد مؤثرهٔ اعلام‌شده (بدون حدس غلظت) |
| `concentration_strength` | غلظت / قدرت اعلام‌شده یا نامشخص |
| `target_claim` | هدف اعلام‌شده (مثلاً جوش، چربی یا ظاهر منافذ) |
| `application_area` | ناحیهٔ مصرف اعلام‌شده |
| `frequency_contact_time` | دفعات مصرف / مدت تماس، فقط طبق منبع |
| `rinse_leave_on` | آبکشی‌شونده / بدون آبکشی / نامشخص |
| `irritation_warnings` | هشدارهای تحریک، خشکی، حساسیت و محدودیت مصرف |

#### 5.7.1 Detailed field contract — `ANTI_ACNE`

This is a **conceptual V1 contract for review**, not a declaration that each candidate key exists in the API, DTO, or database. It does not authorize diagnosis, treatment decisions, smart-fill, evidence mapping, or operational product registration.

| Concept / candidate key | Meaning and semantic class | Source / provenance requirement | Validation and unknown/conflict behavior | Consultation relevance |
|---|---|---|---|---|
| Exact product identity, brand, name | Product identity fact | Exact package or manufacturer source for the specific product | Preserve exact wording; similar names do not establish identity | Prevents transferring claims between products |
| Market, variant, formula and package version | Identity/version context | Market-specific label, exact manufacturer SKU, or documented package evidence | Keep unknowns explicit; conflicting versions remain separate | Claims and instructions may vary by market/version |
| Full INCI | Source fact about labelled formula | Complete ingredient list for the exact market/version | Distinguish full INCI from highlighted ingredients; partial lists must be labelled partial | Enables ingredient review without proving acne efficacy |
| Active ingredients / `active_ingredients` | Labelled or manufacturer-identified ingredient subset | Exact label/manufacturer source; preserve whether legally designated as an active ingredient in that market | Do not call an ingredient a regulatory “active” unless the source and market justify it | Supports review of the actual formula and applicable label |
| Concentration / strength / `concentration_strength` | Quantitative identity or claim fact | Exact package, official technical document, or product-specific source | Record only stated values and units; never infer from INCI order, ingredient reputation, or another version | Strength can materially change interpretation and tolerability |
| Acne-related claim / `acne_claim` | Manufacturer claim, not verified outcome | Exact wording, URL/package reference, market/version and source date where available | Preserve narrow wording; “helps reduce the look of blemishes” is not equivalent to treating acne | Search/research lead, not diagnosis or guaranteed benefit |
| Target claim / `target_claim` | Manufacturer claim or clearly labelled intended-use statement | Exact source wording | Separate acne, excess oil, clogged pores, and cosmetic appearance claims; do not treat them as interchangeable | Clarifies the actual claim under review |
| Mechanism / ingredient role | Scientific interpretation or inference | Ingredient identity plus reliable technical evidence where necessary | Label inference and rationale; do not present a plausible mechanism as proof of finished-product results | Helps explain plausibility, not product efficacy |
| Finished-product evidence | Evidence about the exact marketed product | Identifiable product-specific study/report with formula/version, method, population, duration, comparator and outcomes when reported | Record unavailable details as unknown; distinguish manufacturer summaries from independently reviewed reports | Best relevant evidence for the exact product claim |
| Ingredient-level evidence | Evidence about an individual ingredient or ingredient class | Traceable study/reference and relevant conditions | Keep separate from finished-product evidence; do not transfer ingredient outcomes directly to the product | Indirect context only |
| Skin type / suitability claim | Manufacturer claim or bounded evidence-based inference | Exact source for claims; independent support for any broader interpretation | Do not infer universal suitability for oily, sensitive, adolescent, or acne-prone skin from category or ingredient list alone | Requires individual context and caution |
| Application area / `application_area` | Label instruction | Exact product directions | Do not assume face-only, body-safe, eye-area-safe, or spot-only use | Avoids invented use directions |
| Frequency, amount, contact time | Label instruction | Exact product directions for the same version | Do not infer daily use, dosage, layering, or contact time; unknown remains unknown | Relevant to use and irritation risk |
| Rinse / leave-on | Label instruction | Exact directions | Preserve explicit distinction; do not infer from gel/serum naming | Affects exposure and instructions |
| Irritation, dryness, sensitivity and other warnings | Source fact and/or separately sourced limitation | Exact label/manufacturer warnings; independent limitations need their own evidence | “Not stated” is not “none”; retain conflicting instructions and warnings | Supports risk screening but is not safety clearance |
| Evidence / QA state | Existing Evidence and QA workflow | Use existing source, claim, field, market, dates and QA fields where available | Do not invent new enum values or auto-verify evidence; Evidence QA is not Product QA | Supports traceable human review |
| Candidate skin-need relationship | Research candidate only | Specific claim/feature, evidence reference and explicit relationship basis | No automatic P01–P61 mapping; no diagnosis or individual treatment recommendation | May support later reviewed search/consultation logic only if separately authorized |

#### 5.7.2 Evidence review requirements

For each material anti-acne, blemish, pore, oil-control, or treatment-related claim, capture or explicitly mark unknown:

- exact product, market, variant and formula/version;
- exact claim wording, source, and date when available;
- whether the material is marketing copy, label text, ingredient-level research, product-specific testing, consumer testimony, or an independently reviewed clinical study;
- study population, acne/blemish definition or severity, design, comparator, duration, outcome measure, numerical result, and adverse events when reported;
- whether results apply to the finished product or only to an ingredient, and whether the tested formula matches the marketed version;
- missing protocol/report details, limitations, conflicts, and whether the conclusion is narrower than the marketing wording.

Ingredient presence alone does not establish concentration, efficacy, appropriate treatment, or suitability. Do not infer acne-treatment efficacy from an ingredient list, testimonials, before/after images, or a marketing phrase. Do not convert cosmetic appearance claims into medical treatment claims.

#### 5.7.3 Unknown and conflict handling

- Missing concentration, strength, pH, usage frequency, contact time, full INCI, market, formula version, or study details remain unknown; never fill them from a similar product.
- If sources disagree, preserve the source-bound assertions and flag the conflict under the existing workflow; do not silently select the more favorable claim.
- Distinguish “not stated”, “not applicable”, and an explicit negative claim where the current data model supports those distinctions; do not introduce new persisted values through this document.
- Do not provide diagnosis or prescribe a product from this template. Product intake captures claims and evidence for review; it does not establish an individual's condition.

#### 5.7.4 Template-specific acceptance criteria

- [ ] Exact product identity and market/version are recorded or explicitly unknown.
- [ ] Full INCI is distinguishable from selected or manufacturer-highlighted ingredients.
- [ ] Concentrations, strength, pH, and usage instructions are captured only from exact supporting sources.
- [ ] Cosmetic claims, manufacturer claims, ingredient-level evidence, and finished-product evidence remain distinct.
- [ ] Evidence review retains study context, limitations, conflicts, and adverse-event information when available.
- [ ] “Not stated” is not interpreted as “none”; UNKNOWN and CONFLICT remain visible.
- [ ] No acne diagnosis, guaranteed outcome, or individual treatment recommendation is inferred.
- [ ] No automatic P01–P61 linking, Evidence verification, Product QA, activation, or recommendation eligibility is introduced.
- [ ] Existing DuplicateCheck, research-draft, Evidence QA, Product QA, and lifecycle controls remain authoritative.
- [ ] This conceptual contract does not imply API/DTO/schema/database implementation or operational product registration.



### 5.8 `EXFOLIANT`
| Box ID | Label |
|---|---|
| `exfoliant_type` | نوع لایه‌برداری اعلام‌شده (فیزیکی / شیمیایی / آنزیمی / ترکیبی / نامشخص) |
| `active_exfoliants` | مواد لایه‌بردار اعلام‌شده |
| `concentration_strength` | غلظت / قدرت اعلام‌شده یا نامشخص |
| `ph_value` | pH اندازه‌گیری‌شده یا اعلام‌شده، در صورت وجود |
| `target_claim` | هدف اعلام‌شده و نتیجهٔ مورد ادعا |
| `frequency_contact_time` | دفعات مصرف / مدت تماس، فقط طبق منبع |
| `rinse_leave_on` | آبکشی‌شونده / بدون آبکشی / نامشخص |
| `sun_sensitivity_warnings` | هشدارهای تحریک، حساسیت نوری و محدودیت‌های مصرف |

#### 5.8.1 Detailed field contract — `EXFOLIANT`

This is a **conceptual V1 contract for review**, not a declaration that each candidate key exists in the API, DTO, or database. It does not authorize smart-fill, evidence mapping, product registration, treatment advice, or automatic skin-problem linking.

| Concept / candidate key | Meaning and semantic class | Source / provenance requirement | Validation and unknown/conflict behavior | Consultation relevance |
|---|---|---|---|---|
| Exact product identity, brand, name | Product identity fact | Exact package or manufacturer source | Preserve exact name and variant; similar names do not establish formula identity | Prevents transferring instructions or claims between products |
| Market, formula/version, variant and size | Identity/version context | Market-specific package, exact SKU or official manufacturer source | Unknown remains unknown; retain regional/version conflicts | Formulas, concentrations, and directions may differ |
| Full INCI | Label fact about the formula | Complete package list or exact manufacturer source for same market/version | Distinguish full INCI from selected acids/enzymes or highlighted ingredients | Ingredient review, not proof of exfoliating performance |
| Exfoliant type / `exfoliant_type` | Manufacturer descriptor or reviewed classification | Exact source for manufacturer wording; rationale/source for reviewer classification | Keep physical, chemical, enzyme-based, mixed, and unknown distinctions where supported; do not infer from product name | Describes claimed mechanism, not potency or suitability |
| Named exfoliating ingredients / `active_exfoliants` | Labelled ingredient subset or manufacturer claim | Exact package/manufacturer source | Preserve exact ingredient names; do not assume every acid or enzyme is present at an effective concentration | Research lead only |
| Concentration / strength | Quantitative product fact or claim | Exact label or official technical document tied to the version | Never infer from INCI order, category, retailer copy for another version, or ingredient-level studies; retain units and stated basis | Material to interpreting exposure, but not sufficient alone to establish safety or efficacy |
| pH / `ph_value` | Measured attribute or manufacturer-reported fact | Exact measurement/report or product-specific technical source; method/date when available | Do not infer pH from ingredients, “gentle”, “low pH”, or product category; preserve unknown/conflict | Context for some acid formulations, not a standalone safety verdict |
| Physical exfoliant particles or method | Formula fact / product descriptor | Exact INCI and product description | Do not infer particle size, abrasiveness, or pressure/duration from “scrub”; distinguish manufacturer claim from observation | Helps characterize use method without assuming injury or benefit |
| Target claim / `target_claim` | Manufacturer claim, not verified outcome | Exact claim wording, source, market/version and date when available | Keep texture, dullness, roughness, clogged-pore, pigment, and acne claims distinct; do not convert cosmetic wording into treatment claims | Search/research lead only |
| Finished-product evidence | Evidence about the exact finished formula | Product/version-specific test or study tied to the claim | Capture design, population/test material, comparator, duration, endpoint, method, result and limitations when reported | Supports only the endpoint actually tested |
| Ingredient-level evidence | Research about an ingredient or mechanism | Traceable source and relevant concentration/formulation context where available | Keep separate from finished-product evidence; do not transfer ingredient outcomes directly to the product | Indirect research context only |
| Frequency, amount, contact time | Label instruction | Exact product directions for the same market/version | Do not invent daily/weekly use, application amount, leave-on time, or escalation schedule | Critical instruction fidelity |
| Rinse / leave-on | Label instruction | Exact directions | Do not infer from format, acid type, or marketing name | Determines exposure and correct use |
| Application area and layering cautions | Label instruction or separately sourced limitation | Exact label/manufacturer directions; independent guidance requires its own source | Do not assume face/body/eye-area use or compatibility with retinoids, benzoyl peroxide, or other products | Relevant to context-sensitive review, not personalized prescription |
| Irritation, barrier, photosensitivity and other warnings | Source fact and/or separately sourced limitation | Exact label warnings and appropriately sourced limitations | “Not stated” is not “none”; do not assume every exfoliant has identical warnings or identical risk | Risk screening only, not safety clearance |
| Evidence / QA state | Existing Evidence and QA workflow | Reuse existing source, claim, field, market, dates, conflict and QA fields where supported | Do not invent enums or auto-verify Evidence; Evidence QA is not Product QA | Makes claims traceable for human review |
| Candidate relationship to a skin need | Research candidate only | Specific feature/claim, evidence reference, explicit relationship basis, confirmed identifier and authorized mechanism | No automatic P01–P61 mapping; no diagnosis or individualized treatment recommendation | Potential later research aid only if separately authorized |

#### 5.8.2 Evidence review requirements

For each material claim about exfoliation, smoothness, texture, pores, pigment appearance, acne, or other outcomes, capture or explicitly mark unknown:

- exact product, market, variant and formula/version;
- exact claim wording, source and date when available;
- whether the source is label text, marketing copy, ingredient-level research, consumer feedback, instrumental testing, or a product-specific study;
- the exfoliation method and actual measured endpoint, including method, population/test material, duration, comparator and numerical results when reported;
- for ingredient research, relevant concentration, pH, vehicle/formulation, exposure and study conditions when available;
- adverse events, irritation/tolerability findings, limitations, missing protocol details, and conflicting sources;
- whether the evidence supports the narrow claim or is being stretched to a broader clinical outcome.

Ingredient presence does not establish concentration, product strength, safe frequency, or finished-product efficacy. Do not infer a suitable schedule, combine-use compatibility, or treatment outcome from the ingredient list. Do not use an ingredient study as proof that the marketed product produces the same result.

#### 5.8.3 Unknown and conflict handling

- Missing concentration, pH, full INCI, formula/version, contact time, frequency, application area, warning details, or study methods remain unknown.
- Preserve conflicting label and manufacturer statements; do not select a concentration or direction from a similar product or another market.
- Keep manufacturer claims, measured facts, ingredient-level evidence, finished-product evidence, and reviewer inferences distinguishable.
- “Not stated” is not “none”; absence of a warning in a source is not proof of no risk.
- This template does not recommend an exfoliation schedule or diagnose a skin condition. Product intake captures source-bound information for review only.

#### 5.8.4 Template-specific acceptance criteria

- [ ] Exact product identity and market/version are recorded or explicitly unknown.
- [ ] Full INCI is distinguished from selected exfoliating ingredients and marketing highlights.
- [ ] Exfoliant type is source-bound or supported by an explicit reviewer rationale.
- [ ] Concentration, pH, frequency, amount and contact time are never guessed.
- [ ] Finished-product evidence is distinguished from ingredient-level research, marketing, testimonials and uncontrolled demonstrations.
- [ ] Claims preserve their exact endpoint and are not expanded into unsupported treatment claims.
- [ ] Instructions, application area, layering cautions and warnings are source-bound; “not stated” is not “none”.
- [ ] UNKNOWN and CONFLICT remain visible under the existing workflow.
- [ ] No automatic P01–P61 mapping, Evidence verification, Product QA, activation, or recommendation eligibility is introduced.
- [ ] Existing DuplicateCheck, research-draft, Evidence QA, Product QA, and lifecycle controls remain authoritative.
- [ ] This conceptual contract does not imply API/DTO/schema/database implementation or operational product registration.

