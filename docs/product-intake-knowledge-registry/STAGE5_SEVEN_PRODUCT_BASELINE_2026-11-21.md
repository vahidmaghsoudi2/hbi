# Stage 5 — Seven-Product Snapshot / Baseline

**Status:** IN PROGRESS — source-document baseline captured; live Product Master / ProductKnowledge / Evidence readback NOT VERIFIED.  
**Scope:** Read-only snapshot and baseline of the seven canonical product IDs. This is not Stage 6 research reconciliation, not product activation/acceptance, and not authorization for database/API/runtime changes.  
**Baseline commit:** `c8af280349ac33070e606e048a7ccfb57eb87705` (Stage 4 PO-accepted PR head; PR #647 remains unmerged).  
**Source manifest:** `docs/product-intake-knowledge-registry/SEVEN_PRODUCT_EVIDENCE_DRAFT_MANIFEST_V1.json` at blob SHA `51895372efc3b615a5c124de0b7bdd21320ec525`, manifest version `hbi.product-research-draft-manifest.v1`, created 2026-11-09.  
**Snapshot date:** 2026-11-21.  
**Evidence limitation:** Git source/docs are verified. No live application was launched and no DB/API readback or product runtime state was accessed; therefore the live fields below are marked NOT VERIFIED, not inferred.

## Purpose and rules

- Freeze the baseline for exactly seven existing canonical Product IDs (P1–P7).
- Preserve product identity/version boundaries and the manifest's draft-only status.
- Capture assertion inventory, source fields, identity caveats, conflicts, and explicit unknowns.
- Do not treat draft assertions as ProductKnowledge or verified facts.
- No Product Master, Evidence, QA, inventory, lifecycle, customer, database, schema, API, runtime, or deployment writes.
- No direct SQL, launcher, git checkout/fetch, dependency install, or backend start.
- Stage 6 research/evidence reconciliation is NOT started by this baseline.

## Snapshot integrity

| Item | Value |
|---|---|
| Canonical product count | 7 |
| Manifest assertions staged | 24 |
| Manifest assertion state | PENDING / UNVERIFIED (per manifest rules) |
| Live Product Master readback | NOT VERIFIED |
| Live ProductKnowledge readback | NOT VERIFIED |
| Live Evidence readback / QA state | NOT VERIFIED |
| Current physical package / GTIN match | UNKNOWN unless explicitly stated below |
| Inventory / lifecycle / active status | NOT VERIFIED |
| Duplicate resolution against live catalog | NOT VERIFIED |
| Runtime snapshot | NOT PERFORMED |
| Source-file/blob integrity | VERIFIED via GitHub file SHA above |

## Canonical product records

| Dossier | Product ID | Research identity (not physical identity verification) | Draft assertion count | Draft fields |
|---|---|---|---:|---|
| P1 | `HBI-PROD-FE320FA135B843B6` | COSRX The 6 Peptide Skin Booster Serum; 150 ml research target | 4 | ingredients; ingredient_roles; manufacturer_claims; known_use_cases |
| P2 | `HBI-PROD-2CC249240D504453` | Neutrogena Clear & Defend 2% Salicylic Acid Face Wash; 200 ml | 4 | ingredients; manufacturer_claims; ingredient_roles; usage_instructions |
| P3 | `HBI-PROD-C29AA2F410A84CCA` | Garnier Vitamin C Brightening Gel Cleanser; 200 ml Australia source-page version | 3 | ingredients; ingredient_roles; known_use_cases |
| P4 | `HBI-PROD-7F55ED88F41144F1` | SKIN1004 Madagascar Centella Hyalu-Cica Water-Fit Sun Serum SPF50+ PA++++; Korean/international version | 3 | ingredients; ingredient_roles; manufacturer_claims |
| P5 | `HBI-PROD-96788ADC488942E3` | ISDIN FotoUltra 100 Active Unify SPF50+ | 2 | manufacturer_claims; known_use_cases |
| P6 | `HBI-PROD-70EEE418BE0F4DAB` | Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter; historical 100 ml dossier | 3 | ingredients; manufacturer_claims; ingredient_roles |
| P7 | `HBI-PROD-22C55A8223A945A6` | Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum; 30 ml | 5 | ingredients; manufacturer_claims; usage_instructions; ingredient_roles; claimed_benefits |

## Per-product baseline and identity boundaries

### P1 — COSRX The 6 Peptide Skin Booster Serum
- Product ID: `HBI-PROD-FE320FA135B843B6`
- Research target: 150 ml.
- Physical package / GTIN / market-to-source formula match: UNKNOWN.
- Individual peptide concentrations: UNKNOWN.
- Draft assertion inventory: ingredients, ingredient-role inference, manufacturer claims, known use cases (4).
- All staged assertions remain PENDING / UNVERIFIED. Manufacturer efficacy figures are not independently verified.

### P2 — Neutrogena Clear & Defend 2% Salicylic Acid Face Wash
- Product ID: `HBI-PROD-2CC249240D504453`
- Research target: 200 ml; UK is source market only.
- Physical target market/formula match: UNKNOWN; package INCI and warnings not verified.
- Draft assertion inventory: ingredients, manufacturer claims, ingredient-role inference, usage instructions (4).
- The reported “97%” is a manufacturer-page claim, not an acne cure rate.

### P3 — Garnier Vitamin C Brightening Gel Cleanser
- Product ID: `HBI-PROD-C29AA2F410A84CCA`
- Research target: 200 ml; Australia source-page version.
- Physical package market/formula match: UNKNOWN; current package INCI may differ.
- Draft assertion inventory: ingredients, ingredient-role inference, known use cases (3).

### P4 — SKIN1004 Madagascar Centella Hyalu-Cica Water-Fit Sun Serum
- Product ID: `HBI-PROD-7F55ED88F41144F1`
- Research target: SPF50+ PA++++ Korean/international formula.
- Keep distinct from US sunscreen drug-label version; physical package/GTIN match: UNKNOWN.
- Draft assertion inventory: ingredients, ingredient-role inference, manufacturer claims (3).

### P5 — ISDIN FotoUltra 100 Active Unify
- Product ID: `HBI-PROD-96788ADC488942E3`
- Research target: SPF50+.
- Mexico official page is source scope; physical package/market/formula match: UNKNOWN.
- Do not import Spot Prevent or EU/IT formula details.
- No ingredient-role assertion staged because source-matched INCI is not established.
- Draft assertion inventory: manufacturer claims, known use cases (2).

### P6 — Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter
- Product ID: `HBI-PROD-70EEE418BE0F4DAB`
- Historical dossier: 100 ml.
- Distinct from replacement/current Dark Spot Clearing Serum.
- Retailer INCI snapshot does not verify physical package, lot, or exact formula.
- Draft assertion inventory: ingredients, manufacturer claims, ingredient-role inference (3).

### P7 — Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum
- Product ID: `HBI-PROD-22C55A8223A945A6`
- Research target: 30 ml; US official source scope only.
- Physical package market/formula match: UNKNOWN.
- Keep distinct from Anua Azelaic 10 Hyaluron pads.
- Manifest records a conflict: two existing Evidence rows for `field=ingredients`; do not add another conflicting ingredients assertion before human reclassification.
- Draft assertion inventory: ingredients, manufacturer claims, usage instructions, ingredient-role inference, claimed benefits (5).

## Live-system baseline checklist (read-only; not performed)

| Check | Status | Reason |
|---|---|---|
| Product Master record readback for each ID | NOT VERIFIED | No permitted live DB/API read session or readback artifact in this execution |
| Product identity/status/variant/size/market/GTIN | NOT VERIFIED | Source manifest does not establish current stored values |
| ProductKnowledge row and completeness | NOT VERIFIED | No runtime readback |
| Evidence rows, source references, QA verdicts, conflict flags | NOT VERIFIED | Manifest draft inventory is not stored Evidence readback |
| Duplicate/identity comparison | NOT VERIFIED | Requires current catalog readback and physical identity evidence |
| Inventory quantity / sellability | NOT VERIFIED | No live inventory access; do not infer zero or positive stock |
| Lifecycle / activation / approval | NOT VERIFIED | No live record access |
| Data integrity / stale / orphan relations | NOT VERIFIED | Requires read-only current-state inspection |
| Baseline DB backup or snapshot | NOT PERFORMED | No DB access or export authorized/available |

## Baseline conclusions

1. The repository has a canonical seven-product draft research manifest, source blob SHA verified.
2. The manifest contains 24 draft assertions across seven canonical Product IDs.
3. Product identity/version boundaries and explicit UNKNOWNs are documented; P4, P5, P6 and P7 have material formula/market or version caveats.
4. P7 has a known ingredients-field conflict in the manifest; this is a reconciliation item, not resolved in Stage 5.
5. The repository snapshot is NOT a live Product Master / ProductKnowledge / Evidence / inventory baseline. That gap remains BLOCKING for a complete Stage 5 baseline.

## Stage 5 acceptance checklist

- [x] Baseline SHA and source manifest blob SHA pinned.
- [x] Exactly seven canonical Product IDs enumerated.
- [x] All 24 draft assertions inventoried by field.
- [x] Identity/version boundaries and known conflicts captured.
- [x] Source-only snapshot explicitly separated from live data.
- [x] No runtime, DB, API, schema, inventory, lifecycle, or product-data mutation.
- [ ] Live read-only Product Master / ProductKnowledge / Evidence / inventory snapshot obtained with provenance.
- [ ] Catalog duplicate and stored-identity reconciliation verified.
- [ ] PO acceptance of complete baseline.

**Disposition:** Stage 5 deliverable is **PARTIAL / BLOCKED**, not DONE. The source-document baseline is complete, but the missing live readback is a material gap and must not be concealed. Next permitted action should be to obtain an explicitly authorized, isolated read-only data snapshot or approved API readback path and complete the missing checklist; no product changes are implied.
