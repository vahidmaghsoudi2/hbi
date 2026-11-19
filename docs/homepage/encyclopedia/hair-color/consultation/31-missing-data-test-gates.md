# فعالیت ۳۱ — آزمون داده‌های ناقص

## Required data matrix
برای initial generic review، ۹ ورودی لازم: target color، priorities، current base، current color by region، color history، other chemical history، regional map، safety screen و service constraints. برای product-specific claims دو مورد product identity و product evidence نیز لازم‌اند؛ این دو به مشاورهٔ generic الزام عمومی اضافه نمی‌شوند.

## وضعیت‌ها
- `needs_more_information`: required missing یا unknown؛ هیچ definitive personalized advice.
- `limited_review`: ورودی ثبت شده ولی image-only، source/confidence unknown/low؛ confirm decision-relevant fields.
- `conflict_review`: conflict در required field؛ dependent review متوقف.
- `data_complete_for_review`: فقط completeness، نه feasibility/validity.
- invalid/duplicate input → fail-closed.

## مرز
Data completeness از product knowledge completeness جدا است. دادهٔ کامل، KNOWLEDGE_GAP یا ENGINE_FAIL را رفع نمی‌کند و هیچ توصیهٔ شیمیایی را valid نمی‌کند.

## پیاده‌سازی و آزمون
`app/domain/hair_color_missing_data_gates.py` و `tests/test_hair_color_missing_data_gates.py` generic/product-specific requirements، unknown/missing، image-only uncertainty، conflict، duplicate و invalid را پوشش می‌دهند. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۳۲ — آزمون پیشنهادهای متعارض یا نامعتبر؛ candidate validation، duplicate/rank/conflict و fail-closed behaviors را cross-check کنید.
