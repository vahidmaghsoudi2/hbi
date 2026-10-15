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
  // The product picker must either offer real options or explain why it is empty.
  const productOptionCount = await page.locator("#sale-product option").count();
  if (productOptionCount <= 1) {
    await expect(page.getByRole("status")).toBeVisible();
  }

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

test("Dashboard report shortcuts preserve their own report destinations", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-dashboard-links-test-token");
  });
  await page.goto("/");
  await page.getByRole("button", { name: "بازکردن داشبورد" }).click();
  await expect(page.getByRole("heading", { name: "داشبورد HBI" })).toBeVisible();

  await expect(page.getByRole("link", { name: "گزارش فروش" })).toHaveAttribute("href", "/accounting?section=sales");
  await expect(page.getByRole("link", { name: "مشاهدهٔ موجودی" })).toHaveAttribute("href", "/accounting?section=inventory");
  await expect(page.getByRole("link", { name: "بررسی موجودی" })).toHaveAttribute("href", "/accounting?section=inventory");
  await expect(page.getByRole("link", { name: "بازکردن گزارش موجودی" })).toHaveAttribute("href", "/accounting?section=inventory");
  await expect(page.getByRole("link", { name: "همهٔ گردش‌ها" })).toHaveAttribute("href", "/accounting?section=stock-flow");
});

test("Settings is a separate homepage section and owns the logout action", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-settings-test-token");
  });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();

  await expect(page.getByRole("button", { name: "خروج از حساب مدیر" })).toHaveCount(0);
  await page.getByRole("button", { name: "ورود به تنظیمات" }).click();
  await expect(page.getByRole("heading", { name: "تنظیمات", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "حساب مدیر" })).toBeVisible();
  await page.getByRole("button", { name: "خروج از حساب مدیر" }).click();
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("heading", { name: "ورود مدیر HBI" })).toBeVisible();
});
