const { test, expect } = require("@playwright/test");

test("Product Intake category remains operator-only and is not sent as knowledge evidence", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "d1-category-evidence-regression-token");
  });

  let createPayload = null;
  let createRequestCount = 0;

  // Every API request is fulfilled by an isolated browser fixture. No live API,
  // database, Product Master, Evidence, or QA write is performed by this test.
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

    if (path.endsWith("/products/duplicate-check/") && method === "POST") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ result: "NEW", check_id: "DUP-D1-FIXTURE-001", reason: "isolated regression fixture", candidates: [] }),
      });
    }

    if (path.endsWith("/products/") && method === "POST") {
      createRequestCount += 1;
      createPayload = request.postDataJSON();
      return route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({
          product_id: createPayload.product_id,
          brand: createPayload.brand,
          product_name: createPayload.product_name,
          product_line: createPayload.product_line,
          variant: createPayload.variant,
          size_value: createPayload.size_value,
          size_unit: createPayload.size_unit,
          identity_status: "NEEDS_REVIEW",
          qa_verdict: "PENDING",
          status: "DRAFT",
        }),
      });
    }

    if (path.endsWith("/products/manage") || path.endsWith("/products/sellable") || path.endsWith("/evidence/")) {
      return route.fulfill({ status: 200, contentType: "application/json", body: "[]" });
    }

    if (path.endsWith("/reports/sales/period/today")) {
      return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ sale_count: 0, revenue_toman: 0, revenue_usd: 0 }) });
    }

    return route.fulfill({ status: 200, contentType: "application/json", body: "[]" });
  });

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();

  await page.getByRole("button", { name: "ورود به مدیریت محصولات" }).click();
  await page.getByRole("button", { name: "ورود و ویرایش محصول" }).click();
  await expect(page.getByRole("heading", { name: /ورود محصول/ })).toBeVisible();

  await page.getByLabel("۱) خلاصه معرفی شما").fill("آبرسان آزمایشی, برند: TestBrand, حجم 50 ml");
  await page.getByRole("button", { name: "تکمیل هوشمند اطلاعات" }).click();
  await page.locator("#product-line-select").selectOption("SKIN");

  // A category value is explicitly present in the operator form; it must not
  // be transformed into either ProductKnowledge use-cases or evidence claims.
  await page.locator("label.pro-label").filter({ hasText: /^دسته$/ }).locator("xpath=following-sibling::input").fill("اپراتوری دسته تست");

  await page.getByRole("button", { name: "بررسی تکراری بودن" }).click();
  await expect(page.getByText("بررسی تکراری: NEW", { exact: false })).toBeVisible();

  await page.getByRole("button", { name: "ثبت محصول به‌صورت Draft" }).click();
  await expect(page.getByRole("status")).toContainText("ثبت اولیه انجام شد");

  expect(createRequestCount).toBe(1);
  expect(createPayload).not.toBeNull();
  expect(createPayload.product_line).toBe("SKIN");
  expect(createPayload).not.toHaveProperty("knowledge_use_cases");
  expect(createPayload).not.toHaveProperty("knowledge_evidence_claim");
  expect(createPayload).not.toHaveProperty("knowledge_evidence_source_reference");
});
