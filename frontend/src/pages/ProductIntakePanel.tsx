import { useState } from "react";
import { createProduct } from "../api/client";
import type { ProductCreateRequest } from "../types/api";

type Props = {
  onRegistered?: (productId: string) => void;
};

/**
 * PO product intake: free-text → draft fields → confirm → POST /products/
 * Extracts fields only; does not invent medical claims.
 */
export default function ProductIntakePanel({ onRegistered }: Props) {
  const [intakeRaw, setIntakeRaw] = useState("");
  const [draftId, setDraftId] = useState("");
  const [draftBrand, setDraftBrand] = useState("");
  const [draftName, setDraftName] = useState("");
  const [draftVariant, setDraftVariant] = useState("clear");
  const [draftSize, setDraftSize] = useState(50);
  const [draftUnit, setDraftUnit] = useState("ml");
  const [draftSpf, setDraftSpf] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  function buildDraftFromText(raw: string) {
    const text = raw.trim();
    if (!text) {
      setErr("متن معرفی محصول را بنویسید.");
      return;
    }
    setErr(null);
    setMsg(null);

    const spfM = text.match(/SPF\s*(\d+\+?)/i);
    const spf = spfM ? `SPF${spfM[1]}` : "";
    setDraftSpf(spf);

    const sizeM = text.match(/(\d+(?:\.\d+)?)\s*(ml|میلی\s*لیتر|میلیلیتر)/i);
    const size = sizeM ? parseFloat(sizeM[1]) : 50;
    setDraftSize(size);
    setDraftUnit("ml");

    let variant = "clear";
    if (/رنگی|tint|color/i.test(text)) variant = "tinted";
    else if (/بی\s*رنگ|بدون\s*رنگ|clear/i.test(text)) variant = "clear";
    setDraftVariant(variant);

    let brand = "Gallery";
    const latinBrand = text.match(/\b([A-Za-z][A-Za-z0-9]{1,24})\b/);
    if (latinBrand) brand = latinBrand[1];
    if (/پرودرما|proderma/i.test(text)) brand = "Proderma";
    if (/ایزدین|isdin/i.test(text)) brand = "ISDIN";
    if (/لاروش|la\s*roche/i.test(text)) brand = "LaRochePosay";
    if (/بیودرما|bioderma/i.test(text)) brand = "Bioderma";
    setDraftBrand(brand);

    setDraftName(text.replace(/\s+/g, " ").slice(0, 120));

    const slugBrand =
      brand.toUpperCase().replace(/[^A-Z0-9]+/g, "-").replace(/^-|-$/g, "") || "ITEM";
    const slugSpf = spf.replace("+", "PLUS") || "NOSPF";
    setDraftId(`${slugBrand}-${slugSpf}-${size}ML`.replace(/--+/g, "-"));
    setMsg("پیش‌نویس آماده است. بررسی/ویرایش کنید، سپس تأیید و ثبت.");
  }

  async function confirmRegister() {
    setErr(null);
    setMsg(null);
    if (!draftId.trim() || !draftBrand.trim() || !draftName.trim()) {
      setErr("شناسه، برند و نام محصول الزامی است.");
      return;
    }
    setBusy(true);
    try {
      const body: ProductCreateRequest = {
        product_id: draftId.trim(),
        brand: draftBrand.trim(),
        product_name: draftName.trim(),
        variant: draftVariant || null,
        size_value: draftSize,
        size_unit: draftUnit || "ml",
        identity_status: "VERIFIED",
        qa_verdict: "PENDING",
        status: "ACTIVE",
      };
      const created = await createProduct(body);
      setMsg(`ثبت شد: ${created.product_id}`);
      setIntakeRaw("");
      onRegistered?.(created.product_id);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="pro-panel">
      <h1>ورود محصول (تأیید مدیر)</h1>
      <p className="pro-lead">
        متن جعبه را بنویسید → پیش‌نویس فیلدها → ویرایش شما → تأیید و ثبت در کاتالوگ. ادعای درمانی اختراع نمی‌شود.
      </p>
      {err && <div className="pro-alert">{err}</div>}
      {msg && <div className="pro-status-msg">{msg}</div>}
      <div className="pro-form">
        <label className="pro-label" htmlFor="intake-raw">
          متن معرفی / جعبه
        </label>
        <textarea
          id="intake-raw"
          className="pro-input"
          rows={4}
          value={intakeRaw}
          onChange={(e) => setIntakeRaw(e.target.value)}
          placeholder="مثال: کرم ضد آفتاب و روشن‌کننده لک پوست بی‌رنگ SPF50 حجم 40 میلی‌لیتر پرودرما"
        />
        <div className="pro-actions">
          <button type="button" className="pro-btn-secondary" onClick={() => buildDraftFromText(intakeRaw)}>
            ساخت پیش‌نویس
          </button>
        </div>
        <fieldset className="pro-fieldset">
          <legend>پیش‌نویس (قابل ویرایش)</legend>
          <label className="pro-label">product_id</label>
          <input className="pro-input" value={draftId} onChange={(e) => setDraftId(e.target.value)} />
          <label className="pro-label">برند</label>
          <input className="pro-input" value={draftBrand} onChange={(e) => setDraftBrand(e.target.value)} />
          <label className="pro-label">نام محصول</label>
          <input className="pro-input" value={draftName} onChange={(e) => setDraftName(e.target.value)} />
          <label className="pro-label">variant</label>
          <input className="pro-input" value={draftVariant} onChange={(e) => setDraftVariant(e.target.value)} />
          <label className="pro-label">حجم</label>
          <input
            className="pro-input"
            type="number"
            value={draftSize}
            onChange={(e) => setDraftSize(Number(e.target.value) || 0)}
          />
          <label className="pro-label">واحد</label>
          <input className="pro-input" value={draftUnit} onChange={(e) => setDraftUnit(e.target.value)} />
          <label className="pro-label">SPF (نمایش)</label>
          <input className="pro-input" value={draftSpf} readOnly />
        </fieldset>
        <div className="pro-actions">
          <button type="button" className="pro-btn-primary" disabled={busy} onClick={() => void confirmRegister()}>
            {busy ? "در حال ثبت…" : "تأیید و ثبت در کاتالوگ"}
          </button>
        </div>
      </div>
    </section>
  );
}
