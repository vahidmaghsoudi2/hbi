import { useState } from "react";
import { runHairDialogueTurn } from "../api/client";
import type { HairDialogueState, HairDialogueTurnRequest, HairDialogueTurnResponse } from "../types/api";

const initialState: HairDialogueState = {
  case_id: "SYNTHETIC-ROW71-UI-001",
  case_version: "case-v1",
  goal_version: "goal-v1",
  active_proposal_id: null,
  active_proposal_case_version: null,
  active_proposal_goal_version: null,
  rejected_proposal_ids: [],
  client_decision: "NONE",
  execution_consent_for_proposal_id: null,
};

const proposalId = "SYNTHETIC-PROPOSAL-ROW71-001";
const steps: Array<{ label: string; request: (state: HairDialogueState) => HairDialogueTurnRequest }> = [
  { label: "پرسش اطلاعاتی اولیه", request: state => ({ action: "ANSWER_QUESTION", state, question_code: "STATUS_REASON", answer_code: "STATUS_REASON" }) },
  { label: "اتصال پیشنهاد مصنوعی", request: state => ({ action: "ATTACH_PROPOSAL", state, proposal_id: proposalId }) },
  { label: "پذیرش پیشنهاد", request: state => ({ action: "ACCEPT_PROPOSAL", state, proposal_id: proposalId }) },
  { label: "رضایت مستقل اجرای خدمت", request: state => ({ action: "RECORD_EXECUTION_CONSENT", state, proposal_id: proposalId, explicit_consent: true }) },
  { label: "پرسش اطلاعاتی بعدی", request: state => ({ action: "ANSWER_QUESTION", state, question_code: "PROCESS_LIMIT", answer_code: "PROCESS_LIMIT" }) },
  { label: "تغییر هدف و ابطال نسخهٔ قبلی", request: state => ({ action: "CHANGE_GOAL", state, new_goal_version: "goal-v2" }) },
];

function assertNonPublishingEnvelope(response: HairDialogueTurnResponse) {
  if (
    response.recommendation !== null ||
    response.display_allowed !== false ||
    response.client_visible !== false ||
    response.persistence !== "COMPUTED_ONLY"
  ) {
    throw new Error("قرارداد عدم انتشار/عدم ذخیره‌سازی API نقض شد؛ گردش متوقف شد.");
  }
}

export default function HairDialogueWorkbench({ adminToken }: { adminToken: string }) {
  const [state, setState] = useState<HairDialogueState>(initialState);
  const [stepIndex, setStepIndex] = useState(0);
  const [history, setHistory] = useState<HairDialogueTurnResponse[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function runNext() {
    if (!adminToken || busy || stepIndex >= steps.length) return;
    setBusy(true);
    setError(null);
    try {
      const response = await runHairDialogueTurn(steps[stepIndex].request(state), adminToken);
      assertNonPublishingEnvelope(response);
      setState(response.state);
      setHistory(previous => [...previous, response]);
      setStepIndex(previous => previous + 1);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(false);
    }
  }

  function reset() {
    setState(initialState);
    setStepIndex(0);
    setHistory([]);
    setError(null);
  }

  const latest = history[history.length - 1];
  return (
    <section className="card" aria-labelledby="hair-dialogue-workbench-heading" data-testid="hair-dialogue-workbench">
      <h2 id="hair-dialogue-workbench-heading">گردش داخلی گفت‌وگوی مصنوعی — ردیف ۷۱</h2>
      <p>این گردش فقط از API موجود <code>/api/v1/hair/dialogue/turn</code> استفاده می‌کند. شناسه و پیشنهاد ثابت مصنوعی‌اند؛ هیچ دادهٔ مشتری یا توصیهٔ شیمیایی وارد نمی‌شود.</p>
      <ol aria-label="مراحل گردش گفت‌وگو">
        {steps.map((step, index) => (
          <li key={step.label} data-testid="dialogue-step" aria-current={index === stepIndex ? "step" : undefined}>
            {step.label}{index < stepIndex ? " — انجام شد" : index === stepIndex ? " — نوبت فعلی" : ""}
          </li>
        ))}
      </ol>
      <dl className="hair-specialist-dl">
        <div><dt>شناسهٔ مصنوعی</dt><dd>{state.case_id}</dd></div>
        <div><dt>نسخهٔ پرونده</dt><dd data-testid="dialogue-case-version">{state.case_version}</dd></div>
        <div><dt>نسخهٔ هدف</dt><dd data-testid="dialogue-goal-version">{state.goal_version}</dd></div>
        <div><dt>تصمیم</dt><dd data-testid="dialogue-client-decision">{state.client_decision}</dd></div>
        <div><dt>رضایت اجرا</dt><dd data-testid="dialogue-execution-consent">{state.execution_consent_for_proposal_id || "ثبت نشده"}</dd></div>
        <div><dt>پیشنهاد فعال</dt><dd data-testid="dialogue-active-proposal">{state.active_proposal_id || "ندارد"}</dd></div>
      </dl>
      {latest && (
        <div className="alert" role="status" data-testid="dialogue-safety-envelope">
          recommendation=null · display_allowed=false · client_visible=false · persistence=COMPUTED_ONLY
        </div>
      )}
      {error && <div className="alert error" role="alert">{error}</div>}
      <div className="row">
        <button type="button" onClick={runNext} disabled={!adminToken || busy || stepIndex >= steps.length}>
          {busy ? "در حال ارسال به API…" : stepIndex >= steps.length ? "گردش کامل شد" : `اجرای مرحلهٔ ${stepIndex + 1}`}
        </button>
        <button type="button" className="secondary" onClick={reset} disabled={busy}>شروع مجدد نمونهٔ مصنوعی</button>
      </div>
      <p className="meta">انتقال‌های موفق: {history.length} از {steps.length} — پس از تغییر هدف، پیشنهاد، پذیرش و رضایت نسخهٔ قبلی باید پاک شوند.</p>
    </section>
  );
}
