import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import {
  generateRecommendations,
  listRecommendationsByCase,
  createSpecialistOverride,
  createFeedback,
  getConsultationOutput,
  getExplainableSuitability,
} from "../api/client";
import type {
  RecommendationDTO,
  ConsultationOutputDTO,
  ExplainableSuitabilityDTO,
} from "../types/api";

export default function RecommendationPage() {
  const [caseId, setCaseId] = useState(() => sessionStorage.getItem("hbi_case_id") ?? "");
  const [concerns, setConcerns] = useState(() => sessionStorage.getItem("hbi_concerns") ?? "");
  const [items, setItems] = useState<RecommendationDTO[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [showAll, setShowAll] = useState(false);
  const [consultationOutput, setConsultationOutput] = useState<ConsultationOutputDTO | null>(null);
  const [problemId, setProblemId] = useState("P17");
  const [suitability, setSuitability] = useState<ExplainableSuitabilityDTO | null>(null);

  async function onGenerate(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setInfo(null);
    setItems([]);
    setShowAll(false);
    setBusy(true);
    const token = sessionStorage.getItem("hbi_access_token");
    if (!token) {
      setError("ابتدا از مسیر Pilot توکن بگیرید.");
      setBusy(false);
      return;
    }
    try {
      const request = {
        case_id: caseId.trim(),
        customer_profile: { concerns: concerns.trim() },
      };
      await generateRecommendations(request, token);
      // Render the persisted customer-facing view, not only the POST response.
      const persisted = await listRecommendationsByCase(caseId.trim(), token);
      const output = await getConsultationOutput(caseId.trim(), token);
      setItems(persisted);
      setConsultationOutput(output);
      setShowAll(false);
      sessionStorage.setItem("hbi_case_id", caseId.trim());
      sessionStorage.setItem("hbi_concerns", concerns.trim());
      setInfo(`تولید انجام شد؛ ${persisted.length} پیشنهاد واجد شرایط از سوابق ذخیره‌شده بازخوانی شد.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function onLoadSuitability() {
    setError(null);
    setSuitability(null);
    const token = sessionStorage.getItem("hbi_access_token");
    if (!token) {
      setError("توکن موجود نیست.");
      return;
    }
    if (!/^P(?:0[1-9]|[1-5][0-9]|6[01])$/.test(problemId.trim().toUpperCase())) {
      setError("کد مسئله باید بین P01 تا P61 باشد.");
      return;
    }
    setBusy(true);
    try {
      const result = await getExplainableSuitability(
        caseId.trim(),
        problemId.trim().toUpperCase(),
        token
      );
      setSuitability(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function onOverride(rec: RecommendationDTO, action: string) {
    setError(null);
    setInfo(null);
    const token = sessionStorage.getItem("hbi_access_token");
    if (!token) {
      setError("توکن موجود نیست.");
      return;
    }
    const reason = window.prompt("دلیل Override (اجباری برای Traceability):");
    if (!reason || !reason.trim()) {
      setError("دلیل Override الزامی است.");
      return;
    }
    try {
      // specialist_id is NOT sent — backend derives operator from authenticated token only
      const ovr = await createSpecialistOverride(
        {
          recommendation_id: String(rec.recommendation_id),
          case_id: caseId.trim(),
          action,
          reason: reason.trim(),
        },
        token
      );
      setInfo(`Override ثبت شد: ${ovr.override_id} (Recommendation اصلی تغییر نکرد)`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  async function onFeedback(rec: RecommendationDTO, outcome: string) {
    setError(null);
    setInfo(null);
    const token = sessionStorage.getItem("hbi_access_token");
    if (!token) {
      setError("توکن موجود نیست.");
      return;
    }
    try {
      const fb = await createFeedback(
        {
          case_id: caseId.trim(),
          source: "SPECIALIST",
          outcome,
          recommendation_id: String(rec.recommendation_id),
          comment: `Gallery feedback: ${outcome}`,
        },
        token
      );
      setInfo(`Feedback ثبت شد: ${fb.feedback_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <section>
      <h1>Recommendation</h1>
      <p className="lead">
        <code>POST /api/v1/recommendations/generate</code> با مالکیت Case.
        Specialist Override و Feedback بدون تغییر مخفی Recommendation اصلی.
        هویت Operator فقط از توکن احراز هویت.
      </p>
      <form className="card" onSubmit={onGenerate}>
        <label htmlFor="case_id">Case ID</label>
        <input
          id="case_id"
          value={caseId}
          onChange={(e) => setCaseId(e.target.value)}
        />
        <label htmlFor="concerns">نیازها / نگرانی‌ها</label>
        <textarea
          id="concerns"
          value={concerns}
          onChange={(e) => setConcerns(e.target.value)}
        />
        <button type="submit" disabled={busy}>
          {busy ? "…" : "تولید و بازخوانی Recommendation ذخیره‌شده"}
        </button>
        <button
          type="button"
          disabled={busy || !caseId.trim()}
          onClick={async () => {
            setError(null);
            setInfo(null);
            setItems([]);
            setShowAll(false);
            setBusy(true);
            const token = sessionStorage.getItem("hbi_access_token");
            if (!token) {
              setError("ابتدا از مسیر Pilot توکن بگیرید.");
              setBusy(false);
              return;
            }
            try {
              const persisted = await listRecommendationsByCase(caseId.trim(), token);
              const output = await getConsultationOutput(caseId.trim(), token);
              setItems(persisted);
              setConsultationOutput(output);
              setShowAll(false);
              sessionStorage.setItem("hbi_case_id", caseId.trim());
              setInfo(`از سوابق ذخیره‌شده ${persisted.length} پیشنهاد واجد شرایط بازخوانی شد.`);
            } catch (err) {
              setError(err instanceof Error ? err.message : String(err));
            } finally {
              setBusy(false);
            }
          }}
        >
          بارگذاری پیشنهادهای ذخیره‌شده
        </button>
        <Link className="btn secondary" to="/pilot">
          بازگشت به Pilot
        </Link>
      </form>
      {error && <div className="alert error">{error}</div>}
      {info && <div className="alert">{info}</div>}
      {consultationOutput && (
        <section className="card" aria-label="خروجی مشاوره">
          <h2>خروجی مشاوره</h2>
          <p>
            وضعیت: {consultationOutput.recommendation_status === "RECOMMENDATIONS_AVAILABLE"
              ? "پیشنهادهای واجد شرایط موجود است"
              : "در حال حاضر پیشنهاد تأییدشده‌ای وجود ندارد"}
          </p>
          <p>اطلاعات فرم مشاوره: {consultationOutput.consultation_context_status === "PRESENT" ? "ثبت شده" : "ثبت نشده"}</p>
          {consultationOutput.consultation_context && (
            <ul>
              <li>ناحیه‌ها: {consultationOutput.consultation_context.affected_areas.join("، ") || "ثبت نشده"}</li>
              <li>مدت: {consultationOutput.consultation_context.duration || "ثبت نشده"}</li>
              <li>شدت: {consultationOutput.consultation_context.severity ?? "ثبت نشده"}</li>
              <li>عوامل تشدیدکننده: {consultationOutput.consultation_context.aggravating_factors.join("، ") || "ثبت نشده"}</li>
              <li>محصولات فعلی: {consultationOutput.consultation_context.current_products.join("، ") || "ثبت نشده"}</li>
            </ul>
          )}
          <p>این خروجی فقط از اطلاعات ثبت‌شده پرونده و پیشنهادهای واجد شرایط ساخته شده است.</p>
        </section>
      )}
      <section className="card" aria-label="توضیح تناسب محصول">
        <h2>توضیح تناسب محصول</h2>
        <p>کد مسئله از بانک P01 تا P61 را وارد کنید. این بررسی فقط کاندیداها و موانع را توضیح می‌دهد و توصیه صادر نمی‌کند.</p>
        <label htmlFor="suitability_problem_id">کد مسئله</label>
        <input
          id="suitability_problem_id"
          value={problemId}
          onChange={(e) => setProblemId(e.target.value.toUpperCase())}
          maxLength={3}
        />
        <button type="button" disabled={busy || !caseId.trim()} onClick={onLoadSuitability}>
          {busy ? "…" : "بررسی و نمایش دلایل"}
        </button>
        {suitability && (
          <div className="results">
            <p>کاندیدای جاری: {suitability.candidate_count}</p>
            {suitability.candidates.length === 0 && (
              <p>برای این مسئله ProductProblemLink کاندیدای جاری ثبت نشده است. این نتیجه به معنی نامناسب بودن محصول نیست.</p>
            )}
            {suitability.candidates.map((candidate) => (
              <article className="rec-item" key={candidate.link_id}>
                <strong>{candidate.brand} · {candidate.product_name}</strong>
                <p>وضعیت تناسب: {candidate.suitability_status}</p>
                <ul>{candidate.explanations.map((reason, index) => <li key={index}>{reason}</li>)}</ul>
                <p>شاهد: {candidate.evidence_claim}</p>
                <p>منبع: {candidate.evidence_source_reference}</p>
                <p>توصیه‌پذیر: خیر، بررسی انسانی الزامی است.</p>
              </article>
            ))}
          </div>
        )}
      </section>
      {items.length > 0 && (
        <div className="results">
          {items.slice(0, showAll ? items.length : 5).map((r) => (
            <article key={String(r.recommendation_id)} className="rec-item">
              <div>
                <strong>{r.product_id}</strong>
                {r.final_score != null && (
                  <span className="score"> · score {r.final_score}</span>
                )}
              </div>
              <div>eligibility: {r.eligibility ?? r.eligibility_status ?? "—"}</div>
              {(r.reasoning || r.ranking_reasons) && (
                <p>{r.reasoning || r.ranking_reasons}</p>
              )}
              {r.pk_completeness?.domain_report && (
                <details>
                  <summary>گزارش ساختاریافتهٔ Product Knowledge · {r.pk_completeness.status}</summary>
                  <ul>{r.pk_completeness.domain_report.map((item) => (
                    <li key={item.field}><strong>{item.label}</strong> · {item.status}: {item.message}</li>
                  ))}</ul>
                </details>
              )}
              {Array.isArray(r.warnings) && r.warnings.length > 0 && (
                <aside className="alert" role="status" aria-label="هشدارهای مشاوره">
                  <strong>هشدارهای لازم برای اپراتور / پزشک</strong>
                  <ul>{r.warnings.map((warning, index) => (
                    <li key={index}>{typeof warning === "string" ? warning : JSON.stringify(warning)}</li>
                  ))}</ul>
                </aside>
              )}
              <div className="actions" style={{ marginTop: "0.5rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                <button type="button" onClick={() => onOverride(r, "ACCEPT")}>
                  Override: Accept
                </button>
                <button type="button" onClick={() => onOverride(r, "REJECT")}>
                  Override: Reject
                </button>
                <button type="button" onClick={() => onFeedback(r, "ACCEPTED")}>
                  Feedback: Accepted
                </button>
                <button type="button" onClick={() => onFeedback(r, "FOLLOW_UP_NEEDED")}>
                  Feedback: Follow-up
                </button>
              </div>
            </article>
          ))}
          {items.length > 5 && (
            <button type="button" onClick={() => setShowAll((value) => !value)}>
              {showAll ? "نمایش کمتر" : `نمایش ${items.length - 5} محصول دیگر`}
            </button>
          )}
        </div>
      )}
      {!busy && !error && items.length === 0 && (
        <div className="alert">
          سیستم در این مرحله پیشنهاد قابل‌اعتماد تولید نکرد. اپراتور پاسخ مشتری را بر عهده می‌گیرد؛
          کمبود اطلاعات یا Evidence باید در به‌روزرسانی بعدی برطرف شود.
        </div>
      )}
    </section>
  );
}
