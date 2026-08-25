# ثبت محصول — Product Intake Vertical Slice

**Document ID:** HBI-PRODUCT-INTAKE-VERTICAL-SLICE-001  
**نوع:** فرمان اجرایی (Executive Order)  
**ثبت‌کننده:** Grok2 (وزیر دست چپ — GitHub Executive)  
**دستور PO:** مهندس وحید مقصودی  
**تاریخ ثبت:** 2026-08-25  
**MASTER مبنا:** `666ee97cf7932f2ff90b8cdd9944edb34070377b`  
**وضعیت این Commit:** DOCS-ONLY — هیچ تغییر app/ / Seed / Product A–D اعمال نشده است.

---

## فرمان اجرایی — Product Intake Vertical Slice

**MASTER مبنا:** `666ee97cf7932f2ff90b8cdd9944edb34070377b`

### مأموریت

یک مسیر کامل و حداقلی برای ورود محصول جدید ایجاد کنید تا مالک محصول بتواند بدون دخالت مهندس، محصولات جدید گالری را وارد سیستم کند؛ بدون آنکه Product A–D، Seed، Scoring، Evidence Claims موجود، Hard Gate یا Pilot Flow دستخوش تغییر شوند.

**هدف این مرحله:**

```text
Product Intake → ذخیره کنترل‌شده → بررسی → Active → ورود مجاز به Recommendation
```

این مرحله باید یک **Vertical Slice واقعی** باشد، نه آغاز یک سیستم مدیریت محصول بزرگ.

---

### فرمان ۱ — Grok1: مدیر اجرای این مأموریت

Grok1 مسئول هماهنگی اجرای این Change Set است.

**وظایف:**

- وضعیت فعلی Master را قبل از هر تغییر ثبت کند.
- Scope را قفل کند.
- تغییرات اعضای تیم را با هدف اصلی تطبیق دهد.
- هر پیشنهاد خارج از Scope را به Version-2 منتقل کند.
- در پایان، گزارش نهایی شامل تغییرات، تست‌ها، ریسک‌ها و تصمیم Release ارائه کند.

**اصل:** هیچ Scope Explosion مجاز نیست.

---

### فرمان ۲ — Grok2: مهندس مسیر Product Intake

Grok2 باید مسیر واقعی ورود محصول را پیاده‌سازی کند.

**مسیر مورد انتظار:**

```text
Create Draft Product → ثبت Identity → ثبت Claims با Source → Review → Activate
```

**الزامات:**

- محصول جدید ابتدا **DRAFT** باشد.
- Draft در Recommendation واقعی قابل استفاده نباشد.
- Active شدن تنها پس از عبور از کنترل‌های لازم امکان‌پذیر باشد.
- محصول Active بتواند وارد Recommendation شود.
- محصول جدید نباید هیچ داده موجود Product A–D را تغییر دهد.

---

### فرمان ۳ — Qwen1: مالک Data Contract

Qwen1 باید قبل از گسترش Schema، قرارداد حداقلی Product Intake را مشخص و تأیید کند.

**حداقل مفهومی قرارداد — Product Identity**

- product_id
- product_code
- brand
- canonical_name
- description
- category
- variant/size در حد لازم
- status
- created_at / updated_at
- created_by

**Claims — هر Claim باید حداقل داشته باشد:**

- claim_id
- product_id
- claim_text
- claim_type
- source_ref / source
- evidence_status
- created_at

**وضعیت محصول (Vertical Slice امروز):**

```text
DRAFT → ACTIVE
```

وضعیت‌های آینده (NEEDS_REVIEW، CONFLICT_UNRESOLVED، SUSPENDED، ARCHIVED) در طراحی قابل پیش‌بینی باشند؛ اگر برای مسیر امروز لازم نیستند، سیستم پیچیده برای آن‌ها ساخته نشود.

---

### فرمان ۴ — DeepSeek1: Security Gate

DeepSeek1 باید اطمینان دهد که مسیر ورود محصول باعث ایجاد مسیر امنیتی جدید و ناامن نشود.

**حداقل کنترل‌ها:**

- فقط کاربر مجاز بتواند Product Intake انجام دهد.
- Draft محصول در Recommendation واقعی قابل دسترسی نباشد.
- دسترسی به محصول متعلق به کاربر/مالک دیگر وجود نداشته باشد.
- داده حساس در log وارد نشود.
- عملیات Create / Update / Activate قابل ردیابی پایه باشد.

Rate Limit، Brute-force و Audit کامل Production همچنان **Version-2** هستند.

---

### فرمان ۵ — DeepSeek2: Data Architecture Review

DeepSeek2 باید بررسی کند که طراحی جدید:

- با مدل فعلی Product / Recommendation / Evidence ناسازگار نباشد.
- به Product A–D دست نزند.
- Migration غیرضروری ایجاد نکند.
- داده‌های قبلی را خراب نکند.
- امکان توسعه آینده را بدون بازنویسی اساسی حفظ کند.

اگر تغییر Schema ضروری نیست، Schema را تغییر ندهید.

---

### فرمان ۶ — Qwen2: Documentation & Archive

Qwen2 باید قرارداد و مسیر نهایی را مستند کند:

- چه چیزی وارد می‌شود؟
- چه چیزی اجباری است؟
- چه چیزی Unknown است؟
- چه چیزی نیازمند Source است؟
- چه زمانی محصول Active می‌شود؟
- چه زمانی وارد Recommendation می‌شود؟

همچنین یک دستورالعمل کوتاه برای مالک محصول آماده شود تا در آینده بتواند محصول جدید را خودش وارد کند.

---

### فرمان ۷ — تست واقعی با یک محصول

پس از آماده شدن Vertical Slice، با یک ضدآفتاب واقعی از محصولات جدید گالری آزمایش شود.

**سناریو:**

1. ایجاد محصول  
2. مشاهده وضعیت DRAFT  
3. ثبت Identity  
4. ثبت Claim و Source  
5. بررسی  
6. فعال‌سازی  
7. مشاهده در مسیر Recommendation  
8. اطمینان از عدم تغییر محصولات قبلی  

این تست باید ثابت کند که هدف اصلی محقق شده:  
**مالک محصول می‌تواند محصول جدید را وارد کند، بدون اینکه هر بار برای ورود محصول نیاز به توسعه نرم‌افزار باشد.**

---

### فرمان ۸ — تست‌های ممنوعه / خارج از Scope

در این Change Set موارد زیر را توسعه ندهید:

- Pricing  
- Inventory Management  
- Redis  
- Product Versioning کامل  
- Variant Management پیچیده  
- Scheduled Activation  
- Multi-language  
- Bundle/Kit  
- Recommendation redesign  
- تغییر Scoring  
- تغییر Threshold  
- تغییر Hard Gate  
- تغییر Evidence Claims موجود  
- تغییر Product A–D  
- تغییر Seed  
- Refactor گسترده  

همه این موارد در صورت نیاز به **Version-2** منتقل شوند.

---

### فرمان ۹ — معیار موفقیت

Change Set تنها زمانی موفق است که:

- محصول جدید بدون تغییر کد (پس از اتمام Slice) قابل ثبت باشد.
- محصول ابتدا DRAFT باشد.
- Draft وارد Recommendation واقعی نشود.
- Claim بدون Source به‌عنوان حقیقت قطعی ثبت نشود.
- Active شدن کنترل‌شده باشد.
- Active Product در Recommendation قابل استفاده باشد.
- Product A–D بدون تغییر باقی بمانند.
- Pilot Flow بدون Regression باقی بماند.
- تست Authorization و Ownership سبز باشد.
- هیچ 5xx جدید ایجاد نشود.
- هیچ Migration غیرضروری ساخته نشود.
- مسیر ورود برای مالک محصول قابل استفاده باشد.

---

### فرمان نهایی

1. اول قرارداد کوچک را تثبیت کنید.  
2. سپس کوچک‌ترین پیاده‌سازی لازم را انجام دهید.  
3. سپس با یک محصول واقعی آزمایش کنید.  
4. اگر Vertical Slice سالم بود، متوقف شوید.  

**هدف این مرحله ساختن «سیستم عظیم مدیریت محصولات» نیست.**  

هدف این است:

> «وحید بتواند فردا یک ضدآفتاب جدید را خودش وارد کند و سیستم آن را درست، امن و قابل‌کنترل بشناسد.»

هر چیزی که برای رسیدن به این هدف ضروری نیست، فعلاً ساخته نشود.  
هیچ تغییر خارج از این فرمان مجاز نیست.

---

## TRACE STATUS (ثبت مستند)

```text
Actor: Grok2
Action: DOCS-ONLY registration of PO executive order
Path: 08-Meeting-Room/PRODUCT_INTAKE_VERTICAL_SLICE.md
Baseline Master: 666ee97cf7932f2ff90b8cdd9944edb34070377b
App code changed: NO
Seed / Product A–D changed: NO
Scoring / Hard Gate / Pilot Flow changed: NO
Implementation status: NOT STARTED — awaiting Qwen1 Data Contract + coordinated execution
Next: Qwen1 minimal contract → DeepSeek2 architecture check → Grok2 implementation under locked scope
```
