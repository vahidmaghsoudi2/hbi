# Home Frontend — Backend Connections

**Locked Commit:** `6f3fcfcc6681a5e612b9ded401b2406ca3604c71`  
**Page:** `frontend/src/pages/NewHomePage.tsx`  
**Status:** Digital Front Door — بدون Mock/Fake

## Endpoints Used in Home

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET    | `/api/v1/products/`          | نمایش نمونه محصول تأییدشده |
| POST   | `/api/v1/auth/pilot-token`   | دریافت توکن آزمایشی برای ادامه مسیر |
| POST   | `/api/v1/customers/intake`   | ثبت مراجعه مشتری و دریافت customer/case |

## Notes
- تمام درخواست‌ها از `frontend/src/api/client.ts` انجام می‌شوند.
- هیچ داده Hardcoded یا Mock در صفحه اصلی استفاده نشده است.
- تغییرات کد این صفحه بدون دستور مستقیم PO ممنوع است.
