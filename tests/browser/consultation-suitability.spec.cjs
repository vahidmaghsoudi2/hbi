const { test, expect } = require("@playwright/test");

test("Stage 15-16: customer consultation survives API round-trip and renders explainable output", async ({ page, request }) => {
  const api = process.env.HBI_TEST_API_URL || "http://127.0.0.1:8765/api/v1";
  const tokenResponse = await request.post(`${api}/auth/pilot-token`, {
    data: { customer_id: "CUST-PILOT-1" },
  });
  expect(tokenResponse.status()).toBe(200);
  const token = (await tokenResponse.json()).access_token;
  const headers = { Authorization: `Bearer ${token}` };

  const created = await request.post(`${api}/cases/`, {
    headers,
    data: { customer_id: "CUST-PILOT-1", case_type: "SKIN" },
  });
  expect(created.status()).toBe(201);
  const caseId = (await created.json()).case_id;

  const context = {
    affected_areas: ["cheek"],
    duration: "three weeks",
    severity: 4,
    aggravating_factors: ["sun exposure"],
    current_products: ["gentle cleanser"],
    notes: "Disposable browser proof only",
  };
  const saved = await request.put(`${api}/cases/${encodeURIComponent(caseId)}/consultation`, {
    headers,
    data: context,
  });
  expect(saved.status()).toBe(200);

  await page.addInitScript(({ accessToken, newCaseId }) => {
    sessionStorage.setItem("hbi_admin_access_token", "pilot-browser-proof-admin-gate-token");
    sessionStorage.setItem("hbi_access_token", accessToken);
    sessionStorage.setItem("hbi_case_id", newCaseId);
  }, { accessToken: token, newCaseId: caseId });

  await page.goto("/recommendation");
  await page.getByRole("button", { name: "بارگذاری پیشنهادهای ذخیره‌شده" }).click();
  await expect(page.getByRole("heading", { name: "خروجی مشاوره" })).toBeVisible();
  await expect(page.getByText("اطلاعات فرم مشاوره: ثبت شده")).toBeVisible();
  await expect(page.getByText("cheek", { exact: false })).toBeVisible();
  await expect(page.getByText("three weeks", { exact: false })).toBeVisible();
  await expect(page.getByText("در حال حاضر پیشنهاد واجد شرایطی وجود ندارد")).toBeVisible();

  // Keep the empty-result path covered independently.
  await page.locator("#suitability_problem_id").fill("P43");
  const emptyResponse = page.waitForResponse((response) =>
    response.url().includes(`/recommendations/case/${caseId}/suitability/P43`) &&
    response.request().method() === "GET"
  );
  await page.getByRole("button", { name: "بررسی و نمایش دلایل" }).click();
  expect((await emptyResponse).status()).toBe(200);
  await expect(page.getByText("کاندیدای جاری: 0")).toBeVisible();
  await expect(page.getByText(/این نتیجه به معنی نامناسب بودن محصول نیست/)).toBeVisible();

  // Positive browser path: candidate is visible but never becomes a recommendation.
  await page.locator("#suitability_problem_id").fill("P17");
  const suitabilityResponse = page.waitForResponse((response) =>
    response.url().includes(`/recommendations/case/${caseId}/suitability/P17`) &&
    response.request().method() === "GET"
  );
  await page.getByRole("button", { name: "بررسی و نمایش دلایل" }).click();
  const candidateResponse = await suitabilityResponse;
  expect(candidateResponse.status()).toBe(200);
  const suitabilityBody = await candidateResponse.json();
  expect(suitabilityBody.candidate_count).toBe(1);
  expect(suitabilityBody.recommendation_eligible).toBe(false);
  expect(suitabilityBody.candidates[0].review_gate).toBe("HUMAN_REVIEW_ONLY");
  expect(suitabilityBody.candidates[0].suitability_status).toBe("HUMAN_REVIEW_REQUIRED");
  expect(suitabilityBody.candidates[0].product_gate_blockers).toEqual([]);
  await expect(page.getByText("کاندیدای جاری: 1")).toBeVisible();
  await expect(page.getByText("COSRX · The 6 Peptide Skin Booster Serum")).toBeVisible();
  await expect(page.getByText("وضعیت تناسب: HUMAN_REVIEW_REQUIRED")).toBeVisible();
  await expect(page.getByText("توصیه‌پذیر: خیر، بررسی انسانی الزامی است.")).toBeVisible();

  await page.locator("#suitability_problem_id").fill("P22");
  const rejectedProblem = page.waitForResponse((response) =>
    response.url().includes(`/recommendations/case/${caseId}/suitability/P22`) &&
    response.request().method() === "GET"
  );
  await page.getByRole("button", { name: "بررسی و نمایش دلایل" }).click();
  expect((await rejectedProblem).status()).toBe(422);
  await expect(page.locator(".alert.error")).toBeVisible();
});
