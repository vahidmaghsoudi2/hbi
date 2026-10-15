const { test, expect } = require("@playwright/test");

test("Pilot browser: generate, persisted readback, reload, and fail closed", async ({ page, request }) => {
  // Route-level access is covered by homepage-navigation.spec.cjs. This proof uses a\n  // dummy AdminGate session to exercise the pilot workflow; API tokens are still\n  // obtained and validated through the real backend below.\n  await page.addInitScript(() => {\n    sessionStorage.setItem("hbi_admin_access_token", "pilot-browser-proof-admin-gate-token");\n  });\n\n  const api = process.env.HBI_TEST_API_URL || "http://127.0.0.1:8765/api/v1";
  const generated = [];
  const readbacks = [];
  let generateRequests = 0;

  page.on("request", req => {
    if (req.method() === "POST" && req.url().endsWith("/recommendations/generate")) generateRequests += 1;
  });
  page.on("response", async response => {
    if (response.url().endsWith("/recommendations/generate") && response.request().method() === "POST" && response.ok()) {
      try { generated.push(await response.json()); } catch {}
    }
    if (/\/recommendations\/case\//.test(response.url()) && response.request().method() === "GET" && response.ok()) {
      try { readbacks.push(await response.json()); } catch {}
    }
  });

  await page.goto("/pilot");
  await page.getByRole("button", { name: "دریافت JWT" }).click();
  await expect(page.getByRole("heading", { name: "ایجاد Case" })).toBeVisible();
  await page.getByRole("button", { name: "ایجاد Case" }).click();
  await expect(page.getByRole("heading", { name: "Case ایجاد شد" })).toBeVisible();
  const caseId = (await page.locator("p").filter({ hasText: "case_id:" }).innerText()).split("case_id:")[1].trim();
  expect(caseId).toBeTruthy();

  await page.getByRole("button", { name: "تولید Recommendation" }).click();
  await expect(page.getByRole("heading", { name: "Recommendation", exact: true })).toBeVisible();
  await page.locator("#concerns").fill("ضدآفتاب");
  const generateResponse = page.waitForResponse(r => r.request().method() === "POST" && r.url().endsWith("/recommendations/generate"));
  await page.getByRole("button", { name: /تولید و بازخوانی Recommendation/ }).click();
  const genResp = await generateResponse;
  expect(genResp.status(), await genResp.text()).toBe(200);
  const postRows = await genResp.json();
  expect(Array.isArray(postRows)).toBeTruthy();
  expect(postRows.length).toBeGreaterThan(0);
  const expected = postRows.filter(r => r.recommendation_id && r.product_id).map(r => ({ recommendation_id: r.recommendation_id, product_id: r.product_id }));
  expect(expected.length).toBeGreaterThan(0);
  await expect(page.getByText(expected[0].product_id, { exact: true })).toBeVisible();

  const firstRead = await request.get(`${api}/recommendations/case/${encodeURIComponent(caseId)}`, {
    headers: { Authorization: `Bearer ${await page.evaluate(() => sessionStorage.getItem("hbi_access_token"))}` }
  });
  expect(firstRead.status()).toBe(200);
  const persisted = await firstRead.json();
  for (const row of expected) {
    expect(persisted.some(p => p.recommendation_id === row.recommendation_id && p.product_id === row.product_id)).toBeTruthy();
  }

  await page.reload();
  const before = generateRequests;
  const savedRead = page.waitForResponse(r => r.request().method() === "GET" && r.url().includes(`/recommendations/case/`) && r.ok());
  await page.getByRole("button", { name: "بارگذاری پیشنهادهای ذخیره‌شده" }).click();
  expect((await savedRead).status()).toBe(200);
  await expect(page.getByText(expected[0].product_id, { exact: true })).toBeVisible();
  expect(generateRequests).toBe(before);

  // Missing token must fail in the UI before a generation request is sent.
  await page.evaluate(() => sessionStorage.removeItem("hbi_access_token"));
  const beforeMissing = generateRequests;
  await page.getByRole("button", { name: /تولید و بازخوانی Recommendation/ }).click();
  await expect(page.getByText("ابتدا از مسیر Pilot توکن بگیرید.")).toBeVisible();
  expect(generateRequests).toBe(beforeMissing);

  // Invalid token must be rejected by the API, and must not create additional records.
  await page.evaluate(() => sessionStorage.setItem("hbi_access_token", "invalid-browser-proof-token"));
  const invalidRead = await request.get(`${api}/recommendations/case/${encodeURIComponent(caseId)}`, {
    headers: { Authorization: "Bearer invalid-browser-proof-token" }
  });
  expect(invalidRead.status()).toBe(401);
  const invalidGenerate = await request.post(`${api}/recommendations/generate`, {
    headers: { Authorization: "Bearer invalid-browser-proof-token" },
    data: { case_id: caseId, customer_profile: { concerns: "ضدآفتاب" } }
  });
  expect(invalidGenerate.status()).toBe(401);
  const validToken = await page.evaluate(() => sessionStorage.getItem("hbi_access_token"));
  const refreshTokenResponse = await request.post(`${api}/auth/pilot-token`, { data: { customer_id: "CUST-PILOT-1" } });
  expect(refreshTokenResponse.status()).toBe(200);
  const valid = (await refreshTokenResponse.json()).access_token;
  const afterInvalid = await request.get(`${api}/recommendations/case/${encodeURIComponent(caseId)}`, {
    headers: { Authorization: `Bearer ${valid}` }
  });
  expect(afterInvalid.status()).toBe(200);
  const afterRows = await afterInvalid.json();
  expect(afterRows.map(r => r.recommendation_id).sort()).toEqual(persisted.map(r => r.recommendation_id).sort());
});
