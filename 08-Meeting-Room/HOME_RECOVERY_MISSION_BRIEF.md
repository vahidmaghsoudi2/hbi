# مأموریت بازیابی Home و آشتی واقعیت
## Home Recovery and Reality Reconciliation

تاریخ صدور: ۳۰ اوت ۲۰۲۶
صادرکننده: مهندس وحید مقصودی (Product Owner)
تهیه‌کننده سند: Qwen2 (مسئول مستندسازی و کنترل کیفیت آرشیو - هاب B)
گیرنده مأموریت: DeepSeek2 (Frontend Engineer / Recovery Specialist)
وضعیت: در حال اجرا (H0 - Reality Reconciliation)
اولویت: بحرانی

---

## ۱. هدف مأموریت
پیدا کردن، محافظت و آشتی دادن نسخه واقعی Home جدید با master فعلی گیت‌هاب، بدون ساختن دوباره از صفر.

---

## ۲. وضعیت فعلی (بر اساس Reality Check ۳۰ اوت)

| بخش | وضعیت |
|:---|:---|
| معماری Home جدید | APPROVED (تأییدشده توسط PO) |
| Roadmap Home | در GitHub ثبت شده |
| تفکیک Public / Pilot / Workspace | تعریف شده |
| Backend واقعی برای Recommendation | E2E تأیید شده |
| Frontend فعلی (HomePage.tsx) | Home قدیمی Catalog |
| Home جدید در master | وجود ندارد |
| Capability Map جدید | در master نیست |
| Implementation جدید Home | در master تأیید نشده |
| Recovery لپ‌تاپ | باید بررسی نهایی شود |

**SHA فعلی master:** 4554edde... (تأیید شود قبل از اجرا)

---

## ۳. شرح وظیفه DeepSeek2

### مرحله ۱: بررسی کامل لپ‌تاپ
- اسکن کامل E:\hbi و تمام زیرپوشه‌ها
- بررسی تمام branchهای محلی Git
- بررسی تاریخچه Git (commit history) برای یافتن نسخه‌های قبلی Home
- بررسی پوشه‌های backup محلی (در صورت وجود)

### مرحله ۲: شناسایی نسخه‌های Home
- یافتن تمام فایل‌های مرتبط با Home جدید (در لپ‌تاپ و Git history)
- تشخیص کدام نسخه جدید است و کدام قدیمی
- بررسی frontend/src/pages/HomePage.tsx فعلی (Catalog قدیمی)
- شناسایی هر فایل Home جدیدی که ممکن است در branchهای دیگر یا commitهای قبلی باشد

### مرحله ۳: تطبیق با master
- مقایسه نسخه پیدا شده با master فعلی
- شناسایی تفاوت‌ها
- تعیین اینکه آیا نسخه پیدا شده واقعاً جدید است یا خیر

### مرحله ۴: محافظت و تحویل
- اگر نسخه جدید واقعاً وجود دارد: آن را در یک branch جداگانه محافظت کنید، تمام تغییرات را با Evidence مستند کنید و گزارش کامل تهیه کنید.
- اگر نسخه جدید پیدا نشد: گزارش دهید که هیچ نسخه جدیدی یافت نشد و پیشنهاد دهید که آیا باید از صفر ساخته شود یا خیر.

### مرحله ۵: گزارش نهایی
تهیه گزارش کامل شامل: لیست تمام نسخه‌های Home پیدا شده، وضعیت هر نسخه، تطبیق با master و پیشنهاد اقدام بعدی.

---

## ۴. محدودیت‌های مطلق

### ممنوع
- ساختن Home از صفر (مگر اینکه PO صریحاً دستور دهد)
- تغییر frontend/src/pages/HomePage.tsx فعلی بدون مجوز
- Commit یا Push به master بدون تأیید PO
- حذف یا بازنویسی نسخه‌های قدیمی بدون مستندسازی
- حدس زدن محتوای Home جدید بدون Evidence

### مجاز
- خواندن و بررسی تمام فایل‌ها
- ایجاد branchهای موقت برای محافظت
- تهیه گزارش و مستندات
- پیشنهاد اقدام (اما اجرا فقط با مجوز PO)

---

## ۵. اصل حاکم
**NO ASSUMPTION:** هیچ ادعایی بدون Artifact واقعی پذیرفته نمی‌شود.

**Source of Truth:** GitHub CURRENT MASTER + Local Laptop Evidence

---

## ۶. ترتیب مراحل پروژه (طبق Roadmap رسمی)
- H0: Reality Reconciliation (مأموریت فعلی DeepSeek2)
- H1: Public Home Consolidation (پس از تکمیل H0)
- H2: Operational Workspace
- H3: Home Stats Contract
- H4: Product Intake Vertical Slice
- H5: Evidence/Product Review
- H6: Consultation
- H7: Future Expansion

---

## ۷. قانون ثبت وضعیت
از این به بعد، وضعیت هر مرحله باید در GitHub ثبت شود تا از تکرار باستان‌شناسی چت جلوگیری شود.

---

## تأییدیه PO
- [ ] مأموریت تأیید شد
- [ ] DeepSeek2 مجاز به اجرا است
- [ ] SHA فعلی master تأیید شد: 4554edde...

**تاریخ تأیید:** _______________  
**امضای PO:** مهندس وحید مقصودی
