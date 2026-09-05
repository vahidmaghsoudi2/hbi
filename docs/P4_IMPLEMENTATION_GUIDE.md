# راهنمای پیاده‌سازی P4 — P4 Implementation Guide

**وضعیت:** پیش‌نویس / DRAFT  
**مرجع قرارداد:** `docs/P4_PRODUCT_INTAKE_GOVERNANCE_CONTRACT_V1.md`  
**مرجع قوانین:** `docs/01_project_control/PROJECT_RULES.md`  
**تاریخ:** 2026-09-05

## Reality Note
Existing coverage was inspected before defining remaining scope.

Reference: `tests/test_product_compliance.py`

این Note ادعا نمی‌کند که همه الزامات قرارداد §18 پوشش کامل دارند؛ فقط ثبت می‌کند که قبل از تعریف Scope باقی‌مانده، پوشش موجود بررسی شده است.

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
3. فقط تغییر حداقلی + تست روی **gap باقی‌مانده**.
4. تست محلی:
   ```
   pip install -r requirements.txt
   pip install pytest pytest-cov
   pytest -q tests/...
   ```
5. PR با قالب رسمی باز کنید و **CURRENT MASTER SHA** را در بدنه بنویسید.
6. درخواست بررسی PO؛ Merge فقط پس از خط تأیید PO.

## Work Packageها (Scope پس از Reality Alignment)
| WP | Issue | Scope باقی‌مانده |
|----|-------|------------------|
| WP-01 | #15 | Guard/محدودسازی `update_governance_privileged`؛ TransitionService از این متد استفاده نمی‌کند؛ call site تست: `test_interface.py` |
| WP-02 | #16 | فقط gapهای facade/API که compliance پوشش نداده |
| WP-03 | #17 | فقط شاخه‌های evaluate تست‌نشده در EvidenceReadiness |
| WP-04 | #18 | QA_CHANGE / APPROVE / ACTIVATE / REJECT / ARCHIVE / IDENTITY — نه CREATE/SUBMIT |
| WP-05 | #19 | خانه‌های missing ماتریس §16؛ پوشش کامل NOT VERIFIED |
| WP-06 | #20 | CI governance-tests job + branch protection پس از توافق PO (قالب/Guide در PR #21) |

## Project Board پیشنهادی
نام: **P4 Governance Implementation**  
ستون‌ها: Backlog → To Do → In Progress → Review → QA → Done

کارت‌ها را به Issueهای #15 تا #20 لینک کنید.

## حفاظت شاخه master (برای ادمین)
- Require PR reviews (حداقل ۱ — ترجیحاً شامل PO)
- Require status checks: job تست موجود در `test.yml` و (در صورت ایجاد) governance-tests
- Enforce CODEOWNERS
- جلوگیری از force-push و حذف شاخه

## یادداشت زبان
متن‌های حاکمیتی و راهنما برای خوانایی PO به فارسی نوشته می‌شوند.  
شناسه‌های فنی (مسیر فایل، نام متد، نام شاخه، برچسب CI) انگلیسی می‌مانند تا با ابزارها و AI سازگار بمانند.
