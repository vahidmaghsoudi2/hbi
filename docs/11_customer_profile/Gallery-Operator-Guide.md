# راهنمای سریع فروشنده گالری — پروفایل مشتری v1

## هدف
ثبت مراجعه در کمتر از ۹۰ ثانیه و آماده‌سازی توصیه — بدون فرم طولانی.

## یک مسیر پیشنهادی

### ۱) Intake
```http
POST /api/v1/customers/intake
Authorization: Bearer <token>

{
  "name": "سارا محمدی",
  "mobile": "0912xxxxxxx",
  "concerns": "ضدآفتاب, پوست چرب",
  "consent": 1,
  "open_case": true
}
```

### ۲) پاسخ نمونه
```json
{
  "customer": { "customer_id": "CUST_...", "name": "...", "concerns": "..." },
  "case": { "case_id": "CASE_...", "case_type": "OPEN" },
  "recommendation_profile": { "concerns": "ضدآفتاب, پوست چرب" },
  "generate_hint": { "path": "POST /api/v1/recommendations/generate", "body": { ... } }
}
```

### ۳) درخواست توصیه (واحد Recommendation — تغییر نمی‌دهیم)
```http
POST /api/v1/recommendations/generate
{
  "case_id": "CASE_...",
  "customer_profile": { "concerns": "ضدآفتاب, پوست چرب" }
}
```

## مهمان بدون موبایل
```json
{ "name": "مهمان", "guest": true, "concerns": "آبرسان", "consent": 0, "open_case": true }
```

## اگر محصولی نیامد
طبیعی است (قرارداد No Hallucination). به مشتری بگویید گزینه‌ای با شواهد کافی نیست یا نیاز به سؤال بیشتر است — داده جعلی نشان ندهید.

## ویرایش بعدی
نگرانی همان موبایل را دوباره با `intake` بفرستید؛ concerns همان مشتری به‌روز می‌شود.
