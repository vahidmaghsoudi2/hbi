# HBI-PO-DEC-ENCYCLOPEDIA-PRIMARY-KB-001

**Title:** دانشنامه به‌عنوان بانک اصلی دانش مشاوره (Primary Knowledge Base)
**Status:** DECIDED / PO ACCEPTED — BINDING FOR TEAM
**Date:** 2026-11-17 (1405-08-26)
**Authority:** Product Owner — مهندس مقصودی
**Scope:** Homepage دانشنامه · Product Knowledge · Evidence · Recommendation
**Supersedes:** Any prior interpretation that «دانشنامه فقط مرجع انسانی/نمایشی/read-only است و در مسیر مشاوره نقشی ندارد»

---

## 1. Decision (متن الزام‌آور)

1. **دانشنامه** (از جمله «ویژگی محصولات پوستی» و «مشکلات پوستی») بانک اصلی دانش کسب‌وکار برای مسیر مشاوره است، نه یک دفترچه تزئینی.
2. هدف نهایی این است که محتوای تأییدشدهٔ دانشنامه وارد مسیر رسمی تصمیم سیستم شود و مشاوره بر پایهٔ همان دانش انجام شود.
3. واژه‌های فنی موجود در کد (`Evidence`, `ProductKnowledge`) ابزار پیاده‌سازی هستند، نه جایگزین مفهومی دانشنامه.
4. تفسیر قدیمی «دانشنامه فقط برای مطالعه اپراتور است و سیستم به آن نیاز ندارد» **باطل و غیرقابل استناد** است.
5. هر عضو تیم که به مخزن سر می‌زند باید این تصمیم را مبنا قرار دهد و به مستندات/نظرات قبلی که خلاف آن‌اند استناد نکند.

---

## 2. Why this decision was required

در بررسی عملی هوم‌پیج مشخص شد:

- موتور توصیه (`RecommendationService`) در runtime از `ProductKnowledge` + `Evidence` (تأییدشده) + پاسخ مشاوره Case استفاده می‌کند.
- UI دانشنامه در وضعیت فعلی بیشتر نمایش پژوهشی/خواندنی است و اتصال کامل به مسیر تصمیم ندارد.
- این شکاف باعث شده کار پژوهشی روی دانشنامه از نظر اثر مشاوره «بی‌نتیجه» به نظر برسد.

Product Owner تصریح کرد که این وضعیت قابل قبول نیست و منطق کسب‌وکار گالری ایجاب می‌کند دانشنامه پایه باشد.

---

## 3. Target operating model (binding direction)

```
دانشنامه تأییدشده (ویژگی محصول + مشکلات)
        ↓
ثبت/نگاشت رسمی به Evidence (با منبع و QA)
        ↓
تجمیع به ProductKnowledge
        ↓
Recommendation / Consultation
```

قواعد:

- بدون تبدیل محتوای دانشنامه به واحدهای رسمی قابل‌ممیزی، آن محتوا وارد تصمیم خودکار نمی‌شود.
- اما **هدف سیستم** دیگر «دانشنامه جدا از تصمیم» نیست؛ هدف «دانشنامه به‌عنوان منبع اصلی تغذیه مسیر تصمیم» است.
- ورود محصول (Product Master) همچنان لازم است تا هویت عملیاتی محصول وجود داشته باشد؛ این جایگزین دانشنامه نیست.

---

## 4. What is obsolete (must not be cited as current policy)

هر عبارت از این دست در مستندات/بحث‌های قبلی:

- «دانشنامه فقط مرجع انسانی است»
- «دانشنامه SoR ورود محصول نیست و در مشاوره نقشی ندارد» (به‌معنای نفی نقش راهبردی)
- «دانشنامه صرفاً نمایش/سازمان‌دهی است و نباید پایه تصمیم باشد»

این‌ها با تصمیم حاضر **جایگزین** می‌شوند.

نکته: محدودیت‌های فنی فعلی کد نفی نمی‌شوند؛ اما دیگر به‌عنوان سیاست مطلوب تفسیر نمی‌شوند.

---

## 5. Implementation boundary (important)

این سند:

- یک **تصمیم Product Owner** و جهت‌گیری الزام‌آور است.
- به‌تنهایی مجوز تغییر schema/API/دیتابیس نیست.
- کار فنی بعدی باید با حداقل تغییر معماری و حفظ مسیر فعلی Evidence → ProductKnowledge انجام شود (اتصال دانشنامه به همان مسیر، نه دور زدن QA).

---

## 6. Required team behavior

- قبل از هر طراحی/پیاده‌سازی مرتبط با مشاوره یا دانش محصول، این تصمیم را بخوانید.
- در PR/Issue جدید به این شناسه لینک دهید: `HBI-PO-DEC-ENCYCLOPEDIA-PRIMARY-KB-001`
- اگر مستندی هنوز تفسیر قدیمی را دارد، آن را اصلاح یا با بنر «SUPERSEDED» علامت بزنید.

---

## 7. Related records

- Issue #406 — Product Characteristics / permissions / Gates
- `docs/homepage/README.md` — homepage authority map (updated under this decision)
- `docs/homepage/product-management/README.md` — boundary text updated
- Runtime path today: `app/services/recommendation_service.py` (ProductKnowledge + Evidence)
- Aggregation path today: `app/services/product_knowledge_service.py`

---

**Recorded by instruction of Product Owner on 2026-11-17.**
