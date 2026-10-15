const { test, expect } = require("@playwright/test");

test("Homepage requires the Admin session before exposing the workspace", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("heading", { name: "ورود مدیر HBI" })).toBeVisible();
});

test("Homepage navigation keeps sales, inventory, and reports in their own destinations", async ({ page }) => {
  // The route gate checks presence of the Admin session token. API authorization
  // is covered separately; this UI test uses a dummy token to exercise navigation.
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-navigation-test-token");
  });
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();

  // Direct sale remains a first-class destination and does not require consultation.
  await page.getByRole("button", { name: "ورود به فروش" }).click();
  await expect(page.getByRole("heading", { name: "فروش", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "بازکردن فروش" }).click();
  await expect(page.getByRole("heading", { name: "ثبت فروش" })).toBeVisible();
  await expect(page.getByText(/ثبت فروش مستقیم بدون مشاوره/)).toBeVisible();
  await expect(page.locator("#sale-product")).toBeVisible();

  // Inventory must open the inventory report, not silently land on today's sales.
  await page.getByRole("button", { name: "منوی اصلی" }).click();
  await page.getByRole("button", { name: "ورود به کالا و موجودی" }).click();
  await page.getByRole("link", { name: "بازکردن گزارش موجودی" }).click();
  await expect(page).toHaveURL(/\/accounting\?section=inventory$/);
  await expect(page.getByText("بخش فعال: موجودی")).toBeVisible();

  // Reports expose the existing report destinations explicitly.
  await page.getByRole("link", { name: "بازگشت به خانه HBI" }).click();
  await page.getByRole("button", { name: "ورود به گزارش‌ها" }).click();
  await expect(page.getByRole("link", { name: "بازکردن گزارش فروش" })).toBeVisible();
  await expect(page.getByRole("link", { name: "بازکردن گزارش موجودی" })).toBeVisible();
  await expect(page.getByRole("link", { name: "بازکردن گردش کالا" })).toBeVisible();
  await page.getByRole("link", { name: "بازکردن گزارش مالی" }).click();
  await expect(page).toHaveURL(/\/accounting\?section=finance-report$/);
  await expect(page.getByText("بخش فعال: گزارش مالی")).toBeVisible();
});
