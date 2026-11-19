# فعالیت ۳۲ — آزمون پیشنهادهای متعارض یا نامعتبر

## Cross-module validation
Candidate bundle قبل از نمایش، به چهار motor state متصل می‌شود. فقط `suggestion_reviewable` اجازهٔ options review می‌دهد. Conditional، request information و stop/referral گزینهٔ unqualified را منتشر نمی‌کنند.

## Test matrix
- یک candidate valid؛ چند candidate valid با rank؛
- unvalidated / rejected / evidence-less exclusion؛
- duplicate rank، duplicate family؛
- >3 candidate (no truncation)؛
- DATA_GAP، KNOWLEDGE_GAP، SAFETY_STOP، ENGINE_FAIL؛
- conditional state؛
- invalid gate.

## مرز
این validation از upstream flags/evidence refs استفاده می‌کند و evidence را از نظر علمی verify نمی‌کند. Candidate conflict/invalid به output suggestion تبدیل نمی‌شود؛ reason/exclusion حفظ می‌شود.

## پیاده‌سازی و آزمون
`app/domain/hair_color_invalid_option_bundle.py` wrapper یکپارچه و `tests/test_hair_color_invalid_option_bundle.py` matrix above. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۳۳ — آزمون تغییر هدف و اطلاعات؛ versioning/invalidation integration را بررسی کنید.
