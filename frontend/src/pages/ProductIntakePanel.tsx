import { useEffect, useState } from "react";
import { createProduct, updateProduct } from "../api/client";
import type { ProductCreateRequest, ProductDTO, ProductUpdateRequest } from "../types/api";

type Props = {
  onRegistered?: (productId: string) => void;
  editProduct?: ProductDTO | null;
  onCancelEdit?: () => void;
};

type Draft = {
  product_id: string;
  brand: string;
  product_name: string;
  variant: string;
  size_value: number;
  size_unit: string;
  spf: string;
  category: string;
  barcode_gtin: string;
  market_region: string;
  packaging_version: string;
  identity_status: string;
  qa_verdict: string;
  status: string;
};

const EMPTY: Draft = {
  product_id: "",
  brand: "",
  product_name: "",
  variant: "clear",
  size_value: 50,
  size_unit: "ml",
  spf: "",
  category: "",
  barcode_gtin: "",
  market_region: "IR",
  packaging_version: "",
  identity_status: "VERIFIED",
  qa_verdict: "PENDING",
  status: "ACTIVE",
};

/** Complete protocol fields from intro text — extract only, no invented medical claims. */
export function completeFromIntro(raw: string): Draft {
  const text = raw.trim();
  const d: Draft = { ...EMPTY };

  const spfM = text.match(/SPF\s*(\d+\+?)/i);
  d.spf = spfM ? `SPF ${spfM[1]}` : "";

  const sizeM = text.match(/(\d+(?:\.\d+)?)\s*(ml|میلی\s*لیتر|میلیلیتر|گرم|g\b)/i);
  if (sizeM) {
    d.size_value = parseFloat(sizeM[1]);
    d.size_unit = /گرم|\bg\b/i.test(sizeM[2]) ? "g" : "ml";
  }

  if (/رنگی|tint|color/i.test(text)) d.variant = "tinted";
  else if (/بی\s*رنگ|بدون\s*رنگ|clear|بی‌رنگ/i.test(text)) d.variant = "clear";

  if (/پرودرما|proderma/i.test(text)) d.brand = "Proderma";
  else if (/ایزدین|isdin/i.test(text)) d.brand = "ISDIN";
  else if (/لاروش|la\s*roche|laroche/i.test(text)) d.brand = "La Roche-Posay";
  else if (/بیودرما|bioderma/i.test(text)) d.brand = "Bioderma";
  else if (/اوین|eucerin/i.test(text)) d.brand = "Eucerin";
  else if (/نوتروژنا|neutrogena/i.test(text)) d.brand = "Neutrogena";
  else {
    const latin = text.match(/\b([A-Z][A-Za-z0-9\-']{1,28})\b/);
    d.brand = latin ? latin[1] : "Gallery";
  }

  if (/ضد\s*آفتاب|ضدآفتاب|sunscreen|spf/i.test(text)) {
    if (/لک|unify|spot|lightening|روشن/i.test(text)) d.category = "ضدآفتاب ضدلک صورت";
    else if (/رنگی|tint/i.test(text)) d.category = "ضدآفتاب رنگی صورت";
    else d.category = "ضدآفتاب صورت";
  } else if (/آبرسان|مرطوب|hydrat|moistur/i.test(text)) d.category = "مرطوب‌کننده / آبرسان";
  else if (/ضدچروک|anti.?age/i.test(text)) d.category = "ضدپیری صورت";
  else d.category = "مراقبت پوست";

  let name = text.replace(/\s+/g, " ").slice(0, 100);
  if (d.spf && !/SPF/i.test(name)) name = `${name} (${d.spf})`;
  d.product_name = name;

  const slugBrand =
    d.brand.toUpperCase().replace(/[^A-Z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 20) || "ITEM";
  const slugSpf = d.spf.replace(/\s+/g, "").replace("+", "PLUS") || "GEN";
  const catHint = /ضدآفتاب|sunscreen/i.test(d.category) ? "SPF" : /آبرسان|مرطوب/i.test(d.category) ? "HYDR" : "SKIN";
  d.product_id = `${slugBrand}-${catHint}-${slugSpf}-${d.size_value}${d.size_unit.toUpperCase()}`
    .replace(/--+/g, "-")
    .slice(0, 64);

  d.identity_status = "VERIFIED";
  d.qa_verdict = "PENDING";
  d.status = "ACTIVE";
  d.market_region = "IR";
  return d;
}

function fromProduct(p: ProductDTO): Draft {
  return {
    product_id: p.product_id,
    brand: p.brand || "",
    product_name: p.product_name || "",
    variant: String(p.variant ?? "clear"),
    size_value: Number(p.size_value ?? 50),
    size_unit: String(p.size_unit ?? "ml"),
    spf: "",
    category: "",
    barcode_gtin: String((p as { barcode_gtin?: string }).barcode_gtin ?? ""),
    market_region: String((p as { market_region?: string }).market_region ?? "IR"),
    packaging_version: String((p as { packaging_version?: string }).packaging_version ?? ""),
    identity_status: p.identity_status || "VERIFIED",
    qa_verdict: p.qa_verdict || "PENDING",
    status: String((p as { status?: string }).status ?? "ACTIVE"),
  };
}

export default function ProductIntakePanel({ onRegistered, editProduct, onCancelEdit }: Props) {
  const [intro, setIntro] = useState("");
  const [draft, setDraft] = useState<Draft>(EMPTY);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const editing = Boolean(editProduct?.product_id);

  useEffect(() => {
    if (editProduct?.product_id) {
      setDraft(fromProduct(editProduct));
      setIntro("");
      setMsg(`ویرایش محصول: ${editProduct.product_id}`);
      setErr(null);
    }
  }, [editProduct]);

  function setField<K extends keyof Draft>(key: K, value: Draft[K]) {
    setDraft((prev) => ({ ...prev, [key]: value }));
  }

  function runComplete() {
    if (!intro.trim()) {
      setErr("ابتدا خلاصه معرفی محصول را بنویسید.");
      return;
    }
    const completed = completeFromIntro(intro);
    if (editing) completed.product_id = draft.product_id;
    setDraft(completed);
    setErr(null);
    setMsg("اطلاعات تکمیل شد. هر باکس را بررسی/ویرایش کنید، سپس تأیید و ذخیره.");
  }

  async function save() {
    setErr(null);
    setMsg(null);
    if (!draft.product_id.trim() || !draft.brand.trim() || !draft.product_name.trim()) {
      setErr("شناسه، برند و نام محصول الزامی است.");
      return;
    }
    setBusy(true);
    try {
      if (editing) {
        const body: ProductUpdateRequest = {
          brand: draft.brand.trim(),
          product_name: draft.product_name.trim(),
          variant: draft.variant || null,
          size_value: draft.size_value,
          size_unit: draft.size_unit || "ml",
          barcode_gtin: draft.barcode_gtin || null,
          market_region: draft.market_region || null,
          packaging_version: draft.packaging_version || null,
          identity_status: draft.identity_status,
          qa_verdict: draft.qa_verdict,
          status: draft.status,
        };
        const updated = await updateProduct(draft.product_id.trim(), body);
        setMsg(`به‌روزرسانی شد: ${updated.product_id}`);
        onRegistered?.(updated.product_id);
      } else {
        const body: ProductCreateRequest = {
          product_id: draft.product_id.trim(),
          brand: draft.brand.trim(),
          product_name: draft.product_name.trim(),
          variant: draft.variant || null,
          size_value: draft.size_value,
          size_unit: draft.size_unit || "ml",
          barcode_gtin: draft.barcode_gtin || null,
          market_region: draft.market_region || null,
          packaging_version: draft.packaging_version || null,
          identity_status: draft.identity_status || "VERIFIED",
          qa_verdict: draft.qa_verdict || "PENDING",
          status: draft.status || "ACTIVE",
        };
        const created = await createProduct(body);
        setMsg(`ذخیره شد: ${created.product_id}`);
        setIntro("");
        onRegistered?.(created.product_id);
      }
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="pro-panel">
      <h1>{editing ? "ویرایش محصول" : "ورود محصول (تکمیل هوشمند + تأیید مدیر)"}</h1>
      <p className="pro-lead">
        خلاصه را بنویسید → تکمیل خودکار فیلدهای پروتکل → ویرایش شما → تأیید و ذخیره. ادعای درمانی اختراع نمی‌شود.
      </p>
      {err && <div className="pro-alert">{err}</div>}
      {msg && <div className="pro-status-msg">{msg}</div>}

      {!editing && (
        <div className="pro-form">
          <label className="pro-label" htmlFor="intro-raw">
            ۱) خلاصه معرفی شما
          </label>
          <textarea
            id="intro-raw"
            className="pro-input"
            rows={3}
            value={intro}
            onChange={(e) => setIntro(e.target.value)}
            placeholder="مثال: کرم ضد آفتاب و روشن‌کننده لک پوست بی‌رنگ SPF50 حجم 40 میلی‌لیتر پرودرما"
          />
          <div className="pro-actions">
            <button type="button" className="pro-btn-primary" onClick={runComplete}>
              تکمیل هوشمند اطلاعات
            </button>
          </div>
        </div>
      )}

      <fieldset className="pro-fieldset" style={{ marginTop: "1rem" }}>
        <legend>۲) فیلدهای پروتکل (قابل ویرایش قبل از ذخیره)</legend>
        <div className="pro-grid-2">
          <div>
            <label className="pro-label">product_id</label>
            <input className="pro-input" value={draft.product_id} onChange={(e) => setField("product_id", e.target.value)} disabled={editing} />
          </div>
          <div>
            <label className="pro-label">برند</label>
            <input className="pro-input" value={draft.brand} onChange={(e) => setField("brand", e.target.value)} />
          </div>
          <div style={{ gridColumn: "1 / -1" }}>
            <label className="pro-label">نام محصول</label>
            <input className="pro-input" value={draft.product_name} onChange={(e) => setField("product_name", e.target.value)} />
          </div>
          <div>
            <label className="pro-label">variant</label>
            <input className="pro-input" value={draft.variant} onChange={(e) => setField("variant", e.target.value)} />
          </div>
          <div>
            <label className="pro-label">SPF</label>
            <input className="pro-input" value={draft.spf} onChange={(e) => setField("spf", e.target.value)} />
          </div>
          <div>
            <label className="pro-label">حجم</label>
            <input className="pro-input" type="number" value={draft.size_value} onChange={(e) => setField("size_value", Number(e.target.value) || 0)} />
          </div>
          <div>
            <label className="pro-label">واحد</label>
            <input className="pro-input" value={draft.size_unit} onChange={(e) => setField("size_unit", e.target.value)} />
          </div>
          <div>
            <label className="pro-label">دسته</label>
            <input className="pro-input" value={draft.category} onChange={(e) => setField("category", e.target.value)} />
          </div>
          <div>
            <label className="pro-label">بارکد / GTIN</label>
            <input className="pro-input" value={draft.barcode_gtin} onChange={(e) => setField("barcode_gtin", e.target.value)} placeholder="اختیاری" />
          </div>
          <div>
            <label className="pro-label">منطقه بازار</label>
            <input className="pro-input" value={draft.market_region} onChange={(e) => setField("market_region", e.target.value)} />
          </div>
          <div>
            <label className="pro-label">identity_status</label>
            <select className="pro-input" value={draft.identity_status} onChange={(e) => setField("identity_status", e.target.value)}>
              <option value="VERIFIED">VERIFIED</option>
              <option value="NEEDS_REVIEW">NEEDS_REVIEW</option>
              <option value="PARTIAL_IDENTITY">PARTIAL_IDENTITY</option>
              <option value="CONFLICT">CONFLICT</option>
            </select>
          </div>
          <div>
            <label className="pro-label">status</label>
            <select className="pro-input" value={draft.status} onChange={(e) => setField("status", e.target.value)}>
              <option value="ACTIVE">ACTIVE</option>
              <option value="DRAFT">DRAFT</option>
            </select>
          </div>
          <div>
            <label className="pro-label">qa_verdict</label>
            <select className="pro-input" value={draft.qa_verdict} onChange={(e) => setField("qa_verdict", e.target.value)}>
              <option value="PENDING">PENDING</option>
              <option value="VALID">VALID</option>
              <option value="INVALID">INVALID</option>
            </select>
          </div>
        </div>
      </fieldset>

      <div className="pro-actions" style={{ marginTop: "1rem" }}>
        <button type="button" className="pro-btn-primary" disabled={busy} onClick={() => void save()}>
          {busy ? "در حال ذخیره…" : editing ? "تأیید و به‌روزرسانی" : "تأیید نهایی و ذخیره"}
        </button>
        {editing && (
          <button
            type="button"
            className="pro-btn-secondary"
            onClick={() => {
              onCancelEdit?.();
              setDraft(EMPTY);
              setMsg(null);
            }}
          >
            انصراف از ویرایش
          </button>
        )}
      </div>
    </section>
  );
}
