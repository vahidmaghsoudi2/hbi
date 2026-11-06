const { test, expect } = require("@playwright/test");
const fs = require("fs");

/**
 * Activity 35 / PR #504 acceptance:
 * Customer-visible Home Page results must survive operator-session failure.
 *
 * Uses the disposable pilot SQLite DB and real backend HTTP APIs.
 * Operator failure is injected only on operator-scoped routes; customer
 * generate/read paths remain real and unmocked.
 */
test("Home Page keeps customer recommendations when operator session fails", async ({ page, request }) => {
  const api = process.env.HBI_TEST_API_URL || "http://127.0.0.1:8765/api/v1";
  const dbUrl = process.env.DATABASE_URL || "";
  expect(dbUrl.startsWith("sqlite:///"), "requires disposable SQLite DATABASE_URL").toBeTruthy();

  const dbPath = dbUrl.replace("sqlite:///", "");
  expect(fs.existsSync(dbPath), `isolated SQLite must exist: ${dbPath}`).toBeTruthy();

  // --- Real backend: guest + customer token ---
  const guestResp = await request.post(`${api}/customers/guest`, {
    data: { name: "Operator Isolation Guest", consent: 0, concerns: "ضدآفتاب" },
  });
  expect(guestResp.ok(), await guestResp.text()).toBeTruthy();
  const guest = await guestResp.json();
  const customerId = guest.customer_id || guest.customer?.customer_id;
  expect(customerId).toBeTruthy();

  const tokenResp = await request.post(`${api}/auth/pilot-token`, {
    data: { customer_id: customerId },
  });
  expect(tokenResp.ok(), await tokenResp.text()).toBeTruthy();
  const tokenPair = await tokenResp.json();
  const customerToken = tokenPair.access_token;
  expect(customerToken).toBeTruthy();

  // --- Real intake opens a SKIN case owned by this customer ---
  const mobile = `09${String(Date.now()).slice(-9)}`;
  const intakeResp = await request.post(`${api}/customers/intake`, {
    headers: { Authorization: `Bearer ${customerToken}` },
    data: {
      name: "Isolation",
      family_name: "Operator",
      mobile,
      concerns: "ضدآفتاب",
      consent: 0,
      skin_profile: "خشک",
      case_type: "SKIN",
      guest: false,
      open_case: true,
    },
  });
  expect(intakeResp.ok(), await intakeResp.text()).toBeTruthy();
  const intake = await intakeResp.json();
  const caseId = intake.case?.case_id || intake.case_id;
  expect(caseId, "case must be created for customer consultation").toBeTruthy();

  // Case-owned consultation answer required for SKIN eligibility gate.
  const answerResp = await request.post(`${api}/recommendations/next-question/${caseId}/answer`, {
    headers: { Authorization: `Bearer ${customerToken}` },
    data: { question_id: "skin.primary_need.v1", answer: "sun_protection" },
  });
  expect(answerResp.ok(), await answerResp.text()).toBeTruthy();

  // --- Real generate: at least one ELIGIBLE recommendation persisted ---
  const genResp = await request.post(`${api}/recommendations/generate`, {
    headers: { Authorization: `Bearer ${customerToken}` },
    data: {
      case_id: caseId,
      customer_profile: { concerns: "ضدآفتاب", skin_type: "خشک" },
    },
  });
  expect(genResp.ok(), await genResp.text()).toBeTruthy();
  const generated = await genResp.json();
  expect(Array.isArray(generated)).toBeTruthy();
  expect(generated.length, "at least one recommendation row expected").toBeGreaterThan(0);
  const eligible = generated.filter(
    (r) => String(r.eligibility_status || r.eligibility || "").toUpperCase() === "ELIGIBLE"
  );
  expect(eligible.length, "at least one ELIGIBLE recommendation required").toBeGreaterThan(0);
  // Public generate contract must not leak internal exclusion reasons.
  for (const row of generated) {
    expect(row).not.toHaveProperty("exclusion_reasons");
  }

  // Public case read confirms persistence for the same case.
  const publicRead = await request.get(`${api}/recommendations/case/${caseId}`, {
    headers: { Authorization: `Bearer ${customerToken}` },
  });
  expect(publicRead.ok(), await publicRead.text()).toBeTruthy();
  const publicList = await publicRead.json();
  expect(Array.isArray(publicList)).toBeTruthy();
  expect(publicList.length).toBeGreaterThan(0);
  for (const row of publicList) {
    expect(row).not.toHaveProperty("exclusion_reasons");
    expect(String(row.eligibility_status || row.eligibility || "").toUpperCase()).toBe("ELIGIBLE");
  }

  // Isolated DB must contain the case row (file-backed SQLite via real backend writes).
  const { execFileSync } = require("child_process");
  const py = `
import sqlite3, sys
c = sqlite3.connect(sys.argv[1])
row = c.execute(
    "SELECT case_id, customer_id, case_type FROM [Case] WHERE case_id=?",
    (sys.argv[2],),
).fetchone()
if not row:
    raise SystemExit("case row missing")
print("|".join("" if x is None else str(x) for x in row))
`.trim();
  const out = execFileSync("python3", ["-c", py, dbPath, caseId], { encoding: "utf-8" }).trim();
  const parts = out.split("|");
  expect(parts[0]).toBe(caseId);
  expect(parts[1]).toBe(customerId);
  expect(String(parts[2] || "").toUpperCase()).toBe("SKIN");

  // --- Inject operator failure only (customer APIs stay real) ---
  let operatorTokenCalls = 0;
  let evaluationsCalls = 0;
  await page.route("**/api/v1/auth/pilot-operator-token", async (route) => {
    operatorTokenCalls += 1;
    await route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({ detail: "operator session unavailable for isolation proof" }),
    });
  });
  await page.route("**/api/v1/recommendations/case/*/evaluations", async (route) => {
    evaluationsCalls += 1;
    await route.fulfill({
      status: 403,
      contentType: "application/json",
      body: JSON.stringify({ detail: "operator evaluations blocked for isolation proof" }),
    });
  });

  // Seed customer session; intentionally omit operator token.
  await page.addInitScript(
    ({ accessToken, refreshToken, cid, caze }) => {
      sessionStorage.setItem("hbi_admin_access_token", "pilot-browser-proof-admin-gate-token");
      sessionStorage.setItem("hbi_access_token", accessToken);
      sessionStorage.setItem("hbi_refresh_token", refreshToken || "");
      sessionStorage.setItem("hbi_customer_id", cid);
      sessionStorage.setItem("hbi_case_id", caze);
      sessionStorage.removeItem("hbi_operator_access_token");
    },
    {
      accessToken: customerToken,
      refreshToken: tokenPair.refresh_token,
      cid: customerId,
      caze: caseId,
    }
  );

  await page.goto("/");
  await page.getByRole("button", { name: "ورود به مشاوره" }).click();
  await page.getByRole("button", { name: "مشاهده نتایج همین نشست" }).click();

  await expect(page.getByRole("heading", { name: "نتایج ارزیابی برای اپراتور" })).toBeVisible();
  // Customer results must render; empty wipe is the regression under test.
  await expect(page.getByText("هنوز پیشنهادی گرفته نشده — از مشاوره شروع کنید.")).toHaveCount(0);
  await expect(page.getByText(/پیشنهاد واجد شرایطی یافت نشد/)).toHaveCount(0);

  // At least one recommendation card / product reference from the public list.
  const firstProduct = String(publicList[0].product_id || "");
  if (firstProduct) {
    await expect(page.getByText(firstProduct, { exact: false }).first()).toBeVisible({ timeout: 15000 });
  } else {
    await expect(page.locator(".pro-tag").filter({ hasText: "واجد" }).first()).toBeVisible();
  }

  // Refresh must recover the same case results via customer token path.
  await page.reload();
  await page.getByRole("button", { name: "ورود به مشاوره" }).click();
  await page.getByRole("button", { name: "مشاهده نتایج همین نشست" }).click();
  await expect(page.getByText("هنوز پیشنهادی گرفته نشده — از مشاوره شروع کنید.")).toHaveCount(0);
  if (firstProduct) {
    await expect(page.getByText(firstProduct, { exact: false }).first()).toBeVisible({ timeout: 15000 });
  }

  // Operator failure routes were exercised without wiping UI.
  expect(operatorTokenCalls + evaluationsCalls).toBeGreaterThan(0);

  // --- Authorized operator path remains available outside the blocked UI session ---
  const opResp = await request.post(`${api}/auth/pilot-operator-token`, { data: {} });
  expect(opResp.ok(), await opResp.text()).toBeTruthy();
  const opToken = (await opResp.json()).access_token;
  expect(opToken).toBeTruthy();

  const evalResp = await request.get(`${api}/recommendations/case/${caseId}/evaluations`, {
    headers: { Authorization: `Bearer ${opToken}` },
  });
  expect(evalResp.ok(), await evalResp.text()).toBeTruthy();
  const evaluations = await evalResp.json();
  expect(Array.isArray(evaluations)).toBeTruthy();
  expect(evaluations.length).toBeGreaterThan(0);

  // Internal evaluation payload may include exclusion_reasons; public must not.
  const publicAgain = await request.get(`${api}/recommendations/case/${caseId}`, {
    headers: { Authorization: `Bearer ${customerToken}` },
  });
  const publicAgainList = await publicAgain.json();
  for (const row of publicAgainList) {
    expect(row).not.toHaveProperty("exclusion_reasons");
  }
});
