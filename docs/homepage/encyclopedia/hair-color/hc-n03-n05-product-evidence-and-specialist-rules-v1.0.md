# HBI Hair Consultation — HC-N03 to HC-N05 Product Evidence and Specialist Rules v1.0

- **Status:** evidence audit and rule/oracle specification; no product-specific chemistry or execution rule is active.
- **Work items:** HC-N03 Bijourka evidence; HC-N04 Magic Color evidence; HC-N05 specialist rule catalogue and synthetic oracle cases.
- **Depends on:** HC-N01/N02 logical contract and case model proposal in stacked PR #575.
- **Data policy:** synthetic-only; no real customer records, photos, or case data in any environment.
- **Critical distinction:** a source may support a bounded claim without being sufficient to activate a hair-colour recommendation rule. Product identity, formula, safety, application instructions, and colour outcome are separate claim domains.

## 1. Executive conclusion

Package B can establish the evidence policy, general scientific/safety rules, product-specific evidence dossiers, and synthetic validation oracles. It cannot honestly mark either brand's chemistry as verified today.

**Current findings:**
1. Bijourka's 88-row HBI catalogue artifact is a retailer-derived identity snapshot. Its SHA-256 identifies the repository artifact, not an authenticated manufacturer edition or formula.
2. A secondary business directory attributes Bijourka to Emad Ara, and a Telegram channel bearing the Emad Ara name contains Bijourka promotional material. The channel's ownership/authenticity has not been independently established; the business directory is not the manufacturer.
3. No official Bijourka manufacturer catalogue, current INCI list, product-specific instruction sheet, Safety Data Sheet, formula revision, or market-specific technical dossier was retrieved in this audit.
4. “Magic Color” is not uniquely identified by publicly discoverable material. Search results include unrelated products and similarly named brands. An Iranian retail listing for a “Magic” colour line is not enough to prove it is the exact Magic Color intended by HBI.
5. General regulator/scientific sources support bounded rules about oxidative vs non-oxidative dye classes, sensitization/allergy, label directions, and hair-fibre damage. They do not validate Bijourka or Magic Color formulas.

**Result:** no Bijourka or Magic Color formula, developer pairing, mixing ratio, processing time, shade outcome, safety profile, or product-specific recommendation rule may be activated from the evidence currently available.

## 2. Evidence classification and activation policy

### 2.1 Source classes

| Source class | Examples | What it may support | What it cannot establish alone |
|---|---|---|---|
| REGULATOR_PRIMARY | FDA, EU Cosmetics Regulation, national competent authority records | Regulatory statements within the authority's jurisdiction and scope | Product formula, product identity, or legality in another market |
| SCIENTIFIC_PRIMARY | SCCS final opinions, peer-reviewed studies | Substance- or mechanism-specific scientific claims within the studied conditions | Whole-product safety or equivalence across brands |
| MANUFACTURER_PRIMARY | Official current catalogue, exact label/INCI, product instruction leaflet, signed technical dossier | Exact product identity, declared ingredients, intended use and instructions within the identified version/market | Independent proof of every marketing or performance claim |
| MANUFACTURER_AUTHENTICATED_CHANNEL | Officially linked company account/document repository | Product notices or documents when account ownership and provenance are established | Formula equivalence across revisions or markets without exact records |
| SECONDARY_BUSINESS_DIRECTORY | Company directory, distributor listing | Leads for manufacturer identity and contact discovery | Manufacturer-level verification |
| RETAILER_CATALOGUE | Retail product page, retailer album | Retailer-listed name, code, package size, advertised description at capture time | Official catalogue completeness, formula, safety, exact instructions, or publisher authenticity |
| SOCIAL_OR_USER_GENERATED | Social posts, comments, stylist/client anecdotes | Case-specific leads requiring review | Generalizable technical or safety rules |
| HBI_REPOSITORY_ARTIFACT | HBI CSV/JSON snapshot and digest | Integrity of the captured HBI artifact | Publisher authenticity, official edition, or truth of source claims |

### 2.2 Evidence statuses

Use these exact conceptual statuses:
- DISCOVERED: source/claim located but not assessed.
- IDENTITY_UNCONFIRMED: source or product identity cannot be reliably tied to the claimed publisher/product.
- SECONDARY_ONLY: only secondary evidence is available.
- CAPTURED_UNVERIFIED: HBI captured an artifact but publisher provenance is not authenticated.
- VERIFIED_SOURCE: source identity and integrity verified, but applicability to the specific claim not established.
- VERIFIED_APPLICABLE: source identity, exact subject/product/version/market, claim scope, and conditions reviewed and accepted for that claim.
- CONFLICTED: credible sources disagree.
- SUPERSEDED: newer/corrected source replaces this source for the same scope.
- REJECTED: source/claim unsuitable or false for the stated scope.

Only VERIFIED_APPLICABLE can support activation of a rule, and only for the exact scope it covers. VERIFIED_SOURCE is not automatically a verified claim.

### 2.3 Claim taxonomy

Each claim must be stored independently:
- PRODUCT_IDENTITY: brand owner, manufacturer, product line, exact SKU/shade code, package size, market, version/edition, batch/lot where relevant.
- CATALOG_IDENTITY: listed series, shade code, shade name, product description, package size.
- INGREDIENT_DECLARATION: exact INCI or other legally applicable ingredient declaration from the identified package/version.
- CHEMICAL_CLASS: oxidative/non-oxidative, permanent/semi-permanent/temporary, only when supported by exact product documentation.
- SAFETY_AND_WARNINGS: warnings, contraindications, sensitization statements, intended-use restrictions, test requirements.
- APPLICATION_INSTRUCTIONS: product-specific directions and limits. These are never inferred or generated by HBI.
- PERFORMANCE_CLAIM: coverage, durability, lift, tone, gray coverage, conditioning, or other measurable performance.
- MARKETING_CLAIM: gold, keratin, argan, “repair”, “anti-damage”, “low ammonia”, and similar promotional wording.
- SCIENTIFIC_CLAIM: bounded proposition supported by scientific/regulatory evidence.
- SPECIALIST_RULE: reviewed decision rule with scope, preconditions, exclusions, source chain, version, and oracle cases.

## 3. Product dossier — Bijourka (HC-N03)

### 3.1 Known repository artifact

HBI currently holds:
- CSV: docs/homepage/encyclopedia/hair-color/catalog/raeaka_bijourka_catalog.csv
- Snapshot: docs/homepage/encyclopedia/hair-color/catalog/raeaka_bijourka_snapshot.json
- Source URL: https://raeaka.com/آلبوم-رنگ-مو-بیجورکا/
- Capture timestamp: 2026-11-10T18:57:00Z
- Expected rows/columns: 88 / 6
- Snapshot ID: hbi-hair-catalog-snapshot-20261110-185700z
- Ingestion ID: hbi-hair-catalog-ingestion-20261110-185700z-01
- Artifact SHA-256: 1887a7d166164639e2c235a7144fe6b27b4861f5c36fac9af383bef14eec1212
- publisher_edition, publisher_revision, and publisher_captured_at are null.

**Interpretation:** this is an HBI-registered snapshot of a retailer album. The digest establishes integrity of the captured repository artifact only. It does not establish that the publisher is the manufacturer, that the listing is complete/current, or that rows are chemically equivalent to current packages.

### 3.2 Public source audit

| Source | What was found | Class / status | Permitted use |
|---|---|---|---|
| Raeaka Bijourka album | Retailer album with shade rows and product descriptions | RETAILER_CATALOGUE / CAPTURED_UNVERIFIED | Historical secondary identity snapshot only |
| Technolife Bijourka brand page | Retail listing with 101 displayed items and variants | RETAILER_CATALOGUE / SECONDARY_ONLY | Discovery/cross-check leads; not official catalogue completeness |
| Technolife product pages | Examples include BI1/BI8, 100 ml, and a repeated licence-number field | RETAILER_CATALOGUE / SECONDARY_ONLY | Record exact retailer assertion; not product identity or proof of authenticity |
| Iranmadex Emad Ara directory | Attributes Bijourka among brands marketed by Emad Ara | SECONDARY_BUSINESS_DIRECTORY / SECONDARY_ONLY | Manufacturer-identity lead only |
| Telegram @EmadAraProducts | Channel titled “محصولات شرکت عمادآرا”; posts include Bijourka media and a Bijourka hair-colour video | SOCIAL_OR_USER_GENERATED until ownership authenticated | Lead for original documents; not official by name alone |
| Emad Ara website | Previously inaccessible to the audit (403); no official Bijourka technical dossier retrieved | MANUFACTURER_PRIMARY not obtained | No product claim supported from unavailable site |
| Retailer/distributor marketing pages | Claims include 24K gold, argan, keratin, low ammonia, coverage, durability, and biological/therapeutic effects | MARKETING_CLAIM / SECONDARY_ONLY | Do not activate; health/therapeutic claims excluded absent appropriate evidence |

### 3.3 Bijourka claim disposition

| Claim family | Current status | Rule |
|---|---|---|
| Manufacturer attribution to Emad Ara | SECONDARY_ONLY | Do not mark verified until an official company source/authenticated manufacturer document confirms it |
| 88-row shade catalogue | CAPTURED_UNVERIFIED | Identity-only, retailer-derived; no chemical or operational use |
| Shade code/name/series and package size | SECONDARY_ONLY | May be stored as retailer-listed values with source/capture date; not official |
| Exact INCI/formula | MISSING | No ingredient-level rule |
| Product type and oxidative/non-oxidative class | MISSING | Do not infer |
| Developer compatibility / product instructions | MISSING | No product-specific execution instruction |
| Allergy/safety warnings and test instructions | MISSING | No product-specific safety clearance |
| Gray coverage, lift, durability, final tone | UNVERIFIED | No performance promise or deterministic prediction |
| Gold/keratin/argan/low-ammonia/repair claims | SECONDARY_ONLY | Marketing claims, not scientific or product-performance evidence |

### 3.4 Bijourka ingestion gate

To move Bijourka beyond identity-only, the source package must contain:
1. Official current manufacturer catalogue or a document whose publisher identity can be authenticated.
2. Exact product/package identity and market (brand, product line, shade code, package size, legal manufacturer/responsible entity, and any registration/notification identifier).
3. Current package ingredient declaration (INCI) for the exact product family/version.
4. Product-specific instructions and warnings from the exact package/leaflet.
5. Technical dossier or Safety Data Sheet when relevant to a claim being assessed.
6. Revision/effective date and a method to distinguish old/new formulations and market variants.
7. Source capture metadata and file digest; publisher version/revision remains distinct from the HBI artifact digest.

A catalogue is not an INCI list; an INCI list is not an application instruction; a retailer code is not a formula identifier.

## 4. Product dossier — Magic Color (HC-N04)

### 4.1 Identity ambiguity

Public searches for “Magic Color” return multiple unrelated products and companies. Examples include:
- A product page for “Magic Color” by Nicka K / Hair & Beauty Corp, a foreign boxed permanent colour system.
- A German Safety Data Sheet titled “MAGIC COLOR COLORATIONSCREME”, reference 17101–17155, for a separate oxidation hair-colour cream.
- Iranian retailer pages using “مجیک” / “مجیکالر” for 100 ml colour lines and marketing ingredient/mixing claims, without enough primary evidence to tie the listing to the exact HBI-intended manufacturer and product.

These are homonyms, not proof of shared brand ownership, formulation, or product family. The foreign product page and German SDS are excluded from HBI Magic Color evidence unless exact package identity later proves they are the same product—which has not been established.

### 4.2 Current disposition

| Claim family | Current status | Rule |
|---|---|---|
| Exact brand owner/manufacturer | IDENTITY_UNCONFIRMED | No product dossier against a guessed manufacturer |
| Iranian “مجیک” retail product family | SECONDARY_ONLY | Lead only; do not equate with HBI Magic Color |
| Exact SKU/shade list | MISSING | No shade identity mapping |
| Exact INCI/formula | MISSING | No ingredient-level rule |
| Product type / oxidation class | MISSING | Do not infer |
| Product instructions | MISSING | No execution instructions |
| Safety warnings/test instructions | MISSING | No product-specific safety clearance |
| Performance and conditioning claims | SECONDARY_ONLY | Do not activate |

### 4.3 Magic Color identity gate

Before any Magic Color product is ingested, establish:
- Exact Latin/Persian brand spelling and logo.
- Legal manufacturer or responsible company shown on package.
- Product-line name and exact shade code.
- Package size and market.
- Barcode/registration or notification identifier if present (cross-reference only, not proof by itself).
- Front/back package panels and official catalogue/leaflet.
- Product class based on exact documentation.

Until this identity gate passes, all Magic Color-specific claims remain withheld.

## 5. General scientific and regulatory knowledge — bounded claims only

These sources support general rules. They do not prove either HBI brand's formulation or safety.

### 5.1 Hair-colour product classes

The European Commission describes temporary and semi-permanent dyes as non-oxidative and permanent dyes as including oxidative systems. In oxidative systems, colour is produced from precursors and couplers in the presence of hydrogen peroxide. This is a general product-class explanation, not an assertion that a particular Bijourka or Magic Color item uses that chemistry.

**Rule KB-HC-001 — classify only from exact product evidence**
- Input: exact package/official documentation and market/version.
- Output: product class with source reference and verification status.
- Stop: if exact documentation does not establish the class, return KNOWLEDGE_GAP.
- Forbidden: infer class from shade code, retailer category, marketing term, or brand reputation.

### 5.2 Sensitization and allergy

FDA states that sensitization can develop after repeated exposure and that a person may react despite previous uneventful use. FDA also states that a negative skin test does not guarantee that a reaction will not occur during use. Product instructions and warnings must be followed; different dye products should not be mixed. Previous tolerance of another product does not establish safety of the current product.

**Rule KB-HC-002 — previous tolerance is not future safety proof**
- Prior uneventful use cannot prove future non-reactivity.
- Exact product instructions and any known reaction history must be considered.
- A reported prior reaction or relevant warning triggers a safety stop/appropriate professional-health referral; the engine must not override it.
- A negative test result must not be represented as a guarantee of safety.
- Never infer an allergen profile from a different shade, brand, or historical formulation.

**Rule KB-HC-003 — exact product instructions govern safety steps**
- Use only exact manufacturer's current instructions for the exact product/market/version.
- HBI must not invent, shorten, replace, or generalize a manufacturer's test instructions.
- If exact instructions are unavailable or product identity is unresolved, withhold product-specific guidance and return a knowledge gap.
- The system must not advise mixing different dye products.

### 5.3 Ingredient-specific opinions

SCCS opinions evaluate named substances, specified product types, concentrations, and conditions based on submitted dossiers. The SCCS opinion on HC Red 18 (SCCS/1673/24) is tied to that named substance and specified use conditions; the opinion on HC Yellow 16 (SCCS/1670/24) likewise has its own named substance and conditions. These opinions do not approve a whole commercial product or brand.

**Rule KB-HC-004 — substance opinion is not whole-product approval**
- Match exact INCI/substance identity (including relevant salt/form), CAS/EC identifiers where available, concentration, product type, exposure conditions, market, and current regulatory status.
- If one or more are unknown, the opinion cannot be used to declare the product safe.
- Never transfer an opinion from one dye intermediate to another or from one product to every shade in a brand.
- Regulatory scope must be explicit: an EU restriction/opinion is not an automatic statement of Iranian market authorization.

### 5.4 Hair-fibre damage and lightening

The American Academy of Dermatology notes that colouring/perming treatments can make hair dry and brittle and that lightening more than three shades generally requires higher peroxide volumes and can cause more damage. This is general dermatological guidance, not a numerical formula engine or deterministic prediction for an individual head of hair.

**Rule KB-HC-005 — damage risk is a constraint, not a shade formula**
- The system may communicate that more extensive lightening generally increases damage risk.
- It must not predict exact damage, breakage, or final colour from one photograph or shade number.
- Hair history, prior chemical services, current condition, regional variation, and professional assessment remain relevant.
- If material uncertainty or substantial damage risk cannot be resolved, withhold an execution suggestion and identify the missing assessment.

### 5.5 Image limitations

The approved HBI README states that an image alone cannot establish chemical history, internal pigment, porosity, elasticity, or material compatibility.

**Rule KB-HC-006 — image is supporting observation only**
- An image may support bounded visible observations such as apparent colour distribution or visible banding, with lighting/camera limitations.
- It cannot establish chemical history, internal pigment, porosity, elasticity, compatibility, or product chemistry.
- Never convert a visual guess into a KNOWN fact.
- If a recommendation depends on hidden hair properties, request a valid assessment or stop.

## 6. Specialist rule catalogue — implementation-neutral, non-active

The following rule IDs are stable documentation identifiers for review and test traceability. They are not runtime enums and none is active for product-specific execution recommendations.

| Rule ID | Rule title | Current status | Hard-stop / expected behavior |
|---|---|---|---|
| KB-HC-001 | Exact product-class identification | GENERAL_RULE_REVIEWED | Unknown class → KNOWLEDGE_GAP; no inference |
| KB-HC-002 | Prior tolerance is not future safety proof | GENERAL_RULE_REVIEWED | Relevant reaction history → safety stop / appropriate referral |
| KB-HC-003 | Exact product instructions govern safety steps | GENERAL_RULE_REVIEWED | Missing exact instructions → withhold product-specific directions |
| KB-HC-004 | Substance-specific SCCS opinion scope | GENERAL_RULE_REVIEWED | Mismatched substance/conditions → no safety inference |
| KB-HC-005 | Lightening/damage risk constraint | GENERAL_RULE_REVIEWED | Material unknown/damage risk → no unsupported execution suggestion |
| KB-HC-006 | Image limitation | GENERAL_RULE_REVIEWED | Hidden facts cannot be promoted from image-only input |
| KB-HC-007 | Exact brand/SKU/market/version identity | IMPLEMENTATION_REQUIRED | Ambiguous identity → KNOWLEDGE_GAP |
| KB-HC-008 | Formula revision invalidation | IMPLEMENTATION_REQUIRED | Changed formula/version invalidates dependent claims/rules/options |
| KB-HC-009 | Cross-brand shade-code non-equivalence | GENERAL_RULE_REVIEWED | No mapping by number similarity; require verified equivalence evidence |
| KB-HC-010 | Manufacturer-vs-retailer source hierarchy | IMPLEMENTATION_REQUIRED | Retailer claim cannot be promoted to manufacturer fact |
| KB-HC-011 | Marketing-vs-scientific claim separation | GENERAL_RULE_REVIEWED | Marketing claim cannot support safety, repair, or clinical benefit |
| KB-HC-012 | No unsupported colour-outcome guarantee | GENERAL_RULE_REVIEWED | Swatch/photo/shade code alone cannot guarantee result |
| KB-HC-013 | Conflicting product documents | IMPLEMENTATION_REQUIRED | Material conflict → withhold dependent output pending resolution |
| KB-HC-014 | No chemical execution instruction without exact product dossier | GENERAL_RULE_REVIEWED | Missing official directions/validated rules → no ratio/developer/time/formula output |
| KB-HC-015 | Specialist oracle traceability | IMPLEMENTATION_REQUIRED | Every accepted rule needs version-bound oracle cases and rationale |

**Activation policy:** GENERAL_RULE_REVIEWED means the bounded general principle is supported by the cited public source and ready for specialist review. It does not mean executable in the hair-colour engine. Product-specific rules require exact primary product evidence plus specialist validation and oracle coverage.

## 7. HC-N05 synthetic oracle set

All fixtures must use clearly synthetic identifiers and contain no real customer details, images, or case history. These are behavioral oracles, not evidence that an actual product is safe or effective.

| Oracle | Synthetic setup | Required result | Forbidden behavior |
|---|---|---|---|
| HC-O01 | Exact product label, market, SKU and version resolve to one manufacturer document | Identity may be verified within that scope | Generalize to other shades/markets |
| HC-O02 | Retailer catalogue conflicts with manufacturer catalogue | Prefer verified current manufacturer evidence for its exact scope; record conflict | Silently select retailer claim |
| HC-O03 | Brand known but manufacturer and formula revision unknown | KNOWLEDGE_GAP; no product-specific recommendation | Infer from brand name |
| HC-O04 | Two brands use same shade number without equivalence evidence | Treat as distinct products | Map by numeric shade code |
| HC-O05 | Previous uneventful use but current sensitization concern exists | Prior tolerance is not a safety guarantee | Return “safe because used before” |
| HC-O06 | Synthetic negative test result with exact label caveat | Explain that a negative result is not a guarantee; follow exact product instructions | Promise no reaction |
| HC-O07 | Image-only case asks for chemical history or porosity | Mark facts unknown; request valid assessment | Infer hidden properties from image |
| HC-O08 | Exact INCI unavailable; asks whether formula is ammonia-free or contains PPD | KNOWLEDGE_GAP; no ingredient claim | Use retailer marketing or another shade's label |
| HC-O09 | SCCS opinion for named ingredient but product INCI unknown | No whole-product safety conclusion | Treat ingredient opinion as brand approval |
| HC-O10 | Formula revision differs from version behind an earlier rule | Invalidate dependent outputs and require fresh review | Carry old rule approval forward |
| HC-O11 | Target requires substantial lightening but hair history/condition is unreliable | Withhold execution recommendation; state uncertainty/damage constraint | Guarantee shade or damage outcome |
| HC-O12 | No valid option remains under documented constraints | Zero options and actual supported reason | Invent a substitute or mislabel as out-of-scope |
| HC-O13 | Product leaflet missing or belongs to another market/version | KNOWLEDGE_GAP; withhold product-specific guidance | Borrow directions from similar product |
| HC-O14 | Product claim says “keratin repair / gold / low ammonia” without primary evidence | Store only as unverified marketing claim | Treat as proven repair/safety/chemical property |
| HC-O15 | Question after rejecting exact suggestion version | Answer without reactivating rejected suggestion | Re-display rejected version as active |

### Oracle acceptance requirements

Each oracle record must include:
- synthetic fixture ID and scenario ID;
- exact claim/rule under test;
- source references and their status;
- case/target/rule/product version context;
- expected engine state, consultation response state (or explicitly non-consultation event), reason code, and option count;
- exact forbidden behavior;
- dependency and invalidation expectation;
- test owner/reviewer and review date;
- note that synthetic success is not scientific product validation.

No numeric confidence score or quality threshold is introduced without a defined measurement method and specialist agreement.

## 8. Product-knowledge registry record shape

A product dossier must be versioned and claim-oriented.

| Field | Purpose |
|---|---|
| product_identity_ref | HBI opaque identity reference |
| brand, manufacturer, product_line | Separate brand owner and legal manufacturer when known |
| sku_or_shade_code, shade_name, package_size | Exact marketed identity |
| market_region | Market to which label/document applies |
| package_revision, formula_revision, effective_date | Distinguish formula and label versions |
| batch_or_lot | Optional traceability for a specific package |
| source_refs[] | Immutable source references and digests |
| claims[] | Bounded claim text, claim type, scope and status |
| ingredient_declaration_ref | Exact package/INCI evidence or null |
| instructions_ref | Exact instructions/warnings or null |
| regulatory_refs[] | Market-specific regulatory references |
| review_status | Explicit evidence status |
| reviewer_ref, reviewed_at | Review traceability |
| supersedes_product_version_ref | Explicit version lineage |
| dependency_refs[] | Rules and outputs depending on this dossier |

Never overwrite a formula revision. Append a new revision and invalidate only dependent claims/rules/options; if dependency impact is unknown, withhold the affected output.

## 9. Source register — public sources reviewed 2026-11-15

1. **European Commission — Hair dye products**  
   https://single-market-economy.ec.europa.eu/sectors/cosmetics/cosmetic-products-specific-topics/hair-dye-products_en  
   Supports general distinction between temporary/semi-permanent non-oxidative dyes and permanent oxidative dyes, and the general precursor/coupler + hydrogen peroxide mechanism. Not product-specific.

2. **U.S. FDA — Cosmetics Safety Q&A: Hair Dyes**  
   https://www.fda.gov/cosmetics/resources-consumers-cosmetics/cosmetics-safety-qa-hair-dyes  
   Supports following exact package instructions, repeated testing according to label, not mixing different dye products, and other bounded safety precautions.

3. **U.S. FDA — Hair Dyes**  
   https://www.fda.gov/cosmetics/cosmetic-products/hair-dyes  
   Supports possibility of sensitization after repeated exposure and reactions despite prior uneventful use; even a negative skin test does not guarantee no reaction.

4. **American Academy of Dermatology — Coloring and perming tips for healthier-looking hair**  
   https://www.aad.org/public/everyday-care/hair-scalp-care/hair/coloring-perming-tips  
   Supports general dryness/brittleness and greater damage risk with more extensive lightening. Not an individual result prediction.

5. **European Commission SCCS — Opinions index**  
   https://health.ec.europa.eu/scientific-committees/scientific-committee-consumer-safety-sccs/sccs-opinions_en  
   Shows SCCS opinions are based on specific dossiers and scoped substances/conditions.

6. **SCCS — Scientific Advice on HC Red No. 18 (SCCS/1673/24)**  
   https://health.ec.europa.eu/publications/sccs-scientific-advice-hc-red-no-18-colipa-no-b124-cas-no-1444596-49-9-submission-ii_en  
   Substance-specific opinion; cannot be generalized to a brand or unrelated ingredient.

7. **SCCS — Scientific Advice on HC Yellow No. 16 (SCCS/1670/24)**  
   https://health.ec.europa.eu/publications/sccs-scientific-advice-hc-yellow-no-16-colipa-no-b123-cas-no-1184721-10-5-submission-ii_en  
   Substance-specific example; applicability restricted to exact substance and stated conditions.

8. **European Commission Regulation (EC) No 1223/2009**  
   https://eur-lex.europa.eu/eli/reg/2009/1223/oj/eng  
   Primary EU cosmetics regulation. Regulatory conclusions limited to the EU market and current consolidated text/annexes.

9. **NHS — Hair dye reactions**  
   https://www.nhs.uk/conditions/hair-dye-reactions/  
   Supports high-level awareness of delayed reactions and PPD-related allergy risk. Health-service guidance, not a product dossier.

10. **Iranmadex — Emad Ara manufacturer directory**  
    https://iranmadex.com/fa/manufacturers/عماد-ارا  
    Secondary business directory; lead only for Bijourka manufacturer identity.

11. **Telegram — Emad Ara Products channel**  
    https://t.me/s/EmadAraProducts  
    Public channel with Bijourka promotional media; ownership/authenticity not independently verified.

12. **Technolife — Bijourka brand listing**  
    https://www.technolife.com/brand/bijourka  
    Retailer listing; secondary identity/catalogue discovery only.

13. **HBI current Bijourka snapshot source**  
    https://raeaka.com/آلبوم-رنگ-مو-بیجورکا/  
    Retailer catalogue source for the 88-row HBI identity snapshot; not manufacturer-primary.

14. **NDBinahayat — Iranian “Magic” product listing**  
    https://ndbinahayat.com/product/رنگ-مو-مجیک-سری-طلایی-5-3-قهوه-ای-طلایی-روش/  
    Retailer/distributor listing. Does not establish this is the HBI-intended Magic Color brand or authenticate formula/instructions.

15. **Hair & Beauty Corp — Magic Color by Nicka K**  
    https://hairandbeautycorp.com/products/magic-color  
    Foreign product page; treated as potentially unrelated homonym until exact package identity proves otherwise.

16. **German SDS — MAGIC COLOR COLORATIONSCREME**  
    https://www.friseurversand.com/media/7f/40/2d/1752664154/26023-3.pdf  
    SDS for named product/reference 17101–17155; not linked to HBI Magic Color identity and excluded from HBI product rules.

## 10. Package B exit criteria

HC-N03 Bijourka can advance beyond identity-only when:
- [ ] Official manufacturer identity and current catalogue are authenticated.
- [ ] Exact product/shade/market/version records are captured.
- [ ] Exact package INCI and current instructions are available for each product family in scope.
- [ ] Product-specific warnings and applicable regulatory references are resolved.
- [ ] Every claim has bounded source, scope, status, and reviewer traceability.
- [ ] Formula/label revisions and dependency invalidation are tested.

HC-N04 Magic Color can advance from identity-unconfirmed when:
- [ ] Exact intended brand and manufacturer are identified from package or authenticated manufacturer source.
- [ ] Foreign and similarly named products are disambiguated.
- [ ] Exact catalogue, product identity, INCI, warnings, and instructions are captured.
- [ ] Claims and rules meet the same evidence standard as Bijourka.

HC-N05 can advance when:
- [ ] General rules KB-HC-001 through KB-HC-006 have specialist review.
- [ ] Product-specific rules remain disabled until product dossiers pass.
- [ ] All 15 synthetic oracles are encoded and tested.
- [ ] Every oracle traces to exact claims, rules, versions, dependencies, and forbidden behavior.
- [ ] No unsupported chemical instruction, deterministic colour guarantee, or cross-brand shade equivalence is emitted.

## 11. Explicit non-authorization and limits

This package does not:
- approve any Bijourka or Magic Color formula, shade, developer, mixing ratio, timing, or application instruction;
- activate a chemical or product-specific rule;
- establish product safety from a brand name, retailer page, licence number, or marketing claim;
- establish Iranian regulatory approval from an EU/FDA source;
- permit real customer data, images, or case histories;
- authorize a production database, pilot, deployment, release, or PR merge;
- claim synthetic oracle success is specialist or scientific validation.

**Current result:** general evidence-backed safety and scientific principles are documented for review; both brand-specific product dossiers remain blocked by primary source identity/document gaps.
