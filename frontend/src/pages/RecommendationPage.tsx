import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { generateRecommendations } from "../api/client";
import type { RecommendationDTO } from "../types/api";

export default function RecommendationPage() {
  const [caseId, setCaseId] = useState(() => sessionStorage.getItem("hbi_case_id") ?? "");
  const [concerns, setConcerns] = useState(() => sessionStorage.getItem("hbi_concerns") ?? "");
  const [items, setItems] = useState<RecommendationDTO[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onGenerate(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const token = sessionStorage.getItem("hbi_access_token");
    if (!token) {
      setError("ابتدا از مسیر Pilot توکن بگیرید.");
      setBusy(false);
      return;
    }
    try {
      const result = await generateRecommendations(
        {
          case_id: caseId.trim(),
          customer_profile: { concerns: concerns.trim() },
        },
        token
      );
      setItems(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section>
      <h1>Recommendation</h1>
      <p className="lead">
        <code>POST /api/v1/recommendations/generate</code> با مالکیت Case.
        فیلدهای AD-3 (score / eligibility / reasoning / availability) در صورت وجود نمایش داده می‌شوند.
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
          {busy ? "…" : "تولید Recommendation"}
        </button>
        <Link className="btn secondary" to="/pilot">
          بازگشت به Pilot
        </Link>
      </form>
      {error && <div className="alert error">{error}</div>}
      {items.length > 0 && (
        <div className="results">
          {items.map((r) => (
            <article key={r.recommendation_id} className="rec-item">
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
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
