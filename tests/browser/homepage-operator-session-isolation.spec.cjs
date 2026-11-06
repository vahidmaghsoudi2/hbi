const { test, expect } = require("@playwright/test");

test("Homepage keeps persisted customer recommendations when operator evaluation access returns 401", async ({ page, request }) => {
  const api = process.env.HBI_TEST_API_URL || "http://127.0.0.1:8765/api/v1";

  // Use the disposable browser-proof database's seeded customer and real API-issued
  // customer/operator tokens. The recommendation and Case are created through HBI.
  const customerTokenResponse = await request.post(`${api}/auth/pilot-token`, {
    data: { customer_id: "CUST-PILOT-1" },
  });
  expect(customerTokenResponse.status(), await customerTokenResponse.text()).toBe(200);
  const customerToken = (await customerTokenResponse.json()).access_token;

  const operatorTokenResponse = await request.post(`${api}/auth/pilot-operator-token`);
  expect(operatorTokenResponse.status(), await operatorTokenResponse.text()).toBe(200);
  const operatorToken = (await operatorTokenResponse.json()).access_token;

  await page.addInitScript(({ customerToken: customer, operatorToken: operator }) => {
    // The homepage route gate checks for an Admin session. This token is only
    // used for that UI gate; customer and operator API calls use real JWTs above.
    sessionStorage.setItem("hbi_admin_access_token", "homepage-session-isolation-admin-gate");
    sessionStorage.setItem("hbi_access_token", customer);
    sessionStorage.setItem("hbi_refresh_token", "browser-proof-refresh-placeholder");
    sessionStorage.setItem("hbi_customer_id", "CUST-PILOT-1");
    sessionStorage.setItem("hbi_operator_access_token", operator);
  }, { customerToken, operatorToken });

  let operatorFailures = 0;
  await page.route("**/recommendations/case/*/evaluations", async (route) => {
    operatorFailures += 1;
    await route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ detail: "operator session expired for acceptance test" }),
    });
  });

  // The current Home Page does not yet render Next Question (activity 32).
  // Preserve the existing Case-owned answer gate in this isolation proof by
  // recording the bounded answer before the real recommendation endpoint runs.
  let caseAnswerWrites = 0;
  await page.route("**/recommendations/generate", async (route) => {
    const payload = route.request().postDataJSON();
    const answerResponse = await request.post(
      `${api}/recommendations/next-question/${encodeURIComponent(payload.case_id)}/answer`,
      {
        headers: { Authorization: `Bearer ${customerToken}` },
        data: { question_id: "skin.primary_need.v1", answer: "sun_protection" },
      },
    );
    expect(answerResponse.status(), await answerResponse.text()).toBe(200);
    caseAnswerWrites += 1;
    await route.continue();
  });

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();
  await page.getByRole("button", { name: "ورود به مشاوره" }).click();
  await page.getByRole("button", { name: "شروع مشاوره" }).click();
  await expect(page.getByRole("heading", { name: "فرم مشاوره سریع" })).toBeVisible();

  await page.locator("#name").fill("پذیرش جداسازی نشست");
  await page.locator("#mobile").fill("09000000001");
  await page.getByText("ضدآفتاب / SPF", { exact: true }).click();
  await page.getByText("چرب", { exact: true }).click();

  const generatedResponsePromise = page.waitForResponse((response) =>
    response.request().method() === "POST" && response.url().endsWith("/recommendations/generate")
  );
  await page.getByRole("button", { name: "ثبت مراجعه + دریافت پیشنهاد" }).click();
  const generatedResponse = await generatedResponsePromise;
  expect(generatedResponse.status(), await generatedResponse.text()).toBe(200);
  const generatedRows = await generatedResponse.json();
  expect(Array.isArray(generatedRows)).toBeTruthy();

  const eligibleRows = generatedRows.filter((row) =>
    String(row.eligibility_status ?? row.eligibility ?? "").trim().toUpperCase() === "ELIGIBLE"
  );
  expect(eligibleRows.length, "The isolated HBI seed must produce at least one eligible recommendation").toBeGreaterThan(0);
  expect(caseAnswerWrites).toBe(1);

  await expect(page.getByRole("heading", { name: "نتایج ارزیابی برای اپراتور" })).toBeVisible();
  await expect(page.getByText(eligibleRows[0].product_id, { exact: true })).toBeVisible();
  await expect(page.getByText(/پیشنهاد واجد شرایط آماده است/)).toBeVisible();
  await expect(page.getByText("هنوز پیشنهادی گرفته نشده — از مشاوره شروع کنید.")).toHaveCount(0);
  await expect.poll(() => operatorFailures).toBeGreaterThan(0);

  const caseId = await page.evaluate(() => sessionStorage.getItem("hbi_case_id"));
  expect(caseId).toBeTruthy();

  // Confirm persistence and the public/internal authorization boundary against
  // the real API, independently of the browser's injected 401.
  const publicRead = await request.get(`${api}/recommendations/case/${encodeURIComponent(caseId)}`, {
    headers: { Authorization: `Bearer ${customerToken}` },
  });
  expect(publicRead.status(), await publicRead.text()).toBe(200);
  const publicRows = await publicRead.json();
  expect(publicRows.length).toBeGreaterThan(0);
  expect(publicRows.every((row) => String(row.eligibility_status ?? row.eligibility ?? "").trim().toUpperCase() === "ELIGIBLE")).toBeTruthy();
  expect(publicRows.every((row) => !Object.prototype.hasOwnProperty.call(row, "exclusion_reasons"))).toBeTruthy();
  for (const eligible of eligibleRows) {
    expect(publicRows.some((row) => row.recommendation_id === eligible.recommendation_id)).toBeTruthy();
  }

  const customerCannotReadInternal = await request.get(
    `${api}/recommendations/case/${encodeURIComponent(caseId)}/evaluations`,
    { headers: { Authorization: `Bearer ${customerToken}` } },
  );
  expect([401, 403]).toContain(customerCannotReadInternal.status());

  const operatorCanReadInternal = await request.get(
    `${api}/recommendations/case/${encodeURIComponent(caseId)}/evaluations`,
    { headers: { Authorization: `Bearer ${operatorToken}` } },
  );
  expect(operatorCanReadInternal.status(), await operatorCanReadInternal.text()).toBe(200);
  expect(Array.isArray(await operatorCanReadInternal.json())).toBeTruthy();

  // A full reload resets React state. Re-open the same consultation result panel;
  // the public recommendation must be reconstructed from the persisted Case.
  await page.reload();
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();
  await page.getByRole("button", { name: "ورود به مشاوره" }).click();
  await page.getByRole("button", { name: "مشاهده نتایج همین نشست" }).click();
  await expect(page.getByRole("heading", { name: "نتایج ارزیابی برای اپراتور" })).toBeVisible();
  await expect(page.getByText(eligibleRows[0].product_id, { exact: true })).toBeVisible();
  await expect(page.getByText("هنوز پیشنهادی گرفته نشده — از مشاوره شروع کنید.")).toHaveCount(0);
  await expect.poll(() => operatorFailures).toBeGreaterThan(1);
});
