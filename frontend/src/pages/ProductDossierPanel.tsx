import { useEffect, useRef, useState } from "react";
import {
  getProductEvidence,
  getProductKnowledge,
  getProductKnowledgeCompleteness,
} from "../api/client";
import type {
  EvidenceDTO,
  ProductDTO,
  ProductKnowledgeDTO,
  ProductKnowledgeCompletenessDTO,
} from "../types/api";

type Props = {
  product: ProductDTO;
  onEnsureSession: () => Promise<string | null>;
  onBack: () => void;
  onEdit: () => void;
  onReview: () => void;
};

function display(value: unknown): string {
  if (value == null || value === "") return "ثبت نشده";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  try { return JSON.stringify(value); } catch { return String(value); }
}

const KNOWLEDGE_FIELDS: Array<[keyof ProductKnowledgeDTO, string]> = [
  ["ingredients", "ترکیبات / INCI"],
  ["ingredient_roles", "نقش ترکیبات"],
  ["other_attributes", "ویژگی‌های دیگر"],
  ["claimed_benefits", "مزایای ادعاشده"],
  ["known_use_cases", "موارد کاربرد شناخته‌شده"],
  ["contraindications", "موارد منع مصرف و احتیاط"],
  ["usage_instructions", "دستور مصرف"],
  ["manufacturer_claims", "ادعاهای سازنده"],
  ["evidence_refs", "ارجاعات شواهد"],
];

export default function ProductDossierPanel({
  product,
  onEnsureSession,
  onBack,
  onEdit,
  onReview,
}: Props) {
  const [knowledge, setKnowledge] = useState<ProductKnowledgeDTO | null>(null);
  const [completeness, setCompleteness] = useState<ProductKnowledgeCompletenessDTO | null>(null);
  const [evidence, setEvidence] = useState<EvidenceDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState<string[]>([]);
  const ensureSessionRef = useRef(onEnsureSession);
  ensureSessionRef.current = onEnsureSession;

  useEffect(() => {
    let current = true;
    async function load() {
      setLoading(true);
      setErrors([]);
      try {
        const token = await ensureSessionRef.current();
        if (!token) throw new Error("نشست اپراتور برای مشاهده پرونده محصول در دسترس نیست.");
        const results = await Promise.allSettled([
          getProductKnowledge(product.product_id, token),
          getProductKnowledgeCompleteness(product.product_id, token),
          getProductEvidence(product.product_id, token),
        ]);
        if (!current) return;
        const nextErrors: string[] = [];
        if (results[0].status === "fulfilled") setKnowledge(results[0].value);
        else { setKnowledge(null); nextErrors.push("دانش ساخت‌یافته محصول بارگذاری نشد."); }
        if (results[1].status === "fulfilled") setCompleteness(results[1].value);
        else { setCompleteness(null); nextErrors.push("گزارش کامل‌بودن دانش محصول بارگذاری نشد."); }
        if (results[2].status === "fulfilled") setEvidence(Array.isArray(results[2].value) ? results[2].value : []);
        else { setEvidence([]); nextErrors.push("فهرست شواهد محصول بارگذاری نشد."); }
        setErrors(nextErrors);
      } catch (error) {
        if (current) {
          setKnowledge(null);
          setCompleteness(null);
          setEvidence([]);
          setErrors([error instanceof Error ? error.message : String(error)]);
        }
      } finally {
        if (current) setLoading(false);
      }
    }
    void load();
    return () => { current = false; };
  }, [product.product_id]);

  return (
    <section className="pro-panel" aria-labelledby="product-dossier-title">
      <div className="pro-panel-head">
        <div>
          <h1 id="product-dossier-title">پرونده واحد محصول</h1>
          <p className="pro-muted">اطلاعات هویتی، دانش محصول، شواهد و کنترل کیفیت برای همین شناسه</p>
        </div>
        <button type="button" className="pro-btn-secondary" onClick={onBack}>بازگشت به فهرست کالاها</button>
      </div>

      <dl className="pro-dl">
        <div><dt>نام محصول</dt><dd>{product.product_name}</dd></div>
        <div><dt>برند</dt><dd>{display(product.brand)}</dd></div>
        <div><dt>شناسه محصول</dt><dd><code>{product.product_id}</code></dd></div>
        <div><dt>وضعیت هویت</dt><dd>{display(product.identity_status)}</dd></div>
        <div><dt>وضعیت چرخه عمر</dt><dd>{display(product.status)}</dd></div>
        <div><dt>نتیجه کنترل کیفیت</dt><dd>{display(product.qa_verdict)}</dd></div>
        <div><dt>خط محصول</dt><dd>{display(product.product_line)}</dd></div>
        <div><dt>گونه / حجم</dt><dd>{[product.variant, product.size_value, product.size_unit].filter((v) => v != null && v !== "").join(" ") || "ثبت نشده"}</dd></div>
      </dl>

      <div className="pro-actions">
        <button type="button" className="pro-btn-primary" onClick={onEdit}>ویرایش مشخصات محصول</button>
        <button type="button" className="pro-btn-secondary" onClick={onReview}>بازکردن بررسی کیفیت و شواهد</button>
      </div>

      {loading ? <p role="status">در حال بارگذاری دانش و شواهد محصول…</p> : null}
      {errors.map((message) => <p className="pro-error" role="alert" key={message}>{message}</p>)}

      <section aria-labelledby="product-knowledge-title">
        <h2 id="product-knowledge-title">دانش ساخت‌یافته محصول</h2>
        {knowledge ? (
          <>
            <p className="pro-muted">وضعیت دانش: {display(knowledge.evidence_status)} · اطمینان: {display(knowledge.knowledge_confidence)}</p>
            <dl className="pro-dl">
              {KNOWLEDGE_FIELDS.map(([field, label]) => (
                <div key={field}><dt>{label}</dt><dd>{display(knowledge[field])}</dd></div>
              ))}
            </dl>
          </>
        ) : !loading && !errors.some((message) => message.includes("دانش ساخت‌یافته")) ? (
          <p className="pro-muted">رکورد دانش ساخت‌یافته برای این محصول در دسترس نیست.</p>
        ) : null}
      </section>

      <section aria-labelledby="product-completeness-title">
        <h2 id="product-completeness-title">کامل‌بودن پرونده دانش</h2>
        {completeness ? (
          <>
            <p className="pro-muted">وضعیت: {display(completeness.status)} · رکورد دانش مفقود: {completeness.pk_record_missing ? "بله" : "خیر"} · بررسی منع مصرف: {completeness.contraindications_unreviewed ? "نیازمند بررسی" : "بررسی‌شده"}</p>
            {completeness.missing_domains.length ? <p>حوزه‌های ناقص: {completeness.missing_domains.join("، ")}</p> : <p>حوزه ناقصی در گزارش ثبت نشده است.</p>}
            {completeness.domain_report.map((item) => (
              <p className="pro-muted" key={item.field}>{item.label}: {item.status}، {item.message}</p>
            ))}
          </>
        ) : !loading ? <p className="pro-muted">گزارش کامل‌بودن در دسترس نیست.</p> : null}
      </section>

      <section aria-labelledby="product-evidence-title">
        <h2 id="product-evidence-title">شواهد ثبت‌شده ({evidence.length})</h2>
        {evidence.length ? (
          <div className="pro-product-grid">
            {evidence.map((item) => (
              <article className="pro-product-card" key={item.evidence_id}>
                <strong>{display(item.claim || item.field || item.evidence_id)}</strong>
                <p className="pro-muted">فیلد: {display(item.field)} · وضعیت QA: {display(item.qa_status)} · تعارض: {display(item.conflict_status)}</p>
                <p className="pro-muted">منبع: {display(item.source_type)} · مرجع: {display(item.source_reference)}</p>
              </article>
            ))}
          </div>
        ) : !loading && !errors.some((message) => message.includes("فهرست شواهد")) ? (
          <p className="pro-muted">شاهدی برای نمایش دریافت نشد.</p>
        ) : null}
      </section>
    </section>
  );
}
