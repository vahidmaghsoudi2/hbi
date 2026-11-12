import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";

const BASE = import.meta.env?.VITE_API_BASE ?? "/api/v1";

async function getCurrentFx() {
  const res = await fetch(`${BASE}/fx/current`);
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  return res.json() as Promise<{ fx_rate_usd_to_irr: number | null; source?: Record<string, unknown> | null }>;
}

async function setOperationalFx(body: { fx_rate_usd_to_irr: number; note?: string }, token: string) {
  const res = await fetch(`${BASE}/fx/operational`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  return res.json() as Promise<Record<string, unknown> & { fx_rate_usd_to_irr: number }>;
}

export default function PricingFxPage() {
  const [token, setToken] = useState<string | null>(() => sessionStorage.getItem("hbi_admin_access_token"));
  const [rate, setRate] = useState<number | null>(null);
  const [source, setSource] = useState<Record<string, unknown> | null>(null);
  const [value, setValue] = useState("");
  const [note, setNote] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function load() {
    setError(null);
    try {
      const current = await getCurrentFx();
      setRate(current.fx_rate_usd_to_irr);
      setSource(current.source ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  useEffect(() => {
    setToken(sessionStorage.getItem("hbi_admin_access_token"));
    void load();
  }, []);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setStatus(null);
    const adminToken = sessionStorage.getItem("hbi_admin_access_token");
    setToken(adminToken);
    if (!adminToken) {
      setError("برای ثبت نرخ، نشست Admin لازم است.");
      return;
    }
    const nextRate = Number(value.replaceAll(",", "").trim());
    if (!Number.isFinite(nextRate) || nextRate <= 0) {
      setError("نرخ باید یک عدد مثبت باشد.");
      return;
    }
    setLoading(true);
    try {
      const row = await setOperationalFx(
        { fx_rate_usd_to_irr: nextRate, note: note.trim() || undefined },
        adminToken
      );
      setRate(row.fx_rate_usd_to_irr);
      setSource(row);
      setValue("");
      setNote("");
      setStatus("نرخ عملیاتی جدید ثبت شد. قیمت فروش تومان از این نرخ جاری مشتق می‌شود.");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  const sampleToman = rate == null ? null : Math.round((25 * rate) / 10);

  return (
    <div className="home-root pro-home">
      <header className="pro-header">
        <div className="pro-header-inner">
          <div className="pro-brand">
            <span className="pro-brand-mark">HBI</span>
            <div>
              <div className="pro-brand-title">گالری مقصودی</div>
              <div className="pro-brand-sub">نرخ عملیاتی و قیمت فروش</div>
            </div>
          </div>
          <nav className="pro-nav" aria-label="مدیریت نرخ ارز">
            <Link to="/" className="pro-nav-btn">خانه HBI</Link>
            <Link to="/accounting" className="pro-nav-btn">حسابداری</Link>
          </nav>
        </div>
      </header>
      <main className="pro-main">
        <section className="pro-panel">
          <div className="pro-panel-head">
            <div>
              <h1>نرخ عملیاتی دلار / ریال</h1>
              <p className="pro-lead">نرخ جاری برای محاسبه قیمت فروش تومان ثبت می‌شود. قیمت فروش اصلی هر محصول همچنان USD است.</p>
            </div>
            <span className="pro-status-msg">{token ? "Admin فعال" : "Admin لازم است"}</span>
          </div>
          {error ? <div className="pro-alert" role="alert">{error}</div> : null}
          {status ? <div className="pro-status-bar"><span className="dot on" /><span className="pro-status-msg">{status}</span></div> : null}
          <section className="pro-fieldset">
            <h2>نرخ جاری</h2>
            <p className="pro-summary">
              {rate == null ? "نرخ عملیاتی ثبت‌شده در دسترس نیست." : <>۱ دلار = <strong>{rate.toLocaleString("en-US")} ریال</strong> · قیمت تومان از تقسیم ریال بر ۱۰ به‌دست می‌آید.</>}
            </p>
            {source?.effective_at ? <p className="pro-muted">زمان اثرگذاری: {String(source.effective_at)}</p> : null}
            {source?.note ? <p className="pro-muted">یادداشت: {String(source.note)}</p> : null}
          </section>
          <form className="pro-form" onSubmit={submit}>
            <fieldset className="pro-fieldset">
              <legend>ثبت نرخ جدید</legend>
              <label className="pro-label" htmlFor="fx-rate">نرخ USD → IRR *</label>
              <input id="fx-rate" className="pro-input" type="text" inputMode="numeric" value={value} onChange={(e) => setValue(e.target.value)} placeholder="مثلاً 1,100,000" disabled={!token || loading} />
              <label className="pro-label" htmlFor="fx-note">یادداشت</label>
              <input id="fx-note" className="pro-input" value={note} onChange={(e) => setNote(e.target.value)} placeholder="مثلاً نرخ روز" disabled={!token || loading} />
            </fieldset>
            <div className="pro-actions">
              <button type="submit" className="pro-btn-primary" disabled={!token || loading}>{loading ? "در حال ثبت…" : "ثبت نرخ عملیاتی"}</button>
              <button type="button" className="pro-btn-secondary" onClick={() => void load()} disabled={loading}>نوسازی</button>
            </div>
          </form>
          <section className="pro-fieldset">
            <h2>نمونه محاسبه</h2>
            <p className="pro-summary">قیمت فروش USD = 25 → قیمت جاری تومان: <strong>{sampleToman == null ? "در دسترس نیست" : `${sampleToman.toLocaleString("en-US")} تومان`}</strong></p>
            <p className="pro-muted">این مقدار از FX جاری مشتق می‌شود و قیمت USD محصول را تغییر نمی‌دهد.</p>
          </section>
        </section>
      </main>
    </div>
  );
}
