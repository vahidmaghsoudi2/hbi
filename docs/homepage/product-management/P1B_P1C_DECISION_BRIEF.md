# Decision brief — P1b vs P1c (and PR #446)

**Date:** 2026-10-25  
**Author role:** Workstream manager (Grok), read-only vs runtime  
**Authority:** Issue #406 only for AUTHORIZE  
**Code baseline:** `master` — `ProductIntakePanel.tsx` (P1 skeleton PR #455), `app/interface/schemas.py` (`ProductCreate`, `ResearchAssertion`), `Product` / `Evidence` / `ProductKnowledge` models  
**Related map:** [SKIN_INTAKE_BOX_TO_FORM_MAPPING_V1.md](./SKIN_INTAKE_BOX_TO_FORM_MAPPING_V1.md)

No code, API, DTO, schema, DB, or product registration in this document.

---

## A. PR #446 — live disposition (not blind Update / not blind Close)

| Observation | Evidence |
|-------------|----------|
| State | Open; `mergeable_state: dirty` |
| Compare to `master` | **Diverged** (branch ahead with encyclopedia tree; master ahead with later homepage/product-management docs) |
| `docs/homepage/encyclopedia/**` on `master` | **Absent (404)** — entire hub is unique to #446 branch |
| Unique value on #446 | Encyclopedia menu mirror; `skin/README.md` team boundaries + test readiness checklist; `PRODUCTS.md` / `DECISIONS.md`; other submenu stubs |
| Conflict hotspot | `docs/homepage/README.md` edited on both sides (product-management links on master vs encyclopedia links on branch) |

**Recommendation**

1. **Do not** force-push or blind Update branch without reading the README conflict.
2. **Do not** Close #446 until unique encyclopedia/skin coordination text is **re-homed** onto current `master` (clean branch from tip of master + copy unique files + merged README links), then Close #446 as **superseded** with a link to the salvage PR.
3. Template SoR remains `docs/homepage/product-management/` — encyclopedia only **links**, does not duplicate the nine-template field map.

---

## B. What the form already supports (facts)

### Product create (`ProductCreate`)

Required: `product_id`, `brand`, `product_name`, `product_line`.  
Optional identity: `variant`, `size_value`, `size_unit`, `barcode_gtin`, `market_region`, `country_of_origin`, `packaging_version`.  
Optional intake hints: `knowledge_use_cases`, `knowledge_evidence_claim`, `knowledge_evidence_source_reference` (not full template payload).  
`duplicate_check_id` when needed.

**Not on ProductCreate:** per-box template attributes (texture, PA, water resistance, etc.), `skin_form_template` code.

### Research draft (`POST .../research-draft`, `ResearchAssertion`)

Required per row: `claim`, `source_type`, `source_reference`.  
Optional: `claim_type`, `field`, `source_date`, `evidence_strength`, `market_region`, `notes`.

UI `field` options today: `claimed_benefits` | `known_use_cases` | `ingredients` | `contraindications` | `usage_instructions` | `manufacturer_claims`.

Created evidence is **draft/PENDING** path — not ProductKnowledge and not VERIFIED by default.

### ProductKnowledge

Rebuild **read model** from eligible Evidence only. **Not** a form write target for template boxes.

### P1 skeleton (already on master)

When `product_line === "SKIN"`: nine templates + shared labels; inputs **disabled**, empty, **not POSTed**.

### Defaults (must stay in acceptance tests)

`EMPTY` / `completeFromIntro`: `variant="clear"`, `size_value=50`, `size_unit="ml"`, `market_region="IR"` (IR forced again after smart complete). Must not become FACT without source or explicit operator choice.

---

## C. Option P1b — local enable (no official store)

**Intent:** Operators (product team + skin-problem observers) can **type and validate** box values in the UI for dry-run / coordination tests.

| Dimension | Detail |
|-----------|--------|
| **Scope of change** | Frontend only: enable inputs; optional `sessionStorage`/`localStorage` keyed by product_id+template; still **no** new API fields |
| **Data destination** | Browser only (or none). **Not** Product, Evidence, or ProductKnowledge |
| **Limits** | Cannot prove server readback; two browsers diverge; not audit-grade for #406 characteristics bank |
| **Acceptance** | Boxes editable when SKIN+template selected; values survive refresh if local store used; create Draft still ignores box payload; AT-DEF-01…03 still apply to identity protocol; no P0x auto-link; no PK write |
| **Tests** | Manual/UI: select each of 9 templates; fill shared box; confirm disabled path no longer blocks typing; confirm network tab create body has no template payload; confirm IR/50/clear still flagged in test notes as non-FACT |
| **Risk** | Low to server integrity; medium to false confidence (“we saved features”) if UI does not label **پیش‌نویس محلی — ذخیرهٔ رسمی نیست** |

**Fit for “real joint test”:** Good for **UX and team checklist** only. Weak for **evidence-grade** joint test.

---

## D. Option P1c — official research-draft path

**Intent:** Map filled boxes to **existing** `ResearchAssertion` rows after a product_id exists (create Draft first, or edit existing Draft).

| Dimension | Detail |
|-----------|--------|
| **Scope of change** | Frontend (and only if needed, thin client mapping). **No** schema/DB if we only use existing research-draft contract |
| **Data destination** | `Evidence` via `POST /products/{id}/research-draft` — one assertion per box (or batched). `field` from allow-list; free-text attributes → `claim` + `notes`; always require `source_type` + `source_reference` |
| **Contract support** | **Yes** for claim/source/field/notes/market_region. **No** first-class columns for texture/PA/etc. — those stay inside `claim`/`notes` until a later AUTHORIZE |
| **Limits** | Product must exist first; template code still not stored on Product unless later AUTHORIZE; PENDING evidence does not populate trusted PK; operator must not mark FACT without basis |
| **Acceptance** | Given Draft product + SKIN + template: submitting boxes creates Evidence rows with PENDING QA; missing source blocks submit; efficacy numbers only as MANUFACTURER_CLAIM/draft; stated_skin_goals → `known_use_cases` text only; list evidence readback matches; AT-DEF defaults not auto-asserted as FACT in claims |
| **Tests** | Integration: create test product → fill two shared boxes with source → research-draft → GET evidence; negative: empty source_reference → error; negative: no product_id → blocked; confirm PK not updated until verify path |
| **Risk** | Medium if UI implies verification; low if labeled پیش‌نویس پژوهشی. Higher operational value for two-team test |

**Fit for “real joint test”:** **Stronger** path — both teams can inspect **server-side** draft claims without activation/QA bypass.

---

## E. Recommendation to Product Owner (decision only)

| Priority | Recommendation |
|----------|----------------|
| 1 | **Salvage #446** unique encyclopedia/skin docs onto current master (separate docs PR), then Close #446 as superseded. |
| 2 | For the **first joint practical test**, prefer **P1c** on a **synthetic** product only, after explicit AUTHORIZE — uses real research-draft contract already in API. |
| 3 | Use **P1b** only if you want a same-day UX dry-run with **zero** server writes of box content; label UI as non-official. |
| 4 | Do **not** re-build P1 skeleton (#455 done). |
| 5 | Do **not** write ProductKnowledge from the form. |

**Suggested AUTHORIZE text (if you choose P1c):**  
«مجاز است: فعال‌سازی باکس‌های قالب پوست در ProductIntakePanel و ارسال محتوای باکس‌ها به research-draft موجود برای یک محصول آزمایشی؛ بدون schema/DB جدید؛ بدون FACT خودکار برای IR/50/clear؛ بدون P01–P61؛ بدون QA/activation.»

**Suggested AUTHORIZE text (if you choose P1b):**  
«مجاز است: فقط فعال‌سازی ورودی باکس‌ها و ذخیرهٔ محلی مرورگر؛ بدون POST باکس به API.»

Until one of these (or a hybrid) is recorded in Issue #406, **no runtime change**.

---

## F. Essential decisions for you (checklist)

1. [ ] P1b, P1c, hybrid (P1b then P1c), or defer UI enablement?  
2. [ ] Approve salvage plan for #446 encyclopedia tree onto master?  
3. [ ] Confirm AT-DEF-01…03 remain blocking for “FACT” interpretation?

---

*End of brief. Awaiting PO decision before any implementation.*
