import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import {
  generateRecommendations,
  listRecommendationsByCase,
  createSpecialistOverride,
  createFeedback,
} from "../api/client";
import type { RecommendationDTO } from "../types/api";

export default function RecommendationPage() {
  const [caseId, setCaseId] = useState(() => sessionStorage.getItem("hbi_case_id") ?? "");
  const [concerns, setConcerns] = useState(() => sessionStorage.getItem("hbi_concerns") ?? "");
  const [items, setItems] = useState<RecommendationDTO[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [showAll, setShowAll] = useState(false);

  async function onGenerate(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setInfo(null);
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
      setItems(persisted);
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
            setBusy(true);
            const token = sessionStorage.getItem("hbi_access_token");
            if (!token) {
              setError("ابتدا از مسیر Pilot توکن بگیرید.");
              setBusy(false);
              return;
            }
            try {
              const persisted = await listRecommendationsByCase(caseId.trim(), token);
              setItems(persisted);
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
