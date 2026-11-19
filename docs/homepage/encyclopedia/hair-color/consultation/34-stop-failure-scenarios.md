# فعالیت ۳۴ — آزمون stop و failure

## Scenario matrix
SF01 safety stop؛ SF02 engine fail output suppression؛ SF03 data gap؛ SF04 knowledge gap؛ SF05 client stop/no auto resume؛ SF06 restart incomplete؛ SF07 fresh restart؛ SF08 workflow bypass؛ SF09 conditional output؛ SF10 scope exclusion.

## Cross-module tests
Tests exercise motor-state mapping، gap handling، stop/restart gate، workflow transitions، response-state mapping و option bundle suppression. Stop/Failure behaviors are controls, not technical hair-color oracle.

## پیاده‌سازی
`app/domain/hair_color_stop_failure_scenarios.py` scenario catalog؛ `tests/test_hair_color_stop_failure_scenarios.py` cross-module matrix. Test/CI اجرا نشده است.

## گام بعد
فعالیت ۳۵ — بررسی مستندات و شواهد هر قاعده؛ scientific/product claims باید evidence traceable داشته باشند و evidence gaps مانع claims باشند.
