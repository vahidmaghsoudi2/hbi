# HBI Product Research Working Ledger — Seven Skincare Products
**Version:** 0.1 | **Date:** 2026-10-19  
**Status:** Research continuity artifact; not an approved ProductKnowledge record, Product QA, or product activation.

## Governance and continuity
This file preserves research across conversations. Issue #406 remains the single source of truth for the Product Characteristics & Capabilities team roadmap. This ledger is subordinate to #406 and is not a parallel roadmap. It does not amend the Product Intake contract or authorize changes to application code, schema, API, UI, database, tests, workflows, or product lifecycle.

Rules:
- Lock product identity, market, volume, formula/version and source to each fact.
- Separate manufacturer claims, independent evidence, observations, inferences, unknowns and conflicts.
- Ingredient-level evidence does not establish efficacy of a finished product.
- Do not infer concentrations, study methods, safety or efficacy absent evidence.
- “Not found in sources checked” is not “does not exist.”
- This ledger is research, not an approved or automatic ProductKnowledge entry.
- Continue from the open research queue; repeat previous research only to resolve a contradiction, version change or source problem.

## P1 — COSRX The 6 Peptide Skin Booster Serum, 150 ml
Official: https://www.cosrx.com/collections/all/products/the-6-peptide-skin-booster-serum

The official page lists 150 ml and 50 ml sizes; six peptides (Acetyl Hexapeptide-8, Copper Tripeptide-1, sh-Polypeptide-121, Dipeptide Diaminobutyroyl Benzylamide Diacetate, Oligopeptide-68, Palmitoyl Tripeptide-8); niacinamide, humectants and supporting ingredients. The manufacturer reports +162.5% deep moisture, +76.4% texture, +40.1% clarity, +24.5% radiance and +22.2% density, based on 20 subjects at Dermacosmetic Skin Science Laboratory Co., Ltd, 2023-09-18 to 2023-10-31. Public information does not provide enough detail to independently assess the full protocol, control, instruments and analysis. Manufacturer reports irritation and non-comedogenicity testing; this is not equivalent to independent peer-reviewed proof. Concentrations of individual peptides remain UNKNOWN unless supported by a reliable source.

Independent context: a systematic review of cosmetic peptides identified 15 clinical studies; six were placebo-controlled and five double-blind. This does not prove efficacy of this exact serum. https://pubmed.ncbi.nlm.nih.gov/30941744/

Open: locate original test report/protocol; search independent trials of exact formula; map ingredient roles without inferring product efficacy.

## P2 — Neutrogena Clear & Defend 2% Salicylic Acid Face Wash, 200 ml; market/version unconfirmed
Official research source (UK page only): https://www.neutrogena.co.uk/skincare/cleansers-washes/clear-and-defend-daily-wash

**Intake confirmation (2026-10-27):** size = 200 ml (user-confirmed); market/region = UNKNOWN (retain the existing research dossier without assigning it to the user's physical unit); information basis = prior research file; GTIN/barcode = NOT PROVIDED. Packaging version, physical-unit identity and formula match remain UNVERIFIED. The UK official page is retained as a source for the prior research snapshot, not as proof that the target unit is the UK-market version.

The UK page declares 2% salicylic acid. Its displayed INCI includes surfactants, glycerin, salicylic acid, panthenol, tocopherol and fragrance. The manufacturer says 97% noticed fewer new spots in four weeks, based on clinical grading of n=34; the public page does not provide the full protocol/control or absolute change. Do not call this a 97% acne cure. The page gives directions to wet the face, massage gently, avoid eyes/mouth and rinse; it mentions twice-daily use, but individual tolerance may differ. These are source-page observations, not package-verified instructions for the unconfirmed target unit.

Open: original study documentation; physical package INCI and warnings; market/version identity; independent evidence for the exact SKU. Ingredient-level salicylic acid guidance is contextual, not proof of this rinse-off product. No Product Master registration, ProductKnowledge approval or live runtime transaction is implied by this research update.

## P3 — Garnier Vitamin C Brightening Gel Cleanser, 200 ml, Australia
Official: https://www.garnier.com.au/about-our-brands/skin-active/garnier-skin-active-vitamin-c-brightening-gel-cleanser-200ml

Official INCI includes Ascorbyl Glucoside, lemon extract, glycerin, panthenol, tocopheryl acetate, salicylic acid, surfactants, fragrance, Linalool, Limonene and Benzyl Salicylate. Ascorbyl Glucoside is not automatically equivalent to pure L-ascorbic acid; concentration is not stated in the reviewed source. This is a rinse-off cleanser; evidence from leave-on vitamin C products should not be transferred automatically. Fragrance ingredients may matter for susceptible users, but their presence does not mean everyone will react.

Open: verify current package INCI/warnings; find independent product-specific brightening studies; map ingredient roles. Background on contact allergy: https://dermnetnz.org/topics/contact-allergy-to-limonene-and-linalool

## P4 — SKIN1004 Madagascar Centella Hyalu-Cica Water-Fit Sun Serum SPF50+ PA++++, Korean/international version
Official international/UK source: https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-spf50-pa?country=GB  
Separate US version: https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-uv

Primary dossier is the Korean/international SPF50+ PA++++ version. The US SPF50 product has a separate US sunscreen drug label and lists Avobenzone 2.7%, Homosalate 13.6%, Octisalate 4.5% and Octocrylene 9%. The two formulas and UV-filter systems must not be merged. Claims about hydration, finish, soothing and UV protection must be tied to the exact label/version. Product-specific independent RCT evidence has not yet been established in the sources reviewed.

Open: confirm actual package/GTIN when user supplies it; review exact label directions and protection evidence; search independent product-specific data.

## P5 — ISDIN FotoUltra 100 Active Unify SPF50+
Official Mexico source: https://www.isdin.com/mx/p/fotoultra-active-unify-spf-50/1160

Official Mexico page reports a 22% reduction in spot intensity and 15% reduction in spot area in 31 subjects aged 35–65 with mild/moderate facial hyperpigmentation after 28 and 84 days. Full protocol, control, blinding, instruments and statistical report are not public on the reviewed page. Treat these as manufacturer-reported test data, not independently verified proof. Formula/INCI and fragrance claims may vary by market; UK and Mexico versions must not be assumed identical.

Open: find original test report and independent publication; pin claims to a specific market/packaging version.

## P6 — Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter, 100 ml
Official: https://www.clinique.com/product/4034/68008/skincare/serum/even-better-clinicaltm-radical-dark-spot-corrector-interrupter

Official page reports 39% visible reduction in dark spots in 12 weeks from clinical testing on 52 women. Separate consumer testing on 533 women reports different outcomes; sample sizes and endpoints must not be conflated. Public page does not establish that the 52-person study was randomized, double-blind or controlled; do not label it an RCT without protocol evidence. Ingredients include Ascorbyl Glucoside, Dimethoxytolyl Propylresorcinol and Salicylic Acid; active concentrations remain proprietary/UNKNOWN from reviewed public information. Do not convert cosmetic spot claims into a medical melasma-treatment claim.

Open: locate protocol/original report; verify exact 100 ml-market INCI; search independent studies of the finished formula.

## P7 — Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum, 30 ml
Official: https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum

Manufacturer claims 10% azelaic acid. Current official INCI includes Azelaic Acid, Panthenol, Betaine Salicylate, Glycerin, Niacinamide, Sodium Hyaluronate, Centella components, Squalane, Zinc PCA and Ceramide NP. Manufacturer recommends gradual introduction, beginning at one to two times weekly and increasing as tolerated. Brand material reports 90% of participants agreed that red troubled spots looked improved, but full public protocol is not available in the reviewed source. Do not transfer a study of Anua’s separate azelaic-acid pad to this serum.

Open: find original serum study documentation; search exact-formula independent studies; verify warnings and market-specific formula. Separate pad product: https://anua.com/products/azelaic-10-hyaluron-redness-soothing-pad. Azelaic acid review: https://pubmed.ncbi.nlm.nih.gov/37152770/

## Cross-product evidence
- AAD 2024 acne guideline conditionally recommends topical salicylic acid and azelaic acid in acne management; this does not prove any named product’s efficacy: https://pubmed.ncbi.nlm.nih.gov/38300170/
- Systematic review of topical post-inflammatory hyperpigmentation treatments: 47 studies, 1,853 participants; broad contextual evidence only, not proof for these products: https://pubmed.ncbi.nlm.nih.gov/34525885/
- Niacinamide studies are formulation-, concentration-, population- and endpoint-specific; do not transfer their results automatically to these products: https://pubmed.ncbi.nlm.nih.gov/16029679/ ; https://pubmed.ncbi.nlm.nih.gov/18492135/ ; https://pubmed.ncbi.nlm.nih.gov/15002658/
- Sunscreen use, reapplication and water-resistance statements must follow the exact product/market label. Do not infer water resistance or regulatory equivalence from product name alone.

## Next research queue
1. Map ingredient roles for all seven formulas using authoritative references, distinguishing active ingredients, base, humectants, surfactants, emollients, UV filters, preservatives and fragrance.
2. Locate primary manufacturer protocols, especially COSRX, ISDIN, Clinique and Anua.
3. Search independent peer-reviewed studies of each exact finished product.
4. Verify package-specific warnings, directions, current INCI and market/version.
5. For each new finding, record source URL, source type, exact fact/claim, date/version if available, limitation and review status.
6. When actual catalog/photos/packaging are supplied, use them to disambiguate market/formula; do not guess product identity.

This is an initial continuity snapshot, not a claim of exhaustive global searching. “Not found so far” means not established in sources checked to date.

## Handoff rule
At the start of a new conversation, retrieve this file and current Issue #406 first. Continue from the open research queue. Do not repeat completed findings unless correcting a contradiction, source change or version mismatch. This ledger is research only and does not itself approve or populate ProductKnowledge.


---

## Research pass 1 — ingredient-role boundaries and study-protocol follow-up
**Reviewed:** 2026-10-19  
**Status:** source review; no ProductKnowledge approval or implementation authorization.

### A. Ingredient-role mapping — conservative, label-level only

This is a first-pass role map from the ingredient declarations already recorded above. It is not a complete INCI audit and does not infer concentrations, clinical effectiveness, safety for a particular person, or a regulatory approval.

| Product | Ingredient groups visible in the recorded label/source | Defensible interpretation | Boundary / unresolved point |
|---|---|---|---|
| P1 COSRX 6 Peptide Booster | Peptides; niacinamide; humectants | Formula includes peptide ingredients and water-binding/supporting ingredients. | Individual peptide concentrations, mechanism at this formula's use level, and product-specific independent efficacy remain UNKNOWN. |
| P2 Neutrogena UK 2% SA Wash | Declared 2% salicylic acid; surfactants; glycerin; panthenol; tocopherol; fragrance | Salicylic acid is the declared highlighted ingredient; surfactants perform cleansing, while glycerin is commonly used as a humectant. | Rinse-off exposure and the exact study protocol limit what can be inferred from general ingredient evidence. Manufacturer says 97% noticed fewer new spots in 4 weeks (n=34, clinical grading); this is not a 97% cure rate. |
| P3 Garnier Australia Vitamin C Cleanser | Ascorbyl Glucoside; salicylic acid; surfactants; glycerin; panthenol; fragrance components | Cleansing system plus listed vitamin-C derivative and supporting humectant ingredients. | Ascorbyl Glucoside must not be relabelled as pure L-ascorbic acid; concentration and exact-product brightening evidence are not established. Fragrance constituents are a possible relevance for susceptible users, not proof that every user will react. |
| P4 SKIN1004 international SPF50+ PA++++ | Four chemical UV filters listed on the international formula; glycerin, niacinamide, Centella asiatica and multiple hyaluronate forms | UV filters are the protection system; other listed ingredients serve formulation/skin-conditioning roles. | Confirm the actual market label before use. The US SPF50 UV SKU has different filters and is not interchangeable with the international formula. Manufacturer-controlled formula reports do not establish independent clinical efficacy. |
| P5 ISDIN Active Unify SPF50+ | Sunscreen filters plus marketed brightening/spot-care ingredients, depending on market formula | UV protection and appearance-of-spot claims must be treated as distinct endpoints. | Market-specific INCI and the original protocol behind the reported 22% spot-intensity and 15% spot-area changes remain open. |
| P6 Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter | Ascorbyl Glucoside, Dimethoxytolyl Propylresorcinol, salicylic acid, supporting base ingredients | Product contains listed ingredients associated with cosmetic tone/spot-care positioning. | Do not infer active concentrations or a medical melasma indication. The 52-person clinical result and 533-person consumer test are separate data sets/endpoints. |
| P7 Anua Azelaic Acid 10% + Hyaluron Serum | Manufacturer-declared 10% azelaic acid; niacinamide, panthenol, betaine salicylate, humectants, centella components, squalane, zinc PCA, ceramide NP | Manufacturer-declared azelaic acid concentration is distinct from the roles of supporting ingredients. | Manufacturer recommends gradual introduction. The 90% agreement result is a manufacturer-reported outcome; the full protocol, control, endpoints and analysis remain unavailable in the public page reviewed. Do not transfer evidence from the separate pad. |

### B. Source interpretation rules confirmed

1. The European Commission's CosIng page describes its database as an informative ingredient/reference resource and explicitly states that inclusion in CosIng does not itself mean an ingredient is approved for use or determine its regulatory status. Source: https://single-market-economy.ec.europa.eu/sectors/cosmetics/cosmetic-ingredient-database_en
2. FDA distinguishes sunscreen active ingredients, which protect against UV rays, from inactive ingredients used in the formulation. This is especially relevant to maintaining separate dossiers for the US OTC SKIN1004 SPF50 UV product and the Korean/international SPF50+ PA++++ product. Sources: https://www.fda.gov/drugs/understanding-over-counter-medicines/sunscreen-how-help-protect-your-skin-sun and https://www.fda.gov/drugs/understanding-over-counter-medicines/questions-and-answers-fdas-regulatory-actions-over-counter-sunscreen
3. Ingredient presence or general ingredient-level evidence is not proof that the finished product achieves a claimed result. A rinse-off cleanser, a leave-on serum and a sunscreen are different exposure/formulation contexts.
4. A manufacturer's clinical or consumer result is recorded as a manufacturer-reported claim unless the full protocol/report or a suitable independent publication is available and reviewed. Do not promote a study to “RCT,” “independent,” or “peer-reviewed” without evidence supporting that classification.

### C. Protocol and independent-evidence search disposition

- COSRX: official page continues to disclose n=20 and a 2023 test window, but the full protocol, control, instruments and statistical analysis were not available in the reviewed page. Exact-product independent evidence remains NOT ESTABLISHED in this pass.
- Neutrogena UK: official page confirms the 200 ml UK product, declared 2% salicylic acid and the n=34/4-week clinical-grading statement. Full protocol and independent exact-SKU evidence remain NOT ESTABLISHED in this pass. The page says the product and ingredients may change; package label verification remains necessary.
- SKIN1004: an official brand information page reports a dry-environment moisture test on 20 adults and a separate SPF measurement on 10 subjects for the Korean/international product. These are manufacturer-published test summaries, not independent peer-reviewed confirmation. The US formula is explicitly separate. Source: https://info.skin1004.com/guide/moisturizing-sunscreen-that-wont-leave-skin-feeling-tight
- Anua: a current brand page repeats the 90% participant-agreement statement for the exact serum, but the complete protocol is not presented on the page reviewed. Source: https://pages.anua.com/solutions/redness-prone-routine-sensitive-skin
- ISDIN and Clinique: the public manufacturer claims already recorded in their dossiers remain insufficient to establish randomization, blinding, control design or independent replication. Original reports/protocols are still open research items.
- Across this pass, an exact-product independent peer-reviewed trial was NOT ESTABLISHED from the sources checked. This is a bounded search result, not proof that no such study exists.

### D. Next queue — priority order

1. Seek primary protocols/reports for COSRX, ISDIN, Clinique and Anua; capture study sponsor, design, control, population, endpoints, instruments, duration, analysis and conflicts of interest where available.
2. Seek independent exact-finished-product studies for all seven, preserving exact market, size, formula/version and dates. Record negative search outcomes as “not found in sources checked,” never as proof of absence.
3. Complete the ingredient-role map from current official INCI/package labels, and use a suitable authoritative reference for each role. Keep uncertain functions UNKNOWN rather than guessing from marketing language.
4. Verify package-specific directions, warnings, market and GTIN when a real package/catalog image is supplied.
5. Do not convert any research-ledger statement directly into ProductKnowledge or product activation. Follow Issue #406's gates and existing Intake/QA governance.



### E. Supplementary source check — manufacturer-held study documentation
**Reviewed:** 2026-10-19

- **P5 ISDIN Active Unify:** An additional official ISDIN Chile page identifies its 31-subject evaluation of facial hyperpigmentation (ages 35–65; assessment after 28 and 84 days) as **“Data on file, 2024.”** This is useful provenance for the manufacturer's reported data, but the underlying report is not exposed on that page for independent appraisal. Do not treat the label “clinical” or “data on file” as proof of randomization, blinding, control design, peer review or independent replication. Source: https://www.isdin.com/cl/p/active-unify-spf-50/1160
- **P7 Anua Azelaic Acid 10% + Hyaluron Serum:** The brand-owned routine page repeats the 90% participant-agreement claim for the exact serum, but does not publish the complete protocol. A separate retail listing describes a 4-week consumer self-assessment involving 22 participants aged 20–59 and attributes the claims to P&K Skin Research Center; because this is a secondary retail source, it is a lead for locating the original report, not a substitute for it. Do not conflate consumer agreement with objective clinical improvement. Sources: https://pages.anua.com/solutions/redness-prone-routine-sensitive-skin and https://vitaliaina.com/products/azelaic-acid-10-hyaluron-serum
- **P3 Garnier Australia:** The current official page describes the 200 ml gel cleanser as rinse-off, identifies “Vitamin Cg” as Ascorbyl Glucoside, and warns that ingredient lists are updated and the package is the current reference. This reinforces the need to verify the physical label before locking an INCI snapshot. Source: https://www.garnier.com.au/about-our-brands/skin-active/garnier-skin-active-vitamin-c-brightening-gel-cleanser-200ml

**Status:** These findings refine provenance and search leads only. They do not establish independent efficacy for any exact finished product and do not change the approval status of the ledger.


### F. Exact-finished-product study screen — pass 2
**Reviewed:** 2026-10-19  
**Method:** Targeted web-index searches combining each exact product name with clinical study/trial/PubMed terms. This is a screening pass, not a systematic review; indexing and naming differences can hide relevant reports.

| Product | Search-screen result | Handling decision |
|---|---|---|
| P1 COSRX The 6 Peptide Skin Booster Serum | Search results surfaced the manufacturer's own n=20 claim and unrelated peptide research, but no independently published study of this exact finished product was established. | Keep manufacturer claim separate; continue seeking protocol/report and exact-SKU publications. |
| P2 Neutrogena Clear & Defend 2% Salicylic Acid Face Wash, UK 200 ml | A PubMed result involving a different skincare regimen and a Neutrogena 2% salicylic-acid cleanser surfaced. It did not establish that the tested cleanser was this exact UK Clear & Defend SKU. | Exclude from product-specific efficacy evidence; ingredient/class similarity is not product identity. |
| P3 Garnier Vitamin C Brightening Gel Cleanser, Australia 200 ml | No independent exact-finished-product study was established in this search screen. | Do not substitute vitamin C ingredient studies for evidence of this rinse-off formula. |
| P4 SKIN1004 Hyalu-Cica Water-Fit Sun Serum SPF50+ PA++++, Korean/international | Search results surfaced brand-published summaries for moisture/SPF testing, but no independent peer-reviewed exact-SKU study was established. | Keep brand test summaries in manufacturer-evidence tier; retain separate US SKU dossier. |
| P5 ISDIN FotoUltra 100 Active Unify SPF50+ | The manufacturer-reported 31-subject evaluation and “Data on file, 2024” reference remain leads; no accessible independent exact-product paper was established in this screen. | Request/locate underlying report; do not infer design features absent from the public summary. |
| P6 Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter, 100 ml | Search results surfaced an independent-looking dark-spot study of a different product (SkinMedica Dark Spot Tx), not this Clinique serum. | Explicitly exclude the SkinMedica study from Clinique product-specific evidence. Clinique's 52-woman result remains a manufacturer-reported claim pending full protocol. |
| P7 Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum, 30 ml | Search results surfaced a 2026 study of a different anhydrous concentrate combining retinal 0.1% with azelaic acid 10%, not the Anua serum. | Explicitly exclude it from Anua product-specific evidence; shared azelaic-acid percentage does not establish formula equivalence. |

**Representative exclusion/source checks**
- A PubMed record on a niacinamide-containing moisturizer and a Neutrogena salicylic-acid cleanser involved a different study regimen; it is not proof for the exact Clear & Defend UK SKU: https://pubmed.ncbi.nlm.nih.gov/31461548/
- A 2026 split-face study concerns a distinct anhydrous retinal/azelaic-acid concentrate, not Anua's multi-ingredient serum: https://pubmed.ncbi.nlm.nih.gov/42572367/
- A 12-week dark-spot study concerns SkinMedica Dark Spot Tx, not Clinique Even Better Clinical: https://pmc.ncbi.nlm.nih.gov/articles/PMC10544009/
- A peptide study on Medipep-6PN is not a study of the COSRX six-peptide booster: https://pmc.ncbi.nlm.nih.gov/articles/PMC12940413/

**Interpretation guardrail:** “Not established in this search screen” means the search did not verify an exact-product independent study. It is not a claim that no study exists. Do not transfer efficacy results between products merely because they share an ingredient, ingredient percentage, product category or marketing goal.

**Next action from this pass:** Prioritize locating the original manufacturer reports for P1, P5, P6 and P7; then obtain current package/INCI evidence for the exact market/SKU before any catalog-ready knowledge extraction. No ProductKnowledge, QA, lifecycle or implementation status changes are authorized by this research update.


### G. Original Clinical Evidence Verification — Pass 3 (four priority products)
**Review date:** 2026-10-19  
**Purpose:** Incorporate the Pass 3 evidence dossier and independently cross-check selected claims against publicly accessible primary/manufacturer pages. This is still a research artifact, not an approved ProductKnowledge record.

#### G1. P1 — COSRX The 6 Peptide Skin Booster Serum
- The current COSRX product page publicly states five quantitative outcomes (+162.5% deep moisture, +76.4% texture, +40.1% clarity, +24.5% radiance, +22.2% density) and attributes them to clinical trials of 20 subjects conducted by Dermacosmetic Skin Science Laboratory Co., Ltd from 2023-09-18 to 2023-10-31. It also reports 100% of participants reported smoother/more supple skin. Source: https://www.cosrx.com/collections/all/products/the-6-peptide-skin-booster-serum
- Classification: **MANUFACTURER_CLAIM**. The public page does not expose the complete protocol/report, statistical analysis, control/blinding details, adverse-event table or raw data. “Independent laboratory” wording alone does not establish independence of sponsorship or study design.
- Product-specific peer-reviewed publication or public trial registration: **NOT ESTABLISHED in the sources checked**. Do not substitute general peptide/niacinamide literature.

#### G2. P5 — ISDIN FotoUltra 100 Active Unify SPF50+
- The official ISDIN Spain page confirms the 22% spot-intensity and 15% spot-area claims for 31 people aged 35–65 with mild-to-moderate facial hyperpigmented spots after 28 and 84 days; the page labels this “Data on file, 2024.” It also labels blue-light hyperpigmentation testing and the 82% MMP statement as “Data on file, 2023,” with the latter explicitly based on skin explants. Source: https://www.isdin.com/es/p/fotoultra-active-unify-spf-50/1160
- Classification: the 22%/15% figures remain **MANUFACTURER_CLAIM**; complete study design, control, measurement method and statistical analysis are not available on the public page. The MMP result is ex vivo and must not be described as an RCT or clinical outcome in humans.
- A peer-reviewed, open-access randomized investigator-masked intra-individual study exists for **ISDIN FOTOULTRA 100 SPOT PREVENT**, not Active Unify: 20 participants with Fitzpatrick types IV–V, daily use for 20 days, ΔITA° primary endpoint at Day 22; registration ISRCTN11448711. The paper discloses ISDIN funding and ISDIN employee/consultant relationships among authors. Sources: https://pubmed.ncbi.nlm.nih.gov/41240206/ and https://doi.org/10.1007/s13555-025-01586-w
- Hard boundary: this paper is relevant contextual evidence for a different named product/formula, not direct clinical proof for Active Unify. No transfer of its outcome to Active Unify is allowed without exact-formula equivalence evidence.

#### G3. P6 — Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter
- The official US product page confirms “39% visible reduction in dark spots in 12 weeks” based on clinical testing on 52 women after 12 weeks. It separately reports consumer testing on 536 women; current page claims include 84% saying skin looks more radiant and 93% saying skin feels soothed/calmer. Source: https://www.clinique.com/product/4034/68008/skincare/serum/even-better-clinicaltm-radical-dark-spot-corrector-interrupter
- Classification: the 39% result is **MANUFACTURER_CLAIM**; the page does not disclose enough information to establish randomization, blinding, control, measurement instrument, or independent replication. Consumer-report outcomes must stay separate from clinical testing.
- A separate manufacturer/retailer claim of 94% may appear in other campaign material, but the current official page checked here states 84% radiance and 93% soothed/calmer. Do not reconcile or replace one figure without the exact market, campaign date and source being captured.
- The literature includes a letter/case report titled “Exogenous ochronosis associated with dimethoxytolyl propylresorcinol (UP302).” It is a limited safety signal, not a rate estimate and not proof that this finished Clinique product caused the event. Source: https://pubmed.ncbi.nlm.nih.gov/34031918/

#### G4. P7 — Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum
- The current official serum page identifies 10% azelaic acid and describes non-comedogenic/low-irritation testing, but the publicly displayed page does not provide a complete serum study protocol with n, control, objective endpoints and analysis. Source: https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum
- A separate Anua routine page repeats that 90% of participants agreed the appearance of red troubled spots improved; the full protocol is not published on that page. Source: https://pages.anua.com/solutions/redness-prone-routine-sensitive-skin
- Important product-identity distinction: Anua's **Azelaic 10 Hyaluron Redness Soothing Pad** page reports a separate study by P&K Skin Research Center, 21 participants aged 20–59, 2025-01-20 to 2025-02-19. This is the pad, not the serum, and its sample size or results must not be attributed to the serum. Source: https://anua.com/products/azelaic-10-hyaluron-redness-soothing-pad
- Classification for finished-serum efficacy: **MANUFACTURER_CLAIM / PARTIAL** where the specific claim is documented; independent product-specific clinical efficacy remains **UNKNOWN / NOT ESTABLISHED in the sources checked**.

#### G5. Cross-product evidence decisions
1. Keep each numeric efficacy statement linked to its exact product, market/version, source date and evidence type.
2. Keep clinical investigator assessments, instrumental endpoints, consumer self-report, tolerability testing and ex vivo results as separate evidence classes.
3. “Not established in the sources checked” is a bounded search conclusion, not proof of non-existence.
4. Do not create a numeric confidence score from subjective labels such as Low or Low–Moderate unless HBI has an approved scoring rubric.
5. Suggested provisional evidence fields for future schema mapping: `claim_type=MANUFACTURER_CLAIM`, `evidence_status=PARTIAL` where the manufacturer summary is public but protocol is incomplete; `UNKNOWN` for unverified product-specific clinical efficacy. These are research recommendations only, not writes to ProductKnowledge.
6. Next action: request full reports/protocols from COSRX, ISDIN and Clinique; request the serum-specific tolerability/efficacy report from Anua; in parallel verify physical package, market, GTIN and current INCI before any catalog-ready extraction.

**Governance:** This Pass 3 update does not authorize PR merge, product activation, QA approval, database/schema/API/UI changes or direct ProductKnowledge writes.


### H. Pass 4 — source discrepancies and request-ready evidence gaps
**Reviewed:** 2026-10-19  
**Purpose:** Capture new source-level details and prevent market/formula/endpoint conflation. This pass does not claim access to confidential manufacturer reports.

#### H1. COSRX — marketing summary is still the only publicly inspectable study summary located
The current official product page repeats the five numeric outcomes, n=20, and the 2023-09-18 to 2023-10-31 test window, naming Dermacosmetic Skin Science Laboratory Co., Ltd. The full protocol/report was not exposed in the page reviewed. Source: https://www.cosrx.com/collections/all/products/the-6-peptide-skin-booster-serum  
**Open request:** ask for the final report and protocol, endpoint definitions/units, baseline and post-treatment values, analysis plan, missing-data handling, adverse events, ethics/consent information, funding/sponsor and investigator independence.

#### H2. ISDIN — a distinct market/product variant gives a different study description
A Colombian official ISDIN page for **FotoUltra 100 Active Unify Color SPF50+** states a 22% reduction in solar spots, but attributes it to a study of **30 subjects aged 35–68 over 12 weeks** and labels it “ISDIN, Data on File, 2024.” Source: https://www.isdin.mom/co/p/active-unify-color-spf-50/0131  
This differs from the standard Active Unify description previously recorded (31 subjects aged 35–65; assessment at days 28 and 84). Do not treat these as the same cohort or the same SKU until the product name, country, tint/color, formula, protocol and endpoint definition are reconciled. This may be a market/variant distinction or a separate presentation of evidence; the public pages alone do not resolve it. The 82% MMP statement remains ex vivo skin-explant evidence, not a human clinical endpoint.

**Open request:** request both referenced 2024 data-on-file reports and ask ISDIN to map each report to GTIN, market, tinted/untinted SKU, formula/version, sample size, visit schedule and endpoint.

#### H3. Clinique — separate endpoints and study populations
The current official US page states 39% visible dark-spot reduction after 12 weeks based on clinical testing on 52 women. It separately reports consumer testing on 536 women for 84% radiance and 93% soothed/calmer, and other consumer outcomes at 28 days with distinct denominators (533 and 433). Source: https://www.clinique.com/product/4034/68008/skincare/serum/even-better-clinicaltm-radical-dark-spot-corrector-interrupter  
A retailer page also repeats a separate claim that redness from irritation was reduced after 150 minutes in clinical testing on 26 people versus an untreated control; the exact official market/campaign source and protocol for that endpoint still need to be captured before elevating it to a confirmed dossier claim. Source: https://www.macys.com/shop/product/clinique-even-better-clinical-radical-dark-spot-corrector-interrupter-serum-1-oz.?ID=10516332  
**Open request:** request full reports for both the 52-person/12-week dark-spot endpoint and 26-person/150-minute redness endpoint. Keep the latter as a separate, lower-provenance source lead until official product-page substantiation and methods are obtained.

#### H4. Anua — serum claim and pad study must remain separate
The official Anua serum page confirms the brand's 10% azelaic-acid positioning, but does not expose a complete product-specific clinical report with sample size, control, objective endpoint and statistical analysis. Source: https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum  
The brand's routine page repeats that 90% of participants agreed the appearance of red troubled spots improved, but does not provide the full protocol. Source: https://pages.anua.com/solutions/redness-prone-routine-sensitive-skin  
A separate official page for **Azelaic 10 Hyaluron Redness Soothing Pad** gives a different product and a P&K Skin Research Center study description (21 participants, ages 20–59, 2025-01-20 to 2025-02-19). Source: https://anua.com/products/azelaic-10-hyaluron-redness-soothing-pad  
**Hard boundary:** do not transfer the pad's sample size, study period or outcome to the serum.  
**Open request:** ask Anua for the serum-specific protocol/report and a clear statement of the tested SKU, formulation, test site, participant count, comparator, objective/subjective endpoints and adverse events.

#### H5. Standardized evidence-request checklist
For each manufacturer request, ask for:
1. Exact product name, GTIN, country/market, formula version and tested package/INCI.
2. Full final report plus protocol and any amendments.
3. Study design, comparator/control, randomization and blinding.
4. Sample size enrolled/completed, inclusion/exclusion criteria, demographics and attrition.
5. Endpoint definitions, instrument/model, units, baseline/follow-up values and analysis methods.
6. Statistical plan, confidence intervals/p-values where applicable, multiplicity handling and missing-data handling.
7. Adverse events/tolerability findings and ethics/consent information.
8. Sponsor, laboratory, investigators, funding and conflict-of-interest declarations.
9. Whether a public publication or registry record exists and permission to cite the report accurately.

**Current disposition:** Public manufacturer summaries are recorded as manufacturer claims; no confidential report is presumed to have been obtained. These requests are a research task only and do not authorize ProductKnowledge entry, QA approval, product activation, code changes or PR merge.


### I. Pass 5 — manufacturer evidence-request routing and ready-to-send request
**Reviewed:** 2026-10-19  
**Purpose:** Convert the existing evidence gaps into an actionable outreach step without repeating the prior evidence review. Contact routes below were located on official brand pages; no request has been sent by this project.

#### I1. Official contact routes located
- **ISDIN Colombia:** official contact form, with profile options including consumer, healthcare professional and other: https://www.isdin.com/co/contact_us. The official page lists +57 601 307 4279, Monday–Friday 09:00–18:00. Use the form and identify the request as a research/documentation inquiry, not an adverse-event report. Source checked: https://www.isdin.com/co/contact_us
- **COSRX:** official product inquiry page: https://www.cosrx.com/pages/product-inquiry. Official global customer-service email listed on the brand's store/contact information: global@cosrx.co.kr. Source checked: https://www.cosrx.com/pages/stores?q=uEq
- **Clinique US:** official product/ingredient customer-care page: https://www.clinique.com/pages/general-info. It directs product/ingredient questions to Consumer Care at 1-866-707-2100 or through Contact Us / Beauty-Product Advice. Source checked: https://www.clinique.com/pages/general-info
- **Anua US:** official contact form and email help@anua.us: https://anua.com/pages/contact. Source checked: https://anua.com/pages/contact

**Routing limitation:** These are consumer/product-support channels, not confirmed scientific-affairs or medical-information contacts. Ask them to route the inquiry to the clinical research, regulatory, or scientific documentation team. Do not assume they will disclose confidential reports.

#### I2. Ready-to-send English request — common body
**Subject:** Request for substantiation and study documentation for [exact product name / market / size]

Hello Product Support / Scientific Documentation Team,

I am conducting a product-evidence review and would appreciate your help locating the documentation supporting the published study or efficacy statements for **[exact product name, market, size, and variant]**.

Could you please route this inquiry to the appropriate clinical research, regulatory, or scientific documentation team and provide, where shareable:
1. The full final study report and protocol (including amendments), or a public publication/registry reference.
2. The exact tested product identity: market/country, size, GTIN, formula/version and tested INCI.
3. Study design, comparator/control, randomization/blinding, enrolled and completed participant counts, population, duration and assessment schedule.
4. Endpoint definitions, measurement instruments and units, baseline/follow-up values, statistical methods and uncertainty estimates.
5. Adverse-event/tolerability summary, sponsor/funding, investigator/laboratory details and conflicts of interest.
6. Confirmation of which public product-page claim(s) are supported by this report, and whether the tested formula matches the currently marketed version.

If the full report cannot be shared, a study synopsis containing the above information or a public reference would still be useful. Please identify any details that cannot be disclosed rather than leaving them ambiguous.

Thank you.

#### I3. Product-specific inserts — preserve the unresolved distinctions
- **ISDIN:** “Please provide the two source reports labelled Data on File, 2024: (a) standard Active Unify SPF50+ described as n=31, ages 35–65, assessments at days 28 and 84; and (b) Active Unify Color SPF50+ described on the Colombian page as n=30, ages 35–68, over 12 weeks. Please map each report separately to GTIN, market, tinted/untinted SKU, formula/version, protocol, endpoint definition and visit schedule. We are not assuming these are the same cohort.” Public routing page: https://www.isdin.com/co/contact_us
- **COSRX:** “Please provide the report behind the published n=20 evaluation dated 2023-09-18 to 2023-10-31 by Dermacosmetic Skin Science Laboratory Co., Ltd., including the definitions and units for deep moisture, texture, clarity, radiance and density, plus baseline/follow-up results and study methods.” Product inquiry: https://www.cosrx.com/pages/product-inquiry
- **Clinique:** “Please provide the substantiation/report for the 39% visible dark-spot reduction claim after 12 weeks (clinical testing, n=52 women). Separately, please confirm whether an official report exists for the retailer-reported 150-minute redness endpoint (n=26 vs untreated control); do not combine the two endpoints.” Contact route: https://www.clinique.com/pages/general-info
- **Anua:** “Please provide the serum-specific report behind the statement that 90% of participants agreed the appearance of red troubled spots improved. Please confirm the tested product was the 30 ml Azelaic Acid 10% + Hyaluron Redness Soothing Serum, not the separate pad product, and supply participant count, study period, comparator, endpoint, analysis and tolerability details.” Contact route: https://anua.com/pages/contact

#### I4. Execution status and next action
- Status: **REQUEST TEXT PREPARED; NOT SENT.** This ledger does not have an authenticated outbound-email/contact-form action, so no contact is claimed.
- Priority 1: ISDIN discrepancy request, because two official market pages describe materially different sample/age/visit details under the 2024 data-on-file reference.
- Priority 2: COSRX and Clinique full reports; Priority 3: Anua serum-specific report.
- When replies arrive, add source/date, sender role (if provided), attachment/public link, product-version mapping, report access status and evidence limitations to this same ledger. Do not create a parallel tracker.
- No ProductKnowledge write, QA approval, product activation, implementation change or PR merge is authorized by this pass.


#### I5. Follow-up verification — ISDIN discrepancy is broader than tinted vs untinted
A further check of official ISDIN pages found a third relevant presentation:
- **Colombia, standard Active Unify SPF50+ (untinted):** official page states 22% reduction in spot intensity; study described as 30 subjects aged 35–68 over 12 weeks, evaluating “Active Unify Sin Color,” Data on File 2024. https://www.isdin.com/co/p/active-unify-spf-50/1160
- **Colombia, Active Unify Color SPF50+:** official page states 22% reduction; 30 subjects aged 35–68 over 12 weeks, Data on File 2024. https://www.isdin.com/co/p/active-unify-color-spf-50/0131
- **Spain, standard Active Unify SPF50+:** official page states both 22% intensity and 15% area reduction; 31 subjects aged 35–65, mild-to-moderate facial hyperpigmented spots, after 28 and 84 days, Data on File 2024. https://www.isdin.com/es/p/fotoultra-active-unify-spf-50/1160
- **Spain, Active Unify Color SPF50+:** official page repeats the 31-subject, age 35–65, day 28/84 description for the 22% intensity and 15% area claims. https://www.isdin.com/es/p/active-unify-color-spf-50/0131

**Interpretation:** The earlier hypothesis that the n=30 vs n=31 discrepancy may simply reflect tinted versus untinted variants is not supported as a complete explanation: the Colombian untinted page also reports n=30/ages 35–68/12 weeks, while Spanish standard and Color pages report n=31/ages 35–65/day 28 and 84. Public pages do not establish whether this is a distinct market-specific study, a localized claim error, a protocol revision or different reporting of a shared study. Keep all four page-level descriptions distinct pending the source report; do not collapse them into a single cohort or assert a cause.

**Updated request to ISDIN:** Request the source report(s) behind both the Colombian n=30/35–68/12-week wording and the Spanish n=31/35–65/day-28-and-84 wording, and ask whether each report supports the standard and Color SKUs in each market. Request report IDs, protocol/version dates, GTINs, formulas, endpoints, enrolled/completed counts and visit schedule. This supersedes the narrower assumption that only the Color variant needs reconciliation.


#### I6. New public primary-source lead — EADV 2024 abstract for an ISDIN DP-Complex sunscreen
A targeted search found an EADV Congress 2024 scientific abstract titled **“Clinical evaluation of the depigmentant effect of a new facial suncare formulation with DP-Complex and very high UV protection in subjects with hyperpigmentation”** (Abstract 4411). Public source: https://eadv.org/wp-content/uploads/scientific-abstracts/EADV-congress-2024/Pigmentary-disorders.pdf

The indexed abstract reports:
- Authors: Sonia Aladren, Javier Bustos, Alessandro De Luca and Monica Foyaca; affiliations are ISDIN, Innovation and Development, Barcelona.
- 30 women, ages 36–64, Fitzpatrick II–IV, mild/moderate facial hyperpigmented spots; topical fluid used at least twice daily for 12 weeks.
- Assessments at baseline, day 28 and day 84; investigator assessments included modified MASI, IGA and GAIS; Mexameter measured melanin index; VISIA evaluated spot number/area.
- Reported results include mMASI change −12.15% and IGA photodamage −8.3% at day 28; IGA hyperpigmentation −7.2% at day 84; spot-area melanin index −10.8% at day 28 and −22.1% at day 84; VISIA UV count −10.3% and brown spots −10.5% at day 84. It reports 30 participants' subjective improvement and good tolerability.
- The abstract does not establish a randomized or controlled design; authors are manufacturer-affiliated. Treat as **manufacturer-affiliated conference abstract**, not independent replication or a complete study report.

**Identity crosswalk remains unresolved:** This abstract's n=30, female-only sample and 12-week schedule resembles the Colombian public claim more than the Spanish n=31/day-28-and-84 description, but its age range (36–64), phototypes (II–IV), product description (“new facial suncare formulation with DP-Complex”) and endpoints do not exactly match the Colombian page's stated ages 35–68. It is a plausible source lead, **not verified as the same study or exact marketed SKU**. Do not combine the abstract's results with the Active Unify product claims until ISDIN confirms report ID, tested formula, market/GTIN and correspondence to the web-page claim.

**ISDIN request update:** specifically ask whether EADV 2024 abstract 4411 corresponds to the Data-on-File 2024 reports used on Colombian and Spanish pages; request the full report and explain the n/age/endpoint differences. Keep the abstract as a separate cited evidence record until that mapping is documented.


---

## Pass 6 — bounded public-source sweep (2026-10-19)

**Purpose:** Capture only material new source details found in the final bounded sweep. This is a grouped addendum, not a change to the roadmap or an approval of product claims.

### P4 — SKIN1004 Hyalu-Cica Water-Fit Sun Serum: expanded manufacturer test detail

New official SKIN1004 source pages provide additional test-method detail for the Korean/international Water-Fit Sun Serum. The brand reports:
- In-vivo SPF test: SPF 50.5 ± 7.1, n=10, back-area test site.
- In-vivo UVA protection factor (PFA): 16.56 ± 2.69, n=10; a PPD-method UVA protection factor of 17.3 is also reported for 10 adult volunteers (skin types II–III, ages 22–60).
- In-vitro ISO 24443 test: critical wavelength 376.0 nm and UVA-PF 14.9 ± 0.4, n=4 plates.
- Separate 100-hour hydration test: Corneometer mean 42.38 A.U. before use, 71.32 A.U. immediately after application, and 45.73 A.U. at 100 hours, n=20 adults aged 20–60.
- Dry-environment hydration test: 47.45 A.U. baseline, 80.52 A.U. after application, 79.21 A.U. after dry-environment exposure, n=20.

Sources:
- https://info.skin1004.com/guide/non-comedogenic-sunscreen-for-dry-acne-prone-skin-2
- https://info.skin1004.com/guide/moisturizing-sunscreen-that-wont-leave-skin-feeling-tight

**Evidence status:** Manufacturer-published test summaries. They improve transparency about endpoints and sample sizes but are not independent peer-reviewed replication. Do not transfer these results to the distinct U.S. Water-Fit Sun Serum UV SKU. Obtain the full reports and tested formula/market identification if stronger substantiation is needed.

### P7 — Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum: additional secondary-source detail

A retailer page attributes a four-week consumer self-assessment to 22 participants aged 20–59 and reports 100% agreement on suitability for acne-prone skin, 90% agreement on reduced redness, and 90% agreement that red troubled spots looked improved. It also displays a separate P&K Skin Research Center test dated 2024-09-19 to 2024-10-21, n=20 adults aged 20–59, and a “troubled spot area improved by 108.6%” result.

Source:
- https://vitaliaina.com/products/azelaic-acid-10-hyaluron-serum

**Evidence status:** Secondary retail source, not the original P&K report. The 20-person instrumental/clinical test and 22-person consumer self-assessment appear to be distinct cohorts or endpoints; do not combine their sample sizes or outcomes. Request the serum-specific original report, endpoint definitions, baseline/post values, analysis and formula/GTIN confirmation. Do not transfer evidence from the separately marketed pad.

### P5 — ISDIN Active Unify: older EADV 2013 poster citation lead

Some current ISDIN market pages cite an older EADV 2013 poster: “Efficacy of a new topical formulation in melasma patients,” attributed to Trullas C. et al. A secondary dermatology commentary describes a related EADV 2013 poster record as “Axillary hyperpigmentation – Efficacy of a new topical formulation in melasma patients,” P1443, and reports 33 women aged 31–68 with MASI, physician global assessment, photographs and Mexameter measurements. The commentary notes author affiliations with ISDIN/EVIC/ISDIN Innovation and discusses measurement limitations.

Sources:
- https://www.isdin.com/es-AR/producto/foto-ultra-isdin/active-unify-fusion-fluid-spf-50
- https://www.globale-dermatologie.com/en/quoi-de-neuf-pour-traiter-le-melsma-chloasma-masque-de-grossesse.html

**Evidence status:** Historical, manufacturer-associated conference-poster lead; the original poster/full report was not located in this sweep. The reported axillary hyperpigmentation population and “new topical formulation” do not establish identity with the current facial Active Unify commercial SKU or with the 2024 Data-on-File studies. Do not use as direct proof for the current SKU. Add this as a specific question in the ISDIN request only if the company can identify the poster/formula crosswalk.

### Cross-product conclusion from Pass 6

This sweep did not establish a publicly available, complete independent finished-product clinical report for any of the seven exact commercial SKUs. It did improve the traceability of manufacturer-reported testing for P4, add a secondary-source lead for P7, and identify a historical formulation-identity lead for P5. Manufacturer claims remain manufacturer claims until their source reports and tested-product identity are verified.

**Next action:** No further ledger edit for routine searches. Continue with the already-prepared prioritized manufacturer evidence requests (ISDIN first; COSRX and Clinique next; Anua after), and update this same ledger only when replies or materially decisive new evidence arrive. Keep Issue #406 as the roadmap source of truth; this ledger remains subordinate research continuity only.

---

## Pass 7 — seven-dossier readiness and identity-lock consolidation (2026-10-20)

**Purpose:** Consolidate the current dossier state into one operational view, based on sources already recorded in this ledger and the subsequent dossier review. This is not a new evidence search, not a ProductKnowledge approval, and not authorization to change application behavior.

### A. Cross-product identity and evidence matrix

| ID | Target dossier / market | Source basis currently recorded | Identity lock | Main unresolved items | Evidence interpretation |
|---|---|---|---|---|---|
| P1 | COSRX The 6 Peptide Skin Booster Serum, 150 ml | Official COSRX product page; manufacturer-reported n=20 evaluation (2023-09-18 to 2023-10-31); systematic-review context is not product-specific | PARTIAL — name/size identified as target, but actual package, GTIN and formula version not supplied | Original study protocol/report; current package INCI; exact-product independent study; peptide concentrations | Study outcomes remain manufacturer-reported; ingredient/systematic-review context does not establish efficacy of this serum |
| P2 | Neutrogena Clear & Defend 2% Salicylic Acid Face Wash, 200 ml, UK | Official UK product page; manufacturer reports n=34 and 97% noticed fewer new spots after four weeks | PARTIAL — UK target variant specified; actual package/GTIN and current label not supplied | Original study report and comparator/design; package INCI and warnings; exact-SKU independent evidence | The 97% figure is not a 97% cure rate and must remain attributed to the manufacturer |
| P3 | Garnier Vitamin C Brightening Gel Cleanser, 200 ml, Australia | Official Garnier Australia page and declared INCI | PARTIAL — Australia target and size specified; actual package/GTIN and current label not supplied | Package INCI/warnings; exact-product brightening evidence; concentration of Ascorbyl Glucoside | Ascorbyl Glucoside must not be relabelled as pure L-ascorbic acid; rinse-off evidence cannot automatically be transferred from leave-on products |
| P4 | SKIN1004 Madagascar Centella Hyalu-Cica Water-Fit Sun Serum SPF50+ PA++++, Korean/international | Official international/UK page and official brand test summaries | PARTIAL — target formula family and market scope identified; actual package/GTIN not supplied | Exact label/market confirmation; full test reports; independent exact-product evidence | Keep the US “Water-Fit Sun Serum UV” SKU separate; official brand summaries are manufacturer-published, not independent replication |
| P5 | ISDIN FotoUltra 100 Active Unify SPF50+ | Official Colombia and Spain pages for standard and Color variants; EADV 2024 abstract 4411 is a separate manufacturer-affiliated lead | PARTIAL — multiple market/variant pages identified; no exact gallery package/GTIN crosswalk | Full Data-on-File report(s); mapping of n=30/ages 35–68/12 weeks vs n=31/ages 35–65/days 28 and 84; tested formula and SKU mapping | Keep all page-level descriptions distinct. Do not infer a common cohort, explain the discrepancy by tint status, or equate abstract 4411 with the commercial SKU without confirmation |
| P6 | Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter, 100 ml | Official Clinique product page; 39% visible dark-spot reduction claim after 12 weeks in clinical testing, n=52 women; separate consumer testing n=533 | PARTIAL — target name/size specified; actual package/GTIN and market-specific INCI not supplied | Original clinical report/protocol; exact 100 ml-market INCI; independent exact-formula studies | The n=52 clinical result and n=533 consumer test are separate datasets/endpoints and must never be combined |
| P7 | Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum, 30 ml | Official Anua product page; manufacturer 90% participant-agreement statement; secondary retailer reports separate 22-person consumer and 20-person P&K test details | PARTIAL — target serum identified by name/size, but actual package/GTIN and formula version not supplied | Original serum-specific report; endpoint definitions and underlying values; current package INCI/warnings; independent exact-product evidence | Do not combine the 22- and 20-person reports or transfer results from the separate azelaic-acid pad |

### B. Profile field disposition

For all seven dossiers, use the following working disposition until an actual package or authoritative version-specific source resolves it:

- **Name / brand / target market / nominal size:** recorded as the intended research target, not proof that a gallery item has been uniquely identified.
- **GTIN / barcode / actual package revision:** UNKNOWN until observed on the gallery sample or documented by a version-specific authoritative source.
- **INCI / concentrations:** use only the source or label that matches the market and formula. Do not infer undeclared concentrations.
- **Directions / warnings:** retain the exact wording and market scope of the cited label; do not promote a secondary summary into a package-level fact.
- **Manufacturer efficacy claims:** record with attribution, population, duration and endpoint where available. Do not relabel as independent evidence, RCT, cure, treatment indication or guaranteed outcome without supporting documentation.
- **Independent finished-product efficacy:** NOT ESTABLISHED in the bounded sources currently recorded. This means not established from sources checked, not proof that no study exists.
- **ProductKnowledge / QA / activation:** none of these dossiers is approved, written to ProductKnowledge, or activated by this research pass.

### C. Correction and consistency control

A prior conversational summary associated Clinique’s 39% clinical result with the 533-person consumer-test sample. That association is incorrect. The ledger’s existing distinction is retained: **n=52 for the 39% clinical-testing claim; n=533 for separate consumer testing.** Do not merge their endpoints or sample sizes.

Some prior conversational summaries used shortened descriptions of product claims and tests. Where they differ from the more specific source notes in this ledger, this ledger’s product-, market- and study-specific distinctions govern. The summaries are not new source evidence.

### D. Completion decision and next action

- Seven research dossiers exist; all seven remain **PARTIAL for identity lock** because no actual gallery package/GTIN crosswalk has been supplied.
- Research summaries are useful for review but do not satisfy Gate 2 by themselves: package identity, per-field provenance, warnings, and study limitations must remain auditable.
- Do not block routine dossier work on every unresolved study discrepancy. Record the exact reported variants and proceed with the supported facts; reserve deeper follow-up for evidence that materially changes product identity, claim meaning, safety/warnings or acceptance.
- The next decisive action remains the already-prepared manufacturer evidence requests (ISDIN first; COSRX and Clinique next; Anua after). **REQUEST TEXT PREPARED; NOT SENT.** No outbound request is claimed.
- Keep Issue #406 as the sole roadmap and this existing PR #411 ledger as subordinate research continuity. No new Issue/PR, code/schema/API/UI/database/test change, ProductKnowledge write, QA approval, activation or merge is included in this pass.

---

## Pass 8 — proposed per-field acceptance matrix for PO review (2026-10-20)

**Purpose:** Convert the seven-dossier review into a small, reviewable proposal for field-level acceptance. This is a proposal for PO decision, not an approved product profile, not an executable acceptance contract, and not authorization to implement or populate ProductKnowledge.

### A. Repository search disposition

A focused read-only GitHub code search for an authoritative ProductKnowledge profile / required-field / field-acceptance matrix returned no matching files. This is consistent with the existing Issue #406 audit disposition: the authoritative profile, required fields per profile, and acceptance criteria per field have **not been established** in the reviewed repository evidence. Search results are bounded; they do not prove that no relevant artifact exists anywhere outside the inspected repository/index.

**Decision boundary:** Do not infer mandatory fields from the current nullable ProductKnowledge columns, Product Intake/G8 contracts, or these seven example products. The proposal below must be explicitly approved or revised by the PO before it can become an executable acceptance mapping.

### B. Proposed field groups and minimum acceptance checks

| Field group | Candidate fields / content | Minimum acceptance check proposed for PO review | If evidence is missing or mismatched |
|---|---|---|---|
| Product identity | Brand; product name; dosage/form/type where relevant; market/country; variant/formula/version; nominal pack size; GTIN/barcode when present | Values must identify one target SKU/version within a declared market scope. Package or authoritative version-specific source must support the identity. Name similarity alone is insufficient. | Keep identity PARTIAL; GTIN may remain UNKNOWN if not present/observed. Do not merge variants. |
| Ingredient declaration | Full INCI / ingredient list; declared active ingredient and concentration, if explicitly stated | Cite a current package label or official source applicable to the exact market/version. Preserve source wording; do not infer undeclared concentrations or equate ingredient derivatives without support. | Field remains UNKNOWN or PARTIAL; do not fill by inference from another market/version. |
| Directions and warnings | Directions for use; precautions; warnings; relevant package statements | Preserve wording and market/version applicability from the exact label or authoritative source. Distinguish a secondary summary from label-level evidence. | Mark not verified for the target package; do not silently substitute directions from a similar SKU. |
| Manufacturer claims | Benefit, performance, appearance, or usage claims | Attribute explicitly to the manufacturer and retain the exact endpoint, population, duration and numerical result when published. Do not relabel a marketing/consumer statement as independent evidence or medical treatment efficacy. | Claim may be recorded as a sourced manufacturer claim with limitations; it does not satisfy an independent-efficacy requirement. |
| Study/test supporting a claim | Sponsor, tested product/version, study type, sample size/population, duration, comparator/control, endpoint, measurement method, result, analysis, conflicts of interest, report/source | Each available item must be source-backed. Study identity must be linked to the exact tested product before attributing results to a specific commercial SKU. Do not infer randomization, blinding, control, peer review, or independence. | Record only the confirmed study details; unresolved design fields remain UNKNOWN. Keep conflicting reports separate until reconciled. |
| Independent finished-product evidence | Independent study/publication and its link to exact product/formula | Evidence must evaluate the exact finished product or clearly explain limits on applicability. Ingredient-level research is contextual only. | Use NOT ESTABLISHED IN SOURCES CHECKED, not “no evidence exists”; do not infer finished-product efficacy from ingredients alone. |
| Source provenance | Source URL/title/publisher; source type; market/version; publication or update date if available; retrieval date; exact supported field/claim; limitations | Every accepted factual value/claim must be traceable to a source whose scope matches the field. Manufacturer, retailer, regulator, primary study and independent publication must remain distinguishable. | Field does not pass acceptance until adequate provenance is recorded. |
| Conflicts and review state | Conflicting values; scope of conflict; review disposition; reviewer/decision record when applicable | Conflicts must be explicit and scoped to the affected field/version. Resolve only with evidence or an authorized decision; do not invent a reconciliation. | A blocking unresolved conflict prevents SUPPORTED for the affected profile scope; use CONFLICT only when the conflict is actually established and material. |

### C. Approved status semantics; profile-level mapping still not executable

The Product Owner has already approved the status meanings in the decision recorded at https://github.com/vahidmaghsoudi2/hbi/pull/411#issuecomment-6277900118. That decision is semantic approval, not implementation authorization.

- **NULL:** not assessed, or a legacy record whose status has not yet been adjudicated.
- **UNKNOWN:** assessed, but no acceptable/usable evidence exists within the applicable scope.
- **PARTIAL:** some required fields are covered, but not all.
- **SUPPORTED:** all required fields in the defined profile/scope meet their acceptance criteria, with no blocking unresolved conflict.
- **CONFLICT:** an unresolved blocking conflict affects the applicable scope.

These statuses describe evidence/coverage only. They are not safety certification, regulatory approval, a clinical efficacy verdict, or probability values. The approved meanings do not define which profile applies, which fields are required for that profile, or the field-level acceptance/source rules. Those details remain open in the matrix below; implementation remains unauthorized until the applicable matrix is approved and a separate implementation authorization is recorded.

### D. PO decisions required before implementation

1. Approve or revise the product-profile set and define each profile's intended scope.
2. Select the required fields for each profile; distinguish required, conditional and optional fields.
3. Approve the field-level acceptance checks and what source classes are acceptable for each field.
4. Define when a conflict is material/blocking and who may resolve it.
5. Confirm whether exact market/variant/pack identity is a prerequisite for product-level SUPPORTED.
6. Only after these decisions, map the approved matrix to ProductKnowledge fields and separately authorize any implementation.

### E. Seven-dossier application (research only)

The current seven dossiers do not yet pass a unique gallery-package identity lock: no actual gallery package/GTIN crosswalk has been supplied. Their names, markets and nominal sizes identify research targets, not proof of the identity of a physical gallery item. Keep the existing dossier-specific limits and source records in Pass 7. Do not mark any of the seven SUPPORTED or write them to ProductKnowledge based on this proposal.

**Disposition:** Proposed matrix for PO review; executable acceptance mapping remains **BLOCKED / NOT SPECIFIED** until approved. Gate 0 remains **PARTIAL**. No code, schema, API, UI, migration, database, test, ProductKnowledge, QA, or activation change is included. No new Issue or PR is created.


---

## Pass 9 — bounded ProductKnowledge rebuild safeguard (2026-10-20)

**Implementation change:** `ProductKnowledgeService.update_from_evidence()` now explicitly clears `evidence_status` during every rebuild. A rebuild filters pending and conflicting evidence and replaces the current field values; carrying forward a previously assigned status could therefore leave a stale status attached to a changed evidence set. Until the PO-approved profile/required-field matrix is executable, the rebuild leaves status NULL rather than deriving SUPPORTED/PARTIAL/UNKNOWN/CONFLICT from an unapproved mapping.

**Regression test added:** `tests/test_product_knowledge_service_rebuild.py` checks that a rebuild with no eligible evidence clears stale knowledge fields, refs, confidence and `evidence_status`, and does not consume pending or conflicting claims.

**Validation status:** The code and regression test were committed to this existing research branch. A workflow-run lookup for the test commit returned no runs; therefore this change is **not yet reported as CI-passed**, and the test has not been represented as executed locally. Verify the PR workflow result before considering this safeguard validated.

**Scope boundary:** This does not implement the full status mapping, approve a profile matrix, lock the seven physical product identities, or authorize ProductKnowledge writes for the seven research dossiers. Those remain separate gates. No schema/API/database migration or new Issue/PR was created.


---

## Pass 10 — CI validation of bounded rebuild safeguard (2026-10-21)

**Validation result: PASS on the tested commit.** The three GitHub Actions workflows associated with implementation/ledger commit `a235f9d9b58798e6f29cdfaea7a5404ab2a82655` completed successfully:

- HBI CI #1662: https://github.com/vahidmaghsoudi2/hbi/actions/runs/39477476595
  - Python application/test compilation: success
  - G8 regression bundle: success
  - Strict-coverage test suite: success
  - Frontend build: success
  - Governance test suite: success
  - Isolated pilot smoke: success
- HBI Pilot Browser Proof #475: https://github.com/vahidmaghsoudi2/hbi/actions/runs/39477476548
  - Real-browser proof: success
- HBI Auto Tasks #215: https://github.com/vahidmaghsoudi2/hbi/actions/runs/39477476435
  - PyCompile and pytest + coverage: success

This validates the committed regression test and the repository checks executed by these workflows for that commit. It does **not** mean the full Product Knowledge project or status mapping is complete, and it does not prove that any of the seven researched products is a verified physical gallery item.

**Current disposition:** The stale-status clearing safeguard is CI-validated. The profile/required-field acceptance matrix remains suspended pending PO approval; full `evidence_status` mapping remains unauthorized until that decision and a separate implementation authorization are recorded. P1–P7 remain PARTIAL for physical identity lock pending package photos or a reliable GTIN-to-formula/market crosswalk. PR #411 remains open and unmerged; no merge, rebase, schema/API/database migration, ProductKnowledge population for the seven dossiers, or manufacturer outreach is authorized by this pass.


---

## Pass 11 — PO matrix approval and current gate correction (2026-10-22)

**Live-source reconciliation:** Product Owner approval of the Pass 8 profile / required-field / source / field-acceptance matrix is recorded in [Issue #406 comment 6324481621](https://github.com/vahidmaghsoudi2/hbi/issues/406#issuecomment-6324481621). The earlier Pass 10 statement that this matrix is still awaiting PO approval is historical to its 2026-10-21 recording time and is superseded for current status by that explicit approval. Pass 8 remains the approved matrix basis; this note does not silently change its contents.

**Current gate disposition:**
- **Matrix approval:** APPROVED for the next planning gate.
- **Full `evidence_status` mapping / application behavior:** NOT AUTHORIZED. A separate, explicit implementation authorization with scope is still required before implementation or ProductKnowledge writes.
- **P1–P7 physical identity lock:** PARTIAL. Obtain actual package photos and/or a reliable GTIN-to-exact-formula-and-market crosswalk before treating a gallery item as uniquely identified.
- **Evidence requests to manufacturers:** PREPARED, NOT SENT. No outbound request is authorized by this status correction.
- **PR #411:** remains the sole working ledger and is open/unmerged.

**Current verified baseline:** branch `docs/product-research-ledger-seven-products-20261019`, head `7319d36f8e97bcb010337c9508abfd280cb5c052`. The three Pass 10 documentation workflows on this SHA completed successfully: [HBI CI #1663](https://github.com/vahidmaghsoudi2/hbi/actions/runs/39659682415), [Pilot Browser Proof #476](https://github.com/vahidmaghsoudi2/hbi/actions/runs/39659682435), and [Auto Tasks #216](https://github.com/vahidmaghsoudi2/hbi/actions/runs/39659682409).

**Next action:** collect physical package/GTIN evidence for P1–P7, preserving each product's market/formula boundaries. Do not implement the full status mapping or write product rows until separate scoped implementation authorization is recorded. Keep the SKIN1004 Korean/international and US variants separate; keep Clinique n=52 clinical testing distinct from n=533 consumer testing; keep Anua serum and pad evidence separate; retain the unresolved ISDIN source discrepancies without guessing. No new Issue/PR, merge, rebase, force-push, schema/API/database change, or manufacturer outreach is part of this pass.


---

## Research pass 2 — common skin-concern coverage matrix (V1)
**Purpose:** Turn the seven ingredient dossiers into one consistent first-pass view of common skin concerns. This is a research crosswalk, not a final product recommendation, clinical claim, approved ProductKnowledge record, or implementation authorization.

### V1 common concern groups

- **C1 — Acne/oil/congestion:** oily appearance, comedones and acne-prone skin. These are related but not interchangeable outcomes.
- **C2 — Dryness/dehydration/barrier comfort:** tightness, roughness and moisture retention; hydration claims do not establish barrier repair.
- **C3 — Sensitivity/redness/irritation:** tolerability and visible redness. Cosmetic soothing is not a diagnosis or treatment claim for rosacea, eczema or other disease.
- **C4 — Dark spots/post-inflammatory hyperpigmentation/uneven tone:** distinguish spot appearance from diagnosis-specific treatment.
- **C5 — UV protection and sun-related worsening:** protection must be tied to the exact sunscreen formula/market and label directions.
- **C6 — Texture/fine lines/dull appearance:** cosmetic appearance outcomes, not proof of structural or long-term clinical change.

### Product-to-concern research matrix

| Product | Ingredient/formula basis already recorded | Candidate concern groups for V1 review | Current evidence interpretation | Limitation / next check |
|---|---|---|---|---|
| P1 COSRX 6 Peptide Booster | Peptides, niacinamide and humectant/supporting ingredients listed by manufacturer | C2, C4, C6 | Manufacturer reports moisture, texture, clarity, radiance and density outcomes in n=20; independent exact-formula efficacy is NOT ESTABLISHED in reviewed sources. | Retrieve full protocol; do not infer peptide concentrations or transfer evidence from unrelated peptide products. |
| P2 Neutrogena Clear & Defend UK 2% Salicylic Acid Wash | Manufacturer-declared 2% salicylic acid; surfactants, glycerin, panthenol and fragrance | C1; monitor C2/C3 for tolerability | Salicylic acid provides a plausible ingredient-level rationale for acne/congestion; manufacturer reports fewer new spots in n=34, but full protocol and independent exact-SKU evidence remain NOT ESTABLISHED. | Verify current package INCI/warnings. Rinse-off exposure and frequency affect interpretation; do not label the 97% statement as a cure rate. |
| P3 Garnier Vitamin C Brightening Gel Cleanser, Australia | Ascorbyl Glucoside, salicylic acid, surfactants, glycerin, panthenol and fragrance components | Cleansing as a supporting function; C4 and C1 remain exploratory | Listed ingredients justify investigation, not a finished-product brightening or acne conclusion. | Verify current package formula; do not equate Ascorbyl Glucoside with pure L-ascorbic acid or transfer leave-on serum evidence to a rinse-off cleanser. |
| P4 SKIN1004 Hyalu-Cica Water-Fit Sun Serum, Korean/international dossier | International formula's UV filters plus humectant/skin-conditioning ingredients as recorded in the dossier | C5, C2; C4 only as prevention of UV-related worsening, not spot treatment | Sunscreen function is the primary rationale; hydration/soothing outcomes are manufacturer claims unless independently supported. | Keep US SPF50 drug-label SKU separate. Confirm actual market label and directions; do not treat sunscreen as a standalone treatment for existing pigmentation. |
| P5 ISDIN FotoUltra 100 Active Unify SPF50+ | Sunscreen filters and marketed spot-care ingredients; exact formula depends on market | C5, C4 | Manufacturer reports spot-intensity and spot-area changes in n=31; full protocol and independent replication are NOT ESTABLISHED in reviewed sources. | Pin all ingredient and performance claims to a specific market/version; obtain original report if available. |
| P6 Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter | Ascorbyl Glucoside, Dimethoxytolyl Propylresorcinol and salicylic acid listed in dossier | C4; C6 as a secondary appearance outcome only if source supports it | Manufacturer reports a 12-week dark-spot result in 52 women; separate consumer test must remain a separate data set. | Exact active concentrations and full protocol remain UNKNOWN from sources reviewed; do not infer treatment efficacy for melasma or all pigmentation disorders. |
| P7 Anua Azelaic Acid 10% + Hyaluron Serum | Manufacturer-declared 10% azelaic acid; niacinamide, betaine salicylate, panthenol, humectants and supporting ingredients | C1, C4 (post-inflammatory marks), C2; C3 only with explicit tolerability caveat | Ingredient-level context supports investigating acne and post-inflammatory marks; the manufacturer's 90% agreement result lacks a full public protocol in reviewed sources. | Verify current market INCI/warnings. Do not infer suitability for every redness-prone user or transfer evidence from the separate pad. |

### Coverage and relationship rules

1. The groups above are a **research taxonomy**, not replacements for the canonical skin-problem list P01–P61.
2. Do not assign official problem IDs from memory or name similarity. Before linking a product to a problem record, inspect the canonical map and confirm that the exact problem concept and its current status permit this relationship.
3. A candidate group in the table means “investigate this relationship,” not “the product is suitable,” “the product treats this condition,” or “the relationship is approved.”
4. Ingredient-level rationale, manufacturer claim, independent finished-product evidence and a final product–problem relationship must remain distinguishable.
5. A concern is not “covered” merely because a product row mentions it. Coverage requires a source-backed relation, version match, limitation statement and appropriate review state.
6. The first release may honestly leave a concern uncovered or UNKNOWN. Do not manufacture coverage to make the matrix look complete.

### Review requested from Grok — independent challenge pass

Please review this matrix against the seven dossiers and the actual official skin-problem map, without changing code, schema, UI, database, product lifecycle or the Product Intake contract. Return findings only in the existing PR #411 discussion:
- flag any ingredient/market/version mismatch;
- challenge every product–concern candidate that overstates ingredient-level evidence as finished-product efficacy;
- identify the exact canonical P01–P61 problem IDs only where the map supports the concept and status;
- mark unsupported links as UNKNOWN / NOT VERIFIED rather than guessing;
- prioritize the smallest corrections needed for a defensible V1 covering common skin concerns.

No new Issue/PR, no implementation, and no claim of product registration or acceptance is authorized by this review request.


---

## Research pass 3 — cautious crosswalk to canonical P01–P61 IDs
**Source checked:** `SKIN_PROBLEM_SPACE_MAP_V0.1.md` on `master`, blob `c57ce7edbcee513dcb60b735ce91b98de22d8aa2`. The map explicitly says its designation does not imply medical validation, Need acceptance, treatment authorization, product mapping or recommendation permission.

| Product | Canonical concepts to investigate | Boundary |
|---|---|---|
| P1 COSRX | P02 dehydration/impaired moisture retention; P43 uneven skin texture; P17 hyperpigmentation only if a separate source supports that exact outcome | P43 boundary is open; fine lines/radiance do not have a directly equivalent dedicated ID in this map. Do not force-match them. |
| P2 Neutrogena UK wash | P03 oily skin/seborrhoea; P08 acne; P09 open comedones; P10 closed comedones | Ingredient-level salicylic-acid rationale is not a confirmed product relationship; P11 inflammatory lesions and P12 nodular/cystic acne must not be inferred from the broad word “acne.” |
| P3 Garnier cleanser | P03 oily skin and P08/P09/P10 only as exploratory concepts for review | Current record is a rinse-off cleanser; the listed ingredients do not establish efficacy against these specific problem units. Leave links unapproved until product-specific evidence and exact formula are checked. |
| P4 SKIN1004 international sunscreen | P22 sun-related pigmentation; P17 dark spots only as a distinct pigmentation presentation; P02 dehydration only if the hydration claim is supported for this version | P22 is a context/presentation relation. Sunscreen is relevant to UV protection/prevention, not proof of treatment for existing pigmentation. Keep US SKU separate. |
| P5 ISDIN Active Unify | P17 hyperpigmentation/dark spots; P19 post-inflammatory hyperpigmentation only if source supports this subtype; P22 sun-related pigmentation | Manufacturer-reported spot outcomes remain manufacturer claims until protocol and independent evidence are reviewed. P51 chronic UV damage is context/not Need-level and must not be used to imply treatment of chronic damage. |
| P6 Clinique Dark Spot Corrector | P17 hyperpigmentation/dark spots; P19 post-inflammatory hyperpigmentation only if supported by the exact claim/evidence | Do not map to P18 melasma as a treatment claim; the map labels P18 a Clinical Condition/Clinical Anchor. Cosmetic dark-spot claims do not authorize disease-treatment advice. |
| P7 Anua Azelaic Acid 10% serum | P08 acne; P13 acne aftermath/discoloration; P19 post-inflammatory hyperpigmentation; P03 oily skin only if supported; P24 persistent redness only as an exploratory tolerability/appearance question | P13 is a cross-shelf sequela and P19 a pigmentation sequela. The presence of azelaic acid does not establish effectiveness of this serum for every subtype. P24 must not be treated as rosacea treatment; P26 is a Clinical Condition. |

### Crosswalk disposition

- These are **candidate ID references for research**, not approved Problem↔Product relationships.
- No P01–P61 item is marked Accepted or made eligible for recommendation by this crosswalk.
- The Map's structural designation is not medical validation; current working records also state that Product mapping has not started. Respect that boundary.
- Before creating any final relationship, confirm the exact product version, the relevant claim/evidence, the problem unit's current disposition in the Map and Working Records, and the authorized Product Intake relationship contract.
- If no exact canonical concept fits, record “no direct map match / gap” rather than inventing a new ID or broadening a clinical condition.


---

## Research pass 4 — Grok red-team dispositions and recommendation gate
**Input:** Independent Grok critique supplied for the V1 matrix and canonical P01–P61 crosswalk. This section records the critique as a research disposition; it does not accept any Problem, create a Product↔Problem relation, authorize recommendations, or approve PR merge.

### Mandatory labels for every candidate cell

- `candidate_only` — concept may fit the Map, but product/version-specific evidence is not yet sufficient for a verified relationship.
- `manufacturer_claim_only` — support currently rests on an identified manufacturer claim/endpoint; do not describe it as independently established efficacy.
- `not_linked` — do not create a Product↔Problem link unless exact-SKU evidence and the canonical boundary are verified.
- `UNKNOWN / NOT VERIFIED` — formula, endpoint, protocol, or relevant source remains unresolved.

**Recommendation gate:** For P1–P7, “Is the consultation engine authorized to recommend this product for this problem based on this research matrix?” = **NO / NOT AUTHORIZED**. The matrix is not an approved recommendation input. No Problem ID is accepted as a Need by this document. This gate can only be reconsidered through the existing HBI governance/PO path after exact-version identity, evidence QA, canonical boundary review, and the authorized relationship contract are satisfied.

### Corrected candidate dispositions

| Product | Problem ID / concept | V1 disposition | Required condition before any approved link |
|---|---|---|---|
| P1 COSRX 6 Peptide Booster | P02 dehydration / moisture retention | `candidate_only` | Same-SKU hydration endpoint or adequate direct product evidence; verify P02 boundary/working-record disposition. |
| P1 COSRX | P17 hyperpigmentation | `not_linked` | Do not link from peptides/niacinamide alone; require the exact product study to measure the relevant dark-spot outcome and verify Map boundary. |
| P1 COSRX | P43 uneven texture | `candidate_only` only if wording matches the Map definition | Inspect the P43 definition and same-SKU endpoint; do not force-match texture, fine lines, radiance or density as equivalent concepts. Otherwise `not_linked`. |
| P2 Neutrogena UK 2% SA wash | P08 acne | `manufacturer_claim_only` + `candidate_only` | Verify exact current UK SKU/INCI, manufacturer endpoint and study protocol; rinse-off limitations must remain explicit. No recommendation authorization. |
| P2 Neutrogena | P03 oily skin; P09 open comedones; P10 closed comedones | `not_linked` until exact claims/endpoints support each concept | Do not infer P09/P10 from the general word “acne.” Never infer P11/P12 from a broad acne claim. |
| P3 Garnier Vitamin C cleanser | P03, P08, P09, P10, P17 | `not_linked` | Current rationale is ingredient/category-level and insufficient for an official product link. Verify exact market formula and direct finished-product endpoint first. |
| P4 SKIN1004 international/Korean sunscreen | P22 sun-related pigmentation/UV context | `candidate_only` for prevention/context, not spot treatment | Verify exact market SKU, filters and label directions. Keep US version separate. |
| P4 SKIN1004 | P17 existing hyperpigmentation; P02 hydration | `not_linked` unless same-version evidence directly supports the specific endpoint | Sunscreen use alone does not prove treatment of existing pigmentation; hydration requires same-version evidence. |
| P5 ISDIN Active Unify | P17 hyperpigmentation/dark spots | `manufacturer_claim_only` + `candidate_only` | Retrieve full report/protocol and verify exact market formula; preserve reported percentages as manufacturer claims unless independently established. |
| P5 ISDIN | P19 post-inflammatory hyperpigmentation | `not_linked` until population and endpoint explicitly cover PIH | Do not infer PIH from a general dark-spot outcome. P18 melasma is not to be linked absent explicit evidence for that exact SKU and valid clinical boundary. |
| P5 ISDIN | P22 sun-related pigmentation/UV context | `candidate_only` as context/prevention | Must not imply treatment of chronic UV damage or use P51 as an accepted Need; P51 is context/not Need-level. |
| P6 Clinique Dark Spot Corrector | P17 hyperpigmentation/dark spots | `manufacturer_claim_only` + `candidate_only` | Retrieve full protocol and endpoint; keep n=52 study separate from n=533 consumer-test data. |
| P6 Clinique | P19 PIH | `not_linked` unless the same-SKU study explicitly covers PIH | Do not infer a PIH relationship from a generic dark-spot claim. P18 melasma is not a default match or treatment claim. |
| P7 Anua 10% azelaic acid serum | P08 acne; P13 acne aftermath; P19 PIH | `candidate_only` at most; otherwise `not_linked` pending same-serum evidence | General azelaic-acid literature is ingredient-level, not finished-serum proof. Do not transfer the separate pad study to the serum. |
| P7 Anua | redness / P24 persistent redness; P26 rosacea | `not_linked` for recommendation; tolerability may be researched separately | Redness, irritation and rosacea are not interchangeable. Do not imply rosacea treatment or general suitability for all redness-prone users. |

### Evidence retrieval queue (same exact product/version)

1. **P1 COSRX:** obtain complete manufacturer protocol for reported n=20 test; confirm endpoints, duration, formula version and whether hydration/texture/dark spots were measured. Do not infer active concentrations.
2. **P2 Neutrogena:** capture current UK package/INCI and warnings for the 2% salicylic-acid wash; retrieve protocol behind the n=34 new-spots statement. Do not label a promotional percentage as cure rate.
3. **P3 Garnier:** confirm exact market/product packaging and current INCI; until a direct finished-product endpoint is available, leave brightening/acne links unlinked.
4. **P4 SKIN1004:** establish which exact Korean/international SKU is the dossier target; retain a separate US SKU dossier. Verify sunscreen label and only record hydration/soothing claims when supported for the target version.
5. **P5 ISDIN:** request the full report behind the n=31 spot-intensity/area results, including population, endpoint definitions, duration, version/market and protocol.
6. **P6 Clinique:** request the complete report for the 12-week n=52 result; separately record the n=533 consumer test, with distinct methodology and claims.
7. **P7 Anua:** confirm current serum packaging/INCI and warnings; request the full protocol behind the 90% agreement result. Keep evidence about the separate pad strictly separate.

### Canonical Map / Working Records boundary

The Map and Working Records are structural references, not medical validation or recommendation permission. The Working Records state that Problem Bank V1, Need extraction/acceptance, and Product mapping have not started; all listed P items remain Accepted=No / Undetermined where recorded. Therefore:
- No Product↔Problem relationship is approved by this pass.
- No product recommendation is authorized by this pass.
- Do not change Problem acceptance or status to make product research appear complete.
- If the exact concept is absent or the boundary is unresolved, record `not_linked` / `UNKNOWN`, not a new P ID.

### Review outcome

Grok's independent challenge is incorporated as constraints for the next research pass. It is not an approval to merge this PR or a claim that the evidence retrieval queue is complete. No code, schema, API, UI, database or operational product record is changed by this documentation update.


---

## Research pass 5 — official-source evidence audit (2026-10-24)
**Method:** Targeted public-web retrieval of official manufacturer pages, checked after Grok's critique. This pass records what the pages actually disclose; a manufacturer page is evidence of the manufacturer's label/claim, not independent verification of efficacy. No final Product↔Problem link is created.

### Source-level findings

| Product | Official source observed | What is directly supported by the source | Disposition after source check |
|---|---|---|---|
| P1 COSRX The 6 Peptide Skin Booster Serum | https://www.cosrx.com/collections/all/products/the-6-peptide-skin-booster-serum | Official page lists six peptides, niacinamide, hyaluronic acid, N-acetylglucosamine and allantoin; reports a test of 20 subjects with moisture, texture, clarity, radiance and density figures and names Dermacosmetic Skin Science Laboratory Co., Ltd. | `manufacturer_claim_only` for the reported endpoints. The public page gives dates (2023-09-18 to 2023-10-31) but not a full protocol. P17 dark-spot link remains `not_linked` unless the exact endpoint clearly measures the canonical P17 concept. Do not infer concentrations or independent replication. |
| P2 Neutrogena Clear & Defend 2% Salicylic Acid Face Wash, UK | https://www.neutrogena.co.uk/skincare/cleansers-washes/clear-and-defend-daily-wash | Official UK page states 2% salicylic acid, lists the INCI, says suitable for spot-prone/oily skin, and reports “97% noticed less new spots in 4 weeks” with clinical grading in 34 subjects. It warns that product/ingredients may change. | `manufacturer_claim_only` for the n=34 result; P08 may remain `candidate_only` for review. P09/P10 remain `not_linked` absent direct endpoints for open/closed comedones. The 97% figure is not a cure rate and the full protocol is not disclosed on the page. |
| P3 Garnier Vitamin C Brightening Gel Cleanser, Australia | https://www.garnier.com.au/about-our-brands/skin-active/garnier-skin-active-vitamin-c-brightening-gel-cleanser-200ml | Official Australia page identifies it as rinse-off and lists sodium laureth sulfate, coco-betaine, glycerin, lemon extract, ascorbyl glucoside, panthenol, salicylic acid, fragrance allergens and perfume. It explicitly says lists can change and the package should be checked. | Exact market formula is now source-backed at page level, but direct finished-product efficacy endpoints for acne/comedones or pigmentation were not located in this pass. Keep official problem links `not_linked`; ingredient list alone is not efficacy evidence. |
| P4 SKIN1004 Hyalu-Cica Water-Fit Sun Serum, Korean/international formula | https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-spf50-pa?country=BE&variant=45493174337782 | Official international page lists organic UV filters, niacinamide, glycerin, centella and hyaluronic-acid forms, and SPF50+ PA++++. | Supports identity/ingredient review and UV-protection function only for this market formula. P22 can remain a context/prevention `candidate_only`; no treatment claim for existing P17 pigmentation. Keep separate from US SKU. |
| P4 SKIN1004 Water-Fit Sun Serum UV, US formula (separate SKU) | https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-uv?variant=50346297852150 | Official US page identifies a separate sunscreen drug product, with active filters avobenzone 2.7%, homosalate 13.6%, octisalate 4.5%, octocrylene 9%, plus a different inactive-ingredient list. | Confirms the market/version split. Do not copy US active ingredients into the Korean/international dossier or vice versa. |
| P5 ISDIN FotoUltra 100 Active Unify SPF50+ | No exact-version official protocol/report was verified in this retrieval pass. Search results included a separate ISDIN FOTOULTRA 100 SPOT PREVENT study/product; it is not the same SKU. | The existence of evidence for SPOT PREVENT does not establish evidence for Active Unify. | Keep exact-SKU endpoints `UNKNOWN / NOT VERIFIED`; do not import Spot Prevent data. Request the Active Unify report, market label and endpoint definitions. |
| P6 Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter | https://www.clinique.com/product/4034/68008/skincare/serum/even-better-clinicaltm-radical-dark-spot-corrector-interrupter | Official page states a 39% visible reduction in dark spots after 12 weeks in clinical testing of 52 women; separately reports consumer testing on 536 women for radiance/soothing. | Record the clinical n=52 and consumer n=536 as separate datasets. Both are manufacturer-reported. Full protocol and specific PIH/melasma endpoint are not established from the page. P17 `manufacturer_claim_only`/candidate; P19 `not_linked` absent explicit PIH endpoint; P18 not linked by default. |
| P7 Anua Azelaic Acid 10% + Hyaluron Serum | No official product page with full current formula and complete methodology for the reported 90% result was verified in this retrieval pass. | Public general azelaic-acid literature cannot establish this serum's finished-product efficacy; a separate pad's results are not transferable. | Keep formula/version and 90% endpoint `UNKNOWN / NOT VERIFIED` pending exact official source, package INCI and protocol. No official P08/P13/P19 link. |

### Evidence QA corrections and next retrieval actions

1. Source links above establish manufacturer identity/claims only. They do not independently validate the clinical claim or establish a product recommendation.
2. COSRX, Neutrogena and Clinique have identifiable manufacturer-reported sample sizes/endpoints on official pages; full methods remain incomplete. Keep `manufacturer_claim_only` until QA is adequate.
3. Garnier's exact Australia ingredient list is available, but direct efficacy evidence for the target problems remains absent; keep links `not_linked`.
4. SKIN1004 market split is directly confirmed by the official pages; keep separate formula dossiers and never merge INCI lists.
5. For ISDIN Active Unify and Anua serum, this pass did not verify the required exact-SKU evidence. The similar ISDIN Spot Prevent product and Anua pad are explicit non-transfer cases.
6. The next evidence action is to obtain package photos/official labels and complete reports for ISDIN Active Unify and Anua serum, plus full protocols for COSRX, Neutrogena and Clinique. Until then, all seven remain **NO / NOT AUTHORIZED** for consultation-engine recommendation based on this matrix.

No code, schema, API, UI, database, ProductKnowledge record, or approved Product↔Problem relationship was changed by this pass.

---
## Research pass 6 — exact official-page follow-up and correction register (2026-10-24)

**Continuity rule:** This pass is appended after Research pass 5. Passes 1–5 and all earlier sections remain preserved verbatim. This pass does not replace the earlier record; where it finds a better source, it explicitly corrects the earlier *search disposition* while retaining the historical fact that the source was not found during Pass 5.

### 6.1 P7 — Anua Azelaic Acid 10 Hyaluron Redness Soothing Serum

**Official exact-product page now verified:** https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum

The current official product page identifies the serum, states a 10% azelaic-acid formulation, lists the ingredient declaration, describes redness/blemish/oil-control/hydration positioning, and gives gradual-use directions (start 1–2 times weekly and increase as tolerated). It labels the testing results “Non-comedogenic, Low-Irritation.” The page does **not** disclose a full study protocol, sample size, comparator, validated endpoints, statistical analysis, or the underlying report for those labels.

Official brand routine page: https://pages.anua.com/solutions/redness-prone-routine-sensitive-skin reports that 90% of participants agreed that the appearance of red troubled spots improved, and attributes the statement to a 2026 Anua US clinical study. The public summary still does not disclose enough methodology to independently assess the result.

**Correction to Pass 5:** Pass 5's wording that an official product page had not been verified was accurate for that retrieval pass but is superseded as a *current retrieval status* by this Pass 6 source check. The correct current status is: exact-product official page and manufacturer claim FOUND; complete protocol/report NOT VERIFIED. Keep manufacturer_claim_only for the 90% statement, and do not promote it to independent efficacy evidence.

The official separate-pad page describes a different product and its own study (21 participants, 2025-01-20 to 2025-02-19): https://anua.com/products/azelaic-10-hyaluron-redness-soothing-pad. That study remains explicitly NON-TRANSFERABLE to the serum.

**Disposition:** P7 formula/brand claim is source-backed at official-page level; physical package, market/GTIN and current package-to-page match remain UNVERIFIED until a package/label is available. No P08/P13/P19/P24 relationship is approved. Ingredient-level azelaic-acid evidence and the pad study do not prove this serum's finished-product efficacy.

### 6.2 P5 — ISDIN FotoUltra 100 Active Unify SPF50+

**Official UK exact-product page verified:** https://www.isdin.com/en-GB/product/foto-ultra-isdin/active-unify-spf-50

The page identifies FotoUltra 100 Active Unify SPF 50+, 50 ml, and claims it clarifies/unifies skin tone and helps reduce and prevent sun-caused pigmentation spots, with visible results after one month. It lists a formula including niacinamide, UV filters, phenylethyl resorcinol, panthenol, tocopheryl acetate and other supporting ingredients, and gives directions including morning/midday application and reapplication every two hours.

**Evidence boundary:** This source supports an official market-specific identity/INCI/marketing-claim record. It does not provide the original protocol or verify the previously recorded 31-subject, 22% spot-intensity and 15% spot-area results. Do not attach those figures to this UK page unless the source/report establishes the same market, tested SKU and formula version.

**Disposition:** P17 remains manufacturer_claim_only + candidate_only as a claim-led research lead, not an approved relationship. P19 remains not_linked unless exact-version evidence explicitly covers post-inflammatory hyperpigmentation. P18 melasma is not a default match. The identity gate remains BLOCKED until the conflicting market/study descriptions are mapped to the tested package, market, formula/version and report. Do not infer tinted/untinted equivalence.

### 6.3 Source and evidence classification rules reaffirmed

- An official page can verify what the manufacturer currently lists or claims; it does not independently validate clinical efficacy.
- A page-level INCI is not proof that the physical package in the target market has the same current formula. Preserve package/market/version uncertainty.
- A manufacturer-reported percentage without the underlying methods remains manufacturer_claim_only.
- Do not transfer results between different formats (serum versus pad), SKUs, market formulas, or populations/endpoints.
- All P1–P7 consultation-engine eligibility remains **NO / NOT AUTHORIZED**. No Product↔Problem relation is accepted or upgraded by this pass.

### 6.4 Updated next actions

1. P5 ISDIN: reconcile the official UK page and any study summary against the exact tested market/SKU/GTIN/formula; retrieve the original report/protocol before attaching numerical outcomes.
2. P7 Anua: retain the now-verified official serum page and the separate official 90% claim page; request the complete serum study report/protocol. Keep the pad study in the non-transferable category.
3. P1 COSRX, P2 Neutrogena and P6 Clinique: continue seeking complete protocols/reports; preserve existing official-page findings as manufacturer claims.
4. P1–P7 identity gate: obtain current package/label evidence where possible. Until then, do not mark product identity LOCKED or use this research matrix for recommendations.

**Change scope:** append-only documentation/research. No ProductKnowledge record, approved Product↔Problem relation, Map/Working Records status, code, schema, API, UI, database, workflow, or product lifecycle was changed. No merge authorization is implied.

---
## Research pass 7 — protocol retrieval follow-up for P1, P2 and P6 (2026-10-24)

**Continuity:** Appended after Pass 6. No earlier pass or product dossier is replaced. Search scope was limited to publicly indexed official pages and exact-phrase/protocol searches; absence from these results is not proof that a report does not exist.

### 7.1 P1 COSRX — original study protocol remains unavailable in reviewed public sources

Official product page rechecked: https://www.cosrx.com/collections/all/products/the-6-peptide-skin-booster-serum

The page repeats the five numerical outcomes (+162.5% deep moisture, +76.4% texture, +40.1% clarity, +24.5% radiance, +22.2% density), says the testing involved 20 subjects, and names Dermacosmetic Skin Science Laboratory Co., Ltd with a 2023-09-18 to 2023-10-31 study window. No full protocol, baseline/absolute values, control/comparator, measurement instruments, statistical plan or complete report was located in this bounded retrieval.

**Disposition:** Keep all five outcomes as manufacturer-reported claims only. They do not establish P17 pigmentation efficacy or independently validated effects. A texture claim must not automatically be mapped to P43 without checking that canonical definition and the exact endpoint.

### 7.2 P2 Neutrogena UK Clear & Defend 2% Salicylic Acid Face Wash — exact protocol remains unavailable

Official UK product page: https://www.neutrogena.co.uk/skincare/cleansers-washes/clear-and-defend-daily-wash

The official page continues to state 2% salicylic acid and “97% noticed less new spots in 4 weeks” based on clinical grading of 34 subjects. Exact-phrase searches did not locate the underlying study report or a peer-reviewed publication that clearly matches this exact UK rinse-off SKU, market and claim. The page itself does not expose sufficient protocol details to establish the comparator, baseline, lesion-specific endpoint definitions, statistical analysis or independent replication.

**Disposition:** Keep the 97% figure as manufacturer_claim_only, not a cure rate. P08 may remain a research candidate only; P09/P10 remain not_linked without direct open-/closed-comedone endpoints. Do not infer P11/P12 from generic “acne” language.

### 7.3 P6 Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter — endpoints confirmed; full protocol not found

Official product page rechecked: https://www.clinique.com/product/4034/68008/skincare/serum/even-better-clinicaltm-radical-dark-spot-corrector-interrupter

The page states that clinical testing on 52 women after 12 weeks showed a 39% visible reduction in dark spots. It separately reports consumer testing on 536 women, including 84% saying skin looked more radiant and 93% saying skin felt soothed/calmer. The page does not disclose the full clinical protocol, control group, randomization/blinding, instrument, prespecified endpoint, analysis or a PIH-/melasma-specific result.

**Disposition:** Keep the n=52 clinical claim and n=536 consumer results as separate manufacturer-reported datasets. Do not describe the clinical study as an RCT or independent study without documentation. P17 remains claim-led candidate only; P19 remains not_linked unless exact-product evidence explicitly measures PIH; P18 melasma is not a default match.

### 7.4 Consolidated outcome and next action

- For P1, P2 and P6, official pages confirm the existence of manufacturer claims but the full original protocols/reports were NOT VERIFIED in this bounded search.
- A public product page or consumer-test percentage does not independently validate a clinical effect.
- Continue requesting the reports from manufacturers; if a report is later found, append a new numbered pass with the exact report URL, version/market, method, population, comparator, endpoint, analysis and limitations. Do not overwrite this search history.
- All P1–P7 consultation-engine recommendation status remains **NO / NOT AUTHORIZED**. No product-problem relation is approved.

**Change scope:** research documentation only; no Map/Working Records status, ProductKnowledge, code, schema, API, UI, database, workflow or product lifecycle change.


---
## Research pass 8 — seven-product identity/source reconciliation and readiness gate (2026-10-24)

**Continuity and preservation rule:** This is an append-only continuation after Research pass 7. Passes 1–7 and the earlier ProductKnowledge/WP-0 sections are retained in this same file. This pass does not replace earlier results. If a source retrieval changes, the new status is recorded here while the prior search history remains intact.

### 8.1 Purpose and method

The previous passes established official-page claims for several products, but an official web page is not proof that the physical package intended for this dossier has the same market, GTIN, current INCI or tested formula. This pass reconciles the *research-source state* and the remaining identity/evidence gates across all seven dossiers. It is a bounded public-source recheck, not a physical-package inspection and not a clinical evidence review.

### 8.2 Current identity and evidence gate by dossier

| Dossier | Official source state | Exact target package / market match | Underlying product-study protocol | Research disposition |
|---|---|---|---|---|
| P1 COSRX The 6 Peptide Skin Booster Serum 150 ml | Official product page available: https://www.cosrx.com/collections/all/products/the-6-peptide-skin-booster-serum. It states five outcomes from 20 subjects and names the testing laboratory/date range. | NOT VERIFIED from a physical package in this workflow; page-level formula is not package-level confirmation. | NOT VERIFIED in the reviewed public sources; methods/comparator/instruments/statistical plan unavailable. | Manufacturer claims only. No P17 link; P43 only if the Map definition and exact endpoint align; otherwise not_linked. |
| P2 Neutrogena Clear & Defend 2% Salicylic Acid Face Wash, UK | Official UK page available: https://www.neutrogena.co.uk/skincare/cleansers-washes/clear-and-defend-daily-wash. The 2% salicylic-acid declaration and n=34 / 97% new-spots claim are manufacturer statements. Retail listing also surfaced at https://www.boots.com/neutrogena-clear-defend-facial-wash-10233110, but a retailer page is not the study protocol. | UK market is the intended dossier framing; current physical package/INCI and GTIN are NOT VERIFIED. Manufacturer warns formula/listings may change. | NOT VERIFIED. The public page does not provide enough method details to establish comparator or lesion-specific endpoints. | P08 candidate_only / manufacturer_claim_only. P09/P10 not_linked without open-/closed-comedone endpoints; no inference to P11/P12. |
| P3 Garnier Vitamin C Brightening Gel Cleanser, Australia | Official AU page available: https://www.garnier.com.au/about-our-brands/skin-active/garnier-skin-active-vitamin-c-brightening-gel-cleanser-200ml. It identifies a rinse-off cleanser and lists the page-level INCI. | Australia is the source-page market, but the physical target package/GTIN and current package-to-page match are NOT VERIFIED. | No direct finished-product protocol for the target problem endpoints was verified in this pass. | Exact page-level ingredients can inform research only. Product-problem links remain not_linked; ingredient/category claims are not finished-product efficacy proof. |
| P4 SKIN1004 Madagascar Centella Hyalu-Cica Water-Fit Sun Serum 50 ml — international/Korean formula | Official international page available: https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-spf50-pa?country=BE&variant=45493174337782. It lists SPF50+ PA++++ and a formula with organic UV filters, niacinamide, glycerin, centella and hyaluronic-acid forms. | The international page identity is source-backed; physical package, target market and GTIN are NOT VERIFIED. Keep the US sunscreen as a separate dossier/SKU. | No independent, exact-version endpoint protocol was verified here for treatment of existing pigmentation or a skin-condition claim. | UV protection/prevention context only; P22 remains candidate_only at most. Do not claim treatment of existing P17 pigmentation. Do not merge US active filters/INCI into this formula. |
| P5 ISDIN FotoUltra 100 Active Unify SPF50+ 50 ml | Official UK page available: https://www.isdin.com/en-GB/product/foto-ultra-isdin/active-unify-spf-50. It claims tone-unifying and reduction/prevention of sun-caused pigmentation spots, with visible results after one month, and publishes a page-level composition. | UK page is verified as a manufacturer source; physical package/GTIN and correspondence to the formula/population behind any separate numeric study summary are NOT VERIFIED. | Original protocol behind the previously mentioned 31-subject / 22% intensity / 15% area figures remains NOT VERIFIED for the exact target SKU/market. Do not attach these numbers to the UK page without the original report. | P17 manufacturer_claim_only + candidate_only; P19 not_linked unless the exact-version endpoint explicitly covers PIH; P18 melasma not a default match. Identity gate remains BLOCKED. |
| P6 Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter | Official product page available: https://www.clinique.com/product/4034/68008/skincare/serum/even-better-clinicaltm-radical-dark-spot-corrector-interrupter. Clinical n=52 / 12-week dark-spot result and consumer-test results are separate manufacturer-reported datasets. | Physical package, market/GTIN and current package-to-page match are NOT VERIFIED. | Full clinical protocol and PIH-/melasma-specific endpoint NOT VERIFIED in the reviewed public page. | P17 manufacturer_claim_only / candidate_only; P19 not_linked absent an explicit PIH endpoint; P18 not linked by default. Keep clinical and consumer datasets separate. |
| P7 Anua Azelaic Acid 10 Hyaluron Redness Soothing Serum | Official exact-product page available: https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum. Official routine/claim page: https://pages.anua.com/solutions/redness-prone-routine-sensitive-skin. The page-level ingredient declaration and manufacturer claim are source-backed; full methodology for the 90% statement is not. | Physical package, market/GTIN and current package-to-page match are NOT VERIFIED. | Full serum study protocol/report NOT VERIFIED. Separate pad study remains NON-TRANSFERABLE to the serum. | Manufacturer_claim_only for the 90% statement; no approved P08/P13/P19/P24 relation. Do not infer rosacea treatment or general suitability for all redness-prone skin. |

### 8.3 Gate definitions to prevent false completion

- **SOURCE_PAGE_FOUND** means an official page for a named product/version was located. It does not mean the physical product in hand matches that page.
- **PACKAGE_IDENTITY_VERIFIED** requires readable package/label evidence sufficient to record the exact marketed name, market/version, current INCI and GTIN where present, with unresolved discrepancies noted. No dossier is marked PACKAGE_IDENTITY_VERIFIED by this pass.
- **PROTOCOL_VERIFIED** requires the original report or a sufficiently detailed primary publication for the exact tested SKU/formula/market, including population, duration, comparator/control where applicable, endpoint definitions, measurement method and analysis. A marketing page or percentage alone does not pass this gate.
- **RELATIONSHIP_APPROVED** remains a separate governance decision after evidence QA and canonical Map/Working Records review. Neither SOURCE_PAGE_FOUND nor PACKAGE_IDENTITY_VERIFIED alone approves a Product↔Problem relation.

### 8.4 Corrections and boundaries

1. Pass 5's initial “not found” statuses for P5/P7 are historical search results, not errors to erase. Pass 6 already corrected the *current source-discovery status*: official pages were subsequently found; the full protocol and physical package match remain unverified.
2. The SKIN1004 international/Korean and US formulations remain separate. Official pages show different UV-filter declarations; no cross-market ingredient transfer is permitted.
3. The P5 UK Active Unify marketing page does not establish that the previously cited numerical study summary used the same UK SKU/formula. That connection remains unverified.
4. P1/P2/P6 public pages identify manufacturer claims but do not expose the complete underlying protocols in the reviewed sources.
5. For every P1–P7 dossier, consultation-engine recommendation remains **NO / NOT AUTHORIZED** on the basis of this research matrix. No Product↔Problem relationship is accepted or created by this pass.

### 8.5 Next operational step

The next evidence input should be the current front/back package-label photos for the seven actual target products (especially P3 market/GTIN, P4 market split, P5 tested-version identity, and P7 serum-versus-pad identity). Use those to create a package-to-source comparison within this same ledger, recording only visible/legible fields and marking unreadable fields UNKNOWN. In parallel, continue requests for the exact primary reports for P1, P2, P5, P6 and P7. Do not pause preservation of existing findings while waiting for new evidence.

**Change scope:** research ledger only. No code, schema, API, UI, database, ProductKnowledge row, operational product record, Map/Working Records acceptance status, or approved Product↔Problem relation was changed. This pass does not authorize PR merge or implementation.


---
## Research pass 9 — expanded public-web source retrieval and evidence corrections (2026-10-24)

**Continuity rule:** Appended after Pass 8 in the same ledger. Passes 1–8 are retained. This pass uses public web sources, including official manufacturer pages and a primary research paper where relevant; it does not require physical package photographs to continue. Search-result availability is not treated as proof that a physical package matches a webpage.

### 9.1 New source-level findings and corrections

#### P1 — COSRX The 6 Peptide Skin Booster Serum (150 ml)

Official product page rechecked: https://www.cosrx.com/collections/all/products/the-6-peptide-skin-booster-serum

The current official page explicitly labels the product “Original,” shows 150 ml and 50 ml variants, lists the ingredient declaration, and reports the five outcomes from 20 subjects (deep moisture +162.5%, texture +76.4%, clarity +40.1%, radiance +24.5%, density +22.2%) for a test dated 2023-09-18 to 2023-10-31. It also makes broad product-positioning statements about pores/sebum, fine lines, texture, tone, hydration and suitability for acne-prone skin.

**Evidence correction:** These are still manufacturer-published statements. The page's use of “independent skin science testing” identifies a named testing laboratory but does not provide the full protocol, raw data, comparator, measurement method, endpoint definitions or statistical analysis. “Uneven tone,” “clarity,” “radiance” and “texture” must not be treated as interchangeable with canonical P17 hyperpigmentation or P43 without exact definition/endpoint review. The non-comedogenic/irritation-test wording is not proof that the product treats acne.

Disposition: manufacturer_claim_only for the reported endpoints; P02/P43 remain research candidates only where the endpoint matches the canonical definition; P17 remains not_linked pending direct endpoint validation.

#### P2 — Neutrogena Clear & Defend 2% Salicylic Acid Face Wash, UK

Official manufacturer page: https://www.neutrogena.co.uk/skincare/cleansers-washes/clear-and-defend-daily-wash
Retail corroboration (not a primary clinical source): https://www.boots.com/neutrogena-/neutrogena-washes-and-exfoliators/neutrogena-clear-defend-facial-wash-10233110

The manufacturer page reports “97% noticed less new spots in 4 weeks” with clinical grading in 34 subjects, lists 2% salicylic acid and an INCI, and warns that product/ingredients may change. Boots' listing also describes 2% salicylic acid and the same n=34/97% claim. The retail listing corroborates how the product is marketed but does not supply the original protocol or independently verify the claim.

Disposition: no change to the gate. The numerical claim remains manufacturer_claim_only; P08 remains candidate_only; P09/P10 remain not_linked without specific open-/closed-comedone endpoints. Do not treat retail repetition of a manufacturer claim as independent evidence.

#### P3 — Garnier Vitamin C Brightening Gel Cleanser, Australia

Official manufacturer page: https://www.garnier.com.au/about-our-brands/skin-active/garnier-skin-active-vitamin-c-brightening-gel-cleanser-200ml
Retail corroboration: https://www.coles.com.au/product/garnier-vitamin-c-brightening-gel-cleanser-200ml-5940375

The official page identifies the 200 ml rinse-off product, describes Vitamin Cg (ascorbyl glucoside) and citrus extract, and lists the page-level INCI including sodium laureth sulfate, coco-betaine, glycerin, ascorbyl glucoside, panthenol, salicylic acid, fragrance and fragrance allergens. Both official and retail pages carry substantially similar product-positioning/ingredient information; the official page warns that ingredient lists change and the package should be checked.

**Boundary:** Marketing claims about glow/brightening and the presence of salicylic acid do not establish a finished-product endpoint for acne, open/closed comedones or a defined hyperpigmentation concept. The Australian market page is a source, not proof that the user-targeted SKU is the Australian formula.

Disposition: P08/P09/P10/P17 remain not_linked until exact target-market identity and direct finished-product evidence justify a specific relationship.

#### P4 — SKIN1004 Hyalu-Cica Water-Fit Sun Serum, international vs US formula

Official international page: https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-spf50-pa?country=BE&variant=45493174337782
Official US page: https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-uv?variant=50346297852150
Additional US product details published on the brand's information site: https://info.skin1004.com/products/skin1004-hyalu-cica-water-fit-sun-serum-uv

The international page states SPF50+ PA++++ and lists filters including Diethylamino Hydroxybenzoyl Hexyl Benzoate, Ethylhexyl Triazone, Methylene Bis-Benzotriazolyl Tetramethylbutylphenol and Diethylhexyl Butamido Triazone. The US product page explicitly identifies a separate sunscreen drug product with active filters avobenzone 2.7%, homosalate 13.6%, octisalate 4.5% and octocrylene 9%. The brand's US product-information page gives SKU USSKS001 and GTIN 8809913832805 for the US item; those identifiers apply to that US listing only and must not be copied into the international dossier.

Disposition: this strengthens the documented market split but does not identify the actual target package. Keep the two formulas separate. P22 remains a prevention/context candidate only; do not infer treatment of existing P17 pigmentation. Hydration/soothing claims remain manufacturer positioning unless linked to a relevant exact-version endpoint.

#### P5 — ISDIN FotoUltra 100 Active Unify SPF50+

Official UK product page: https://www.isdin.com/en-GB/product/foto-ultra-isdin/active-unify-spf-50
Official UK product family page: https://www.isdin.com/en-GB/products/foto-ultra-isdin
Potentially confusing but explicitly different product study: https://pmc.ncbi.nlm.nih.gov/articles/PMC12872947/

The official UK page confirms the name “FotoUltra 100 Active Unify SPF 50+,” 50 ml, page-level composition, use directions and manufacturer claims about clarifying/unifying skin tone and reducing/preventing sun-caused pigmentation spots. The official product-family page separately lists Active Unify and Spot Prevent as distinct products.

The located peer-reviewed randomized study concerns **FOTOULTRA 100 SPOT PREVENT**, not Active Unify. It is therefore not evidence for the Active Unify dossier, even though both are ISDIN sunscreens and may share some broad ingredients/marketing territory.

Disposition: the exact-SKU study protocol behind the earlier 31-subject / 22% spot-intensity / 15% spot-area figures remains UNKNOWN / NOT VERIFIED for Active Unify. P17 remains manufacturer_claim_only + candidate_only; P19 remains not_linked absent an exact-SKU PIH endpoint; P18 melasma is not a default match. The product identity/study correspondence gate remains blocked.

#### P6 — Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter

Official product page: https://www.clinique.com/product/4034/68008/skincare/serum/even-better-clinicaltm-radical-dark-spot-corrector-interrupter

The official page contains several distinct manufacturer-reported datasets:
- Clinical testing on 52 women after 12 weeks: 39% visible reduction in dark spots.
- Consumer testing on 536 women: 84% said skin looked more radiant and 93% said skin felt soothed/calmer.
- Separate consumer testing on 533 women after 28 days: 90% said skin looked brighter, 89% said skin looked more even, and 81% said the look of dark spots including sun spots was reduced.
- Separate consumer testing on 433 women after 28 days: 83% said the look of acne marks was reduced.

**Correction to the previous summary:** The page does include a consumer-reported acne-mark outcome (n=433). It is not the same as the clinical n=52 dark-spot test, and it is not, by itself, a controlled clinical demonstration of a canonical P19 post-inflammatory-hyperpigmentation endpoint. The public page does not disclose enough protocol detail to establish lesion classification, comparator, blinding, instrument or statistical analysis for these consumer outcomes.

Disposition: keep all datasets distinct and labelled manufacturer_claim_only. The acne-mark consumer result may be recorded as a research lead for review, but P19 remains not_linked until the canonical P19 definition and endpoint population are explicitly matched. P17 remains claim-led candidate only; P18 melasma is not a default match.

#### P7 — Anua Azelaic Acid 10 Hyaluron Redness Soothing Serum

Official US product page: https://pages.anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum
Official global product page: https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum
Official routine/claim page: https://pages.anua.com/solutions/redness-prone-routine-sensitive-skin

The official US page provides the serum ingredient declaration, use directions, and “Non-comedogenic, Low-Irritation” testing labels. The exact-product page identifies 10% azelaic acid and includes ingredients such as panthenol, betaine salicylate, glycerin, allantoin, niacinamide, centella-derived ingredients, zinc PCA and ceramide NP. The official routine page's 90% red-troubled-spot statement remains a manufacturer claim; full study protocol, sample size, comparator, validated endpoint and analysis were not located in the public summary reviewed here.

**Important formula/claim caution:** Anua product pages and market-specific pages may differ in naming and presentation. Do not assume every regional page, package or formula is identical without a market/version match. The separate azelaic-acid pad's study remains non-transferable to the serum.

Disposition: exact official serum source and page-level INCI are found; physical package/market match and full protocol remain unverified. Keep the 90% result manufacturer_claim_only. Do not approve P08/P13/P19/P24 links or infer rosacea treatment from general redness positioning.

### 9.2 Consolidated evidence-state update

| Gate | Current state after Pass 9 |
|---|---|
| Official product source page | Located for P1–P7 at least for the market/version stated in each cited URL |
| Physical target package / market / GTIN matched to source | NOT VERIFIED for all P1–P7 in this workflow |
| Full original protocol verified for the exact target SKU | NOT VERIFIED for P1, P2, P5, P6 and P7; no relevant direct efficacy protocol verified for P3/P4 in this pass |
| Manufacturer claims separated from independent evidence | YES; retailer repetition is not counted as independent evidence |
| Approved Product↔Problem relation | NONE |
| Consultation-engine authorization from this matrix | **NO / NOT AUTHORIZED for P1–P7** |

### 9.3 Next research work (no package-photo dependency)

1. Compare the canonical definitions for P02, P08, P13, P17, P19, P22, P24, P26 and P43 in the existing Map/Working Records before any candidate is converted into a relation; preserve the documented governance boundary.
2. Search for primary reports/publications matching the exact claims and exact SKUs for COSRX, Neutrogena, Active Unify, Clinique and Anua. For any paper found, first check whether it actually tests the same finished product, market formula and endpoint; exclude mismatched SKUs (including Spot Prevent versus Active Unify).
3. Build a source-evidence register for every claim with fields: exact source URL, source type, exact product/version, claim verbatim or concise paraphrase, population/sample size, duration, endpoint, protocol availability, conflicts/limitations, evidence label, canonical candidate ID, and review state.
4. Keep the identity uncertainty explicit. The absence of package photos does not block web research, but it does block claiming that a specific physical package/GTIN has been verified.
5. Continue append-only in this same ledger as Research pass 10; do not create a parallel file or identifier.

**Change scope:** public-source research and documentation only. No code, schema, API, UI, database, ProductKnowledge row, operational product record, accepted Map/Working Records status or approved Product↔Problem relation changed. PR merge is not authorized by this pass.


---
## Research pass 10 — canonical Map and Working Records crosswalk (2026-10-24)

**Scope:** Read-only crosswalk against the owner-designated P01–P61 Map on `master` and the current Working Records. This pass clarifies canonical unit boundaries; it does not medically validate the Map, accept a Need, approve Product↔Problem relations, or authorize product recommendations.

### 10.1 Canonical sources read

1. `docs/product-intake-knowledge-registry/SKIN_PROBLEM_SPACE_MAP_V0.1.md` on `master`, blob SHA `c57ce7edbcee513dcb60b735ce91b98de22d8aa2`.
2. `docs/product-intake-knowledge-registry/SKIN_PROBLEM_BANK_WORKING_RECORDS.md` on `master`, blob SHA `30bb058b46462fc125ed80c2c471d2e6394bc38a`.
3. `docs/product-intake-knowledge-registry/SKIN_PROBLEM_BANK_CONSOLIDATED_REFERENCE.md` and `SKIN_PROBLEM_BANK_WORKSPACE_INDEX.md` were also checked for current governance/navigation state.

The Map itself states that its P01–P61 designation is the owner's structural reference list only: Map placement is not medical validation, Need acceptance, treatment authorization, or product mapping. Working Records likewise mark the relevant records Identified / Identified+Linked, Accepted = No, and operational status Undetermined or Clinical-anchor only. Definitions below reproduce the Map's structural labels; they are not new clinical definitions.

### 10.2 Canonical ID definitions and evidence crosswalk

| Canonical ID | Map-defined unit and boundary | Product dossier evidence currently available | Pass 10 disposition / missing proof |
|---|---|---|---|
| **P02** | Dehydration / impaired moisture retention; S01 manifestation/related presentation, recorded as MERGE/RELATED TO P01. Working Records preserve P02 as Identified+Linked to P01, not merged/deleted, Accepted = No; standalone operational status undetermined. | P1 COSRX has manufacturer-reported moisture result (+162.5% deep moisture, n=20); P2/P3 cleanser hydration/supporting ingredients and P4 hydration positioning are not direct proof of this canonical presentation. No exact protocol/endpoint definition or target-package match established. | **NOT LINKED.** P1's broad moisture result is a research lead only; it does not establish improvement in impaired moisture retention as defined for P02. Need endpoint definition, method, duration, exact SKU/formula and suitable comparison; preserve P02/P01 governance boundary. |
| **P08** | Acne; S03 Problem/Clinical presentation and parent of P09–P12. P09/P10/P11 are subtype/manifestation records; P12 is a severity/clinical subtype. No independent Need determination. | P2 Neutrogena UK wash: manufacturer-reported “97% noticed less new spots in 4 weeks,” clinical grading n=34, declared 2% salicylic acid; full protocol unavailable. P7 Anua serum has manufacturer non-comedogenic/low-irritation labels and a 90% redness-related claim, not proof of acne improvement. P3 cleanser ingredient presence alone is insufficient. | **CANDIDATE ONLY / manufacturer_claim_only for P2 claim.** Need exact product protocol, definition of “new spots,” baseline/comparator and analysis; confirm target market/package. Do not infer P09/P10/P11/P12-specific efficacy from general acne wording. |
| **P13** | Acne aftermath/discoloration; S03→S04 sequela/post-inflammatory presentation, Related/Cross-Shelf. Working Records explicitly say S04 is not opened by this cross-reference. | P6 Clinique has a separate consumer-reported outcome that acne marks looked reduced (n=433, 28 days); public page does not provide enough detail to establish lesion classification, comparator, blinding, measurement or relation to canonical P13. P2's “new spots” claim is not an aftermath endpoint. | **RESEARCH CANDIDATE ONLY; not linked.** Obtain the original study/protocol and match what “acne marks” means to P13; distinguish post-inflammatory discoloration from active acne and from P17/P19. No S04 scope expansion is implied. |
| **P17** | Hyperpigmentation/dark spots; S04 Problem/presentation, with P18/P19 as structurally related but distinct units. | P5 ISDIN Active Unify and P6 Clinique have manufacturer-reported dark-spot/tone claims. P6 reports clinical n=52/12-week 39% visible dark-spot reduction, plus separate consumer datasets. P1's clarity/radiance claims are not equivalent to a defined hyperpigmentation endpoint. Exact protocols and target package matches remain unverified. | **CANDIDATE ONLY / manufacturer_claim_only for applicable claims; no approved link.** Require exact-SKU study endpoint, protocol, market/formula match and clear lesion/pigmentation definition. Do not merge P17 with P18 or P19. |
| **P19** | Post-inflammatory hyperpigmentation; P17/S04 sequela/pigmentation presentation, Related/Sequela, linked to P17 but not merged. Working Records keep operational definition and evidence UNKNOWN. | P6 consumer-reported “acne marks” outcome (n=433, 28 days) is a potential lead only; the public claim does not prove that participants had PIH as defined by P19. P5's sun-caused spots claim does not establish PIH. P3 brightening marketing is not an exact PIH endpoint. | **NOT LINKED.** Exact PIH-specific population/endpoint and original protocol required. A consumer perception about acne marks cannot be promoted to controlled clinical proof of canonical P19. |
| **P22** | Sun-related pigmentation; P17/S09 Context/pigmentation presentation, Related/Context. Context is not automatically an independent Problem or Need; S09 is not reopened by the relation. | P4 international SKIN1004 SPF50+ PA++++ and its distinct US formula have manufacturer UV-protection positioning; P5 ISDIN Active Unify SPF50+ has manufacturer claims about reducing/preventing sun-caused spots. For P5, the located peer-reviewed Spot Prevent study is a different product and is excluded. Exact target package and Active Unify protocol are unverified. | **CONTEXT CANDIDATE ONLY; no treatment link.** Sunscreen protection/prevention context is not proof of treatment for existing pigmentation or P17/P19. Keep P4 formulas separate; require exact-market label/protection evidence and exact-SKU evidence for any spot-reduction claim. |
| **P24** | Persistent redness; S05 Problem/presentation, parent of P25/P26 only as Map. P25 flushing is a symptom/manifestation; P26 rosacea is a distinct Clinical Condition/Clinical Anchor. | P7 Anua serum's manufacturer claim says 90% agreed red-troubled spots looked improved; full protocol, validated endpoint, comparator and analysis not located. P4's soothing positioning is not a persistent-redness endpoint. | **CANDIDATE ONLY / manufacturer_claim_only for P7 claim; no approved link.** Need direct endpoint for persistent redness, time course, population, protocol and exact product/market match. Do not infer P26 rosacea treatment. |
| **P26** | Rosacea; Clinical Condition and Clinical Anchor linked structurally to P24/S05. Not an ordinary-care approval or product-treatment permission. | No reviewed P1–P7 source establishes an exact-SKU, rosacea-specific clinical endpoint. P7's general redness claim and ingredient list are insufficient. | **NOT LINKED.** Requires rosacea-specific evidence, appropriate clinical oversight and explicit governance; do not infer diagnosis or treatment from redness positioning. |
| **P43** | Uneven skin texture; S07 Problem/presentation, mapped with boundary open. Working Records preserve the open boundary and do not establish acceptance or a complete operational definition. | P1 COSRX manufacturer reports +76.4% texture result in 20 subjects, but full protocol/measurement definition unavailable. P3 glow/brightening marketing and other product texture/finish language do not establish the canonical P43 endpoint. | **CANDIDATE ONLY / manufacturer_claim_only for P1 claim; no approved link.** Obtain endpoint definition, measurement method, comparator/statistics and exact SKU/market match; confirm the measured “texture” matches P43 rather than hydration, radiance or cosmetic finish. |

### 10.3 Product-level crosswalk summary

- **P1 COSRX:** P02 and P43 are narrow research leads only (manufacturer-reported moisture/texture results); no accepted relation.
- **P2 Neutrogena UK:** P08 is a claim-led research candidate only; no P09/P10/P11/P12 subtype-specific relation.
- **P3 Garnier Australia:** no canonical product relation supported by the reviewed page-level ingredient/marketing information; target market/package identity is still unverified.
- **P4 SKIN1004:** P22 prevention/context only; no claim that it treats existing hyperpigmentation. International/Korean and US formulas remain separate.
- **P5 ISDIN Active Unify:** P17/P22 claim-led leads only; the Spot Prevent paper is excluded as a different product; P19 is not linked.
- **P6 Clinique:** P17 claim-led lead; P13/P19 acne-mark outcome is a lead for protocol retrieval only, not proof of canonical PIH.
- **P7 Anua serum:** P24 general redness claim is a research lead only; no P26 rosacea relation. Evidence for the separate pad is non-transferable.

### 10.4 Evidence register fields required for each future source

For each claim or study, record: source URL; source class (manufacturer, primary publication, independent secondary source, retail corroboration); exact product name, market, volume, formula/version and SKU/GTIN if known; verbatim claim or bounded paraphrase; study population/sample; duration; endpoint definition; measurement method; comparator/control; protocol/report availability; statistical analysis; sponsor/conflicts where disclosed; limitations/version mismatch; canonical candidate ID; evidence label (`manufacturer_claim_only`, `candidate_only`, `not_linked`, `UNKNOWN`, or later approved state only after governance); reviewer/date; review state.

### 10.5 Gate outcome

- Canonical Map/Working Records reviewed for all nine requested IDs: **PASS for structural crosswalk**.
- Medical validation or acceptance of the Map's units: **NOT CLAIMED**.
- Exact physical target package/market/GTIN verified for P1–P7: **NOT VERIFIED**.
- Full exact-SKU protocols verified for the cited claims: **NOT VERIFIED**.
- Approved Product↔Problem relationships: **NONE**.
- Product recommendation / consultation-engine authorization for P1–P7: **NO / NOT AUTHORIZED**.
- Code, schema, API, UI, database, operational product records, ProductKnowledge rows and Map/Working Records statuses changed: **NO**.
- PR merge authorization: **NOT GRANTED**.

### 10.6 Next action

Continue in this same ledger with source-by-source protocol retrieval for the highest-value open leads: P2→P08, P1→P02/P43, P6→P13/P19, P5→P17/P22, and P7→P24. Each paper/report must first pass exact-product, market/formula and endpoint matching. In parallel, use the existing Map/Working Records definitions as the only canonical structural baseline. Do not ask for or assume package photos as a prerequisite to web research; do not claim package identity is verified without them or equivalent direct label/GTIN evidence.

**Change scope:** append-only research documentation. Passes 1–9 remain unchanged. No product records were created and no Product↔Problem relation was approved.


---
## Research pass 11 — primary-source protocol retrieval and claim-boundary audit (2026-10-24)

**Purpose:** pursue the highest-value protocol leads identified in Pass 10 using public official product pages and searches for the underlying methods/reports. This is a source-retrieval audit, not an efficacy approval. No missing protocol is inferred from a marketing summary.

### 11.1 Source-by-source findings

#### P1 — COSRX The 6 Peptide Skin Booster Serum

**Official source:** https://www.cosrx.com/collections/all/products/the-6-peptide-skin-booster-serum  
**Additional official page:** https://www.cosrx.com/collections/dermskincare-guide

The official product page attributes five outcomes to a trial of 20 subjects conducted by Dermacosmetic Skin Science Laboratory Co., Ltd from 2023-09-18 to 2023-10-31: deep moisture +162.5%, texture +76.4%, clarity +40.1%, radiance +24.5%, density +22.2%. The additional official brand page also states after four weeks: texture +76.41%, density +22.22%, moisture/radiance +162.5%, blackheads decreased 21.95%, and excess sebum decreased 29.48%.

**Retrieval result:** the reviewed official pages do not provide a complete study report, sample characteristics beyond n=20, detailed endpoint definitions, measurement instruments, comparator/control, analysis plan or uncertainty estimates. A search did not establish a publicly accessible primary protocol/report. The extra blackhead/sebum figures are an important official claim lead, but cannot be assigned to P09/P08 as approved evidence without knowing exact measures and study conditions.

**Disposition:** retain `manufacturer_claim_only` and `candidate_only` for P02/P43, and add P08/P09 as **claim-led retrieval candidates only** for the newly located blackhead/sebum claims. Do not link to P10/P11/P12; no subtype-specific evidence located. Non-comedogenic/irritation tests remain safety/compatibility claims, not proof of acne treatment.

#### P2 — Neutrogena Clear & Defend 2% Salicylic Acid Face Wash (UK)

**Official source:** https://www.neutrogena.co.uk/skincare/cleansers-washes/clear-and-defend-daily-wash  
**Retail corroboration (not independent evidence):** https://www.boots.com/neutrogena-/neutrogena-washes-and-exfoliators/neutrogena-clear-defend-facial-wash-10233110

The official page reports “97% noticed less new spots in 4 weeks” with “clinical grading, 34 subjects,” and lists 2% salicylic acid. It also warns that product and ingredients may change. Boots repeats substantially the same claim and sample note.

**Retrieval result:** no public full protocol/report located. The wording does not specify baseline lesion counts, whether “new spots” means all acne lesions or a defined subtype, comparator, assessor blinding, statistical method or confidence intervals. The retail repetition is not an independent replication.

**Disposition:** P08 remains `candidate_only` / `manufacturer_claim_only`; no P09/P10/P11/P12 relation. Require the primary report or sufficient protocol metadata and target-label match.

#### P6 — Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter

**Official source:** https://www.clinique.com/product/4034/68008/skincare/serum/even-better-clinicaltm-radical-dark-spot-corrector-interrupter

The official page separates multiple cohorts/outcomes: clinical testing of 52 women after 12 weeks with a reported 39% visible dark-spot reduction; consumer testing of 536 women after 7 days (84% more radiant, 93% soothed/calmer); consumer testing of 533 women after 28 days (90% brighter, 89% more even, 81% look of dark spots including sun spots reduced); and a separate consumer test of 433 women after 28 days (83% said the look of acne marks was reduced).

**Retrieval result:** the product page does not supply the complete protocols for these cohorts, control/comparator details, definition of “acne marks,” objective vs subjective assessment methods or analysis plan. The 433-person acne-mark consumer endpoint must not be merged with the 52-person clinical dark-spot endpoint.

**Disposition:** P17 remains claim-led candidate only. P13/P19 remain unlinked; the acne-mark consumer result is a protocol-retrieval lead, not evidence that the cohort had canonical PIH. P18 melasma remains unlinked by default.

#### P5 — ISDIN FotoUltra 100 Active Unify SPF50+ 50 ml

**Official UK source:** https://www.isdin.com/en-GB/product/foto-ultra-isdin/active-unify-spf-50  
**Official family page distinguishing variants:** https://www.isdin.com/en-GB/products/foto-ultra-isdin  
**Official Spot Prevent page (different product):** https://www.isdin.com/en-GB/product/foto-ultra-isdin/spot-prevent-color-spf-50

The official Active Unify page describes SPF50+, 50 ml, and claims it helps reduce and prevent pigmentation spots caused by the sun, with visible results after one month and best results after three months. A retailer page repeats figures of 22% reduction in sun-spot intensity and 15% reduction in area, but the reviewed official Active Unify page does not expose the full study report or enough protocol metadata to verify those figures for the exact target SKU. Official Spot Prevent pages disclose separate tests for Spot Prevent; those are not transferable to Active Unify.

**Retrieval result:** no exact-SKU primary protocol/report for the 22%/15% figures was verified in this pass. Do not treat retail summaries as a primary study, and do not substitute a Spot Prevent paper or its subjects/outcomes.

**Disposition:** P17/P22 remain manufacturer-claim-led candidates only; P19 remains `not_linked`. Keep Active Unify separate from Spot Prevent. The sun-caused pigmentation claim does not establish a PIH endpoint.

#### P7 — Anua Azelaic Acid 10 Hyaluron Redness Soothing Serum

**Official serum source:** https://pages.anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum  
**Official routine page:** https://pages.anua.com/solutions/redness-prone-routine-sensitive-skin  
**Official pad page, explicitly a different product:** https://anua.com/products/azelaic-10-hyaluron-redness-soothing-pad

The official routine page, dated 2026-06-04, says 90% of participants agreed the appearance of red troubled spots improved in a clinical study of the **serum**. The page identifies 10% azelaic acid and sodium hyaluronate, but does not provide the study sample size, duration, comparator, validated endpoint, measurement method or full report.

The official **pad** page separately reports a clinical study at P&K Skin Research Center, 2025-01-20 to 2025-02-19, n=21 aged 20–59, concerning non-comedogenic suitability, redness/soothing of acne trouble areas and irritation from external physical stimulation. This protocol belongs to the pad and must not be transferred to the serum. The pad page's statement that redness is due to dryness and not associated with disease is a further boundary, not a rosacea treatment claim.

**Disposition:** serum P24 remains a `manufacturer_claim_only` / `candidate_only` lead with protocol details unknown. P26 remains `not_linked`; general redness language does not establish rosacea-specific efficacy. Pad evidence is explicitly excluded from the serum dossier.

### 11.2 Retrieval summary

| Product | Strongest source found this pass | Protocol availability | Evidence label / disposition |
|---|---|---|---|
| P1 COSRX | Official product page + official brand guide | Full report not public/verified | Manufacturer claims; new P08/P09 leads only; P02/P43 candidates only |
| P2 Neutrogena UK | Official UK product page; Boots repeats claim | n=34 and 4-week wording only; full protocol unavailable | P08 candidate only; no subtype link |
| P6 Clinique | Official product page with separate cohorts | Cohort sizes/durations/claim percentages shown; full methods unavailable | P17 candidate; P13/P19 unlinked |
| P5 ISDIN Active Unify | Official Active Unify page; retailer repeats 22%/15% figures | Exact-SKU primary report not verified | P17/P22 claim-led candidates; P19 unlinked; Spot Prevent excluded |
| P7 Anua serum | Official serum/routine page | 90% claim visible; sample/protocol details unavailable | P24 claim-led candidate; P26 unlinked; pad protocol excluded |

### 11.3 Evidence quality and governance decision

- This pass found additional public official claims, not a sufficient basis to approve any Product↔Problem relation.
- Manufacturer-hosted figures remain manufacturer claims unless the underlying report/protocol can be independently inspected and matched to the exact SKU, market and endpoint.
- Retailer repetition does not count as independent evidence.
- Ingredient lists, non-comedogenic labels, consumer-perception percentages and sunscreen positioning are not interchangeable with validated clinical endpoints.
- Product identity and target physical package/market/GTIN remain **NOT VERIFIED** for P1–P7.
- Approved Product↔Problem relations: **NONE**.
- Consultation-engine authorization: **NO / NOT AUTHORIZED** for P1–P7.
- No operational product records, ProductKnowledge rows, code, schema, API, UI, database or canonical Map/Working Records statuses were changed. Passes 1–10 remain unchanged.

### 11.4 Next action

Continue retrieval of primary reports or technical dossiers, prioritizing: (1) COSRX 2023 Dermacosmetic Skin Science Laboratory report including the blackhead/sebum endpoints; (2) Neutrogena UK 34-subject clinical grading protocol; (3) Clinique's distinct 52-, 536-, 533- and 433-person protocols; (4) ISDIN Active Unify-specific substantiation for the 22%/15% figures; and (5) Anua serum-specific protocol behind the 90% redness claim. If a report is not publicly accessible, record it as unavailable and keep the relation unlinked; do not fill gaps by inference.

**Change scope:** append-only research documentation. No implementation, operational product entry, accepted relation or merge authorization.


---

## Batch intake execution handoff — P1–P7 (2026-10-26)

**Product Owner direction:** all seven research products are to be entered together as one coordinated batch. P4/SKIN1004 is included and must not hold the other six products back. This is an execution handoff, not proof that any Product Master record exists.

### Batch manifest

| ID | Product identity from current dossier | Safe initial treatment | Do not infer / unresolved |
|---|---|---|---|
| P1 | COSRX The 6 Peptide Skin Booster Serum | SKIN; DRAFT; QA PENDING; identity review as needed | Select the actual size/packaging from catalog evidence; 150 ml and 50 ml variants exist; no GTIN guess |
| P2 | Neutrogena Clear & Defend 2% Salicylic Acid Face Wash, UK, 200 ml | SKIN; DRAFT; QA PENDING | Confirm current package/GTIN and label version; preserve UK market |
| P3 | Garnier Vitamin C Brightening Gel Cleanser, Australia, 200 ml | SKIN; DRAFT; QA PENDING | Confirm current package/GTIN and label version; preserve Australian market |
| P4 | SKIN1004 Madagascar Centella Hyalu-Cica Water-Fit Sun Serum, Korean/international SPF50+ PA++++ dossier | SKIN; DRAFT; QA PENDING | Korean/international formula is distinct from the US SPF50 drug-label formula; confirm actual package/GTIN before final identity verification |
| P5 | ISDIN FotoUltra 100 Active Unify SPF50+ | SKIN; DRAFT; QA PENDING | Pin market and package version; do not transfer evidence from Spot Prevent or assume a market-specific INCI |
| P6 | Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter, 100 ml | SKIN; DRAFT; QA PENDING | Confirm actual market/package/GTIN and current INCI |
| P7 | Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum, 30 ml | SKIN; DRAFT; QA PENDING | Confirm actual market/package/GTIN; do not transfer study evidence from the separate pad |

### Required per-item execution sequence

1. Use the existing official Product Intake UI and obtain an authenticated session.
2. Enter only supported identity facts from the dossier and any available catalog/label evidence; leave unknown GTIN, market, packaging version, variant or formula fields blank rather than inventing values.
3. Run the official DuplicateCheck for that exact identity snapshot. Stop and review any match, conflict, or stale check before creating.
4. Create only through the existing UI/API route. Preserve `status=DRAFT`, `qa_verdict=PENDING`, and a non-promoted identity status appropriate to the evidence. Do not submit, approve, activate, or auto-populate confirmed ProductKnowledge.
5. Read back the returned Product record and record its product ID, identity status, QA verdict, lifecycle status, DuplicateCheck result/reference, and verification evidence.
6. Repeat for all seven, then report a seven-row outcome matrix with CREATED / BLOCKED / DUPLICATE-REVIEW / NOT VERIFIED. A green CI run is not runtime entry evidence.

### Current execution state

- Batch scope decision: **RECORDED** in Issue #406 comment https://github.com/vahidmaghsoudi2/hbi/issues/406#issuecomment-6416661728.
- Research dossier for P1–P7: **AVAILABLE**, with identity and study limitations documented above.
- Authenticated runtime session and seven official DuplicateCheck/create/readback transactions: **NOT VERIFIED / NOT YET EXECUTED** in this handoff.
- Product Master records created by this documentation update: **NONE**.
- No direct database writes, seed changes, new parallel Product Master records, or automatic ProductKnowledge claims are authorized.

**Next action:** execute the same official intake workflow for all seven in one batch when an authenticated HBI runtime is available. Missing package-specific identifiers must remain explicit unknowns; they are not a reason to postpone the other products.


---

## Source-code execution path audit — official Product Intake (2026-10-26)

**Scope:** read-only inspection of the current `master` source files. This confirms code paths and guardrails only; it does not prove that the deployed runtime is reachable or that any product was created.

### Confirmed source paths

- API router registration: `app/main.py` mounts products at `/api/v1/products` and DuplicateCheck at `/api/v1/products/duplicate-check`.
- DuplicateCheck transaction: `POST /api/v1/products/duplicate-check/`, implemented by `app/api/routers/duplicate_checks.py`, calls `DuplicateCheckService.check(...)` and returns a persisted `check_id`, result, candidates, and provenance.
- Possible-match resolution: `POST /api/v1/products/duplicate-check/audit/{check_id}/decision`. A `POSSIBLE_MATCH` requires an operator decision; the create service expects the corresponding `duplicate_check_id` after a recorded `NEW` decision.
- Product creation: `POST /api/v1/products/`, implemented by `app/api/routers/products.py`, calls `ProductService.create_product_with_inventory(...)`. The service enforces DuplicateCheck, requires an explicit `product_line`, strips client-supplied governance fields, and initializes `status=DRAFT`, `qa_verdict=PENDING`, `identity_status=NEEDS_REVIEW`.
- Readback: `GET /api/v1/products/{product_id}`; authorized catalog listing is `GET /api/v1/products/manage`.
- Product registration also creates a zero-quantity Inventory anchor if one does not already exist. The code comment explicitly says this does not imply physical stock; no Stock-In transaction should be performed as part of this batch.

### Operational safeguards

1. Run DuplicateCheck separately for each exact product identity snapshot and preserve its `check_id` and result.
2. For `NEW`, proceed only with supported fields; for `POSSIBLE_MATCH`, resolve the audit using the authorized operator workflow before create; for `EXISTING` or unresolved conflict, do not create a second record.
3. `product_id` is required by the current create schema. Do not fabricate identifiers. Obtain an identifier through the existing approved intake convention/operator workflow before submitting create.
4. `product_line=SKIN` is required and must be an explicit operator classification. Unknown barcode, market, packaging version, variant, or formula must not be filled by inference.
5. Do not call submit, QA, identity-verification, approval, activation, Stock-In, or ProductKnowledge mutation endpoints for this initial registration batch.
6. After create, read back each product and preserve the returned product ID, status, identity status, QA verdict, DuplicateCheck audit reference/result, and any inventory-anchor behavior.

### Execution evidence boundary

- Code route and service behavior: **CONFIRMED BY SOURCE INSPECTION**.
- Authenticated deployed runtime, environment/base URL, and operator session: **NOT AVAILABLE/NOT VERIFIED in this session**.
- DuplicateCheck/create/readback transactions for P1–P7: **NOT EXECUTED / NO TRANSACTION EVIDENCE**.
- Product Master records created by this source audit: **NONE**.

This addendum records an execution-path audit only. It does not change the roadmap, intake contract, schema, API, UI, database, or any product record.


---

## Research pass 12 — current official-page refresh and formula/version drift check (2026-10-26)

**Purpose:** refresh the official pages for the product dossiers and identify source changes that could invalidate earlier formula or claim assumptions. This is append-only research. It does not verify the physical package/GTIN, establish independent finished-product efficacy, approve Product↔Problem links, or authorize ProductKnowledge changes.

### 12.1 P2 — Neutrogena Clear & Defend 2% Salicylic Acid Face Wash, UK, 200 ml

**Official source checked:** https://www.neutrogena.co.uk/skincare/cleansers-washes/clear-and-defend-daily-wash

The current official UK page continues to identify the 200 ml product and declare 2% salicylic acid. Its displayed INCI is: Aqua, Cocamidopropyl Hydroxysultaine, Sodium Methyl Cocoyl Taurate, Glycerin, Salicylic Acid, Sodium Hydrolyzed Potato Starch Dodecenylsuccinate, C12-15 Alkyl Lactate, Panthenol, Cocamidopropyl PG-Dimonium Chloride Phosphate, Disodium Tetrapropenyl Succinate, PEG-120 Methyl Glucose Dioleate, Sodium Chloride, Disodium EDTA, Citric Acid, Sodium Hydroxide, Tocopherol, Benzalkonium Chloride, Parfum. The page states that product and ingredients may change and directs users to check the package label. It reports “97% noticed less new spots in 4 weeks” based on clinical grading in 34 subjects; the full protocol remains unavailable on the page reviewed.

**Disposition:** preserve the prior exact UK-market dossier; current official web INCI is a source snapshot, not proof that a physical unit has the same formula. Keep the numeric result as a manufacturer-reported claim and P08 as a claim-led candidate only; no P09–P12 subtype relation is established.

### 12.2 P3 — Garnier Vitamin C Brightening Gel Cleanser, Australia, 200 ml

**Official source checked:** https://www.garnier.com.au/about-our-brands/skin-active/garnier-skin-active-vitamin-c-brightening-gel-cleanser-200ml

The current Australian page confirms the 200 ml rinse-off gel cleanser and labels its highlighted “Vitamin C” as **Vitamin Cg**. The displayed INCI is: Aqua/Water, Sodium Laureth Sulfate, Coco-Betaine, Sodium Chloride, Glycerin, Citrus Lemon Fruit Extract/Lemon Fruit Extract, PPG5-Ceteth-20, Sodium Hydroxide, Ascorbyl Glucoside, Citric Acid, Panthenol, Polyquaternium-7, Tocopheryl Acetate, Sodium Benzoate, Salicylic Acid, Linalool, Limonene, Benzyl Salicylate, Parfum/Fragrance. The page explicitly says ingredient lists are updated regularly and the received package is the current reference.

**Disposition:** use “Ascorbyl Glucoside / Vitamin Cg,” not “pure L-ascorbic acid.” This is a rinse-off formula; claims or study outcomes from leave-on vitamin-C products are not transferable. Fragrance constituents are a possible consideration for susceptible users, not evidence that every user will react. Physical package/GTIN remains unverified.

### 12.3 P4 — SKIN1004 Hyalu-Cica Water-Fit Sun Serum, international vs US formula

**International/Korean-style official page checked:** https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-spf50-pa?country=GB  
**US official page checked:** https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-uv

The international page names **SPF50+ PA++++** and displays a UV-filter system including Diethylamino Hydroxybenzoyl Hexyl Benzoate, Ethylhexyl Triazone, Methylene Bis-Benzotriazolyl Tetramethylbutylphenol and Diethylhexyl Butamido Triazone. The US page separately identifies a US sunscreen drug-product formula with active ingredients Avobenzone 2.7%, Homosalate 13.6%, Octisalate 4.5% and Octocrylene 9%; it also says the ingredient list may change and the package label is the latest reference.

**Disposition:** these are separate formula/market dossiers. Do not copy the US active-ingredient list or US SPF50 label into the international SPF50+ PA++++ record, and do not infer the target physical package solely from the product name. International formula's product-specific independent clinical efficacy remains NOT ESTABLISHED in the sources checked.

### 12.4 P5 — ISDIN FotoUltra 100 Active Unify SPF50+, Mexico

**Official Mexico page checked:** https://www.isdin.com/mx/p/fotoultra-active-unify-spf-50/1160

The current official page identifies a 50 ml product and reports 22% lower solar-spot intensity and 15% lower spot area after 28 and 84 days of normal use, based on 31 people aged 35–65 with mild-to-moderate facial hyperpigmented spots; the source labels the substantiation “Data on file, 2024.” The same page identifies the product's DP-Complex as niacinamide, esclareolida and Pisum sativum, highlights vitamin E, and gives sunscreen directions including generous application 30 minutes before exposure and reapplication every two hours and after sweating, swimming, bathing or towel drying.

**Disposition:** the percentages remain **MANUFACTURER_CLAIM** because the underlying report is not publicly available on the page. Keep the 2023 ex-vivo MMP claim separate from human clinical outcomes. Preserve Mexico market identity; do not merge with Spot Prevent, tinted Color variants, or other market formulas without exact identity/protocol reconciliation.

### 12.5 P6 — Clinique formula/name drift: current official page is not a safe substitute for the 100 ml dossier

**Previously recorded page:** https://www.clinique.com/product/4034/68008/skincare/serum/even-better-clinicaltm-radical-dark-spot-corrector-interrupter  
**Current redirect destination checked:** https://www.clinique.com/products/even-better-clinical-dark-spot-clearing-serum

The older URL now redirects to a page titled **Even Better Clinical Dark Spot Clearing Serum**. The current page reports different headline endpoints: up to 49% visible improvement in sun/age spots among top responders (22 of 53 panelists; 34% average improvement across all 53) and up to 56% visible improvement in post-acne mark intensity among top responders (9 of 34 panelists; 37% average across all 34), both after 12 weeks. It lists a formula including magnesium ascorbyl phosphate, ascorbyl glucoside, niacinamide, acetyl glucosamine, salicylic acid and Dimethoxytolyl Propylresorcinol/UP302-related material. The page advises checking the received package because ingredients may change.

**Critical version boundary:** these current results and the displayed ingredient list do **not** overwrite the earlier 100 ml “Radical Dark Spot Corrector + Interrupter” dossier or its previously recorded 52-woman/39% claim. The current page may represent a reformulation/rebranding, and the public redirect alone does not establish equivalence of formula, size, market, packaging or study cohort.

**Disposition:** keep the P6 target identity/formula and market **UNRESOLVED / NEEDS_REVIEW** until the actual 100 ml package/market is matched. Retain the older claim as historical source-bound manufacturer material; store current-page claims as a separate version/source lead only. No P17, P13 or P19 relation is approved from this page.

### 12.6 P7 — Anua Azelaic Acid 10 Hyaluron Redness Soothing Serum, US official page

**Official source checked:** https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum

The current US page identifies 10% azelaic acid and displays the following INCI: Water, Azelaic Acid, Propylene Glycol, Sodium Hydroxide, Dipropylene Glycol, 1,2-Hexanediol, Panthenol, Hydroxyethylcellulose, Betaine Salicylate, Glycerin, Biosaccharide Gum-1, Ethylhexylglycerin, Allantoin, Dipotassium Glycyrrhizate, Melia Azadirachta Leaf Extract, Camellia Sinensis Leaf Water, Sodium Hyaluronate, Melia Azadirachta Flower Extract, Niacinamide, Aloe Barbadensis Leaf Juice, Beta-Glucan, Centella Asiatica Extract, Centella Asiatica Leaf Extract, Centella Asiatica Root Extract, Madecassoside, Asiaticoside, Asiatic Acid, Madecassic Acid, Squalane, Zinc PCA, Butylene Glycol, Pentylene Glycol, Caprylyl/Capryl Glucoside, Hydrogenated Lecithin, Ceramide NP. The page directs users to start at 1–2 times per week and gradually increase frequency to up to twice daily; daytime use should be paired with SPF 30 or higher. It labels the testing results “Non-comedogenic, Low-Irritation,” but the page reviewed does not show a full protocol, sample size or statistical report.

**Disposition:** retain 10% as a manufacturer-declared concentration, and keep tolerability-test labels separate from proof of efficacy for acne, persistent redness, rosacea or pigmentation. The 90% participant-agreement statement remains a separate manufacturer claim from the brand routine page; do not infer that the current product page provides the missing protocol. Evidence for the separate Anua pad remains non-transferable to this serum.

### 12.7 P1 — COSRX official identity reminder

**Official source checked:** https://www.cosrx.com/collections/all/products/the-6-peptide-skin-booster-serum

The official page continues to offer 150 ml and 50 ml options under the same product family. The selected dossier remains the 150 ml research target, but the actual package/GTIN is not verified. The current page's ingredient list and manufacturer-reported outcome summaries do not expose a complete independent protocol. Do not assign the 50 ml GTIN or package identity to a 150 ml unit by name matching.

### 12.8 Research disposition after current-page refresh

- Official page refresh completed for P1, P2, P3, P4, P5, P6 and P7.
- Newly material discrepancy: **P6's prior official URL redirects to a differently named current serum page with different reported endpoints.** The current page must not silently replace the older 100 ml product dossier.
- P3's official Australian page confirms Vitamin Cg means Ascorbyl Glucoside and provides a current page-level INCI snapshot; package label remains authoritative for the physical unit.
- P4 international and US formulas remain explicitly separate.
- Exact physical package/GTIN verification: **NOT VERIFIED** for all seven.
- Publicly accessible exact-product independent efficacy protocols: **NOT ESTABLISHED** by this refresh; this is a bounded result, not proof of absence.
- Approved Product↔Problem relations: **NONE**. Existing crosswalk labels such as candidate-only or manufacturer-claim-only remain unchanged.
- Product lifecycle/QA/ProductKnowledge, schema, API, UI and database states: **UNCHANGED**.
- This addendum is append-only research in the existing ledger; it does not authorize merging PR #411 or any implementation change.


---

## Research pass 13 — P6 historical identity triangulation (2026-10-26)

**Purpose:** follow up the material Clinique name/formula drift recorded in pass 12. This pass checks whether public product pages independently support the older 100 ml target identity and whether the brand itself distinguishes it from the replacement. It does not establish the target user's physical unit, GTIN, market-specific formula, or the protocol behind historical efficacy claims.

### Sources checked

- Clinique historical product page, queried at the 100 ml size: https://www.clinique.com/product/4034/68008/skincare/serum/even-better-clinicaltm-radical-dark-spot-corrector-interrupter?size=3.4_fl._oz._%2F_100_ml
- Clinique discontinued-products page: https://www.clinique.com/discontinued-products/even-better-clinical-radical-dark-spot-corrector-interrupter
- Harrods 100 ml listing: https://www.harrods.com/en-gb/p/clinique-even-better-clinical-radical-dark-spot-correctorand-interrupter-100ml-000000000006795757
- Kohl's listing for the older named product: https://www.kohls.com/product/prd-5074573/clinique-even-better-clinical-radical-dark-spot-corrector-interrupter-serum.jsp

### Findings

1. The Clinique URL associated with the older name remains discoverable in search results with the title **Even Better Clinical Radical Dark Spot Corrector + Interrupter** and a 100 ml size parameter. Its indexed key-ingredient text names UP302 (Dimethoxytolyl Propylresorcinol), Ascorbyl Glucoside, and Salicylic Acid. This is consistent with the historical dossier's product name, but an indexed result or query parameter is not proof that the page currently serves a distinct, purchasable 100 ml formulation; the pass-12 observed redirect still matters.
2. Clinique's own discontinued-products page explicitly says **Radical Dark Spot Corrector + Interrupter is no longer available** and presents **Even Better Clinical Dark Spot Clearing Serum** as its replacement. This is direct brand evidence that the names should not be silently treated as one unchanged live SKU.
3. Harrods independently lists the older product name at **100 ml** and displays an INCI beginning Water/Aqua/Eau, Cyclopentasiloxane, Dimethicone, Polysilicone-11, Isododecane, Butylene Glycol, Ascorbyl Glucoside, with Salicylic Acid, Acetyl Glucosamine and Dimethoxytolyl Propylresorcinol later in the list. Kohl's displays the same older-name ingredient pattern. These retailer listings support the existence of a historical 100 ml product dossier; they do not establish the formula on a physical unit now in hand or resolve market/lot variation.
4. The older-name INCI displayed by these listings differs from the newer page snapshot recorded in pass 12, which includes Magnesium Ascorbyl Phosphate and other listed components. The safest interpretation is **distinct historical versus current-page source snapshots**, not a merged formula.
5. The historical product's 52-woman/39% claim remains a source-bound manufacturer claim from earlier ledger research. This pass did not locate the underlying full study protocol or independently verify its endpoint, cohort, statistical analysis, or exact correspondence to every 100 ml market variant.

### P6 disposition update

- Historical name/100 ml product existence: **SUPPORTED BY BRAND/RETAILER PAGE EVIDENCE**, bounded to the source records above.
- Current brand position: **DISCONTINUED; brand identifies Dark Spot Clearing Serum as replacement**.
- Exact physical package, GTIN, market, formula/lot match: **UNVERIFIED / NEEDS_REVIEW**.
- Formula relationship: preserve historical and current-page INCI snapshots separately; do not combine ingredient lists or transfer claims between them.
- Historical efficacy protocol: **NOT INDEPENDENTLY VERIFIED**.
- Product↔Problem relation: no relation approved by this pass; P17/P19 remain candidate-only or unresolved as already recorded.

This is an append-only evidence update to the existing seven-product ledger. It does not modify product records, lifecycle/QA state, ProductKnowledge, schema, API, UI, database, or the Skin Problem Space's P01–P61 relation criteria.

---

## Intake identity decisions — user confirmation batch (2026-10-27)

**Purpose:** record the user's consolidated answers as research-target/identity-intake decisions. These decisions supersede any implication in older section headings that a research-source market is confirmed for the target physical unit. They do not establish physical-package identity unless explicitly stated, and they do not create or approve Product Master/ProductKnowledge records.

| Product | User-confirmed decision | Market / physical identity status | Handling rule |
|---|---|---|---|
| P1 — COSRX The 6 Peptide Skin Booster Serum | **150 ml — temporary research target** | Actual package/GTIN and formula match remain **UNVERIFIED**. | Keep the 150 ml dossier as the research target only; do not treat the selected size as confirmation of a physical unit. |
| P3 — Garnier Vitamin C Brightening Gel Cleanser | **200 ml — volume confirmed by user** | Market = **UNKNOWN**. Australia remains an official research source, not confirmation of the user's target market or package. Physical package/GTIN remain **UNVERIFIED**. | Keep the Australian source snapshot separate; do not assign Australia as the target unit's market. |
| P4 — SKIN1004 Madagascar Centella Hyalu-Cica Water-Fit Sun Serum | **Korean/international version selected as research target** | Physical package/GTIN and exact formula match remain **UNVERIFIED**. | Keep the US sunscreen-drug formula in a separate dossier; no formula transfer between US and Korean/international versions. |
| P5 — ISDIN FotoUltra 100 Active Unify SPF50+ | **50 ml — temporary research target** | Market = **UNKNOWN**; physical package/GTIN and formula match remain **UNVERIFIED**. | Mexico remains a source-specific research snapshot only; do not assign Mexico or another market to the target unit. |
| P6 — Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter | **Historical 100 ml version selected as research target** | Brand marks the older product discontinued; physical package/GTIN, market and formula/lot match remain **UNVERIFIED / NEEDS_REVIEW**. | Preserve the historical dossier separately from the replacement/current Dark Spot Clearing Serum. Do not transfer current-page ingredients or efficacy claims to the historical version. |
| P7 — Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum | **30 ml serum selected as research target** | Physical package/GTIN and market-specific formula match remain **UNVERIFIED**. | Keep the serum separate from Anua azelaic-acid pads; do not infer physical-unit identity from the product name alone. |

### Batch-level disposition

- P2 remains as previously recorded: 200 ml user-confirmed; market unknown; GTIN not provided; package/formula match unverified.
- P1 and P5 sizes are **temporary research targets**, not confirmed physical-package facts.
- P3's 200 ml volume is user-confirmed, but its target market is explicitly **UNKNOWN**; the Australia page is source context only.
- P4's Korean/international version is the selected research target, not proof that a physical package has been inspected.
- P6 is explicitly the historical 100 ml product target; the replacement/current serum remains a separate product/version.
- P7 is the 30 ml serum target, not the separate pad product.
- For every product, missing GTIN, package, market or formula facts remain unknown/unverified rather than inferred.
- This update records intake decisions only. **No Product Master create, DuplicateCheck, readback, QA approval, ProductKnowledge write, activation, stock-in or live runtime transaction was executed by this documentation update.** Product Master records created by this update: **NONE**.
- Continue the existing official batch-intake procedure when an authenticated runtime/operator session is available; preserve DuplicateCheck and readback evidence for each actual transaction.


---
## Research pass 14 — product-feature ↔ canonical skin-problem candidate matrix (2026-10-29)

**Purpose:** continue the existing Product Features ↔ Skin Problem Space work using only evidence and decisions already recorded in this ledger and the owner-designated P01–P61 Map. This is a structured candidate crosswalk in the existing research ledger, not a new research pass from outside sources and not a persisted/approved runtime relationship.

### Decision rules applied

- Product-feature statements are not automatically skin-problem relations. Each cell is limited by the specific recorded claim, the product's exposure/formula/version, and the current P01–P61 boundary.
- `manufacturer_claim_only` means the relevant outcome is a manufacturer-reported claim, not independently established efficacy.
- `candidate_only` means a narrow relationship is plausible for review but is not approved or recommendation-authorizing.
- `not_linked` means the existing record does not support a defensible product-to-problem relation at this stage.
- Identity uncertainty remains a blocker where the formula/version matters. The selected research target is not proof of a physical package.
- No canonical P-code is promoted to an accepted Need. No recommendation permission is granted. No new P-code is created.

### Current seven-product crosswalk

| Ledger product | Existing product-feature basis | Canonical P-code candidate | Current disposition | Why this boundary is retained |
|---|---|---|---|---|
| P1 — COSRX The 6 Peptide Skin Booster Serum, 150 ml research target | Existing ledger records manufacturer-reported deep-moisture and texture outcomes; humectants and peptides are listed. Full protocol and physical package/GTIN are not verified. | P02 — dehydration/impaired moisture retention | `manufacturer_claim_only` + `candidate_only` | The moisture endpoint is manufacturer-reported; the exact physical SKU and full protocol remain unverified. P02 remains a related manifestation to P01, not an accepted independent Need. |
| P1 — COSRX | Existing ledger records a manufacturer-reported texture outcome. | P43 — uneven skin texture | `manufacturer_claim_only` + `candidate_only`, boundary-open | Only the stated texture endpoint is relevant. Do not map radiance, fine lines or density to P43 by analogy; the Map marks P43 boundary as open. |
| P1 — COSRX | Peptides/niacinamide or a general clarity/radiance claim, without a verified dark-spot endpoint. | P17 — hyperpigmentation/dark spots | `not_linked` | Ingredient presence and general clarity/radiance do not establish a product-specific hyperpigmentation outcome. |
| P2 — Neutrogena Clear & Defend 2% Salicylic Acid Face Wash, 200 ml research target | Existing UK-source dossier records a manufacturer statement that 97% noticed fewer new spots in four weeks (n=34, clinical grading); the target market/package remains unverified. | P08 — acne | `manufacturer_claim_only` + `candidate_only` | “Fewer new spots” is not a cure rate; full protocol and physical-unit identity are unverified. The relation is exploratory and not recommendation-authorizing. |
| P2 — Neutrogena | Existing formula lists 2% salicylic acid and cleansing surfactants; no direct recorded endpoint for sebum, open comedones or closed comedones. | P03, P09, P10 | `not_linked` | Ingredient-level rationale is not a finished-product result. Do not infer P09/P10 from a broad acne/spot claim; do not infer P11/P12. |
| P3 — Garnier Vitamin C Brightening Gel Cleanser, 200 ml research target | Existing ledger records a rinse-off cleanser, Ascorbyl Glucoside/Vitamin Cg, salicylic acid, surfactants, humectants and fragrance components; no verified product-specific problem endpoint. | P03, P08, P09, P10, P17 | `not_linked` | The current evidence basis is ingredient/category/name-level. Do not convert “brightening” or ingredient presence into a P-code relationship. Target market and physical package remain unverified. |
| P4 — SKIN1004 Hyalu-Cica Water-Fit Sun Serum, Korean/international research target | Existing ledger records SPF50+ PA++++ and manufacturer-published UV protection test summaries; exact physical package remains unverified. | P22 — sun-related pigmentation / UV context | `candidate_only` (context/prevention only) | P22 is a context/presentation relation. Sunscreen protection does not prove treatment of existing dark spots or chronic UV damage. Keep the US sunscreen-drug formula separate. |
| P4 — SKIN1004 | Existing ledger records manufacturer-published hydration test information for the Korean/international product. | P02 — dehydration/impaired moisture retention | `manufacturer_claim_only` + `candidate_only` | This is a version-specific manufacturer test summary, not independent efficacy proof. Do not transfer it to the US formula or infer treatment of P01 dryness. |
| P4 — SKIN1004 | Sunscreen/UV protection alone. | P17 — hyperpigmentation/dark spots | `not_linked` | Prevention/context is not evidence of treatment for existing pigmentation. |
| P5 — ISDIN FotoUltra 100 Active Unify SPF50+, 50 ml research target | Existing ledger records manufacturer-reported reductions in spot intensity/area in 31 participants; underlying report is not public in the recorded sources and market/physical unit are unverified. | P17 — hyperpigmentation/dark spots | `manufacturer_claim_only` + `candidate_only` | Outcome is a manufacturer claim with unresolved protocol and exact version correspondence. Do not present the percentages as independently verified efficacy. |
| P5 — ISDIN | Existing product positioning and UV-protection role in the ledger. | P22 — sun-related pigmentation / UV context | `candidate_only` (context/prevention only) | Context/prevention is distinct from treatment of existing pigmentation. P51 remains context/not Need-level and is not a treatment link. |
| P5 — ISDIN | Recorded broad spot-intensity/area endpoint does not specifically establish post-inflammatory etiology. | P19 — post-inflammatory hyperpigmentation | `not_linked` | Do not infer PIH from a general dark-spot result. |
| P6 — Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter, historical 100 ml research target | Existing ledger records the historical manufacturer-reported 39% visible dark-spot reduction in 52 women; the target product is discontinued and physical package/market/formula match remain unverified. | P17 — hyperpigmentation/dark spots | `manufacturer_claim_only` + `candidate_only` | Historical, version-bound claim only. Keep separate from the replacement Dark Spot Clearing Serum and from the distinct n=533 consumer test. |
| P6 — Clinique | Existing historical dark-spot claim does not establish PIH-specific results or a medical indication. | P19, P18 | `not_linked` | Do not infer post-inflammatory hyperpigmentation or melasma treatment from a general cosmetic dark-spot claim. P18 is a Clinical Condition/Clinical Anchor. |
| P7 — Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum, 30 ml research target | Existing ledger records manufacturer-declared 10% azelaic acid, the serum's ingredient list, gradual-introduction advice, and a manufacturer-reported 90% agreement statement; full protocol and exact physical package remain unverified. | P08 — acne; P13 — acne aftermath/discoloration; P19 — post-inflammatory hyperpigmentation | `candidate_only` for further boundary review; `not_linked` for recommendation | Ingredient-level azelaic-acid evidence and a broad “red troubled spots” statement do not establish efficacy of this finished serum for every acne/PIH subtype. Do not transfer evidence from the separate pad. |
| P7 — Anua | Manufacturer's redness-soothing positioning and tolerability labels. | P24 — persistent redness; P26 — rosacea | `not_linked` | Redness, irritation, and rosacea are not interchangeable. Tolerability wording is not proof of treatment for persistent redness or rosacea. |

### Crosswalk result and handoff

- **Candidate-only review rows:** P1→P02/P43; P2→P08; P4→P22/P02; P5→P17/P22; P6→P17; P7→P08/P13/P19 (candidate review only, no recommendation link).
- **Explicitly not linked at this stage:** P1→P17; P2→P03/P09/P10; P3→P03/P08/P09/P10/P17; P4→P17; P5→P19; P6→P18/P19; P7→P24/P26.
- These are **research dispositions only**. They do not create database relationships, ProductKnowledge records, Evidence rows, approved product/problem links, accepted Needs, or recommendation permissions.
- The current Skin Problem Space Map remains the sole P01–P61 list. Its stated boundary labels remain unchanged. Any relation needing a clinical condition, an unresolved boundary, or evidence not present in this ledger stays `not_linked` / `UNKNOWN`.
- The next work within the existing path is to compare these candidate cells against the already-existing Skin Problem Space Working Records/status decisions in Issue #403 and preserve any narrower current disposition there. Do not change problem statuses to make this crosswalk appear complete.
- No outside sources were searched for this pass. No new Issue/PR or parallel document was created. No code, API, schema, UI, database, QA, lifecycle or ProductKnowledge state was changed. G8 remains **BLOCKED / NOT VERIFIED**.


---

## Research pass 15 — two-example bounded semantic pilot (2026-10-29)

**Purpose:** exercise the two-decision method against the already-recorded P2/Neutrogena and P5/ISDIN dossiers. This pass uses the sources and limitations already in this ledger and the canonical Map/Working Records; it is not a new external research pass, independent second-team review, ProductKnowledge approval, or a persisted Product↔Problem relationship.

### Guardrails and input readiness

- The existing Research pass 14 crosswalk is retained; this section tests its two candidate rows rather than creating a second matrix.
- Product Master IDs have **not** been matched to P2 and P5 in this pass. Research labels P2/P5 are ledger identifiers, not proof of a matching operational `product_id`.
- Neutrogena target: 200 ml is user-confirmed, but target market, physical package, GTIN and formula match remain UNKNOWN/UNVERIFIED. The UK manufacturer page is source context, not proof of the target unit's market/version.
- ISDIN target: 50 ml is a temporary research target; target market, physical package, GTIN and formula match remain UNKNOWN/UNVERIFIED. The Mexico page is source context, not proof of the target unit's market/version.
- Map/Working Records boundary: P08 is mapped as an acne problem/clinical presentation, but its operational definition remains UNKNOWN and Accepted=No. P17 is mapped as hyperpigmentation/dark spots, but its operational definition remains UNKNOWN and Accepted=No. Structural presence in the Map is not problem acceptance or recommendation permission.

### Pilot A — Neutrogena Clear & Defend 2% Salicylic Acid Face Wash ↔ P08

**Bounded proposition under review:** The existing UK official product page reports that 97% of 34 participants noticed fewer new spots after four weeks, assessed by clinical grading; the same page declares 2% salicylic acid and gives rinse-off directions. This is a statement about what the manufacturer page reports, not a claim that 97% were cured or that the result has been independently verified.

| Decision question | Finding | Basis and limitation |
|---|---|---|
| 1. Does the recorded source support the exact attribution? | **YES — attribution only.** | The ledger records the UK official source and its stated n=34/four-week result. Source: https://www.neutrogena.co.uk/skincare/cleansers-washes/clear-and-defend-daily-wash |
| 2. Do the accessible details establish the claimed outcome independently? | **NOT ESTABLISHED.** | The full protocol/control, absolute change and independent exact-SKU evidence are not established in the recorded sources. The manufacturer statement must remain a manufacturer-reported claim. |
| 3. Is the claim sufficient to support a relation to the target product and P08? | **CANDIDATE ONLY / NEEDS REVIEW.** | “Fewer new spots” is narrowly relevant to the broad P08 acne presentation, but target package/market/formula identity is unresolved and P08's operational definition/acceptance is unresolved. No P09–P12 subtype or P13 aftermath/PIH relation is inferred. |
| Current permitted use | **Research review only.** | No approved relationship, finished-product efficacy conclusion, individual recommendation, or ProductKnowledge promotion. |

**Pilot A disposition:** retain the existing P2→P08 candidate only. Do not upgrade it to supported. The main blockers are physical SKU/market match, the missing full study protocol, and the unaccepted/operationally undefined P08 record.

### Pilot B — ISDIN FotoUltra 100 Active Unify SPF50+ ↔ P17

**Bounded proposition under review:** The existing Mexico manufacturer page reports a 22% reduction in spot intensity and a 15% reduction in spot area in 31 participants aged 35–65 with mild/moderate facial hyperpigmentation, with assessments reported at 28 and 84 days. The underlying report/protocol is not available in the recorded public source. These are manufacturer-reported results, not independently verified efficacy.

| Decision question | Finding | Basis and limitation |
|---|---|---|
| 1. Does the recorded source support the exact attribution? | **YES — attribution only.** | The ledger records the Mexico official page and its reported sample, population and outcomes. Source: https://www.isdin.com/mx/p/fotoultra-active-unify-spf-50/1160 |
| 2. Do the accessible details establish the claimed outcome independently? | **NOT ESTABLISHED.** | The complete protocol, control, blinding, instruments, statistical report and independent exact-formula evidence are not established in the recorded sources. “Data on file” is provenance for a manufacturer-held report, not independent verification. |
| 3. Is the claim sufficient to support a relation to the target product and P17? | **CANDIDATE ONLY / NEEDS REVIEW.** | The reported dark-spot intensity/area endpoints are relevant to the broad P17 presentation, but target market/package/formula identity is unresolved and P17's operational definition/acceptance is unresolved. The claim does not establish P19 (post-inflammatory hyperpigmentation). P22 remains context-only unless the exact claim and evidence separately establish the sun-related context; sunscreen status alone is not sufficient. |
| Current permitted use | **Research review only.** | No approved relationship, finished-product efficacy conclusion, individual recommendation, or ProductKnowledge promotion. |

**Pilot B disposition:** retain the existing P5→P17 candidate only. Do not upgrade it to supported. The main blockers are physical SKU/market match, unavailable full protocol, and the unaccepted/operationally undefined P17 record.

### Cross-pilot findings

1. The source can support that a manufacturer made a bounded claim without independently proving the outcome described by that claim.
2. Product-specific relation decisions require an additional check of target SKU/version, endpoint-to-problem fit and the canonical problem's current boundary/status.
3. Neither sample supports automatic extension to adjacent P-codes. For Neutrogena, acne/“new spots” does not automatically imply subtypes, scarring or PIH. For ISDIN, general dark-spot endpoints do not establish PIH, and sunscreen category alone does not establish a P22 relationship.
4. UNKNOWN identity or missing protocol must remain visible. Neither is proof of ineffectiveness; neither permits a supported relationship.
5. A complete two-way *software* search was not tested. Only the semantic consistency requirement was reviewed: any future product→problem and problem→product views must return the same relationship, claim, limitations and status. No existing software capability is presumed.
6. The two pilot entries are a first-pass assessment by this workstream. Independent review by the Product Features team and joint adjudication have **not yet been performed**; no reviewer/date is invented.
7. No Product Master, Evidence, ProductKnowledge, QA, lifecycle, database, API, schema, UI or problem-bank status was changed. No new P-code, Need, parallel document or relationship record was created. G8 remains **BLOCKED / NOT VERIFIED**.

### Handoff after this pass

- Product Features team: independently check the two source attributions and the recorded identity/protocol gaps; report only corrections or new evidence, not a repeat of the existing dossier.
- Skin Problem team: confirm whether the P08/P17 boundary notes above faithfully reflect the current Map and Working Records; do not treat this as a request to accept either problem.
- Joint next gate: compare both reviews and decide whether the temporary semantic format is sufficient. Only then decide whether any genuine gap requires a bounded proposal in Issue #406. No implementation is authorized by this pass.


---

## Research pass 16 — six remaining dossiers normalized to the five-stage Product Features standard (2026-10-30)

**Purpose:** continue the existing seven-product ledger after the bounded ISDIN P5 pilot. This pass normalizes P1, P2, P3, P4, P6 and P7 against the five-stage working standard recorded in PR #480. It uses only source snapshots, user identity decisions and limitations already recorded in this ledger; it is not a fresh external research sweep, physical-package inspection, runtime audit, independent clinical validation, or approval of Product↔Problem relationships.

**Standard reference:** [PR #480 — Product Features to Skin Problem Linking Standard V1 / ISDIN P5 pilot](https://github.com/vahidmaghsoudi2/hbi/pull/480). PR #480 remains Draft/Open/Unmerged at the time of this pass; the standard is applied here as a working research protocol, not represented as merged policy.

### A. P1 — COSRX The 6 Peptide Skin Booster Serum, 150 ml research target

**1. Identity and version**
- Research label: P1; not an operational Product Master ID.
- User-selected research target: 150 ml. The official COSRX product page offers 150 ml and 50 ml options under the same product family.
- Physical package, GTIN, target market and exact package-to-page/formula match: **UNKNOWN / NOT VERIFIED**. Do not infer 150 ml physical identity from the selected research target or borrow the 50 ml GTIN.

**2. Features and function**
- Existing official-page snapshot records a peptide/humectant-oriented leave-on skin booster and manufacturer-reported outcomes concerning deep moisture, texture, clarity/radiance and related cosmetic endpoints.
- Ingredient-role notes remain label-level observations from the recorded official page; ingredient presence does not establish the finished product's clinical effect.
- The source-recorded moisture and texture figures remain manufacturer-reported. No ingredient or claim is converted into a medical indication.

**3. Evidence and provenance**
- Primary source already recorded: https://www.cosrx.com/collections/all/products/the-6-peptide-skin-booster-serum
- The page-level claim summary and named test context are attributable to the manufacturer. Complete study protocol, measurement methods, comparator, statistical plan and independently reviewable report remain **NOT VERIFIED** in the ledger.
- No exact physical package/GTIN match or independent finished-product efficacy report is established.

**4. Fit and limitations**
- Moisture and texture outcomes are narrow cosmetic endpoints only. They do not establish treatment of a diagnosed skin condition, nor can they be expanded to fine lines, density, radiance or pigmentation by analogy.
- Any tolerance or suitability assessment requires the actual package INCI and user-specific context; the present dossier does not establish universal suitability.

**5. Canonical problem-link candidates**
- P02: manufacturer-claim-only / candidate-only, limited to the recorded moisture endpoint; P02's relationship to P01 and its acceptance boundary remain governed by the canonical Map/Working Records.
- P43: manufacturer-claim-only / candidate-only, limited to the recorded texture endpoint; the P43 boundary remains open.
- P17: **not linked**. General clarity/radiance language or ingredient presence is insufficient.
- No supported relation or recommendation permission.

### B. P2 — Neutrogena Clear & Defend 2% Salicylic Acid Face Wash, 200 ml research target

**1. Identity and version**
- Research label: P2; not an operational Product Master ID.
- User-confirmed target volume: 200 ml. The UK official page is the source context for the recorded formula/claim; it does not prove that the user's physical target is the UK-market package.
- Target market, package photograph, GTIN, exact current INCI and physical package-to-page match: **UNKNOWN / NOT VERIFIED**.

**2. Features and function**
- Existing UK source snapshot declares 2% salicylic acid and identifies a rinse-off daily face wash.
- The same manufacturer page reports that 97% of 34 participants noticed fewer new spots after four weeks, described as clinical grading.
- Salicylic acid presence is a formula fact from the source page; it is not independent proof that the finished wash achieves a specific acne endpoint.

**3. Evidence and provenance**
- Primary source already recorded: https://www.neutrogena.co.uk/skincare/cleansers-washes/clear-and-defend-daily-wash
- The 97% / n=34 / four-week statement is a manufacturer-reported result. Full protocol, comparator/control, baseline and absolute change, definition/counting of “new spots,” statistical analysis and independent exact-SKU report remain **NOT VERIFIED**.
- The source's UK market identity must not be assigned to the physical target without package/GTIN evidence.

**4. Fit and limitations**
- A rinse-off product's exposure differs from a leave-on product; no efficacy transfer from leave-on salicylic-acid studies is allowed.
- “Fewer new spots” is not a cure rate and does not establish all acne presentations, severity, scarring, PIH or a subtype-specific outcome.
- Current package instructions and precautions must be taken from the actual package when available.

**5. Canonical problem-link candidates**
- P08: manufacturer-claim-only / candidate-only, narrowly tied to the reported fewer-new-spots endpoint; P08 operational definition and acceptance remain unresolved in Working Records.
- P03, P09 and P10: **not linked** from the current evidence; no direct sebum/open-comedone/closed-comedone endpoint is recorded.
- No inference to P11/P12, P13 or P19; no supported relation or recommendation permission.

### C. P3 — Garnier Vitamin C Brightening Gel Cleanser, 200 ml research target

**1. Identity and version**
- Research label: P3; not an operational Product Master ID.
- User-confirmed volume: 200 ml. User did not confirm Australia as the market; Australia is only the official source-page market recorded in the dossier.
- Physical package, target market, GTIN and package-to-page/formula match: **UNKNOWN / NOT VERIFIED**.

**2. Features and function**
- Existing Australian official-page snapshot identifies a rinse-off gel cleanser and displays Ascorbyl Glucoside (Vitamin Cg), salicylic acid, surfactants, glycerin, panthenol and fragrance constituents including parfum and listed fragrance allergens.
- Use “Ascorbyl Glucoside / Vitamin Cg”; do not relabel it as pure L-ascorbic acid.
- The ingredient list is a source-page snapshot and may change; the received package label remains authoritative for the physical unit.

**3. Evidence and provenance**
- Primary source already recorded: https://www.garnier.com.au/about-our-brands/skin-active/garnier-skin-active-vitamin-c-brightening-gel-cleanser-200ml
- The current dossier contains no verified exact-finished-product clinical protocol for a canonical skin-problem endpoint.
- Ingredient declaration and “brightening” positioning are source-attributable facts/claims, not proof of treatment efficacy.

**4. Fit and limitations**
- Rinse-off exposure limits transfer from leave-on vitamin-C or salicylic-acid studies.
- Fragrance constituents may be relevant when assessing an individual's sensitivities, but their presence does not prove that every user will react.
- No medical, pigment-treatment or acne-treatment suitability conclusion is established by the present evidence.

**5. Canonical problem-link candidates**
- P03, P08, P09, P10 and P17: **not linked** on current evidence. Ingredient/category/name-level rationale is insufficient to assign a P-code.
- No supported relation or recommendation permission.

### D. P4 — SKIN1004 Madagascar Centella Hyalu-Cica Water-Fit Sun Serum, Korean/international research target

**1. Identity and version**
- Research label: P4; not an operational Product Master ID.
- User-selected target: Korean/international formula. This is a research-version decision, not proof of a physical package.
- International/Korean-style SPF50+ PA++++ dossier and US SPF50 sunscreen-drug formula remain separate. Physical package, GTIN and exact formula match: **UNKNOWN / NOT VERIFIED**.

**2. Features and function**
- Existing international official-page snapshot identifies SPF50+ PA++++ and an organic UV-filter system; it also records niacinamide, glycerin, centella and hyaluronic-acid-related ingredients in the page-level formula.
- Existing manufacturer-published UV-protection and hydration test summaries remain attributed to that international formula only.
- The US page separately lists Avobenzone 2.7%, Homosalate 13.6%, Octisalate 4.5% and Octocrylene 9%; these US active ingredients must not be copied into the international formula record.

**3. Evidence and provenance**
- International source already recorded: https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-spf50-pa?country=GB
- US source already recorded for version separation: https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-uv
- UV-protection/hydration summaries are manufacturer-source material. Independent exact-version clinical evidence for treatment of existing pigmentation or a skin condition is **NOT ESTABLISHED** in the ledger.
- Actual package, GTIN and current label correspondence remain unverified.

**4. Fit and limitations**
- UV protection/prevention context is not treatment evidence for existing dark spots, melasma, PIH or chronic UV damage.
- Hydration positioning/test summaries do not establish treatment of P01 dryness or every P02 presentation.
- Use, reapplication and precautions must follow the actual market-specific package label; do not combine US and international instructions or formulas.

**5. Canonical problem-link candidates**
- P22: context/prevention candidate only, subject to the canonical Map boundary; not an independent Need or treatment link.
- P02: manufacturer-claim-only / candidate-only, restricted to the recorded international-formula hydration test summary.
- P17: **not linked** from sunscreen status or UV protection alone.
- No supported relation or recommendation permission.

### E. P6 — Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter, historical 100 ml research target

**1. Identity and version**
- Research label: P6; not an operational Product Master ID.
- User-selected target is the historical 100 ml product named “Even Better Clinical Radical Dark Spot Corrector + Interrupter.”
- The brand identifies the older product as discontinued and presents “Even Better Clinical Dark Spot Clearing Serum” as its replacement. These are not assumed to be the same unchanged SKU.
- Physical historical package, GTIN, market, lot and exact INCI match: **UNKNOWN / NOT VERIFIED**.

**2. Features and function**
- Historical dossier retains the older product name, historical source-bound INCI snapshot and the previously recorded 52-woman / 39% visible dark-spot manufacturer claim.
- Retailer snapshots support the existence of an older 100 ml product and display a historical INCI pattern; they do not establish the formula of a physical unit now in hand.
- The newer/current Dark Spot Clearing Serum page reports different endpoints and a different displayed INCI snapshot. Keep it as a separate version/source record; do not merge it into the historical dossier.

**3. Evidence and provenance**
- Historical product source and retailer references are recorded in Research pass 13; the brand discontinuation/replacement page is recorded there as well.
- The historical 52-woman / 39% result remains a manufacturer claim. Full study protocol, comparator, endpoint method, statistics and independent exact-market/100 ml formula verification remain **NOT VERIFIED**.
- Current-page 12-week outcomes (including separate sun/age-spot and post-acne-mark cohorts) are not transferable to the historical 100 ml product.

**4. Fit and limitations**
- Historical dark-spot positioning does not establish PIH-specific or melasma-specific efficacy, a medical indication, or suitability for every pigmentation cause.
- Do not transfer ingredients, efficacy figures or study populations from the replacement product to the historical product.
- The discontinued status and lack of physical-unit verification materially limit operational intake and any current-use assumption.

**5. Canonical problem-link candidates**
- P17: historical manufacturer-claim-only / candidate-only, limited to the older product's recorded dark-spot claim.
- P18 and P19: **not linked**; general dark-spot claims do not establish melasma or post-inflammatory etiology.
- No supported relation or recommendation permission.

### F. P7 — Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum, 30 ml research target

**1. Identity and version**
- Research label: P7; not an operational Product Master ID.
- User-selected research target: 30 ml serum. Keep it distinct from Anua azelaic-acid pads and from any regional package/formula not matched to the target.
- Physical package, market, GTIN and exact package-to-page/formula match: **UNKNOWN / NOT VERIFIED**.

**2. Features and function**
- Existing US official-page snapshot declares 10% azelaic acid and lists the serum INCI, including panthenol, betaine salicylate, glycerin, allantoin, niacinamide, centella-related ingredients, sodium hyaluronate, squalane and ceramide NP.
- The page advises gradual introduction (starting 1–2 times weekly and increasing as tolerated, up to twice daily) and daytime SPF use.
- “Non-comedogenic” and “low-irritation” are manufacturer test labels; they are not efficacy findings for acne, rosacea, PIH or persistent redness.
- The 90% agreement statement is a separate manufacturer claim from the official routine/claim page, not a protocol disclosed on the serum product page.

**3. Evidence and provenance**
- Product source already recorded: https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum
- Separate routine/claim source already recorded: https://pages.anua.com/solutions/redness-prone-routine-sensitive-skin
- Full serum-specific study protocol/report, sample details, validated endpoint, comparator and statistical analysis for the 90% claim remain **NOT VERIFIED**.
- Evidence for the separate azelaic-acid pad is **NON-TRANSFERABLE** to this serum.

**4. Fit and limitations**
- Ingredient-level evidence for azelaic acid is not automatically finished-serum efficacy evidence.
- Redness, irritation, acne, PIH and rosacea are not interchangeable endpoints. The serum's positioning and tolerability labels do not establish treatment of P24 or P26.
- Follow the actual package instructions and assess tolerability; no universal suitability claim is made.

**5. Canonical problem-link candidates**
- P08, P13 and P19: retain only the previously recorded candidate-review status where applicable; no subtype-specific or recommendation relationship is established from ingredient presence or the broad “red troubled spots” claim.
- P24 and P26: **not linked**; no persistent-redness or rosacea treatment inference.
- No supported relation or recommendation permission.

### G. Consolidated six-dossier completion status and handoff

| Research dossier | Five-stage normalization | Main unresolved identity item | Evidence limitation | Current P-code handling |
|---|---|---|---|---|
| P1 COSRX | Recorded in this pass | Physical 150 ml package, GTIN, market/formula match | Manufacturer claim summaries; full protocol not verified | P02/P43 candidate-only; P17 not_linked |
| P2 Neutrogena | Recorded in this pass | Market, package, GTIN and formula match | Manufacturer 34-subject claim; full protocol not verified | P08 candidate-only; subtypes not_linked |
| P3 Garnier | Recorded in this pass | Market, package and GTIN | No exact-product problem-endpoint protocol verified | No P-code link |
| P4 SKIN1004 | Recorded in this pass | Physical international/Korean package and GTIN | Manufacturer summaries; no exact-version treatment evidence verified | P22 context-only; P02 candidate-only; P17 not_linked |
| P6 Clinique historical | Recorded in this pass | Physical historical 100 ml package, market, GTIN and formula/lot | Historical manufacturer claim; protocol not verified; replacement is distinct | P17 candidate-only; P18/P19 not_linked |
| P7 Anua | Recorded in this pass | Physical 30 ml package, market, GTIN and formula | Manufacturer claim; serum protocol not verified; pad evidence excluded | Existing P08/P13/P19 candidates remain review-only; P24/P26 not_linked |

**Completion meaning:** the six existing research dossiers are now organized against the five-stage working standard using the evidence already recorded. This is documentary normalization, not proof that identity gates are closed or that the dossiers are ready for Product Master approval.

**Next bounded actions**
1. Continue product-side read-only runtime audit for the actual seven existing Product records and their Evidence/ProductKnowledge readback. Record environment identity and only populated, source-traceable values; do not create or mutate records. The latest Issue #403 handoff explicitly notes that the other six records' Evidence/ProductKnowledge state had not yet been audited.
2. Resolve physical identity only when package/GTIN/market/INCI evidence is available. Do not block completion of other dossiers on the ISDIN package.
3. Request additional study documents only where a specific missing protocol would materially change a dossier; do not start an unbounded web search in this pass.
4. Keep all P-code dispositions as research-only. No P-code acceptance, supported relationship, Recommendation permission, Product Master/ProductKnowledge/Evidence/QA/lifecycle write, API/schema/DB/UI change, or G8 transition is authorized.

**Governance:** This is an append-only update to the existing seven-product research ledger on the existing PR #411 branch. No new Issue, PR, parallel ledger, product record or problem ID was created. PR #411 was not merged; PR #480 remains Draft/Open/Unmerged. G8 remains **BLOCKED / NOT VERIFIED**.


---

## Research pass 17 — conservative ingredient-role map reconciliation (2026-10-31)

**Input:** Product-by-product ingredient-role map supplied for review (compiled by Grok).  
**Purpose:** compare the proposed CORE / SUPPORT / CLAIM-LINK / RISK / TECH / UNKNOWN labels with the existing seven-product research ledger and normalize them without treating an unsourced ingredient list as a verified package INCI.

**Disposition:** this is an append-only research reconciliation. The supplied table did not include a source URL, source date, market, package image or lot for each ingredient row. Therefore, its additional ingredient names and exact formula groupings are retained as *candidate mapping input*, not as a replacement for the source-bound INCI snapshots already in this ledger. No Product Master, Evidence, ProductKnowledge, QA, lifecycle, database, API, schema, UI, recommendation or P-code relationship was changed.

### A. Role vocabulary — normalized meaning

| Label | Meaning used in this pass | What it does not mean |
|---|---|---|
| CORE | Ingredient/system central to the product's declared primary function (e.g. UV filters in sunscreen; surfactant system in a cleanser; a manufacturer-declared active percentage). | Not proof of clinical efficacy, universal suitability or a validated treatment indication. |
| SUPPORT | Ingredient with a plausible formulation/skin-conditioning role supported by ingredient identity and context. | Not proof that the finished product delivers a clinical outcome. |
| CLAIM-LINK | Ingredient or ingredient group explicitly connected to a manufacturer positioning/claim, or a candidate link that still needs source confirmation. | Not an independently verified mechanism or a supported Product↔Problem relationship. |
| RISK | A review flag for an ingredient/label feature that may matter in a specific sensitivity, exposure or use context. | Not a prediction that a particular user will react, and not automatically a contraindication. |
| TECH | Solvent, surfactant, emulsifier, rheology modifier, pH adjuster, chelator, preservative, film former or other formulation function. | Not a skin benefit or active claim. |
| UNKNOWN | Role, concentration, presence in the target market/version, or source correspondence is not established. | Not zero, absent, ineffective or safe by default. |

One ingredient may have more than one defensible role. Role assignment is context- and formula-dependent; INCI order alone does not establish a precise concentration, efficacy or safety ranking.

### B. Product-by-product reconciliation

| Product | Retained CORE | SUPPORT / CLAIM-LINK | TECH / RISK | Reconciliation and unresolved limits |
|---|---|---|---|---|
| **P1 COSRX The 6 Peptide Skin Booster** | No individual peptide is promoted to a proven efficacy CORE. The six-peptide cluster remains **CLAIM-LINK** because the manufacturer highlights the peptide complex. | Niacinamide and the listed humectant/NMF group remain SUPPORT candidates; allantoin/adenosine remain support candidates only where present on the source-matched INCI. | Glycols/water and the listed emulsifier, polymer, chelator and preservative groups are TECH. | Preserve the six named peptides as a manufacturer-highlighted cluster, not as six independently proven actives. Individual peptide percentages and the exact formula/physical 150 ml package match remain UNKNOWN. The submitted extended amino-acid/NMF list requires a source-matched INCI check before it is treated as complete. |
| **P2 Neutrogena Clear & Defend 2% SA Face Wash** | **Salicylic Acid 2%** remains CORE only as a manufacturer-declared concentration on the UK source page; the surfactant system is the CORE cleansing system. | Glycerin and panthenol are SUPPORT candidates. | Surfactants, viscosity/pH agents, chelator and preservative functions are TECH. Parfum is a conditional RISK flag. Benzalkonium chloride is recorded as a formulation ingredient; no extra antimicrobial benefit is inferred. | The UK source is not proof that the user's physical 200 ml unit is UK-market. Keep market, package, current INCI and GTIN unverified. Fragrance presence does not mean everyone will react. The manufacturer's n=34 / four-week “fewer new spots” statement remains a manufacturer claim, not a cure rate. |
| **P3 Garnier Vitamin C Brightening Gel Cleanser** | The surfactant system is CORE for cleansing. **Sodium Laureth Sulfate** is one member of that system, not the whole functional core. | Ascorbyl Glucoside and lemon extract are CLAIM-LINK to the brand's Vitamin C/brightening positioning; glycerin, panthenol and tocopheryl acetate are SUPPORT candidates. Salicylic Acid concentration remains UNKNOWN. | Surfactants and salt/thickener/pH/preservative ingredients are TECH. Parfum and listed fragrance allergens are conditional RISK flags. | Retain Ascorbyl Glucoside as a vitamin-C derivative; do not rename it L-ascorbic acid. It is a rinse-off cleanser, so leave-on vitamin-C evidence is not transferable. SLES presence alone does not establish that the formula is harsh or unsuitable for every user. Australia remains the source-page market, not confirmed physical-unit market. |
| **P4 SKIN1004 Hyalu-Cica Water-Fit Sun Serum** | International/Korean SPF50+ PA++++ UV-filter system remains CORE for UV protection, but only for that version. | Niacinamide, glycerin, hyaluronate forms and Centella are SUPPORT candidates. Botanical extracts may be CLAIM-LINK only where the exact manufacturer claim/source supports the link. | Emollients, silicones, emulsifiers, polymers, pH adjusters and preservatives are TECH. | Keep the international/Korean formula and the US SPF50 drug-label formula as separate dossiers. The US actives and declared percentages must not be imported into the international INCI. The submitted Centella ppm and HA ppm values remain UNKNOWN until tied to an exact official source and version. Neither botanical presence nor hydration claims establish treatment of pigmentation. |
| **P5 ISDIN FotoUltra 100 Active Unify SPF50+** | UV-filter system is CORE for sunscreen function, subject to exact market/label confirmation. | Niacinamide, Sclareolide and Pisum Sativum Extract remain CLAIM-LINK candidates for the manufacturer's Unify/spot-positioning claim; do not present the proposed mechanism as established. Glycerin and tocopherol derivatives may be SUPPORT where source-matched. | Solvents, emollients, silica, emulsifiers and stabilizers are TECH. | Existing ledger's primary claim source is the Mexico page; the submitted table describes an EU/IT formula. Do not merge them. The EU/IT INCI, Titanium Dioxide nano status, and any peptide pair reported on some lists require exact-version primary-source confirmation. Peptides are UNKNOWN for the target dossier until then. Existing Mexico manufacturer data (31 subjects; 22% spot-intensity and 15% spot-area reductions) remain manufacturer-reported, not independent proof. |
| **P6 Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter (historical 100 ml)** | No single ingredient is assigned a quantified CORE: concentrations are not publicly established in the reviewed historical dossier. The silicone base is a formulation platform, not a dark-spot active. | Ascorbyl Glucoside, Dimethoxytolyl Propylresorcinol and Acetyl Glucosamine remain CLAIM-LINK candidates to the historical dark-spot positioning. Botanical extracts and other listed ingredients remain SUPPORT/CLAIM-LINK candidates only when verified against the historical formula. | Silicones, volatile carriers, emulsifiers, pH agents, chelators and preservatives are TECH. Colorants are appearance TECH. Salicylic Acid concentration remains UNKNOWN. | Keep the discontinued historical product separate from the replacement/current Clinique serum. The supplied botanical “interrupter” grouping is not proof of a shared mechanism or efficacy. Do not import current formula ingredients or outcomes into the historical 100 ml record. |
| **P7 Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum** | **Azelaic Acid 10%** remains CORE as a manufacturer-declared concentration for the exact serum source. | Panthenol, allantoin, dipotassium glycyrrhizate, beta-glucan, centella components, glycerin, hyaluronate, squalane, ceramide NP, zinc PCA and niacinamide are SUPPORT candidates. Betaine Salicylate is recorded as a supporting ingredient; no independent exfoliation or acne outcome is inferred from its presence. | Solvents, pH adjusters, cellulose/polymer thickener and glucoside surfactant are TECH. | Keep the serum distinct from Anua's separate pads. The 10% declaration belongs to the serum source; regional formula variants and Disodium Azelate substitution/addition are not assumed without exact-label evidence. The supplied pH-sensitivity statement is not used to infer a formula defect or use rule. The brand's 90% agreement result remains a manufacturer claim with protocol limitations. |

### C. Corrections to prevent overstatement

1. **CORE is product-function-specific.** A cleanser's surfactant system can be CORE for cleansing without becoming an acne-treatment active. A sunscreen's UV filters are CORE for UV protection, not for treatment of existing pigmentation.
2. **CLAIM-LINK is not evidence of efficacy.** Ingredient presence, a brand's ingredient story and a finished-product outcome are three separate assertions.
3. **RISK is not a contraindication.** Fragrance/allergen presence is a review flag for context-sensitive assessment. It must not be automatically mapped to ProductKnowledge.contraindications; the existing warning/contraindication contract remains unresolved.
4. **TECH ingredients must not be marketed as skin benefits.** Solvents, surfactants, pH adjusters, chelators and preservatives primarily describe formula construction unless a separate supported claim exists.
5. **No percentage by INCI position.** Apart from manufacturer-declared values already source-attributed (P2 2%; P7 10%), concentrations remain UNKNOWN. INCI order does not provide an exact percentage.
6. **Version lock precedes formula comparison.** P2 UK source vs physical target, P3 Australia source vs physical target, P4 international vs US, P5 Mexico vs EU/IT, and P6 historical vs replacement must remain distinct.
7. **Ingredient-level literature is not finished-product evidence.** It cannot by itself establish a P-code relationship, customer suitability, consultation readiness or recommendation permission.

### D. Source and record-quality requirement for future enrichment

Before any candidate ingredient row is treated as source-verified, its research record must identify: exact product/version; market; source URL and source type (official label/official page/secondary); date accessed or label date; exact INCI spelling; declared concentration if explicitly stated; proposed role; reason/limitation; and whether the row is manufacturer claim, independent ingredient context, or analyst interpretation. Missing values remain UNKNOWN. This is a research documentation recommendation only, not a new schema or required Product Intake field.

### E. Net result

The submitted map adds useful role granularity to the existing pass-16 dossiers, especially the separation of cleansing systems, UV filters, declared actives, supporting ingredients and formulation technology. It does **not** establish that every ingredient in the supplied tables is present in the target physical package, nor does it establish efficacy or safety of the finished products. The source-bound identity, market/version and evidence limitations already recorded in passes 1–16 remain controlling.

**No ProductKnowledge approval, Product QA promotion, Product↔Problem relationship, Recommendation permission, G8 transition, or implementation authorization is created by this pass.**


---

## Research pass 18 — Product Owner review and ProductKnowledge persistence matrix (2026-10-31)

**Review basis:** pass 1–17 in this ledger; current Product Intake UI, Evidence model/service/API schema, ProductKnowledge model/service/response, and the explicit PO decision recorded in PR #411 comment 6468141807.

**Disposition:** research review and persistence mapping only. No Product Master, Evidence, ProductKnowledge, QA, lifecycle, database, API, schema, UI, Recommendation or Product↔Problem data was written.

### A. Product Owner review — accepted with evidence boundaries

The CORE / SUPPORT / CLAIM-LINK / RISK / TECH / UNKNOWN vocabulary is accepted as an **analyst-facing ingredient-role map**, with the following binding interpretation:

- CORE means central to the product's declared/formulation function, not clinically proven efficacy.
- SUPPORT means plausible formulation/skin-conditioning support, not a finished-product outcome.
- CLAIM-LINK means a manufacturer-positioning link or a candidate requiring source confirmation; it is not independent efficacy evidence.
- RISK is a context-sensitive review flag, not a contraindication or prediction of an individual reaction.
- TECH describes formula construction, not a skin benefit.
- UNKNOWN must remain visible and must not be converted to empty, absent, safe, zero concentration or ineffective.

**Product-specific disposition**

| Product dossier | Review decision | Conditions before any operational transfer |
|---|---|---|
| P1 COSRX 6 Peptide Booster, 150 ml | Accept the peptide cluster as CLAIM-LINK; niacinamide/humectant/NMF and soothing ingredients as SUPPORT candidates; base/emulsifier/preservative groups as TECH. | Confirm the target package/version and exact INCI. Keep individual peptide concentrations UNKNOWN. Do not convert peptide presence into a product efficacy or anti-age claim. |
| P2 Neutrogena Clear & Defend 2% SA Face Wash, 200 ml | Accept the surfactant system as cleansing CORE; the 2% SA as manufacturer-declared CORE for the UK source version; glycerin/panthenol as SUPPORT; fragrance as conditional RISK. | UK is a source market only; physical unit market, package INCI and warning text remain unverified. Keep 2% tied to the UK source. |
| P3 Garnier Vitamin C Brightening Gel Cleanser, 200 ml | Accept surfactant system as cleansing CORE; Ascorbyl Glucoside/lemon as CLAIM-LINK; glycerin/panthenol/tocopheryl acetate as SUPPORT; fragrance/allergens as conditional RISK. | Australia source does not prove target package market. Keep salicylic acid concentration UNKNOWN. Do not equate Ascorbyl Glucoside with pure L-ascorbic acid or transfer leave-on evidence to a rinse-off cleanser. |
| P4 SKIN1004 Hyalu-Cica Water-Fit Sun Serum | Accept UV filters as CORE only within the exact formula/market; niacinamide, humectants and Centella as SUPPORT candidates. | Maintain separate international/Korean and US dossiers. Do not merge active filters, percentages, ppm or INCI between them. |
| P5 ISDIN FotoUltra 100 Active Unify SPF50+ | Accept UV-filter system as sunscreen CORE; Unify ingredients as CLAIM-LINK candidates; other supported conditioning ingredients as SUPPORT; formula base as TECH. | Keep Mexico official claim data separate from EU/IT candidate INCI. Do not accept the EU/IT peptide pair, Titanium Dioxide nano status or other market-specific details without exact primary-source confirmation. |
| P6 Clinique Even Better Clinical Radical Dark Spot Corrector + Interrupter, historical 100 ml | Accept silicone base as TECH; named brightening ingredients as CLAIM-LINK candidates; botanical/conditioning ingredients as SUPPORT only where verified against the historical formula. | Preserve historical formula identity; do not import replacement formula facts. Concentrations remain UNKNOWN. |
| P7 Anua Azelaic Acid 10% + Hyaluron Redness Soothing Serum, 30 ml | Accept 10% azelaic acid as manufacturer-declared CORE for the exact serum source; humectant, soothing, Centella and barrier-supporting ingredients as SUPPORT; base/thickeners as TECH. | Keep serum distinct from pads. Verify market-specific label before transfer; do not infer pH defect, contraindication or finished-product efficacy from ingredient presence alone. |

This review accepts the **classification method and bounded interpretation**, not the unsourced completeness of every ingredient row. The pass-17 candidate additions remain subject to exact package/version INCI verification. No ingredient-level clinical efficacy, customer suitability or Product↔Problem relationship is accepted by this review.

### B. Existing persistence path — verified capabilities and blockers

| Data item | Existing source/persistence route | Decision |
|---|---|---|
| Product identity, market, size, packaging version | Product fields include `product_id`, `market_region`, `packaging_version`, size and GTIN. | Use only after DuplicateCheck and identity/version review. P1–P7 are research dossier labels, not proven Product.product_id values. Do not create or mutate Product records from these labels. |
| Source-bound INCI assertion | Evidence supports `claim`, `source_type`, `source_reference`, `claim_type`, `field`, `market_region`, `source_date`, `notes`, QA and conflict states. UI exposes `ingredients`. | Potentially reusable as a source-bound draft. One complete INCI assertion per exact Product/version/source is safer than one Evidence row per ingredient under the same field, because current conflict detection treats distinct claims on the same field as a conflict. |
| ProductKnowledge ingredient summary | `ProductKnowledge.ingredients`; Evidence-to-Knowledge rebuild maps field `ingredients` into this string. | Reusable only after explicit evidence review and exact version identity. Current aggregation splits comma-separated claims, deduplicates through a set, and does not preserve original INCI order or full source/version context in the summary. Evidence remains the provenance record. |
| CORE / SUPPORT / CLAIM-LINK / RISK / TECH role map | Backend rebuild recognizes `ingredient_roles` / `ingredient_role` and maps them to `ProductKnowledge.ingredient_roles`. The Product Intake UI research-field selector does **not** expose `ingredient_roles`. | **BLOCKED for current UI workflow.** Role labels are analyst INFERENCE, not FACT or MANUFACTURER_CLAIM. Do not route them into `claimed_benefits`, `manufacturer_claims` or `contraindications`. A future approved workflow must preserve ingredient-to-role pairing and source/version context. |
| Manufacturer's declared concentration / formula / performance statement | UI/API supports `manufacturer_claims` and `MANUFACTURER_CLAIM`; ProductKnowledge maps only explicitly typed manufacturer claims to `manufacturer_claims`. | Reusable as a source-attributed manufacturer claim, not as independently verified efficacy. Keep exact market/version and quoted metric/protocol limitation in the Evidence row. |
| Claimed finished-product benefits | Existing `claimed_benefits` mapping exists; UI exposes it. | Use only for an actual source-bound product benefit claim. Ingredient-role labels and inferred mechanisms must not be stored here. |
| Known use cases | Existing `known_use_cases` mapping exists; UI exposes it. | Use only for explicit, source-bound use cases. Do not translate P-codes or ingredient presence into use cases. |
| Contraindications / warnings | Existing `contraindications` mapping exists; UI exposes it. | Use only for explicit label warnings or reviewed contraindications. RISK tags for fragrance/allergens are not automatic contraindications. |
| Usage instructions | Existing `usage_instructions` mapping exists; UI exposes it. | Use only from exact package/source directions. Do not borrow directions across market/version or similar products. |
| TECH and UNKNOWN | No dedicated ProductKnowledge destination for TECH or unknown concentrations/roles. | Keep in the research ledger and source-bound Evidence notes until a safe approved representation exists. Never write UNKNOWN as empty or as an affirmative ProductKnowledge fact. |
| Universal “Other features” box | PO decision requires it for all seven products, but the current Evidence UI field selector has no general/other-features destination. | **BLOCKED for current UI workflow.** Do not misroute into benefits/use cases. Existing API `field` is nullable/free text, but an arbitrary field is not a supported ProductKnowledge mapping. |

### C. Cross-cutting technical findings that prevent unsafe bulk transfer

1. **Dossier IDs are not product IDs.** P1–P7 in this ledger are research labels. Each must be matched to an existing, exact Product Master record before Evidence can be attached.
2. **Version isolation is not enforced by ProductKnowledge rebuild.** Evidence has `market_region`, but the rebuild queries all Evidence by `product_id` and does not filter by market/version. Evidence has no dedicated `packaging_version` column. Different market formulas attached to one product_id could therefore be combined into one ProductKnowledge profile. Do not attach distinct formula versions to one product_id.
3. **Evidence conflict detection is field-wide.** Multiple distinct claims sharing the same `field` for one product are marked CONFLICT, even where they might represent separate ingredients or separate versions. Do not create one Evidence row per ingredient using the same field under the current behavior.
4. **Role mapping is not exposed in the current intake UI.** The backend understands `ingredient_roles`, but the UI dropdown omits it. No UI or schema change is authorized by this review.
5. **Evidence QA is not scientific truth certification.** The UI itself states VERIFIED means the review result was recorded; it does not guarantee scientific truth or safety. Manufacturer claims, independent evidence and analyst inference must remain distinguished.
6. **Confidence aggregation is not a product efficacy score.** The current rebuild averages `evidence_strength` across all QA-approved rows without separating claim types or product/version applicability. Do not interpret `knowledge_confidence` as clinical confidence or product effectiveness.
7. **Evidence status reset needs a contract decision.** The current PR branch adds `evidence_status=None` on every rebuild. The ProductKnowledge model allows NULL and the enum includes UNKNOWN, but the current code does not derive a status from the rebuilt evidence set. This should be reviewed against the EMPTY-vs-UNKNOWN contract before merge; this review does not authorize a code change.

### D. Approved data-transfer rule for the seven dossiers

- **Now:** retain the pass-17/18 research map in the ledger. Do not bulk-seed Evidence or ProductKnowledge.
- **After identity/version match:** create source-bound Evidence drafts only for assertions with exact source, market/version and clear claim type. They must remain PENDING/UNKNOWN until a human reviewer checks the source and scope.
- **After human verification:** only supported existing fields may flow through the current rebuild. Do not treat VERIFIED as a Product QA verdict or lifecycle approval.
- **For role labels and Other features:** keep them in the ledger until an approved, tested persistence route exists. No silent remapping to benefits, claims, contraindications or use cases.
- **For formula variants:** use separate, verified Product identities if the catalog supports them; otherwise stop and request a version-isolation decision before attaching Evidence.

### E. Decision and handoff

**Product Owner review:** PASS WITH LIMITATIONS for the role taxonomy and product-specific interpretation; NOT VERIFIED for exhaustive package-level INCI completeness and physical-unit/version matching.

**ProductKnowledge integration readiness:** PARTIAL. Existing Evidence → ProductKnowledge path can safely carry some source-bound fields, but role mapping and Other features are not fully supported by the current UI, and product/version aggregation plus field-wide conflict detection prevent safe bulk ingredient-level transfer.

**Implementation status:** no code/schema/API/UI/database changes authorized or made by this pass. Next allowed step is to prepare a minimal, separately reviewed work package for the blockers in sections B–C, after product identity matching. Do not merge PR #411 based only on this research review.
