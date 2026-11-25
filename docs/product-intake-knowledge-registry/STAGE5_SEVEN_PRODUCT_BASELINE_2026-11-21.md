# Stage 5 — Seven-Product Snapshot / Baseline

**Status:** REPOSITORY BASELINE COMPLETE — ready for PO review. Live operational readback remains explicitly NOT VERIFIED and is not fabricated.  
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
- [x] Repository-backed read-only baseline consolidated from the seven-product draft manifest and supporting GitHub records.
- [x] Product-specific source URLs, claim taxonomy, source-market boundaries, and evidence limitations inventoried for all 24 assertions.
- [x] Existing seed/catalog records checked and separated from these seven canonical IDs (they are a different set of legacy ISDIN records).
- [ ] Live Product Master / ProductKnowledge / Evidence / inventory readback: NOT VERIFIED (live operational access is unavailable in this GitHub-only pass; no inference made).
- [ ] PO acceptance.

**Disposition:** Stage 5's GitHub-backed snapshot/baseline deliverable is **DONE / READY FOR PO REVIEW**. All repository evidence relevant to these seven product dossiers has been inspected and captured below. Live operational DB/API state remains **NOT VERIFIED** and is clearly separated; this does not invalidate the source-repository baseline. Stage 6 remains NOT STARTED.


## Repository evidence inventory — all 24 staged assertions

This section transcribes the current manifest's staged claims for traceability. It is not an independent verification of the linked sources or physical stock. Every staged assertion remains draft and unverified unless the manifest says otherwise; in this manifest all strengths are UNVERIFIED. Assertions are intentionally preserved as claims or inferences, not upgraded to facts.

### P1 — COSRX The 6 Peptide Skin Booster Serum; 150 ml research target

**Product ID:** `HBI-PROD-FE320FA135B843B6`  
**Source market:** not specified  
**Identity limits:** `Physical package/GTIN/market-to-source formula match UNKNOWN`; `Individual peptide concentrations UNKNOWN`


**Assertion ingredients** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `not specified`

The official manufacturer page lists the peptide ingredients Acetyl Hexapeptide-8, Copper Tripeptide-1, sh-Polypeptide-121, Dipeptide Diaminobutyroyl Benzylamide Diacetate, Oligopeptide-68 and Palmitoyl Tripeptide-8, and also highlights niacinamide, hyaluronic acid, N-acetylglucosamine and allantoin. This is a source-page ingredient snapshot, not verification of the physical 150 ml package or a complete current INCI.

Source: https://www.cosrx.com/collections/all/products/the-6-peptide-skin-booster-serum

**Assertion ingredient_roles** · `INFERENCE` · Source type: `ANALYST_REVIEW` · Strength: `UNVERIFIED` · Market: `not specified`

[{"ingredient":"Six-peptide complex (individual peptides listed in ingredients assertion)","role":"CLAIM-LINK"},{"ingredient":"Niacinamide","role":"SUPPORT"},{"ingredient":"Hyaluronic acid / humectant group","role":"SUPPORT"},{"ingredient":"Allantoin","role":"SUPPORT"}]

Source: https://www.cosrx.com/collections/all/products/the-6-peptide-skin-booster-serum

Notes: Analyst role mapping from source-disclosed ingredients and product positioning only; not proof of finished-serum efficacy or exact formula presence in the physical unit.

**Assertion manufacturer_claims** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `not specified`

The manufacturer reports +162.5% deep moisture, +76.4% texture, +40.1% clarity, +24.5% radiance and +22.2% density based on 20 subjects at Dermacosmetic Skin Science Laboratory Co., Ltd, 2023-09-18 to 2023-10-31. Full protocol, comparator, instruments, analysis and independent replication are not available in the reviewed public page; treat all figures as manufacturer-reported only.

Source: https://www.cosrx.com/collections/all/products/the-6-peptide-skin-booster-serum

**Assertion known_use_cases** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `not specified`

Manufacturer positioning: skin conditioning/booster use with moisture, texture and radiance claims. These are cosmetic positioning statements, not a validated treatment indication.

Source: https://www.cosrx.com/collections/all/products/the-6-peptide-skin-booster-serum

### P2 — Neutrogena Clear & Defend 2% Salicylic Acid Face Wash; 200 ml

**Product ID:** `HBI-PROD-2CC249240D504453`  
**Source market:** UK  
**Identity limits:** `UK is the research source market only; physical target market and formula match UNKNOWN`; `Package INCI and warnings not verified`


**Assertion ingredients** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `UK`

UK manufacturer-page INCI snapshot: Aqua, Cocamidopropyl Hydroxysultaine, Sodium Methyl Cocoyl Taurate, Glycerin, Salicylic Acid, Sodium Hydrolyzed Potato Starch Dodecenylsuccinate, C12-15 Alkyl Lactate, Panthenol, Cocamidopropyl PG-Dimonium Chloride Phosphate, Disodium Tetrapropenyl Succinate, PEG-120 Methyl Glucose Dioleate, Sodium Chloride, Disodium EDTA, Citric Acid, Sodium Hydroxide, Tocopherol, Benzalkonium Chloride, Parfum. Manufacturer warns product/ingredients may change; physical package label remains authoritative.

Source: https://www.neutrogena.co.uk/skincare/cleansers-washes/clear-and-defend-daily-wash

**Assertion manufacturer_claims** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `UK`

The UK manufacturer page declares 2% salicylic acid and reports 97% noticed fewer new spots in four weeks, based on clinical grading in 34 subjects. Full protocol, control and absolute change are not disclosed in the reviewed page. This is not a 97% acne cure rate and is not proof that the physical target unit is UK-market.

Source: https://www.neutrogena.co.uk/skincare/cleansers-washes/clear-and-defend-daily-wash

**Assertion ingredient_roles** · `INFERENCE` · Source type: `ANALYST_REVIEW` · Strength: `UNVERIFIED` · Market: `UK`

[{"ingredient":"Salicylic Acid 2% (manufacturer-declared on UK page)","role":"CORE"},{"ingredient":"Cleansing surfactant system","role":"CORE"},{"ingredient":"Glycerin","role":"SUPPORT"},{"ingredient":"Panthenol","role":"SUPPORT"},{"ingredient":"Parfum","role":"RISK"}]

Source: https://www.neutrogena.co.uk/skincare/cleansers-washes/clear-and-defend-daily-wash

Notes: CORE surfactant system means cleansing function, not acne efficacy. Parfum is a context-sensitive review flag, not a contraindication.

**Assertion usage_instructions** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `UK`

UK source page directions: wet face, massage gently, avoid eyes and mouth, rinse; page mentions twice-daily use. These are source-page instructions only and must not replace the physical package directions for the unconfirmed target unit.

Source: https://www.neutrogena.co.uk/skincare/cleansers-washes/clear-and-defend-daily-wash

### P3 — Garnier Vitamin C Brightening Gel Cleanser; 200 ml Australia source-page version

**Product ID:** `HBI-PROD-C29AA2F410A84CCA`  
**Source market:** AU  
**Identity limits:** `Australia is source-page market, not confirmed physical-unit market`; `Current package INCI may differ; package label authoritative`


**Assertion ingredients** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `AU`

Australian manufacturer-page INCI snapshot: AQUA/WATER, SODIUM LAURETH SULFATE, COCO-BETAINE, SODIUM CHLORIDE, GLYCERIN, CITRUS LEMON FRUIT EXTRACT / LEMON FRUIT EXTRACT, PPG5-CETETH-20, SODIUM HYDROXIDE, ASCORBYL GLUCOSIDE, CITRIC ACID, PANTHENOL, POLYQUATERNIUM-7, TOCOPHERYL ACETATE, SODIUM BENZOATE, SALICYLIC ACID, LINALOOL, LIMONENE, BENZYL SALICYLATE, PARFUM / FRAGRANCE. Manufacturer says ingredient lists may change and package label should be checked.

Source: https://www.garnier.com.au/about-our-brands/skin-active/garnier-skin-active-vitamin-c-brightening-gel-cleanser-200ml

**Assertion ingredient_roles** · `INFERENCE` · Source type: `ANALYST_REVIEW` · Strength: `UNVERIFIED` · Market: `AU`

[{"ingredient":"Cleansing surfactant system","role":"CORE"},{"ingredient":"Ascorbyl Glucoside","role":"CLAIM-LINK"},{"ingredient":"Lemon extract","role":"CLAIM-LINK"},{"ingredient":"Glycerin","role":"SUPPORT"},{"ingredient":"Panthenol","role":"SUPPORT"},{"ingredient":"Tocopheryl Acetate","role":"SUPPORT"},{"ingredient":"Parfum / Linalool / Limonene / Benzyl Salicylate","role":"RISK"}]

Source: https://www.garnier.com.au/about-our-brands/skin-active/garnier-skin-active-vitamin-c-brightening-gel-cleanser-200ml

Notes: Ascorbyl Glucoside is a vitamin C derivative, not L-ascorbic acid. Rinse-off exposure is distinct from leave-on products. Fragrance markers are review flags, not automatic contraindications.

**Assertion known_use_cases** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `AU`

Manufacturer positioning is a rinse-off Vitamin C brightening gel cleanser. No product-specific clinical endpoint establishing acne, comedone or pigmentation treatment was verified in the research ledger.

Source: https://www.garnier.com.au/about-our-brands/skin-active/garnier-skin-active-vitamin-c-brightening-gel-cleanser-200ml

### P4 — SKIN1004 Madagascar Centella Hyalu-Cica Water-Fit Sun Serum SPF50+ PA++++; Korean/international version

**Product ID:** `HBI-PROD-7F55ED88F41144F1`  
**Source market:** INTERNATIONAL_KOREAN  
**Identity limits:** `Keep international/Korean formula separate from US sunscreen drug-label version`; `Physical package and GTIN match UNKNOWN`


**Assertion ingredients** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `INTERNATIONAL_KOREAN`

International/Korean manufacturer-page INCI snapshot: Water, Dibutyl Adipate, Propanediol, Diethylamino Hydroxybenzoyl Hexyl Benzoate, Polymethylsilsesquioxane, Ethylhexyl Triazone, Methylene Bis-Benzotriazolyl Tetramethylbutylphenol, Niacinamide, Coco-Caprylate/Caprate, Caprylyl Methicone, Diethylhexyl Butamido Triazone, Glycerin, 1,2-Hexanediol, Butylene Glycol, Pentylene Glycol, Behenyl Alcohol, Poly C10-30 Alkyl Acrylate, Polyglyceryl-3 Methylglucose Distearate, Decyl Glucoside, Tromethamine, Carbomer, Acrylates/C10-30 Alkyl Acrylate Crosspolymer, Sodium Stearoyl Glutamate, Polyacrylate Crosspolymer-6, Ethylhexylglycerin, Adenosine, Xanthan Gum, Centella Asiatica Extract, t-Butyl Alcohol, Sodium Hyaluronate, Betula Platyphylla Japonica Bark Extract, Tocopherol, Hydrolyzed Hyaluronic Acid, Camellia Sinensis Leaf Extract, Ginkgo Biloba Leaf Extract, Brassica Oleracea Italica (Broccoli) Sprout Extract, Camellia Japonica Leaf Extract, Eruca Sativa Leaf Extract, Medicago Sativa (Alfalfa) Extract, Triticum Vulgare (Wheat) Sprout Extract, Inositol, Hyaluronic Acid. This is the international source-page formula only, not proof of physical package match.

Source: https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-spf50-pa?country=GB

**Assertion ingredient_roles** · `INFERENCE` · Source type: `ANALYST_REVIEW` · Strength: `UNVERIFIED` · Market: `INTERNATIONAL_KOREAN`

[{"ingredient":"International formula UV-filter system","role":"CORE"},{"ingredient":"Niacinamide","role":"SUPPORT"},{"ingredient":"Glycerin","role":"SUPPORT"},{"ingredient":"Sodium Hyaluronate / Hydrolyzed Hyaluronic Acid / Hyaluronic Acid","role":"SUPPORT"},{"ingredient":"Centella Asiatica Extract","role":"SUPPORT"}]

Source: https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-spf50-pa?country=GB

Notes: CORE refers to UV protection function, not treatment of existing pigmentation. No US sunscreen active percentages are transferred to this dossier.

**Assertion manufacturer_claims** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `INTERNATIONAL_KOREAN`

The manufacturer identifies this international/Korean version as SPF50+ PA++++. Product-specific independent RCT evidence for this exact formula has not been established in the reviewed dossier. Do not merge with the separate US Water-Fit Sun Serum UV drug-label formula.

Source: https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-spf50-pa?country=GB

### P5 — ISDIN FotoUltra 100 Active Unify SPF50+

**Product ID:** `HBI-PROD-96788ADC488942E3`  
**Source market:** MX  
**Identity limits:** `Mexico official page is the research source; exact target package/market/formula match UNKNOWN`; `Do not import Spot Prevent data or EU/IT formula details`; `No ingredient-role assertion is staged because the exact source-matched INCI is not established for this Product record.`


**Assertion manufacturer_claims** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `MX`

The Mexico manufacturer page reports a 22% reduction in spot intensity and a 15% reduction in spot area in 31 subjects aged 35–65 after 28 and 84 days. The public source does not disclose the full protocol, control, blinding, instruments, statistical analysis or original report. These are manufacturer-reported results, not independently verified proof and not transferable to ISDIN Spot Prevent.

Source: https://www.isdin.com/mx/p/fotoultra-active-unify-spf-50/1160

**Assertion known_use_cases** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `MX`

Manufacturer positioning is high-protection sunscreen with a cosmetic spot/uneven-tone positioning. The disclosed 31-subject endpoints remain manufacturer-reported; no independent exact-SKU study was verified.

Source: https://www.isdin.com/mx/p/fotoultra-active-unify-spf-50/1160

### P6 — Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter; historical 100 ml dossier

**Product ID:** `HBI-PROD-70EEE418BE0F4DAB`  
**Source market:** UK  
**Identity limits:** `Historical product is distinct from the replacement/current Dark Spot Clearing Serum`; `Retailer INCI snapshot does not verify physical package, lot or exact formula`


**Assertion ingredients** · `EVIDENCE` · Source type: `RETAILER` · Strength: `UNVERIFIED` · Market: `UK`

Harrods UK retailer listing for the historical 100 ml Even Better Clinical Radical Dark Spot Corrector + Interrupter displays this INCI snapshot: WaterAquaEau, Cyclopentasiloxane, Dimethicone, Polysilicone-11, Isododecane, Butylene Glycol, Ascorbyl Glucoside, Peg-10 Dimethicone, Peg-6, Morus Bombycis (Mulberry) Root Extract, Scutellaria Baicalensis Root Extract, Camellia Sinensis Leaf Extract, Cucumis Sativus (Cucumber) Fruit Extract, Saccharomyces Lysate Extract, Hordeum Vulgare (Barley) Extract, Salicylic Acid, Triticum Vulgare (Wheat) Germ Extract, Cholesterol, Oryza Sativa (Rice) Bran Extract, Squalane, Acetyl Glucosamine, Sodium Hyaluronate, Caffeine, Isohexadecane, Betula Alba (Birch) Bark Extract, Trametes Versicolor Extract, Sodium RNA, Glycyrrhetinic Acid, Dimethoxytolyl Propylresorcinol, Di-C12-18 Alkyl Dimonium Chloride, Helianthus Annuus (Sunflower) Seedcake, Yeast Extract, Caprylyl Glycol, Propylene Glycol Dicaprate, Ammonium Acryloyldimethyltaurate/VP Copolymer, Acrylamide/Sodium Acryloyldimethyltaurate Copolymer, Polysorbate 20, Tocopheryl Acetate, Polysorbate 80, Tromethamine, Sodium Hydroxide, Hexylene Glycol, Disodium EDTA, Sodium Benzoate, Sodium Metabisulfite, Sodium Sulfite, Phenoxyethanol, Yellow 6 (CI 15985), Yellow 5 (CI 19140). This is a historical retailer snapshot, not a physical package label; exact market/lot/formula match remains unverified. Keep it separate from the replacement Dark Spot Clearing Serum.

Source: https://www.harrods.com/en-gb/p/clinique-even-better-clinical-radical-dark-spot-correctorand-interrupter-100ml-000000000006795757

**Assertion manufacturer_claims** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `UK`

The historical product page reports 39% visible reduction in dark spots in 12 weeks from clinical testing on 52 women. Separate consumer testing on a larger group reports different endpoints and must not be conflated. The public page does not establish randomization, blinding, comparator or full protocol. Do not transfer current replacement-serum outcomes to the historical 100 ml dossier.

Source: https://www.clinique.com/product/4034/68008/skincare/serum/even-better-clinicaltm-radical-dark-spot-corrector-interrupter

**Assertion ingredient_roles** · `INFERENCE` · Source type: `ANALYST_REVIEW` · Strength: `UNVERIFIED` · Market: `UK`

[{"ingredient":"Ascorbyl Glucoside","role":"CLAIM-LINK"},{"ingredient":"Dimethoxytolyl Propylresorcinol","role":"CLAIM-LINK"},{"ingredient":"Acetyl Glucosamine","role":"CLAIM-LINK"},{"ingredient":"Silicone base and volatile carriers","role":"TECH"}]

Source: https://www.clinique.com/product/4034/68008/skincare/serum/even-better-clinicaltm-radical-dark-spot-corrector-interrupter

Notes: Historical formula only. Ingredient roles are not efficacy proof, and no concentration is inferred.

### P7 — Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum; 30 ml

**Product ID:** `HBI-PROD-22C55A8223A945A6`  
**Source market:** US  
**Identity limits:** `US official source is a source scope only; physical package market/formula match UNKNOWN`; `Keep separate from Anua Azelaic 10 Hyaluron pads`; `Existing two Evidence rows conflict on field=ingredients; do not add another conflicting ingredients assertion before human reclassification`


**Assertion ingredients** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `US`

Official US serum-page ingredient declaration includes Azelaic Acid, Panthenol, Betaine Salicylate, Glycerin, Allantoin, Niacinamide, Centella-related ingredients, Sodium Hyaluronate, Squalane, Zinc PCA and Ceramide NP. This is a partial source-bound ingredient summary, not a complete verbatim INCI; the full package INCI remains UNKNOWN until matched to a physical label.

Source: https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum

**Assertion manufacturer_claims** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `US`

The manufacturer declares 10% azelaic acid for this serum and labels testing as non-comedogenic/low-irritation. The public page does not disclose complete methodology for those test labels. Do not infer clinical treatment of acne, rosacea, PIH or persistent redness from ingredient presence or these labels.

Source: https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum

**Assertion usage_instructions** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `US`

Manufacturer advises gradual introduction, beginning 1–2 times weekly and increasing as tolerated (up to twice daily per the source-page routine guidance), with daytime SPF use. Physical package directions remain authoritative.

Source: https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum

**Assertion ingredient_roles** · `INFERENCE` · Source type: `ANALYST_REVIEW` · Strength: `UNVERIFIED` · Market: `US`

[{"ingredient":"Azelaic Acid 10% (manufacturer-declared)","role":"CORE"},{"ingredient":"Panthenol","role":"SUPPORT"},{"ingredient":"Allantoin","role":"SUPPORT"},{"ingredient":"Niacinamide","role":"SUPPORT"},{"ingredient":"Glycerin / Sodium Hyaluronate","role":"SUPPORT"},{"ingredient":"Centella components","role":"SUPPORT"},{"ingredient":"Squalane / Ceramide NP","role":"SUPPORT"}]

Source: https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum

Notes: Role mapping is a cautious ingredient/function interpretation, not finished-product clinical efficacy. Existing conflicting evidence rows require review and reclassification before any accepted knowledge rebuild.

**Assertion claimed_benefits** · `MANUFACTURER_CLAIM` · Source type: `MANUFACTURER` · Strength: `UNVERIFIED` · Market: `US`

A separate Anua routine/claim page reports that 90% of participants agreed the appearance of red troubled spots improved, attributed to a 2026 Anua US clinical study. Public methodology, sample details, comparator, validated endpoint and statistical report are not disclosed. Do not transfer evidence from the separate Anua azelaic-acid pads to this serum.

Source: https://pages.anua.com/solutions/redness-prone-routine-sensitive-skin

Notes: Separate official routine-page manufacturer result. Kept in a distinct ProductKnowledge domain from the product-page 10%/tolerability claims to avoid merging unlike assertions into one field. Protocol remains undisclosed.

## Cross-check against legacy seed/catalog records

The GitHub repository also contains `data/seed_products.json`, `data/seed_evidence.json`, and historical records `docs/01_product_records/PRODUCT_A_RECORD.md` through `PRODUCT_D_RECORD.md`. These describe four separate ISDIN products with legacy IDs: `ISDIN-FOTOUTRA100-50ML`, `ISDIN-FOTOUTRA100COLOR-50ML`, `ISDIN-FUSIONWATERMAGIC-50ML`, and `ISDIN-AGEREVERSEDAY-50ML`. They are **not** the seven canonical HBI-PROD IDs in this baseline and must not be conflated or used as substitutes. Those legacy files record inventory confirmation on 2026-08-23, count 3 each, but that is historical file evidence, not current inventory readback. Their barcode, market and packaging version are UNKNOWN. The D record explicitly treats SPF as a project-record/PO-confirmation value.

## Source audit disposition

- The repository contains a comprehensive draft manifest for all seven IDs and a regression test that asserts exact canonical scope, 24 assertion count, per-product counts, and draft-only boundary including P7 review conflict.
- This confirms the existence and integrity checks of the GitHub source package; it does **not** prove test execution in this pass, nor live operational record state.
- Source assertions and research dossiers are reusable for Stage 6. No re-research of already recorded assertions is authorized by this snapshot; Stage 6 should focus only on gaps, conflicts, market/formula identity verification, and upgrading evidence where needed.


## Operational-state snapshot sourced from existing GitHub read-only records

**Source date:** 2026-11-16 (GitHub Issue #283 comment #6924295875, PO handoff); cross-checked against the older detailed snapshot report in Issue #283 comment #6902085054. This is an existing operator-supplied read-only snapshot, not a fresh query performed by this session. The exact query timestamp, snapshot file/hash, and row-level exports are not present in those comments; freshness is therefore NOT VERIFIED.

| Operational entity | Reported snapshot | Boundary |
|---|---|---|
| Product | 7 rows, one per canonical P1–P7 | PO confirmed product identities; no row-level ID/state export attached in the referenced comment |
| ProductKnowledge | 7 rows | Reported evidence_status=UNKNOWN, knowledge_confidence=0.0 in detailed source snapshot |
| Evidence | 25 rows | Detailed snapshot: 19 PENDING, 6 NEEDS_REVIEW; all 25 evidence_status=UNKNOWN, strength UNVERIFIED, conflict_status NONE. Later PO handoff summary says all 25 are PENDING and notes 2 Anua conflict rows. These summaries conflict; current exact row state is NOT VERIFIED without the read-only exporter output. |
| Inventory | 12 units per product / 84 total | PO accepted planning quantity and use of system quantity for consultation; not a fresh database read. Do not ask for stock re-confirmation or reclassification as a V1 blocker. |
| Product lifecycle / QA | All 7 reportedly DRAFT / NEEDS_REVIEW / PENDING | Source summary only; not fresh row-level readback. |

**Scope decisions that supersede older blockers:** the seven physical identities are PO-confirmed; inventory planning is 12 each / 84; Anua is settled and must not be re-cleaned/reclassified absent a newly observed concrete defect. V1 evidence scope is official manufacturer disclosure and package text; no independent clinical research detour. COSRX scope is only The 6 Peptide Skin Booster Serum. These decisions are recorded in Issue #406 comment #6955477364.

**Manifest-count reconciliation:** the baseline pinned here is the master manifest with 24 assertions. Later open PR #594 proposes the manufacturer/package-only manifest (25 assertions in the 2026-11-18 checkpoint; 27 in an earlier PR state). It is not merged and is not treated as current operational data. The 25 reported Evidence rows are not presumed to map one-to-one to any manifest version.

**Stage 5 disposition:** repository baseline plus existing operational-state snapshot summary is documented and reusable: DONE / READY FOR PO REVIEW. Exact current freshness and row-level reconciliation remain clearly marked NOT VERIFIED, and are not falsely promoted. Stage 6 remains NOT STARTED pending Stage 5 PO acceptance.


---

## 2026-11-22 — Follow-up read-only local database and runtime audit

**Purpose:** continue the Stage 5 live-state investigation using the local read-only diagnostic outputs supplied during the PO execution session. This addendum does not convert any local database artifact into the operational database without a runtime-to-file/endpoint provenance link.

### Runtime configuration and process evidence

- The inspected application configuration in `app/database.py` uses `DATABASE_URL` when supplied and otherwise falls back to `sqlite:///./data/hbi.db`; the relative SQLite path resolves from the process working directory.
- No `DATABASE_URL` was present in the inspected Process, User, or Machine environment scopes.
- No matching HBI runtime process, HBI-named Windows service, listener owned by a matching runtime process, or HBI-named scheduled task was found during the local scan.
- The inspected source checkouts did not contain a populated `data/hbi.db`; two related worktree database files were present but had zero operational records.
- These are bounded local observations at scan time. They do not rule out a remote/cloud/container runtime, a runtime on another machine, or a stopped service.

### Local database artifacts inspected (read-only)

| Artifact label | SHA-256 | Product | ProductKnowledge | Evidence | Inventory | Other relevant counts | Integrity |
|---|---|---:|---:|---:|---:|---|---|
| `MAIN_REPO` local repository DB | `86ca03555529c3a2674d8b41985539de7c7945bd22bbbc3abd0ea23c9ac2ff32` | 7 | 1 | 0 | 7 | ProductMutationLog 7; AdminCredential 1; UserRole 2; DuplicateCheckAudit 14 | `ok` |
| `SAFETY_BACKUP` dated safety backup | `e34ac2c7ac92f53f17cf93af9d7251b0350ad527cad758d89bf8f23436383c6f` | 7 | 7 | 25 | 7 | EvidenceMutationLog 25; Customer 9; Case 1; DuplicateCheckAudit 21; AdminCredential 5; UserRole 5 | `ok` |
| `PPL_WORKTREE` | `87e7e7a9d34c2097d51705c981933d58278c29b53910952bc3dcdde27bf11db6` | 0 | 0 | 0 | 0 | ProductProblemLink schema present; no operational rows | `ok` |
| `SKIN_WORKTREE` | `4debd3ace360c6a694559491db9f1447be52ee50c0254c781fdb452a35449be6` | 0 | 0 | 0 | 0 | No operational rows | `ok` |

All four inspected SQLite files passed `PRAGMA integrity_check`; foreign-key checks reported no violations. No database write, migration, seed, import, or export was performed in this follow-up.

### Data interpretation and conflicts

1. `MAIN_REPO` is not a complete seven-product knowledge/evidence snapshot: only one ProductKnowledge row exists and Evidence is zero. Its seven Product rows are DRAFT / NEEDS_REVIEW / QA PENDING.
2. `SAFETY_BACKUP` is the most data-complete local artifact among those inspected: seven Product rows, seven ProductKnowledge rows, 25 Evidence rows, and seven Inventory rows. However, all seven products remain DRAFT / NEEDS_REVIEW / QA PENDING; all seven knowledge-confidence values are zero; Evidence status is UNKNOWN for six products and CONFLICT for Anua. This is not accepted/verified product knowledge.
3. The safety-backup filename includes `before-productknowledge-write-20261112`, yet its contents include seven ProductKnowledge rows. Filename and contents therefore have unresolved provenance ambiguity. The filename must not be used to infer the database's point-in-time state.
4. The seven Product IDs in `MAIN_REPO` differ from the seven IDs in `SAFETY_BACKUP`, despite matching the same logical seven product names/brands. They represent distinct data generations; they are not interchangeable copies and must not be joined by product name.
5. The safety backup's ProductKnowledge rows link to their corresponding Product rows in that same file, and the 25 Evidence rows are associated with the seven products. This establishes internal linkage in that backup only, not operational use.
6. No credentials, credential values, connection strings, or sensitive row contents were inspected or recorded. Only table counts and integrity outcomes are included here.

### Stage 5 disposition after this audit

- **Local database candidates:** VERIFIED EXISTING as files with the table counts and hashes above.
- **Operational database identity:** NOT VERIFIED.
- **Runtime-to-database provenance:** NOT VERIFIED.
- **Live Product Master / ProductKnowledge / Evidence / inventory readback:** NOT VERIFIED.
- **PO-approved product acceptance or sellability:** NOT VERIFIED; the observed local product rows are still DRAFT / NEEDS_REVIEW / PENDING.
- **Stage 5:** remains **BLOCKED / NOT VERIFIED** for the operational readback criterion.

The decisive missing evidence is not another directory listing. It is an authoritative deployment/runtime reference that identifies the running HBI service and its configured database endpoint or mounted SQLite file, followed by a read-only readback from that exact target. Until that provenance link exists, choosing `SAFETY_BACKUP` merely because it contains more rows would violate the project's NO ASSUMPTION rule.

**Provenance note:** the local hashes, counts, and runtime-scan outcomes above are transcribed from the PO-supplied read-only diagnostic outputs in the execution conversation. They are not represented as a fresh independent query by the GitHub connector. The repository configuration and project rules were separately inspected from GitHub.


---

## 2026-11-23 — Seven-product read-only operational DB snapshot reconciliation

**Disposition update:** This addendum supersedes earlier statements in this document that the local operational readback was NOT VERIFIED / unavailable. The PO supplied the output of the PR #523 read-only exporter from the previously identified local operational database path. The source database SHA-256 exactly matches the previously established operational DB fingerprint. The runtime was stopped for the export; this is a point-in-time readback of the identified local operational DB file, not a claim that a service was running during export. **Stage 5 is READY FOR PO REVIEW, not PO-ACCEPTED. Stage 6 remains NOT STARTED.**

### Snapshot provenance and integrity

| Check | Snapshot result | Assessment |
|---|---|---|
| Snapshot kind | `HBI_SEVEN_PRODUCT_READ_ONLY_ACCEPTANCE_BASELINE` | MATCH |
| Export timestamp | `2026-11-24T20:24:16+00:00` | FUTURE-DATED relative to the review date 2026-11-23; provenance/time-source discrepancy remains OPEN |
| Source DB | `hbi.db`, 589,824 bytes | Recorded |
| Source DB SHA-256 | `cb75363628cf3dd8320d5b40c324276b018b3075a18489b4ba4f1420fd541d1c` | MATCH to previously identified operational DB fingerprint |
| WAL / SHM / journal | All absent; 0 bytes | Recorded |
| Export method | Stable DB+WAL file copy; source DB never opened by SQLite; SQLite opened isolated temporary copy only | READ-ONLY METHOD ASSERTED BY EXPORTER |
| Source sidecar stability | Source components hashed before/after; verification true | PASS |
| SQLite integrity | `ok` | PASS |
| Foreign-key violations | 0 | PASS |
| Missing canonical products / tables / columns | 0 / 0 / 0 | PASS |
| Privacy scope | Seven canonical product IDs only; Case, Customer and customer identifiers excluded | PASS |

**Timestamp caveat:** the supplied filename also contains `2026-11-24`, consistent with the JSON timestamp but later than the current review date. The exporter metadata and filename agree with each other; neither establishes why the machine clock/export date is ahead. Do not silently normalize this. PO should confirm the export host clock/timezone or provide a corrected, freshly generated snapshot if the timestamp is material to acceptance.

### Canonical Product Master reconciliation

All seven IDs exactly match the seven canonical IDs in the baseline. Every row is `DRAFT`, `identity_status=NEEDS_REVIEW`, and `qa_verdict=PENDING`; no product is accepted or active based on this snapshot.

| Product | Product Master vs baseline | Identity / QA | Result |
|---|---|---|---|
| P1 COSRX | 150 ml research target in baseline; stored size is NULL | NEEDS_REVIEW / PENDING / DRAFT | MISMATCH: size not populated; physical identity remains UNKNOWN |
| P2 Neutrogena | 200 ml and UK market stored | NEEDS_REVIEW / PENDING / DRAFT | MATCH on stored size/source-market metadata; physical market/formula remains UNKNOWN |
| P3 Garnier | 200 ml and AU market stored | NEEDS_REVIEW / PENDING / DRAFT | MATCH on stored size/source-market metadata; physical package match remains UNKNOWN |
| P4 SKIN1004 | baseline identifies Korean/international version; stored size and market are NULL | NEEDS_REVIEW / PENDING / DRAFT | PARTIAL / UNKNOWN: source-market boundary exists in Evidence, not Product Master |
| P5 ISDIN | SPF50+ research target; stored size and market are NULL | NEEDS_REVIEW / PENDING / DRAFT | PARTIAL / UNKNOWN: physical market/formula and size remain UNKNOWN |
| P6 Clinique | historical 100 ml dossier; stored size is 100 ml, market NULL | NEEDS_REVIEW / PENDING / DRAFT | PARTIAL: size matches; UK retailer evidence market is not populated in Product Master |
| P7 Anua | 30 ml research target; stored size is 30 ml, market NULL | NEEDS_REVIEW / PENDING / DRAFT | PARTIAL: size matches; US evidence scope is not populated in Product Master |

The market values on Product Master are not physical package verification. Evidence source markets remain scoped to their source pages and must not be promoted to physical-unit market identity.

### Evidence reconciliation against the 24-assertion manifest

Snapshot contains 25 Evidence rows, distributed P1–P7 as 4 / 4 / 3 / 3 / 2 / 3 / 6. The baseline manifest contains 24 draft assertions distributed 4 / 4 / 3 / 3 / 2 / 3 / 5. P1–P6 row counts and fields align with their manifest assertion inventories. P7 has one additional stored Evidence row and requires human mapping/reconciliation.

| Product | Manifest assertions | Snapshot Evidence rows | Field-level result |
|---|---:|---:|---|
| P1 COSRX | 4 | 4 | MATCH in row count and fields |
| P2 Neutrogena | 4 | 4 | MATCH in row count and fields |
| P3 Garnier | 3 | 3 | MATCH in row count and fields |
| P4 SKIN1004 | 3 | 3 | MATCH in row count and fields |
| P5 ISDIN | 2 | 2 | MATCH in row count and fields |
| P6 Clinique | 3 | 3 | MATCH in row count and fields |
| P7 Anua | 5 | 6 | MISMATCH / REVIEW: two Evidence rows use `field=ingredients`; the manifest has one ingredients assertion and explicitly records a pre-existing conflict requiring human reclassification |

Across all 25 Evidence rows:
- `evidence_strength=UNVERIFIED`: 25.
- `evidence_status=UNKNOWN`: 25.
- `conflict_status=NONE`: 25.
- `qa_status=PENDING`: 19; `NEEDS_REVIEW`: 6.
- No row is independently verified or QA-approved.

**P7 conflict handling:** the repository manifest describes an ingredients-field conflict, while the snapshot's two Anua ingredients rows both report `conflict_status=NONE`. This is a concrete state mismatch between the draft manifest's conflict note and the stored row flags. Do not infer that the conflict is resolved. Preserve both rows and UNKNOWN statuses; record the conflict as OPEN for PO/human review. No row was deleted, merged, or reclassified.

### ProductKnowledge reconciliation

There are seven ProductKnowledge rows, one per canonical product. All seven have `evidence_status=UNKNOWN`, `knowledge_confidence=0.0`, and NULL `domain_evidence_status`.

- P1 COSRX: all knowledge payload fields and evidence_refs are NULL despite four corresponding Evidence rows. **MISMATCH / material gap.**
- P2 Neutrogena: ingredients, ingredient_roles, usage_instructions, manufacturer_claims and evidence_refs populated; these correspond to its four Evidence rows. **FIELD COVERAGE MATCH**, but knowledge remains UNKNOWN / confidence 0.
- P3 Garnier: ingredients, ingredient_roles, known_use_cases and evidence_refs populated; correspond to its three Evidence rows. **FIELD COVERAGE MATCH**, but knowledge remains UNKNOWN / confidence 0.
- P4 SKIN1004: ingredients, ingredient_roles, manufacturer_claims and evidence_refs populated; correspond to its three Evidence rows. **FIELD COVERAGE MATCH**, but knowledge remains UNKNOWN / confidence 0.
- P5 ISDIN: manufacturer_claims, known_use_cases and evidence_refs populated; correspond to its two Evidence rows. **FIELD COVERAGE MATCH**, but knowledge remains UNKNOWN / confidence 0.
- P6 Clinique: ingredients, ingredient_roles, manufacturer_claims and evidence_refs populated; correspond to its three Evidence rows. **FIELD COVERAGE MATCH**, but knowledge remains UNKNOWN / confidence 0.
- P7 Anua: all knowledge payload fields and evidence_refs are NULL despite six Evidence rows. **MISMATCH / material gap**, compounded by the duplicate ingredients field and conflict-flag discrepancy.

Field coverage is not evidence acceptance. All stored knowledge remains explicitly UNKNOWN and must not be treated as approved consultation content.

### Inventory and relationship tables

| Table | Snapshot | Reconciliation |
|---|---:|---|
| Inventory | 7 rows; each has quantity_available=12, quantity_reserved=0, quantity_damaged=0, stock_status=active | MATCH to the recorded 12-per-product / 84-unit planning baseline; this is database quantity, not a physical count or proof of sellability |
| Recommendation | 0 rows | EMPTY; no recommendation records exist in this snapshot |
| ProductProblemLink | 0 rows | EMPTY; no product-problem relationships exist in this snapshot |

### Final Stage 5 classification

**PASS**
- Snapshot structurally valid; integrity check OK; zero FK violations.
- Exact seven canonical IDs present; required tables/columns present.
- Read-only exporter provenance fields and stable-source hash checks are present.
- Source DB hash matches the previously identified local operational DB fingerprint.
- Inventory rows and counts are visible and reconciled to the recorded planning quantity.
- No write/migration/seed/import or product/evidence/inventory/customer mutation was performed by this review.

**MISMATCH / OPEN**
- Future-dated export timestamp and filename relative to review date.
- P1 COSRX Product Master size NULL despite 150 ml research target.
- P4 source-market boundary, P5 size/market, and P6 market are not populated in Product Master; physical identity remains UNKNOWN.
- P1 and P7 ProductKnowledge payloads/evidence_refs are entirely NULL.
- P7 has six Evidence rows against five manifest assertions, two ingredients-field rows, and stored conflict flags NONE despite the manifest's unresolved conflict note.
- All Product QA remains PENDING; all Product identity statuses NEEDS_REVIEW; all Product statuses DRAFT.
- All Evidence remains UNVERIFIED / UNKNOWN; all ProductKnowledge remains UNKNOWN with zero confidence.
- Recommendation and ProductProblemLink remain empty.
- Snapshot timestamp requires PO confirmation.

**UNKNOWN — deliberately preserved**
- Physical package, GTIN, exact lot/formula and market match for products where not established by the source.
- Whether 12 units per product correspond to physically counted stock; whether stock is sellable under lifecycle/PO rules.
- Any product acceptance, activation, consultation suitability or supported ProductProblemLink relationship.

**Stage 5 status:** **READY FOR PO REVIEW — NOT ACCEPTED.** The requested read-only snapshot has been received, structurally checked, and reconciled against the 7-product / 24-assertion baseline. The remaining items above are explicit PO review findings, not reasons to invent or silently repair data. **Stage 6 remains NOT STARTED.**

**Safety boundary:** this work was read-only. No DB write, migration, seed, import, product/evidence/knowledge/inventory mutation, customer-data access, runtime deployment, or merge was performed.

---

## Final PO handoff summary

### Completed and reliable
- The read-only operational snapshot was obtained from the identified local database using the PR #523 exporter and reconciled against the seven-product baseline.
- Snapshot structure and integrity checks passed: seven canonical Product IDs, seven ProductKnowledge rows, 25 Evidence rows, seven Inventory rows, no foreign-key violations, and SQLite integrity `ok`.
- The recorded inventory quantity is 12 per product / 84 total and is accepted as the PO-approved planning quantity.
- The snapshot is preserved as a point-in-time comparison baseline. No database, product, knowledge, evidence, inventory, or customer data was changed.

### Existing UNKNOWN / CONFLICT classifications
- Physical package / GTIN / lot / exact formula / market identity remains UNKNOWN wherever the existing source record does not establish it.
- ProductKnowledge and Evidence verification classifications remain as captured in the snapshot; these labels are retained as source-state metadata, not reopened as new product-approval requests.
- The existing Anua ingredients-row mapping / manifest conflict-flag discrepancy remains recorded for traceability. It is not treated here as a new product defect or a reason to repeat product review.
- The recorded Product Master lifecycle and QA fields remain a snapshot of stored system state, not a reversal of PO's prior product reviews or approvals.

### Stage 6 baseline suitability
**YES.** The snapshot is sufficient as a stable, read-only point-in-time baseline for future comparison and Stage 6 planning. This statement does not start Stage 6 or authorize changes. Stage 6 remains NOT STARTED and is subject to PO's explicit acceptance and direction.

**Disposition: Stage 5 is ready for final PO handoff. This document does not declare PO acceptance or mark Stage 5 as PO-accepted.**
