# فعالیت ۱۹ — تعریف محدودیت‌های پیشنهاد

## قرارداد
محدودیت‌ها مستقل از candidate/option ثبت می‌شوند. هر مورد دارای شناسه، نوع، شرح، claim affected، blocking flag و در صورت condition، شرط دقیق است. هیچ limitation ناشناخته یا ناقص به‌صورت silent پذیرفته نمی‌شود.

## انواع
- `data_gap`: دادهٔ ضروری برای claim وابسته مفقود؛ blocking → درخواست اطلاعات.
- `knowledge_gap`: دانش یا evidence معتبر برای claim وجود ندارد؛ پاسخ حدسی ممنوع و claim متوقف/ارجاع می‌شود.
- `safety_stop`: توقف ایمنی؛ پیشنهاد اجرایی منتشر نمی‌شود.
- `scope_exclusion`: claim خارج از دامنه؛ خروجی recommendation برای آن claim ممنوع.
- `engine_fail`: خطای داخلی؛ run fail-closed و خروجی آن متوقف می‌شود.
- `condition`: پیش‌شرط مشخص؛ suggestion فقط conditional و شرط نباید satisfied فرض شود.

## تقدم تصمیم
`engine_fail` → `safety_stop` → `scope_exclusion` → `knowledge_gap` → `data_gap` → `conditional` → `reviewable`. در صورت چند محدودیت، وضعیت بالاتر اعمال می‌شود و IDs محدودیت‌های فعال حفظ می‌شوند. دسته‌های DATA_GAP، KNOWLEDGE_GAP و ENGINE_FAIL از هم جدا باقی می‌مانند.

## اتصال به وضعیت‌های معماری
این gate فقط چهار motor state مصوب را نگاشت می‌کند: suggestion_reviewable، conditional_suggestion، request_more_information، stop_or_referral. هیچ response-state جدید یا workflow-state جدیدی ایجاد نمی‌کند. reviewable به معنی تأیید متخصص، پذیرش مشتری یا consent اجرا نیست.

## پیاده‌سازی و آزمون
`app/domain/hair_color_proposal_limitations.py` و `tests/test_hair_color_proposal_limitations.py` انواع محدودیت، precedence، شرط، invalid و duplicate ID را پوشش می‌دهند. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۲۰ — تطبیق نهایی و تثبیت چهار وضعیت موتور تصمیم، بدون افزودن state تازه.
