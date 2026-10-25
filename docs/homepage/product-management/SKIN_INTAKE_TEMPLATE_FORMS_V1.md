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
