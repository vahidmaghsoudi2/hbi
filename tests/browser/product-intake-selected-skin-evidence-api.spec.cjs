const { test, expect } = require("@playwright/test");

test("authenticated Anua Evidence draft is saved and read back without changing Product Master", async ({ page, request }) => {
  const api = process.env.HBI_TEST_API_URL || "http://127.0.0.1:8765/api/v1";
  const productId = "HBI-PROD-22C55A8223A945A6";
  const productName = "Azelaic Acid 10% + Hyaluron Redness Soothing Serum";
  const sourceReference = "https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum";

  const tokenResponse = await request.post(`${api}/auth/pilot-operator-token`);
  expect(tokenResponse.status(), await tokenResponse.text()).toBe(200);
  const operatorToken = (await tokenResponse.json()).access_token;
  const headers = { Authorization: `Bearer ${operatorToken}` };

  const productsBeforeResponse = await request.get(`${api}/products/manage`, { headers });
  expect(productsBeforeResponse.status(), await productsBeforeResponse.text()).toBe(200);
  const productsBefore = await productsBeforeResponse.json();
  const productBefore = productsBefore.find((item) => item.product_id === productId);
  expect(productBefore).toBeTruthy();
  expect(productBefore).toMatchObject({
    product_line: "SKIN",
    status: "DRAFT",
    identity_status: "NEEDS_REVIEW",
    qa_verdict: "PENDING",
  });

  const evidenceBeforeResponse = await request.get(`${api}/evidence/?product_id=${encodeURIComponent(productId)}`, { headers });
  expect(evidenceBeforeResponse.status(), await evidenceBeforeResponse.text()).toBe(200);
  const evidenceBefore = await evidenceBeforeResponse.json();
  const beforeEvidenceIds = new Set(evidenceBefore.map((item) => item.evidence_id));

  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "authenticated-evidence-browser-proof-admin-gate");
  });

  let productCreateCount = 0;
  let productUpdateCount = 0;
  let researchDraftCount = 0;
  page.on("request", (req) => {
    const url = new URL(req.url());
    if (url.pathname === "/api/v1/products/" && req.method() === "POST") productCreateCount += 1;
    if (url.pathname === `/api/v1/products/${productId}` && ["PUT", "PATCH"].includes(req.method())) productUpdateCount += 1;
    if (url.pathname === `/api/v1/products/${productId}/research-draft` && req.method() === "POST") researchDraftCount += 1;
  });

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();
  await page.getByRole("button", { name: "ورود به مدیریت محصولات" }).click();
  await page.getByRole("button", { name: "بازکردن فهرست کالاها" }).click();

  const productCard = page.locator("article.pro-product-card").filter({ hasText: productName });
  await expect(productCard).toBeVisible();
  await productCard.getByRole("button", { name: "ویرایش" }).click();

  await expect(page.getByRole("heading", { name: "ویرایش محصول" })).toBeVisible();
  await expect(page.locator("#product-line-select")).toHaveValue("SKIN");
  await expect(page.locator("#skin-template")).toHaveValue("HYDRATING_MOISTURIZER");

  const ingredients = page.locator("label.pro-label").filter({ hasText: "ترکیبات پشتیبانِ اعلام‌شده طبق منبع" }).locator("..").locator("textarea");
  const soothingClaim = page.locator("label.pro-label").filter({ hasText: "ادعای تسکینِ اعلام‌شده طبق منبع" }).locator("..").locator("textarea");
  await ingredients.fill("Panthenol, Niacinamide and Sodium Hyaluronate are listed on the official manufacturer source");
  await soothingClaim.fill("The manufacturer describes the serum as redness soothing");
  await page.locator("label.pro-label").filter({ hasText: "نشانی یا مرجع دقیق منبع" }).locator("..").locator("input").fill(sourceReference);

  const saveResponsePromise = page.waitForResponse((response) =>
    response.request().method() === "POST" && response.url().endsWith(`/products/${productId}/research-draft`)
  );
  await page.getByRole("button", { name: "ثبت باکس‌های مجاز به‌صورت پیش‌نویس" }).click();
  const saveResponse = await saveResponsePromise;
  expect(saveResponse.status(), await saveResponse.text()).toBe(200);
  await expect(page.getByRole("status")).toContainText("QA=PENDING");
  expect(researchDraftCount).toBe(1);
  expect(productCreateCount).toBe(0);
  expect(productUpdateCount).toBe(0);

  const savedEvidence = await saveResponse.json();
  expect(savedEvidence).toHaveLength(2);
  expect(savedEvidence.every((item) => item.product_id === productId)).toBeTruthy();
  expect(savedEvidence.every((item) => item.qa_status === "PENDING")).toBeTruthy();
  expect(savedEvidence.every((item) => item.evidence_status === "UNKNOWN")).toBeTruthy();

  const evidenceAfterResponse = await request.get(`${api}/evidence/?product_id=${encodeURIComponent(productId)}`, { headers });
  expect(evidenceAfterResponse.status(), await evidenceAfterResponse.text()).toBe(200);
  const evidenceAfter = await evidenceAfterResponse.json();
  const newEvidence = evidenceAfter.filter((item) => !beforeEvidenceIds.has(item.evidence_id));
  expect(newEvidence).toHaveLength(2);
  expect(newEvidence.map((item) => item.field).sort()).toEqual(["ingredients", "manufacturer_claims"]);
  expect(newEvidence.every((item) => item.product_id === productId)).toBeTruthy();
  expect(newEvidence.every((item) => item.qa_status === "PENDING")).toBeTruthy();
  expect(newEvidence.every((item) => item.evidence_status === "UNKNOWN")).toBeTruthy();
  expect(newEvidence.every((item) => item.source_type === "MANUFACTURER")).toBeTruthy();
  expect(newEvidence.every((item) => item.source_reference === sourceReference)).toBeTruthy();

  const productAfterResponse = await request.get(`${api}/products/${encodeURIComponent(productId)}`, { headers });
  expect(productAfterResponse.status(), await productAfterResponse.text()).toBe(200);
  const productAfter = await productAfterResponse.json();
  expect(productAfter).toMatchObject({
    product_id: productId,
    product_line: "SKIN",
    status: "DRAFT",
    identity_status: "NEEDS_REVIEW",
    qa_verdict: "PENDING",
  });

  const productsAfterResponse = await request.get(`${api}/products/manage`, { headers });
  expect(productsAfterResponse.status(), await productsAfterResponse.text()).toBe(200);
  const productsAfter = await productsAfterResponse.json();
  expect(productsAfter.map((item) => item.product_id).sort()).toEqual(
    productsBefore.map((item) => item.product_id).sort()
  );
});
