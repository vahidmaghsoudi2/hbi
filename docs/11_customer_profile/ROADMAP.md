# نقشه راه واحد پروفایل مشتری — v1

## فاز ۰ — تثبیت تصمیم (اکنون)
- Charter، Contract، Dictionary، Integration Map
- **Gate 0:** بدون تصویب PO برای Migration/UI اصلی، Schema بزرگ ساخته نشود

## فاز ۱ — Discovery گالری
- مشاهده ۲۰–۳۰ تعامل واقعی
- Top Visit Purposes، زمان ثبت، موانع فروشنده
- **Gate 1:** Quick Intake از نظر فروشنده قابل‌استفاده

## فاز ۲ — Backend پایه
- Customer (تقویت مدل فعلی)، Consent مستقل، Visit، ConsultationAnswer، TimelineEvent، Audit
- Guest بدون موبایل، UNKNOWN معتبر
- **Gate 2:** تست داده/دسترسی/رضایت/Audit

## فاز ۳ — Quick Intake + سؤال پویا
- مسیرهای MVP: ضدآفتاب، آبرسان، مو، محصول مشخص، پیگیری
- **Gate 3:** ≥۸۰٪ ثبت آزمایشی ≤۹۰ ثانیه

## فاز ۴ — اتصال Recommendation
- فقط محصول VERIFIED + موجودی + بدون نقض Claim/Safety
- Trace کامل به Visit و Evidence
- **Gate 4:** هر توصیه قابل توضیح

## فاز ۵ — خرید / عدم‌خرید + Timeline
- Outcome اولیه؛ fallback دستی تا POS
- **Gate 5:** Recommendation → Outcome متصل

## فاز ۶ — Follow-up و Outcome
- رضایت، واکنش، Safety escalation
- **Gate 6:** واکنش منفی مانع توصیه نامناسب بعدی شود

## فاز ۷ — Profile Facts + Freshness
- Candidate → Confirm-with-Customer → Confirmed
- **Gate 7:** بدون تأیید مشتری، Insight/Purchase → Fact نشود

## فاز ۸ — Decision Readiness
- READY / READY_WITH_UNKNOWN / CAUTION / REVIEW_REQUIRED
- **Gate 8:** فقط سؤال ضروری؛ UNKNOWN جعل نشود

## فاز ۹ — Pilot واقعی گالری
- ۲–۴ هفته، یک فروشنده/شیفت
- **Gate 9:** KPI سرعت و توضیح‌پذیری

## فاز ۱۰ — پیشرفته (پس از اثبات استفاده)
- Segmentation، Loyalty، POS کامل، Photo با رضایت صریح
