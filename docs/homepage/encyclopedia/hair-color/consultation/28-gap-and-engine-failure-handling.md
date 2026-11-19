# فعالیت ۲۸ — مدیریت DATA_GAP، KNOWLEDGE_GAP و ENGINE_FAIL

## تفکیک
- DATA_GAP: اطلاعات لازم برای claim مشخص مفقود است؛ request_inputs دقیق ثبت می‌شود.
- KNOWLEDGE_GAP: منبع/دانش معتبر برای claim در دسترس نیست؛ پاسخ حدسی ممنوع. این مورد را با درخواست داده از مشتری حل‌شده فرض نکن.
- ENGINE_FAIL: خطای داخلی run؛ تمام خروجی همان run suppress می‌شود و retry با guess ممنوع.

## رفتار ترکیبی
DATA_GAP + KNOWLEDGE_GAP → فقط ورودی‌های مشخصِ data gap درخواست می‌شوند؛ claimهای knowledge gap همچنان بدون پاسخ معتبر می‌مانند. ENGINE_FAIL precedence دارد و suppress_run_output می‌کند. IDها و affected claims برای traceability حفظ می‌شوند.

## پیاده‌سازی و آزمون
`app/domain/hair_color_gap_handling.py` taxonomy و output policies؛ `tests/test_hair_color_gap_handling.py` distinct categories, mixed gaps, precedence, invalid and duplicate IDs را پوشش می‌دهد. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۲۹ — تدوین/تطبیق سناریوهای گفت‌وگویی ده‌گانه، به‌عنوان behavioral tests نه stateها.
