import { useEffect, useState } from "react";
import {
  checkDuplicate,
  createProduct,
  recordDuplicateDecision,
  updateProduct,
} from "../api/client";
import type {
  DuplicateCheckResponse,
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

/** Product Line V1 — operator classification only; never inferred from text/category/AI. */
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
  market_region: "IR",
  packaging_version: "",
  identity_status: "NEEDS_REVIEW",
  qa_verdict: "PENDING",
  status: "DRAFT",
};

/** Normalize for compare / API (trim + upper). Empty stays empty. */
export function normalizeProductLine(value: string | null | undefined): string {
  return (value ?? "").trim().toUpperCase();
}

/**
 * Option-2 semantic: include product_line in PATCH only when the operator
 * actually changed it relative to the value loaded at Edit start.
 */
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

/** Identity fields bound to DuplicateCheck input_snapshot (backend WP-01). */
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

/** Stable fingerprint; any change invalidates prior check/decision. */
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

/**
 * Gate: may the operator proceed to create after a DuplicateCheck result?
 * Pure helper for UI + unit verification without browser harness.
 */
export function canCreateAfterDuplicateCheck(args: {
  check: DuplicateCheckResponse | null;
  checkFingerprint: string | null;
  currentFingerprint: string;
  recordedDecision: string | null;
}): { ok: boolean; reason: string } {
  const { check, checkFingerprint, currentFingerprint, recordedDecision } = args;
  if (!check || !check.check_id) {
    return { ok: false, reason: "DUPLICATE_CHECK_REQUIRED" };
  }
  if (!checkFingerprint || checkFingerprint !== currentFingerprint) {
    return { ok: false, reason: "IDENTITY_CHANGED_RECHECK_REQUIRED" };
  }
  const result = String(check.result || "").toUpperCase();
  if (result === "EXISTING") {
    return { ok: false, reason: "EXISTING_BLOCKED" };
  }
  if (result === "NEW") {
    return { ok: true, reason: "NEW" };
  }
  if (result === "POSSIBLE_MATCH") {
    if (String(recordedDecision || "").toUpperCase() === "NEW") {
      return { ok: true, reason: "POSSIBLE_MATCH_NEW_DECISION" };
    }
    return { ok: false, reason: "OPERATOR_DECISION_REQUIRED" };
  }
  return { ok: false, reason: "UNKNOWN_CHECK_RESULT" };
}

/** Complete protocol fields from intro text — extract only, no invented medical claims. */
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

  const brandMarker = text.match(/(?:برند|brand)\s*[:：-]?\s*([^،,;؛|]+?)(?=\s*(?:[،,;؛|]|\b(?:حجم|volume|spf|SPF)\b)|$)/i);
  if (brandMarker?.[1]?.trim()) {
    d.brand = brandMarker[1].trim().replace(/\s+/g, " ");
  } else if (/پرودرما|proderma/i.test(text)) d.brand = "Proderma";
  else if (/ایزدین|isdin/i.test(text)) d.brand = "ISDIN";
  else if (/لاروش|la\s*roche|laroche/i.test(text)) d.brand = "La Roche-Posay";
  else if (/بیودرما|bioderma/i.test(text)) d.brand = "Bioderma";
  else if (/اوین|eucerin/i.test(text)) d.brand = "Eucerin";
  else if (/نوتروژنا|neutrogena/i.test(text)) d.brand = "Neutrogena";
  else {
    const latin = text.match(/\b([A-Z][A-Za-z0-9\-']{1,28}(?:\s+[A-Z][A-Za-z0-9\-']{1,28}){0,3})\b/);
    d.brand = latin ? latin[1].trim() : "";
  }

  if (/ضد\s*آفتاب|ضدآفتاب|sunscreen|spf/i.test(text)) {
    if (/لک|unify|spot|lightening|روشن/i.test(text)) d.category = "ضدآفتاب ضدلک صورت";
    else if (/رنگی|tint/i.test(text)) d.category = "ضدآفتاب رنگی صورت";
    else d.category = "ضدآفتاب صورت";
  } else if (/آبرسان|مرطوب|hydrat|moistur/i.test(text)) d.category = "مرطوب‌کننده / آبرسان";
  else if (/ضدچروک|anti.?age/i.test(text)) d.category = "ضدپیری صورت";
  else d.category = "مراقبت پوست";

  const nameBeforeMetadata = text.match(/^(.*?)(?=\s*(?:،|,)\s*(?:برند|brand)\b|\s+(?:حجم|volume)\s+\d|\s+(?:SPF)\s*\d+\+?\s*(?:حجم|volume)\b)/i);
  let name = (nameBeforeMetadata?.[1] ?? text).trim().replace(/\s+/g, " ").slice(0, 100);
  if (d.spf && !/SPF/i.test(name)) name = name + " (" + d.spf + ")";
  d.product_name = name;

  const slugBrand =
    d.brand.toUpperCase().replace(/[^A-Z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 20) || "ITEM";
  const slugSpf = d.spf.replace(/\s+/g, "").replace("+", "PLUS") || "GEN";
  const catHint = /ضدآفتاب|sunscreen/i.test(d.category) ? "SPF" : /آبرسان|مرطوب/i.test(d.category) ? "HYDR" : "SKIN";
  d.product_id = `${slugBrand}-${catHint}-${slugSpf}-${d.size_value}${d.size_unit.toUpperCase()}`
    .replace(/--+/g, "-")
    .slice(0, 64);

  d.identity_status = "NEEDS_REVIEW";
  d.qa_verdict = "PENDING";
  d.status = "DRAFT";
  d.market_region = "IR";
  // product_line intentionally left empty — operator must select explicitly
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
    market_region: String((p as { market_region?: string }).market_region ?? "IR"),
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
  const [intro, setIntro] = useState("");
  const [draft, setDraft] = useState<Draft>(EMPTY);
  /** Baseline product_line at Edit entry — used so unchanged line is omitted from PATCH. */
  const [initialProductLine, setInitialProductLine] = useState("");
  const [busy, setBusy] = useState(false);
  const [dupBusy, setDupBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [dupResult, setDupResult] = useState<DuplicateCheckResponse | null>(null);
  const [dupFingerprint, setDupFingerprint] = useState<string | null>(null);
  const [recordedDecision, setRecordedDecision] = useState<string | null>(null);
  const [decisionReason, setDecisionReason] = useState("");
  const editing = Boolean(editProduct?.product_id);

  useEffect(() => {
    if (editProduct?.product_id) {
      const next = fromProduct(editProduct);
      setDraft(next);
      setInitialProductLine(normalizeProductLine(next.product_line));
      setIntro("");
      setMsg(`ویرایش محصول: ${editProduct.product_id}`);
      setErr(null);
      setDupResult(null);
      setDupFingerprint(null);
      setRecordedDecision(null);
    }
  }, [editProduct]);

  function clearDuplicateState() {
    setDupResult(null);
    setDupFingerprint(null);
    setRecordedDecision(null);
  }

  function setField<K extends keyof Draft>(key: K, value: Draft[K]) {
    setDraft((prev) => {
      const next = { ...prev, [key]: value };
      // Identity change invalidates prior DuplicateCheck / operator decision
      const identityKeys: (keyof Draft)[] = [
        "product_id",
        "brand",
        "product_name",
        "variant",
        "size_value",
        "size_unit",
        "barcode_gtin",
        "market_region",
        "packaging_version",
      ];
      if (identityKeys.includes(key)) {
        setDupResult(null);
        setDupFingerprint(null);
        setRecordedDecision(null);
      }
      return next;
    });
  }

  function runComplete() {
    if (!intro.trim()) {
      setErr("ابتدا خلاصه معرفی محصول را بنویسید.");
      return;
    }
    const completed = completeFromIntro(intro);
    if (editing) completed.product_id = draft.product_id;
    // Preserve operator product_line selection; never infer from intro text
    completed.product_line = draft.product_line;
    setDraft(completed);
    clearDuplicateState();
    setErr(null);
    setMsg("اطلاعات پیشنهادی تکمیل شد. هر باکس را بررسی/ویرایش کنید؛ سپس بررسی تکراری و ثبت Draft.");
  }

  async function runDuplicateCheck() {
    setErr(null);
    setMsg(null);
    if (editing) return;
    if (!draft.product_id.trim() || !draft.brand.trim() || !draft.product_name.trim()) {
      setErr("برای بررسی تکراری، شناسه، برند و نام محصول الزامی است.");
      return;
    }
    setDupBusy(true);
    try {
      const activeToken = (await onEnsureSession?.()) ?? token;
      if (!activeToken) {
        setErr("برای بررسی تکراری، نشست فعال ایجاد نشد.");
        return;
      }
      const snap = buildIdentitySnapshot(draft);
      const fp = identityFingerprint(snap);
      const body = {
        product_id: snap.product_id || null,
        brand: snap.brand || null,
        product_name: snap.product_name || null,
        variant: snap.variant || null,
        size_value: snap.size_value,
        size_unit: snap.size_unit || null,
        barcode_gtin: snap.barcode_gtin || null,
        market_region: snap.market_region || null,
        packaging_version: snap.packaging_version || null,
      };
      const result = await checkDuplicate(body, activeToken);
      setDupResult(result);
      setDupFingerprint(fp);
      setRecordedDecision(null);
      const r = String(result.result || "").toUpperCase();
      if (r === "NEW") {
        setMsg(`بررسی تکراری: NEW — می‌توانید پس از تأیید، محصول را به‌صورت Draft ثبت کنید. (${result.reason || ""})`);
      } else if (r === "POSSIBLE_MATCH") {
        setMsg(
          `بررسی تکراری: POSSIBLE_MATCH — تا ثبت تصمیم صریح اپراتور، ایجاد متوقف است. (${result.reason || ""})`,
        );
      } else if (r === "EXISTING") {
        setErr(
          `محصول موجود است (${result.reason || "EXISTING"}). ایجاد رکورد جدید مجاز نیست. شناسه موجود را باز کنید.`,
        );
      } else {
        setErr(`نتیجه بررسی تکراری ناشناخته: ${result.result}`);
      }
    } catch (e) {
      clearDuplicateState();
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setDupBusy(false);
    }
  }

  async function submitOperatorDecision(decision: "NEW" | "EXISTING" | "RENAME") {
    setErr(null);
    if (!dupResult?.check_id) {
      setErr("ابتدا بررسی تکراری را اجرا کنید.");
      return;
    }
    const fp = identityFingerprint(buildIdentitySnapshot(draft));
    if (dupFingerprint !== fp) {
      setErr("مشخصات هویتی پس از بررسی تغییر کرده است. دوباره بررسی تکراری را اجرا کنید.");
      clearDuplicateState();
      return;
    }
    if (decision === "EXISTING") {
      const selected =
        dupResult.candidates?.[0]?.product_id ||
        (dupResult.candidates && dupResult.candidates[0] && dupResult.candidates[0].product_id);
      if (!selected) {
        setErr("برای تصمیم EXISTING شناسه محصول موجود لازم است.");
        return;
      }
    }
    if (decision === "RENAME") {
      setErr(
        "تصمیم RENAME در Backend ثبت می‌شود اما جریان تغییرنام خودکار در این نسخه پیاده نشده است. نام را دستی اصلاح کنید و بررسی را دوباره اجرا کنید.",
      );
    }
    setDupBusy(true);
    try {
      const activeToken = (await onEnsureSession?.()) ?? token;
      if (!activeToken) {
        setErr("نشست فعال برای ثبت تصمیم موجود نیست.");
        return;
      }
      const selectedId =
        decision === "EXISTING" ? dupResult.candidates?.[0]?.product_id ?? null : null;
      await recordDuplicateDecision(
        dupResult.check_id,
        {
          decision,
          selected_product_id: selectedId,
          final_product_name: decision === "RENAME" ? draft.product_name.trim() : null,
          reason: decisionReason.trim() || `operator_${decision.toLowerCase()}`,
        },
        activeToken,
      );
      setRecordedDecision(decision);
      if (decision === "NEW") {
        setMsg("تصمیم NEW ثبت شد. اکنون می‌توانید ثبت Draft را انجام دهید.");
      } else if (decision === "EXISTING") {
        setMsg(
          `تصمیم EXISTING ثبت شد. محصول موجود: ${selectedId || "—"}. ایجاد جدید متوقف است.`,
        );
        if (selectedId) onRegistered?.(selectedId);
      } else {
        setMsg("تصمیم RENAME ثبت شد. نام را اصلاح و بررسی تکراری را دوباره اجرا کنید.");
      }
    } catch (e) {
      setRecordedDecision(null);
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setDupBusy(false);
    }
  }

  async function save() {
    setErr(null);
    setMsg(null);
    if (!draft.product_id.trim() || !draft.brand.trim() || !draft.product_name.trim()) {
      setErr("شناسه، برند و نام محصول الزامی است.");
      return;
    }
    if (!editing && !draft.product_line.trim()) {
      setErr("انتخاب لاین محصول (پوست / مو / زیبایی / ابزار / متفرقه) الزامی است.");
      return;
    }
    setBusy(true);
    try {
      const activeToken = (await onEnsureSession?.()) ?? token;
      if (!activeToken) {
        setErr("برای ثبت یا ویرایش محصول، نشست فعال ایجاد نشد.");
        return;
      }
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
        };
        const lineDelta = productLineForPatch(initialProductLine, draft.product_line);
        if (lineDelta !== undefined) {
          body.product_line = lineDelta;
        }
        const updated = await updateProduct(draft.product_id.trim(), body, activeToken);
        setMsg(`به‌روزرسانی شد: ${updated.product_id}`);
        onRegistered?.(updated.product_id);
      } else {
        const fp = identityFingerprint(buildIdentitySnapshot(draft));
        const gate = canCreateAfterDuplicateCheck({
          check: dupResult,
          checkFingerprint: dupFingerprint,
          currentFingerprint: fp,
          recordedDecision,
        });
        if (!gate.ok) {
          if (gate.reason === "DUPLICATE_CHECK_REQUIRED") {
            setErr("قبل از ثبت، دکمه «بررسی تکراری بودن» را اجرا کنید.");
          } else if (gate.reason === "IDENTITY_CHANGED_RECHECK_REQUIRED") {
            setErr("مشخصات هویتی پس از بررسی تغییر کرده است. دوباره بررسی تکراری را اجرا کنید.");
            clearDuplicateState();
          } else if (gate.reason === "EXISTING_BLOCKED") {
            setErr("نتیجه EXISTING است؛ ایجاد محصول جدید مجاز نیست.");
          } else if (gate.reason === "OPERATOR_DECISION_REQUIRED") {
            setErr("نتیجه POSSIBLE_MATCH است؛ ابتدا تصمیم صریح اپراتور (NEW) را ثبت کنید.");
          } else {
            setErr(`ثبت مجاز نیست: ${gate.reason}`);
          }
          return;
        }
        const body: ProductCreateRequest = {
          product_id: draft.product_id.trim(),
          brand: draft.brand.trim(),
          product_name: draft.product_name.trim(),
          product_line: draft.product_line.trim().toUpperCase(),
          variant: draft.variant || null,
          size_value: draft.size_value,
          size_unit: draft.size_unit || "ml",
          barcode_gtin: draft.barcode_gtin || null,
          market_region: draft.market_region || null,
          packaging_version: draft.packaging_version || null,
          knowledge_use_cases: draft.category || null,
          knowledge_evidence_claim: draft.category || null,
          knowledge_evidence_source_reference: "PRODUCT_INTAKE",
        };
        if (
          String(dupResult?.result || "").toUpperCase() === "POSSIBLE_MATCH" &&
          dupResult?.check_id
        ) {
          body.duplicate_check_id = dupResult.check_id;
        }
        const created = await createProduct(body, activeToken);
        setMsg(`ثبت اولیه انجام شد: ${created.product_id} — وضعیت محصول: Draft`);
        setIntro("");
        clearDuplicateState();
        onRegistered?.(created.product_id);
      }
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  const currentFp = identityFingerprint(buildIdentitySnapshot(draft));
  const createGate = canCreateAfterDuplicateCheck({
    check: dupResult,
    checkFingerprint: dupFingerprint,
    currentFingerprint: currentFp,
    recordedDecision,
  });
  const candidates = dupResult?.candidates ?? [];

  return (
    <section className="pro-panel">
      <h1>{editing ? "ویرایش محصول" : "ورود محصول (تکمیل هوشمند + ثبت اولیه)"}</h1>
      <p className="pro-lead">
        خلاصه را بنویسید → تکمیل خودکار فیلدهای اطلاعاتی → بررسی شما → بررسی تکراری → ثبت اولیه به‌صورت Draft.
        وضعیت هویتی، QA و چرخه انتشار توسط سرور و نقش‌های مربوط کنترل می‌شود.
      </p>
      {err && <div className="pro-alert">{err}</div>}
      {msg && (
        <div className="pro-status-msg" role="status" aria-live="polite">
          <strong>✓ وضعیت</strong>
          <div style={{ marginTop: "0.25rem" }}>{msg}</div>
        </div>
      )}

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
            <input
              className="pro-input"
              value={draft.product_id}
              onChange={(e) => setField("product_id", e.target.value)}
              disabled={editing}
            />
          </div>
          <div>
            <label className="pro-label">برند</label>
            <input className="pro-input" value={draft.brand} onChange={(e) => setField("brand", e.target.value)} />
          </div>
          <div style={{ gridColumn: "1 / -1" }}>
            <label className="pro-label">نام محصول</label>
            <input
              className="pro-input"
              value={draft.product_name}
              onChange={(e) => setField("product_name", e.target.value)}
            />
          </div>
          <div style={{ gridColumn: "1 / -1" }}>
            <label className="pro-label" htmlFor="product-line-select">
              لاین محصول (اجباری) *
            </label>
            <select
              id="product-line-select"
              className="pro-input"
              value={draft.product_line}
              onChange={(e) => setField("product_line", e.target.value)}
              required={!editing}
            >
              <option value="">— انتخاب لاین —</option>
              {PRODUCT_LINE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <p className="pro-lead" style={{ marginTop: "0.25rem", fontSize: "0.85rem" }}>
              انتخاب صریح اپراتور؛ از متن، برند، دسته یا پیشنهاد هوشمند استخراج نمی‌شود.
              در ویرایش، فقط در صورت تغییر واقعی لاین به سرور ارسال می‌شود.
            </p>
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
            <input
              className="pro-input"
              type="number"
              value={draft.size_value}
              onChange={(e) => setField("size_value", Number(e.target.value) || 0)}
            />
          </div>
          <div>
            <label className="pro-label">واحد</label>
            <input
              className="pro-input"
              value={draft.size_unit}
              onChange={(e) => setField("size_unit", e.target.value)}
            />
          </div>
          <div>
            <label className="pro-label">دسته</label>
            <input
              className="pro-input"
              value={draft.category}
              onChange={(e) => setField("category", e.target.value)}
            />
          </div>
          <div>
            <label className="pro-label">بارکد / GTIN</label>
            <input
              className="pro-input"
              value={draft.barcode_gtin}
              onChange={(e) => setField("barcode_gtin", e.target.value)}
              placeholder="اختیاری"
            />
          </div>
          <div>
            <label className="pro-label">منطقه بازار</label>
            <input
              className="pro-input"
              value={draft.market_region}
              onChange={(e) => setField("market_region", e.target.value)}
            />
          </div>
          <div>
            <label className="pro-label">identity_status (سروری)</label>
            <input className="pro-input" value={draft.identity_status} readOnly />
          </div>
          <div>
            <label className="pro-label">status (سروری)</label>
            <input className="pro-input" value={draft.status} readOnly />
          </div>
          <div>
            <label className="pro-label">qa_verdict (سروری)</label>
            <input className="pro-input" value={draft.qa_verdict} readOnly />
          </div>
        </div>
      </fieldset>

      {!editing && (
        <fieldset className="pro-fieldset" style={{ marginTop: "1rem" }}>
          <legend>۳) بررسی تکراری (DuplicateCheck)</legend>
          <p className="pro-lead" style={{ fontSize: "0.9rem" }}>
            قبل از ثبت Draft، مشخصات هویتی باید از مسیر رسمی Backend بررسی شوند. تغییر هر فیلد هویتی، نتیجه قبلی را بی‌اعتبار می‌کند.
          </p>
          <div className="pro-actions">
            <button
              type="button"
              className="pro-btn-secondary"
              disabled={dupBusy || busy}
              onClick={() => void runDuplicateCheck()}
            >
              {dupBusy ? "در حال بررسی…" : "بررسی تکراری بودن"}
            </button>
          </div>
          {dupResult && (
            <div style={{ marginTop: "0.75rem" }}>
              <div>
                <strong>نتیجه:</strong> {String(dupResult.result)}{" "}
                <span style={{ opacity: 0.8 }}>({dupResult.reason || "—"})</span>
              </div>
              <div style={{ fontSize: "0.85rem", marginTop: "0.25rem" }}>
                check_id: <code>{dupResult.check_id}</code>
                {dupFingerprint !== currentFp && (
                  <span style={{ color: "#b45309", marginRight: "0.5rem" }}>
                    — مشخصات تغییر کرده؛ بررسی منقضی است
                  </span>
                )}
              </div>
              {candidates.length > 0 && (
                <ul style={{ marginTop: "0.5rem" }}>
                  {candidates.map((c) => (
                    <li key={c.product_id}>
                      <strong>{c.product_id}</strong> — {c.brand} / {c.product_name}
                      {c.size_value != null ? ` · ${c.size_value}${c.size_unit || ""}` : ""}
                      {c.variant ? ` · ${c.variant}` : ""}
                      {c.conflicting_fields && c.conflicting_fields.length > 0
                        ? ` · تعارض: ${c.conflicting_fields.join(", ")}`
                        : ""}
                      {" "}
                      <button
                        type="button"
                        className="pro-btn-secondary"
                        style={{ marginInlineStart: "0.35rem" }}
                        onClick={() => onRegistered?.(c.product_id)}
                      >
                        باز کردن موجود
                      </button>
                    </li>
                  ))}
                </ul>
              )}
              {String(dupResult.result).toUpperCase() === "POSSIBLE_MATCH" &&
                dupFingerprint === currentFp && (
                  <div style={{ marginTop: "0.75rem" }}>
                    <label className="pro-label" htmlFor="dup-decision-reason">
                      دلیل تصمیم اپراتور
                    </label>
                    <input
                      id="dup-decision-reason"
                      className="pro-input"
                      value={decisionReason}
                      onChange={(e) => setDecisionReason(e.target.value)}
                      placeholder="مثلاً: SKU متمایز با همان نام تجاری"
                    />
                    <div className="pro-actions" style={{ marginTop: "0.5rem" }}>
                      <button
                        type="button"
                        className="pro-btn-primary"
                        disabled={dupBusy}
                        onClick={() => void submitOperatorDecision("NEW")}
                      >
                        تصمیم: NEW (ادامه ایجاد)
                      </button>
                      <button
                        type="button"
                        className="pro-btn-secondary"
                        disabled={dupBusy || candidates.length === 0}
                        onClick={() => void submitOperatorDecision("EXISTING")}
                      >
                        تصمیم: EXISTING (توقف ایجاد)
                      </button>
                    </div>
                    {recordedDecision && (
                      <p className="pro-lead" style={{ marginTop: "0.35rem" }}>
                        تصمیم ثبت‌شده: <strong>{recordedDecision}</strong>
                      </p>
                    )}
                  </div>
                )}
            </div>
          )}
        </fieldset>
      )}

      <div className="pro-actions" style={{ marginTop: "1rem" }}>
        <button
          type="button"
          className="pro-btn-primary"
          disabled={busy || dupBusy || (!editing && !createGate.ok)}
          onClick={() => void save()}
        >
          {busy
            ? "در حال ثبت…"
            : editing
              ? "تأیید و به‌روزرسانی"
              : createGate.ok
                ? "ثبت محصول به‌صورت Draft"
                : "ثبت (پس از بررسی تکراری معتبر)"}
        </button>
        {editing && (
          <button
            type="button"
            className="pro-btn-secondary"
            onClick={() => {
              onCancelEdit?.();
              setDraft(EMPTY);
              setInitialProductLine("");
              clearDuplicateState();
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
