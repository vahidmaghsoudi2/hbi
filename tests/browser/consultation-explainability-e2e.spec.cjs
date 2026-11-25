const { test, expect } = require("@playwright/test");

test("Stage 9-14 E2E: consultation context persists through explainable output", async ({ page, request }) => {
  // The browser workflow uses only the isolated disposable SQLite fixture.
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "stage15-16-browser-proof-admin-gate-token");
  });

  const api = process.env.HBI_TEST_API_URL || "http://127.0.0.1:8765/api/v1";
  const consultationSaveRequests = [];
  page.on("request", (req) => {
    if (req.method() === "PUT" && /\/cases\/[^/]+\/consultation$/.test(new URL(req.url()).pathname)) {
      consultationSaveRequests.push(req);
    }
  });

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();
  await page.getByRole("button", { name: "ورود به مشاوره" }).click();
  await page.getByRole("button", { name: "شروع مشاوره" }).click();
  await expect(page.getByRole("heading", { name: "فرم مشاوره سریع" })).toBeVisible();

  await page.locator("#name").fill("Stage 15 E2E Customer");
  await page.locator("#mobile").fill("09120000015");
  await page.getByLabel("لک و تیرگی").check();
  await page.locator("#affected-areas").fill("گونه");
  await page.locator("#symptom-duration").fill("سه هفته");
  await page.locator("#symptom-severity").selectOption("6");
  await page.locator("#aggravating-factors").fill("آفتاب");
  await page.locator("#current-products").fill("شوینده ملایم");
  await page.locator("fieldset").filter({ has: page.getByText("۶) توضیحات تکمیلی") }).locator("textarea").fill("یادداشت آزمون انتها به انتها");

  const intakeResponsePromise = page.waitForResponse((response) =>
    response.request().method() === "POST" && response.url().endsWith("/customers/intake")
  );
  const saveResponsePromise = page.waitForResponse((response) =>
    response.request().method() === "PUT" && /\/cases\/[^/]+\/consultation$/.test(new URL(response.url()).pathname)
  );
  const generateResponsePromise = page.waitForResponse((response) =>
    response.request().method() === "POST" && response.url().endsWith("/recommendations/generate")
  );

  await page.getByRole("button", { name: "ثبت مراجعه + دریافت پیشنهاد" }).click();

  const intakeResponse = await intakeResponsePromise;
  expect(intakeResponse.status(), await intakeResponse.text()).toBe(200);
  const intake = await intakeResponse.json();
  const caseId = intake?.case?.case_id;
  expect(caseId).toBeTruthy();

  const saveResponse = await saveResponsePromise;
  expect(saveResponse.status(), await saveResponse.text()).toBe(200);
  const savedBody = await saveResponse.json();
  expect(savedBody.case_id).toBe(caseId);
  expect(savedBody.consultation_context).toMatchObject({
    affected_areas: ["گونه"],
    duration: "سه هفته",
    severity: 6,
    aggravating_factors: ["آفتاب"],
    current_products: ["شوینده ملایم"],
    notes: "یادداشت آزمون انتها به انتها",
  });

  const generateResponse = await generateResponsePromise;
  expect([200, 201], await generateResponse.text()).toContain(generateResponse.status());

  await expect(page.getByRole("heading", { name: "نتایج ارزیابی برای اپراتور" })).toBeVisible();
  expect(consultationSaveRequests).toHaveLength(1);

  const token = await page.evaluate(() => sessionStorage.getItem("hbi_access_token"));
  expect(token).toBeTruthy();

  const contextRead = await request.get(
    `${api}/cases/${encodeURIComponent(caseId)}/consultation`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  expect(contextRead.status(), await contextRead.text()).toBe(200);
  expect((await contextRead.json()).consultation_context).toMatchObject({
    affected_areas: ["گونه"],
    duration: "سه هفته",
    severity: 6,
    aggravating_factors: ["آفتاب"],
    current_products: ["شوینده ملایم"],
    notes: "یادداشت آزمون انتها به انتها",
  });

  // Stage 13-14 customer-facing readback is a separate read-only route.
  await page.goto("/recommendation");
  await expect(page.getByRole("heading", { name: "Recommendation", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "بارگذاری پیشنهادهای ذخیره‌شده" }).click();
  const output = page.getByRole("region", { name: "خروجی مشاوره" });
  await expect(output).toBeVisible();
  await expect(output).toContainText("اطلاعات فرم مشاوره: ثبت شده");
  await expect(output).toContainText("گونه");
  await expect(output).toContainText("سه هفته");

  // With no ProductProblemLink rows in this fixture, the UI must state that
  // an empty candidate list is not a product-unsuitability decision.
  await page.locator("#suitability_problem_id").fill("P17");
  await page.getByRole("button", { name: "بررسی و نمایش دلایل" }).click();
  await expect(page.getByText(/این نتیجه به معنی نامناسب بودن محصول نیست/)).toBeVisible();

  const suitability = await request.get(
    `${api}/recommendations/case/${encodeURIComponent(caseId)}/suitability/P17`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  expect(suitability.status(), await suitability.text()).toBe(200);
  const suitabilityBody = await suitability.json();
  expect(suitabilityBody.evaluation_mode).toBe("EXPLAINABLE_HUMAN_REVIEW_ONLY");
  expect(suitabilityBody.computed_only).toBe(true);
  expect(suitabilityBody.recommendation_eligible).toBe(false);
  expect(suitabilityBody.candidate_count).toBe(0);
  expect(suitabilityBody.candidates).toEqual([]);

  const contextOnlyProblem = await request.get(
    `${api}/recommendations/case/${encodeURIComponent(caseId)}/suitability/P22`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  expect(contextOnlyProblem.status()).toBe(422);
});
