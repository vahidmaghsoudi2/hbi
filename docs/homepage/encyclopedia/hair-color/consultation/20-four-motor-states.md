# فعالیت ۲۰ — تثبیت چهار وضعیت موتور تصمیم

## چهار state مصوب (فقط همین چهار مورد)
1. `suggestion_reviewable`: candidate معتبر و evidence-backed برای بازبینی؛ این به معنای approval/acceptance/consent اجرا نیست.
2. `conditional_suggestion`: candidate فقط با prerequisite/condition ثبت‌شده؛ شرط satisfied فرض نمی‌شود.
3. `request_more_information`: data gap ضروری؛ درخواست دادهٔ مشخص قبل از advice وابسته.
4. `stop_or_referral`: safety stop، knowledge gap، scope exclusion، engine failure یا نبود candidate معتبر؛ خروجی حدسی ممنوع.

## تقدم
`engine_fail` > `safety_stop` > `scope_exclusion` > `knowledge_gap` > `data_gap` > `no_valid_candidate` > `condition_pending` > `candidate_reviewable`.

این تقدم تنها motor state را انتخاب می‌کند؛ reason_code علت دقیق را نگه می‌دارد. DATA_GAP، KNOWLEDGE_GAP و ENGINE_FAIL یکی نمی‌شوند.

## مرز state
این چهار مورد motor state هستند، نه consultation response state و نه case workflow state. Conditional suggestion state جدید به فهرست پاسخ مشاوره اضافه نمی‌کند. No execution consent is implied.

## پیاده‌سازی و آزمون
`app/domain/hair_color_four_motor_states.py` و `tests/test_hair_color_four_motor_states.py` نگاشت canonical و precedence را پوشش می‌دهند. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۲۱ — تثبیت پنج وضعیت پاسخ مشاوره، با تفکیک motor state و response state.
