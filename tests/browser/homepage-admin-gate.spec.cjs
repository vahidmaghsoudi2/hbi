const { test, expect } = require("@playwright/test");

test("operational homepage redirects unauthenticated visits to Admin login", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("heading", { name: "ورود مدیر HBI" })).toBeVisible();
});

test("pilot consultation route remains independently reachable without Admin session", async ({ page }) => {
  await page.goto("/pilot");
  await expect(page.getByRole("button", { name: "دریافت JWT" })).toBeVisible();
});
