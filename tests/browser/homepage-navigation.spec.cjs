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
  await expect(page.getByText(/الگوی صندوق فروش|فروش حضوری بدون/).first()).toBeVisible();
  await expect(page.getByText("اقلام فاکتور")).toBeVisible();
  await expect(page.getByLabel("جست‌وجوی طرف‌حساب با نام خانوادگی")).toBeVisible();
  await expect(page.locator("#sale-customer-search")).toHaveAttribute("placeholder", "نام خانوادگی…");
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

test("Browser Back and Forward restore homepage menu and panel navigation", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-browser-history-test-token");
  });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();

  await page.getByRole("button", { name: "ورود به فروش" }).click();
  await expect(page.getByRole("heading", { name: "فروش", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "بازکردن ثبت فروش" }).click();
  await expect(page.getByRole("heading", { name: "ثبت فروش" })).toBeVisible();

  await page.goBack();
  await expect(page.getByRole("heading", { name: "فروش", exact: true })).toBeVisible();
  await page.goBack();
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();

  await page.goForward();
  await expect(page.getByRole("heading", { name: "فروش", exact: true })).toBeVisible();
  await page.goForward();
  await expect(page.getByRole("heading", { name: "ثبت فروش" })).toBeVisible();
});

test("Accounting errors stay within their own sales or finance report", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-accounting-error-boundary-token");
  });
  await page.route("**/reports/sales/period/today", (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify({ sale_count: 2, revenue_toman: 1000, revenue_usd: 1 }),
  }));
  await page.route("**/reports/financial?*", (route) => route.fulfill({
    status: 503,
    contentType: "application/json",
    body: JSON.stringify({ detail: "finance fixture unavailable" }),
  }));
  await page.goto("/accounting?section=sales");
  await expect(page.getByRole("heading", { name: "فروش امروز", exact: true }).first()).toBeVisible();
  await expect(page.getByRole("alert")).toHaveCount(0);
  await page.getByRole("button", { name: "گزارش مالی" }).click();
  await expect(page.getByRole("heading", { name: "گزارش مالی عملیاتی", exact: true })).toBeVisible();
  await expect(page.getByRole("alert")).toContainText("دریافت گزارش مالی ناموفق بود.");
});

test("Inventory report errors stay local to the selected inventory section", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-inventory-error-boundary-token");
  });
  await page.route("**/reports/inventory/low-stock*", (route) => route.fulfill({
    status: 503,
    contentType: "application/json",
    body: JSON.stringify({ detail: "low-stock fixture unavailable" }),
  }));
  await page.route("**/reports/inventory", (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: "[]",
  }));
  await page.route("**/inventory/movements*", (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: "[]",
  }));
  await page.goto("/inventory?section=inventory");
  await expect(page.getByRole("heading", { name: "کالا و موجودی", exact: true })).toBeVisible();
  await expect(page.getByText("دریافت گزارش کمبود موجودی ناموفق بود.")).toHaveCount(0);
  await expect(page.getByText("دادهٔ موجودی برای نمایش وجود ندارد.")).toBeVisible();
  await page.getByRole("button", { name: "کمبود موجودی" }).click();
  await expect(page.getByText("دریافت گزارش کمبود موجودی ناموفق بود.")).toBeVisible();
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
      body: JSON.stringify([{
        customer_id: "CUS-LATE-1",
        name: "Test",
        family_name: "دیررس",
        mobile: "09000000001",
      }]),
    });
  });
  await page.goto("/");
  await page.getByRole("button", { name: "بازکردن داشبورد" }).click();
  await page.getByRole("button", { name: "جست‌وجوی مشتری" }).click();
  await page.getByLabel("جست‌وجوی مشتری قبلی با نام خانوادگی یا موبایل").fill("دیررس");
  const requestStarted = page.waitForRequest((request) => request.url().includes("/customers/search?"));
  await page.getByRole("button", { name: "جست‌وجو" }).click();
  await requestStarted;
  await page.getByRole("button", { name: "بازگشت به داشبورد" }).click();
  await page.getByRole("button", { name: "ثبت فروش" }).click();
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
    body: JSON.stringify([{
      customer_id: "CUS-SEARCH-1",
      name: "Test",
      family_name: "آزمایشی",
      mobile: "09000000000",
    }]),
  }));
  await page.goto("/");
  await page.getByRole("button", { name: "بازکردن داشبورد" }).click();
  await page.getByRole("button", { name: "جست‌وجوی مشتری" }).click();
  await page.getByLabel("جست‌وجوی مشتری قبلی با نام خانوادگی یا موبایل").fill("آزمایشی");
  await page.getByRole("button", { name: "جست‌وجو" }).click();
  await expect(page.getByText("آزمایشی", { exact: true })).toBeVisible();
  await expect(page.getByText("09000000000", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "بازگشت به داشبورد" }).click();
  await page.getByRole("button", { name: "ثبت فروش" }).click();
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
  await expect(page.getByRole("heading", { name: "داشبورد HBI", exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "گزارش فروش" })).toHaveAttribute("href", "/accounting?section=sales");
  await expect(page.getByRole("link", { name: "گزارش موجودی" })).toHaveAttribute("href", "/inventory?section=inventory");
  await expect(page.getByRole("link", { name: "کمبود موجودی", exact: true })).toHaveAttribute("href", "/inventory?section=low-stock");
  await expect(page.getByRole("link", { name: "گردش اخیر" })).toHaveAttribute("href", "/inventory?section=stock-flow");
  await expect(page.getByRole("link", { name: "بازکردن کمبود موجودی" })).toHaveAttribute("href", "/inventory?section=low-stock");
  await page.getByRole("link", { name: "کمبود موجودی", exact: true }).click();
  await expect(page).toHaveURL(/\/inventory\?section=low-stock$/);
  await expect(page.getByRole("heading", { name: "کالا و موجودی", exact: true })).toBeVisible();
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
  await expect(page.getByRole("button", { name: "ابتدا مشتری را ذخیره کنید" })).toBeDisabled();
  await page.getByRole("button", { name: "بازگشت به داشبورد" }).click();
  await expect(page.getByRole("heading", { name: "داشبورد HBI", exact: true })).toBeVisible();
});

test("A blank customer profile cannot claim to consult an existing customer", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-empty-profile-boundary-token");
  });
  await page.goto("/");
  await page.getByRole("button", { name: "ورود به مشتریان" }).click();
  await page.getByRole("button", { name: "بازکردن پروفایل مشتری" }).click();
  await expect(page.getByRole("heading", { name: "پروفایل مشتری", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "ابتدا مشتری را ذخیره کنید" })).toBeDisabled();
  await expect(page.getByRole("button", { name: "ذخیره پروفایل مشتری" })).toBeEnabled();
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

test("Admin logout is always available in the fixed header, without a fake Settings menu", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-header-logout-test-token");
  });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();

  await expect(page.getByRole("button", { name: "ورود به تنظیمات" })).toHaveCount(0);
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

test("Product menu has one canonical list plus intake and QA actions", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-product-catalog-test-token");
  });
  await page.goto("/");
  await page.getByRole("button", { name: "ورود به مدیریت محصولات" }).click();
  await expect(page.getByRole("button", { name: "بازکردن فهرست کالاها" })).toBeVisible();
  await expect(page.getByRole("button", { name: "ورود و ویرایش محصول" })).toBeVisible();
  await expect(page.getByRole("button", { name: "انتخاب محصول برای QA" })).toBeVisible();
  await expect(page.getByRole("link", { name: "بازکردن کاتالوگ هویت‌تأییدشده" })).toHaveCount(0);
  await page.getByRole("button", { name: "انتخاب محصول برای QA" }).click();
  await expect(page.getByRole("heading", { name: "محصولات", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "بازگشت به بخش" }).click();
  await expect(page.getByRole("heading", { name: "مدیریت محصولات", exact: true })).toBeVisible();
});

test("Researched P4 starter pre-fills a SKIN draft without guessing market identity or creating a record", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-p4-starter-test-token");
    sessionStorage.setItem("hbi_operator_access_token", "homepage-p4-starter-operator-token");
  });

  const productMutations = [];
  page.on("request", (request) => {
    const pathname = new URL(request.url()).pathname;
    if (request.method() !== "GET" && (pathname === "/products" || pathname.startsWith("/products/"))) {
      productMutations.push({ method: request.method(), pathname });
    }
  });

  await page.goto("/");
  await page.getByRole("button", { name: "ورود به مدیریت محصولات" }).click();
  await page.getByRole("button", { name: "ورود و ویرایش محصول" }).click();
  await page.getByRole("button", { name: "بارگذاری پیش‌نویس پژوهشی P4 · SKIN1004" }).click();

  const field = (label) => page.locator("label").filter({ hasText: label }).first().locator("..").locator("input");
  await expect(page.getByText(/DuplicateCheck/)).toBeVisible();
  await expect(page.locator("label").filter({ hasText: "product_id" })).toHaveCount(0);
  await expect(field("برند")).toHaveValue("SKIN1004");
  await expect(field("نام محصول")).toHaveValue("Madagascar Centella Hyalu-Cica Water-Fit Sun Serum");
  await expect(page.locator("#product-line-select")).toHaveValue("SKIN");
  await expect(field("منطقه بازار")).toHaveValue("");
  await expect(field("variant")).toHaveValue("");
  await expect(page.getByText(/بازار کره‌ای\/بین‌المللی و آمریکا یکسان فرض نمی‌شوند/)).toBeVisible();
  await expect(page.getByText(/این کار هنوز هیچ رکوردی ایجاد نکرده است/)).toBeVisible();
  expect(productMutations).toEqual([]);
});

test("Obsolete standalone catalog URL redirects to the homepage", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-obsolete-catalog-route-test-token");
  });
  await page.goto("/catalog");
  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "کاتالوگ محصولات با هویت تأییدشده" })).toHaveCount(0);
});
