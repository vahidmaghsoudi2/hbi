# Skin intake — box → form / Evidence mapping (V1)

**Status:** Documentation mapping based on **live `master` code** (read-only inspection).  
**Date:** 2026-10-25  
**Canonical folder:** `docs/homepage/product-management/`  
**Authority:** Issue #406. Research ledger: PR #411 (subordinate).  
**Code baseline:** `frontend/src/pages/ProductIntakePanel.tsx` on `master` (includes P1 skeleton from PR **#455** merge commit `29c141de1a`).

This file does **not** authorize further runtime change. It records what exists and what is still decision/implementation-bound.

---

## 0. Manager disposition (this workstream)

| Item | Live finding | Action |
|------|----------------|--------|
| Template **spec** V1 | `SKIN_INTAKE_TEMPLATE_FORMS_V1.md` on master under this folder | **KEEP** — single map; no parallel copy |
| P1 **UI skeleton** | Already on master: when `product_line === "SKIN"`, selector for 9 templates + shared/specific boxes **disabled, empty, not POSTed** | **KEEP**; do not re-implement; next step is enable+persist only after AUTHORIZE |
| PR **#449** | Closed, not merged (historical) | Not an active path |
| PR **#446** | Open; `mergeable_state: dirty`; encyclopedia hub + skin team notes; conflicts likely on `docs/homepage/README.md` vs later master links | **Inspect diffs before Update or Close**; keep encyclopedia/skin coordination content if still unique; do not treat as template SoR |
| Runtime further change | No new AUTHORIZE assumed in this doc | **No code change in this PR** |

---

## 1. Operator path (real)

```text
Homepage → مدیریت محصولات → ورود و ویرایش محصول
  → ProductIntakePanel
       1) intro + smart complete (identity protocol)
       2) protocol fields + product_line (required on create)
       3) if product_line === SKIN → template selector + empty boxes (local only)
       4) DuplicateCheck
       5) create Draft / edit PATCH
       6) optional research-draft Evidence rows
```

Encyclopedia / دانش پوست docs may **link** here; they are not the write path for Product Master.

---

## 2. Protocol / identity fields (form `Draft` → Product API)

Source: `Draft` type + `EMPTY` + `completeFromIntro` + create/edit handlers in `ProductIntakePanel.tsx`.

| Form field | EMPTY / smart default | Persisted on create? | Notes |
|------------|----------------------|----------------------|--------|
| `product_id` | `""` / derived slug | Yes | Operator-editable before create |
| `brand` | `""` / extracted | Yes | |
| `product_name` | `""` / extracted | Yes | |
| `product_line` | `""` (never inferred) | Yes if set | **Required** on create; SKIN unlocks template block |
| `variant` | **`"clear"`** | Yes if sent | **AT-DEF-02:** not package FACT without source/confirm |
| `size_value` | **`50`** | Yes if sent | **AT-DEF-01:** placeholder risk |
| `size_unit` | **`"ml"`** | Yes if sent | with size |
| `spf` | `""` / from text | Via category/name heuristics; confirm API body | Protocol UI field |
| `category` | `""` / heuristic | Mapped into knowledge_* hints on create in panel | Not a substitute for Evidence |
| `barcode_gtin` | `""` | Yes | Identity / DuplicateCheck |
| `market_region` | **`"IR"`** (+ forced again in `completeFromIntro`) | Yes if sent | **AT-DEF-03:** default without source |
| `packaging_version` | `""` | Yes if used | |
| `identity_status` | `NEEDS_REVIEW` | Server-controlled display | |
| `status` | `DRAFT` | Server lifecycle | |
| `qa_verdict` | `PENDING` | Server-controlled display | |

### Acceptance (defaults)

| ID | Rule |
|----|------|
| AT-DEF-01 | Size 50/ml must not be treated as verified package data without extract or operator intent |
| AT-DEF-02 | variant `clear` must not be treated as verified FACT without keyword or operator intent |
| AT-DEF-03 | market_region `IR` must not be treated as verified market without source or explicit choice |
| AT-DEF-04 | Missing `product_line` blocks create |
| AT-DEF-08 | Identity field change invalidates DuplicateCheck fingerprint |

---

## 3. Shared template boxes → destination

UI labels from `SKIN_SHARED_BOXES` (P1: **disabled**, not in create body).

| Box (UI label) | Exists on Product create body? | Evidence `field` if later saved as research-draft | Status |
|----------------|----------------------------------|---------------------------------------------------|--------|
| منبع / لینک / برچسب | No | `source_reference` (required on research-draft) | **Map to Evidence source_** |
| نوع منبع | No | `source_type` | **Map to Evidence** |
| منطقه بازار (با شاهد) | Overlaps protocol `market_region` | Evidence `market_region` optional | **Do not auto-copy IR** |
| اهداف پوستی اعلام‌شده | No | `known_use_cases` (text only) | **Candidate text only — no P0x IDs** |
| هشدارها و محدودیت‌ها | No | `contraindications` | **Needs enable + Evidence row** |
| روش مصرف | No | `usage_instructions` | **Needs enable + Evidence row** |
| ترکیبات کلیدی اعلام‌شده | No | `ingredients` | **Needs enable + Evidence row** |
| سایر / اضافات | No | `notes` or claim text | Catch-all |

Research-draft UI already allows `field` ∈  
`claimed_benefits` | `known_use_cases` | `ingredients` | `contraindications` | `usage_instructions` | `manufacturer_claims`  
with `claim_type` default `MANUFACTURER_CLAIM` and `source_type` default `MANUFACTURER`.

---

## 4. Template-specific boxes → destination

All P1-specific inputs are **display-only**. Mapping below is **target** for a future enablement AUTHORIZE — not current persistence.

### HYDRATING_MOISTURIZER
| Box | Target |
|-----|--------|
| بافت | **Needs decision/impl** (no Product column; optional claim/`notes`) |
| حس پوستی اعلام‌شده | **Needs decision/impl** |
| روز / شب / هر دو | **Needs decision/impl** |
| ادعای آبرسانی… | Evidence `claimed_benefits` or `manufacturer_claims` + source |

### SUNSCREEN
| Box | Target |
|-----|--------|
| SPF | Protocol `spf` **and/or** Evidence claim; avoid double FACT |
| PA / UVA | **Needs decision/impl** (no dedicated column) |
| نوع فیلتر | **Needs decision/impl** |
| مقاومت آب | **Needs decision/impl** |
| رنگی / بی‌رنگ | Protocol `variant` (tinted/clear) — only with source |
| صورت / بدن | **Needs decision/impl** or `known_use_cases` |

### BRIGHTENING_SPOT
| Box | Target |
|-----|--------|
| هدف اعلام‌شده | `known_use_cases` (text) |
| مواد فعال اعلام‌شده | `ingredients` |
| بازه زمانی ادعا | claim text / `notes` |
| اعداد ادعا | `manufacturer_claims` + source; **never auto VERIFIED** |

### MICELLAR / TONER / CLEANSING_GEL / ANTI_ACNE / EXFOLIANT / OTHER_SKIN
| Pattern | Target |
|---------|--------|
| Label-driven yes/no/unknown attributes | **Needs decision/impl** unless expressed as Evidence claim text |
| Actives / acids / frequency / irritation | `ingredients` / `usage_instructions` / `contraindications` as appropriate |
| why_other / free notes | `notes` |

---

## 5. What is NOT a destination today

| Concept | Status |
|---------|--------|
| `skin_form_template` persisted on Product | **Needs decision/impl** (UI state only today) |
| ProductKnowledge direct write from template boxes | **Forbidden path** — PK is rebuild from eligible Evidence |
| Auto P01–P61 | **Forbidden** |
| Encyclopedia localStorage as SoR | **Forbidden** |

---

## 6. Recommended next steps (ordered)

1. **PR #446:** Refresh live conflict list; keep unique encyclopedia/skin team text; drop redundant README edits already on master; Update or Close with reason — no force-push.
2. **PO in #406:** Acknowledge P1 skeleton already merged (#455); decide whether to AUTHORIZE **P1b** (enable boxes + local/session only) vs **P1c** (persist template id + map shared boxes → research-draft).
3. **Tests:** Automate or manually record AT-DEF-01…03 against current `EMPTY` / `completeFromIntro` before treating Draft identity as package-true.
4. **No parallel Issue/PR** for the same mapping; extend this file only.

---

## 7. Independent review checklist (for Grok / second reviewer)

- [ ] Every shared box row cites real Evidence field or explicit **Needs decision/impl**
- [ ] No invented Product columns
- [ ] Defaults IR / 50 / clear called out with AT-DEF ids
- [ ] P1 skeleton existence on master stated with PR #455 reference
- [ ] #446 disposition does not blindly Close without conflict note

---

*End of mapping V1. Runtime enablement requires explicit AUTHORIZE in Issue #406.*
