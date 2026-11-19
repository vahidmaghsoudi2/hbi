# فعالیت ۱۸ — تعریف منطق انتخاب یک یا چند گزینه

## هدف و قرارداد
این فعالیت فقط candidateهایی را انتخاب می‌کند که از قبل توسط ارزیابی مستقل، از نظر فنی valid و دارای evidence traceable شده‌اند. ماژول تولید یا اعتبارسنجی شیمیایی نیست؛ به candidateهای ساختگی یا صرفاً preferred برچسب valid نمی‌دهد.

## قواعد انتخاب
- candidate با validity `validated`، evidence_refs غیرخالی و goal_fit_basis ثبت‌شده می‌تواند وارد فهرست review شود.
- unvalidated و rejected به‌عنوان گزینهٔ قابل ارائه حذف و علت exclusion ثبت می‌شود.
- اگر هیچ گزینهٔ معتبر باقی نماند: `no_valid_options`؛ به‌جای حدس، درخواست review/evidence.
- یک گزینهٔ معتبر: فقط همان یک گزینه؛ گزینهٔ اضافی ساخته نمی‌شود.
- چند گزینهٔ معتبر: ترتیب رتبهٔ صریح و مستند حفظ می‌شود؛ duplicate rank باعث `ranking_conflict` می‌شود.
- سقف گزینه‌های قابل ارائه ۳ است؛ بیش از ۳ valid به `too_many_valid_options` می‌رود و silently truncation ممنوع است.
- ID یا family تکراری fail-closed است.

## وضعیت‌ها
`options_ready_for_review`, `no_valid_options`, `ranking_conflict`, `too_many_valid_options`, `no_candidates`, `invalid_candidates`, `duplicate_option_ids`, `duplicate_families`.

## مرز ادعا
Valid بودن candidate در این ماژول فقط از ورودی ارزیابی و evidence references گرفته می‌شود؛ این کد خود شواهد را ارزیابی نمی‌کند. انتخاب گزینه، تأیید متخصص، پذیرش مشتری یا اجازهٔ اجرا نیست. هیچ فرمول/شیمی/ایمنی/نتیجه از family label استخراج نمی‌شود.

## پیاده‌سازی و آزمون
`app/domain/hair_color_option_selection.py` و `tests/test_hair_color_option_selection.py` شامل gateهای evidence، حذف گزینهٔ rejected/unvalidated، ترتیب، limit سه‌گزینه‌ای و خطاهای ورودی‌اند. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۱۹ — تعریف محدودیت‌های پیشنهاد؛ باید مشخص کند چه داده/مدرک/وضعیت‌هایی پیشنهاد را conditional، محدود، یا متوقف می‌کنند.
