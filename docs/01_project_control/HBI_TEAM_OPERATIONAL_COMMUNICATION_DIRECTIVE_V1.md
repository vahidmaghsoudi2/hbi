# HBI — دستورالعمل عملیاتی و ارتباطی تیم

**Document ID:** `HBI-TEAM-OPS-COM-001`  
**Title:** دستورالعمل عملیاتی و ارتباطی تیم (نسخه فشرده و الزام‌آور)  
**Version:** V1.0  
**Status:** **ACTIVE** (PO-authorized registration)  
**Date:** 2026-09-09  
**Baseline master (at registration):** `8ab76bb6975b138808ee442cd7ec7e9a606c8c15`  
**Authority:** Product Owner — مهندس مقصودی (رابط ۹ عضو تیم)  
**Type:** Mandatory team operating + communication policy  
**Does not replace:** `PROJECT_RULES.md`, `AGENTS.md`, IOV Policy, Mission Ownership Policy

---

## رابطه با اسناد قبلی (تطبیق)

| سند | نقش پس از این دستورالعمل |
|------|---------------------------|
| `docs/01_project_control/PROJECT_RULES.md` | **Entry Gate و قوانین پایه پروژه** — همچنان اجباری |
| `AGENTS.md` | محدودیت‌های فنی Agent (no direct master push، evidence) |
| `HBI_INDEPENDENT_OUTPUT_VERIFICATION_POLICY.md` | DONE ≠ VERIFIED ≠ ACCEPTED ≠ MERGED |
| `MISSION_OWNERSHIP_POLICY.md` | مالکیت مأموریت |
| `HBI_INTELLIGENT_CORE_ROADMAP_V1.md` | جهت استراتژیک هسته |
| **این سند (`HBI-TEAM-OPS-COM-001`)** | **ارتباط تیمی، قالب پاسخ، دسترسی GitHub، Domain chain، Circuit Breaker، فازهای F0–F7 فشرده** |

**قاعده تعارض:** در تعارض جزئیات، **PROJECT_RULES + origin/master + تصمیم صریح PO** غالب‌اند. این سند **تکمیل و فشرده‌سازی عملیاتی** است، نه جایگزینی خاموش قوانین پایه.

---

## دسترسی GitHub — الزام صریح PO (بسیار مهم)

**مخزن عمومی (Source of Truth):**  
**https://github.com/vahidmaghsoudi2/hbi**

| نقش | دسترسی |
|------|--------|
| **همه اعضای تیم (۹ نفر / همه Agentها)** | از ابتدا تا اکنون **دسترسی خواندن (Read)** به مخزن عمومی داشته و دارند |
| **ادعای «دسترسی ندارم»** | **پذیرفته نیست** — مخزن public است؛ خواندن برای همه ممکن است |
| **Grokها (و Agentهای مجاز نوشتن)** | علاوه بر خواندن، **دسترسی نوشتن** از طریق ابزارهای متصل / فرآیند پروژه دارند |
| **نوشتن روی Repository** | فقط با **دستور صریح مقصودی (PO)** به Grokها / Owner مجاز؛ بدون دستور PO، نوشتن/Merge خودسرانه ممنوع |
| **Merge به master** | فقط با مجوز صریح PO |

Expectation: هیچ عضو نباید کار را به‌خاطر «عدم دسترسی خواندن به GitHub» متوقف اعلام کند.

---

## ۱. مأموریت HBI

HBI یک **سیستم تصمیم‌یار مسئله‌محور** است؛ نه صرفاً موتور پیشنهاد محصول.

```
Customer → Case → Problem → Assessment → Factor
→ Evidence / Unknown / Conflict → Need → Product Requirements
→ Eligibility → Ranking → Recommendation → Human Decision → Outcome
```

**اصل:** ابتدا مسئله را بفهم؛ سپس درباره محصول تصمیم بگیر.

---

## ۲. قوانین غیرقابل‌نقض (فشرده — جزئیات در PROJECT_RULES)

| قانون | الزام |
|--------|--------|
| SOURCE OF TRUTH | فقط `origin/master` |
| CURRENT SHA | هر Audit با SHA واقعی |
| REALITY FIRST | قبل از طراحی/اجرا |
| NO ASSUMPTION / NO INVENTED DATA | بدون حدس و داده ساختگی |
| RAW EVIDENCE | SHA + Path + Evidence |
| EXISTENCE ≠ USAGE ≠ INTEGRATION ≠ VERIFIED | سطوح جدا |
| NO SILENT CHANGE | بدون مجوز تغییر نکن |
| FROZEN MEANS FROZEN | فقط با تصمیم رسمی |
| DONE DEFINED | چرخه کامل Done |
| REGRESSION + POST-MERGE VERIFY | الزامی |

---

## ۳. طبقه‌بندی اجباری ادعا

هر مطلب باید یکی از این‌ها باشد:

- **FACT** — در Repository اثبات شده  
- **CONTRACT** — توسط PO تصویب شده  
- **DESIGN PROPOSAL** — پیشنهاد؛ مجوز اجرا ندارد  
- **OPEN DECISION** — نیاز به PO  
- **UNKNOWN / NOT VERIFIED**  
- **CONFLICT**  

**ممنوع:** اجرای DESIGN PROPOSAL به‌عنوان FACT یا CONTRACT.

---

## ۴. Evidence-Bound Intelligence

هر نتیجه هوشمند باید پاسخ دهد:

1. چه می‌دانیم؟  
2. از کجا می‌دانیم؟  
3. چه نمی‌دانیم؟  
4. چه استنباط شده؟  

`Unknown ≠ Rejected` · `Inference ≠ Fact` · `Insufficient Evidence = خروجی معتبر`

---

## ۵. تفکیک‌های معماری اجباری

```
Factor ≠ Cause ≠ Question
Problem ≠ Need
Assessment ≠ Diagnosis Entity (بدون تصمیم رسمی)
Evidence ≠ Information
Customer Profile ≠ Current Case
Inference ≠ Documented Evidence
Unknown ≠ Conflict ≠ Rejected
```

---

## ۶–۷. زنجیره Domain و Cardinality

زنجیره هدف: Customer → Case → Problem → Assessment → Factor → Evidence/Unknown/Conflict  
وجود هر بخش فقط با Reality Audit اثبات می‌شود.

اصول فعلی: Customer→Case 1:N ؛ Case→Problem امکان 1:N ؛ Case می‌تواند ابتدا بدون Problem باشد ؛ `identified_needs` جایگزین Problem نیست.

موارد Open (بدون اجرای خودسرانه): FactorDefinition vs CaseFactor، مالکیت CaseFactor، مدل Evidence↔Factor، Persistent Unknown/Conflict Register.

---

## ۸–۱۰. Traceability · Provenance · Unknown/Conflict

زنجیره مطلوب توصیه:

```
Recommendation ← Product ← Requirement ← Need ← Assessment ← Problem ← Factor ← Evidence/Provenance
```

اگر بخشی اثبات نشده: **TRACEABILITY = NOT VERIFIED**

Provenance نمونه: `CUSTOMER_REPORT` · `OPERATOR_OBSERVATION` · `EXISTING_CUSTOMER_PROFILE` · `DOCUMENTED_EVIDENCE` · `HBI_INFERENCE`

Logger به‌تنهایی Persistent Register نیست.

---

## ۱۱. Reasoning / Recommendation (تا تصمیم رسمی)

بدون مجوز: تغییر Weighting، Ranking، Threshold، Formulaهای Frozen، گسترش بی‌نیاز ReasoningEngine.  
Recommendation Engine خارج از Scope تغییرات Domain خودسرانه است.

---

## ۱۲. فازهای عملیاتی هسته

| فاز | هدف |
|-----|------|
| F0 | Reality Audit + Capability Map |
| F1 | Customer → Case → Problem → Assessment → Factor |
| F2 | Adaptive Question / Information Completion |
| F3 | Assessment → Need → Product Requirements |
| F4 | Product Master / Gallery / Inventory |
| F5 | Eligibility → Ranking → Recommendation |
| F6 | Human Decision → Outcome |
| F7 | مسئله دوم → تعمیم → تثبیت V1 |

یک مسئله واقعی → یک Vertical Slice واقعی → Outcome → سپس تعمیم.

Vertical Slice = Input → State → Decision → Output → Persistence → Test → Evidence (Demo تنها کافی نیست).

---

## ۱۳. چرخه DONE

```
Reality Audit → Contract Check → Design → PO Authorization
→ Implementation → Test → Regression → Evidence Package
→ Independent Verification → PO Acceptance → Merge
→ Post-Merge Reality Verification
```

تا پایان این چرخه: **DONE نیست.**

---

## ۱۴. Circuit Breaker

توقف فوری اگر: تضاد Contract/P4/P5، تغییر Weighting/Ranking بدون مجوز، داده ساختگی، ابهام Schema، ادعای بدون Evidence، Design→Implement بدون Authorization.

گزارش:

```
BLOCKED
Reason / Evidence / SHA / Path / Decision Required
```

---

## ۱۵. ممنوع بدون Authorization

Model/Service/API جدید، Migration، تغییر Recommendation/Scoring، بازسازی Customer Profile، ERP/Accounting/POS، CRM کامل، پوشش همه مسائل، Demo به‌جای Vertical Slice.

---

## ۱۶. مالکیت کار

**ONE TASK = ONE OWNER = END-TO-END**  
همکاری آزاد است؛ **تصاحب مسئولیت** ممنوع است.

---

## ۱۷. ارتباط تیمی (پیام مستقیم PO)

مقصودی رابط ۹ عضو است. کیفیت پاسخ = سرعت تیم.

1. پاسخ **فشرده و یکپارچه**؛ چند صفحه پراکنده ندهید.  
2. پاسخ را **دو Response جدا** نکنید (Forward جدا می‌شود).  
3. **فارسی**؛ انگلیسی فقط برای Artifact/عبارت فنی لازم.  
4. قابل **Forward** بدون ویرایش دوباره.  
5. هدر کوتاه اجباری:

```
FROM: [Agent]
RECEIVED FROM: [منبع]
TO: [مقصد]
SUBJECT: [موضوع کوتاه]
```

6. ارجاع GitHub: **متن فایل را کپی نکنید** — فقط:

```
Repository: vahidmaghsoudi2/hbi
Branch:
SHA:
Path:
Section / Symbol (در صورت نیاز)
```

---

## ۱۸. استقلال فکری

تأیید بدون دلیل ممنوع. هر تأیید حداقل: Evidence + Reasoning + Impact.  
وگرنه: UNKNOWN / CONFLICT / DESIGN PROPOSAL.

---

## ۱۹. قالب استاندارد پاسخ فنی

```
FROM / RECEIVED FROM / TO / SUBJECT
STATUS: FACT | CONTRACT | DESIGN PROPOSAL | OPEN DECISION | UNKNOWN | CONFLICT
FINDINGS / EVIDENCE (SHA, PATH) / DECISION / RISKS / ACTION / BLOCKER
```

بخش خالی را با داده ساختگی پر نکنید.

---

## ۲۰. منابع اجباری پیش از کار فنی

```
docs/01_project_control/PROJECT_RULES.md
AGENTS.md
docs/01_project_control/HBI_INDEPENDENT_OUTPUT_VERIFICATION_POLICY.md
docs/01_project_state/MISSION_OWNERSHIP_POLICY.md
docs/01_project_control/HBI_INTELLIGENT_CORE_ROADMAP_V1.md
docs/01_project_control/HBI_TEAM_OPERATIONAL_COMMUNICATION_DIRECTIVE_V1.md  (این فایل)
origin/master @ CURRENT SHA
```

هیچ سندی جای Reality Audit روی `origin/master` را نمی‌گیرد.

---

## ۲۱. وضعیت گزارش‌شده WP-CORE-01 (نیازمند Verify با SHA جاری)

```
WP: WP-CORE-01
Domain Contract: PO ACCEPTED (HBI-PO-DEC-WP-CORE-01-001)
Implementation: NOT AUTHORIZED
Reference SHA (historical note): adbd450… — must re-verify against origin/master at use time
```

---

## ۲۲. اصل نهایی

```
REALITY BEFORE DESIGN
DESIGN BEFORE IMPLEMENTATION
AUTHORIZATION BEFORE EXECUTION
EVIDENCE BEFORE CLAIM
TEST BEFORE DONE
INDEPENDENT VERIFICATION BEFORE ACCEPTANCE
PO ACCEPTANCE BEFORE MERGE
POST-MERGE VERIFICATION AFTER MERGE
```

اگر نمی‌دانیم → می‌گوییم نمی‌دانیم. اگر اثبات نشده → می‌گوییم اثبات نشده. اختلاف را پنهان نمی‌کنیم.

**HBI با حدس ساخته نمی‌شود.**

---

**END OF HBI-TEAM-OPS-COM-001**
