const { test, expect } = require("@playwright/test");

const previewResponse = (overrides = {}) => ({
  view_version: "1",
  audience: "INTERNAL_REVIEW_ONLY",
  data_class: "SYNTHETIC_ONLY",
  case: {
    case_id: "SYNTHETIC-ROW69-BROWSER-001",
    case_version: "case-v1",
    goal_version: "goal-v1",
    service_kind: "CATALOG_READY",
  },
  decision: {
    status: "CONTEXT_READY_FOR_CATALOG_IDENTITY_REASONING",
    reason_code: "SYNTHETIC_CATALOG_CONTEXT_READY",
    summary_fa: "زمینهٔ مصنوعی برای بررسی هویت کاتالوگی آماده است.",
    recommendation: null,
    display_allowed: false,
    client_visible: false,
  },
  evidence: [{
    evidence_id: "EV-SYNTHETIC-BROWSER-001",
    source_type: "APPROVED_CATALOG_SNAPSHOT",
    source_reference: "synthetic://catalog/snapshot-001",
    qa_status: "VERIFIED",
  }],
  lineage: {
    run_id: "SYNTHETIC-RUN-BROWSER-001",
    knowledge_package_id: "HBI-HAIR-CATALOG",
    knowledge_package_version: "v1",
    rule_id: "HAIR-CATALOG-IDENTITY",
    rule_version: "v1",
    snapshot_id: "SYNTHETIC-SNAPSHOT-001",
    content_sha256: "a".repeat(64),
    engine_version: "synthetic-engine-v1",
    dependencies: [{ kind: "CATALOG", dependency_id: "SYNTHETIC-CATALOG", version: "v1" }],
    persistence: "COMPUTED_ONLY",
  },
  review_controls: {
    specialist_review_required_by_this_slice: false,
    specialist_review_recorded: false,
    acceptance_inherited: false,
    execution_consent_inherited: false,
    available_actions: [],
  },
  limitations: [
    "این خروجی فقط زمینهٔ مصنوعی است.",
    "پیشنهاد رنگ و مجوز اجرا تولید نمی‌شود.",
  ],
  ...overrides,
});

async function openPreview(page) {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "synthetic-hair-preview-browser-token");
  });
  await page.goto("/hair/specialist-preview");
  await expect(page.getByRole("heading", { name: "پیش‌نمایش داخلی متخصص" })).toBeVisible();
}

test("specialist preview route remains behind the Admin session gate", async ({ page }) => {
  await page.goto("/hair/specialist-preview");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("heading", { name: "ورود مدیر HBI" })).toBeVisible();
});

test("specialist preview renders the five response types and four independent motor states", async ({ page }) => {
  await openPreview(page);
  const contract = page.getByRole("region", { name: "قرارداد انواع پاسخ و حالت موتور" });
  await expect(contract.getByRole("heading", { name: "پنج نوع پاسخ مشاوره" })).toBeVisible();
  await expect(contract.locator("li")).toHaveCount(9);
  await expect(contract.getByText("CONDITIONAL_SUGGESTION")).toBeVisible();
  await expect(contract.getByText("پیشنهاد مشروط» حالت موتور است و نوع پاسخ ششم محسوب نمی‌شود.")).toBeVisible();
  await expect(contract.getByText("تعیین و احراز صلاحیت متخصص بر عهدهٔ Product Owner است؛ سامانه در این برش صلاحیت حرفه‌ای اشخاص را مستقلاً ارزیابی نمی‌کند.")).toBeVisible();
});

test("specialist preview submits only synthetic context and renders evidence, lineage and limits", async ({ page }) => {
  await openPreview(page);
  let submitted = null;
  await page.route("**/api/v1/hair/specialist-preview", async (route) => {
    submitted = route.request().postDataJSON();
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(previewResponse()),
    });
  });

  await page.getByLabel("شناسهٔ پروندهٔ مصنوعی").fill("SYNTHETIC-ROW69-BROWSER-001");
  await page.getByLabel("نسخهٔ پرونده").fill("case-v3");
  await page.getByLabel("نسخهٔ هدف").fill("goal-v4");
  await page.getByRole("button", { name: "ساخت پیش‌نمایش مصنوعی" }).click();

  await expect(page.getByRole("heading", { name: "وضعیت بررسی" })).toBeVisible();
  await expect(page.getByText("SYNTHETIC-ROW69-BROWSER-001")).toBeVisible();
  await expect(page.getByText("EV-SYNTHETIC-BROWSER-001")).toBeVisible();
  await expect(page.getByText("SYNTHETIC-RUN-BROWSER-001")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Lineage و نسخه‌ها" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "محدودیت‌های این خروجی" })).toBeVisible();
  await expect(page.getByText("پیشنهاد رنگ", { exact: true })).toBeVisible();
  await expect(page.getByText("ارائه نشده", { exact: true })).toBeVisible();
  await expect(page.getByText("مجوز اجرای خدمت", { exact: true })).toBeVisible();

  expect(submitted).toEqual({
    case_id: "SYNTHETIC-ROW69-BROWSER-001",
    case_version: "case-v3",
    goal_version: "goal-v4",
    service_kind: "CATALOG_READY",
    catalog_identity: {
      brand: "بیجورکا",
      series: "طبیعی",
      shade_number: "۱",
      shade_name: "مشکی",
      product_specification: null,
      product_volume: null,
    },
  });
});

test("browser form blocks non-synthetic case identifiers before an API request", async ({ page }) => {
  await openPreview(page);
  let requestCount = 0;
  await page.route("**/api/v1/hair/specialist-preview", async (route) => {
    requestCount += 1;
    await route.fulfill({ status: 422, contentType: "application/json", body: JSON.stringify({ detail: "synthetic only" }) });
  });

  await page.getByLabel("شناسهٔ پروندهٔ مصنوعی").fill("REAL-CLIENT-001");
  await page.getByRole("button", { name: "ساخت پیش‌نمایش مصنوعی" }).click();
  await expect(page.getByLabel("شناسهٔ پروندهٔ مصنوعی")).toHaveJSProperty("validity.valid", false);
  await expect(page.getByRole("heading", { name: "وضعیت بررسی" })).toHaveCount(0);
  expect(requestCount).toBe(0);
});

test("specialist preview keeps out-of-scope service as a visible stop with no recommendation", async ({ page }) => {
  await openPreview(page);
  await page.route("**/api/v1/hair/specialist-preview", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(previewResponse({
        case: {
          case_id: "SYNTHETIC-ROW69-BROWSER-001",
          case_version: "case-v1",
          goal_version: "goal-v1",
          service_kind: "OUT_OF_SCOPE",
        },
        decision: {
          status: "STOP_OUT_OF_DOMAIN",
          reason_code: "SERVICE_OUT_OF_SCOPE",
          summary_fa: "این نوع خدمت خارج از دامنه است.",
          recommendation: null,
          display_allowed: false,
          client_visible: false,
        },
      })),
    });
  });

  await page.getByLabel("نوع خدمت").selectOption("COMBINATION_CONSULT");
  await page.getByRole("button", { name: "ساخت پیش‌نمایش مصنوعی" }).click();
  await expect(page.getByText("STOP_OUT_OF_DOMAIN")).toBeVisible();
  await expect(page.getByText("این نوع خدمت خارج از دامنه است.")).toBeVisible();
  await expect(page.getByText("ارائه نشده", { exact: true })).toBeVisible();
  await expect(page.getByText("ممنوع", { exact: true })).toBeVisible();
});

test("specialist preview API failure is contained and does not display stale output", async ({ page }) => {
  await openPreview(page);
  await page.route("**/api/v1/hair/specialist-preview", async (route) => {
    await route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({ detail: "synthetic preview unavailable" }),
    });
  });

  await page.getByRole("button", { name: "ساخت پیش‌نمایش مصنوعی" }).click();
  await expect(page.getByRole("alert")).toContainText("پیش‌نمایش دریافت نشد.");
  await expect(page.getByRole("alert")).toContainText("HTTP 503");
  await expect(page.getByRole("heading", { name: "وضعیت بررسی" })).toHaveCount(0);
});
