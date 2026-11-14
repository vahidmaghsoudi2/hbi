import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { previewHairSpecialist } from "../api/client";
import type { HairSpecialistPreviewResponse } from "../types/api";
import HairDialogueWorkbench from "./HairDialogueWorkbench";

const specialistResponseTypes = [
  { code: "REVIEWABLE_SUGGESTION", label: "پیشنهاد قابل بازبینی متخصص" },
  { code: "NEEDS_MORE_INFORMATION", label: "نیازمند اطلاعات بیشتر" },
  { code: "NEEDS_IN_PERSON_REVIEW", label: "نیازمند بررسی حضوری" },
  { code: "SAFETY_STOP", label: "توقف ایمنی" },
  { code: "OUT_OF_SCOPE", label: "خارج از دامنهٔ نسخهٔ اول" },
];

const motorStates = [
  { code: "REVIEWABLE_SUGGESTION", label: "پیشنهاد قابل بازبینی" },
  { code: "CONDITIONAL_SUGGESTION", label: "پیشنهاد مشروط به شرط مشخص" },
  { code: "REQUEST_MORE_INFORMATION", label: "درخواست اطلاعات بیشتر" },
  { code: "STOP_OR_REFER", label: "توقف یا ارجاع با دلیل" },
];

const initialIdentity = {
  brand: "بیجورکا",
  series: "طبیعی",
  shade_number: "۱",
  shade_name: "مشکی",
  product_specification: "",
  product_volume: "",
};

export default function HairSpecialistPreviewPage() {
  const [caseId, setCaseId] = useState("SYNTHETIC-ROW69-UI-001");
  const [caseVersion, setCaseVersion] = useState("case-v1");
  const [goalVersion, setGoalVersion] = useState("goal-v1");
  const [serviceKind, setServiceKind] = useState("CATALOG_READY");
  const [identity, setIdentity] = useState(initialIdentity);
  const [result, setResult] = useState<HairSpecialistPreviewResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const adminToken = sessionStorage.getItem("hbi_admin_access_token");

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const preview = await previewHairSpecialist({
        case_id: caseId.trim(),
        case_version: caseVersion.trim(),
        goal_version: goalVersion.trim(),
        service_kind: serviceKind.trim(),
        catalog_identity: {
          brand: identity.brand.trim(),
          series: identity.series.trim(),
          shade_number: identity.shade_number.trim(),
          shade_name: identity.shade_name.trim(),
          product_specification: identity.product_specification.trim() || null,
          product_volume: identity.product_volume.trim() || null,
        },
      }, adminToken || "");
      setResult(preview);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="main hair-specialist-page" dir="rtl">
      <div className="row" style={{ justifyContent: "space-between" }}>
        <div>
          <p className="meta">HBI / HAIR / ROW 69</p>
          <h1>پیش‌نمایش داخلی متخصص</h1>
          <p className="lead">نمای فقط‌خواندنی برای پروندهٔ مصنوعی؛ بدون توصیهٔ رنگ و بدون اجرای خدمت.</p>
        </div>
        <Link className="btn secondary" to="/">بازگشت به صفحهٔ اصلی</Link>
      </div>

      <div className="alert" role="note">
        <strong>محدودیت قطعی PO-66-09:</strong> فقط دادهٔ مصنوعی مجاز است. دادهٔ واقعی مشتری دریافت یا ذخیره نمی‌شود.
        این صفحه ابزار تصمیم شیمیایی یا تأیید اجرای خدمت نیست.
      </div>

      <section className="card" aria-labelledby="hair-specialist-contract-heading">
        <h2 id="hair-specialist-contract-heading">قرارداد انواع پاسخ و حالت موتور</h2>
        <p>این فهرست، قرارداد ثابت سامانه است؛ به معنی تولید توصیه یا فعال‌بودن هیچ قاعدهٔ شیمیایی نیست.</p>
        <h3>پنج نوع پاسخ مشاوره</h3>
        <ul className="hair-specialist-contract-list">
          {specialistResponseTypes.map(item => <li key={item.code}><strong>{item.label}</strong><span className="meta">{item.code}</span></li>)}
        </ul>
        <h3>چهار حالت مستقل موتور</h3>
        <ul className="hair-specialist-contract-list">
          {motorStates.map(item => <li key={item.code}><strong>{item.label}</strong><span className="meta">{item.code}</span></li>)}
        </ul>
        <p className="meta">«پیشنهاد مشروط» حالت موتور است و نوع پاسخ ششم محسوب نمی‌شود.</p>
        <p className="meta">تعیین و احراز صلاحیت متخصص بر عهدهٔ Product Owner است؛ سامانه در این برش صلاحیت حرفه‌ای اشخاص را مستقلاً ارزیابی نمی‌کند.</p>
      </section>

      <HairDialogueWorkbench adminToken={adminToken || ""} />

      {!adminToken && <div className="alert error" role="alert">نشست مدیر در مرورگر موجود نیست. ابتدا وارد سامانه شوید.</div>}

      <form className="card" onSubmit={onSubmit}>
        <h2>ورودی آزمایشی</h2>
        <div className="hair-specialist-fields">
          <label>شناسهٔ پروندهٔ مصنوعی
            <input value={caseId} onChange={e => setCaseId(e.target.value)} required pattern="SYNTHETIC-.+" title="شناسه باید با SYNTHETIC- شروع شود." />
          </label>
          <label>نسخهٔ پرونده
            <input value={caseVersion} onChange={e => setCaseVersion(e.target.value)} required />
          </label>
          <label>نسخهٔ هدف
            <input value={goalVersion} onChange={e => setGoalVersion(e.target.value)} required />
          </label>
          <label>نوع خدمت
            <select value={serviceKind} onChange={e => setServiceKind(e.target.value)}>
              <option value="CATALOG_READY">CATALOG_READY</option>
              <option value="COMBINATION_CONSULT">COMBINATION_CONSULT — خارج از دامنه</option>
            </select>
          </label>
          <label>برند
            <input value={identity.brand} onChange={e => setIdentity(v => ({ ...v, brand: e.target.value }))} required />
          </label>
          <label>سری
            <input value={identity.series} onChange={e => setIdentity(v => ({ ...v, series: e.target.value }))} required />
          </label>
          <label>شمارهٔ رنگ
            <input value={identity.shade_number} onChange={e => setIdentity(v => ({ ...v, shade_number: e.target.value }))} required />
          </label>
          <label>نام رنگ
            <input value={identity.shade_name} onChange={e => setIdentity(v => ({ ...v, shade_name: e.target.value }))} required />
          </label>
          <label>مشخصات محصول (اختیاری)
            <input value={identity.product_specification} onChange={e => setIdentity(v => ({ ...v, product_specification: e.target.value }))} />
          </label>
          <label>حجم محصول (اختیاری)
            <input value={identity.product_volume} onChange={e => setIdentity(v => ({ ...v, product_volume: e.target.value }))} />
          </label>
        </div>
        <div className="row">
          <button type="submit" disabled={busy || !adminToken}>{busy ? "در حال دریافت پیش‌نمایش…" : "ساخت پیش‌نمایش مصنوعی"}</button>
          <button type="button" className="secondary" disabled={busy} onClick={() => { setIdentity(initialIdentity); setCaseId("SYNTHETIC-ROW69-UI-001"); setCaseVersion("case-v1"); setGoalVersion("goal-v1"); setServiceKind("CATALOG_READY"); setResult(null); setError(null); }}>بازنشانی نمونه</button>
        </div>
      </form>

      {error && <div className="alert error" role="alert"><strong>پیش‌نمایش دریافت نشد.</strong><pre>{error}</pre></div>}

      {result && (
        <section aria-live="polite">
          <div className="card">
            <div className="row" style={{ justifyContent: "space-between" }}>
              <h2>وضعیت بررسی</h2>
              <span className="badge">{result.decision.status}</span>
            </div>
            <p>{result.decision.summary_fa}</p>
            <dl className="hair-specialist-dl">
              <div><dt>شناسهٔ پرونده</dt><dd>{result.case.case_id}</dd></div>
              <div><dt>نسخهٔ پرونده</dt><dd>{result.case.case_version}</dd></div>
              <div><dt>نسخهٔ هدف</dt><dd>{result.case.goal_version}</dd></div>
              <div><dt>مخاطب</dt><dd>{result.audience}</dd></div>
              <div><dt>طبقهٔ داده</dt><dd>{result.data_class}</dd></div>
              <div><dt>نمایش به مشتری</dt><dd>ممنوع</dd></div>
              <div><dt>پیشنهاد رنگ</dt><dd>ارائه نشده</dd></div>
              <div><dt>مجوز اجرای خدمت</dt><dd>ایجاد نشده</dd></div>
            </dl>
          </div>

          <div className="card">
            <h2>شواهد قابل‌ردیابی</h2>
            {result.evidence.length ? (
              <ul>{result.evidence.map((item, index) => <li key={item.evidence_id + index}>
                <strong>{item.evidence_id}</strong> — {item.source_type} — {item.qa_status}
                <div className="meta">{item.source_reference}</div>
              </li>)}</ul>
            ) : <p className="muted">برای این اجرا شاهدی در خروجی ثبت نشده است.</p>}
          </div>

          <div className="card">
            <h2>Lineage و نسخه‌ها</h2>
            <dl className="hair-specialist-dl">
              <div><dt>Run ID</dt><dd>{result.lineage.run_id}</dd></div>
              <div><dt>Knowledge Package</dt><dd>{result.lineage.knowledge_package_id} / {result.lineage.knowledge_package_version}</dd></div>
              <div><dt>Rule</dt><dd>{result.lineage.rule_id} / {result.lineage.rule_version}</dd></div>
              <div><dt>Snapshot</dt><dd>{result.lineage.snapshot_id}</dd></div>
              <div><dt>SHA-256</dt><dd className="hash-value">{result.lineage.content_sha256}</dd></div>
              <div><dt>Engine</dt><dd>{result.lineage.engine_version}</dd></div>
              <div><dt>Persistence</dt><dd>{result.lineage.persistence}</dd></div>
            </dl>
            <h3>وابستگی‌ها</h3>
            <ul>{result.lineage.dependencies.map((dep, index) => <li key={dep.kind + dep.dependency_id + index}>{dep.kind}: {dep.dependency_id} — {dep.version}</li>)}</ul>
          </div>

          <div className="card">
            <h2>محدودیت‌های این خروجی</h2>
            <ul>{result.limitations.map((item, index) => <li key={index}>{item}</li>)}</ul>
          </div>
        </section>
      )}
    </main>
  );
}
