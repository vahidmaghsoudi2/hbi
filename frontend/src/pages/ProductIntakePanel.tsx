import { useEffect, useState } from "react";
import {
  checkDuplicate,
  createProduct,
  createResearchDraft,
  getProductEvidence,
  verifyEvidence,
  recordDuplicateDecision,
  updateProduct,
} from "../api/client";
import type {
  DuplicateCheckResponse,
  EvidenceDTO,
  ProductCreateRequest,
  ProductDTO,
  ProductUpdateRequest,
} from "../types/api";

type Props = {
  token?: string | null;
  onEnsureSession?: () => Promise<string | null>;
  onRegistered?: (productId: string) => void;
  editProduct?: ProductDTO | null;
  onCancelEdit?: () => void;
};

const PRODUCT_LINE_OPTIONS = [
  { value: "SKIN", label: "پوست (SKIN)" },
  { value: "HAIR", label: "مو (HAIR)" },
  { value: "BEAUTY", label: "زیبایی (BEAUTY)" },
  { value: "TOOLS", label: "ابزار (TOOLS)" },
  { value: "OTHER", label: "متفرقه (OTHER)" },
] as const;

type Draft = {
  product_id: string;
  brand: string;
  product_name: string;
  product_line: string;
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
  product_line: "",
  variant: "clear",
  size_value: 50,
  size_unit: "ml",
  spf: "",
  category: "",
  barcode_gtin: "",
  market_region: "",
  packaging_version: "",
  identity_status: "NEEDS_REVIEW",
  qa_verdict: "PENDING",
  status: "DRAFT",
};

export function normalizeProductLine(value: string | null | undefined): string {
  return (value ?? "").trim().toUpperCase();
}

export function productLineForPatch(
  initialLine: string | null | undefined,
  currentLine: string | null | undefined,
): string | undefined {
  const initial = normalizeProductLine(initialLine);
  const current = normalizeProductLine(currentLine);
  if (current === initial) return undefined;
  if (!current) return undefined;
  return current;
}

export type IdentitySnapshot = {
  product_id: string;
  brand: string;
  product_name: string;
  variant: string;
  size_value: number | null;
  size_unit: string;
  barcode_gtin: string;
  market_region: string;
  packaging_version: string;
};

export function buildIdentitySnapshot(d: {
  product_id: string;
  brand: string;
  product_name: string;
  variant: string;
  size_value: number;
  size_unit: string;
  barcode_gtin: string;
  market_region: string;
  packaging_version: string;
}): IdentitySnapshot {
  return {
    product_id: d.product_id.trim(),
    brand: d.brand.trim(),
    product_name: d.product_name.trim(),
    variant: (d.variant || "").trim(),
    size_value: Number.isFinite(d.size_value) ? d.size_value : null,
    size_unit: (d.size_unit || "").trim(),
    barcode_gtin: (d.barcode_gtin || "").trim(),
    market_region: (d.market_region || "").trim(),
    packaging_version: (d.packaging_version || "").trim(),
  };
}

export function identityFingerprint(s: IdentitySnapshot): string {
  return JSON.stringify({
    product_id: s.product_id.toLowerCase(),
    brand: s.brand.toLowerCase(),
    product_name: s.product_name.toLowerCase(),
    variant: s.variant.toLowerCase(),
    size_value: s.size_value,
    size_unit: s.size_unit.toLowerCase(),
    barcode_gtin: s.barcode_gtin.toLowerCase(),
    market_region: s.market_region.toLowerCase(),
    packaging_version: s.packaging_version.toLowerCase(),
  });
}

export function canCreateAfterDuplicateCheck(args: {
  check: DuplicateCheckResponse | null;
  checkFingerprint: string | null;
  currentFingerprint: string;
  recordedDecision: string | null;
}): { ok: boolean; reason: string } {
  const { check, checkFingerprint, currentFingerprint, recordedDecision } = args;
  if (!check || !check.check_id) return { ok: false, reason: "DUPLICATE_CHECK_REQUIRED" };
  if (!checkFingerprint || checkFingerprint !== currentFingerprint) {
    return { ok: false, reason: "IDENTITY_CHANGED_RECHECK_REQUIRED" };
  }
  const result = String(check.result || "").toUpperCase();
  if (result === "EXISTING") return { ok: false, reason: "EXISTING_BLOCKED" };
  if (result === "NEW") return { ok: true, reason: "NEW" };
  if (result === "POSSIBLE_MATCH") {
    if (String(recordedDecision || "").toUpperCase() === "NEW") {
      return { ok: true, reason: "POSSIBLE_MATCH_NEW_DECISION" };
    }
    return { ok: false, reason: "OPERATOR_DECISION_REQUIRED" };
  }
  return { ok: false, reason: "UNKNOWN_CHECK_RESULT" };
}

/** Extract-only helper for encyclopedia smart-complete; does not write Product Master. */
export function completeFromIntro(raw: string): Draft {
  const text = raw.trim();
  const d: Draft = { ...EMPTY };
  const spfM = text.match(/SPF\s*(\d+\+?)/i);
  d.spf = spfM ? `SPF ${spfM[1]}` : "";
  const sizeM = text.match(/(\d+(?:\.\d+)?)\s*(ml|میلی[\s‌]*لیتر|میلیلیتر|گرم|g\b)/i);
  if (sizeM) {
    d.size_value = parseFloat(sizeM[1]);
    d.size_unit = /گرم|\bg\b/i.test(sizeM[2]) ? "g" : "ml";
  }
  if (/رنگی|tint|color/i.test(text)) d.variant = "tinted";
  else if (/بی\s*رنگ|بدون\s*رنگ|clear|بی‌رنگ/i.test(text)) d.variant = "clear";
  if (/پرودرما|proderma/i.test(text)) d.brand = "Proderma";
  else if (/ایزدین|isdin/i.test(text)) d.brand = "ISDIN";
  else if (/skin\s*1004/i.test(text)) d.brand = "SKIN1004";
  else if (/نوتروژنا|neutrogena/i.test(text)) d.brand = "Neutrogena";
  else if (/کوزارکس|cosrx/i.test(text)) d.brand = "COSRX";
  else if (/گارنیر|garnier/i.test(text)) d.brand = "Garnier";
  else if (/کلینیک|clinique/i.test(text)) d.brand = "Clinique";
  else if (/آنوا|anua/i.test(text)) d.brand = "Anua";
  if (/ضد\s*آفتاب|ضدآفتاب|sunscreen|spf/i.test(text)) d.category = "ضدآفتاب";
  else if (/آبرسان|مرطوب|hydrat|moistur/i.test(text)) d.category = "مرطوب‌کننده / آبرسان";
  else d.category = "";
  d.product_name = text.replace(/\s+/g, " ").slice(0, 100);
  d.product_id = "";
  d.identity_status = "NEEDS_REVIEW";
  d.qa_verdict = "PENDING";
  d.status = "DRAFT";
  d.market_region = "";
  d.product_line = "";
  return d;
}

function fromProduct(p: ProductDTO): Draft {
  const lineRaw = (p as { product_line?: string | null }).product_line;
  return {
    product_id: p.product_id,
    brand: p.brand || "",
    product_name: p.product_name || "",
    product_line: typeof lineRaw === "string" ? lineRaw : "",
    variant: String(p.variant ?? "clear"),
    size_value: Number(p.size_value ?? 50),
    size_unit: String(p.size_unit ?? "ml"),
    spf: "",
    category: "",
    barcode_gtin: String((p as { barcode_gtin?: string }).barcode_gtin ?? ""),
    market_region: String((p as { market_region?: string }).market_region ?? ""),
    packaging_version: String((p as { packaging_version?: string }).packaging_version ?? ""),
    identity_status: p.identity_status || "VERIFIED",
    qa_verdict: p.qa_verdict || "PENDING",
    status: String((p as { status?: string }).status ?? "ACTIVE"),
  };
}

export default function ProductIntakePanel({
  token,
  onEnsureSession,
  onRegistered,
  editProduct,
  onCancelEdit,
}: Props) {
  const [draft, setDraft] = useState<Draft>(EMPTY);
  const [initialProductLine, setInitialProductLine] = useState("");
  const [busy, setBusy] = useState(false);
  const [dupBusy, setDupBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [dupResult, setDupResult] = useState<DuplicateCheckResponse | null>(null);
  const [dupFingerprint, setDupFingerprint] = useState<string | null>(null);
  const [recordedDecision, setRecordedDecision] = useState<string | null>(null);
  const [decisionReason, setDecisionReason] = useState("");
  const [deferredOrigin, setDeferredOrigin] = useState<"" | "DOMESTIC" | "FOREIGN">("");
  const [deferredBuyPrice, setDeferredBuyPrice] = useState("");
  const [deferredSellPrice, setDeferredSellPrice] = useState("");
  const editing = Boolean(editProduct?.product_id);

  useEffect(() => {
    if (editProduct?.product_id) {
      const d = fromProduct(editProduct);
      setDraft(d);
      setInitialProductLine(d.product_line);
      setDupResult(null);
      setDupFingerprint(null);
      setRecordedDecision(null);
    } else {
      setDraft(EMPTY);
      setInitialProductLine("");
    }
  }, [editProduct]);

  function setField<K extends keyof Draft>(key: K, value: Draft[K]) {
    setDraft((prev) => ({ ...prev, [key]: value }));
    setDupResult(null);
    setDupFingerprint(null);
    setRecordedDecision(null);
  }

  async function runDuplicateCheck() {
    setErr(null);
    setMsg(null);
    if (!draft.product_name.trim()) {
      setErr("نام کالا الزامی است.");
      return;
    }
    if (!normalizeProductLine(draft.product_line)) {
      setErr("لاین محصول الزامی است.");
      return;
    }
    setDupBusy(true);
    try {
      const activeToken = (await onEnsureSession?.()) ?? token;
      if (!activeToken) throw new Error("نشست فعال لازم است.");
      const snap = buildIdentitySnapshot(draft);
      const fp = identityFingerprint(snap);
      const res = await checkDuplicate(
        {
          brand: snap.brand || undefined,
          product_name: snap.product_name,
          variant: snap.variant || undefined,
          size_value: snap.size_value ?? undefined,
          size_unit: snap.size_unit || undefined,
          barcode_gtin: snap.barcode_gtin || undefined,
          market_region: snap.market_region || undefined,
          packaging_version: snap.packaging_version || undefined,
        },
        activeToken,
      );
      setDupResult(res);
      setDupFingerprint(fp);
      setRecordedDecision(null);
      setMsg(`نتیجه بررسی تکراری: ${res.result}`);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setDupBusy(false);
    }
  }

  async function recordDecision(decision: "NEW" | "EXISTING") {
    setErr(null);
    if (!dupResult?.check_id) {
      setErr("ابتدا DuplicateCheck را اجرا کنید.");
      return;
    }
    setDupBusy(true);
    try {
      const activeToken = (await onEnsureSession?.()) ?? token;
      if (!activeToken) throw new Error("نشست فعال لازم است.");
      await recordDuplicateDecision(
        dupResult.check_id,
        { decision, reason: decisionReason.trim() || undefined },
        activeToken,
      );
      setRecordedDecision(decision);
      setMsg(`تصمیم اپراتور ثبت شد: ${decision}`);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setDupBusy(false);
    }
  }

  async function save() {
    setErr(null);
    setMsg(null);
    if (!draft.product_name.trim()) {
      setErr("نام کالا الزامی است.");
      return;
    }
    if (!normalizeProductLine(draft.product_line)) {
      setErr("لاین محصول الزامی است.");
      return;
    }
    setBusy(true);
    try {
      const activeToken = (await onEnsureSession?.()) ?? token;
      if (!activeToken) throw new Error("نشست فعال لازم است.");
      if (editing && draft.product_id) {
        const patch: ProductUpdateRequest = {
          product_name: draft.product_name.trim(),
          brand: draft.brand.trim() || undefined,
        };
        const linePatch = productLineForPatch(initialProductLine, draft.product_line);
        if (linePatch) patch.product_line = linePatch;
        await updateProduct(draft.product_id, patch, activeToken);
        setMsg(`ویرایش ذخیره شد: ${draft.product_id}`);
        onRegistered?.(draft.product_id);
      } else {
        const gate = canCreateAfterDuplicateCheck({
          check: dupResult,
          checkFingerprint: dupFingerprint,
          currentFingerprint: identityFingerprint(buildIdentitySnapshot(draft)),
          recordedDecision,
        });
        if (!gate.ok) {
          setErr(`ثبت ممکن نیست: ${gate.reason}`);
          setBusy(false);
          return;
        }
        const payload: ProductCreateRequest = {
          brand: draft.brand.trim() || "—",
          product_name: draft.product_name.trim(),
          product_line: normalizeProductLine(draft.product_line),
          variant: draft.variant || undefined,
          size_value: draft.size_value,
          size_unit: draft.size_unit || undefined,
          barcode_gtin: draft.barcode_gtin || undefined,
          market_region: draft.market_region || undefined,
          packaging_version: draft.packaging_version || undefined,
          duplicate_check_id: dupResult?.check_id,
        };
        const created = await createProduct(payload, activeToken);
        setMsg(`ثبت Draft: ${created.product_id} (قیمت/مبدأ در این فاز ذخیره نشد)`);
        onRegistered?.(created.product_id);
        setDraft(EMPTY);
        setDupResult(null);
        setDupFingerprint(null);
        setRecordedDecision(null);
      }
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="pro-panel">
      <h1>{editing ? "ویرایش محصول" : "ورود محصول (ثبت کاتالوگی)"}</h1>
      <p className="pro-lead">
        ثبت کاتالوگی: نام کالا و لاین محصول را وارد کنید، DuplicateCheck را اجرا کنید، سپس ثبت Draft.
        کد یکتا (HBI-PROD-…) را سیستم پس از عبور از بررسی تکراری می‌سازد. تکمیل هوشمند از این منو حذف شده و به دانشنامه منتقل می‌شود.
        قیمت خرید/فروش و داخلی/خارجی در این فاز فقط روی فرم اعلام می‌شوند و تا اتصال بعدی به انبار/قیمت ذخیرهٔ قطعی نیستند.
      </p>
      {err && <div className="pro-alert">{err}</div>}
      {msg && (
        <div className="pro-status-msg" role="status" aria-live="polite">
          <strong>✓ وضعیت</strong>
          <div style={{ marginTop: "0.25rem" }}>{msg}</div>
        </div>
      )}

      <fieldset className="pro-fieldset" style={{ marginTop: "1rem" }}>
        <legend>۱) مشخصات کاتالوگی</legend>
        <div className="pro-grid-2">
          {!editing && (
            <div style={{ gridColumn: "1 / -1" }}>
              <p className="pro-lead">شناسهٔ محصول پس از DuplicateCheck توسط سیستم تولید می‌شود.</p>
            </div>
          )}
          {editing && (
            <div>
              <label className="pro-label">کد یکتا</label>
              <input className="pro-input" value={draft.product_id} readOnly />
            </div>
          )}
          <div>
            <label className="pro-label">نام کالا *</label>
            <input
              className="pro-input"
              value={draft.product_name}
              onChange={(e) => setField("product_name", e.target.value)}
            />
          </div>
          <div>
            <label className="pro-label" htmlFor="product-line-select">لاین محصول *</label>
            <select
              id="product-line-select"
              className="pro-input"
              value={draft.product_line}
              onChange={(e) => setField("product_line", e.target.value)}
            >
              <option value="">— انتخاب لاین —</option>
              {PRODUCT_LINE_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="pro-label">برند (اختیاری)</label>
            <input className="pro-input" value={draft.brand} onChange={(e) => setField("brand", e.target.value)} />
          </div>
        </div>
      </fieldset>

      <fieldset className="pro-fieldset" style={{ marginTop: "1rem" }}>
        <legend>۲) قیمت و داخلی/خارجی (فاز بعد — هنوز ذخیره نمی‌شود)</legend>
        <p className="pro-lead" style={{ fontSize: "0.9rem" }}>
          این باکس‌ها در فاز بعد به انبار/نرخ دلار وصل می‌شوند. کالای خارجی: خرید و فروش به دلار؛ نمایش ریالی فروش با نرخ روز؛ قیمت خرید دلاری با نرخ روز عوض نمی‌شود.
        </p>
        <div className="pro-grid-2">
          <div>
            <label className="pro-label" htmlFor="deferred-origin">داخلی یا خارجی</label>
            <select id="deferred-origin" className="pro-input" value={deferredOrigin} onChange={(e) => setDeferredOrigin(e.target.value as "" | "DOMESTIC" | "FOREIGN")}>
              <option value="">— انتخاب —</option>
              <option value="DOMESTIC">داخلی (ریال)</option>
              <option value="FOREIGN">خارجی (دلار)</option>
            </select>
          </div>
          <div>
            <label className="pro-label" htmlFor="deferred-buy">قیمت خرید {deferredOrigin === "FOREIGN" ? "(USD)" : deferredOrigin === "DOMESTIC" ? "(ریال)" : ""}</label>
            <input id="deferred-buy" className="pro-input" value={deferredBuyPrice} onChange={(e) => setDeferredBuyPrice(e.target.value)} inputMode="decimal" />
          </div>
          <div>
            <label className="pro-label" htmlFor="deferred-sell">قیمت فروش {deferredOrigin === "FOREIGN" ? "(USD)" : deferredOrigin === "DOMESTIC" ? "(ریال)" : ""}</label>
            <input id="deferred-sell" className="pro-input" value={deferredSellPrice} onChange={(e) => setDeferredSellPrice(e.target.value)} inputMode="decimal" />
          </div>
        </div>
      </fieldset>

      {!editing && (
        <div className="pro-actions" style={{ marginTop: "1rem" }}>
          <button type="button" className="pro-btn-secondary" disabled={dupBusy} onClick={() => void runDuplicateCheck()}>
            بررسی تکراری (DuplicateCheck)
          </button>
          {dupResult?.result === "POSSIBLE_MATCH" && (
            <>
              <input className="pro-input" placeholder="دلیل تصمیم" value={decisionReason} onChange={(e) => setDecisionReason(e.target.value)} />
              <button type="button" className="pro-btn-secondary" disabled={dupBusy} onClick={() => void recordDecision("NEW")}>تصمیم: کالای جدید</button>
              <button type="button" className="pro-btn-secondary" disabled={dupBusy} onClick={() => void recordDecision("EXISTING")}>تصمیم: موجود</button>
            </>
          )}
        </div>
      )}

      <div className="pro-actions" style={{ marginTop: "1rem" }}>
        <button type="button" className="pro-btn-primary" disabled={busy} onClick={() => void save()}>
          {editing ? "ذخیره ویرایش" : "ثبت Draft"}
        </button>
        {editing && onCancelEdit && (
          <button type="button" className="pro-btn-secondary" onClick={onCancelEdit}>انصراف</button>
        )}
      </div>
    </section>
  );
}
