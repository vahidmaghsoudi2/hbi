import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { generateRecommendations } from "../api/client";
import type { RecommendationDTO } from "../types/api";

export default function RecommendationPage() {
  const [caseId, setCaseId] = useState(
    () => sessionStorage.getItem("hbi_case_id") ?? ""
  );
  const [concerns, setConcerns] = useState("");
  const [items, setItems] = useState<RecommendationDTO[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onGenerate(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
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
          customer_profile: concerns.trim()
            ? { concerns: concerns.trim() }
            : {},
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
        <code>POST /api/v1/recommendations/generate</code> با مالکیت Case. فیلدهای AD-3
        (score / eligibility / reasoning / availability) در صورت وجود نمایش داده می‌شوند.
      </p>

      {error && <div className="alert error">{error}</div>}

      <form className="card" onSubmit={onGenerate}>
        <label htmlFor="case_id">Case ID</label>
        <input
          id="case_id"
          value={caseId}
          onChange={(e) => setCaseId(e.target.value)}
          required
          placeholder="CASE-..."
        />
        <label htmlFor="concerns">Concerns (اختیاری — فقط در customer_profile)</label>
        <textarea
          id="concerns"
          rows={3}
          value={concerns}
          onChange={(e) => setConcerns(e.target.value)}
          placeholder="مثلاً: dryness, sensitive scalp"
        />
        <div className="row">
          <button type="submit" disabled={busy}>
            {busy ? "…" : "تولید Recommendation"}
          </button>
          <Link className="btn secondary" to="/pilot">
            بازگشت به Pilot
          </Link>
        </div>
      </form>

      {items.length > 0 && (
        <div className="card">
          <h2>نتایج ({items.length})</h2>
          <div className="rec-list">
            {items.map((r) => (
              <article key={r.recommendation_id} className="rec-item">
                <div>
                  <strong>{r.product_id}</strong>
                  {r.final_score != null && (
                    <span className="score"> · score {r.final_score}</span>
                  )}
                </div>
                <div className="meta">
                  eligibility: {r.eligibility ?? r.eligibility_status ?? "—"}
                </div>
                {(r.reasoning || r.ranking_reasons) && (
                  <div className="meta">{r.reasoning ?? r.ranking_reasons}</div>
                )}
                {r.availability && (
                  <div className="meta">availability: {r.availability}</div>
                )}
                {r.price != null && <div className="meta">price: {r.price}</div>}
              </article>
            ))}
          </div>
        </div>
      )}

      {!busy && items.length === 0 && !error && (
        <div className="alert muted">هنوز نتیجه‌ای تولید نشده است.</div>
      )}
    </section>
  );
}
