# فعالیت ۳۵ — بررسی مستندات و شواهد هر قاعده

## Evidence classification
هر rule/claim با type و evidence source/ref طبقه‌بندی می‌شود؛ این activity evidence را تولید یا source validity را از خود اختراع نمی‌کند:
- owner_defined → owner decision ref؛ owner rule است، scientific claim نیست.
- catalog_identity → catalog snapshot ref؛ فقط هویت/label.
- general_scientific → credible official/scientific source + specialist review برای claim-sensitive domain.
- product_specific → exact product identity + official document + specialist review.
- specialist_rule → explicit specialist review evidence.
- anecdotal → signal only؛ به general rule تبدیل نمی‌شود.

## Statuses
`owner_defined_not_scientific`, `identity_only`, `supported_for_review`, `awaiting_specialist_review`, `evidence_pending`, `product_evidence_pending`, `evidence_quality_unverified`, `anecdotal_signal_only`, `source_mismatch`, invalid. `supported_for_review` به معنی product approval یا execution authorization نیست.

## Scope note
این فعالیت فقط evidence classification و traceability contract را می‌سازد. شش محور اسناد محصول که PO از مسیر اجرایی و معیار تکمیل خارج کرده، دوباره وارد gate یا blocker نمی‌شوند.

## Implementation/tests
`app/domain/hair_color_rule_evidence_audit.py` classification gate؛ `tests/test_hair_color_rule_evidence_audit.py` owner/catalog/product/scientific/specialist/anecdotal/missing/source mismatch را پوشش می‌دهد. Test/CI اجرا نشده است.

## Next
Activity 36 — prepare inventory of rules requiring specialist review. Inventory باید evidence status و domain scope را ثبت کند؛ هیچ rule pending به validated ارتقا داده نشود.
