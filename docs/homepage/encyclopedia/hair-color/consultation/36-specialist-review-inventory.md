# فعالیت ۳۶ — فهرست قواعد نیازمند متخصص

## Inventory
۱۵ موضوع review با scope و وضعیت pending ثبت شده‌اند؛ شامل مبانی رنگ، اصطلاحات، family/numbering boundary، base/target feasibility، regional state، history compatibility، product-specific claims، options ranking و safety/testing. این فهرست **موضوع review** است، نه مجموعهٔ قواعد فنی از پیش ساخته‌شده.

Natural Extra (SR09) owner-defined rule است؛ authority مالک پروژه جدا می‌ماند. هر ادعای فنی/شیمیایی وابسته، specialist review مستقل لازم دارد.

## Status control
- pending_specialist_review (default)
- owner_recorded (برای rule مالک‌تعریف‌شده، فقط trace)
- reviewed_pending_acceptance
- specialist_accepted (reviewer ref + evidence refs + scope لازم؛ PO acceptance جدا)
- not_applicable (scope rationale/trace لازم)

Owner-record برای specialist-required topic آن را specialist accepted نمی‌کند. Specialist review نیز جای PO acceptance را نمی‌گیرد.

## پیاده‌سازی و آزمون
`app/domain/hair_color_specialist_review_inventory.py` topic registry و review status gate؛ `tests/test_hair_color_specialist_review_inventory.py` default pending، owner/specialist separation، evidence/scope completeness و invalid statuses را پوشش می‌دهد. Test/CI اجرا نشده است.

## Next
Activity 37 — ارائهٔ اسناد به متخصص رنگ مو؛ بسته باید از این inventory و evidence map ساخته شود، بدون واردکردن شش محور خارج از scope.
