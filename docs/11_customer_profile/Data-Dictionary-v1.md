# Customer Data Dictionary — v1

## Customer Core (موجود + هدف)
| کلید | نوع | الزام | توضیح |
|------|-----|-------|--------|
| customer_id | string PK | بله | شناسه |
| name / first_name | string | بله | نمایش |
| mobile | string | خیر | unique وقتی پر باشد (لایه سرویس) |
| lifecycle_status | string | آینده | ACTIVE / ARCHIVED |
| created_at / updated_at | datetime | بله | سیستم |

## Consent (هدف)
| consent_type | مثال |
|--------------|------|
| PROFILE_RECORDING | ذخیره پروفایل |
| FOLLOW_UP_CONTACT | تماس پیگیری |
| MARKETING_CONTACT | بازاریابی |
| SENSITIVE_DATA_PROCESSING | داده حساس |
| PHOTO_PROCESSING | تصویر |

## Visit / Answer (هدف)
| فیلد | توضیح |
|------|--------|
| visit_purpose | هدف امروز |
| primary_concern | نگرانی اصلی |
| attribute_key / value | پاسخ پویا |
| value_state | ANSWERED / UNKNOWN / PREFER_NOT_TO_SAY / NOT_APPLICABLE |
| source | CUSTOMER_SELF_REPORTED / OPERATOR_RECORDED |
| recorded_at | زمان |

## Profile Fact (هدف)
| state | معنی |
|-------|------|
| CANDIDATE | مشاهده شده، تأیید نشده |
| CONFIRMED | تأیید صریح مشتری |
| STALE | منقضی / نیاز بازبینی |
| SUPERSEDED | با Fact جدیدتر جایگزین |
| REVOKED | لغو |

## Freshness پیشنهادی (قابل پیکربندی پس از Pilot)
| داده | پیشنهاد |
|------|----------|
| هدف مراجعه | فقط همان جلسه |
| نوع پوست خوداظهاری | ۶ ماه |
| بافت/عطر | ۱۲ ماه |
| واکنش منفی | بدون انقضای خودکار |
| بودجه | جلسه یا ۳۰ روز |
