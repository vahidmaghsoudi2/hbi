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
  },
  {
    dossier: "P3 Garnier",
    productId: "HBI-PROD-C29AA2F410A84CCA",
    source: "https://www.garnier.com.au/about-our-brands/skin-active/garnier-skin-active-vitamin-c-brightening-gel-cleanser-200ml",
    marketRegion: "AU",
    claim: "The Australian manufacturer page identifies a Vitamin C brightening gel cleanser and lists Ascorbyl Glucoside (Vitamin Cg). This is a source-page snapshot; it does not establish the physical target package market or prove treatment efficacy.",
  },
  {
    dossier: "P4 SKIN1004",
    productId: "HBI-PROD-7F55ED88F41144F1",
    source: "https://www.skin1004.com/products/hyalu-cica-water-fit-sun-serum-spf50-pa?country=GB",
    marketRegion: "INTERNATIONAL_KOREAN",
    claim: "The international manufacturer page identifies Hyalu-Cica Water-Fit Sun Serum as SPF50+ PA++++ and describes its UV-protection formula. Do not transfer the separate US sunscreen-drug formula or claims to this international dossier.",
  },
  {
    dossier: "P5 ISDIN",
    productId: "HBI-PROD-96788ADC488942E3",
    source: "https://www.isdin.com/mx/p/fotoultra-active-unify-spf-50/1160",
    marketRegion: "MX",
    claim: "The Mexico manufacturer page reports reductions of 22% in spot intensity and 15% in spot area in 31 subjects, labelled as manufacturer-held data (2024). This is a manufacturer-reported result; the full protocol and match to the physical target package/formula are not independently verified.",
  },
  {
    dossier: "P6 Clinique historical",
    productId: "HBI-PROD-70EEE418BE0F4DAB",
    source: "https://www.harrods.com/en-gb/p/clinique-even-better-clinical-radical-dark-spot-correctorand-interrupter-100ml-000000000006795757",
    marketRegion: undefined,
    field: null,
    sourceType: "RETAILER",
    claimType: "FACT",
    claim: "The retailer listing identifies the historical 100 ml Even Better Clinical Radical Dark Spot Corrector + Interrupter and displays a historical INCI pattern including Ascorbyl Glucoside, Salicylic Acid and Dimethoxytolyl Propylresorcinol. This is retailer listing evidence only; physical package, market, lot and exact formula remain unverified. Do not transfer the replacement serum's formula or claims.",
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
    const assertion = {
      claim: product.claim,
      field: product.field === undefined ? "manufacturer_claims" : product.field,
      source_type: product.sourceType || "MANUFACTURER",
      source_reference: product.source,
      claim_type: product.claimType || "MANUFACTURER_CLAIM",
      notes: `Issue #406 approved P1-P6 staged intake; dossier=${product.dossier}; exact physical package/version match remains subject to the recorded dossier limits.`,
      ...(product.marketRegion ? { market_region: product.marketRegion } : {}),
    };
    const saveResponse = await request.post(
      `${api}/products/${encodeURIComponent(product.productId)}/research-draft`,
      { headers, data: { assertions: [assertion] } },
    );
    expect(saveResponse.status(), `${product.dossier}: ${await saveResponse.text()}`).toBe(200);
    const saved = await saveResponse.json();
    expect(saved).toHaveLength(1);
    expect(saved[0]).toMatchObject({
      product_id: product.productId,
      field: product.field === undefined ? "manufacturer_claims" : product.field,
      source_type: product.sourceType || "MANUFACTURER",
      source_reference: product.source,
      claim_type: product.claimType || "MANUFACTURER_CLAIM",
      qa_status: "PENDING",
      evidence_status: "UNKNOWN",
    });
    written.push({ product, evidenceId: saved[0].evidence_id });
  }

  for (const { product, evidenceId } of written) {
    const evidenceResponse = await request.get(
      `${api}/evidence/?product_id=${encodeURIComponent(product.productId)}`,
      { headers },
    );
    expect(evidenceResponse.status(), await evidenceResponse.text()).toBe(200);
    const evidenceAfter = await evidenceResponse.json();
    const newRows = evidenceAfter.filter((item) => !before.get(`${product.productId}:evidenceIds`).has(item.evidence_id));
    expect(newRows).toHaveLength(1);
    expect(newRows[0].evidence_id).toBe(evidenceId);
    expect(newRows[0]).toMatchObject({
      product_id: product.productId,
      field: product.field === undefined ? "manufacturer_claims" : product.field,
      source_type: product.sourceType || "MANUFACTURER",
      source_reference: product.source,
      claim_type: product.claimType || "MANUFACTURER_CLAIM",
      qa_status: "PENDING",
      evidence_status: "UNKNOWN",
    });

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
