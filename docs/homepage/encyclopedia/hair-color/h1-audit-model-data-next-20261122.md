# ممیزی H1 و مسیر تکمیل قرارداد/مدل داده — 2026-11-22

**وضعیت:** گزارش ممیزی read-only و پیشنهاد مسیر بعدی؛ Draft، بدون تصویب PO و بدون مجوز تغییر runtime.  
**دامنه:** Hair Color فقط؛ Adapter 0.2-draft، Schema، unit/integration tests، synthetic fixture contract و اسناد معماری.  
**مبنای master:** `cc567099a5d66e8656e55ca4436213e285094219` (پس از ادغام PR #551).  
**مبنای سند قرارداد و PO register:** commit ثابت `bde6dd7142badd7026a61af368ee36aa254c15a0`؛ فایل‌های منحصربه‌فرد PR #535 در master در مسیرهای README به commit ثابت پیوند دارند و نباید فرض شود هر لینک در master جاری است.

## 1. خلاصه اجرایی

- Adapter boundary نسخه `0.2-draft` در master پیاده‌سازی شده و tests/CI مربوط به PR #547 آن را تأیید کرده‌اند؛ این امر اثبات موتور مشاوره، دانش تخصصی، یا رفتار Case Store/Orchestrator نیست.
- قرارداد مفهومی Draft 0.2 و PO decision register D-01…D-08 در commit ثابت موجود است؛ **این اسناد بسیار مفصل‌تر از یک طرح اولیه‌اند** و حاوی مالکیت داده، provenance، fail-closed، versioning، traceability و auditهای مستند هستند.
- Fixture manifest S01–S15 نیز در commit ثابت دارای oracleهای ماشین‌خوان و traceability oracleهای ساختاریافته برای S11–S13 است. آن oracleها با صراحت `TEST_ORACLE_ONLY_NOT_WIRE_CONTRACT` علامت‌گذاری شده‌اند؛ وجودشان به معنی قرارداد runtime یا اجرای Case Store/Ledger نیست.
- بزرگ‌ترین کار باز، «از صفر طراحی مدل داده» نیست. کار دقیق‌تر: **تبدیل طراحی موجود به یک قرارداد اجرایی مرحله‌بندی‌شده، تعیین mapping wire-level، تعریف validation/traceability لازم و مشخص‌کردن مرزهای سرویس‌های مالک داده**؛ سپس PO و متخصص باید نقاط نیازمند تصمیم را جداگانه تأیید کنند.
- در این ممیزی هیچ کد، fixture، schema، محصول/کاتالوگ، دادهٔ مشتری یا رفتار runtime تغییر نکرده است.

## 2. شواهد و سطح ادعا

| منبع | شواهد | چه چیزی را اثبات می‌کند | چه چیزی را اثبات نمی‌کند |
|---|---|---|---|
| `app/hair_color/adapter.py` در master | request/response envelope، enums، validation، injected engine، deepcopy | مرز مستقل و اعتبارسنجی‌های فعلی پیاده‌سازی شده‌اند | correctness مشاوره، persistence، ledger، scientific rules |
| `tests/test_hair_color_adapter.py` | 26 test functions | assertions مرزی Adapter | 26 تست موتور تخصصی یا 26 سناریوی end-to-end |
| `tests/test_hair_color_synthetic_integration.py` | 6 functions، شامل 14 scenario parameterized | تمرین عبور synthetic S01–S14 و failure handling | production integration یا runtime case workflow |
| `tests/test_hair_color_adapter_schema_contract.py` | 2 tests | enum/schema drift checks و candidate/reference constraints | کامل بودن domain schema |
| `tests/schemas/hair-color-adapter-0.2-draft.schema.json` | envelope schema | شکل ساختاری envelope draft | domain-specific validation؛ schema خودش opaque sections را مستثنی می‌کند |
| Fixture contract v1 در commit ثابت | 15 fixtures؛ traceability oracle S11–S13 | test oracleهای ساختاریافته برای lineage/ledger/dependency | wire contract، اجرا یا correctness runtime |
| Adapter contract Draft 0.2 در commit ثابت | 1135 lines، شامل sections 4–7، 9، 10، 13 و auditهای افزوده | طراحی مفهومی، مالکیت و محدودیت‌ها، open questions و non-authorizations | PO approval برای production implementation یا اجرای runtime |
| PO decision register D-01–D-08 | معنای design-level و guardrails ثبت شده | تصمیم‌های معنایی مشخص با دامنهٔ approval محدود | مجوز اجرای schema/runtime یا حل تصمیم‌های باز |

## 3. Adapter: وضعیت واقعی H1

### 3.1 مثبت — پیاده‌سازی فعلی
- Request fields و operationهای مجاز بررسی می‌شوند.
- Case/target version مثبت و response-version alignment کنترل می‌شود.
- Engine/consultation states و reason codes محدود به enums فعلی هستند.
- Reason-code duplication رد می‌شود؛ `ENGINE_FAIL` نمی‌تواند به‌صورت consultation success برگردد.
- Summary، arrays و next-step object بررسی می‌شوند.
- حداکثر سه candidate؛ هر candidate باید object باشد.
- Candidate options بدون evidence refs رد می‌شوند؛ refs باید در request evidence context موجود باشند و duplicate نباشند.
- حالت‌های blocking و reason codes مانع options می‌شوند.
- prohibited chemical/execution fields و authoritative decision/workflow fields به‌صورت recursive رد می‌شوند.
- engine exception fail-closed می‌شود؛ engine-owned mutable input/output کپی می‌شود.

### 3.2 شکاف‌های واقعی — بدون تبدیل به FAIL بی‌مدرک

| ID | شکاف / محدودیت | نوع | اقدام پیشنهادی |
|---|---|---|---|
| H1-A | `ANSWER_QUESTION` در envelope، فیلد `question` را required نمی‌کند؛ نمونه تست request هم question را بیرون envelope می‌گذارد | Contract ambiguity/validation gap | در contract revision، requirement و schema condition برای question را مشخص؛ تست missing/blank/question-op mismatch |
| H1-B | `case_context` و `policy_context` عمدتاً opaque هستند | deliberate draft boundary؛ نه defect قطعی | domain sub-schema در proposal جدا، با provenance و knowledge-state؛ approval پیش از implementation |
| H1-C | evidence item schema عمدتاً `evidence_ref` را enforce می‌کند؛ candidate evidence binding و claim-level applicability کامل نیست | Traceability gap | تعریف claim/evidence link و validation owner؛ عدم ادعای validity فقط با ref |
| H1-D | candidate shape opaque است؛ Adapter evidence refs response-level را validate می‌کند، نه linkage مستقل هر candidate/claim | Traceability gap | contract-level candidate key + claim links + evidence links؛ persistent IDs را orchestration mint کند |
| H1-E | پاسخ option-bearing و response-level evidence list: اثبات نمی‌کند هر option با evidence مناسب خودش پشتیبانی می‌شود | Validation boundary | candidate-level evidence requirement و hard-constraint pass evidence در design review |
| H1-F | schema envelope cross-field rules و recursive prohibited fields را به runtime Adapter واگذار می‌کند | Design limitation | document the authoritative validator; add schema/runtime parity tests only after production-contract approval |
| H1-G | question request semantics/ledger lookup/publication-time freshness در Adapter نیست | correct ownership separation, runtime integration gap | Orchestrator/ledger contract و stale-publication gate؛ نه افزودن این اختیار به Adapter |
| H1-H | Adapter persistence، idempotency، event ordering، atomic compare-and-publish، retry یا run correlation را ندارد | intentionally outside boundary | service contract & integration architecture; define before persistent implementation |

**Severity:** موارد H1-A، H1-C، H1-D و H1-E باید پیش از contract production closure حل یا به‌صورت explicit محدود شوند. H1-G/H1-H در مرز Orchestrator/Case Store/Ledger/Workflow باید بررسی شوند. این جدول verdict علمی یا safety approval صادر نمی‌کند.

## 4. اصلاح ممیزی قبلی (دقت لازم)

برخی گزاره‌های گزارش قبلی بیش‌ازحد قطعی بودند و اینجا اصلاح می‌شوند:

1. **S09 permutation ranking:** Fixture S09 در manifest، input permutation و `ranking_stable_under_input_permutation` را صریحاً در assertions دارد. بنابراین «این معیار اصلاً در fixture وجود ندارد» نادرست است. Adapter unit test فقط تعداد candidateها را چک می‌کند؛ fixture oracle، ranking behavior را تعریف می‌کند ولی آن oracle به‌تنهایی execution/runtime proof نیست.
2. **S11–S13 traceability:** fixtureهای ثابت، `traceability_oracle` ساختاریافته برای lineage، run refs، suggestion refs، ledger snapshots، dependency outcomes و interaction events دارند. پس «fixture فاقد structured traceability است» نادرست است. شکاف باقیمانده این است که scope آن oracle صریحاً test-only است و هنوز wire-level/runtime binding و service behavior اثبات نشده.
3. **Schema opaque fields:** این موضوع در Schema به‌عنوان unresolved domain schema عمدی بیان شده است؛ باید به‌عنوان gap تکمیل contract ثبت شود، نه defect یا PO violation.
4. **CI:** CI موفق PR #547 فقط همان commit و tests/workflows اجراشده را تأیید می‌کند. در این نوبت tests locally اجرا نشده‌اند و 53 count صرفاً شمارش ساختار تست‌ها بود، نه claim اجرای محلی.

## 5. ماتریس traceability — وضعیت پوشش

| حوزه | Test/fixture evidence | وضعیت | گام بعدی |
|---|---|---|---|
| Envelope validation | 26 Adapter unit functions؛ schema drift tests | IMPLEMENTED / CI evidence on PR #547 | contract revision فقط برای gaps |
| Data sufficiency, conflict, product identity, knowledge gap | S02–S06 tests/fixtures | SYNTHETIC COVERAGE | product/scientific validation مستقل |
| Safety fail-closed | S07 + specialist-review blocked behavior | SYNTHETIC COVERAGE | policy evidence/PO review؛ نه production safety |
| Candidate count/no fabrication | S08–S10 tests/fixtures | SYNTHETIC COVERAGE | candidate-level evidence binding و ranking behavior execution |
| Question vs acceptance/consent | S11 fixture + adapter boundary test | TEST ORACLE / BOUNDARY COVERAGE | runtime event/Ledger/Orchestrator integration |
| Rejection/deactivation | S12 fixture oracle | TEST ORACLE | exact version binding, ledger state, runtime integration |
| Goal/target version change | S13 fixture oracle | TEST ORACLE | lineage tuple + invalidation/persistence/runtime integration |
| Stop/restart | S14 synthetic test | BOUNDARY ONLY | Workflow event, performed-step log, fresh evaluation service path |
| Engine failure | S15 | SYNTHETIC COVERAGE | run correlation, retry/idempotency, atomic publish policy |
| Evidence revision after client decision | PO proposal 2026-11-12 | OPEN / NO DECISION | PO review independently for A–D; no TTL/notification/consent policy inference |
| Product-specific expert validity | no production engine oracle | BLOCKED | exact identity/scope, official sources, specialist validation; no chemistry-rule activation |

## 6. Model-data implementation preparation (proposal, not runtime schema)

Model data should be built around ownership and immutable references rather than one oversized case blob. This is a decomposition proposal only; field names/types/identifiers below are not PO-approved wire schema.

### 6.1 Candidate-owned domains and authority
- **Case Store:** case identity, case version, goal/target version, source-attributed observations/reports, explicit knowledge states, snapshot creation.
- **Evidence Registry:** exact source/product/market/version/claim scope, validity status, source locator, retrieval/recorded dates, reviewed-by/approval state. Evidence is not automatically approved because it is retrievable.
- **Policy Registry:** versioned constraints and scope; policy ownership/review status.
- **Consultation Run:** request/run identity, immutable snapshot refs, target/case versions, policy/evidence snapshot refs, run outcome/failure stage.
- **Candidate:** run-local candidate key/content; no persistent suggestion ID minted by engine. Orchestrator assigns persistent suggestion identity only after validation.
- **Suggestion Ledger:** append-only decision events and authoritative active/rejected/accepted status derived under approved rules; acceptance distinct from execution consent.
- **Dependency Registry/Graph:** claim/output-to-data/evidence/policy/rule dependencies; impact must be explicit; unresolved impact is not assumed independent.
- **Workflow/Performed-Step Log:** stop, restart request, actual performed steps, workflow transitions; Workflow Engine authority.
- **Audit/Event Log:** actor/source, event type, timestamp, version refs, causation/correlation/idempotency fields as a design checklist; exact semantics need contract review.

### 6.2 Minimum lineage relation
Every publishable candidate should be traceable (design target) through:
`case_ref + case_version + target_version + run_ref + candidate_key + policy_snapshot_ref + evidence/claim links + rule_refs`
Persistent `suggestion_ref/version` and client decision events are assigned/owned outside the engine. A question about an existing suggestion must resolve its exact suggestion version against the authoritative ledger before display. No old candidate can be reactivated merely by a new model response.

### 6.3 Knowledge state and provenance
Keep the existing approved design meanings: `KNOWN`, `UNKNOWN`, `NOT_ASKED`, `MISSING`, `CONFLICT`, `NOT_APPLICABLE`. Preserve false as a known value, not a proxy for unknown. Each decision-relevant field needs source class, record ref, timestamp/recorded-time where available, and derivation relationship. Data reported by a client is not a specialist observation; a derived value is not raw evidence.

### 6.4 Evidence/claim relation
An evidence record should not be attached as a blanket citation to an entire case. The conceptual relation must capture:
- claim or rule being supported;
- evidence reference and exact scope (product identity/market/version where applicable);
- status/applicability and review provenance;
- dependent candidate/output refs;
- version and invalidation/reevaluation relation.
Unknown dependency impact should fail closed for affected publication; do not invent TTL or automatic revocation policy.

## 7. Recommended execution sequence (dependencies, deliverables, gates)

### Work package A — Contract-to-runtime gap closure (next coding proposal)
**Deliverable:** contract revision proposal with domain schemas/conditional request requirements and claim-to-candidate evidence links, plus tests mapping each change to existing D-01…D-08.  
**Not authorized in this draft:** implement schema/runtime changes or alter fixture oracle.  
**Exit:** wire mapping/validation changes identified; unresolved PO policy separated from technical gaps.

### Work package B — Model-data & ownership specification
**Deliverable:** one ownership matrix, event/version lineage table, minimum data/provenance schema proposal, dependency invalidation matrix, and publication-time validation sequence. Reuse existing contract sections 4–7, 9, 13; do not create competing architecture.
**Exit:** each entity/field has authoritative owner, immutable/current semantics, references and allowed mutation; PO review on unresolved behavior.

### Work package C — Synthetic service contract tests
**Deliverable:** separate synthetic tests for Orchestrator ↔ Case Store ↔ Ledger ↔ Workflow boundaries; S11–S14 runtime sequences; S09 ranking permutation; S15 run-scoped stale-output suppression.
**Exit:** assertions run on service boundaries, not just Adapter mocks; no customer data and no scientific claim.

### Work package D — Product-evidence validation packet
**Deliverable:** product identity/market/version and official-source index; evidence-to-claim matrix; review status and unresolved gaps, beginning with Bijourka per README priority. This is documentation/research preparation only; no formulas, processing instructions, safety recommendations or rule activation.
**Exit:** exact product/document identity verified and each claim independently reviewed/approved by the designated specialist. Catalogue snapshot remains unchanged.

### Work package E — Gate for any implementation beyond synthetic boundary
Before non-synthetic engine implementation, require explicit PO authorization for contract revision and a specialist-reviewed bounded evidence/rule set. Pilot/release remain separately blocked by the README and PO-66-09.

## 8. Explicit unresolved items (do not decide by implementation)

- Production wire mapping for manifest oracle labels S06 and S08, preserving their distinct meanings.
- `ANSWER_QUESTION` request field semantics and required question content.
- Domain shape and validation depth for case/policy snapshots.
- Candidate key semantics and per-candidate claim/evidence binding.
- Exact publication-time ledger/version/evidence freshness checks and atomicity.
- Run correlation, retry/idempotency and stale output suppression semantics.
- Evidence revision policy proposal A–D (notification, fresh evaluation, acceptance/consent, performed-step remediation); no automatic TTL/revocation/rollback/compensation/remediation decision.
- Any product-specific chemistry/safety/feasibility claim: must remain disabled until source scope and specialist validation.

## 9. Acceptance criteria for this audit artifact

- Evidence refs and file scope are identified; static claims are separated from runtime proof.
- Existing fixture traceability is acknowledged accurately; test-only scope is not overstated.
- Each gap has owner boundary and suggested next work; no new PO decision is implied.
- Synthetic-only data rule and no-runtime/production authorization remain explicit.
- No catalog, runtime, schema, fixtures, tests, or data have changed.

## 10. Source references

- Master README / Hair Color control: `docs/homepage/encyclopedia/hair-color/README.md`
- Adapter: `app/hair_color/adapter.py`
- Adapter unit tests: `tests/test_hair_color_adapter.py`
- Synthetic integration tests: `tests/test_hair_color_synthetic_integration.py`
- Schema: `tests/schemas/hair-color-adapter-0.2-draft.schema.json`
- Schema drift tests: `tests/test_hair_color_adapter_schema_contract.py`
- Fixed-commit contract Draft 0.2: `docs/homepage/encyclopedia/hair-color/adapter-contract-draft-v0.2.md`
- Fixed-commit PO decision register: `docs/homepage/encyclopedia/hair-color/adapter-contract-po-decision-register-draft-v0.1.md`
- Synthetic fixture contract: `tests/fixtures/hair-color-contract-v1.json`
- Synthetic fixture schema: `tests/fixtures/hair-color-contract-v1.schema.json`
- Evidence revision policy proposal (open): `docs/homepage/encyclopedia/hair-color/po-proposal-evidence-revision-after-client-decision-20261112.md`
