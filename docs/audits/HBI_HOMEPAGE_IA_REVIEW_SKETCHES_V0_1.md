# HBI Homepage — IA Review Sketches V0.1

**Purpose:** lightweight review artifact before any broad navigation rewrite.  
**Source baseline:** Issue #352 / PO comment 6144947310; source inventory in `HBI_HOMEPAGE_STAGE0_ROUTE_ACTION_INVENTORY.md`.  
**Status:** proposed information architecture, not accepted UI or runtime evidence.  
**Notation:** `✓` belongs here; `X` is misplaced or must not be exposed here; `?` capability/behavior is not yet confirmed. Plain line sketches only; no colors or visual polish.

## 1. Proposed top-level tree

```text
HBI · فضای کاری مدیر
|
+-- ✓ خانه / داشبورد
|   +-- اقدام سریع: فروش مستقیم
|   +-- اقدام سریع: مشتریان
|   +-- اقدام سریع: مشاوره
|   +-- خلاصه عملیات: فروش امروز
|   +-- خلاصه عملیات: موجودی / هشدار کمبود
|   +-- خلاصه عملیات: گردش اخیر انبار
|   X فرم کامل فروش
|   X فرم کامل مشاوره
|
+-- ✓ مشتریان
|   +-- جست‌وجو با شماره موبایل / هویت مشتری
|   +-- پروفایل مشتری / ثبت مشتری
|   +-- سابقه خرید مشتری
|   X ایجاد خودکار نشست مشتری هنگام انتخاب برای فروش
|
+-- ✓ مشاوره
|   +-- ثبت واقعیت مراجعه و مسئله
|   +-- ارزیابی نیاز معتبر
|   +-- محصولات واجد شرایط گالری
|   +-- پیشنهادها و شواهد
|   +-- تصمیم اپراتور
|   X میانبر «انتخاب پیشنهاد برای فروش»
|
+-- ✓ فروش
|   +-- ثبت فروش مستقیم (بدون الزام مشاوره)
|   +-- انتخاب اختیاری مشتری
|   +-- انتخاب محصول فعال و واجد شرایط با موجودی و قیمت
|   +-- نتیجه ثبت فروش
|   X product_id دستی برای دور زدن فهرست مجاز
|   X اتصال ضمنی مشتری/مشاوره قبلی
|
+-- ✓ ورود و مدیریت محصول
|   +-- ورود / ویرایش مشخصات محصول
|   +-- کنترل تکراری بودن
|   +-- ثبت شواهد
|   +-- بررسی هویت محصول
|   +-- QA و گردش تأیید
|   X ورود فیزیکی موجودی
|   X گزارش حسابداری
|
+-- ✓ کالا و انبار
|   +-- فهرست کاتالوگ مدیریتی
|   +-- وضعیت قابل فروش / موجودی
|   +-- مشاهده گزارش موجودی
|   X ثبت خرید / ورود فیزیکی کالا (این عملیات در خرید است)
|   ? نمایش فقط کالاهای قابل فروش در کاتالوگ فروش؛ باید از API مجاز تغذیه شود
|
+-- ✓ خرید
|   +-- ثبت خرید
|   +-- ورود فیزیکی موجودی
|   +-- نرخ ارز / قیمت خرید
|   X ورود مشخصات اصلی محصول
|   X QA / تأیید محصول
|
+-- ✓ گزارش‌ها و حسابداری
|   +-- فروش امروز / بازه فروش
|   +-- موجودی و کمبود
|   +-- گردش کالا
|   +-- گزارش مالی پشتیبانی‌شده
|   X سود ناخالص تا تصویب سیاست COGS
|   X اعداد ساختگی برای شمارش QA یا intake
|
+-- ? تنظیمات
|   +-- مقصد مستقل واقعی در کد فعلی احراز نشده
|   X ساخت صفحه تنظیمات نمایشی بدون قابلیت واقعی
|
+-- ✓ نوار ثابت
    +-- هویت گالری / فضای کاری مدیر
    +-- خروج از حساب مدیر
    X نمایش پنل مشتری یا ورود مشتری به سیستم
```

## 2. Line-only sketch of the current main navigation

```text
+------------------------------------------------------------------+
| HBI / گالری مقصودی                      [منوی اصلی] [خروج مدیر]   |
+------------------------------------------------------------------+
| فضای کاری مدیر                                                   |
| یک حوزه را انتخاب کنید.                                          |
|                                                                  |
| [✓ خانه و داشبورد] [✓ مشتریان]       [✓ مشاوره]                  |
| [✓ فروش]           [X مدیریت محصولات: گروه‌بندی بیش از حد]       |
| [✓ خرید]           [✓ گزارش‌ها]      [? تنظیمات مستقل وجود ندارد]|
+------------------------------------------------------------------+
```

**Decision needed before implementation:** split current `مدیریت محصولات` into `ورود و مدیریت محصول` and `کالا و انبار`; keep `خرید` and `گزارش‌ها و حسابداری` separate. This is a navigation decision, not a color/layout task.

## 3. Sketch: Home / Dashboard

```text
+------------------------------------------------------------------+
| HBI                                      [خروج از حساب مدیر]      |
+------------------------------------------------------------------+
| خانه / داشبورد                                                   |
|                                                                  |
| اقدام سریع                                                       |
| [✓ ثبت فروش مستقیم] [✓ مشتریان] [✓ شروع مشاوره]                  |
| [✓ ورود محصول]       [✓ بررسی QA] [✓ خرید / ورود موجودی]         |
|                                                                  |
| خلاصه عملیات                                  [نوسازی داده‌ها]    |
| +------------------+ +------------------+ +--------------------+ |
| | ✓ فروش امروز     | | ✓ موجودی انبار   | | ✓ موجودی کم        | |
| +------------------+ +------------------+ +--------------------+ |
|                                                                  |
| موارد نیازمند توجه                                               |
| [✓ هشدارهای مستند / X شمارش ساختگی QA]                            |
|                                                                  |
| آخرین گردش‌های انبار                                             |
| [✓ فهرست کوتاه گردش‌ها]                                          |
|                                                                  |
| X فرم فروش کامل / X فرم مشاوره کامل داخل داشبورد                 |
+------------------------------------------------------------------+
```

**Source reality:** current dashboard contains quick actions, sales/inventory/low-stock summaries, recent stock movements, and links into Accounting. Product-intake/QA totals are intentionally absent because a verified Admin lifecycle summary API has not been established.

## 4. Sketch: domain landing page

```text
+------------------------------------------------------------------+
| HBI                         [بازگشت به منوی اصلی] [خروج مدیر]     |
+------------------------------------------------------------------+
| [نام حوزه]                                                       |
| فقط عملیات همین حوزه                                             |
|                                                                  |
| [✓ زیرعملیات مرتبط 1] [✓ زیرعملیات مرتبط 2] [✓ زیرعملیات مرتبط 3]|
|                                                                  |
| X زیرمنوی متعلق به حوزه دیگر                                     |
+------------------------------------------------------------------+
```

Current source implements this landing pattern for Customers, Consultation, Sales, Product Management, Purchases, Reports, and Home. It does not yet expose all approved domains as independent primary sections.

## 5. Sketch: Customers

```text
+------------------------------------------------------------------+
| مشتریان                                                          |
| [✓ جست‌وجو با موبایل / نام خانوادگی] [✓ جست‌وجو]                  |
|                                                                  |
| نتایج                                                             |
| [✓ مشتری] [شماره موبایل] [شناسه] [انتخاب برای سابقه / پروفایل]   |
|                                                                  |
| سابقه خرید                                                       |
| [✓ فهرست سابقه همان مشتری]                                       |
|                                                                  |
| پروفایل                                                           |
| [✓ مشاهده / تکمیل / ثبت مشتری]                                   |
|                                                                  |
| X فرم مشاوره اجباری برای ثبت فروش                                |
| X استفاده از نام کوچک به‌عنوان کلید هویت                         |
+------------------------------------------------------------------+
```

**Source concern:** current customer-selection flow calls a pilot-token endpoint and switches to Consultation. Keep the customer domain separate; trace and refactor that cross-domain transition only after preserving required consultation behavior and identity rules.

## 6. Sketch: Consultation

```text
+------------------------------------------------------------------+
| مشاوره                                                           |
| [✓ ثبت واقعیت مراجعه]                                            |
| [✓ مسئله / نیاز]                                                 |
| [✓ شواهد و شرایط لازم]                                           |
| [✓ فهرست محصولات واجد شرایط]                                     |
| [✓ پیشنهادها و علت تصمیم]                                        |
| [✓ تصمیم اپراتور]                                                |
|                                                                  |
| X انتخاب مستقیم پیشنهاد برای فروش از کارت نتیجه                  |
| X تصمیم خودکار «بهترین محصول» بدون Need و شواهد معتبر            |
+------------------------------------------------------------------+
```

The intended flow remains: Customer/Consultation Reality → Problem → Valid Need → Eligible HBI Gallery Product → Recommendation → Operator Decision. The customer has no system account or system access.

## 7. Sketch: Sales

```text
+------------------------------------------------------------------+
| فروش                                                             |
| ثبت فروش مستقیم؛ مشاوره پیش‌نیاز نیست                            |
|                                                                  |
| مشتری (اختیاری)                                                  |
| [جست‌وجوی مشتری] [نتایج] [مشتری انتخاب‌شده / حذف انتخاب]          |
|                                                                  |
| محصول قابل فروش                                                  |
| [فقط محصول ACTIVE + هویت VERIFIED + QA VALID + موجودی + قیمت]    |
| تعداد [ ]                                                        |
| قیمت از موجودی / نرخ ارز رسمی                                   |
| مبلغ [محاسبه‌شده]                                                |
| [✓ ثبت فروش]                                                     |
|                                                                  |
| نتیجه / شناسه فروش                                               |
| X product_id دستی                                                 |
| X customer_id از نشست قبلی بدون انتخاب صریح                      |
| X نیاز به مشاوره قبلی                                            |
+------------------------------------------------------------------+
```

The source fix in PR #363 now adds an Admin-only sellable-products endpoint and optional explicit customer association. CI and runtime still need to prove the behavior end to end.

## 8. Sketch: Product Intake & Product Management

```text
+------------------------------------------------------------------+
| ورود و مدیریت محصول                                              |
| [✓ ورود / ویرایش مشخصات]                                         |
| [✓ بررسی تکراری بودن]                                            |
| [✓ ثبت شواهد با منبع]                                            |
| [✓ بررسی هویت]                                                   |
| [✓ QA / تأیید / رد با دلیل]                                      |
|                                                                  |
| X ثبت فیزیکی موجودی                                              |
| X خرید                                                            |
| X گزارش فروش / حسابداری                                          |
+------------------------------------------------------------------+
```

Product intake creates a governed product record; it does not imply physical stock. Existing pilot product imports are outside this homepage task.

## 9. Sketch: Products & Inventory

```text
+------------------------------------------------------------------+
| کالا و انبار                                                     |
| [✓ فهرست کاتالوگ مدیریتی]                                        |
| [✓ وضعیت کالا و موجودی]                                          |
| [✓ مشاهده گزارش موجودی / گردش]                                   |
|                                                                  |
| [رفتن به خرید برای ورود فیزیکی موجودی]                           |
| X فرم QA / تغییر وضعیت محصول در این صفحه                         |
+------------------------------------------------------------------+
```

The product list used for management and the list used for sale must remain distinct. Sale selection must be backed by explicit eligibility and inventory conditions, not by identity status alone.

## 10. Sketch: Purchasing

```text
+------------------------------------------------------------------+
| خرید                                                             |
| [✓ انتخاب کالای مدیریت‌شده]                                      |
| [✓ مقدار خرید / ورود فیزیکی]                                     |
| [✓ قیمت خرید / نرخ ارز]                                          |
| [✓ ثبت ورود موجودی و گردش انبار]                                 |
|                                                                  |
| X ساخت یا ویرایش مشخصات اصلی محصول                               |
| X تأیید QA                                                       |
+------------------------------------------------------------------+
```

## 11. Sketch: Reports & Accounting

```text
+------------------------------------------------------------------+
| گزارش‌ها و حسابداری                                              |
| [✓ فروش امروز] [✓ موجودی] [✓ گردش کالا] [✓ گزارش مالی]           |
|                                                                  |
| X سود ناخالص تا سیاست COGS تصویب نشده                            |
| X گزارش QA / intake با شمارش ساختگی                              |
+------------------------------------------------------------------+
```

Current route is `/accounting`; its sections are sales, inventory, stock flow, and financial report. This is the current source reality, not proof that all calculations are accepted.

## 12. Existing auxiliary routes requiring an access decision

```text
/pilot
  X Do not expose as a normal Admin menu item before access/token review.

/recommendation
  X Do not expose as a normal Admin menu item before access/token review.

/catalog
  ? Admin-gated route currently calls public product-list behavior.
  ✓ Keep distinct from the internal managed catalog until references are traced.

/login
  ✓ Public login entry; after logout protected destinations must return here.
```

## 13. Relationship map

```text
Customer record
    |
    +--> Customer profile / purchase history
    |
    +--> [only if consultation requested] Consultation reality
                 |
                 v
              Problem
                 |
                 v
              Valid Need
                 |
                 v
       Eligible HBI Gallery Products
                 |
                 v
          Recommendation + Evidence
                 |
                 v
          Operator Decision
                 |
                 +--> remains in Consultation
                 X--> no direct sale shortcut

Direct Sales ------------------------------------+
    |                                            |
    +--> optional explicit customer selection    |
    +--> active, QA-valid, identity-verified      |
    |    product + price + available stock       |
    +--> Sale record + inventory decrement + StockMovement
                                                 |
Purchasing --> stock-in --> Inventory / StockMovement
                                                 |
Reports / Accounting <---------------------------+
```

## 14. Acceptance checklist before calling homepage final

- [ ] Product Owner approves the primary-domain tree and the split between Product Management, Products & Inventory, and Purchasing.
- [ ] Every visible button is mapped to one actual route/panel and tested.
- [ ] No customer-facing login or system access is introduced.
- [ ] Direct sale works without consultation and without customer; explicit customer association also works.
- [ ] Sale picker excludes DRAFT, inactive, QA-invalid, identity-unverified, no-stock, and unpriced products.
- [ ] Sale writes and stock movements are consistent in a real database.
- [ ] Customer identity conflict rules are respected.
- [ ] Settings is either a real supported destination or explicitly excluded from this release; no fake placeholder.
- [ ] CI passes on exact PR heads.
- [ ] Windows/browser proof covers login, refresh, navigation, back/forward, logout, and protected routes.
- [ ] Stage 1 + Stage 2 are reviewed as one coherent tree; only then consider merge to master with explicit approval.
