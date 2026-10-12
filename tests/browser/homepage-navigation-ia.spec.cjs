const { test, expect } = require("@playwright/test");

test("homepage navigation exposes each operational domain and its intended destinations", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "browser-test-admin-token");
  });

  await page.route("**/api/v1/products/manage", route => route.fulfill({ status: 200, contentType: "application/json", body: "[]" }));
  await page.route("**/api/v1/products/", route => route.fulfill({ status: 200, contentType: "application/json", body: "[]" }));

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "کار امروز را از اینجا شروع کنید." })).toBeVisible();

  const destinations = [
    ["خانه و داشبورد", "/"],
    ["کالا و انبار", "/catalog"],
    ["کاتالوگ کالاها", "/catalog"],
    ["بررسی پرونده کالا", "/workspace?panel=review"],
    ["ثبت و ویرایش کالا", "/workspace?panel=intake"],
    ["خرید و ورود موجودی", "/purchase"],
    ["مشتری و مشاوره", "/workspace?panel=consult"],
    ["ثبت مراجعه و مشاوره", "/workspace?panel=consult"],
    ["پرونده مشتری", "/workspace?panel=profile"],
    ["سوابق مراجعه", "/workspace?panel=previous"],
    ["نتایج ارزیابی و پیشنهاد", "/workspace?panel=results"],
    ["فروش", "/workspace?panel=sales"],
    ["مالی و حسابداری", "/accounting"],
  ];

  for (const [label, href] of destinations) {
    const link = page.getByRole("link", { name: new RegExp(label) }).first();
    await expect(link, `expected visible navigation link: ${label}`).toBeVisible();
    await expect(link).toHaveAttribute("href", href);
  }

  // The main domains must expose their operations in the correct submenu, without
  // duplicate generic-workspace/accounting cards in the homepage's secondary area.
  await expect(page.locator(".hbi-subnav").filter({ hasText: "کاتالوگ کالاها" })).toBeVisible();
  await expect(page.locator(".hbi-subnav").filter({ hasText: "پرونده مشتری" })).toBeVisible();
  await expect(page.getByRole("link", { name: "محیط کاری کامل" })).toHaveCount(0);
  await expect(page.locator(".hbi-more-card").filter({ hasText: "مالی و حسابداری" })).toHaveCount(0);

  // Direct sale must remain a first-class route and not be nested under consultation.
  await page.locator('a.hbi-nav-item[href="/workspace?panel=sales"]').click();
  await expect(page).toHaveURL(/\/workspace\?panel=sales$/);
  await expect(page.getByRole("heading", { name: "ثبت فروش" })).toBeVisible();
});

test("unknown route returns to the authenticated homepage instead of rendering a blank page", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "browser-test-admin-token");
  });

  await page.goto("/this-route-does-not-exist");
  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("heading", { name: "کار امروز را از اینجا شروع کنید." })).toBeVisible();
});

test("logout returns to login and protected routes remain gated", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "browser-test-admin-token");
  });

  await page.goto("/");
  await page.getByRole("button", { name: /خروج از حساب/ }).click();
  await expect(page).toHaveURL(/\/login$/);

  await page.goto("/accounting");
  await expect(page).toHaveURL(/\/login$/);
});
