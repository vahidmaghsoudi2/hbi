# فعالیت ۳۹ — اعمال اصلاحات تأییدشده

## Current situation
هیچ review واقعی از متخصص و هیچ PO approval برای correction در این مسیر وجود ندارد؛ بنابراین **اصلاحی اعمال نشده است**. این activity correction workflow و gate را پیاده‌سازی می‌کند تا اصلاحات آینده فقط بعد از تأیید قابل اعمال شوند.

## Required conditions
Correction record must include ID/topic، description، specialist record ref، evidence refs، specialist acceptance within scope، PO approval/ref، baseline/target version و scope note. Applied status additionally requires an application receipt ref.

## Statuses
- `pending_specialist_review`
- `pending_PO_approval`
- `approved_ready_to_apply`
- `applied_with_trace`
- `incomplete_proposal`
- `invalid_version_change`

## Boundaries
- Specialist acceptance ≠ PO approval.
- PO approval alone does not create specialist evidence.
- `approved_ready_to_apply` does not claim code/docs changed.
- `applied_with_trace` only records receipt supplied; receipt is not independently verified by this module.
- No correction is fabricated or applied in this activity.

## Implementation
`app/domain/hair_color_approved_corrections.py` guarded correction validator; `tests/test_hair_color_approved_corrections.py` pending gates, approvals, version, receipt and fail-closed tests. Test/CI اجرا نشده است.

## Next
Activity 40 — reconcile review/evidence records to PO decisions and correction receipts; preserve pending status for all unsupported/unreviewed rules.
