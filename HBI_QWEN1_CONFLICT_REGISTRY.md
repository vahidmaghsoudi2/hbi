# HBI_QWEN1_CONFLICT_REGISTRY.md

**Reviewer:** Qwen1  
**Role:** WS-03 — Data Contract + Product/Evidence QA Master  
**Date:** 2026-08-26  
**Purpose:** ثبت اختلافات بین Contract v1.0 و Reality فعلی

---

## CRITICAL CONFLICTS

### Conflict #1: فیلد status در دیتابیس vs مدل پایتون

**Contract v1.0:**
- فیلد status با مقادیر DRAFT/ACTIVE تعریف شده

**Reality:**
- در مدل پایتون فیلد status وجود ندارد
- اما در سشن قبلی، Qwen1 ستون status با مقدار پیش‌فرض 'ACTIVE' به دیتابیس اضافه کرد

**تأثیر:**
- ناسازگاری بین مدل و دیتابیس
- احتمال خطای runtime

**اقدام پیشنهادی:**
- یا فیلد status را به مدل پایتون اضافه کنیم
- یا ستون status را از دیتابیس حذف کنیم

**اولویت:** 🔴 HIGH

---

### Conflict #2: فیلدهای inventory_confirmation و inventory_confirmation_date

**Contract v1.0:**
- فیلد inventory_confirmation (boolean) الزامی
- فیلد inventory_confirmation_date (datetime) الزامی

**Reality:**
- این فیلدها در مدل پایتون وجود ندارند
- این فیلدها در دیتابیس وجود ندارند

**تأثیر:**
- Contract v1.0 نمی‌تواند بدون تغییر اجرا شود

**اقدام پیشنهادی:**
- حذف این فیلدها از Contract v1.0 (توصیه می‌شود)
- یا افزودن این فیلدها به مدل و دیتابیس

**اولویت:** 🔴 HIGH

---

### Conflict #3: فیلتر qa_verdict در Recommendation

**Contract v1.0:**
- انتظار دارد qa_verdict=VALID در Recommendation فیلتر شود

**Reality:**
- Recommendation فقط identity_status را فیلتر می‌کند
- qa_verdict بررسی نمی‌شود

**تأثیر:**
- محصول با identity_status=VERIFIED اما qa_verdict=INVALID وارد Recommendation می‌شود

**اقدام پیشنهادی:**
- افزودن فیلتر qa_verdict=VALID به Recommendation (توصیه می‌شود)
- یا تغییر Contract v1.0 برای حذف این شرط

**اولویت:** 🔴 HIGH

---

## MEDIUM CONFLICTS

### Conflict #4: نام‌گذاری identity_status

**Contract v1.0:**
IDENTIFIED | PARTIALLY_IDENTIFIED | UNIDENTIFIED

**Reality:**
VERIFIED | PARTIAL_IDENTITY | CONFLICT | NEEDS_REVIEW

**تأثیر:**
- سردرگمی در مستندات و کد

**اقدام پیشنهادی:**
- تغییر Contract v1.0 برای استفاده از نام‌گذاری Reality (توصیه می‌شود)

**اولویت:** 🟡 MEDIUM

---

### Conflict #5: سطح qa_verdict (Product vs Claim)

**Contract v1.0:**
- qa_status در سطح Claim تعریف شده

**Reality:**
- qa_verdict در سطح Product تعریف شده

**تأثیر:**
- اختلاف معماری

**اقدام پیشنهادی:**
- حفظ qa_verdict در سطح Product (توصیه می‌شود)

**اولویت:** 🟡 MEDIUM

---

## LOW CONFLICTS

### Conflict #6: نام‌گذاری canonical_name vs product_name

**Contract v1.0:**
- فیلد canonical_name

**Reality:**
- فیلد product_name

**تأثیر:**
- سردرگمی جزئی

**اقدام پیشنهادی:**
- تغییر Contract v1.0 برای استفاده از product_name (توصیه می‌شود)

**اولویت:** 🟢 LOW

---

## SUMMARY

| سطح | تعداد |
|-----|-------|
| 🔴 CRITICAL | 3 |
| 🟡 MEDIUM | 2 |
| 🟢 LOW | 1 |
| **مجموع** | **6** |

---

**NO COMMIT / NO PUSH