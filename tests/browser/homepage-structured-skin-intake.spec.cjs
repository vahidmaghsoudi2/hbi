const { test, expect } = require("@playwright/test");

test("Homepage records structured skin consultation answers on the current Case before recommendation", async ({ page, request }) => {
  const api = process.env.HBI_TEST_API_URL || "http://127.0.0.1:8765/api/v1";
  const customerTokenResponse = await request.post(`${api}/auth/pilot-token`, {
    data: { customer_id: "CUST-PILOT-1" },
  });
  expect(customerTokenResponse.status(), await customerTokenResponse.text()).toBe(200);
  const customerToken = (await customerTokenResponse.json()).access_token;

  const operatorTokenResponse = await request.post(`${api}/auth/pilot-operator-token`);
  expect(operatorTokenResponse.status(), await operatorTokenResponse.text()).toBe(200);
  const operatorToken = (await operatorTokenResponse.json()).access_token;

  await page.addInitScript(({ customerToken: customer, operatorToken: operator }) => {
    sessionStorage.setItem("hbi_admin_access_token", "homepage-structured-intake-admin-gate");
    sessionStorage.setItem("hbi_access_token", customer);
    sessionStorage.setItem("hbi_refresh_token", "browser-proof-refresh-placeholder");
    sessionStorage.setItem("hbi_customer_id", "CUST-PILOT-1");
    sessionStorage.setItem("hbi_operator_access_token", operator);
  }, { customerToken, operatorToken });

  let operatorFailures = 0;
  let nextQuestionReads = 0;
  let caseAnswerWrites = 0;
  page.on("request", (req) => {
    if (!req.url().includes("/recommendations/next-question/")) return;
    if (req.method() === "GET") nextQuestionReads += 1;
    if (req.method() === "POST") caseAnswerWrites += 1;
  });

  await page.route("**/recommendations/case/*/evaluations", async (route) => {
    operatorFailures += 1;
    await route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ detail: "operator session expired for structured-intake proof" }),
    });
  });

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();
  await page.getByRole("button", { name: "ورود به مشاوره" }).click();
  await page.getByRole("button", { name: "شروع مشاوره" }).click();
  await expect(page.getByRole("heading", { name: "فرم مشاوره سریع" })).toBeVisible();

  await page.locator("#name").fill("پذیرش جداسازی نشست");
  await page.locator("#mobile").fill("09000000001");
  await page.getByText("محافظت در برابر آفتاب", { exact: true }).click();
  await page.getByText("چرب", { exact: true }).click();
  await page.locator("#consult-duration").selectOption("one_to_four_weeks");
  await page.locator("#consult-severity").selectOption("moderate");
  await page.locator("#consult-area").selectOption("face");
  await page.getByText("آفتاب", { exact: true }).click();
  await page.locator("#consult-product-history").fill("ضدآفتاب قبلی؛ خشکی گزارش‌شده");
  await page.locator("#consult-additional-context").fill("توضیح ثبت‌شده توسط مشتری در همین مراجعه");

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
  expect(eligibleRows.length).toBeGreaterThan(0);

  // One initial GET + one GET after each of the eight Case-owned answers.
  expect(nextQuestionReads).toBe(9);
  expect(caseAnswerWrites).toBe(8);
  await expect(page.getByRole("heading", { name: "نتایج ارزیابی برای اپراتور" })).toBeVisible();
  await expect(page.getByRole("heading", { name: eligibleRows[0].product_id })).toBeVisible();
  await expect.poll(() => operatorFailures).toBeGreaterThan(0);

  const caseId = await page.evaluate(() => sessionStorage.getItem("hbi_case_id"));
  expect(caseId).toBeTruthy();

  const caseRead = await request.get(`${api}/cases/customer/CUST-PILOT-1`, {
    headers: { Authorization: `Bearer ${customerToken}` },
  });
  expect(caseRead.status(), await caseRead.text()).toBe(200);
  const cases = await caseRead.json();
  const savedCase = cases.find((item) => item.case_id === caseId);
  expect(savedCase).toBeTruthy();
  const evidenceState = JSON.parse(savedCase.evidence_gaps);
  const answerMap = new Map(evidenceState.answers.map((item) => [item.question_id, item]));
  const expected = {
    "skin.primary_need.v1": "sun_protection",
    "skin.current_type.v1": "چرب",
    "skin.duration.v1": "one_to_four_weeks",
    "skin.self_reported_severity.v1": "moderate",
    "skin.affected_area.v1": "face",
    "skin.aggravating_factors.v1": "sun_exposure",
    "skin.product_history.v1": "ضدآفتاب قبلی؛ خشکی گزارش‌شده",
    "skin.additional_context.v1": "توضیح ثبت‌شده توسط مشتری در همین مراجعه",
  };
  for (const [questionId, value] of Object.entries(expected)) {
    expect(answerMap.get(questionId)?.value).toBe(value);
    expect(answerMap.get(questionId)?.source).toBe("CURRENT_CASE_CONSULTATION");
  }

  const nextQuestion = await request.get(
    `${api}/recommendations/next-question/${encodeURIComponent(caseId)}`,
    { headers: { Authorization: `Bearer ${customerToken}` } },
  );
  expect(nextQuestion.status(), await nextQuestion.text()).toBe(200);
  expect((await nextQuestion.json()).status).toBe("NO_QUESTION");

  const publicRead = await request.get(`${api}/recommendations/case/${encodeURIComponent(caseId)}`, {
    headers: { Authorization: `Bearer ${customerToken}` },
  });
  expect(publicRead.status(), await publicRead.text()).toBe(200);
  const publicRows = await publicRead.json();
  expect(publicRows.length).toBeGreaterThan(0);
  expect(publicRows.every((row) => String(row.eligibility_status ?? row.eligibility ?? "").trim().toUpperCase() === "ELIGIBLE")).toBeTruthy();

  const internalRead = await request.get(
    `${api}/recommendations/case/${encodeURIComponent(caseId)}/evaluations`,
    { headers: { Authorization: `Bearer ${customerToken}` } },
  );
  expect([401, 403]).toContain(internalRead.status());

  await page.reload();
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();
  await page.getByRole("button", { name: "ورود به مشاوره" }).click();
  await page.getByRole("button", { name: "مشاهده نتایج همین نشست" }).click();
  await expect(page.getByRole("heading", { name: "نتایج ارزیابی برای اپراتور" })).toBeVisible();
  await expect(page.getByRole("heading", { name: eligibleRows[0].product_id })).toBeVisible();
  await expect.poll(() => operatorFailures).toBeGreaterThan(1);
});
