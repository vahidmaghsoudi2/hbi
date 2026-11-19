# فعالیت ۳۷ — آماده‌سازی بستهٔ بررسی متخصص

## وضعیت
**Package prepared; not sent.** متخصص/گیرنده در repository مشخص نشده و هیچ delivery یا review انجام‌شده ادعا نمی‌شود.

## بسته
- ۱۵ review topic مطابق inventory فعالیت ۳۶؛
- اسناد موضوعی پشتیبان؛
- سؤال‌های تخصصی دقیق برای هر موضوع؛
- evidence request و scope boundaries؛
- template status fields برای reviewer/evidence/scope/decision.

## قواعد
- هیچ technical rule از قبل accepted نیست.
- owner-defined Natural Extra rule با scientific claim جداست.
- catalog label identity با chemistry claim متفاوت است.
- شش محور evidence خارج از scope اجرایی و acceptance باقی می‌مانند؛ در این package blocker نشده‌اند.
- متخصص می‌تواند reviewed/revision/not-applicable ثبت کند؛ پذیرش PO جداگانه است.

## پیاده‌سازی
`app/domain/hair_color_specialist_review_package.py` manifest topic/doc/question/evidence request؛ `tests/test_hair_color_specialist_review_package.py` coverage inventory، unique IDs، references و delivery status را بررسی می‌کند. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۳۸ — ثبت نظر متخصص برای هر قاعده؛ تا دریافت نظر واقعی، statusها pending می‌مانند.
