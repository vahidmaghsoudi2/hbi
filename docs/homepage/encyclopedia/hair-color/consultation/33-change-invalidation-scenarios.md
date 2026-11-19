# فعالیت ۳۳ — آزمون تغییر هدف و اطلاعات

## Scenario matrix
CH01 target change → full known-output invalidation + fresh evaluation.
CH02 current base → only dependent base/regional/feasibility/options/review/decision outputs.
CH03 service history → history, safety, and dependent outputs.
CH04 product evidence → family/product-dependent outputs; unrelated regional assessment preserved.
CH05 safety screen → safety and dependent approvals/consent invalidated.
CH06 multi-input change → dependency union.
CH07 unknown changed item → full fail-closed invalidation.
CH08 new case/suggestion version → decision records default pending; no carry-forward.
CH09 same version → reject.
CH10 unrelated outputs → preserve.

## Implementation/test
`app/domain/hair_color_change_invalidation_scenarios.py` lists ten test contracts. `tests/test_hair_color_change_invalidation_scenarios.py` cross-tests version invalidation and decision records. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۳۴ — آزمون stop/failure؛ safety stops، stop requests، restart، engine fail و no-auto-resume را یکپارچه cross-check کنید.
