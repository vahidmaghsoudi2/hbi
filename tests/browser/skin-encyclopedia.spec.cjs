const { test, expect } = require("@playwright/test");

test("Skin encyclopedia reads product identity, evidence and knowledge without inventing missing values", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "skin-encyclopedia-test-token");
  });

  const product = {
    product_id: "TEST-SKIN-001",
    brand: "Test Brand",
    product_name: "Test Moisturizer",
    product_line: "SKIN",
    variant: null,
    size_value: null,
    size_unit: null,
    identity_status: "UNVERIFIED",
    qa_verdict: "PENDING",
    status: "DRAFT",
  };
  const hairProduct = {
    product_id: "TEST-HAIR-001",
    brand: "Test Brand",
    product_name: "Test Hair Serum",
    product_line: "HAIR",
    variant: null,
    size_value: null,
    size_unit: null,
    identity_status: "UNVERIFIED",
    qa_verdict: "PENDING",
    status: "DRAFT",
  };

  await page.route("**/api/v1/products/manage", (route) => route.fulfill({
    status: 200, contentType: "application/json", body: JSON.stringify([product, hairProduct]),
  }));
  await page.route("**/api/v1/products/TEST-SKIN-001", (route) => route.fulfill({
    status: 200, contentType: "application/json", body: JSON.stringify(product),
  }));
  await page.route("**/api/v1/evidence/?product_id=TEST-SKIN-001", (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify([{
      evidence_id: "EV-TEST-001",
      product_id: "TEST-SKIN-001",
      field: "ingredients",
      claim: "Water",
      claim_type: "MANUFACTURER_CLAIM",
      qa_status: "PENDING",
      evidence_status: "UNKNOWN",
      conflict_status: "NONE",
      source_type: "OFFICIAL_SOURCE",
      source_reference: "https://example.invalid/product",
    }]),
  }));
  await page.route("**/api/v1/evidence/knowledge/TEST-SKIN-001", (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify({
      product_knowledge_id: "PK-TEST-001",
      product_id: "TEST-SKIN-001",
      ingredients: null,
      ingredient_roles: null,
      claimed_benefits: null,
      known_use_cases: null,
      contraindications: null,
      usage_instructions: null,
      manufacturer_claims: null,
      evidence_refs: null,
      evidence_status: "UNKNOWN",
      knowledge_confidence: null,
    }),
  }));

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();
  await page.getByRole("button", { name: "ورود به دانشنامه" }).click();
  await page.getByRole("button", { name: "مشاهده محصولات ثبت‌شده" }).click();

  await expect(page.getByRole("heading", { name: "دانشنامهٔ ویژگی محصولات پوستی" })).toBeVisible();
  await expect(page.getByLabel("انتخاب محصول")).toContainText("Test Moisturizer");
  await expect(page.getByLabel("انتخاب محصول")).not.toContainText("Test Hair Serum");
  await expect(page.getByRole("heading", { name: "هویت و نسخهٔ محصول" })).toBeVisible();
  await expect(page.getByText("ثبت نشده / نامشخص").first()).toBeVisible();
  await expect(page.getByRole("heading", { name: "دانش تجمیع‌شدهٔ واجد شرایط" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "شواهد و منشأ اطلاعات" })).toBeVisible();
  await expect(page.getByText("Water")).toBeVisible();
  await expect(page.getByText(/QA: PENDING · شواهد: UNKNOWN/)).toBeVisible();
});
