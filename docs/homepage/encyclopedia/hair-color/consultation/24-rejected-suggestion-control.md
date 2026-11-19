# فعالیت ۲۴ — مدیریت رد پیشنهاد

## قرارداد رد
رد پیشنهاد current باید به suggestion_id و candidate_key/fingerprint پایدار متصل شود. هر دو identity و key در rejection trace حفظ می‌شوند؛ جلوگیری از resurfacing فقط با ID کافی نیست، بنابراین candidate_key نیز برای همان گزینه نگه داشته می‌شود.

## انتخاب جایگزین
- rejected ID یا rejected key هرگز active alternative نمی‌شود؛ حتی اگر با ID تازه و key قبلی بازگردد.
- candidate نامعتبر یا بدون evidence refs حذف می‌شود و علت ثبت می‌شود.
- فقط candidateهای valid و evidence-backed مرتب‌شده با rank صریح وارد review می‌شوند.
- یک valid → فقط یک alternative؛ چند valid → ترتیب rank؛ سقف ۳، بیشتر از آن fail-closed و clarification/refinement، بدون truncate.
- اگر valid alternative موجود نباشد، `no_valid_alternatives`؛ suggestion ردشده دوباره پیشنهاد نمی‌شود و candidate جدید fabricated نمی‌شود.

## مرز
Rejection trace تصمیم مشتری است، نه consent اجرا. Candidate-key stability باید در upstream evaluator فراهم شود؛ این ماژول fingerprint را خودش تولید یا شیمی/محتوا را ارزیابی نمی‌کند.

## پیاده‌سازی و آزمون
`app/domain/hair_color_rejected_suggestion_control.py` و `tests/test_hair_color_rejected_suggestion_control.py` rejection identity/key persistence، candidate validity/evidence، alternatives count، ranking و duplicate را پوشش می‌دهند. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۲۵ — تفکیک پذیرش پیشنهاد از اجازهٔ اجرا؛ acceptance نباید خودکار execution consent ایجاد کند.
