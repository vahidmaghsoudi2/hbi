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
| **P0** | This fixed-template specification and documentation links | PO template decisions approved; P0 delivery still requires review, current branch, passing required checks, and merge |
| **P1** | Template selector and empty shared/specific boxes inside the existing Product Intake UI, only under `product_line = SKIN` | Explicitly authorized only after P0 is merged; no work before that gate |
| **P2** | Smart extraction | Not authorized by P1 |
| **P3** | Evidence mapping / research-draft creation | Not authorized by P1 |
| **P4** | Consultation bridge / problem mapping | Not authorized by P1; canonical problem links require separate rules |

No phase in this table authorizes schema/API/DB changes, product activation, QA bypass, or verified ProductKnowledge from smart-fill alone.

## 8. Acceptance checklist

- [x] Scope is restricted to `product_line = SKIN`.
- [x] Canonical location is under `docs/homepage/product-management/`.
- [x] Product Owner approved the merged hydration/moisturizer template and all nine V1 templates: [Issue #406 decision](https://github.com/vahidmaghsoudi2/hbi/issues/406#issuecomment-6389070595).
- [x] P1 is gated on P0 merge and remains limited to UI skeleton / empty boxes.
- [ ] P0 documentation PR is reviewed, based on current master, and merged.
- [ ] After P0 merge, record the resulting master commit and verify the exact merge outcome before starting P1.

## 9. Remaining boundaries (not unresolved template-count decisions)

- The storage representation for future template values (notes/JSON versus schema) is **not decided here** and is outside P0/P1 authorization; P1 must not add schema/API/DB.
- `stated_skin_goals` remains plain text/candidate only. No automatic linkage to P01–P61 is allowed. Any future linkage policy needs a separate explicit decision in Issue #406.
- Physical identity of each of the seven research dossiers remains separate from this template specification. No product is thereby registered as an operational record.

---

*P0 specification only. P1 starts only after P0 is actually merged; its scope remains the existing-form UI skeleton described above.*
