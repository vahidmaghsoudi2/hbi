const { test, expect } = require("@playwright/test");

test("selected existing skin product receives source-bound box drafts without creating a product", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "selected-skin-evidence-fixture-token");
  });

  const selectedProduct = {
    product_id: "HBI-SKIN-EXISTING-001",
    brand: "Fixture Skin Brand",
    product_name: "Existing Skin Product",
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

    if (path.endsWith("/products/HBI-SKIN-EXISTING-001/research-draft") && method === "POST") {
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
  await expect(page.getByText("Existing Skin Product")).toBeVisible();
  await page.getByRole("button", { name: "ویرایش" }).click();

  await expect(page.getByRole("heading", { name: "ویرایش محصول" })).toBeVisible();
  await expect(page.locator("#product-line-select")).toHaveValue("SKIN");

  const skinGoals = page.locator("label.pro-label").filter({ hasText: "اهداف پوستی اعلام‌شده" }).locator("..").locator("textarea");
  await expect(skinGoals).toBeEnabled();
  await skinGoals.fill("Fixture manufacturer claim for skin goals");

  // Source reference is mandatory: the API must not be called before it is supplied.
  await page.getByRole("button", { name: "ثبت باکس‌های مجاز به‌صورت پیش‌نویس" }).click();
  await expect(page.getByText(/نوع منبع و نشانی\/مرجع دقیق منبع.*الزامی است/)).toBeVisible();
  expect(researchRequestCount).toBe(0);

  await page.locator("label.pro-label").filter({ hasText: "نشانی یا مرجع دقیق منبع" }).locator("..").locator("input").fill("https://example.invalid/fixture-source");
  await page.getByRole("button", { name: "ثبت باکس‌های مجاز به‌صورت پیش‌نویس" }).click();
  await expect(page.getByRole("status")).toContainText("QA=PENDING");
  
  expect(researchRequestCount).toBe(1);
  expect(researchPath).toBe("/api/v1/products/HBI-SKIN-EXISTING-001/research-draft");
  expect(researchPayload.assertions).toHaveLength(1);
  expect(researchPayload.assertions[0]).toMatchObject({
    claim: "Fixture manufacturer claim for skin goals",
    field: "skin_goals",
    source_type: "MANUFACTURER",
    source_reference: "https://example.invalid/fixture-source",
  });
  expect(productCreateCount).toBe(0);
});
