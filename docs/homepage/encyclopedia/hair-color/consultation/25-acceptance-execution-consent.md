# فعالیت ۲۵ — تفکیک پذیرش پیشنهاد از اجازهٔ اجرا

## اصل
Client acceptance و execution consent دو event مستقل هستند و هر دو به case_version و suggestion_id مشخص متصل می‌شوند. قبول پیشنهاد هرگز execution consent را خودکار ایجاد نمی‌کند.

## قرارداد
- Decision record برای هر نسخه/پیشنهاد مشخص ساخته می‌شود.
- Acceptance: pending / accepted / rejected.
- Execution consent: pending / granted / withheld؛ default pending.
- consent فقط پس از acceptance صریح همان suggestion قابل ثبت است.
- نسخه/پیشنهاد mismatch باعث stale rejection می‌شود.
- اجرای واقعی تنها زمانی از این gate مجاز است که candidate معتبر، specialist approval، acceptance و consent جداگانه وجود داشته باشند و safety stop فعال نباشد؛ workflow همچنان execution authorization و state transition جداگانه لازم دارد.
- Reject → consent ممنوع. Withheld/pending → authorization ممنوع.
- تغییر version/suggestion، record جدید می‌خواهد؛ consent قبلی carry over نمی‌شود.

## مرز
این gate consent را ثبت و authorization facts را بررسی می‌کند؛ اجرای خدمت یا workflow state را تغییر نمی‌دهد. پذیرش مشتری به تنهایی execution authority نیست.

## پیاده‌سازی و آزمون
`app/domain/hair_color_acceptance_execution_consent.py` و `tests/test_hair_color_acceptance_execution_consent.py` default pending، separation، rejected/withheld، specialist/safety gates و stale identity را پوشش می‌دهند. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۲۶ — مدیریت تغییر هدف یا اطلاعات؛ versioning و dependency-based invalidation و عدم carry-forward acceptance/consent.
