import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createCase, pilotToken } from "../api/client";
import type { CaseDTO, TokenPair } from "../types/api";

type Step = "auth" | "case" | "done";

export default function PilotPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>("auth");
  const [customerId, setCustomerId] = useState("CUST-PILOT-1");
  const [caseType, setCaseType] = useState("OPEN");
  const [token, setToken] = useState<TokenPair | null>(null);
  const [caseDto, setCaseDto] = useState<CaseDTO | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onAuth(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const pair = await pilotToken({ customer_id: customerId.trim() });
      setToken(pair);
      sessionStorage.setItem("hbi_access_token", pair.access_token);
      sessionStorage.setItem("hbi_refresh_token", pair.refresh_token);
      sessionStorage.setItem("hbi_customer_id", customerId.trim());
      setStep("case");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function onCreateCase(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setError(null);
    setBusy(true);
    try {
      const created = await createCase(
        { customer_id: customerId.trim(), case_type: caseType || "OPEN" },
        token.access_token
      );
      setCaseDto(created);
      sessionStorage.setItem("hbi_case_id", created.case_id);
      setStep("done");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section>
      <h1>مسیر Pilot</h1>
      <p className="lead">
        Authentication → Case → Recommendation. فقط قراردادهای واقعی Backend.
      </p>

      <div className="steps">
        <span className={`step ${step === "auth" ? "active" : "done"}`}>۱. احراز هویت</span>
        <span className={`step ${step === "case" ? "active" : step === "done" ? "done" : ""}`}>
          ۲. ایجاد Case
        </span>
        <span className={`step ${step === "done" ? "active" : ""}`}>۳. Recommendation</span>
      </div>

      {error && <div className="alert error">{error}</div>}

      {step === "auth" && (
        <form className="card" onSubmit={onAuth}>
          <h2>احراز هویت Pilot</h2>
          <p className="muted">
            endpoint: <code>POST /api/v1/auth/pilot-token</code> — فقط محیط non-production
          </p>
          <label htmlFor="customer_id">Customer ID</label>
          <input
            id="customer_id"
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
            required
            placeholder="CUST-PILOT-1"
          />
          <button type="submit" disabled={busy}>
            {busy ? "…" : "دریافت JWT"}
          </button>
        </form>
      )}

      {step === "case" && token && (
        <form className="card" onSubmit={onCreateCase}>
          <h2>ایجاد Case</h2>
          <p className="muted">
            قرارداد: <code>{"{"} customer_id, case_type? {"}"}</code> — فیلد concerns اینجا نیست.
          </p>
          <div className="alert ok">توکن دریافت شد. refresh_token نیز ذخیره شد.</div>
          <label htmlFor="case_type">Case type</label>
          <input
            id="case_type"
            value={caseType}
            onChange={(e) => setCaseType(e.target.value)}
            placeholder="OPEN"
          />
          <div className="row">
            <button type="submit" disabled={busy}>
              {busy ? "…" : "ایجاد Case"}
            </button>
            <button type="button" className="secondary" onClick={() => setStep("auth")}>
              بازگشت
            </button>
          </div>
        </form>
      )}

      {step === "done" && caseDto && (
        <div className="card">
          <h2>Case ایجاد شد</h2>
          <p>
            <strong>case_id:</strong> {caseDto.case_id}
          </p>
          <p>
            <strong>customer_id:</strong> {caseDto.customer_id}
          </p>
          <p>
            <strong>case_type:</strong> {caseDto.case_type}
          </p>
          <div className="row">
            <button type="button" onClick={() => navigate("/recommendation")}>
              تولید Recommendation
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
