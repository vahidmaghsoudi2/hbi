const { test, expect } = require("@playwright/test");

test("Homepage persists the structured skin intake on the current Case", async ({ page, request }) => {
  const api = process.env.HBI_TEST_API_URL || "http://127.0.0.1:8765/api/v1";
  const mobile = `0913${String(Date.now()).slice(-7)}`;
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-structured-intake-admin-gate");
  });

  let questionReads = 0;
  let answerWrites = 0;
  page.on("request", (req) => {
    if (!req.url().includes("/recommendations/next-question/")) return;
    if (req.method() === "GET") questionReads += 1;
    if (req.method() === "POST") answerWrites += 1;
  });

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();
  await page.getByRole("button", { name: "ورود به مشاوره" }).click();
  await page.getByRole("button", { name: "شروع مشاوره" }).click();
  await expect(page.getByRole("heading", { name: "فرم مشاوره سریع" })).toBeVisible();

  await page.locator("#name").fill("Home Page Structured Intake E2E");
  await page.locator("#mobile").fill(mobile);
  await page.getByText("ضدآفتاب / SPF", { exact: true }).click();
  await page.getByText("چرب", { exact: true }).click();
  await page.locator("#consult-duration").selectOption("one_to_four_weeks");
  await page.locator("#consult-severity").selectOption("moderate");
  await page.locator("#consult-area").selectOption("face");
  await page.getByText("آفتاب", { exact: true }).click();
  await page.locator("#consult-product-history").fill("ضدآفتاب قبلی؛ خشکی گزارش‌شده");
  await page.locator("#consult-additional-context").fill("توضیح همین مراجعه");

  const generatedPromise = page.waitForResponse((response) =>
    response.request().method() === "POST" && response.url().endsWith("/recommendations/generate")
  );
  await page.getByRole("button", { name: "ثبت مراجعه + دریافت پیشنهاد" }).click();
  const generated = await generatedPromise;
  expect(generated.status(), await generated.text()).toBe(200);

  expect(questionReads).toBe(9);
  expect(answerWrites).toBe(8);

  const session = await page.evaluate(() => ({
    caseId: sessionStorage.getItem("hbi_case_id"),
    customerId: sessionStorage.getItem("hbi_customer_id"),
    accessToken: sessionStorage.getItem("hbi_access_token"),
  }));
  const { caseId, customerId, accessToken } = session;
  expect(caseId).toBeTruthy();
  expect(customerId).toBeTruthy();
  expect(accessToken).toBeTruthy();
  const casesResponse = await request.get(`${api}/cases/customer/${encodeURIComponent(customerId)}`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  expect(casesResponse.status(), await casesResponse.text()).toBe(200);
  const cases = await casesResponse.json();
  const savedCase = cases.find((item) => item.case_id === caseId);
  expect(savedCase).toBeTruthy();

  const state = JSON.parse(savedCase.evidence_gaps);
  const answers = new Map(state.answers.map((item) => [item.question_id, item]));
  const expected = new Map([
    ["skin.primary_need.v2", ["ضدآفتاب"]],
    ["skin.current_type.v1", ["چرب"]],
    ["skin.duration.v1", "one_to_four_weeks"],
    ["skin.self_reported_severity.v1", "moderate"],
    ["skin.affected_area.v1", "face"],
    ["skin.aggravating_factors.v1", ["sun_exposure"]],
    ["skin.product_history.v1", "ضدآفتاب قبلی؛ خشکی گزارش‌شده"],
    ["skin.additional_context.v1", "توضیح همین مراجعه"],
  ]);
  for (const [questionId, value] of expected) {
    expect(answers.get(questionId)?.value).toEqual(value);
    expect(answers.get(questionId)?.source).toBe("CURRENT_CASE_CONSULTATION");
  }

  const next = await request.get(`${api}/recommendations/next-question/${encodeURIComponent(caseId)}`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  expect(next.status(), await next.text()).toBe(200);
  expect((await next.json()).status).toBe("NO_QUESTION");
});
