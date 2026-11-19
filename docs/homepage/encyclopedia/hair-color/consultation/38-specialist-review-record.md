# فعالیت ۳۸ — ساختار ثبت نظر متخصص

## Purpose
ساخت قالب استاندارد برای ثبت نظر واقعی متخصص، بدون ساختن review یا approval فرضی. این فعالیت فقط intake/schema و validation را آماده می‌کند.

## Statuses
- `reviewed_with_comments`
- `revision_requested`
- `accepted_within_scope`
- `not_applicable`

## Required record fields
topic ID، outcome، reviewer reference، ISO date، evidence references، reviewed scope، findings، limitations، record reference.

## Controls
- topic باید در inventory فعالیت ۳۶ باشد.
- تاریخ نامعتبر و status ناشناخته رد می‌شوند.
- reviewer، evidence، scope، findings و limitations اجباری‌اند.
- Specialist نمی‌تواند Natural Extra owner-defined rule را به‌عنوان اختیار مالک قبول کند.
- Specialist acceptance در scope خودش PO acceptance یا execution authorization نیست.
- هیچ رکورد review واقعی در این فعالیت ثبت نشده؛ همه موضوعات pending باقی می‌مانند.

## Implementation
`app/domain/hair_color_specialist_review_record.py` schema/validation؛ `tests/test_hair_color_specialist_review_record.py` required fields، date، topic/status و owner boundary را پوشش می‌دهد. Test/CI اجرا نشده است.

## Next
Activity 39 — reconcile specialist review results against evidence audit; pending/revision/accepted scope must map back to rule IDs and remain traceable.
