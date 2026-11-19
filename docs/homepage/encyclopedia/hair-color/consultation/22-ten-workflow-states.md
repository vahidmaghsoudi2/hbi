# فعالیت ۲۲ — تثبیت ده وضعیت گردش پرونده

## Canonical workflow states
1. `incomplete_acceptance`
2. `awaiting_evaluation`
3. `awaiting_test`
4. `safety_stopped`
5. `ready_for_specialist_decision`
6. `awaiting_client_confirmation`
7. `approved_for_execution`
8. `in_execution`
9. `needs_follow_up`
10. `closed` (terminal)

## Transition guard (concept implementation)
- Intake ناقص → evaluation فقط با intake_complete.
- Evaluation → awaiting_test فقط با test_required.
- Evaluation → ready_for_specialist_decision فقط با evaluation_complete و evidence_ready و بدون safety stop/تست باز.
- Specialist decision → client confirmation فقط با specialist_approved.
- Client confirmation → approved_for_execution فقط با specialist approval + client acceptance + **execution consent جداگانه**.
- Approved → in_execution فقط با execution_authorized.
- safety_stopped → awaiting_evaluation فقط با fresh_evaluation و restart_authorized؛ auto-resume ممنوع.
- awaiting_test → evaluation فقط با test_completed و fresh_evaluation.
- needs_follow_up → evaluation فقط با fresh_evaluation.
- closed terminal است؛ closure از اجرا با completion_recorded و closure اداری از سایر مسیرهای مجاز با close_authorized.
- هر transition ناموجود یا fact ناقص fail-closed است.

## تفکیک
Workflow state با چهار motor state و پنج consultation response state مستقل است. پذیرش مشتری به تنهایی execution consent نیست. Safety stop و stop request مسیر auto-resume ندارند.

## پیاده‌سازی و آزمون
`app/domain/hair_color_workflow_states.py` transition map و guards را پیاده می‌کند. `tests/test_hair_color_workflow_states.py` ده-state، مسیرهای مجاز/غیرمجاز، consent، restart، test و terminal closure را پوشش می‌دهد. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۲۳ — مدیریت پرسش مشتری پیش از تصمیم؛ سؤال نباید پذیرش/رد یا consent را تغییر دهد.
