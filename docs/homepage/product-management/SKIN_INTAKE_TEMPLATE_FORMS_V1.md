# Skin product intake — fixed template forms (V1)

**Status:** DRAFT specification for implementation planning  
**Date:** 2026-10-24  
**Canonical location:** `docs/homepage/product-management/SKIN_INTAKE_TEMPLATE_FORMS_V1.md` (homepage menu: مدیریت محصولات → ورود و ویرایش محصول)  
**Authority:** Product decisions / Gates remain in [Issue #406](https://github.com/vahidmaghsoudi2/hbi/issues/406). This file is the operational field map for skin intake templates.  
**Do not copy** this map into scattered Issues or parallel folders; update this file only.  
**Research continuity:** [PR #411](https://github.com/vahidmaghsoudi2/hbi/pull/411) ledger stays subordinate research; it does not replace this form map.

## 1. Purpose

Define **fixed, type-specific field boxes** for skin-care products so smart completion can fill structured boxes (not free-form typing of every attribute). Operators review and correct before Draft + DuplicateCheck + QA.

This V1 is intentionally incomplete and editable in later versions.

## 2. Architecture (non-negotiable)

```text
product_line = SKIN          ← existing mandatory line (operator selects; not inferred)
    └── skin_form_template   ← one of the templates below (V1)
            ├── shared boxes (all templates)
            ├── template-specific boxes
            └── extras box (catch-all)
```

| Layer | Role |
|-------|------|
| `product_line = SKIN` | Existing HBI line; required on create |
| `skin_form_template` | New discriminator for which fixed boxes apply |
| Protocol / identity fields | Existing smart complete (`completeFromIntro`): name, brand, size, SPF, GTIN, category hint, etc. |
| Template boxes | Structured attributes + claims for later consultation / problem linking |
| Evidence / research draft | Strong efficacy numbers and sources → draft claims (`PENDING`), not auto-VERIFIED |
| ProductKnowledge | Only after authorized QA path; templates do not bypass QA |
| Encyclopedia UI | Optional display later; **not** the system of record for these boxes |

## 3. V1 template list (`skin_form_template`)

| Code | Label (FA) | Notes |
|------|------------|--------|
| `HYDRATING_MOISTURIZER` | آبرسان / مرطوب‌کننده | V1 merges آبرسان and مرطوب‌کننده |
| `SUNSCREEN` | ضدآفتاب | |
| `BRIGHTENING_SPOT` | روشن‌کننده و ضدلک | |
| `MICELLAR` | میسلار واتر | |
| `TONER` | تونر | |
| `CLEANSING_GEL` | ژل شستشو | |
| `ANTI_ACNE` | ضدجوش | |
| `EXFOLIANT` | لایه‌بردار | |
| `OTHER_SKIN` | سایر (پوست) | When no template fits; still under SKIN |

**Primary only in V1.** Optional secondary tags may come in V1.1.

## 4. Shared boxes (every template)

| Box id | Label (FA) | Smart-fill | Storage hint | Consultation use |
|--------|------------|------------|--------------|------------------|
| `source_ref` | منبع / لینک / برچسب | From pasted URL or برچسب بسته | Evidence `source_reference` / notes | Traceability |
| `source_type` | نوع منبع | Default MANUFACTURER or LABEL | Evidence `source_type` | Traceability |
| `market_region` | منطقه بازار | From intro if present; else operator | Product / evidence region | Version control |
| `stated_skin_goals` | اهداف پوستی اعلام‌شده (متنی) | Keywords from summary | Notes or draft claim `known_use_cases` | **Candidate only** for later P01–P61 |
| `warnings_limits` | هشدارها و محدودیت‌ها | From label phrases | `contraindications` or notes | Safety in advice |
| `usage_directions` | روش مصرف | From label | `usage_instructions` | Advice |
| `key_ingredients` | ترکیبات کلیدی (اعلام‌شده) | INCI/list if in text | `ingredients` | Never invent concentrations |
| `extras` | سایر / اضافات | Remainder text | notes | Catch-all |

**Hard rules for smart fill**

1. Do not invent concentrations, medical diagnoses, or cure claims.
2. Percent efficacy → manufacturer/draft claim with source only; never verified from smart fill alone.
3. Do not auto-assign canonical problem IDs (P08, P17, …).
4. `product_line` remains operator-selected SKIN.

## 5. Template-specific boxes (V1 minimum)

### 5.1 `HYDRATING_MOISTURIZER`
| Box id | Label |
|--------|--------|
| `texture` | بافت (کرم / ژل / لوسیون / سرم / نامشخص) |
| `skin_feel` | حس پوستی اعلام‌شده |
| `day_night` | روز / شب / هردو / نامشخص |
| `hydration_claim` | ادعای آبرسانی یا حفظ رطوبت (متن + منبع) |

### 5.2 `SUNSCREEN`
| Box id | Label |
|--------|--------|
| `spf_value` | SPF |
| `pa_rating` | PA / UVA claim |
| `filter_type` | شیمیایی / فیزیکی / ترکیبی / نامشخص |
| `water_resistance` | مقاومت در برابر آب |
| `tint` | رنگی / بی‌رنگ / نامشخص |
| `face_body` | صورت / بدن / هردو |

### 5.3 `BRIGHTENING_SPOT`
| Box id | Label |
|--------|--------|
| `target_discoloration` | هدف اعلام‌شده |
| `actives_stated` | مواد فعال اعلام‌شده |
| `claim_timeline` | بازهٔ زمانی ادعای سازنده |
| `claim_metrics` | اعداد ادعای سازنده فقط با منبع |

### 5.4 `MICELLAR`
| Box id | Label |
|--------|--------|
| `makeup_removal` | پاک‌کننده آرایش بله/خیر/نامشخص |
| `rinse_required` | نیاز به آبکشی |
| `eye_area` | مناسب اطراف چشم طبق برچسب |

### 5.5 `TONER`
| Box id | Label |
|--------|--------|
| `toner_role` | نقش اعلام‌شده |
| `alcohol_stated` | الکل در فرمول اعلام شده |

### 5.6 `CLEANSING_GEL`
| Box id | Label |
|--------|--------|
| `rinse_off` | آبکشی‌شونده |
| `surfactant_or_acid_focus` | تمرکز اعلام‌شده |
| `frequency_label` | تناوب مصرف طبق برچسب |

### 5.7 `ANTI_ACNE`
| Box id | Label |
|--------|--------|
| `acne_focus` | تمرکز اعلام‌شده |
| `actives_stated` | مواد فعال اعلام‌شده |
| `leave_on_or_rinse` | ماندگار / آبکشی |

### 5.8 `EXFOLIANT`
| Box id | Label |
|--------|--------|
| `exfoliant_type` | شیمیایی / فیزیکی / آنزیمی / نامشخص |
| `acids_or_grains_stated` | اسیدها یا ذرات اعلام‌شده |
| `frequency_label` | تناوب مصرف |
| `irritation_warning` | هشدار تحریک از برچسب |

### 5.9 `OTHER_SKIN`
| Box id | Label |
|--------|--------|
| `why_other` | چرا در قالب‌های بالا جا نگرفت |
| `free_structured_notes` | یادداشت ساخت‌یافته اپراتور |

## 6. Operator flow (V1 target UX)

1. Open **مدیریت محصولات → ورود و ویرایش محصول**.
2. Paste **خلاصه معرفی** → existing **تکمیل هوشمند** for protocol fields.
3. Select **`product_line = SKIN`**.
4. Select **`skin_form_template`**.
5. Template smart fill (future) on text / label paste.
6. Operator edits boxes; fills `extras` if needed.
7. **DuplicateCheck** → create **Draft**.
8. Optional research-draft Evidence rows for claim-like boxes.
9. QA path unchanged.

## 7. Implementation phases

| Phase | Scope |
|-------|--------|
| **P0 — this document** | Lock V1 boxes (docs only) |
| **P1 — UI skeleton** | Template selector + empty boxes under SKIN; no API/schema/DB |
| **P2 — smart fill** | Deterministic extractors |
| **P3 — Evidence mapping** | Research-draft button |
| **P4 — consultation bridge** | Problem IDs only after PO rules in #406 |

**No phase authorizes** activation, QA bypass, or verified ProductKnowledge from smart fill alone.

## 8. Acceptance (docs)

- [x] Templates under SKIN only
- [x] Canonical path under `docs/homepage/product-management/`
- [ ] PO approval in Issue #406
- [ ] P1 authorized only after this P0 is merged

## 9. Open PO decisions

1. Confirm `HYDRATING_MOISTURIZER` merge.
2. Confirm nine templates.
3. V1 storage: notes/JSON vs schema.
4. When `stated_skin_goals` may link to P01–P61.

---

*P0 specification only. P1 starts only after merge + explicit authorization.*
