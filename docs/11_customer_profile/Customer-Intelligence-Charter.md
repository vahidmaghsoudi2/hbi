# Customer Intelligence Charter — v1

## تعریف
HBI یک سیستم **پشتیبان تصمیم** برای فروشنده و مشتری است؛ نه پرونده پزشکی، نه سامانه امتیازدهی زیبایی، و نه موتور فروش خودکار.

## چهار هدف همزمان
1. فروشنده در کمتر از ۹۰ ثانیه مراجعه را ثبت و مشاوره را شروع کند.
2. مشتری فقط داده ضروری همان مراجعه را بدهد.
3. سیستم از مراجعه، خرید و بازخورد «حافظه قابل‌ردیابی» بسازد.
4. هیچ Preference / Skin Fact / Outcome بدون توضیح و بدون کنترل انسانی به Fact قطعی تبدیل نشود.

## زنجیره عملیاتی
```
Customer Core
    → Visit / Consultation
    → Dynamic Questions
    → Answers + Source + Context + Time
    → Decision Readiness
    → Evidence-Gated Recommendation
    → Purchase / No-Purchase / Service
    → Outcome / Follow-up
    → Timeline + Customer Memory
```

## قانون Promotion
| نوع | ورود خودکار به Profile Fact؟ |
|-----|------------------------------|
| Raw Event (پاسخ جلسه) | خیر |
| Purchase Signal | خیر |
| Operator Observation | خیر |
| Derived Insight | خیر |
| تأیید صریح مشتری | **بله** |

## Out of Scope نسخه ۱
- Fact Promotion خودکار سه‌جلسه‌ای
- تحلیل تصویر / دستگاه
- Segmentation / RFM / Loyalty کامل
- POS یکپارچه کامل (فقط fallback دستی)
- Success Score عمومی محصول از Outcome یک مشتری
