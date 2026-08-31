# Home Page Polish — تعیین تکلیف

**Branch:** `feature/home-page-polish`  
**Owner:** Grok1  
**PO:** مهندس مقصودی

## تشخیص
1. `home.css` طراحی گالری (هدر، هیرو، نیاز، مسیر، محصولات، فوتر) داشت اما `NewHomePage.tsx` از کلاس‌های آن استفاده نمی‌کرد و شبیه فرم خام بود.
2. ورودی دوگانه: `index.html` → `main.jsx` در حالی که `App.tsx` و `main.tsx` مسیر اصلی TypeScript بودند.
3. `react-router-dom` در `package.json` نبود در حالی که در کد import می‌شد.
4. فقط یک محصول نشان داده می‌شد؛ نیازهای سریع به concerns وصل نبود.

## اصلاحات این پکیج
- بازطراحی `NewHomePage` با layout هنری RTL و اتصال واقعی API
- `main.tsx` هر دو CSS را load می‌کند؛ `index.html` به `main.tsx`
- افزودن `react-router-dom` به dependencies
- چیپ‌های نیاز → `concerns` → intake → recommendation
- UX برای خالی بودن کاتالوگ / خطا / No Match

## خارج از محدوده
- scoring / seed / recommendation engine
- بازنویسی کامل Catalog/Pilot (فقط Home به‌عنوان درِ ورودی)

## اجرا محلی
```bash
cd frontend && npm install && npm run dev
# Backend: uvicorn روی :8000 — proxy در vite.config.ts
```
