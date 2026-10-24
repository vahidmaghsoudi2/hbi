# Skin product intake — fixed template forms (V1)

**Status:** DRAFT specification for implementation planning  
**Date:** 2026-10-24  
**Authority:** Product decisions / Gates remain in [Issue #406](https://github.com/vahidmaghsoudi2/hbi/issues/406). This file is the operational field map for skin intake templates.  
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
| `HYDRATING_MOISTURIZER` | آبرسان / مرطوب‌کننده | V1 merges «آبرسان» and «مرطوب‌کننده» to avoid duplicate registration; split in a later version only if PO requires |
| `SUNSCREEN` | ضدآفتاب | |
| `BRIGHTENING_SPOT` | روشن‌کننده و ضدلک | |
| `MICELLAR` | میسلار واتر | |
| `TONER` | تونر | |
| `CLEANSING_GEL` | ژل شستشو | |
| `ANTI_ACNE` | ضدجوش | |
| `EXFOLIANT` | لایه‌بردار | |
| `OTHER_SKIN` | سایر (پوست) | When no template fits; still under SKIN |

**Primary + secondary (optional in UI later):** one **primary** template is required; optional secondary tags (e.g. primary `CLEANSING_GEL` + secondary `ANTI_ACNE`) may be added in V1.1 if a product spans two roles. V1 ships with primary only + `extras`.

## 4. Shared boxes (every template)

| Box id | Label (FA) | Smart-fill | Storage hint | Consultation use |
|--------|------------|------------|--------------|------------------|
| `source_ref` | منبع / لینک / برچسب | From pasted URL or «برچسب بسته» | Evidence `source_reference` / notes | Traceability |
| `source_type` | نوع منبع | Default MANUFACTURER or LABEL | Evidence `source_type` | Traceability |
| `market_region` | منطقه بازار | From intro if present; else operator | Product / evidence region | Version control |
| `stated_skin_goals` | اهداف پوستی اعلام‌شده (متنی) | Keywords from summary | Notes or draft claim field `known_use_cases` | **Candidate only** for later P01–P61 link — not an official problem ID |
| `warnings_limits` | هشدارها و محدودیت‌ها | From label phrases | Evidence field `contraindications` or notes | Safety in advice |
| `usage_directions` | روش مصرف | From label | Evidence `usage_instructions` | Advice |
| `key_ingredients` | ترکیبات کلیدی (اعلام‌شده) | INCI/list if in text | Evidence `ingredients` | Never invent concentrations |
| `extras` | سایر / اضافات | Remainder text | notes | Catch-all for unmodeled attributes |

**Hard rules for smart fill**

1. Do not invent concentrations, medical diagnoses, or cure claims.  
2. Percent efficacy → store only as manufacturer/draft claim with source; never as verified fact from smart fill alone.  
3. Do not auto-assign canonical problem IDs (P08, P17, …).  
4. `product_line` remains operator-selected SKIN.

## 5. Template-specific boxes (V1 minimum)

### 5.1 `HYDRATING_MOISTURIZER` — آبرسان / مرطوب‌کننده

| Box id | Label |
|--------|--------|
| `texture` | بافت (کرم / ژل / لوسیون / سرم / نامشخص) |
| `skin_feel` | حس پوستی اعلام‌شده (سبک / چرب / نامشخص) |
| `day_night` | روز / شب / هردو / نامشخص |
| `hydration_claim` | ادعای آبرسانی یا حفظ رطوبت (متن + منبع) |

### 5.2 `SUNSCREEN` — ضدآفتاب

| Box id | Label |
|--------|--------|
| `spf_value` | SPF |
| `pa_rating` | PA / UVA claim |
| `filter_type` | شیمیایی / فیزیکی / ترکیبی / نامشخص |
| `water_resistance` | مقاومت در برابر آب (دقیقه یا نامشخص) |
| `tint` | رنگی / بی‌رنگ / نامشخص |
| `face_body` | صورت / بدن / هردو |

### 5.3 `BRIGHTENING_SPOT` — روشن‌کننده و ضدلک

| Box id | Label |
|--------|--------|
| `target_discoloration` | هدف اعلام‌شده (لک / یکنواختی / درخشش / نامشخص) |
| `actives_stated` | مواد فعال اعلام‌شده (بدون غلظت ساختگی) |
| `claim_timeline` | بازهٔ زمانی ادعای سازنده (مثلاً ۱۲ هفته) اگر آمده |
| `claim_metrics` | اعداد ادعای سازنده (٪، n) فقط با منبع |

### 5.4 `MICELLAR` — میسلار واتر

| Box id | Label |
|--------|--------|
| `makeup_removal` | پاک‌کننده آرایش بله/خیر/نامشخص |
| `rinse_required` | نیاز به آبکشی بله/خیر/نامشخص |
| `eye_area` | مناسب اطراف چشم طبق برچسب بله/خیر/نامشخص |

### 5.5 `TONER` — تونر

| Box id | Label |
|--------|--------|
| `toner_role` | نقش اعلام‌شده (آماده‌سازی / تعادل pH / آرامش / نامشخص) |
| `alcohol_stated` | الکل در فرمول اعلام شده بله/خیر/نامشخص |

### 5.6 `CLEANSING_GEL` — ژل شستشو

| Box id | Label |
|--------|--------|
| `rinse_off` | آبکشی‌شونده (پیش‌فرض بله) |
| `surfactant_or_acid_focus` | تمرکز اعلام‌شده (پاک‌کنندگی / اسید / نامشخص) |
| `frequency_label` | تناوب مصرف طبق برچسب |

### 5.7 `ANTI_ACNE` — ضدجوش

| Box id | Label |
|--------|--------|
| `acne_focus` | تمرکز اعلام‌شده (جوش سطحی / کومدون / چربی / نامشخص) |
| `actives_stated` | مواد فعال اعلام‌شده |
| `leave_on_or_rinse` | ماندگار روی پوست / آبکشی |

### 5.8 `EXFOLIANT` — لایه‌بردار

| Box id | Label |
|--------|--------|
| `exfoliant_type` | شیمیایی / فیزیکی / آنزیمی / نامشخص |
| `acids_or_grains_stated` | اسیدها یا ذرات اعلام‌شده |
| `frequency_label` | تناوب مصرف طبق برچسب |
| `irritation_warning` | هشدار تحریک از برچسب |

### 5.9 `OTHER_SKIN` — سایر

| Box id | Label |
|--------|--------|
| `why_other` | چرا در قالب‌های بالا جا نگرفت |
| `free_structured_notes` | یادداشت ساخت‌یافته اپراتور |

## 6. Operator flow (V1 target UX)

1. Open **مدیریت محصولات → ورود و ویرایش محصول**.  
2. Paste **خلاصه معرفی** → existing **تکمیل هوشمند** for protocol fields.  
3. Select **`product_line = SKIN`**.  
4. Select **`skin_form_template`**.  
5. Run **template smart fill** (future) on the same text / optional second paste (label text).  
6. Operator edits boxes; fills `extras` if needed.  
7. **DuplicateCheck** → create **Draft**.  
8. Optional: promote selected boxes into **research draft** Evidence rows (claim_type + field + source).  
9. QA / verify / conflict resolution unchanged.

## 7. Implementation phases (do not skip)

| Phase | Scope | Code change? |
|-------|--------|--------------|
| **P0 — this document** | Lock V1 boxes and rules | Docs only |
| **P1 — UI skeleton** | Template selector + empty boxes under SKIN on intake form; save as structured JSON or notes until schema agreed | Frontend (+ optional JSON column/API later) |
| **P2 — smart fill rules** | Deterministic extractors per template (regex / keyword); no LLM required for V1 | Frontend helpers |
| **P3 — Evidence mapping** | Button: «ثبت به‌عنوان پیش‌نویس شاهد» for claim-like boxes | API research-draft already exists |
| **P4 — consultation bridge** | Map `stated_skin_goals` to official problem IDs only after PO rules | Requires #406 decision |

**No phase authorizes** activation, QA bypass, or writing verified ProductKnowledge from smart fill alone.

## 8. Acceptance criteria for V1 docs (this file)

- [x] Templates listed under SKIN only  
- [x] Shared + per-template boxes named  
- [x] Smart-fill safety rules stated  
- [x] Explicit non-goals: no auto problem IDs, no QA skip, encyclopedia not SoR  
- [ ] PO approval recorded in Issue #406 (pending)  
- [ ] P1 UI implementation authorized separately  

## 9. Open decisions for Product Owner

1. Confirm merge of آبرسان + مرطوب‌کننده into `HYDRATING_MOISTURIZER`.  
2. Confirm nine codes above vs splitting hydrators again.  
3. Whether template payload in V1 may live in `notes`/JSON without migration, or requires schema.  
4. When official links from `stated_skin_goals` → P01–P61 may begin.

---

*End of V1 specification. Implementation starts only after PO approval of this map and an explicit P1 authorization.*
