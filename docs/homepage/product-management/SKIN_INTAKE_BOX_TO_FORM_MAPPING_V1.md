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


---

## 8. PO-directed seven-product template matrix (design proposal, 2026-10-28)

**Decision source:** Issue #406 and its latest PO decision.  
**Purpose:** Specify the correct *type-specific* boxes for the seven existing SKIN products before changing runtime code. This section extends this mapping document; it does not create a second roadmap or authorize a new API/schema/database field.

### 8.1 Template assignment

| Dossier | Existing Product Master record | Primary template | Why this template | Identity caveat |
|---|---|---|---|---|
| P1 COSRX The 6 Peptide Skin Booster Serum | `HBI-PROD-F66ED6FEA6144D71` | `OTHER_SKIN` for V1 | A peptide booster serum does not fit the current hydration, sunscreen, cleanser, toner, micellar, acne, exfoliant or brightening-specific form solely from its name. Keep peptide/booster details in its dedicated extras until a general serum template is separately approved. | 150 ml dossier; confirm the physical pack/version before attaching pack-specific facts. |
| P2 Neutrogena Clear & Defend 2% Salicylic Acid Face Wash | `HBI-PROD-37EB7C42C6BE413B` | `CLEANSING_GEL` | Primary product is a rinse-off face wash; salicylic acid is a formula/claim detail and does not turn the cleanser into a leave-on exfoliant. | Dossier's market and physical formula are unconfirmed; the UK source must not be represented as proof of the user's exact pack. |
| P3 Garnier Vitamin C Brightening Gel Cleanser | `HBI-PROD-9F7C2CE624D14E5A` | `CLEANSING_GEL` | Primary function/form is a rinse-off gel cleanser; brightening wording and vitamin-C derivative remain source-bound claims/ingredient data. | Dossier cites Australian version; verify physical pack before treating INCI as exact. |
| P4 SKIN1004 Madagascar Centella Hyalu-Cica Water-Fit Sun Serum | `HBI-PROD-AB647F422E174BD8` | `SUNSCREEN` | It is a sunscreen despite “serum” in the product name. | Keep Korean/international SPF50+ PA++++ and US SPF50 UV drug-label versions separate. No cross-version filter/formula copying. |
| P5 ISDIN FotoUltra 100 Active Unify SPF50+ | `HBI-PROD-03781074C3BF448A` | `SUNSCREEN` | Primary product is a sunscreen; spot-related wording is an additional manufacturer claim, not a replacement template. | Dossier source is Mexico; don't assume same formula or claims for other markets. |
| P6 Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter | `HBI-PROD-85AD86B15C734EF2` | `BRIGHTENING_SPOT` | Primary positioning is dark-spot correction/brightening serum. | Research dossier concerns 100 ml; verify exact market/package and avoid mixing clinical and consumer-test endpoints. |
| P7 Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum | `HBI-PROD-7AD37ECCEA874E12` | `OTHER_SKIN` for V1 | A soothing serum with azelaic-acid positioning is not a cleanser or exfoliant; V1 has no general serum template. Use structured shared boxes and source-bound extras; do not infer acne/rosacea diagnosis. | 10% is a manufacturer-declared claim in the dossier, not an independently verified concentration. Keep exact serum separate from Anua pads and other SKUs. |

Template selection is based on primary product form/use, not merely on an ingredient or secondary marketing claim. The operator must explicitly select `product_line=SKIN` and the primary template. This matrix is an initial assignment from the research dossier, not proof that a physical unit's market/formula has been verified.

### 8.2 Shared boxes — required for every template

| Box | What may be recorded | Evidence handling / boundary |
|---|---|---|
| Source reference | Exact URL, package label reference, dated document or other traceable source | Required for each research assertion; no unsourced claim is submitted. |
| Source type | Manufacturer, package label, peer-reviewed publication, clinical trial, regulatory source, other allowed existing value | Use only values accepted by the current Evidence API; don't invent enum values. |
| Market/version context | Market, formula/version, pack size and date when evidenced | Unknown remains unknown; never use the UI default or a sibling-market source as package proof. |
| Manufacturer-stated goal/use | Exact claim wording or carefully bounded summary | Existing `known_use_cases` / `claimed_benefits` only when semantics match; do not map automatically to P01–P61 or diagnosis. |
| Key ingredients | Ingredient names actually present in the exact source/label; distinguish partial key list from full INCI | Existing `ingredients` Evidence field. Do not infer concentration or ingredient role from presence alone. |
| Usage directions | Source's amount, frequency, area, rinse/leave-on and reapplication statements, only when stated | Existing `usage_instructions`; source wording/market remains visible. |
| Warnings and limitations | Label warnings and separately sourced evidence limitations | Existing `contraindications` only where semantically appropriate; not a safety clearance. |
| Other features / extras | Free text preserving a relevant detail that has no dedicated box, with source and claim type | Preserve as a research assertion only if existing endpoint can represent it without semantic misclassification. Do not silently map arbitrary text to `ingredients`, `contraindications`, or a verified field. If no safe destination exists, retain it in the research working record and flag it for mapping review rather than discarding it or changing the API. |

### 8.3 Type-specific boxes

#### `CLEANSING_GEL` — P2 Neutrogena and P3 Garnier
- Rinse-off / leave-on status (label-bound; expected rinse-off for these products, but still record from exact label).
- Declared cleansing focus / manufacturer-stated use.
- Highlighted active ingredients and concentrations only when the exact label/source states them.
- Frequency and directions exactly as labelled.
- Eye/mucosal avoidance, irritation, fragrance/allergen warnings only if the source states them.
- Product-specific claims (for example, spot/brightening wording) separately from cleanser function.
- For P2, 2% salicylic acid is in the research dossier for the UK source; do not treat it as confirmed for the target pack until market/formula identity is checked.
- For P3, Ascorbyl Glucoside must not be relabelled as pure L-ascorbic acid; concentration remains unknown unless sourced.

#### `SUNSCREEN` — P4 SKIN1004 and P5 ISDIN
- SPF exactly as shown on the matched package/market source.
- PA/UVA wording or rating only if explicitly present on that exact source.
- UV filters/active ingredients as listed for that exact market/version.
- Water resistance only when stated; do not infer it.
- Tinted/untinted and face/body suitability only when supported by the exact label.
- Amount, application, reapplication and other directions exactly as labelled.
- Spot/brightening/hydration claims remain separate manufacturer claims with their own source and endpoint; never treat them as proof of sunscreen performance.
- P4 must keep international SPF50+ PA++++ and US SPF50 UV formula records separate.
- P5 claims from the Mexico page remain market-specific until the target pack is verified.

#### `BRIGHTENING_SPOT` — P6 Clinique
- Manufacturer-stated target/appearance claim (not a diagnosis or promise of treatment).
- Named key ingredients as published for the exact 100 ml/market version.
- Manufacturer-reported study outcome, duration, sample and endpoint as separate sourced claim text.
- Distinguish the 52-person clinical test from the 533-person consumer test; never combine denominators/endpoints.
- Do not infer active concentrations, RCT design, independent verification or treatment of melasma without supporting sources.

#### `OTHER_SKIN` — P1 COSRX and P7 Anua
- Product form and stated intended use.
- Named actives/key ingredients and supporting ingredient groups as reported by source.
- Manufacturer claims and study summaries recorded verbatim or accurately summarized with sample, duration, endpoint and source where available.
- Usage directions and warnings from exact label.
- P1 COSRX: keep the six named peptides, niacinamide/humectant context and manufacturer-reported study outcomes separate; peptide concentrations and exact-product independent efficacy remain unknown unless evidenced.
- P7 Anua: keep the manufacturer's 10% azelaic-acid declaration distinct from independent confirmation; record gradual-introduction instructions only from the matched official source; never transfer evidence from the separate pad product.
- These two products remain on `OTHER_SKIN` in V1 rather than inventing an unapproved generic-serum template. A future general-serum template requires a separate revision decision.

### 8.4 Data-state semantics for every box

| State | Meaning | UI / persistence rule |
|---|---|---|
| EMPTY | No value/assertion has been entered | Never interpret as safe, absent, negative, or “does not have this feature.” |
| UNKNOWN | Explicit assertion that the value is currently unknown/unresolved | Requires a source/reference when submitted through research-draft, such as a documented check or explicit review note; remains PENDING/UNKNOWN. |
| NEEDS_REVIEW | A value exists or a source/identity conflict requires a human check | Keep the candidate and reason visible; do not silently select one market/formula/source. |
| NOT_APPLICABLE / FEATURE_ABSENT | Use “فاقد این ویژگی” only where the attribute is genuinely inapplicable or an authoritative source supports absence | Do not infer absence from an ingredient list that may be partial or a source that does not mention the attribute. Preserve the rationale/source. |
| CONFLICT | Relevant sources disagree | Preserve competing assertions and sources; do not overwrite one with another without review. |

These are design-level semantics. Before adding a new persisted enum or column, map them to existing UI state and Evidence claim types. If the current API cannot represent a state without distortion, do not simulate it by misusing another field; record the gap for an explicitly authorized contract change.

### 8.5 Persistence boundary and implementation sequence

1. Keep Product Master identity fields, Evidence research assertions and approved ProductKnowledge separate.
2. Use the existing research-draft endpoint and accepted Evidence fields only when the box's meaning matches that field.
3. Require source type and source reference for each submitted assertion. Keep drafts `PENDING` / `UNKNOWN`; never auto-approve.
4. Do not send every box as `ingredients` or as a generic claim. Field mapping must be semantic and allowlisted.
5. Do not create a Product Master record from the box form. Select one of the existing seven products and verify the selected ID before submission.
6. Preserve all existing identity/version/market caveats. In particular, do not seed defaults such as `IR`, `clear`, or `50 ml` as package facts.
7. First implement and test the shared boxes + `OTHER_SKIN` and type-specific boxes against a non-test existing SKIN product; then test the two cleanser products, the two sunscreens and Clinique. This order is a verification sequence, not permission to write fabricated claims.
8. No new API, database column, schema migration, taxonomy, or ProductKnowledge direct-write path is authorized by this matrix.

### 8.6 Acceptance criteria before enabling all seven products

- [ ] Each of the seven existing IDs opens in edit mode and shows the correct primary template.
- [ ] Every template includes the shared boxes and an always-available extras box.
- [ ] Empty, UNKNOWN, NEEDS_REVIEW, FEATURE_ABSENT/NOT_APPLICABLE and CONFLICT are not collapsed into one value.
- [ ] Empty optional boxes do not block product intake.
- [ ] Every submitted research assertion requires source type and source reference and remains PENDING/UNKNOWN pending review.
- [ ] Every structured box maps only to a semantically compatible existing Evidence field.
- [ ] Extras never silently become a verified ProductKnowledge fact; if there is no safe destination, preserve and flag rather than mis-map.
- [ ] No Product Master create call is triggered by saving research boxes.
- [ ] No default value is represented as a package fact without source/explicit operator confirmation.
- [ ] Tests prove the selected product ID is used, no cross-product contamination occurs, and no pending assertion appears as approved ProductKnowledge.
- [ ] Local registration/read-back is verified against a real existing product before the seven-product batch is called complete.

*This matrix is a design/field-mapping update to the existing PR #466, not runtime implementation or product evidence entry. CI and local read-back remain separate verification gates.*
