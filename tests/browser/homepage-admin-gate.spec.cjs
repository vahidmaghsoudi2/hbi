const { test, expect } = require("@playwright/test");

test("operational homepage redirects unauthenticated visits to Admin login", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("heading", { name: "ورود مدیر HBI" })).toBeVisible();
});

test("pilot consultation route remains independently reachable without Admin session", async ({ page }) => {
  await page.goto("/pilot");
  await expect(page.getByRole("button", { name: "دریافت JWT" })).toBeVisible();
});

test("existing buyer can be selected for sale without minting a customer or pilot token", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "browser-test-admin-token");
  });

  let pilotTokenRequests = 0;
  page.on("request", request => {
    if (/\/auth\/(pilot-token|pilot-operator-token)$/.test(request.url())) pilotTokenRequests += 1;
  });

  await page.route("**/api/v1/products/manage", route => route.fulfill({ status: 200, contentType: "application/json", body: "[]" }));
  await page.route("**/api/v1/products/", route => route.fulfill({ status: 200, contentType: "application/json", body: "[]" }));
  await page.route("**/api/v1/customers/search?**", route => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify([{ customer_id: "CUST-BROWSER-1", name: "Browser Buyer", mobile: "09120000000", concerns: null, skin_profile: null }])
  }));

  await page.goto("/");
  await page.locator('a.hbi-nav-item[href="/workspace?panel=sales"]').click();
  await expect(page).toHaveURL(/\/workspace\?panel=sales$/);
  await expect(page.getByRole("heading", { name: "ثبت فروش" })).toBeVisible();
  await page.locator("#sale-customer-search").fill("09120000000");
  await page.getByRole("button", { name: "جست‌وجوی مشتری" }).click();
  await page.getByRole("button", { name: /انتخاب برای فروش: Browser Buyer/ }).click();

  await expect(page.getByText("CUST-BROWSER-1", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "ثبت فروش" })).toBeVisible();
  expect(pilotTokenRequests).toBe(0);
});


test("existing customer consultation retains the legacy pilot-token session flow", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "browser-test-admin-token");
  });

  let pilotTokenRequests = 0;
  let historyAuthorization = "";
  page.on("request", request => {
    if (/\/auth\/pilot-token$/.test(request.url())) pilotTokenRequests += 1;
    if (/\/api\/v1\/sales\/customer\/CUST-BROWSER-2$/.test(request.url())) {
      historyAuthorization = request.headers()["authorization"] || "";
    }
  });

  await page.route("**/api/v1/products/manage", route => route.fulfill({ status: 200, contentType: "application/json", body: "[]" }));
  await page.route("**/api/v1/products/", route => route.fulfill({ status: 200, contentType: "application/json", body: "[]" }));
  await page.route("**/api/v1/customers/search?**", route => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify([{ customer_id: "CUST-BROWSER-2", name: "Consult Buyer", mobile: "09121111111", concerns: "ضدآفتاب", skin_profile: "خشک" }])
  }));
  await page.route("**/api/v1/auth/pilot-token", route => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify({ access_token: "browser-test-customer-token", refresh_token: "browser-test-refresh-token", token_type: "bearer" })
  }));
  await page.route("**/api/v1/sales/customer/CUST-BROWSER-2", route => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: "[]"
  }));
  await page.route("**/api/v1/customers/id/CUST-BROWSER-2", route => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify({ customer_id: "CUST-BROWSER-2", name: "Consult Buyer", mobile: "09121111111", concerns: "ضدآفتاب", skin_profile: "خشک" })
  }));

  await page.goto("/");
  await page.locator('a.hbi-nav-item[href="/workspace?panel=sales"]').click();
  await expect(page).toHaveURL(/\/workspace\?panel=sales$/);
  await page.locator("#sale-customer-search").fill("09121111111");
  await page.getByRole("button", { name: "جست‌وجوی مشتری" }).click();
  await page.getByRole("button", { name: /انتخاب برای مشاوره: Consult Buyer/ }).click();
  // Consultation selection switches the active panel locally; assert the UI rather than a URL change.
  await expect(page.getByRole("button", { name: "ثبت مراجعه + دریافت پیشنهاد" })).toBeVisible();
  await expect.poll(() => page.evaluate(() => sessionStorage.getItem("hbi_access_token"))).toBe("browser-test-customer-token");
  await expect.poll(() => page.evaluate(() => sessionStorage.getItem("hbi_customer_id"))).toBe("CUST-BROWSER-2");
  await expect.poll(() => historyAuthorization).toBe("Bearer browser-test-customer-token");
  expect(pilotTokenRequests).toBe(1);
});

test("sale picker uses Admin-managed catalog, excludes drafts, and has no manual product-id bypass", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "browser-test-admin-token");
  });

  let publicProductListRequests = 0;
  page.on("request", request => {
    if (/\\/api\\/v1\\/products\\/$/.test(new URL(request.url()).pathname)) publicProductListRequests += 1;
  });

  await page.route("**/api/v1/products/manage", route => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify([
      { product_id: "P-ACTIVE", product_name: "Active sunscreen", brand: "Brand A", status: "ACTIVE", identity_status: "VERIFIED", qa_verdict: "VALID" },
      { product_id: "P-DRAFT", product_name: "Draft sunscreen", brand: "Brand B", status: "DRAFT", identity_status: "NEEDS_REVIEW", qa_verdict: "PENDING" }
    ])
  }));
  await page.route("**/api/v1/customers/search?**", route => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify([{ customer_id: "CUST-PICKER-1", name: "Picker Buyer", mobile: "09123334444" }])
  }));

  await page.goto("/");
  await page.locator('a.hbi-nav-item[href="/workspace?panel=sales"]').click();
  await page.locator("#sale-customer-search").fill("09123334444");
  await page.getByRole("button", { name: "جست‌وجوی مشتری" }).click();
  await page.getByRole("button", { name: /انتخاب برای فروش: Picker Buyer/ }).click();

  const picker = page.locator("#sale-product");
  await expect(picker.locator("option", { hasText: "Active sunscreen" })).toHaveCount(1);
  await expect(picker.locator("option", { hasText: "Draft sunscreen" })).toHaveCount(0);
  await expect(page.locator("#sale-manual")).toHaveCount(0);
  expect(publicProductListRequests).toBe(0);
});
