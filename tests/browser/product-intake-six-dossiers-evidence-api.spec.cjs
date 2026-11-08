const { test, expect } = require("@playwright/test");

// Follow-up to the approved Anua pilot: source-bound manufacturer assertions for P1-P6.
// All writes run only against the disposable pilot API configured for this workflow.
const PRODUCTS = [
  {
    dossier: "P1 COSRX",
    productId: "HBI-PROD-FE320FA135B843B6",
    source: "https://www.cosrx.com/collections/all/products/the-6-peptide-skin-booster-serum",
    marketRegion: undefined,
    claim: "The manufacturer presents The 6 Peptide Skin Booster as a peptide-oriented skin booster and reports cosmetic moisture and texture outcomes. The full study protocol and physical 150 ml package/formula match are not verified in the dossier.",
  },
  {
    dossier: "P2 Neutrogena",
    productId: "HBI-PROD-2CC249240D504453",
    source: "https://www.neutrogena.co.uk/skincare/cleansers-washes/clear-and-defend-daily-wash",
    marketRegion: "UK",
    claim: "The UK manufacturer page declares 2% salicylic acid and describes Clear & Defend Daily Wash as a rinse-off face wash. The UK source version is not proof of the physical target package or its market.",
    additionalAssertions: [{
      claim: "The UK manufacturer page displays this INCI list for Clear & Defend 2% Salicylic Acid Face Wash: Aqua, Cocamidopropyl Hydroxysultaine, Sodium Methyl Cocoyl Taurate, Glycerin, Salicylic Acid, Sodium Hydrolyzed Potato Starch Dodecenylsuccinate, C12-15 Alkyl Lactate, Panthenol, Cocamidopropyl PG-Dimonium Chloride Phosphate, Disodium Tetrapropenyl Succinate, PEG-120 Methyl Glucose Dioleate, Sodium Chloride, Disodium EDTA, Citric Acid, Sodium Hydroxide, Tocopherol, Benzalkonium Chloride, Parfum. The manufacturer warns product and ingredients may change; the physical package label remains authoritative.",
      field: "ingredients", source_type: "MANUFACTURER",
      source_reference: "https://www.neutrogena.co.uk/skincare/cleansers-washes/clear-and-defend-daily-wash",
      claim_type: "MANUFACTURER_CLAIM", market_region: "UK",
    }],
  },
  {
    dossier: "P3 Garnier",
    productId: "HBI-PROD-C29AA2F410A84CCA",
    source: "https://www.garnier.com.au/about-our-brands/skin-active/garnier-skin-active-vitamin-c-brightening-gel-cleanser-200ml",
    marketRegion: "AU",
    claim: "The Australian manufacturer page identifies a Vitamin C brightening gel cleanser and lists Ascorbyl Glucoside (Vitamin Cg). This is a source-page snapshot; it does not establish the physical target package market or prove treatment efficacy.",
    additionalAssertions: [{
      claim: "The Australian manufacturer page displays this INCI list for the 200 ml Vitamin C Brightening Gel Cleanser: AQUA/WATER, SODIUM LAURETH SULFATE, COCO-BETAINE, SODIUM CHLORIDE, GLYCERIN, CITRUS LEMON FRUIT EXTRACT / LEMON FRUIT EXTRACT, PPG5-CETETH-20, SODIUM HYDROXIDE, ASCORBYL GLUCOSIDE, CITRIC ACID, PANTHENOL, POLYQUATERNIUM-7, TOCOPHERYL ACETATE, SODIUM BENZOATE, SALICYLIC ACID, LINALOOL, LIMONENE, BENZYL SALICYLATE, PARFUM / FRAGRANCE. The manufacturer warns ingredient lists are updated regularly and the package label is authoritative.",
      field: "ingredients", source_type: "MANUFACTURER",
      source_reference: "https://www.garnier.com.au/about-our-brands/skin-active/garnier-skin-active-vitamin-c-brightening-gel-cleanser-200ml",
      claim_type: "MANUFACTURER_CLAIM", market_region: "AU",
    }],
  },
  {
    dossier: "P4 SKIN1004",
    productId: "HBI-PROD-7F55ED88F41144F1",
    source: "https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-spf50-pa?country=GB",
    marketRegion: "INTERNATIONAL_KOREAN",
    claim: "The international manufacturer page identifies Hyalu-Cica Water-Fit Sun Serum as SPF50+ PA++++ and describes its UV-protection formula. Do not transfer the separate US sunscreen-drug formula or claims to this international dossier.",
    additionalAssertions: [{
      claim: "The international/Korean manufacturer page displays this INCI list for Hyalu-Cica Water-Fit Sun Serum SPF50+ PA++++: Water, Dibutyl Adipate, Propanediol, Diethylamino Hydroxybenzoyl Hexyl Benzoate, Polymethylsilsesquioxane, Ethylhexyl Triazone, Methylene Bis-Benzotriazolyl Tetramethylbutylphenol, Niacinamide, Coco-Caprylate/Caprate, Caprylyl Methicone, Diethylhexyl Butamido Triazone, Glycerin, 1,2-Hexanediol, Butylene Glycol, Pentylene Glycol, Behenyl Alcohol, Poly C10-30 Alkyl Acrylate, Polyglyceryl-3 Methylglucose Distearate, Decyl Glucoside, Tromethamine, Carbomer, Acrylates/C10-30 Alkyl Acrylate Crosspolymer, Sodium Stearoyl Glutamate, Polyacrylate Crosspolymer-6, Ethylhexylglycerin, Adenosine, Xanthan Gum, Centella Asiatica Extract, t-Butyl Alcohol, Sodium Hyaluronate, Betula Platyphylla Japonica Bark Extract, Tocopherol, Hydrolyzed Hyaluronic Acid, Camellia Sinensis Leaf Extract, Ginkgo Biloba Leaf Extract, Brassica Oleracea Italica (Broccoli) Sprout Extract, Camellia Japonica Leaf Extract, Eruca Sativa Leaf Extract, Medicago Sativa (Alfalfa) Extract, Triticum Vulgare (Wheat) Sprout Extract, Inositol, Hyaluronic Acid. This is the international source-page formula only; keep the US sunscreen-drug formula separate.",
      field: "ingredients", source_type: "MANUFACTURER",
      source_reference: "https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-spf50-pa?country=GB",
      claim_type: "MANUFACTURER_CLAIM", market_region: "INTERNATIONAL_KOREAN",
    }],
  },
  {
    dossier: "P5 ISDIN",
    productId: "HBI-PROD-96788ADC488942E3",
    source: "https://www.isdin.com/mx/p/fotoultra-active-unify-spf-50/1160",
    marketRegion: "MX",
    sourceDate: "2024",
    claim: "The existing research ledger's Mexico manufacturer source snapshot (2024) records reductions of 22% in spot intensity and 15% in spot area in 31 subjects. The current public page no longer exposes this result, so retain it only as a historical manufacturer-reported claim pending source revalidation; it is not independent efficacy evidence and is not proof of the physical target package/formula.",
  },
  {
    dossier: "P6 Clinique historical",
    productId: "HBI-PROD-70EEE418BE0F4DAB",
    source: "https://www.harrods.com/en-gb/p/clinique-even-better-clinical-radical-dark-spot-correctorand-interrupter-100ml-000000000006795757",
    marketRegion: "UK",
    field: "ingredients",
    sourceType: "RETAILER",
    claimType: "EVIDENCE",
    claim: "Harrods UK retailer listing for the historical 100 ml Even Better Clinical Radical Dark Spot Corrector + Interrupter displays this INCI string: WaterAquaEau, Cyclopentasiloxane, Dimethicone, Polysilicone-11, Isododecane, Butylene Glycol, Ascorbyl Glucoside, Peg-10 Dimethicone, Peg-6, Morus Bombycis (Mulberry) Root Extract, Scutellaria Baicalensis Root Extract, Camellia Sinensis Leaf Extract, Cucumis Sativus (Cucumber) Fruit Extract, Saccharomyces Lysate Extract, Hordeum Vulgare (Barley) ExtractExtrait D'Orge, Salicylic Acid, Triticum Vulgare (Wheat) Germ Extract, Cholesterol, Oryza Sativa (Rice) Bran Extract, Squalane, Acetyl Glucosamine, Sodium Hyaluronate, Caffeine, Isohexadecane, Betula Alba (Birch) Bark Extract, Trametes Versicolor Extract, Sodium Rna, Glycyrrhetinic Acid, Dimethoxytolyl Propylresorcinol, Di-C12-18 Alkyl Dimonium Chloride, Helianthus Annuus (Sunflower) Seedcake, Yeast ExtractFaexExtrait De Levure, Caprylyl Glycol, Propylene Glycol Dicaprate, Ammonium Acryloyldimethyltaurate/Vp Copolymer, Acrylamide/Sodium Acryloyldimethyltaurate Copolymer, Polysorbate 20, Tocopheryl Acetate, Polysorbate 80, Tromethamine, Sodium Hydroxide, Hexylene Glycol, Disodium Edta, Sodium Benzoate, Sodium Metabisulfite, Sodium Sulfite, Phenoxyethanol, Yellow 6 (Ci 15985), Yellow 5 (Ci 19140). This is a retailer source snapshot, not the physical package label; exact market/lot/formula match remains unverified. Keep it separate from the replacement Dark Spot Clearing Serum.",
  },
];

test("P1-P6 source-bound Evidence drafts persist and read back without Product Master mutation", async ({ request }) => {
  const api = process.env.HBI_TEST_API_URL || "http://127.0.0.1:8765/api/v1";
  const tokenResponse = await request.post(`${api}/auth/pilot-operator-token`);
  expect(tokenResponse.status(), await tokenResponse.text()).toBe(200);
  const operatorToken = (await tokenResponse.json()).access_token;
  const headers = { Authorization: `Bearer ${operatorToken}` };

  const productsBeforeResponse = await request.get(`${api}/products/manage`, { headers });
  expect(productsBeforeResponse.status(), await productsBeforeResponse.text()).toBe(200);
  const productsBefore = await productsBeforeResponse.json();
  const productIdsBefore = productsBefore.map((item) => item.product_id).sort();

  const before = new Map();
  for (const product of PRODUCTS) {
    const row = productsBefore.find((item) => item.product_id === product.productId);
    expect(row, `${product.dossier} canonical Product Master row missing`).toBeTruthy();
    expect(row.product_line).toBe("SKIN");
    const productResponse = await request.get(`${api}/products/${encodeURIComponent(product.productId)}`, { headers });
    expect(productResponse.status(), await productResponse.text()).toBe(200);
    before.set(product.productId, await productResponse.json());

    const evidenceResponse = await request.get(
      `${api}/evidence/?product_id=${encodeURIComponent(product.productId)}`,
      { headers },
    );
    expect(evidenceResponse.status(), await evidenceResponse.text()).toBe(200);
    before.set(`${product.productId}:evidenceIds`, new Set((await evidenceResponse.json()).map((item) => item.evidence_id)));

    const knowledgeResponse = await request.get(
      `${api}/evidence/knowledge/${encodeURIComponent(product.productId)}`,
      { headers },
    );
    expect(knowledgeResponse.status(), await knowledgeResponse.text()).toBe(200);
    before.set(`${product.productId}:knowledge`, await knowledgeResponse.json());
  }

  const written = [];
  for (const product of PRODUCTS) {
    const assertions = [
      {
        claim: product.claim,
        field: product.field === undefined ? "manufacturer_claims" : product.field,
        source_type: product.sourceType || "MANUFACTURER",
        source_reference: product.source,
        claim_type: product.claimType || "MANUFACTURER_CLAIM",
        notes: `Issue #406 approved P1-P6 staged intake; dossier=${product.dossier}; exact physical package/version match remains subject to the recorded dossier limits.`,
        ...(product.marketRegion ? { market_region: product.marketRegion } : {}),
        ...(product.sourceDate ? { source_date: product.sourceDate } : {}),
      },
      ...(product.additionalAssertions || []),
    ];
    const saveResponse = await request.post(
      `${api}/products/${encodeURIComponent(product.productId)}/research-draft`,
      { headers, data: { assertions } },
    );
    expect(saveResponse.status(), `${product.dossier}: ${await saveResponse.text()}`).toBe(200);
    const saved = await saveResponse.json();
    expect(saved).toHaveLength(assertions.length);
    for (let index = 0; index < assertions.length; index += 1) {
      const assertion = assertions[index];
      expect(saved[index]).toMatchObject({
        product_id: product.productId,
        field: assertion.field === undefined ? null : assertion.field,
        source_type: assertion.source_type,
        source_reference: assertion.source_reference,
        claim_type: assertion.claim_type,
        qa_status: "PENDING",
        evidence_status: "UNKNOWN",
      });
    }
    written.push({ product, evidenceIds: saved.map((item) => item.evidence_id) });
  }

  for (const { product, evidenceIds } of written) {
    const evidenceResponse = await request.get(
      `${api}/evidence/?product_id=${encodeURIComponent(product.productId)}`,
      { headers },
    );
    expect(evidenceResponse.status(), await evidenceResponse.text()).toBe(200);
    const evidenceAfter = await evidenceResponse.json();
    const newRows = evidenceAfter.filter((item) => !before.get(`${product.productId}:evidenceIds`).has(item.evidence_id));
    expect(newRows).toHaveLength(evidenceIds.length);
    for (const evidenceId of evidenceIds) {
      const row = newRows.find((item) => item.evidence_id === evidenceId);
      expect(row, `${product.dossier}: Evidence ${evidenceId} missing from read-back`).toBeTruthy();
      expect(row.product_id).toBe(product.productId);
      expect(row.qa_status).toBe("PENDING");
      expect(row.evidence_status).toBe("UNKNOWN");
    }

    const knowledgeAfterResponse = await request.get(
      `${api}/evidence/knowledge/${encodeURIComponent(product.productId)}`,
      { headers },
    );
    expect(knowledgeAfterResponse.status(), await knowledgeAfterResponse.text()).toBe(200);
    const knowledgeAfter = await knowledgeAfterResponse.json();
    const knowledgeBefore = before.get(`${product.productId}:knowledge`);
    for (const field of [
      "ingredients", "ingredient_roles", "claimed_benefits", "known_use_cases",
      "contraindications", "usage_instructions", "manufacturer_claims",
      "other_attributes", "evidence_refs", "evidence_status", "knowledge_confidence",
    ]) {
      expect(knowledgeAfter[field], `${product.dossier}: ProductKnowledge.${field} changed`).toEqual(knowledgeBefore[field]);
    }

    const productAfterResponse = await request.get(
      `${api}/products/${encodeURIComponent(product.productId)}`,
      { headers },
    );
    expect(productAfterResponse.status(), await productAfterResponse.text()).toBe(200);
    const productAfter = await productAfterResponse.json();
    const productBefore = before.get(product.productId);
    expect(productAfter).toMatchObject({
      product_id: product.productId,
      product_line: "SKIN",
      status: productBefore.status,
      identity_status: productBefore.identity_status,
      qa_verdict: productBefore.qa_verdict,
    });
  }

  const productsAfterResponse = await request.get(`${api}/products/manage`, { headers });
  expect(productsAfterResponse.status(), await productsAfterResponse.text()).toBe(200);
  const productsAfter = await productsAfterResponse.json();
  expect(productsAfter.map((item) => item.product_id).sort()).toEqual(productIdsBefore);
});
