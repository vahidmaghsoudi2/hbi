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
  await page.getByRole("button", { name: "فروش", exact: true }).click();
  await page.locator("#sale-customer-search").fill("09120000000");
  await page.getByRole("button", { name: "جست‌وجوی مشتری" }).click();
  await page.getByRole("button", { name: /انتخاب برای فروش: Browser Buyer/ }).click();

  await expect(page.getByText("CUST-BROWSER-1", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "ثبت فروش" })).toBeVisible();
  expect(pilotTokenRequests).toBe(0);
});
