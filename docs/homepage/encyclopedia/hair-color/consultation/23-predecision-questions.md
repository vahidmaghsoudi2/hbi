# فعالیت ۲۳ — مدیریت پرسش مشتری پیش از تصمیم

## قرارداد
در زمان `awaiting_client_confirmation` (یا هر وضعیت قبل از تصمیم)، سؤال مشتری یک پیام informational است؛ سؤال به‌تنهایی accept، reject، execution consent یا stop request محسوب نمی‌شود.

## رفتار
- سؤال با ID و متن ثبت می‌شود.
- پاسخ فقط از evidence refs موجود ارائه می‌شود؛ بدون evidence، reliable answer unavailable اعلام می‌شود و حدس ممنوع.
- case_state، suggestion_id و case_version تغییر نمی‌کنند.
- decision event فقط از یک ورودی ساختاریافتهٔ جداگانه و explicit ثبت می‌شود؛ از متن سؤال intent استخراج نمی‌شود.
- explicit decision eventهای مجاز در این قرارداد: accept_suggestion، reject_suggestion، execution_consent و stop_request. اثر/transition آن‌ها در فعالیت‌های مربوط جداگانه بررسی می‌شود.

## مرز
این ماژول پاسخ محتوایی به سؤال را تولید نمی‌کند؛ فقط policy و traceability کنترل می‌کند. پرسش «آیا درست است؟» یا «چرا؟» تصمیم مشتری نیست. قبول پیشنهاد با اجازهٔ اجرا متفاوت است.

## پیاده‌سازی و آزمون
`app/domain/hair_color_predecision_questions.py` و `tests/test_hair_color_predecision_questions.py` evidence/no-evidence، state/version preservation و event separation را پوشش می‌دهند. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۲۴ — مدیریت رد پیشنهاد؛ پیشنهاد ردشده نباید دوباره active شود و جایگزین‌ها فقط candidateهای valid باشند.
