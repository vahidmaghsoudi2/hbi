# فعالیت ۳۰ — سناریوهای تخصصی رنگ مو

## دامنهٔ سناریوها
۱۲ archetype برای پوشش داده و safety gates ثبت شد: regional unevenness، unknown history، lightening، plant-dye uncertainty، chemical smoothing، ambitious target، unknown product identity، safety reaction/test، conflict، photo-only reference، ambiguous family، poor image quality.

## Oracle و پذیرش
این سناریوها behavioral/domain coverage templates هستند؛ **هیچ technical outcome، فرمول، compatibility یا رنگ نتیجه‌ای ساخته نشده**. تمام oracleها specialist_review_pending هستند. سناریو فقط پس از تکمیل required facts، approval متخصص و evidence refs می‌تواند ready_for_specialist_test شود. Missing facts، evidence و specialist approval جداگانه gate می‌شوند.

## پیاده‌سازی
`app/domain/hair_color_specialist_scenarios.py` catalog و readiness gate؛ `tests/test_hair_color_specialist_scenarios.py` coverage count، missing inputs، oracle pending، evidence missing و readiness را بررسی می‌کند. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۳۱ — آزمون داده‌های ناقص؛ با test cases و gap handling موجود cross-check و سپس پوشش یکپارچهٔ missing-data را توسعه دهید.
