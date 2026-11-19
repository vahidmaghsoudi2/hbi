"""Ten approved dialogue-behavior scenarios; contracts, not workflow states."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class DialogueScenario:
    scenario_id: str
    label: str
    invariant: str

SCENARIOS=(
    DialogueScenario("D01","Sequential questions","Questions do not change case/suggestion/version."),
    DialogueScenario("D02","Simple reason explanation","User-facing explanation avoids internal code/debug details."),
    DialogueScenario("D03","Recorded data or specific missing input","Use evidence refs or disclose missing data."),
    DialogueScenario("D04","Insufficient required data","No definitive advice while required data is missing."),
    DialogueScenario("D05","Goal change","Create a new version and fresh evaluation."),
    DialogueScenario("D06","Rejected suggestion","Rejected ID/key must not return active."),
    DialogueScenario("D07","Acceptance vs execution consent","Acceptance does not grant execution consent."),
    DialogueScenario("D08","Pre-decision question","Question text is not acceptance/rejection/consent."),
    DialogueScenario("D09","Absent evidence","Reliable answer unavailable; do not guess."),
    DialogueScenario("D10","Changed effective data","Invalidate dependent outputs; preserve unrelated outputs."),
)

_SIMPLE_REASONS={
    "data_gap":"اطلاعات لازم هنوز کامل نیست؛ لطفاً مورد مشخص‌شده را تکمیل کنید.",
    "knowledge_gap":"برای این بخش پاسخ قابل اتکایی نداریم؛ حدس نمی‌زنیم.",
    "engine_fail":"در بررسی داخلی خطا رخ داد؛ این نوبت پاسخ متوقف شد.",
    "safety_stop":"به دلیل ملاحظهٔ ایمنی، ادامهٔ پیشنهاد متوقف شده است.",
    "scope_exclusion":"این درخواست خارج از محدودهٔ نسخهٔ فعلی است.",
    "condition_pending":"این پیشنهاد فقط پس از برآورده‌شدن شرط ثبت‌شده قابل بررسی است.",
    "candidate_reviewable":"این گزینه برای بررسی ثبت شده است؛ تصمیم یا اجازهٔ اجرا محسوب نمی‌شود.",
}

def simple_reason(reason_code: object)->str:
    if not isinstance(reason_code,str):
        return "دلیل قابل توضیح در دسترس نیست؛ برای جلوگیری از حدس، بررسی متوقف می‌شود."
    return _SIMPLE_REASONS.get(reason_code,"دلیل و محدودیت ثبت شده است؛ در صورت نبود اطلاعات معتبر، حدس نمی‌زنیم.")

def dialogue_scenarios()->tuple[DialogueScenario,...]:
    return SCENARIOS
