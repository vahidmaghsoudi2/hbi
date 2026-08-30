# گزارش پیشرفت واحد پروفایل مشتری

| مرحله | وضعیت |
|--------|--------|
| Merge به master (PR #6) | `d88f8a5` |
| تست واحد | ۵/۵ سبز |
| E2E intake→case→generate | بدون crash؛ ۰ توصیه روی DB خالی (طبیعی) |
| v1.1 | search نام + get by id + intake برای توکن اپراتور |

**API گالری:**
- `POST /api/v1/customers/intake`
- `POST /api/v1/customers/guest`
- `GET /api/v1/customers/search?q=`
- `GET /api/v1/customers/id/{id}`
- `GET /api/v1/customers/recommendation-profile`
