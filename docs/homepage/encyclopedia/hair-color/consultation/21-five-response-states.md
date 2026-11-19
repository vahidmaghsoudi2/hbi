# فعالیت ۲۱ — تثبیت پنج وضعیت پاسخ مشاوره

## پنج response state (فقط همین پنج label)
1. `suggestion_reviewable_by_specialist`
2. `needs_more_information_or_test`
3. `needs_in_person_or_specialist_review`
4. `safety_stop_no_execution_suggestion`
5. `outside_first_version_scope`

## تفکیک با motor state
Conditional suggestion، motor state است؛ **response label ششم نیست**. Conditionalها با نوع prerequisite به یکی از response labelهای موجود map می‌شوند: data/test → needs more information or test؛ شرط unresolved یا in-person → needs in-person/specialist review. اگر condition type نامعلوم باشد، نگاشت محافظه‌کارانه specialist review است.

## نگاشت
- suggestion_reviewable → suggestion_reviewable_by_specialist.
- request_more_information → needs_more_information_or_test.
- conditional_suggestion → information/test یا specialist review؛ هیچ response label جدید.
- stop_or_referral با safety reason → safety_stop_no_execution_suggestion.
- stop_or_referral با scope reason → outside_first_version_scope.
- knowledge gap / engine fail / سایر stop-referral → needs_in_person_or_specialist_review به‌صورت fail-closed؛ reason code دقیق حفظ می‌شود.

## مرز
Response state با workflow state یا motor state یکی نیست. این نگاشت پذیرش مشتری یا consent اجرا تولید نمی‌کند.

## پیاده‌سازی و آزمون
`app/domain/hair_color_five_response_states.py` و `tests/test_hair_color_five_response_states.py` labelهای canonical و mappingهای condition/safety/scope/knowledge/engine/invalid را پوشش می‌دهند. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۲۲ — تثبیت ده وضعیت گردش پرونده؛ workflow از motor/response مستقل باقی می‌ماند.
