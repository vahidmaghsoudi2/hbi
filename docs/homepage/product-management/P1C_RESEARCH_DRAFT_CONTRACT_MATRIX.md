# P1c — research-draft contract matrix (pre-implementation)

**Date:** 2026-10-25  
**Status:** Evidence-only; **no runtime change authorized**  
**PO path:** P1c (synthetic product → existing research-draft) after explicit AUTHORIZE in Issue #406  
**Baseline:** `master` — `ResearchDraftService`, `POST /api/v1/products/{product_id}/research-draft`, `ResearchAssertion`, `Evidence`, `ProductIntakePanel` P1 skeleton (#455)

Related: [SKIN_INTAKE_BOX_TO_FORM_MAPPING_V1.md](./SKIN_INTAKE_BOX_TO_FORM_MAPPING_V1.md) · [P1B_P1C_DECISION_BRIEF.md](./P1B_P1C_DECISION_BRIEF.md)

---

## 1. Contract facts (server)

| Item | Fact |
|------|------|
| Endpoint | `POST /api/v1/products/{product_id}/research-draft` |
| Auth roles | EDITOR, REVIEWER_QA, PO, ADMIN |
| Body | `{ "assertions": [ ResearchAssertion, ... ] }` |
| Assertion **required** | `claim`, `source_type`, `source_reference` (non-empty strings) |
| Assertion **optional** | `claim_type`, `field`, `source_date`, `evidence_strength`, `market_region`, `notes` |
| Forced on create | `qa_status="PENDING"`, `evidence_status="UNKNOWN"`, notes prefixed with `[RESEARCH_DRAFT actor=…]` |
| Product | Must **already exist**; draft does not create Product or change P4 lifecycle |
| Knowledge | Rebuild runs after create; **PENDING research is excluded** from trusted ProductKnowledge aggregates |
| claim_type allow-list | FACT, MANUFACTURER_CLAIM, EVIDENCE, INFERENCE, UNKNOWN, CONFLICT |
| `field` | Free string at API layer; UI today offers six labels only (see §3) |

**Provenance rule for this matrix:** Putting several unrelated attributes into one `claim` or `notes` blob is **not** treated as structured support. Each testable attribute needs its own assertion **or** is **BLOCKED / needs decision**.

---

## 2. Identity protocol (not research-draft)

These use `ProductCreate` / DuplicateCheck, not research-draft. AT-DEF still applies.

| Input | Server store | FACT without source? |
|-------|--------------|----------------------|
| brand, product_name, product_line, product_id | Product | Operator-entered |
| variant default `clear` | Product if sent | **No — AT-DEF-02** |
| size 50/ml defaults | Product if sent | **No — AT-DEF-01** |
| market_region `IR` default | Product if sent | **No — AT-DEF-03** |
| skin_form_template selector | **Not persisted** on Product today | **Needs decision** to store template code |

---

## 3. Shared boxes → research-draft mapping

Legend: **OK** = contract supports structured row · **PARTIAL** = only as free-text claim with loss of structure · **BLOCKED** = do not implement as P1c store without decision

| Box (UI) | Template | claim (suggested) | field | source_type | source_reference | notes | QA after POST | Readable later? |
|----------|----------|-------------------|-------|-------------|------------------|-------|---------------|------------------|
| منبع / لینک / برچسب | all | Often **is** the source_reference, not a separate claim | — | required on every row | **required** | optional | PENDING | Yes on Evidence |
| نوع منبع | all | N/A — maps to **source_type** on each row | — | **required enum-like string** | — | — | PENDING | Yes |
| منطقه بازار (با شاهد) | all | Optional per-row `market_region` | optional | required | required | may note “operator-selected” | PENDING | Yes if set |
| اهداف پوستی اعلام‌شده | all | Exact operator/source text | `known_use_cases` | required | required | **No P0x IDs** | PENDING | Yes as claim text |
| هشدارها و محدودیت‌ها | all | Warning text | `contraindications` | required | required | — | PENDING | Yes |
| روش مصرف | all | Directions text | `usage_instructions` | required | required | — | PENDING | Yes |
| ترکیبات کلیدی اعلام‌شده | all | Ingredient list text as on source | `ingredients` | required | required | no invented % | PENDING | Yes |
| سایر / اضافات | all | Remainder text | omit or `notes`-heavy claim | required | required | extras | PENDING | Yes as opaque text |

If **source** boxes are empty, **entire assertion is rejected** by server (ValidationError).

---

## 4. Template-specific boxes

### HYDRATING_MOISTURIZER

| Box | Mapping | Verdict |
|-----|---------|---------|
| بافت | No `field` in UI allow-list; would be free-text `claim` only | **PARTIAL** — structure not preserved as typed attribute |
| حس پوستی | same | **PARTIAL** |
| روز / شب | same | **PARTIAL** |
| ادعای آبرسانی + منبع | `field=claimed_benefits` or `manufacturer_claims`, claim=text, claim_type=MANUFACTURER_CLAIM, source_* required | **OK** |

### SUNSCREEN

| Box | Mapping | Verdict |
|-----|---------|---------|
| SPF | Prefer protocol `spf` on Product when known; else claim with field omit or notes | **PARTIAL** if only in claim; identity SPF is not research-draft |
| PA / UVA | free-text claim only | **PARTIAL** |
| نوع فیلتر | free-text claim only | **PARTIAL** |
| مقاومت آب | free-text claim only | **PARTIAL** |
| رنگی / بی‌رنگ | Product `variant` (identity), not research-draft | **Identity path**; AT-DEF-02 |
| صورت / بدن | `known_use_cases` claim text | **OK** as text |

### BRIGHTENING_SPOT

| Box | Mapping | Verdict |
|-----|---------|---------|
| هدف اعلام‌شده | `known_use_cases` | **OK** (text) |
| مواد فعال اعلام‌شده | `ingredients` | **OK** |
| بازه زمانی ادعا | claim text + notes | **PARTIAL** |
| اعداد ادعا (٪، n) | `manufacturer_claims`, claim_type=MANUFACTURER_CLAIM, source required | **OK** as claim — **never auto FACT/VERIFIED** |

### MICELLAR / TONER / CLEANSING_GEL / ANTI_ACNE / EXFOLIANT

| Pattern | Verdict |
|---------|---------|
| Yes/no label attributes (rinse, alcohol, eye area, …) | **PARTIAL** unless encoded as explicit claim sentence + source |
| Actives / acids / frequency / irritation warning | **OK** via `ingredients` / `usage_instructions` / `contraindications` when written as claim text with source |

### OTHER_SKIN

| Box | Verdict |
|-----|---------|
| why_other / free notes | **OK** as claim + notes (opaque) |

---

## 5. Explicit non-destinations

| Target | Allowed in P1c? |
|--------|-----------------|
| ProductKnowledge write from form | **No** |
| Auto P01–P61 | **No** |
| claim_type=FACT for IR/50/clear/smart defaults | **No** |
| Storing `skin_form_template` on Product | **Not in contract today — needs decision** |
| Structured columns for texture/PA/filter | **Not in contract — BLOCKED as structured** |

---

## 6. Acceptance tests — one synthetic product (when AUTHORIZE)

Prereq: operator JWT; product created as **Draft** with obvious test id (e.g. `TEST-P1C-001`); `product_line=SKIN`.

| ID | Test | Expected |
|----|------|----------|
| T-P1C-01 | POST research-draft with one assertion: claim + source_type + source_reference, field=`ingredients` | 201/200; evidence `qa_status=PENDING`; notes contain `[RESEARCH_DRAFT` |
| T-P1C-02 | GET product evidence list | Same claim/field/source readable |
| T-P1C-03 | POST missing source_reference | Validation error; no row |
| T-P1C-04 | GET/rebuild ProductKnowledge | Draft assertion **not** treated as trusted aggregate content solely due to PENDING |
| T-P1C-05 | UI/API must not set claim_type=FACT for default IR/50/clear without operator+source | Pass only if enforced in client rules under AUTHORIZE |
| T-P1C-06 | stated_skin_goals text only | No P0x identifiers written |
| T-P1C-07 | Second assertion `manufacturer_claims` with % figure | Stored PENDING; not VERIFIED |

Existing automated coverage touchpoints: `tests/test_intake_e2e_api_slice_001.py` (research-draft + verify separation).

---

## 7. PR #446 salvage plan (no close yet)

| Step | Action |
|------|--------|
| 1 | Keep #446 open until unique tree is on master |
| 2 | From **current master tip**, branch `docs/homepage-encyclopedia-salvage-…` |
| 3 | Copy unique paths: `docs/homepage/encyclopedia/**` (README, skin/*, stubs) |
| 4 | Merge README links: keep master product-management links **and** encyclopedia links |
| 5 | Open docs-only PR; after merge + verify links, Close #446 as **superseded** with pointer |
| 6 | No parallel Issue; no runtime in salvage PR |

---

## 8. Blockers before P1c code

1. Explicit AUTHORIZE text in Issue #406 (scope = synthetic product + research-draft mapping only).  
2. Client rule: every enabled box → **own** assertion with source_*; refuse submit if source missing.  
3. Accept **PARTIAL** for attribute-like boxes (texture, PA, …) or defer enabling those inputs.  
4. AT-DEF identity defaults remain non-FACT.  
5. #446 unique docs preserved per §7 (can proceed in parallel as docs-only).

---

*End of matrix. Awaiting PO AUTHORIZE before any implementation.*
