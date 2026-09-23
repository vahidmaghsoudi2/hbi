/**
 * INVENTORY-OUTFLOW-001 — مخارج و ضایعات (non-customer stock exit).
 * Not Sale. Not Purchase. Admin-only (matches POST /inventory/outflow AuthZ).
 */
import { useState } from "react";
import { Link } from "react-router-dom";
import { recordInventoryOutflow } from "../api/client";

const REASONS: { value: "DAMAGE_WASTE" | "INTERNAL_USE" | "SHORTAGE_LOSS" | "OTHER"; label: string }[] = [
  { value: "DAMAGE_WASTE", label: "خرابی / ضایعات" },
  { value: "INTERNAL_USE", label: "مصرف داخلی" },
  { value: "SHORTAGE_LOSS", label: "کسری / مفقودی" },
  { value: "OTHER", label: "سایر" },
];

/** Backend requires ROLE_ADMIN only — never Operator/Editor token. */
function adminAccessToken(): string | null {
  return sessionStorage.getItem("hbi_admin_access_token");
}

export default function OutflowPage() {
  const [productId, setProductId] = useState("");
  const [quantity, setQuantity] = useState("");
  const [reason, setReason] = useState<(typeof REASONS)[number]["value"]>("DAMAGE_WASTE");
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const hasAdmin = Boolean(adminAccessToken());

  async function submit() {
    setErr(null);
    setMsg(null);
    const token = adminAccessToken();
    if (!token) {
      setErr("برای ثبت خروج غیرمشتری نشست Admin لازم است (نه Operator).");
      return;
    }
    if (!productId.trim()) {
      setErr("شناسه محصول الزامی است.");
      return;
    }
    const quantityValue = Number(quantity);\n    if (!Number.isInteger(quantityValue) || quantityValue < 1) {
      setErr("تعداد باید حداقل ۱ باشد.");
      return;
    }
    setBusy(true);
    try {
      const result = await recordInventoryOutflow(
        {
          product_id: productId.trim(),
          quantity: quantityValue,
          reason,
          note: note.trim() || undefined,
        },
        token
      );
      setMsg(
        `خروج ثبت شد: ${result.outflow_id} · علت ${result.reason} · موجودی باقی‌مانده ${result.inventory?.quantity_available ?? "—"}`
      );
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="pro-page" dir="rtl">
      <header className="pro-header">
        <h1>مخارج و ضایعات</h1>
        <p className="pro-lead">
          خروج کالا از موجودی گالری بدون فروش به مشتری. این مسیر آمار فروش را افزایش نمی‌دهد. فقط Admin.
        </p>
        <nav className="pro-nav">
          <Link to="/" className="pro-nav-btn">
            خانه
          </Link>
          <Link to="/purchase" className="pro-nav-btn">
            خرید (ورود)
          </Link>
          <Link to="/accounting" className="pro-nav-btn">
            حسابداری
          </Link>
        </nav>
      </header>

      <p className="pro-status-bar">
        <span className={hasAdmin ? "dot on" : "dot"} />
        <span>{hasAdmin ? "Admin فعال" : "Admin لازم است"}</span>
      </p>

      {!hasAdmin && (
        <p className="pro-error">
          نشست Admin در این مرورگر وجود ندارد. ابتدا نشست مدیریتی را ایجاد کنید، سپس این صفحه را نوسازی کنید.
        </p>
      )}

      <section className="pro-card">
        <h2>ثبت خروج غیرمشتری</h2>
        <label>
          شناسه محصول
          <input value={productId} onChange={(e) => setProductId(e.target.value)} placeholder="PRODUCT-ID" disabled={!hasAdmin} />
        </label>
        <label>
          تعداد
          <input
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            value={quantity}
            disabled={!hasAdmin}
            onChange={(e) => setQuantity(e.target.value.replace(/[^0-9]/g, ""))}
          />
        </label>
        <label>
          علت خروج
          <select value={reason} disabled={!hasAdmin} onChange={(e) => setReason(e.target.value as typeof reason)}>
            {REASONS.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          یادداشت (اختیاری)
          <input value={note} disabled={!hasAdmin} onChange={(e) => setNote(e.target.value)} placeholder="توضیح کوتاه" />
        </label>
        <button type="button" className="pro-btn-primary" disabled={busy || !hasAdmin} onClick={() => void submit()}>
          {busy ? "در حال ثبت…" : "ثبت خروج"}
        </button>
        {msg && <p className="pro-ok">{msg}</p>}
        {err && <p className="pro-error">{err}</p>}
      </section>

      <p className="pro-muted">
        خرید = ورود از تأمین‌کننده · فروش = خروج به مشتری · مخارج و ضایعات = خروج بدون فروش مشتری
      </p>
    </div>
  );
}
