const { test, expect } = require("@playwright/test");

test("Skin problem bank renders all 61 source-backed records and searches across the full reference list", async ({ page }) => {
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
  const list = page.getByRole("navigation", { name: "فهرست ۶۱ مشکل پوستی P01 تا P61" });
  await expect(list.locator(".pro-problem-item")).toHaveCount(61);
  await expect(page.getByRole("heading", { name: "Hyperpigmentation/dark spots" })).toBeVisible();
  await expect(page.getByText("Problem/presentation", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("UNKNOWN", { exact: false }).first()).toBeVisible();
  await expect(page.getByText("Commit مبنا:")).toBeVisible();

  // P22 is cross-listed in the Map, but its canonical row and shelf are S04.
  // The UI must not duplicate it under S09 or infer a second canonical record.
  await page.getByLabel("فیلتر قفسه").selectOption("S04");
  await expect(list.locator(".pro-problem-item")).toHaveCount(7);
  await expect(list.getByRole("button", { name: /P22/ })).toBeVisible();
  await list.getByRole("button", { name: /P22/ }).click();
  await expect(page.getByRole("heading", { name: "Sun-related pigmentation" })).toBeVisible();
  await expect(page.getByText("Context/pigmentation presentation", { exact: true }).first()).toBeVisible();
  await page.getByLabel("فیلتر قفسه").selectOption("ALL");
  await expect(list.locator(".pro-problem-item")).toHaveCount(61);

  // P22 is cross-listed under S09 but remains canonical under S04 only.
  await page.getByLabel("فیلتر قفسه").selectOption("S09");
  await expect(list.locator(".pro-problem-item")).toHaveCount(2);
  await expect(list.getByRole("button", { name: /P22/ })).toHaveCount(0);
  await page.getByLabel("فیلتر قفسه").selectOption("S10");
  await expect(list.locator(".pro-problem-item")).toHaveCount(5);
  await expect(list.getByRole("button", { name: /P61/ })).toBeVisible();
  await page.getByLabel("فیلتر قفسه").selectOption("ALL");

  const requestsAfterOpen = requests.slice(beforeOpen);
  expect(requestsAfterOpen.filter((url) => /github\.com|\/api\//i.test(url))).toEqual([]);

  await page.getByLabel("جست‌وجو در ۶۱ مشکل پوستی P01–P61").fill("P24");
  await expect(list.locator(".pro-problem-item")).toHaveCount(1);
  await expect(list.getByRole("button", { name: /P24/ })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Persistent redness" })).toBeVisible();

  await page.getByLabel("جست‌وجو در ۶۱ مشکل پوستی P01–P61").fill("P61");
  await expect(list.locator(".pro-problem-item")).toHaveCount(1);
  await expect(list.getByRole("button", { name: /P61/ })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Photosensitivity" })).toBeVisible();

  await page.getByLabel("جست‌وجو در شش مدخل پایلوت").fill("not-a-record");
  await expect(list.locator(".pro-problem-item")).toHaveCount(0);
  await expect(page.getByText("در میان ۶۱ مشکل پوستی نتیجه‌ای پیدا نشد.")).toBeVisible();
});
