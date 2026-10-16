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
  await expect(page.getByRole("button", { name: "بازگشت به بخش" })).toHaveCount(0);
  await page.getByRole("button", { name: "بازکردن ثبت فروش" }).click();
  await expect(page.getByRole("button", { name: "بازگشت به بخش" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "ثبت فروش" })).toBeVisible();
  await expect(page.getByText(/ثبت فروش مستقیم بدون مشاوره/)).toBeVisible();
  await expect(page.locator("#sale-product")).toBeVisible();
  // The product picker must either offer real options or explain why it is empty.
  const productOptionCount = await page.locator("#sale-product option").count();
  if (productOptionCount <= 1) {
    await expect(page.getByRole("status")).toBeVisible();
  }
  await page.getByRole("button", { name: "بازگشت به بخش" }).click();
  await expect(page.getByRole("heading", { name: "فروش", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "منوی اصلی" }).click();

  // Inventory must open the inventory report, not silently land on today's sales.
  await page.getByRole("button", { name: "ورود به کالا و موجودی" }).click();
  await expect(page.getByRole("link", { name: "بازکردن کمبود موجودی" })).toHaveAttribute("href", "/inventory?section=low-stock");
  await page.getByRole("link", { name: "بازکردن کمبود موجودی" }).click();
  await expect(page).toHaveURL(/\/inventory\?section=low-stock$/);
  await expect(page.getByRole("heading", { name: "کمبود موجودی", exact: true })).toBeVisible();
  await page.getByRole("link", { name: "بازگشت به خانه HBI" }).click();
  await page.getByRole("button", { name: "ورود به کالا و موجودی" }).click();
  await page.getByRole("link", { name: "بازکردن گزارش موجودی" }).click();
  await expect(page).toHaveURL(/\/inventory\?section=inventory$/);
  await expect(page.getByRole("heading", { name: "کالا و موجودی", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "گردش کالا" }).click();
  await expect(page.getByRole("heading", { name: "گردش کالا", exact: true })).toBeVisible();

  // Accounting owns sales/finance reports only; inventory stays in کالا و موجودی.
  await page.getByRole("link", { name: "بازگشت به خانه HBI" }).click();
  await page.getByRole("button", { name: "ورود به حسابداری و گزارش‌ها" }).click();
  await expect(page.getByRole("heading", { name: "حسابداری و گزارش‌ها", exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "بازکردن گزارش فروش" })).toBeVisible();
  await expect(page.getByRole("link", { name: "بازکردن گزارش مالی" })).toBeVisible();
  await expect(page.getByRole("link", { name: "بازکردن گزارش موجودی" })).toHaveCount(0);
  await expect(page.getByRole("link", { name: "بازکردن گردش کالا" })).toHaveCount(0);
  await page.getByRole("link", { name: "بازکردن گزارش فروش" }).click();
  await expect(page).toHaveURL(/\/accounting\?section=sales$/);
  await expect(page.getByRole("heading", { name: "حسابداری و گزارش‌ها", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "فروش امروز", exact: true }).first()).toBeVisible();
});

test("Dashboard report shortcuts preserve their own report destinations", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-dashboard-links-test-token");
  });
  await page.route("**/reports/inventory/low-stock?threshold=5", (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify([{ inventory_id: "INV-LOW-1", product_id: "P-LOW-1", quantity_available: 2 }]),
  }));
  await page.goto("/");
  await page.getByRole("button", { name: "بازکردن داشبورد" }).click();
  await expect(page.getByRole("heading", { name: "داشبورد HBI", exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "گزارش فروش" })).toHaveAttribute("href", "/accounting?section=sales");
  await expect(page.getByRole("link", { name: "گزارش موجودی" })).toHaveAttribute("href", "/inventory?section=inventory");
  await expect(page.getByRole("link", { name: "کمبود موجودی" })).toHaveAttribute("href", "/inventory?section=low-stock");
  await expect(page.getByRole("link", { name: "گردش اخیر" })).toHaveAttribute("href", "/inventory?section=stock-flow");
  await expect(page.getByRole("link", { name: "بازکردن کمبود موجودی" })).toHaveAttribute("href", "/inventory?section=low-stock");
  await page.getByRole("link", { name: "کمبود موجودی" }).click();
  await expect(page).toHaveURL(/\/inventory\?section=low-stock$/);
  await expect(page.getByRole("heading", { name: "کالا و موجودی", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "کمبود موجودی", exact: true })).toBeVisible();
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
  await expect(page.getByPlaceholder("نام خانوادگی یا شماره موبایل مشتری…")).toBeVisible();
  // Consultation form must not appear until the operator explicitly opens consultation.
  await expect(page.getByRole("heading", { name: "فرم مشاوره سریع" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "ثبت مراجعه + دریافت پیشنهاد" })).toHaveCount(0);
});

test("Consultation actions stay focused on the customer problem and recommendation flow", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-consultation-boundary-test-token");
  });
  await page.goto("/");
  await page.getByRole("button", { name: "ورود به مشاوره" }).click();
  await page.getByRole("button", { name: "شروع مشاوره" }).click();
  await expect(page.getByRole("heading", { name: "فرم مشاوره سریع" })).toBeVisible();
  await expect(page.getByRole("button", { name: "ثبت مراجعه + دریافت پیشنهاد" })).toBeVisible();
  await expect(page.getByRole("button", { name: "محصولات", exact: true })).toHaveCount(0);
  await page.getByRole("button", { name: "بازگشت به بخش" }).click();
  await expect(page.getByRole("heading", { name: "نتایج مشاوره جاری" })).toBeVisible();
  await page.getByRole("button", { name: "مشاهده نتایج همین نشست" }).click();
  await expect(page.getByRole("heading", { name: "نتایج ارزیابی برای اپراتور" })).toBeVisible();
  await expect(page.getByText("هنوز پیشنهادی گرفته نشده — از مشاوره شروع کنید.")).toBeVisible();
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


test("Purchase navigation returns to inventory, not accounting", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-purchase-navigation-test-token");
  });
  await page.goto("/");
  await page.getByRole("button", { name: "ورود به خرید" }).click();
  await page.getByRole("link", { name: "بازکردن خرید و موجودی" }).click();
  await expect(page).toHaveURL(/\/purchase$/);
  await expect(page.getByRole("heading", { name: "خرید \/ ورود کالا" })).toBeVisible();
  await expect(page.getByRole("link", { name: "کالا و موجودی" })).toHaveAttribute("href", "/inventory?section=inventory");
  await expect(page.getByRole("link", { name: "حسابداری" })).toHaveCount(0);
});

test("Accounting deep-links stay on sales and finance sections", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-accounting-test-token");
  });
  await page.goto("/accounting?section=finance-report");
  await expect(page.getByRole("heading", { name: "حسابداری و گزارش‌ها", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "گزارش مالی عملیاتی", exact: true })).toBeVisible();
  await expect(page.getByText("COGS", { exact: true })).toBeVisible();
  await expect(page.getByText("DEFERRED BY PO").first()).toBeVisible();
  // Inventory is not an accounting destination.
  await expect(page.getByRole("heading", { name: "موجودی کالا", exact: true })).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "گردش کالا", exact: true })).toHaveCount(0);
});

test("Dashboard quick actions stay limited to sale, customers, and consultation", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-dashboard-actions-test-token");
  });
  await page.goto("/");
  await page.getByRole("button", { name: "بازکردن داشبورد" }).click();
  await expect(page.getByRole("heading", { name: "داشبورد HBI", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "اقدام سریع" })).toBeVisible();
  await expect(page.getByRole("button", { name: "ثبت فروش" })).toBeVisible();
  await expect(page.getByRole("button", { name: "جست‌وجوی مشتری" })).toBeVisible();
  await expect(page.getByRole("button", { name: "شروع مشاوره" })).toBeVisible();
  await page.getByRole("button", { name: "ثبت فروش" }).click();
  await expect(page.getByRole("heading", { name: "ثبت فروش", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "بازگشت به داشبورد" }).click();
  await expect(page.getByRole("heading", { name: "داشبورد HBI", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "شروع مشاوره" }).click();
  await expect(page.getByRole("heading", { name: "فرم مشاوره سریع" })).toBeVisible();
  await page.getByRole("button", { name: "بازگشت به داشبورد" }).click();
  await expect(page.getByRole("heading", { name: "داشبورد HBI", exact: true })).toBeVisible();
  // Product intake / purchase / QA are not dashboard quick actions.
  await expect(page.getByRole("button", { name: "ورود و ویرایش محصول" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "بازکردن بررسی QA" })).toHaveCount(0);
  await expect(page.getByRole("link", { name: "بازکردن خرید و موجودی" })).toHaveCount(0);
});

test("Settings does not invent extra configuration and keeps logout owned there", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-settings-boundary-test-token");
  });
  await page.goto("/");
  await page.getByRole("button", { name: "ورود به تنظیمات" }).click();
  await expect(page.getByRole("heading", { name: "تنظیمات", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "حساب مدیر" })).toBeVisible();
  await expect(page.getByText(/تنظیمات عملیاتی دیگری در این بخش هنوز تعریف نشده/)).toBeVisible();
  await expect(page.getByRole("button", { name: "خروج از حساب مدیر" })).toBeVisible();
});

test("Product menu exposes the managed list and the separate approved catalog route", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-product-catalog-test-token");
  });
  await page.goto("/");
  await page.getByRole("button", { name: "ورود به مدیریت محصولات" }).click();
  await expect(page.getByRole("button", { name: "بازکردن فهرست مدیریتی" })).toBeVisible();
  await expect(page.getByRole("button", { name: "ورود و ویرایش محصول" })).toBeVisible();
  await expect(page.getByRole("button", { name: "انتخاب محصول برای QA" })).toBeVisible();
  await page.getByRole("button", { name: "انتخاب محصول برای QA" }).click();
  await expect(page.getByRole("heading", { name: "محصولات", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "بازگشت به بخش" }).click();
  await page.getByRole("link", { name: "بازکردن کاتالوگ هویت‌تأییدشده" }).click();
  await expect(page).toHaveURL(/\/catalog$/);
  await expect(page.getByRole("heading", { name: "کاتالوگ محصولات با هویت تأییدشده", exact: true })).toBeVisible();
  await page.getByRole("link", { name: "بازگشت به منوی اصلی" }).click();
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();
});
