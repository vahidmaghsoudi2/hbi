import { useEffect, useState } from "react";
import { getProduct, getProductEvidence, getProductKnowledge, listProducts } from "../api/client";
import type { EvidenceDTO, ProductDTO, ProductKnowledgeDTO } from "../types/api";

type Props = { onBack: () => void };

const labels: Array<[keyof ProductKnowledgeDTO, string]> = [
  ["ingredients", "ترکیبات ثبت‌شده"],
  ["ingredient_roles", "نقش ترکیبات"],
  ["claimed_benefits", "ادعاهای ثبت‌شده"],
  ["known_use_cases", "موارد کاربرد تأییدشده"],
  ["contraindications", "محدودیت‌ها و احتیاط‌ها"],
  ["usage_instructions", "دستور مصرف"],
  ["manufacturer_claims", "ادعاهای سازنده"],
  ["evidence_status", "وضعیت شواهد"],
  ["knowledge_confidence", "اطمینان دانش"],
  ["evidence_refs", "مراجع شواهد"],
];

function valueOrUnknown(value: unknown): string {
  if (value === null || value === undefined || value === "") return "ثبت نشده / نامشخص";
  if (typeof value === "number") return String(value);
  return String(value);
}

export default function SkinProductEncyclopedia({ onBack }: Props) {
  const [products, setProducts] = useState<ProductDTO[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [product, setProduct] = useState<ProductDTO | null>(null);
  const [knowledge, setKnowledge] = useState<ProductKnowledgeDTO | null>(null);
  const [evidence, setEvidence] = useState<EvidenceDTO[]>([]);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [knowledgeError, setKnowledgeError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    listProducts().then((rows) => {
      if (!alive) return;
      const available = Array.isArray(rows) ? rows : [];
      setProducts(available);
      if (available.length) setSelectedId(available[0].product_id);
    }).catch((e) => {
      if (alive) setError(e instanceof Error ? e.message : String(e));
    }).finally(() => { if (alive) setLoadingList(false); });
    return () => { alive = false; };
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setProduct(null); setKnowledge(null); setEvidence([]);
      return;
    }
    let alive = true;
    setLoadingDetail(true); setError(null); setKnowledgeError(null);
    setProduct(null); setKnowledge(null); setEvidence([]);
    const token = sessionStorage.getItem("hbi_admin_access_token") ?? sessionStorage.getItem("hbi_access_token") ?? "";
    Promise.all([
      getProduct(selectedId),
      getProductEvidence(selectedId, token),
      getProductKnowledge(selectedId, token).catch((e) => {
        if (alive) setKnowledgeError(e instanceof Error ? e.message : String(e));
        return null;
      }),
    ]).then(([p, ev, pk]) => {
      if (!alive) return;
      setProduct(p); setEvidence(Array.isArray(ev) ? ev : []); setKnowledge(pk);
    }).catch((e) => {
      if (alive) setError(e instanceof Error ? e.message : String(e));
    }).finally(() => { if (alive) setLoadingDetail(false); });
    return () => { alive = false; };
  }, [selectedId]);

  return (
    <section className="pro-panel" aria-labelledby="skin-encyclopedia-title">
      <div className="pro-section-head">
        <h1 id="skin-encyclopedia-title">دانشنامهٔ ویژگی محصولات پوستی</h1>
        <button type="button" className="pro-btn-secondary" onClick={onBack}>بازگشت</button>
      </div>
      <p className="pro-lead">این صفحه فقط داده‌های موجود در مسیر رسمی محصول، شواهد و ProductKnowledge را می‌خواند. مقدار ثبت‌نشده به‌صورت نامشخص نمایش داده می‌شود؛ این صفحه محصول یا تأیید QA ایجاد نمی‌کند.</p>
      <p><a href="https://github.com/vahidmaghsoudi2/hbi/blob/master/docs/homepage/encyclopedia/skin/PRODUCTS.md" target="_blank" rel="noreferrer">دفتر پژوهش هفت محصول P1–P7 (جدا از ثبت عملیاتی)</a></p>
      {loadingList ? <p role="status">در حال دریافت فهرست محصولات…</p> : null}
      {error ? <p className="pro-error" role="alert">دریافت اطلاعات کامل نشد: {error}</p> : null}
      {!loadingList && products.length === 0 && !error ? <p className="pro-muted">محصولی در فهرست رسمی قابل نمایش نیست. پرونده‌های پژوهشی P1–P7 به معنی ثبت عملیاتی نیستند.</p> : null}
      {products.length > 0 ? (
        <div className="pro-product-card">
          <label htmlFor="skin-product-select">انتخاب محصول</label>
          <select id="skin-product-select" className="pro-input" value={selectedId} onChange={(e) => setSelectedId(e.target.value)}>
            {products.map((item) => <option key={item.product_id} value={item.product_id}>{item.brand} · {item.product_name} ({item.product_id})</option>)}
          </select>
        </div>
      ) : null}
      {loadingDetail ? <p role="status">در حال دریافت جزئیات…</p> : null}
      {product ? <>
        <section className="pro-product-card" aria-labelledby="skin-product-identity">
          <h2 id="skin-product-identity">هویت و نسخهٔ محصول</h2>
          <dl>
            {([
              ["شناسه", product.product_id],
              ["برند", product.brand],
              ["نام", product.product_name],
              ["لاین", product.product_line],
              ["واریانت", product.variant],
              ["حجم", product.size_value == null ? null : `${product.size_value} ${product.size_unit ?? ""}`.trim()],
              ["وضعیت هویت", product.identity_status],
              ["وضعیت QA", product.qa_verdict],
              ["چرخهٔ محصول", product.status],
            ] as Array<[string, unknown]>).map(([label, value]) => <div key={label}><dt><strong>{label}</strong></dt><dd>{valueOrUnknown(value)}</dd></div>)}
          </dl>
        </section>
        <section className="pro-product-card" aria-labelledby="skin-product-knowledge">
          <h2 id="skin-product-knowledge">دانش تجمیع‌شدهٔ واجد شرایط</h2>
          {knowledgeError ? <p className="pro-muted">ProductKnowledge قابل دریافت نیست: {knowledgeError}</p> : null}
          {knowledge ? <dl>{labels.map(([key, label]) => <div key={key}><dt><strong>{label}</strong></dt><dd>{valueOrUnknown(knowledge[key])}</dd></div>)}</dl> : <p className="pro-muted">رکورد ProductKnowledge موجود یا قابل خواندن نیست؛ داده‌ای حدس زده نمی‌شود.</p>}
        </section>
        <section className="pro-product-card" aria-labelledby="skin-product-evidence">
          <h2 id="skin-product-evidence">شواهد و منشأ اطلاعات</h2>
          {evidence.length === 0 ? <p className="pro-muted">شاهدی برای این محصول از API دریافت نشد.</p> : <ul className="pro-ol">{evidence.map((item) => <li key={item.evidence_id}>
            <p><strong>{item.field ?? "فیلد نامشخص"}</strong> · {item.claim ?? "متن ادعا ثبت نشده"}</p>
            <p className="pro-muted">نوع ادعا: {valueOrUnknown(item.claim_type)} · QA: {valueOrUnknown(item.qa_status)} · شواهد: {valueOrUnknown(item.evidence_status)} · تعارض: {valueOrUnknown(item.conflict_status)}</p>
            <p>منبع: {item.source_reference ?? "ثبت نشده"} {item.source_type ? `· ${item.source_type}` : ""}</p>
          </li>)}</ul>}
        </section>
      </> : null}
    </section>
  );
}
