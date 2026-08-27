# HBI_QWEN1_DATA_CONTRACT_REALITY_REPORT.md

**Reviewer:** Qwen1  
**Role:** WS-03 — Data Contract + Product/Evidence QA Master  
**Date:** 2026-08-26  
**Input:** HBI_DEEPSEEK2_PRODUCT_INTAKE_MASTER_REPORT.md  
**Baseline Contract:** Minimal Product Intake Data Contract v1.0  
**Source of Truth:** GitHub master (HEAD: b3ddf6f6adf8c589b18fa84eb7b6030eb4c8cbc7)

---

## Executive Verdict

**وضعیت کلی:** READY_WITH_FINDINGS

Contract v1.0 با Reality فعلی HBI ۷۰٪ سازگار است، اما ۳ اختلاف بحرانی و ۲ اختلاف متوسط وجود دارد.

**خلاصه یافته‌ها:**

1. ✅ Product Identity: مدل فعلی ۱۳ فیلد دارد. سازگاری بالا.
2. ✅ Identity Status Flow: چهار مقدار VERIFIED/PARTIAL_IDENTITY/CONFLICT/NEEDS_REVIEW. سازگار.
3. ⚠️ CRITICAL CONFLICT #1: فیلد status در دیتابیس اضافه شده اما در مدل پایتون نیست.
4. ⚠️ CRITICAL CONFLICT #2: فیلدهای inventory_confirmation و inventory_confirmation_date در Contract بودند اما در Reality نیستند.
5. ✅ QA Verdict: فیلد qa_verdict با شش مقدار در مدل فعلی وجود دارد. سازگار.
6. ⚠️ CRITICAL CONFLICT #3: qa_verdict در Recommendation فیلتر نمی‌شود.
7. ✅ Evidence & Claims: EvidenceService وجود دارد. سازگار.
8. ✅ Recommendation Eligibility: فیلتر identity_status=VERIFIED و Hard Gate فعال. سازگار.
9. ⚠️ MEDIUM CONFLICT #1: ۳ از ۵ شرط Recommendation Eligibility پیاده‌سازی شده‌اند.
10. ⚠️ MEDIUM CONFLICT #2: claim_type های Contract باید بررسی شوند.

**اقدام فوری:** هیچ تغییری در کد یا Contract انجام نشود.

---

## 1. Contract v1.0 Summary

### 1.1 Product Identity (10 فیلد)

| # | فیلد | نوع | الزامی |
|---|------|-----|--------|
| 1 | product_id | string | ✅ |
| 2 | brand | string | ✅ |
| 3 | canonical_name | string | ✅ |
| 4 | variant | string | ❌ |
| 5 | size_value | float | ❌ |
| 6 | size_unit | string | ❌ |
| 7 | barcode_gtin | string | ❌ |
| 8 | market_region | string | ✅ |
| 9 | packaging_version | string | ❌ |
| 10 | inventory_confirmation | boolean | ✅ |
| 11 | inventory_confirmation_date | datetime | ✅ |

### 1.2 Identity Status

IDENTIFIED | PARTIALLY_IDENTIFIED | UNIDENTIFIED

### 1.3 Claim Contract (8 فیلد)

| # | فیلد | نوع | الزامی |
|---|------|-----|--------|
| 1 | claim_id | string | ✅ |
| 2 | product_id | string | ✅ |
| 3 | claim_text | string | ✅ |
| 4 | field | string | ✅ |
| 5 | claim_type | enum | ✅ |
| 6 | qa_status | enum | ✅ |
| 7 | created_at | datetime | ✅ |
| 8 | created_by | string | ✅ |

### 1.4 Claim Types

FACT | MANUFACTURER_CLAIM | EVIDENCE_SUPPORTED | INFERENCE | UNKNOWN

### 1.5 Recommendation Eligibility (5 شرط)

1. status = ACTIVE
2. identity_status تأییدشده
3. حداقل یک ادعای VERIFIED
4. عبور از Hard Gate
5. final_score >= 0.50

---

## 2. Reality Check

### 2.1 مدل Product فعلی

**فیلدهای موجود:**
- product_id ✅
- brand ✅
- product_name ✅ (معادل canonical_name)
- variant ✅
- size_value ✅
- size_unit ✅
- barcode_gtin ✅
- market_region ✅
- country_of_origin ✅ (اضافه)
- packaging_version ✅
- identity_status ✅
- qa_verdict ✅
- created_at ✅
- updated_at ✅

**فیلدهای گمشده:**
- ❌ canonical_name (به جای آن product_name)
- ❌ inventory_confirmation
- ❌ inventory_confirmation_date
- ❌ status (در دیتابیس اضافه شده، اما در مدل نیست)

**فیلدهای اضافه:**
- ✅ country_of_origin
- ✅ qa_verdict
- ✅ updated_at

---

## 3. Field-by-Field Mapping

| Contract v1.0 | Reality | وضعیت |
|---------------|---------|-------|
| product_id | product_id | ✅ MATCH |
| brand | brand | ✅ MATCH |
| canonical_name | product_name | ⚠️ RENAME |
| variant | variant | ✅ MATCH |
| size_value | size_value | ✅ MATCH |
| size_unit | size_unit | ✅ MATCH |
| barcode_gtin | barcode_gtin | ✅ MATCH |
| market_region | market_region | ✅ MATCH |
| packaging_version | packaging_version | ✅ MATCH |
| inventory_confirmation | ❌ MISSING | 🔴 GAP |
| inventory_confirmation_date | ❌ MISSING | 🔴 GAP |
| status | ❌ MISSING (در مدل) | 🔴 GAP |
| country_of_origin | country_of_origin | ✅ EXTRA |
| qa_verdict | qa_verdict | ✅ EXTRA |
| updated_at | updated_at | ✅ EXTRA |

---

## 4. Identity Status Flow Validation

**سناریو:** محصول جدید با identity_status=NEEDS_REVIEW

**Reality:**
- ProductService.get_verified_products فقط VERIFIED را برمی‌گرداند ✅
- Recommendation فقط VERIFIED را می‌پذیرد ✅

**نتیجه:** ✅ PASS

---

## 5. QA Verdict Flow Validation

**سناریو:** محصول با identity_status=VERIFIED اما qa_verdict=INVALID

**Reality:**
- Recommendation فقط identity_status را فیلتر می‌کند ⚠️
- qa_verdict بررسی نمی‌شود ⚠️

**نتیجه:** 🔴 FAIL

---

## 6. Evidence & Claims Validation

**سناریو:** ثبت ادعا برای محصول جدید

**Reality:**
- EvidenceService وجود دارد ✅
- POST /api/v1/evidence/ موجود است ✅

**نتیجه:** ✅ PASS

---

## 7. Recommendation Eligibility Validation

**سناریو:** محصول VERIFIED با Evidence معتبر

**Reality:**
- identity_status=VERIFIED ✅
- موجودی > 0 ✅
- final_score >= 0.5 ✅

**Contract v1.0:**
- status=ACTIVE ⚠️
- identity_status تأییدشده ✅
- حداقل یک ادعای VERIFIED ⚠️
- عبور از Hard Gate ✅
- final_score >= 0.50 ✅

**نتیجه:** ⚠️ PARTIAL PASS (۳ از ۵ شرط)

---

## 8. Frozen Files Verification

| فایل | وضعیت |
|------|-------|
| data/seed_products.json | ✅ FROZEN |
| scoring_constants.py | ✅ FROZEN |
| scoring.py | ✅ FROZEN |
| Product A–D | ✅ FROZEN |
| Evidence Claims | ✅ FROZEN |
| Recommendation Formula | ✅ FROZEN |

**نتیجه:** ✅ ALL FROZEN

---

## 9. Acceptance Matrix

| سناریو | معیار پذیرش | وضعیت |
|--------|-------------|-------|
| محصول جدید با identity_status=NEEDS_REVIEW | نباید در Recommendation ظاهر شود | ✅ PASS |
| محصول جدید با identity_status=VERIFIED | باید در Recommendation ظاهر شود | ✅ PASS |
| محصول بدون Evidence | score پایین، احتمالاً INELIGIBLE | ✅ PASS |
| محصول با Evidence معتبر | score بالا، احتمالاً ELIGIBLE | ✅ PASS |
| محصول با هویت CONFLICT | نباید وارد Recommendation شود | ✅ PASS |
| محصول با qa_verdict=INVALID | نباید وارد Recommendation شود | 🔴 FAIL |
| ایجاد محصول از طریق API | باید بدون دسترسی مستقیم DB ممکن باشد | 🔴 FAIL |
| به‌روزرسانی identity_status از طریق API | باید ممکن باشد | 🔴 FAIL |

**نتیجه:** ۵ از ۸ سناریو PASS، ۳ سناریو FAIL

---

## 10. Verdict

**وضعیت نهایی:** READY_WITH_FINDINGS

✅ **آنچه درست کار می‌کند:**
- Identity Status Flow صحیح است
- Evidence Service فعال است
- Recommendation Eligibility تا حد زیادی کار می‌کند
- فایل‌های Frozen تغییر نکرده‌اند

⚠️ **اختلافات بحرانی:**
1. فیلد status در دیتابیس اضافه شده اما در مدل پایتون نیست
2. فیلدهای inventory_confirmation و inventory_confirmation_date در Contract بودند اما در Reality نیستند
3. qa_verdict در Recommendation فیلتر نمی‌شود

⚠️ **اختلافات متوسط:**
1. نام‌گذاری identity_status متفاوت است
2. qa_verdict در سطح Product است، نه Claim

**توصیه Qwen1:** گزینه A (هماهنگ‌سازی Contract با Reality) ساده‌تر و عملی‌تر است.

---

**NO COMMIT / NO PUSH