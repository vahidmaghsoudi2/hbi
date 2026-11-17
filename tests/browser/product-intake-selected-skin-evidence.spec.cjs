const { test, expect } = require("@playwright/test");

test("selected existing skin product receives source-bound box drafts without creating a product", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "selected-skin-evidence-fixture-token");
  });

  const selectedProduct = {
    product_id: "HBI-PROD-2CC249240D504453",
    brand: "Neutrogena",
    product_name: "Clear & Defend 2% Salicylic Acid Face Wash",
    product_line: "SKIN",
    variant: "clear",
    size_value: 50,
    size_unit: "ml",
    identity_status: "VERIFIED",
    qa_verdict: "PENDING",
    status: "ACTIVE",
  };
  let researchPayload = null;
  let researchPath = null;
  let researchRequestCount = 0;
  let productCreateCount = 0;

  // Isolated API fixtures only: no live API or database writes.
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname;
    const method = request.method();

    if (path.endsWith("/auth/pilot-operator-token") && method === "POST") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ access_token: "fixture-operator-token", refresh_token: "fixture-refresh-token", token_type: "bearer" }),
      });
    }

    if (path.endsWith("/products/manage") && method === "GET") {
      return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([selectedProduct]) });
    }

    if (path.endsWith("/evidence/") && method === "GET") {
      return route.fulfill({ status: 200, contentType: "application/json", body: "[]" });
    }

    if (path.endsWith("/products/HBI-PROD-2CC249240D504453/research-draft") && method === "POST") {
      researchRequestCount += 1;
      researchPath = path;
      researchPayload = request.postDataJSON();
      return route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify((researchPayload.assertions || []).map((item, index) => ({
          evidence_id: `FIXTURE-EVIDENCE-${index + 1}`,
          product_id: selectedProduct.product_id,
          claim: item.claim,
          field: item.field,
          source_type: item.source_type,
          source_reference: item.source_reference,
          qa_status: "PENDING",
          evidence_status: "UNKNOWN",
          conflict_status: "NONE",
        }))),
      });
    }

    if (path.endsWith("/products/") && method === "POST") {
      productCreateCount += 1;
      return route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Unexpected product creation in this test" }) });
    }

    if (path.endsWith("/reports/sales/period/today")) {
      return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ sale_count: 0, revenue_toman: 0, revenue_usd: 0 }) });
    }

    return route.fulfill({ status: 200, contentType: "application/json", body: "[]" });
  });

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();
  await page.getByRole("button", { name: "ورود به مدیریت محصولات" }).click();
  await page.getByRole("button", { name: "بازکردن فهرست کالاها" }).click();
  await expect(page.getByText("Clear & Defend 2% Salicylic Acid Face Wash")).toBeVisible();
  await page.getByRole("button", { name: "ویرایش" }).click();

  await expect(page.getByRole("heading", { name: "ویرایش محصول" })).toBeVisible();
  await expect(page.locator("#product-line-select")).toHaveValue("SKIN");
  await expect(page.locator("#skin-template")).toHaveValue("CLEANSING_GEL");
  await expect(page.locator("#skin-template")).toBeDisabled();

  const skinGoals = page.locator("label.pro-label").filter({ hasText: "کاربردهای پوستی اعلام‌شده سازنده" }).locator("..").locator("textarea");
  await expect(skinGoals).toBeEnabled();
  await skinGoals.fill("Fixture manufacturer claim for skin goals");

  const salicylic = page.locator("label.pro-label").filter({ hasText: "سالیسیلیک اسید و غلظتِ اعلام‌شده در همین نسخه" }).locator("..").locator("textarea");
  await expect(salicylic).toBeEnabled();
  await salicylic.fill("2% salicylic acid as stated on the cited UK source; exact physical pack not confirmed");
  const otherFeatures = page.locator("label.pro-label").filter({ hasText: "سایر ویژگی‌ها (برای هر محصول" }).locator("..").locator("textarea");
  await expect(otherFeatures).toBeEnabled();
  await otherFeatures.fill("Additional sourced note that has no dedicated box");

  // Source reference is mandatory: the API must not be called before it is supplied.
  await page.getByRole("button", { name: "ثبت باکس‌های مجاز به‌صورت پیش‌نویس" }).click();
  await expect(page.getByText(/نوع منبع و نشانی\/مرجع دقیق منبع.*الزامی است/)).toBeVisible();
  expect(researchRequestCount).toBe(0);

  await page.locator("label.pro-label").filter({ hasText: "نشانی یا مرجع دقیق منبع" }).locator("..").locator("input").fill("https://example.invalid/fixture-source");
  await page.getByRole("button", { name: "ثبت باکس‌های مجاز به‌صورت پیش‌نویس" }).click();
  await expect(page.getByRole("status")).toContainText("QA=PENDING");
  
  expect(researchRequestCount).toBe(1);
  expect(researchPath).toBe("/api/v1/products/HBI-PROD-2CC249240D504453/research-draft");
  expect(researchPayload.assertions).toHaveLength(3);
  expect(researchPayload.assertions[0]).toMatchObject({
    claim: "Fixture manufacturer claim for skin goals",
    field: "known_use_cases",
    source_type: "MANUFACTURER",
    source_reference: "https://example.invalid/fixture-source",
  });
  expect(researchPayload.assertions[1]).toMatchObject({
    claim: "2% salicylic acid as stated on the cited UK source; exact physical pack not confirmed",
    field: "ingredients",
    claim_type: "MANUFACTURER_CLAIM",
    source_reference: "https://example.invalid/fixture-source",
  });
  expect(researchPayload.assertions[2]).toMatchObject({
    claim: "سایر ویژگی‌ها: Additional sourced note that has no dedicated box",
    field: "other_attributes",
    claim_type: "UNKNOWN",
    source_type: "MANUFACTURER",
    source_reference: "https://example.invalid/fixture-source",
    notes: expect.stringContaining("box kind=other"),
  });
  expect(productCreateCount).toBe(0);
});


test("Anua soothing claim maps to manufacturer claims, not ingredients", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "selected-skin-evidence-fixture-token");
  });

  const selectedProduct = {
    product_id: "HBI-PROD-22C55A8223A945A6",
    brand: "Anua",
    product_name: "Azelaic Acid 10% + Hyaluron Redness Soothing Serum",
    product_line: "SKIN",
    size_value: 30,
    size_unit: "ml",
    identity_status: "NEEDS_REVIEW",
    qa_verdict: "PENDING",
    status: "DRAFT",
  };
  let researchPayload = null;
  let researchPath = null;
  let productCreateCount = 0;

  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname;
    const method = request.method();

    if (path.endsWith("/auth/pilot-operator-token") && method === "POST") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ access_token: "fixture-operator-token", refresh_token: "fixture-refresh-token", token_type: "bearer" }),
      });
    }
    if (path.endsWith("/products/manage") && method === "GET") {
      return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([selectedProduct]) });
    }
    if (path.endsWith("/evidence/") && method === "GET") {
      return route.fulfill({ status: 200, contentType: "application/json", body: "[]" });
    }
    if (path.endsWith("/products/HBI-PROD-22C55A8223A945A6/research-draft") && method === "POST") {
      researchPath = path;
      researchPayload = request.postDataJSON();
      return route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify((researchPayload.assertions || []).map((item, index) => ({
          evidence_id: `FIXTURE-ANUA-EVIDENCE-${index + 1}`,
          product_id: selectedProduct.product_id,
          claim: item.claim,
          field: item.field,
          source_type: item.source_type,
          source_reference: item.source_reference,
          qa_status: "PENDING",
          evidence_status: "UNKNOWN",
          conflict_status: "NONE",
        }))),
      });
    }
    if (path.endsWith("/products/") && method === "POST") {
      productCreateCount += 1;
      return route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Unexpected product creation in this test" }) });
    }
    if (path.endsWith("/reports/sales/period/today")) {
      return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ sale_count: 0, revenue_toman: 0, revenue_usd: 0 }) });
    }
    return route.fulfill({ status: 200, contentType: "application/json", body: "[]" });
  });

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();
  await page.getByRole("button", { name: "ورود به مدیریت محصولات" }).click();
  await page.getByRole("button", { name: "بازکردن فهرست کالاها" }).click();
  await expect(page.getByText("Azelaic Acid 10% + Hyaluron Redness Soothing Serum")).toBeVisible();
  await page.getByRole("button", { name: "ویرایش" }).click();
  await expect(page.getByRole("heading", { name: "ویرایش محصول" })).toBeVisible();
  await expect(page.locator("#product-line-select")).toHaveValue("SKIN");
  await expect(page.locator("#skin-template")).toHaveValue("HYDRATING_MOISTURIZER");

  const ingredients = page.locator("label.pro-label").filter({ hasText: "ترکیبات پشتیبانِ اعلام‌شده طبق منبع" }).locator("..").locator("textarea");
  const soothingClaim = page.locator("label.pro-label").filter({ hasText: "ادعای تسکینِ اعلام‌شده طبق منبع" }).locator("..").locator("textarea");
  await ingredients.fill("Panthenol, Niacinamide and Sodium Hyaluronate are listed on the official source");
  await soothingClaim.fill("The manufacturer describes the serum as redness soothing");
  await page.locator("label.pro-label").filter({ hasText: "نشانی یا مرجع دقیق منبع" }).locator("..").locator("input").fill("https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum");

  await page.getByRole("button", { name: "ثبت باکس‌های مجاز به‌صورت پیش‌نویس" }).click();
  await expect(page.getByRole("status")).toContainText("QA=PENDING");

  expect(researchPath).toBe("/api/v1/products/HBI-PROD-22C55A8223A945A6/research-draft");
  expect(researchPayload.assertions).toHaveLength(2);
  expect(researchPayload.assertions[0]).toMatchObject({
    field: "ingredients",
    claim_type: "MANUFACTURER_CLAIM",
    source_type: "MANUFACTURER",
    source_reference: "https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum",
  });
  expect(researchPayload.assertions[1]).toMatchObject({
    claim: "The manufacturer describes the serum as redness soothing",
    field: "manufacturer_claims",
    claim_type: "MANUFACTURER_CLAIM",
    source_type: "MANUFACTURER",
    source_reference: "https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum",
  });
  expect(productCreateCount).toBe(0);
});
