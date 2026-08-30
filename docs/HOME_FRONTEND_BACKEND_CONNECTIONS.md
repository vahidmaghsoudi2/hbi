# Home Frontend — Backend Connections

**Locked Commit:** `6800ea5bf7445ec073fe07d0b78889e445194fd9`  
**Page:** `frontend/src/pages/NewHomePage.tsx`  
**Status:** Digital Front Door — بدون Mock/Fake

## Endpoints Used in Home

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET    | `/api/v1/products/`          | نمایش نمونه محصول تأییدشده |
| POST   | `/api/v1/auth/pilot-token`   | دریافت توکن آزمایشی برای ادامه مسیر |
| POST   | `/api/v1/customers/guest`    | ایجاد حساب مهمان بدون نیاز به احراز هویت |
| POST   | `/api/v1/customers/intake`   | ثبت مراجعه مشتری و دریافت customer/case |
| GET    | `/api/v1/evidence/?product_id=` | دریافت شواهد محصول برای نمایش اعتماد |

## Notes
- تمام درخواست‌ها از `frontend/src/api/client.ts` انجام می‌شوند.
- هیچ داده Hardcoded یا Mock در صفحه اصلی استفاده نشده است.
- ذخیره‌سازی `hbi_case_id` و `hbi_customer_id` در sessionStorage انجام می‌شود.
- ذخیره‌سازی `hbi_concerns` در sessionStorage انجام می‌شود تا در صفحه Recommendation استفاده شود.
- تغییرات کد این صفحه بدون دستور مستقیم PO ممنوع است.
