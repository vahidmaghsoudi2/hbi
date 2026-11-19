# فعالیت ۲۷ — مدیریت توقف مسیر مشاوره و restart

## Stop request
درخواست مشتری برای توقف به‌صورت stop_request_id، case_version و suggestion_id ثبت می‌شود. فقط performed_steps که به‌صورت صریح ثبت شده‌اند نگهداری می‌شوند؛ planned/assumed steps اضافه نمی‌شوند. مسیر consultation متوقف است و auto-resume=false.

## اثر توقف
- درخواست توقف به معنای رد/قبول پیشنهاد یا execution consent نیست.
- توقف، dependent prior decisions را invalidates می‌کند.
- suggestion/case path قبلی خودکار ادامه نمی‌یابد.
- توقف به معنای closure نیست؛ closure تابع workflow جداگانه است.

## Restart gate
Restart فقط با version جدید و همهٔ checks تازه:
1. وضعیت مو fresh؛
2. داده‌های fresh؛
3. safety assessment fresh؛
4. rules/contract fresh؛
5. evidence fresh؛
6. restart authorization صریح.
اگر حتی یک مورد missing باشد، restart blocked. در صورت کامل بودن، فقط fresh evaluation تحت version جدید شروع می‌شود؛ acceptance، consent، specialist review و path قدیمی carry over نمی‌شوند.

## پیاده‌سازی و آزمون
`app/domain/hair_color_stop_restart.py` و `tests/test_hair_color_stop_restart.py` stop trace، performed steps، no auto-resume، version gate و fresh-check checklist را پوشش می‌دهند. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۲۸ — مدیریت DATA_GAP، KNOWLEDGE_GAP و ENGINE_FAIL و کنترل output در هر یک.
