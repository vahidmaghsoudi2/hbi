# فعالیت ۲۹ — ده سناریوی گفت‌وگویی

این ده سناریو **behavioral contracts** هستند؛ state یا workflow جدید نیستند.

| ID | سناریو | معیار |
|---|---|---|
| D01 | سؤال‌های متوالی | case/suggestion/version unchanged |
| D02 | توضیح دلیل ساده | متن کاربرپسند، بدون debug/internal details |
| D03 | دادهٔ ثبت‌شده یا سؤال دقیق | evidence refs یا missing-data disclosure |
| D04 | دادهٔ ضروری ناکافی | no definitive advice |
| D05 | تغییر هدف | new version + fresh evaluation |
| D06 | پیشنهاد ردشده | rejected ID/key not active again |
| D07 | پذیرش در برابر consent اجرا | acceptance does not authorize execution |
| D08 | سؤال پیش از تصمیم | question is not a decision |
| D09 | نبود evidence | reliable answer unavailable; no guessing |
| D10 | تغییر دادهٔ مؤثر | dependency invalidation; unrelated outputs preserved |

## تست
`app/domain/hair_color_dialogue_scenarios.py` قراردادهای ۱۰ مورد و reason explanation ساده را ثبت می‌کند. `tests/test_hair_color_dialogue_scenarios.py` تست‌های cross-module برای هر سناریو دارد. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۳۰ — تدوین سناریوهای تخصصی رنگ مو؛ سناریوهای دانش تخصصی جدا از ۱۰ سناریوی dialog control نگهداری شوند.
