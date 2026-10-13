const { test, expect } = require("@playwright/test");

async function openSubmenu(page, domainLabel) {
  const group = page.locator(".hbi-nav-group").filter({ hasText: domainLabel }).first();
  const toggle = group.getByRole("button", { name: new RegExp(`باز کردن زیرمنوی ${domainLabel}`) });
  if (await toggle.count()) {
    await toggle.click();
  }
}

test("homepage navigation exposes each operational domain and its intended destinations", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "browser-test-admin-token");
  });

  await page.route("**/api/v1/products/manage", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: "[]" })
  );
  await page.route("**/api/v1/products/", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: "[]" })
  );

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "کار امروز را از اینجا شروع کنید." })).toBeVisible();

  // Top-level domains (always visible).
  const topLevel = [
    ["خانه", "/"],
    ["کالا و انبار", "/catalog"],
    ["مشتری و مشاوره", "/workspace?panel=previous"],
    ["فروش", "/sales"],
    ["حسابداری و گزارش", "/accounting"],
  ];
  for (const [label, href] of topLevel) {
    const link = page.locator(`a.hbi-nav-item[href="${href}"]`).filter({ hasText: label }).first();
    await expect(link, `expected visible domain link: ${label}`).toBeVisible();
  }

  // Settings must not appear without a real route.
  await expect(page.getByRole("link", { name: /تنظیمات/ })).toHaveCount(0);

  // Submenus start collapsed.
  await expect(page.locator(".hbi-subnav")).toHaveCount(0);

  // Expand کالا و انبار and assert destinations.
  await openSubmenu(page, "کالا و انبار");
  const goodsSub = page.locator(".hbi-subnav").filter({ hasText: "محصولات (کاتالوگ)" });
  await expect(goodsSub).toBeVisible();
  await expect(goodsSub.locator("a.hbi-subnav-link", { hasText: "محصولات (کاتالوگ)" })).toHaveAttribute("href", "/catalog");
  await expect(goodsSub.locator("a.hbi-subnav-link", { hasText: "ورود کالا / خرید" })).toHaveAttribute("href", "/purchase");
  // Product file review is governance (ProductReviewPanel), not inventory — not in homepage menu.
  await expect(page.locator("a.hbi-subnav-link", { hasText: "بررسی پرونده کالا" })).toHaveCount(0);
  await expect(page.locator("a.hbi-nav-item, a.hbi-subnav-link, a.hbi-action-card").filter({ hasText: "ورود محصول" })).toHaveCount(0);

  // Expand مشتری و مشاوره (accordion closes previous).
  await openSubmenu(page, "مشتری و مشاوره");
  const consultSub = page.locator(".hbi-subnav").filter({ hasText: "پرونده مشتری" });
  await expect(consultSub).toBeVisible();
  await expect(consultSub.locator("a.hbi-subnav-link", { hasText: "مشاوره جدید" })).toHaveAttribute(
    "href",
    "/workspace?panel=consult"
  );
  await expect(consultSub.locator("a.hbi-subnav-link", { hasText: "پرونده مشتری" })).toHaveAttribute(
    "href",
    "/workspace?panel=profile"
  );
  await expect(consultSub.locator("a.hbi-subnav-link", { hasText: "سوابق مشاوره" })).toHaveAttribute(
    "href",
    "/workspace?panel=previous"
  );
  await expect(consultSub.locator("a.hbi-subnav-link", { hasText: "پیشنهاد محصول" })).toHaveAttribute(
    "href",
    "/recommendation"
  );
  // Accordion: کالا submenu closed.
  await expect(page.locator(".hbi-subnav").filter({ hasText: "محصولات (کاتالوگ)" })).toHaveCount(0);

  // Dashboard must not mirror the full submenu list as a second grid.
  await expect(page.locator(".hbi-more-card")).toHaveCount(0);
  await expect(page.getByRole("link", { name: "محیط کاری کامل" })).toHaveCount(0);

  // Quick actions: three daily shortcuts only.
  await expect(page.locator(".hbi-action-card")).toHaveCount(3);

  // Direct sale remains first-class and not nested under consultation.
  await page.locator('a.hbi-nav-item[href="/sales"]').click();
  await expect(page).toHaveURL(/\/sales$/);
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

test("unknown route without an Admin session redirects to login", async ({ page }) => {
  await page.goto("/this-route-does-not-exist");
  await expect(page).toHaveURL(/\/login$/);
});

test("settings are not presented as an implemented page before a real settings route exists", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "browser-test-admin-token");
  });

  await page.goto("/");
  await expect(page.getByRole("link", { name: /تنظیمات/ })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /خروج از حساب/ })).toBeVisible();
});

test("logout returns to login and protected routes remain gated", async ({ page }) => {
  // Seed token once — not via addInitScript (would re-inject after logout).
  await page.goto("/login");
  await page.evaluate(() => {
    sessionStorage.setItem("hbi_admin_access_token", "browser-test-admin-token");
  });
  await page.goto("/");
  await page.getByRole("button", { name: /خروج از حساب/ }).click();
  await expect(page).toHaveURL(/\/login$/);

  await page.goto("/accounting");
  await expect(page).toHaveURL(/\/login$/);
});


test("workspace deep links select the requested customer panel and legacy sales redirects", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "browser-test-admin-token");
  });

  await page.route("**/api/v1/products/manage", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: "[]" })
  );
  await page.route("**/api/v1/products/", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: "[]" })
  );

  await page.goto("/workspace?panel=profile");
  await expect(page.getByRole("heading", { name: "پروفایل مشتری" })).toBeVisible();

  await page.goto("/workspace?panel=consult");
  await expect(page.getByRole("heading", { name: "فرم مشاوره سریع" })).toBeVisible();

  await page.goto("/workspace?panel=sales");
  await expect(page).toHaveURL(/\\/sales$/);
  await expect(page.getByRole("heading", { name: "ثبت فروش" })).toBeVisible();
});

