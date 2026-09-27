import { useEffect, useMemo, useState } from "react";
import {
  activateProduct,
  approveProduct,
  enterProductQaReview,
  getProduct,
  getProductEvidence,
  getProductMutationLog,
  rejectProduct,
  setProductQa,
  submitProduct,
  verifyProductIdentity,
} from "../api/client";
import type { EvidenceDTO, MutationLogDTO, ProductDTO } from "../types/api";

type Props = {
  token?: string | null;
  productId?: string | null;
  onEnsureSession?: () => Promise<string | null>;
  onProductChanged?: () => void;
};

function upper(value: unknown): string {
  return String(value ?? "").trim().toUpperCase();
}

function text(value: unknown): string {
  return String(value ?? "").trim();
}

function formatJson(value: unknown): string {
  if (value == null) return "—";
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function skinSafetyReady(product: ProductDTO, evidences: EvidenceDTO[]): boolean {
  if (upper(product.product_line) !== "SKIN") return true;
  return evidences.some((ev) => {
    const field = text(ev.field).toLowerCase();
    const qa = upper(ev.qa_status);
    const conflict = upper(ev.conflict_status);
    const claimType = upper(ev.claim_type);
    const claim = text(ev.claim);
    if (field !== "contraindications" || qa !== "VERIFIED") return false;
    if (conflict === "CONFLICT" || claimType === "CONFLICT") return false;
    return Boolean(claim) || claimType === "UNKNOWN";
  });
}

export default function ProductReviewPanel({
  token,
  productId,
  onEnsureSession,
  onProductChanged,
}: Props) {
  const [product, setProduct] = useState<ProductDTO | null>(null);
  const [evidences, setEvidences] = useState<EvidenceDTO[]>([]);
  const [logs, setLogs] = useState<MutationLogDTO[]>([]);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [qaVerdict, setQaVerdict] = useState("VALID");
  const [qaNotes, setQaNotes] = useState("");
  const [identityStatus, setIdentityStatus] = useState("VERIFIED");
  const [identityRefs, setIdentityRefs] = useState("");
  const [identityConfidence, setIdentityConfidence] = useState("");
  const [rejectReason, setRejectReason] = useState("");
  const [selectedId, setSelectedId] = useState(productId ?? "");

  const load = async (id: string) => {
    if (!id) {
      setProduct(null);
      setEvidences([]);
      setLogs([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const opToken = (await onEnsureSession?.()) ?? token;
      if (!opToken) throw new Error("نشست اپراتور برای بررسی محصول در دسترس نیست.");
      const [p, ev, log] = await Promise.all([
        getProduct(id),
        getProductEvidence(id, opToken),
        getProductMutationLog(id, opToken),
      ]);
      setProduct(p);
      setEvidences(Array.isArray(ev) ? ev : []);
      setLogs(Array.isArray(log) ? log : []);
      setSelectedId(id);
      setIdentityStatus(upper(p.identity_status) || "NEEDS_REVIEW");
      setQaVerdict(upper(p.qa_verdict) || "PENDING");
      setQaNotes("");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setProduct(null);
      setEvidences([]);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load(productId ?? sessionStorage.getItem("hbi_review_product_id") ?? "");
  }, [productId]);

  const skinReady = useMemo(
    () => (product ? skinSafetyReady(product, evidences) : false),
    [product, evidences]
  );

  const knownBlockers = useMemo(() => {
    if (!product) return [];
    const blockers: string[] = [];
    if (upper(product.identity_status) !== "VERIFIED") blockers.push("هویت محصول هنوز VERIFIED نیست.");
    if (upper(product.qa_verdict) !== "VALID") blockers.push("QA محصول هنوز VALID نیست.");
    if (upper(product.product_line) === "SKIN" && !skinReady) {
      blockers.push("برای SKIN، شواهد contraindications با QA=VERIFIED یا UNKNOWN صریح وجود ندارد.");
    }
    if (!["DRAFT", "SUBMITTED", "QA_REVIEW", "APPROVED", "ACTIVE"].includes(upper(product.status))) {
      blockers.push(`وضعیت فعلی محصول نیازمند بررسی سرور است: ${upper(product.status)}`);
    }
    return blockers;
  }, [product, skinReady]);

  async function run(action: (opToken: string) => Promise<ProductDTO>, success: string) {
    if (!product) return;
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      const opToken = (await onEnsureSession?.()) ?? token;
      if (!opToken) throw new Error("نشست اپراتور در دسترس نیست.");
      const updated = await action(opToken);
      setProduct(updated);
      setNotice(success);
      await load(updated.product_id);
      onProductChanged?.();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function saveQa() {
    if (!product) return;
    await run(
      (opToken) => setProductQa(product.product_id, { verdict: qaVerdict, notes: qaNotes || null }, opToken),
      `تصمیم QA ثبت شد: ${qaVerdict}`
    );
  }

  async function saveIdentity() {
    if (!product) return;
    const confidence = identityConfidence.trim() ? Number(identityConfidence) : null;
    if (confidence != null && (!Number.isFinite(confidence) || confidence < 0 || confidence > 1)) {
      setError("اطمینان هویتی باید عددی بین 0 و 1 باشد.");
      return;
    }
    await run(
      (opToken) =>
        verifyProductIdentity(
          product.product_id,
          {
            identity_status: identityStatus,
            source_refs: identityRefs || null,
            confidence,
          },
          opToken
        ),
      `وضعیت هویت ثبت شد: ${identityStatus}`
    );
  }

  async function doReject() {
    if (!product) return;
    const reason = rejectReason.trim();
    if (!reason) {
      setError("برای Reject دلیل روشن و غیرخالی لازم است.");
      return;
    }
    await run(
      (opToken) => rejectProduct(product.product_id, reason, opToken),
      "محصول Reject شد و دلیل در سابقه ثبت شد."
    );
    setRejectReason("");
  }

  const status = upper(product?.status);

  return (
    <section className="pro-panel">
      <div className="pro-panel-head">
        <div>
          <h1>بررسی پرونده محصول</h1>
          <p className="pro-lead">یک dossier عملیاتی برای همان Product Master؛ Transitionها را سرور انجام می‌دهد.</p>
        </div>
        <button
          type="button"
          className="pro-btn-secondary"
          disabled={loading}
          onClick={() => void load(selectedId)}
        >
          نوسازی
        </button>
      </div>

      {error ? <div className="pro-alert" role="alert">{error}</div> : null}
      {notice ? <div className="pro-status-msg" role="status">{notice}</div> : null}

      {!product && !loading ? (
        <div className="pro-empty">
          <strong>محصولی برای بررسی انتخاب نشده است.</strong>
          <p>از بخش «محصولات» یک Product را انتخاب کنید.</p>
        </div>
      ) : null}

      {loading ? <p className="pro-muted">در حال بارگذاری پرونده…</p> : null}

      {product ? (
        <>
          <div className="pro-product-grid">
            <article className="pro-product-card">
              <h3>{product.product_name}</h3>
              <p className="pro-muted">{product.brand}</p>
              <code className="pro-code">{product.product_id}</code>
              <div className="pro-tags">
                <span className="pro-tag">LINE: {upper(product.product_line) || "—"}</span>
                <span className="pro-tag">STATUS: {status || "—"}</span>
                <span className="pro-tag">QA: {upper(product.qa_verdict) || "—"}</span>
                <span className="pro-tag">IDENTITY: {upper(product.identity_status) || "—"}</span>
              </div>
            </article>

            <article className="pro-product-card">
              <h3>گیت‌های قابل مشاهده</h3>
              {knownBlockers.length === 0 ? (
                <p className="pro-muted">Blocker قابل مشاهده در این dossier ثبت نشده است؛ گیت‌های Evidence Readiness و D3 همچنان توسط سرور تصمیم‌گیری می‌شوند.</p>
              ) : (
                <div className="pro-alert">
                  {knownBlockers.map((item) => <div key={item}>• {item}</div>)}
                  <p style={{ marginBottom: 0 }}>خطاهای دقیق Transition نیز از پاسخ سرور نمایش داده می‌شوند.</p>
                </div>
              )}
            </article>
          </div>

          <fieldset className="pro-fieldset">
            <legend>اطلاعات هویتی و QA</legend>
            <div className="pro-grid-2">
              <div>
                <label className="pro-label">Identity Status</label>
                <select className="pro-input" value={identityStatus} onChange={(e) => setIdentityStatus(e.target.value)}>
                  <option value="VERIFIED">VERIFIED</option>
                  <option value="PARTIAL_IDENTITY">PARTIAL_IDENTITY</option>
                  <option value="CONFLICT">CONFLICT</option>
                  <option value="NEEDS_REVIEW">NEEDS_REVIEW</option>
                </select>
              </div>
              <div>
                <label className="pro-label">Identity Confidence</label>
                <input className="pro-input" value={identityConfidence} onChange={(e) => setIdentityConfidence(e.target.value)} placeholder="0..1 (اختیاری)" />
              </div>
              <div style={{ gridColumn: "1 / -1" }}>
                <label className="pro-label">Identity Source Refs</label>
                <input className="pro-input" value={identityRefs} onChange={(e) => setIdentityRefs(e.target.value)} placeholder="منبع یا ارجاع قابل ردیابی" />
              </div>
              <div>
                <label className="pro-label">QA Verdict</label>
                <select className="pro-input" value={qaVerdict} onChange={(e) => setQaVerdict(e.target.value)}>
                  <option value="PENDING">PENDING</option>
                  <option value="VALID">VALID</option>
                  <option value="INVALID">INVALID</option>
                  <option value="CONFLICT">CONFLICT</option>
                  <option value="UNKNOWN">UNKNOWN</option>
                  <option value="NEEDS_REVIEW">NEEDS_REVIEW</option>
                </select>
              </div>
              <div>
                <label className="pro-label">QA Notes</label>
                <input className="pro-input" value={qaNotes} onChange={(e) => setQaNotes(e.target.value)} placeholder="یادداشت تصمیم QA" />
              </div>
            </div>
            <div className="pro-actions" style={{ marginTop: "0.75rem" }}>
              <button type="button" className="pro-btn-secondary" disabled={busy} onClick={() => void saveIdentity()}>ثبت تصمیم هویت</button>
              <button type="button" className="pro-btn-secondary" disabled={busy} onClick={() => void saveQa()}>ثبت تصمیم QA</button>
            </div>
          </fieldset>

          <fieldset className="pro-fieldset">
            <legend>Transitionهای کنترل‌شده</legend>
            <div className="pro-tags" style={{ marginBottom: "0.75rem" }}>
              <span className="pro-tag">DRAFT → SUBMITTED</span>
              <span className="pro-tag">SUBMITTED → QA_REVIEW</span>
              <span className="pro-tag">QA_REVIEW → APPROVED</span>
              <span className="pro-tag">APPROVED → ACTIVE</span>
            </div>
            <div className="pro-actions">
              {status === "DRAFT" ? (
                <button type="button" className="pro-btn-primary" disabled={busy} onClick={() => void run(
                  (opToken) => submitProduct(product.product_id, opToken),
                  "محصول برای بررسی ارسال شد."
                )}>ارسال برای بررسی</button>
              ) : null}
              {status === "SUBMITTED" ? (
                <button type="button" className="pro-btn-primary" disabled={busy} onClick={() => void run(
                  (opToken) => enterProductQaReview(product.product_id, opToken),
                  "محصول وارد QA Review شد."
                )}>ورود به QA Review</button>
              ) : null}
              {status === "QA_REVIEW" ? (
                <button type="button" className="pro-btn-primary" disabled={busy} onClick={() => void run(
                  (opToken) => approveProduct(product.product_id, opToken),
                  "محصول Approved شد."
                )}>Approve</button>
              ) : null}
              {status === "APPROVED" ? (
                <button type="button" className="pro-btn-primary" disabled={busy} onClick={() => void run(
                  (opToken) => activateProduct(product.product_id, opToken),
                  "محصول Active شد."
                )}>Activate</button>
              ) : null}
            </div>
          </fieldset>

          <fieldset className="pro-fieldset">
            <legend>Reject با دلیل</legend>
            <textarea
              className="pro-input"
              rows={2}
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="دلیل دقیق Reject…"
            />
            <div className="pro-actions" style={{ marginTop: "0.6rem" }}>
              <button type="button" className="pro-btn-secondary" disabled={busy} onClick={() => void doReject()}>
                Reject
              </button>
            </div>
          </fieldset>

          <fieldset className="pro-fieldset">
            <legend>Evidence / Provenance</legend>
            {evidences.length === 0 ? (
              <p className="pro-muted">Evidence ثبت‌شده‌ای برای این Product پیدا نشد.</p>
            ) : (
              <div className="pro-product-grid">
                {evidences.map((ev) => (
                  <article key={ev.evidence_id} className="pro-product-card">
                    <h3>{ev.field || "general"}</h3>
                    <p>{ev.claim || "—"}</p>
                    <div className="pro-tags">
                      <span className="pro-tag">QA: {upper(ev.qa_status)}</span>
                      <span className="pro-tag">CLAIM: {upper(ev.claim_type)}</span>
                      <span className="pro-tag">CONFLICT: {upper(ev.conflict_status) || "NONE"}</span>
                    </div>
                    <p className="pro-muted">Source: {ev.source_type || "—"} · {ev.source_reference || "—"}</p>
                    <code className="pro-code">{ev.evidence_id}</code>
                  </article>
                ))}
              </div>
            )}
          </fieldset>

          <fieldset className="pro-fieldset">
            <legend>Mutation / Audit History</legend>
            {logs.length === 0 ? (
              <p className="pro-muted">سابقه تغییری برای نمایش وجود ندارد.</p>
            ) : (
              <div className="pro-product-grid">
                {logs.slice().reverse().map((log, index) => (
                  <article key={String(log.id ?? index)} className="pro-product-card">
                    <h3>{log.action || "ACTION"}</h3>
                    <p className="pro-muted">
                      {log.actor_id || "—"} · {log.actor_role || "—"} · {log.created_at || "—"}
                    </p>
                    <p>Result: {log.resulting_state || "—"}</p>
                    {log.reason ? <p>Reason: {log.reason}</p> : null}
                    <details className="pro-technical-details">
                      <summary>قبل / بعد</summary>
                      <div className="pro-muted">Before: {formatJson(log.before)}</div>
                      <div className="pro-muted">After: {formatJson(log.after)}</div>
                    </details>
                  </article>
                ))}
              </div>
            )}
          </fieldset>
        </>
      ) : null}
    </section>
  );
}
