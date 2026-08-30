# واحد پروفایل مشتری (Customer Profile / Customer Intelligence)

**وضعیت:** Phase 0 — Contract & Roadmap  
**Owner اجرایی:** Grok1  
**دستور شروع:** PO (مهندس مقصودی)  
**Branch:** `feature/customer-profile-unit`  
**Base master:** `403848ab82d0b76fce2e80105dee8ed046f73b79`

## هدف واحد
شناخت حداقلی و قابل‌ویرایش مشتری برای مشاوره فروش، پیگیری و توصیه Evidence-gated — بدون پرونده پزشکی و بدون حدس خودکار.

## اصل داده
```
RAW EVENT  ≠  PROFILE FACT  ≠  DERIVED INSIGHT  ≠  RECOMMENDATION
```

## فایل‌های این پوشه
| فایل | نقش |
|------|-----|
| `Customer-Intelligence-Charter.md` | مرز سیستم و اهداف |
| `ROADMAP.md` | فاز ۰ تا ۱۰ |
| `Integration-Map.md` | اتصال به فروش، Case، Recommendation، پیگیری |
| `CustomerProfile-v1-Implementation-Contract.md` | قرارداد نسخه ۱ |
| `Data-Dictionary-v1.md` | دیکشنری داده |
| `Editability-and-Versioning.md` | قابلیت ویرایش نسخه‌های بعدی |

## قوانین سخت
- Product A–D، Seed، Scoring، Hard Gate، Evidence Claims: **منجمد**
- مسیر Pilot فعلی (Customer → Case → Recommendation) شکسته نشود
- Fact دائمی فقط با تأیید صریح مشتری
- `UNKNOWN` / `PREFER_NOT_TO_SAY` / `NOT_APPLICABLE` مقادیر معتبر هستند
- تغییر Schema/UI اصلی پس از Gate 0 و در صورت نیاز مجوز Change Control

## ویرایش‌پذیری
تمام قراردادها versioned هستند (`v1`). نسخه‌های بعدی با فایل جدا یا بخش CHANGELOG در همین پوشه ثبت می‌شوند.
