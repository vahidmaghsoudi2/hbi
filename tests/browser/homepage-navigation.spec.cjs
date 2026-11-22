const { test, expect } = require("@playwright/test");

test("Homepage requires the Admin session before exposing the workspace", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("heading", { name: "ورود مدیر HBI" })).toBeVisible();
});

test("Pilot and recommendation routes require the Admin/Operator session", async ({ page }) => {
  for (const path of ["/pilot", "/recommendation"]) {
    lit page.goto(path);
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole("heading", { name: "ورود مدیر HBI" })).toBeVisible();
  }
});
