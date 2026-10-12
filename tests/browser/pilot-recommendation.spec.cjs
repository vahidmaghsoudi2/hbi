const { test, expect } = require("@playwright/test");

// The legacy pilot-token recommendation flow is not an operational user journey.
// Until it is redesigned as an Admin-owned workflow, browser proof verifies that
// these internal routes fail closed for unauthenticated visitors.
test("legacy pilot recommendation flow is not exposed without an Admin session", async ({ page }) => {
  for (const path of ["/pilot", "/recommendation"]) {
    await page.goto(path);
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole("heading", { name: "ورود مدیر HBI" })).toBeVisible();
    await expect(page.getByRole("button", { name: "دریافت JWT" })).toHaveCount(0);
  }
});
