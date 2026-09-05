# راهنمای پیاده‌سازی P4 — P4 Implementation Guide

**وضعیت:** پیش‌نویس / DRAFT  
**مرجع قرارداد:** `docs/P4_PRODUCT_INTAKE_GOVERNANCE_CONTRACT_V1.md`  
**مرجع قوانین:** `docs/01_project_control/PROJECT_RULES.md`  
**تاریخ:** 2026-09-05

## هدف
این سند مسیر اجرای Work Packageهای P4 را برای اعضای تیم و AIها روشن می‌کند.

## قانون طلایی
- **یک کار = یک مالک = مسئولیت صفر تا صد**
- بدون Evidence حدس نزنید.
- نواحی Frozen بدون Finding + تأیید PO باز نمی‌شوند.
- تا تأیید صریح PO به master ادغام نکنید.

## جریان کار کوتاه
1. Issue را از Backlog بردارید و کامنت بگذارید: «این کار را برمی‌دارم — ETA: <روز>».
2. شاخه بسازید: `p4/wp<id>-short-desc` از `origin/master`.
3. فقط تغییر حداقلی + تست.
4. تست محلی:
   ```
   pip install -r requirements.txt
   pip install pytest pytest-cov
   pytest -q tests/...
   ```
5. PR با قالب رسمی باز کنید و **CURRENT MASTER SHA** را در بدنه بنویسید.
6. درخواست بررسی PO؛ Merge فقط پس از خط تأیید PO.

## Work Packageهای تعریف‌شده
| WP | عنوان | اولویت |
|----|--------|--------|
| WP-01 | محدودسازی update_governance_privileged | بالا |
| WP-02 | تست جلوگیری از دور زدن PATCH عمومی | بالا |
| WP-03 | پوشش Evidence readiness | متوسط |
| WP-04 | تست Mutation log برای lifecycle | متوسط |
| WP-05 | تست یکپارچه مجوز API | بالا |
| WP-06 | مستندات و CI حاکمیتی | پایین |

## Project Board پیشنهادی
نام: **P4 Governance Implementation**  
ستون‌ها: Backlog → To Do → In Progress → Review → QA → Done

کارت‌ها را به Issueهای WP-01 تا WP-06 لینک کنید.

## حفاظت شاخه master (برای ادمین)
- Require PR reviews (حداقل ۱ — ترجیحاً شامل PO)
- Require status checks: unit-tests و (پس از ایجاد) governance-tests
- Enforce CODEOWNERS
- جلوگیری از force-push و حذف شاخه

## یادداشت زبان
متن‌های حاکمیتی و راهنما برای خوانایی PO به فارسی نوشته می‌شوند.  
شناسه‌های فنی (مسیر فایل، نام متد، نام شاخه، برچسب CI) انگلیسی می‌مانند تا با ابزارها و AI سازگار بمانند.
