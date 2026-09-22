# Customer Profile Data Dictionary — v1.1

**Status:** ALIGNED TO APPROVED CUSTOMER PROFILE CONTRACT v1.1
**Scope:** vocabulary and behavioral data contract only.
**Implementation status:** reference dictionary; no schema change implied.


## Customer Core (موجود + هدف)
| کلید | نوع | الزام | توضیح |
|------|-----|-------|--------|
| customer_id | string PK | بله | شناسه |
| name / first_name | string | بله | نمایش |
| mobile | string | خیر | unique وقتی پر باشد (لایه سرویس) |
| lifecycle_status | string | آینده | ACTIVE / ARCHIVED |
| created_at / updated_at | datetime | بله | سیستم |

## Consent (current reality)

The existing binary `consent_to_store_data` flag and `consent_date` remain current repository fields. They are not treated as the final purpose-aware consent model defined by Contract v1.1.
Applicable law/regulation and organizational privacy/consent policy govern sensitive-data consent requirements.

| consent_type | مثال |
|--------------|------|
| PROFILE_RECORDING | ذخیره پروفایل |
| FOLLOW_UP_CONTACT | تماس پیگیری |
| MARKETING_CONTACT | بازاریابی |
| SENSITIVE_DATA_PROCESSING | داده حساس |
| PHOTO_PROCESSING | تصویر |

## Visit / Answer (canonical)
| فیلد | توضیح |
|------|--------|
| visit_purpose | هدف امروز |
| primary_concern | نگرانی اصلی |
| attribute_key / value | پاسخ پویا |
value_state | KNOWN / UNKNOWN / PREFER_NOT_TO_SAY / NOT_APPLICABLE
source | CUSTOMER / SELLER / SYSTEM / IMPORTED / OTHER
| recorded_at | زمان |

## Profile Fact (canonical)

Lifecycle/status: `ACTIVE`, `STALE`, `SUPERSEDED`, `REVOKED`, `CONFLICTED`, `UNKNOWN`.

`CANDIDATE` and `CONFIRMED` are not lifecycle/status values. Confirmation is represented through value/provenance/confirmation metadata without creating a second lifecycle vocabulary.

## Provenance

Canonical controlled provenance: `CUSTOMER`, `SELLER`, `SYSTEM`, `IMPORTED`, `OTHER`.

`OTHER` is reserved for a temporary, explicitly documented source and requires review/normalization before becoming a durable provenance category. Legacy labels are not canonical.

## Freshness

Freshness is attribute-specific, not a universal TTL. Current Need ends with its Visit/Case context; identity/contact changes drive review; skin/hair/scalp review is context/change-driven; preferences remain current until changed/rejected; safety constraints are reviewed when relevant information changes; historical interactions/outcomes do not expire; derived summaries are regenerated.

Fixed examples such as six-month skin TTL or twelve-month texture/scent TTL are removed from the canonical dictionary.

## Promotion rules

Visit information does not auto-promote to Profile Fact. Promotion requires explicit customer confirmation or authorized operator action with audit. Purchase/recommendation do not auto-create Preference. Smart Summary does not auto-create Fact.

## Slice 1 boundary

The next additive backend slice is limited to `ProfileFact`, `Preference`, and `ConstraintSafetySignal`. No Customer rewrite, UI, recommendation/scoring/evidence-gate change, or Smart Summary persistence is included.

## Pilot Outcome

Outcome is a separate historical concept and is record-only in the Pilot: it has no effect on scoring, recommendation eligibility, evidence gates, or automatic Promotion.