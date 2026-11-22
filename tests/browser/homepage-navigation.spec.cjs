const { test, expect } = require("@playwright/test");

test("Homepage requires the Admin session before exposing the workspace", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("heading", { name: "ورود مدیر HBI" })).toBeVisible();
});

test("Pilot and recommendation routes require the Admin/Operator session", async ({ page }) => {
  for (const path of ["/pilot", "/recommendation"]) {
    await page.goto(path);
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole("heading", { name: "ورود مدیر HBI" })).toBeVisible();
  }
});

test("Homepage navigation keeps sales, inventory, and reports in their own destinations", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-navigation-test-token");
  });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();
  await page.getByRole("button", { name: "ورود به فروش" }).click();
  await expect(page.getByRole("heading", { name: "فروش", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "بازکردن ثبت فروش" }).click();
  await expect(page.getByRole("heading", { name: "ثبت فروش" })).toBeVisible();
  await page.getByRole("button", { name: "بازگشت به بخش" }).click();
  await page.getByRole("button", { name: "منوی اصلی" }).click();
  await page.getByRole("button", { name: "ورود به کالا و موجودی" }).click();
  await expect(page.getByRole("link", { name: "بازکردن کمبود موجودی" })).toHaveAttribute("href", "/inventory?section=low-stock");
  await page.getByRole("link", { name: "بازکردن کمبود موجودی" }).click();
  await expect(page).toHaveURL(/\/inventory\?section=low-stock$/);
  await page.getByRole("link", { name: "بازگشت به خانه HBI" }).click();
  await page.getByRole("button", { name: "ورود به حسابداری و گزارش‌ها" }).click();
  await expect(page.getByRole("heading", { name: "حسابداری و گزارش‌ها", exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "بازکردن گزارش فروش" })).toBeVisible();
  await expect(page.getByRole("link", { name: "بازکردن گزارش موجودی" })).toHaveCount(0);
});

test("An in-flight customer search cannot repopulate another panel", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-inflight-search-boundary-token");
    sessionStorage.setItem("hbi_operator_access_token", "homepage-operator-inflight-search-token");
  });
  let releaseSearch;
  const holdSearch = new Promise((resolve) => { releaseSearch = resolve; });
  await page.route("**/customers/search**", async (route) => {
    await holdSearch;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([{ customer_id: "CUS-LATE-1", name: "Test", family_name: "دیررس", mobile: "09000000001" }]),
    });
  });
  await page.goto("/");
  await page.getByRole("button", { name: "ورود به مشتریان" }).click();
  await page.getByRole("button", { name: "بازکردن جست‌وجوی مشتری" }).click();
  await page.getByLabel("جست‌وجوی مشتری قبلی با نام خانوادگی یا موبایل").fill("دیررس");
  const requestStarted = page.waitForRequest((request) => request.url().includes("/customers/search?"));
  await page.getByRole("button", { name: "جست‌وجو" }).click();
  await requestStarted;
  await page.getByRole("button", { name: "بازگشت به بخش" }).click();
  await page.getByRole("button", { name: "منوی اصلی" }).click();
  await page.getByRole("button", { name: "ورود به فروش" }).click();
  await page.getByRole("button", { name: "بازکردن ثبت فروش" }).click();
  const responseReceived = page.waitForResponse((response) => response.url().includes("/customers/search?"));
  releaseSearch();
  await responseReceived;
  await expect(page.getByRole("heading", { name: "ثبت فروش" })).toBeVisible();
  await expect(page.getByRole("button", { name: /CUS-LATE-1/ })).toHaveCount(0);
});

test("Customer search results do not leak into the optional sale-account picker", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-search-boundary-test-token");
    sessionStorage.setItem("hbi_operator_access_token", "homepage-operator-search-test-token");
  });
  await page.route("**/customers/search**", (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify([{ customer_id: "CUS-SEARCH-1", name: "Test", family_name: "آزمایشی", mobile: "09000000000" }]),
  }));
  await page.goto("/");
  await page.getByRole("button", { name: "ورود به مشتریان" }).click();
  await page.getByRole("button", { name: "بازکردن جست‌وجوی مشتری" }).click();
  await page.getByLabel("جست‌وجوی مشتری قبلی با نام خانوادگی یا موبایل").fill("آزمایشی");
  await page.getByRole("button", { name: "جست‌وجو" }).click();
  await expect(page.getByText("آزمایشی", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "بازگشت به بخش" }).click();
  await page.getByRole("button", { name: "منوی اصلی" }).click();
  await page.getByRole("button", { name: "ورود به فروش" }).click();
  await page.getByRole("button", { name: "بازکردن ثبت فروش" }).click();
  await expect(page.getByRole("heading", { name: "ثبت فروش" })).toBeVisible();
  await expect(page.getByRole("button", { name: /CUS-SEARCH-1/ })).toHaveCount(0);
});

test("Dashboard report shortcuts preserve their own report destinations", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-dashboard-links-test-token");
  });
  await page.route("**/reports/inventory/low-stock*", (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify([{ inventory_id: "INV-LOW-1", product_id: "P-LOW-1", quantity_available: 2 }]),
  }));
  await page.goto("/");
  await page.getByRole("button", { name: "بازکردن داشبورد" }).click();
  await expect(page.getByRole("heading", { name: "صفحه اول (داشبورد) - نمای کلی", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "وضعیت عملیات" })).toBeVisible();
  await expect(page.getByRole("link", { name: "بازکردن کمبود موجودی" })).toHaveAttribute("href", "/inventory?section=low-stock");
  await expect(page.getByRole("link", { name: "مشاهده همه گردش‌ها" })).toHaveAttribute("href", "/inventory?section=stock-flow");
  await page.getByRole("link", { name: "بازکردن کمبود موجودی" }).click();
  await expect(page).toHaveURL(/\/inventory\?section=low-stock$/);
  await expect(page.getByRole("heading", { name: "کمبود موجودی", exact: true })).toBeVisible();
});

test("Dashboard New customer action clears the previously active customer", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-new-customer-reset-token");
    sessionStorage.setItem("hbi_customer_id", "CUS-OLD-1");
    sessionStorage.setItem("hbi_access_token", "old-customer-token");
    sessionStorage.setItem("hbi_refresh_token", "old-customer-refresh");
  });
  await page.goto("/");
  await page.getByRole("button", { name: "بازکردن داشبورد" }).click();
  await page.getByRole("button", { name: "مشتری جدید" }).click();
  await expect(page.getByRole("heading", { name: "پروفایل مشتری", exact: true })).toBeVisible();
  await expect(page.getByText("CUS-OLD-1", { exact: true })).toHaveCount(0);
  await page.getByRole("button", { name: "بازگشت به داشبورد" }).click();
  await expect(page.getByRole("heading", { name: "صفحه اول (داشبورد) - نمای کلی", exact: true })).toBeVisible();
});

test("Customer search stays in customers domain and does not auto-start consultation", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-customer-boundary-test-token");
  });
  await page.goto("/");
  await page.getByRole("button", { name: "ورود به مشتریان" }).click();
  await expect(page.getByRole("heading", { name: "مشتریان", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "بازکردن جست‌وجوی مشتری" }).click();
  await expect(page.getByRole("heading", { name: "مشتری قبلی / جست‌وجو" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "فرم مشاوره سریع" })).toHaveCount(0);
});

test("Admin logout button is removed from the homepage (HP-05)", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-header-logout-test-token");
  });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();
  await expect(page.getByRole("button", { name: "ورود به تنظیمات" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "خروج از حساب مدیر" })).toHaveCount(0);
});

test("Dashboard quick actions stay limited to sale, consultation, new customer, and purchase", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-dashboard-actions-test-token");
  });
  await page.goto("/");
  await page.getByRole("button", { name: "بازکردن داشبورد" }).click();
  await expect(page.getByRole("heading", { name: "صفحه اول (داشبورد) - نمای کلی", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "وضعیت عملیات" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "میانبرهای عملیات سریع" })).toBeVisible();
  await expect(page.getByRole("button", { name: "ثبت فروش" })).toBeVisible();
  await expect(page.getByRole("button", { name: "شروع مشاوره" })).toBeVisible();
  await expect(page.getByRole("button", { name: "مشتری جدید" })).toBeVisible();
  await expect(page.getByRole("link", { name: "بازکردن خرید" })).toBeVisible();
  await expect(page.getByRole("button", { name: "جست‌وجوی مشتری" })).toHaveCount(0);
  await page.getByRole("button", { name: "ثبت فروش" }).click();
  await expect(page.getByRole("heading", { name: "ثبت فروش", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "بازگشت به داشبورد" }).click();
  await page.getByRole("button", { name: "شروع مشاوره" }).click();
  await expect(page.getByRole("heading", { name: "فرم مشاوره سریع" })).toBeVisible();
});

test("Product menu uses list as primary entry without independent QA menu", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-product-catalog-test-token");
  });
  await page.goto("/");
  await page.getByRole("button", { name: "ورود به مدیریت محصولات" }).click();
  await expect(page.getByRole("button", { name: "بازکردن فهرست کالاها" })).toBeVisible();
  await expect(page.getByRole("button", { name: "شروع ورود محصول" })).toBeVisible();
  await expect(page.getByRole("button", { name: "انتخاب محصول برای QA" })).toHaveCount(0);
});
