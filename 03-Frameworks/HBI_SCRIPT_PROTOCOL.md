# HBI — Script Protocol v2.1

## قوانین طلایی
1. در چت: فقط یک بلوک کامل PowerShell + حداکثر ۳ خط توضیح ضروری.
2. هر اسکریپت باید مستقیماً قابل Copy/Paste باشد.
3. اولین دستور: Set-Location E:\hbi
4. حتماً: $ErrorActionPreference = "Continue"
5. خروجی هر دستور مهم: 2>&1 | Out-String
6. هر اسکریپت باید Commit SHA فعلی GitHub/Origin را گزارش کند.
7. در پایان، گزارش نهایی با Set-Clipboard در Clipboard قرار گیرد.
8. پایان اسکریپت باید دقیقاً مشخص کند: GREEN, RED, YELLOW, BLUE.
9. خط پایانی راهنما: «در چت Ctrl+V بزنید و ارسال کنید.»
10. NO ASSUMPTION: فقط خروجی واقعی اجرا گزارش شود.
11. GitHub = Source of Truth: قبل از نتیجه‌گیری، حداقل git fetch origin و git rev-parse origin/master بررسی شود.
12. هیچ اسکریپتی بدون دستور صریح مجاز به: git reset --hard, git clean, حذف فایل، overwrite فایل موجود نیست.
13. اگر Working Tree تغییر دارد: تغییرات باید شناسایی و حفظ شوند؛ اسکریپت نباید خودسرانه آنها را حذف، stash یا restore کند.
14. هر اسکریپت باید یک هدف مشخص داشته باشد.
15. یک اسکریپت نباید هم‌زمان چند Task مستقل را انجام دهد.
16. کمینه مصرف Token: کد کوتاه، خروجی دقیق، بدون توضیح غیرضروری.

## استاندارد وضعیت
GREEN  = عملیات موفق و نتیجه قابل گزارش
RED    = شکست / خطای اجرایی
YELLOW = نتیجه ناقص یا نیازمند Reality Check
BLUE   = نیازمند تصمیم مدیریتی

## استاندارد گزارش
REPORT
-------
TASK:
STATUS:
LOCAL HEAD:
ORIGIN/MASTER:
ARTIFACTS:
FINDINGS:
NEXT ACTION:
RECIPIENT:

## اصل مهم
اجرای موفق یک دستور ≠ تأیید Artifact.
تست موفق ≠ Gate Approval.
گزارش یک AI ≠ Verification مستقل.
هر مرحله باید بر اساس Artifact قابل مشاهده و قابل بازتولید قضاوت شود.
