# راهنمای پیاده‌سازی P4 — P4 Implementation Guide

**وضعیت:** ALIGNED WITH MASTER (WP-01..06 COMPLETE)  
**مرجع قرارداد:** `docs/P4_PRODUCT_INTAKE_GOVERNANCE_CONTRACT_V1.md`  
**مرجع قوانین:** `docs/01_project_control/PROJECT_RULES.md`  
**تاریخ هم‌ترازی:** 2026-09-07  
**Master SHA at alignment:** `42cc77ec5f8692407df58bb4be9d8a71fc93c52f`

## Reality Note
WP-01 through WP-06 Issues (#15–#20) are **CLOSED** on GitHub and corresponding changes are on `master`.
This guide no longer lists those packages as open residual scope.

Reference suites:
- `tests/test_product_compliance.py`
- `tests/test_wp05_api_auth_matrix.py`
- CI job `governance-tests` in `.github/workflows/test.yml`

## هدف
این سند مسیر اجرای Work Packageهای P4 و وضعیت فعلی آن‌ها را برای اعضای تیم و AIها روشن می‌کند.

## قانون طلایی
- **یک کار = یک مالک = مسئولیت صفر تا صد**
- بدون Evidence حدس نزنید.
- نواحی Frozen بدون Finding + تأیید PO باز نمی‌شوند.
- تا تأیید صریح PO به master ادغام نکنید.

## جریان کار کوتاه
1. Issue را از Backlog بردارید و کامنت بگذارید: «این کار را برمی‌دارم — ETA: <روز>».
2. شاخه بسازید: `p4/wp<id>-short-desc` از `origin/master`.
3. فقط تغییر حداقلی + تست روی **gap باقی‌مانده**.
4. تست محلی:
   ```
   pip install -r requirements.txt
   pip install pytest pytest-cov
   pytest -q tests/...
   ```
5. PR با قالب رسمی باز کنید و **CURRENT MASTER SHA** را در بدنه بنویسید.
6. درخواست بررسی PO؛ Merge فقط پس از خط تأیید PO.

## Work Packageها (وضعیت پس از Reality Alignment 2026-09-07)

| WP | Issue | Status on master | Evidence |
|----|-------|------------------|----------|
| WP-01 | #15 | **DONE / CLOSED** | TransitionService sole lifecycle writer; privileged residual noted in Acceptance Gate |
| WP-02 | #16 | **DONE / CLOSED** | `ProductUpdate` + `extra=forbid`; PATCH 422 tests |
| WP-03 | #17 | **DONE / CLOSED** | EvidenceReadiness branch tests |
| WP-04 | #18 | **DONE / CLOSED** | Mutation log tests for lifecycle actions |
| WP-05 | #19 | **DONE / CLOSED** | API §16 deny-matrix (13 HTTP 403 tests) |
| WP-06 | #20 | **DONE / CLOSED** | `governance-tests` CI job + branch protection ruleset |
| WP-07 | — | **IN PROGRESS (this package)** | Formal Acceptance Gate + guide reconciliation |

## Formal Gate
See: `docs/09_gate_reports/P4_V1_ACCEPTANCE_RECONCILIATION_GATE.md`

## حفاظت شاخه master (اعمال‌شده)
Ruleset **HBI master protection** (`22449413`):
- Require PR for `master`
- Required status checks: `test`, `governance-tests`
- Block force-push and branch deletion

## یادداشت زبان
متن‌های حاکمیتی و راهنما برای خوانایی PO به فارسی نوشته می‌شوند.  
شناسه‌های فنی (مسیر فایل، نام متد، نام شاخه، برچسب CI) انگلیسی می‌مانند تا با ابزارها و AI سازگار بمانند.
