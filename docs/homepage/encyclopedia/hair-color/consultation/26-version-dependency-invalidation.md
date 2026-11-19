# فعالیت ۲۶ — مدیریت تغییر هدف یا اطلاعات و invalidation وابستگی‌ها

## Versioning
هر تغییر مؤثر با old/new case version و changed input ثبت می‌شود. Target color change همیشه full fresh evaluation را trigger می‌کند و outputs/decisions قبلی را invalidates می‌کند.

## Dependency map
- current_base → base/regional assessment, feasibility, options, specialist review, client acceptance, execution consent, plan.
- regional_state → regional assessment and downstream feasibility/options/decisions.
- service_history → history/safety/feasibility/options/decisions.
- safety_screen → safety/feasibility/options/decisions.
- product_identity/evidence → family/feasibility/options/decisions.
- priorities/maintenance → target/family/feasibility/options/decisions.
- image_quality → base/regional assessment and downstream.
- target_color → full known outputs.
- Unknown input dependency → full conservative invalidation.

## Decision records
Dependent specialist review, client acceptance, and execution consent are explicitly invalidated; they do not auto-carry. Unaffected outputs remain preserved. Affected outputs require fresh evaluation as appropriate. No acceptance or consent is copied into new version.

## Implementation and tests
`app/domain/hair_color_version_invalidation.py` dependency registry and invalidation outputs; `tests/test_hair_color_version_invalidation.py` target/full, single/multiple dependency, unknown fail-closed, version validation, preserve/reset behavior. Test/CI not executed.

## Next
Activity 27 — manage consultation stop requests: record only performed steps, prohibit auto-resume, and require fresh evaluation for restart.
