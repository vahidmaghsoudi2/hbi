# Stage 6 — Seven-Product Research & Evidence Reconciliation

**Status:** Research pass completed; ready for PO review, not product-data acceptance.  
**Accepted input:** Stage 5 PO acceptance recorded on PR #650 (comment #7111427943).  
**Scope:** Source-based research reconciliation for the seven canonical dossiers P1–P7 using the Stage 5 baseline and accepted read-only snapshot.  
**Safety:** Research/documentation only. No operational DB writes, migrations, seeds, imports, Evidence/ProductKnowledge mutation, PR #650 merge, or Stage 7 work.

## Classification vocabulary

- **FACT** — directly observable fact about a source, document, product label, or captured snapshot; scope is stated.
- **MANUFACTURER_CLAIM** — statement, benefit, efficacy, test, formula/INCI disclosure, or directions published by the manufacturer. It is not independently established merely by publication.
- **EVIDENCE** — the cited source document/page itself, captured and linked; strength/limitations stated.
- **INFERENCE** — analyst interpretation of disclosed ingredients, role, or product positioning; not a finished-product clinical result.
- **CONFLICT** — incompatible assertions, source versions, or stored mappings that cannot be reconciled from current sources.
- **UNKNOWN** — not established by available public source material or physical-package matching.

## Evidence rules applied

1. Official manufacturer pages are primary evidence for what the manufacturer currently publishes, not independent proof of efficacy.
2. A public ingredient list is source-page evidence only. Exact physical unit, lot, market, formula and GTIN match remain UNKNOWN unless matched to an actual package label.
3. Manufacturer studies with incomplete public protocols are classified MANUFACTURER_CLAIM; the numeric result is not promoted to independently verified EVIDENCE of efficacy.
4. Ingredient roles are INFERENCE, even when ingredient presence is listed by the manufacturer.
5. Do not convert cosmetic positioning into treatment indications, diagnosis, or guaranteed outcomes.
6. Product-specific formula/version boundaries are preserved. No source from a different market/version is silently substituted.
7. Stage 5 snapshot fields and Anua conflict state are preserved. This research does not resolve, overwrite, merge, delete, or reclassify database Evidence rows.

## Summary matrix

| Dossier | Official/source research scope | Main source-supported disclosure | Key limitations / conflicts | Disposition |
|---|---|---|---|---|
| P1 COSRX | COSRX official, 150 ml listing | Six peptides; niacinamide and humectant/support ingredients; manufacturer test results | Individual peptide concentrations, full protocol and physical unit match UNKNOWN | Research reconciled; claims remain MANUFACTURER_CLAIM |
| P2 Neutrogena | UK official page, 200 ml | 2% salicylic acid; INCI; directions; 97% noticed fewer spots in 34-subject clinical grading | Not cure rate; protocol/control not public; package-market match UNKNOWN | Source-page assertions confirmed |
| P3 Garnier | Australia official page, 200 ml | Ascorbyl Glucoside (“Vitamin Cg”), lemon extract, INCI and rinse-off directions | Vitamin C derivative; no product-specific acne/pigment treatment endpoint established; physical version UNKNOWN | Source-page assertions confirmed |
| P4 SKIN1004 | Korean/international official SPF50+ PA++++ page | UV-filter system, INCI, hydrating/texture positioning | Separate US drug-label version has different filters/formula; do not merge | Version boundary reinforced |
| P5 ISDIN | Mexico official Active Unify SPF50+ page | 50 ml, SPF50+, DP-Complex disclosure and manufacturer study endpoints | Study details “data on file”; source market/formula/package match UNKNOWN | Claims retained as manufacturer claims |
| P6 Clinique | Official product page plus retailer ingredient snapshot | CL302/Interrupter positioning; listed ingredients include ascorbyl glucoside, salicylic acid, acetyl glucosamine, UP302 | Historical 100 ml version; retailer INCI snapshot; do not transfer to replacement product; claim-study details limited | Historical/version boundary retained |
| P7 Anua | Official Anua serum page; 30 ml research target | 10% azelaic acid manufacturer declaration; INCI; gradual-use directions | Existing snapshot has 6 Evidence rows vs 5 manifest assertions, duplicate ingredients field, conflict-flag discrepancy; physical version UNKNOWN | Conflict remains OPEN; no DB reconciliation performed |

---

## P1 — COSRX The 6 Peptide Skin Booster Serum (150 ml research target)

**Canonical ID:** `HBI-PROD-FE320FA135B843B6`

### Findings
- **FACT:** Official product page lists the 150 ml size and a source-page INCI including six named peptides: Acetyl Hexapeptide-8, Copper Tripeptide-1, sh-Polypeptide-121, Dipeptide Diaminobutyroyl Benzylamide Diacetate, Oligopeptide-68 and Palmitoyl Tripeptide-8. It also lists Niacinamide, Sodium Hyaluronate, Acetyl Glucosamine, Allantoin and other components.
- **MANUFACTURER_CLAIM:** COSRX reports test outcomes including +162.5% deep moisture, +76.4% texture, +40.1% clarity, +24.5% radiance and +22.2% density, based on 20 subjects and a stated 2023 study period. The public page does not provide a complete protocol, comparator, statistical report or independent replication.
- **MANUFACTURER_CLAIM:** Product positioning is first-step/booster use for hydration, texture, radiance, firmness and related cosmetic concerns.
- **INFERENCE:** Humectant/conditioning role for glycerin and hyaluronic acid; supportive/conditioning roles for niacinamide and allantoin; peptide roles follow the manufacturer's positioning only. Ingredient-role mapping does not prove the finished product's efficacy.
- **UNKNOWN:** Individual peptide concentrations; exact formula/lot/market match for the physical 150 ml unit; full study protocol and independent validation.

**Source:** COSRX official product page: https://www.cosrx.com/collections/all/products/the-6-peptide-skin-booster-serum  
**Evidence status:** Source page captured/reviewed; claims are manufacturer-originated, not independently verified.

## P2 — Neutrogena Clear & Defend 2% Salicylic Acid Face Wash (200 ml, UK source scope)

**Canonical ID:** `HBI-PROD-2CC249240D504453`

### Findings
- **FACT:** UK official product page identifies 200 ml, oil-free, and 2% salicylic acid. The page provides an INCI snapshot and directions: wet face, gently massage, avoid eyes/mouth, rinse; it says twice daily.
- **MANUFACTURER_CLAIM:** “97% noticed less new spots in 4 weeks” is reported as clinical grading in 34 subjects. This wording is a proportion of participants reporting/being graded for the endpoint, not a 97% acne cure rate or 97% reduction in acne.
- **INFERENCE:** Salicylic acid is the exfoliating/acne-positioned active; the surfactant system is the cleansing function; glycerin/panthenol are supportive. Fragrance is a review flag for individual sensitivity, not a universal contraindication.
- **UNKNOWN:** Full study protocol, comparator, absolute change, statistical methods; exact physical market/lot/formula match.

**Source:** Neutrogena UK: https://www.neutrogena.co.uk/skincare/cleansers-washes/clear-and-defend-daily-wash  
**Evidence status:** Official source-page disclosure; efficacy number remains MANUFACTURER_CLAIM.

## P3 — Garnier Vitamin C Brightening Gel Cleanser (200 ml, AU source scope)

**Canonical ID:** `HBI-PROD-C29AA2F410A84CCA`

### Findings
- **FACT:** Australia official page states 200 ml and describes a rinse-off gel cleanser. Its INCI lists Ascorbyl Glucoside, Citrus Lemon Fruit Extract, Glycerin, Panthenol, Tocopheryl Acetate, Salicylic Acid, fragrance and fragrance allergens including Linalool, Limonene and Benzyl Salicylate.
- **MANUFACTURER_CLAIM:** Manufacturer positions it as clarifying/brightening and glow-boosting, with Vitamin Cg and citrus extract; page says dermatologically tested.
- **INFERENCE:** Ascorbyl Glucoside is a vitamin-C derivative; cleanser surfactants provide cleansing; glycerin/panthenol can be considered supportive. Rinse-off exposure differs from leave-on products, so avoid overstating treatment potential.
- **UNKNOWN:** Current physical package INCI/market match; no product-specific clinical endpoint for acne or hyperpigmentation was established from this page.

**Source:** Garnier Australia: https://www.garnier.com.au/about-our-brands/skin-active/garnier-skin-active-vitamin-c-brightening-gel-cleanser-200ml  
**Evidence status:** Official source page; positioning is MANUFACTURER_CLAIM.

## P4 — SKIN1004 Madagascar Centella Hyalu-Cica Water-Fit Sun Serum (Korean/international SPF50+ PA++++ version)

**Canonical ID:** `HBI-PROD-7F55ED88F41144F1`

### Findings
- **FACT:** Official Korean/international source page states SPF50+ PA++++ and discloses an INCI with filters including Diethylamino Hydroxybenzoyl Hexyl Benzoate, Ethylhexyl Triazone, Methylene Bis-Benzotriazolyl Tetramethylbutylphenol and Diethylhexyl Butamido Triazone. The list also includes niacinamide, glycerin, centella and multiple hyaluronic-acid forms.
- **MANUFACTURER_CLAIM:** Serum-like texture, moisturizing, dewy/no-white-cast positioning and UV protection claims.
- **INFERENCE:** The UV-filter combination is the core photoprotection system; humectants and centella are supportive skin-conditioning components. No independent formula-specific test was established in this research.
- **CONFLICT / VERSION BOUNDARY:** The US “Water-Fit Sun Serum UV” source is a separate drug-label formula with different active filters (Avobenzone, Homosalate, Octisalate, Octocrylene) and a different INCI. Do not copy the US formula/active percentages into the Korean/international dossier.
- **UNKNOWN:** Physical package, GTIN, market and formula match.

**Sources:**  
- International/Korean page: https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-spf50-pa?country=GB  
- Separate US formula page (comparison only, not target formula): https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-uv  
**Evidence status:** Official disclosures for two distinct versions; version distinction is a FACT, benefits are MANUFACTURER_CLAIM.

## P5 — ISDIN FotoUltra 100 Active Unify SPF50+ (Mexico source scope)

**Canonical ID:** `HBI-PROD-96788ADC488942E3`

### Findings
- **FACT:** Mexico official page describes the 50 ml SPF50+ sunscreen, identifies DP-Complex components (niacinamide, esclareolida, Pisum sativum) and Vitamin E, and provides the product positioning.
- **MANUFACTURER_CLAIM:** ISDIN reports reduction in spot intensity (22%) and spot area (15%) in 31 participants aged 35–65 with mild/moderate hyperpigmented spots after 28 and 84 days. The page cites data on file (2024); complete protocol, comparator, blinding, instruments and statistical report are not public in the reviewed page.
- **MANUFACTURER_CLAIM:** High UV protection and tone-unifying/spot-correcting positioning.
- **INFERENCE:** Niacinamide and the disclosed DP-Complex are claim-linked/brightening-positioned; Vitamin E is antioxidant-positioned. Do not infer guaranteed pigment clearance.
- **UNKNOWN:** Exact formula/market/lot match for the physical target; complete source-matched INCI was not established in the baseline.

**Source:** ISDIN Mexico: https://www.isdin.com/mx/p/fotoultra-active-unify-spf-50/1160  
**Evidence status:** Official source; study results remain manufacturer-reported/data-on-file.

## P6 — Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter (historical 100 ml dossier)

**Canonical ID:** `HBI-PROD-70EEE418BE0F4DAB`

### Findings
- **FACT:** Clinique's official page identifies the product and positions CL302 Brightening Complex and Interrupter Complex. Public ingredient information includes Ascorbyl Glucoside, Dimethoxytolyl Propylresorcinol (UP302), Salicylic Acid, Acetyl Glucosamine, Squalane, Sodium Hyaluronate and extracts.
- **MANUFACTURER_CLAIM:** The official page reports visible dark-spot improvement claims and consumer/clinical study results. Exact endpoints, test design and full protocol are not fully disclosed in the material reviewed here; percentages should be treated as manufacturer-reported, not independent evidence.
- **EVIDENCE (retailer source):** A retailer ingredient document provides an INCI snapshot consistent with the historical product name. It is secondary-source evidence and does not verify the actual physical package or lot.
- **INFERENCE:** Ascorbyl Glucoside, UP302 and Acetyl Glucosamine are claim-linked brightening ingredients; salicylic acid supports exfoliation positioning; silicone/carrier components relate to formula texture. No ingredient concentration or finished-product efficacy is inferred.
- **CONFLICT / VERSION BOUNDARY:** Historical 100 ml “Radical Dark Spot Corrector + Interrupter” dossier is distinct from the replacement/current product variant. Do not transfer replacement product claims or formula.
- **UNKNOWN:** Exact historic package, lot, market and formula match; independent confirmation of efficacy endpoints.

**Sources:**  
- Clinique official: https://www.clinique.com/product/4034/68008/skincare/serum/even-better-clinicaltm-radical-dark-spot-corrector-interrupter  
- Secondary INCI snapshot: https://xcdn.next.co.uk/pdfs/ingredients/AF1626.pdf  
**Evidence status:** Official product/claim page plus retailer ingredient evidence; formula identity remains unresolved.

## P7 — Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum (30 ml target)

**Canonical ID:** `HBI-PROD-22C55A8223A945A6`

### Findings
- **FACT:** Official Anua serum page declares 10% azelaic acid and provides an ingredient list including azelaic acid, panthenol, betaine salicylate, glycerin, allantoin, niacinamide, sodium hyaluronate, centella components, squalane, zinc PCA and ceramide NP.
- **MANUFACTURER_CLAIM:** Official directions advise gradual introduction, starting 1–2 times per week and increasing as tolerated; page guidance describes use up to twice daily and daytime sunscreen. This is manufacturer guidance, not a personalized tolerance guarantee.
- **INFERENCE:** Azelaic acid is the primary claim-linked active; humectants and soothing/conditioning ingredients are supportive. Ingredient presence does not establish treatment of rosacea, acne, PIH or persistent redness.
- **CONFLICT (snapshot reconciliation):** Stage 5 snapshot has 6 Evidence rows for P7 versus 5 manifest assertions; two rows use `field=ingredients`. Manifest notes an ingredients-field conflict, but the captured rows both have `conflict_status=NONE`. This flag mismatch does not resolve the content conflict. Preserve both existing rows and keep conflict OPEN.
- **UNKNOWN:** Which of the two stored ingredients assertions is correct for the exact physical unit/market; row-level source/version/package mapping; complete independent test protocol for any manufacturer tolerability/benefit claims.
- **Scope:** Serum only; distinct from Anua azelaic-acid pads. No new assertion is inserted and no Evidence row is reclassified.

**Source:** Anua official: https://anuaglobal.co/products/azelaic-acid-10-hyaluron-redness-calming-serum  
**Evidence status:** Official source-page declaration; claims remain manufacturer claims. Existing data conflict remains unresolved.

---

## Cross-product conflict and UNKNOWN ledger

| ID | Classification | Finding | Handling |
|---|---|---|---|
| C-01 | CONFLICT | P4 Korean/international formula vs US drug-label formula have distinct filter systems/INCI | Separate version dossiers; no cross-version data transfer |
| C-02 | CONFLICT | P6 historical Clinique product vs replacement/current product | Keep historical 100 ml dossier separate |
| C-03 | CONFLICT | P7 two stored `ingredients` Evidence rows; snapshot flags NONE while manifest documents conflict | Preserve both rows; conflict OPEN; no mutation |
| U-01 | UNKNOWN | Physical package, GTIN, lot, market-to-source formula match across dossiers | Require package evidence for any future identity assertion |
| U-02 | UNKNOWN | Full public protocols and independent replication for manufacturer study claims | Claims remain manufacturer-originated |
| U-03 | UNKNOWN | P1 individual peptide concentrations | Not disclosed in reviewed source |
| U-04 | UNKNOWN | P5 exact source-matched INCI for physical target | Not promoted from other market/formula pages |
| U-05 | UNKNOWN | P6 exact physical historical formula/lot | Retailer snapshot only |
| U-06 | UNKNOWN | P7 source/package mapping of conflicting stored ingredient assertions | Human QA required before any accepted knowledge rebuild |

## Stage 6 result and boundaries

**Research pass:** COMPLETE for the seven dossiers using source pages identified above.  
**Evidence QA / accepted ProductKnowledge:** NOT performed. All claims, source snapshots and inferences remain draft/review classifications.  
**Physical-package verification:** NOT performed; package identity/version/GTIN/lot UNKNOWN where noted.  
**Operational mutation:** NONE.  
**Stage 7:** NOT STARTED.

### PO review items
1. Review the source links and claim-classification boundaries for each dossier.
2. Review the P4/P6 version boundaries.
3. Review the P7 duplicate ingredients mapping and conflict-flag mismatch before any future Evidence reclassification or ProductKnowledge rebuild.
4. Confirm whether this research artifact is accepted as Stage 6 deliverable. Acceptance would not itself authorize data mutation.

**Prepared as a durable comparison artifact:** source URLs, product IDs, classifications, findings, conflicts and UNKNOWNs are all recorded in this file for later retrieval and comparison.
