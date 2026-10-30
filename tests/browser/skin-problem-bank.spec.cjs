const { test, expect } = require("@playwright/test");

test("Skin problem bank renders only six source-backed records and searches within the pilot", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("hbi_admin_access_token", "skin-problem-bank-test-token");
  });

  const requests = [];
  page.on("request", (request) => requests.push(request.url()));

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "فضای کاری مدیر" })).toBeVisible();
  await page.getByRole("button", { name: "ورود به دانشنامه" }).click();
  await page.getByRole("button", { name: "ورود به دانش پوست" }).click();
  await expect(page.getByRole("heading", { name: "دانش پوست" })).toBeVisible();

  const beforeOpen = requests.length;
  await page.getByRole("button", { name: "ورود به بانک مشکلات پوستی" }).click();
  await expect(page.getByRole("heading", { name: "بانک مشکلات پوستی" })).toBeVisible();
  const list = page.getByRole("navigation", { name: "شش مدخل منتخب مشکلات پوستی" });
  await expect(list.locator(".pro-problem-item")).toHaveCount(6);
  await expect(page.getByRole("heading", { name: "Hyperpigmentation / dark spots" })).toBeVisible();
  await expect(page.getByText("Problem/presentation", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("UNKNOWN", { exact: false }).first()).toBeVisible();
  await expect(page.getByText("Commit مبنا:")).toBeVisible();

  const requestsAfterOpen = requests.slice(beforeOpen);
  expect(requestsAfterOpen.filter((url) => /github\.com|\/api\//i.test(url))).toEqual([]);

  await page.getByLabel("جست‌وجو در شش مدخل پایلوت").fill("P24");
  await expect(list.locator(".pro-problem-item")).toHaveCount(1);
  await expect(list.getByRole("button", { name: /P24/ })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Persistent redness" })).toBeVisible();

  await page.getByLabel("جست‌وجو در شش مدخل پایلوت").fill("not-a-record");
  await expect(list.locator(".pro-problem-item")).toHaveCount(0);
  await expect(page.getByText("در محدودهٔ همین شش مدخل نتیجه‌ای پیدا نشد.")).toBeVisible();
});
