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

/** Product Line V1 — operator classification only; never inferred from text/category/AI. */
const PRODUCT_LINE_OPTIONS = [
  { value: "SKIN", label: "پوست (SKIN)" },
  { value: "HAIR", label: "مو (HAIR)" },
  { value: "BEAUTY", label: "زیبایی (BEAUTY)" },
  { value: "TOOLS", label: "ابزار (TOOLS)" },
  { value: "OTHER", label: "متفرقه (OTHER)" },
] as const;

const SKIN_TEMPLATES = [
  ["HYDRATING_MOISTURIZER", "آبرسان / مرطوب‌کننده", ["بافت", "حس پوستی اعلام‌شده", "روز / شب / هر دو", "ادعای آبرسانی یا حفظ رطوبت (متن + منبع)"]],
  ["SUNSCREEN", "ضدآفتاب", ["SPF", "PA / ادعای UVA", "نوع فیلتر", "مقاومت در برابر آب", "رنگی / بی‌رنگ", "صورت / بدن"]],
  ["BRIGHTENING_SPOT", "روشن‌کننده / ضدلک", ["هدف اعلام‌شده", "مواد فعال اعلام‌شده", "بازه زمانی ادعای سازنده", "اعداد ادعای سازنده (فقط با منبع)"]],
  ["MICELLAR", "میسلار واتر", ["پاک‌کنندگی آرایش", "نیاز به آبکشی", "مناسب اطراف چشم طبق برچسب"]],
  ["TONER", "تونر", ["نقش اعلام‌شده", "الکل طبق فرمول اعلام‌شده"]],
  ["CLEANSING_GEL", "ژل شستشو", ["آبکشی‌شونده", "تمرکز اعلام‌شده", "تناوب مصرف طبق برچسب"]],
  ["ANTI_ACNE", "ضدجوش", ["تمرکز اعلام‌شده", "مواد فعال اعلام‌شده", "ماندگار / آبکشی"]],
  ["EXFOLIANT", "لایه‌بردار", ["نوع لایه‌بردار", "اسیدها یا ذرات اعلام‌شده", "تناوب مصرف", "هشدار تحریک از برچسب"]],
  ["OTHER_SKIN", "سایر (پوست)", ["چرا در قالب‌های بالا جا نگرفت", "یادداشت ساخت‌یافته اپراتور"]],
] as const;

/** Seven approved existing dossiers only; template is tied to Product Master identity. */
const SKIN_SEVEN_PRODUCT_TEMPLATES: Record<string, string> = {
  "HBI-PROD-F66ED6FEA6144D71": "OTHER_SKIN",
  "HBI-PROD-37EB7C42C6BE413B": "CLEANSING_GEL",
  "HBI-PROD-9F7C2CE624D14E5A": "CLEANSING_GEL",
  "HBI-PROD-AB647F422E174BD8": "SUNSCREEN",
  "HBI-PROD-03781074C3BF448A": "SUNSCREEN",
  "HBI-PROD-85AD86B15C734EF2": "BRIGHTENING_SPOT",
  "HBI-PROD-7AD37ECCEA874E12": "OTHER_SKIN",
};

const SKIN_PRODUCT_SPECIFIC_BOXES: Record<string, readonly string[]> = {
  "HBI-PROD-F66ED6FEA6144D71": ["پپتیدها و ترکیبات کلیدی طبق منبع", "ادعاهای اختصاصی بوستر طبق منبع"],
  "HBI-PROD-37EB7C42C6BE413B": ["سالیسیلیک اسید و غلظتِ اعلام‌شده در همین نسخه", "بازار و نسخهٔ منبع Neutrogena"],
  "HBI-PROD-9F7C2CE624D14E5A": ["مشتق ویتامین C طبق INCI همین نسخه", "غلظت مادهٔ شاخص، فقط اگر منبع اعلام کرده باشد"],
  "HBI-PROD-AB647F422E174BD8": ["درجه‌بندی PA/UVA همین نسخه", "فیلترهای UV همین نسخه/بازار", "مقاومت در برابر آب، فقط اگر برچسب تصریح کند"],
  "HBI-PROD-03781074C3BF448A": ["فیلترهای UV همین نسخه/بازار", "ادعای ضدلک و نقطهٔ پایانیِ اعلام‌شده"],
  "HBI-PROD-85AD86B15C734EF2": ["نتیجهٔ آزمون بالینی و مدت آن", "نتیجهٔ آزمون مصرف‌کننده، حجم نمونه و مدت آن"],
  "HBI-PROD-7AD37ECCEA874E12": ["درصد آزلائیک اسیدِ اعلام‌شده در منبع", "ترکیبات پشتیبان و ادعای تسکین طبق منبع"],
};

/** Map only semantically matching template boxes to existing Evidence fields. */
function skinTemplateEvidenceField(template: string, label: string): string | undefined {
  if (template === "BRIGHTENING_SPOT" && label === "هدف اعلام‌شده") return "known_use_cases";
  if (template === "BRIGHTENING_SPOT" && label === "مواد فعال اعلام‌شده") return "ingredients";
  if (template === "CLEANSING_GEL" && label === "تمرکز اعلام‌شده") return "known_use_cases";
  if (template === "CLEANSING_GEL" && label === "تناوب مصرف طبق برچسب") return "usage_instructions";
  if (template === "SUNSCREEN" && label === "صورت / بدن") return "known_use_cases";
  return undefined;
}

/** Only these V1 boxes have a semantically matching source-bound Evidence field. */
const SKIN_OK_EVIDENCE_FIELDS = [
  { key: "skin_goals", label: "اهداف پوستی اعلام‌شده", field: "skin_goals" },
  { key: "warnings", label: "هشدارها و محدودیت‌ها", field: "contraindications" },
  { key: "usage", label: "روش مصرف", field: "usage_instructions" },
  { key: "ingredients", label: "ترکیبات کلیدی اعلام‌شده", field: "ingredients" },
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
  else if (/skin\s*1004/i.test(text)) d.brand = "SKIN1004";
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

  // product_id is allocated by the backend after DuplicateCheck; never invent one here.
  d.product_id = "";

  d.identity_status = "NEEDS_REVIEW";
  d.qa_verdict = "PENDING";
  d.status = "DRAFT";
  d.market_region = "";
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
  const [intro, setIntro] = useState("");
  const [draft, setDraft] = useState<Draft>(EMPTY);
  const [skinTemplate, setSkinTemplate] = useState<string>("");
  const [skinBoxValues, setSkinBoxValues] = useState<Record<string, string>>({});
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
  const [researchProductId, setResearchProductId] = useState<string | null>(null);
  const [researchRows, setResearchRows] = useState<EvidenceDTO[]>([]);
  const [researchClaim, setResearchClaim] = useState("");
  const [researchSourceType, setResearchSourceType] = useState("MANUFACTURER");
  const [researchSourceReference, setResearchSourceReference] = useState("");
  const [researchClaimType, setResearchClaimType] = useState("MANUFACTURER_CLAIM");
  const [researchField, setResearchField] = useState("claimed_benefits");
  const [researchMarketRegion, setResearchMarketRegion] = useState("");
  const [researchNotes, setResearchNotes] = useState("");
  const [researchReviewReason, setResearchReviewReason] = useState("");
  const [researchBusy, setResearchBusy] = useState(false);
  const editing = Boolean(editProduct?.product_id);

  async function loadResearch(productId: string) {
    try {
      const activeToken = (await onEnsureSession?.()) ?? token;
      if (!activeToken) return;
      setResearchRows(await getProductEvidence(productId, activeToken));
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    }
  }

  // The persisted edit target is canonical; draft state may still be initializing on first render.
  const selectedSkinTemplate = SKIN_SEVEN_PRODUCT_TEMPLATES[editProduct?.product_id || draft.product_id] || "";
  const isApprovedSevenProduct = Boolean(selectedSkinTemplate);
  const canSaveSkinEvidenceDraft =
    editing &&
    isApprovedSevenProduct &&
    Boolean(draft.product_id.trim()) &&
    draft.product_line === "SKIN" &&
    researchProductId === draft.product_id;

  async function saveSkinEvidenceDraft() {
    setErr(null);
    setMsg(null);
    if (!canSaveSkinEvidenceDraft || !researchProductId) {
      setErr("ثبت باکس‌های ساخت‌یافته فقط برای محصول پوستِ موجود و انتخاب‌شده مجاز است.");
      return;
    }
    if (!researchSourceType.trim() || !researchSourceReference.trim()) {
      setErr("نوع منبع و نشانی/مرجع دقیق منبع برای ثبت باکس‌های پژوهش الزامی است.");
      return;
    }

    const sharedFields = SKIN_OK_EVIDENCE_FIELDS.map((item) => ({
      field: item.field,
      label: item.label,
      value: (skinBoxValues[item.key] || "").trim(),
      claimType: researchClaimType || "UNKNOWN",
      boxKind: "shared",
    }));
    const templateFields = (SKIN_TEMPLATES.find(([value]) => value === skinTemplate)?.[2] ?? [])
      .filter((label) => !(skinTemplate === "HYDRATING_MOISTURIZER" && label === "ادعای آبرسانی یا حفظ رطوبت (متن + منبع)"))
      .map((label) => {
        const field = skinTemplateEvidenceField(skinTemplate, label);
        return {
          field,
          label,
          value: (skinBoxValues[`template:${skinTemplate}:${label}`] || "").trim(),
          claimType: researchClaimType || "UNKNOWN",
          boxKind: "template",
        };
      });
    const productFields = (SKIN_PRODUCT_SPECIFIC_BOXES[researchProductId || ""] ?? []).map((label) => {
      const structured = label.includes("ترکیبات") || label.includes("فیلترهای UV") || label.includes("پپتیدها") || label.includes("مشتق ویتامین C") || label.includes("آزلائیک اسید") || label.includes("سالیسیلیک اسید");
      return {
        field: structured ? "ingredients" : undefined,
        label,
        value: (skinBoxValues[`product:${researchProductId}:${label}`] || "").trim(),
        claimType: researchClaimType || "UNKNOWN",
        boxKind: "product-specific",
      };
    });
    const fields = [
      ...sharedFields,
      ...(skinTemplate === "HYDRATING_MOISTURIZER"
        ? [{
            field: "claimed_benefits",
            label: "ادعای آبرسانی یا حفظ رطوبت",
            value: (skinBoxValues.claimed_benefits || "").trim(),
            claimType: researchClaimType || "UNKNOWN",
            boxKind: "template",
          }]
        : []),
      ...templateFields,
      ...productFields,
      {
        field: undefined,
        label: "سایر ویژگی‌ها",
        value: (skinBoxValues.other_features || "").trim(),
        claimType: "UNKNOWN",
        boxKind: "other",
      },
    ].filter((item) => item.value.length > 0);

    if (fields.length === 0) {
      setErr("حداقل یک باکس مجاز را با متن مستند تکمیل کنید.");
      return;
    }

    setResearchBusy(true);
    try {
      const activeToken = (await onEnsureSession?.()) ?? token;
      if (!activeToken) throw new Error("نشست فعال برای ثبت پژوهش موجود نیست.");
      await createResearchDraft(
        researchProductId,
        fields.map((item) => ({
          claim: item.field ? item.value : `${item.label}: ${item.value}`,
          field: item.field,
          source_type: researchSourceType.trim(),
          source_reference: researchSourceReference.trim(),
          claim_type: item.claimType,
          market_region: researchMarketRegion.trim() || undefined,
          notes: `Skin intake box kind=${item.boxKind}; label=${item.label}; template=${skinTemplate || "not-selected"}${researchNotes.trim() ? `; ${researchNotes.trim()}` : ""}`,
        })),
        activeToken,
      );
      setSkinBoxValues({});
      setResearchNotes("");
      setMsg("پیش‌نویس‌های باکس‌های مجاز برای محصول انتخاب‌شده ثبت شدند؛ همه با QA=PENDING و evidence_status=UNKNOWN باقی می‌مانند.");
      await loadResearch(researchProductId);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setResearchBusy(false);
    }
  }

  async function saveResearchDraft() {
    setErr(null);
    if (!researchProductId) return;
    if (!researchClaim.trim() || !researchSourceType.trim() || !researchSourceReference.trim()) {
      setErr("برای ثبت شاهد، ادعا، نوع منبع و نشانی/مرجع منبع الزامی است.");
      return;
    }
    setResearchBusy(true);
    try {
      const activeToken = (await onEnsureSession?.()) ?? token;
      if (!activeToken) throw new Error("نشست فعال برای ثبت پژوهش موجود نیست.");
      await createResearchDraft(researchProductId, [{
        claim: researchClaim.trim(),
        source_type: researchSourceType.trim(),
        source_reference: researchSourceReference.trim(),
        claim_type: researchClaimType,
        field: researchField.trim() || undefined,
        market_region: researchMarketRegion.trim() || undefined,
        notes: researchNotes.trim() || undefined,
      }], activeToken);
      setResearchClaim("");
      setResearchNotes("");
      setMsg("پیش‌نویس پژوهش ثبت شد؛ وضعیت شاهد PENDING/UNKNOWN است و تا بررسی صریح، تأییدشده محسوب نمی‌شود.");
      await loadResearch(researchProductId);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setResearchBusy(false);
    }
  }

  async function reviewEvidence(evidenceId: string) {
    setErr(null);
    if (!researchReviewReason.trim()) {
      setErr("برای ثبت نتیجه بررسی شاهد، دلیل بررسی الزامی است.");
      return;
    }
    setResearchBusy(true);
    try {
      const activeToken = (await onEnsureSession?.()) ?? token;
      if (!activeToken) throw new Error("نشست فعال برای بررسی شاهد موجود نیست.");
      await verifyEvidence(evidenceId, "VERIFIED", activeToken, researchReviewReason.trim());
      setResearchReviewReason("");
      setMsg("شاهد بررسی و به‌صورت VERIFIED ثبت شد.");
      if (researchProductId) await loadResearch(researchProductId);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setResearchBusy(false);
    }
  }

  useEffect(() => {
    setSkinBoxValues({});
    if (editProduct?.product_id) {
      const next = fromProduct(editProduct);
      const approvedTemplate = SKIN_SEVEN_PRODUCT_TEMPLATES[editProduct.product_id] || "";
      setSkinTemplate(approvedTemplate);
      setDraft(next);
      setInitialProductLine(normalizeProductLine(next.product_line));
      setIntro("");
      setMsg(`ویرایش محصول: ${editProduct.product_id}`);
      setErr(null);
      setDupResult(null);
      setDupFingerprint(null);
      setRecordedDecision(null);
      setResearchProductId(editProduct.product_id);
      void loadResearch(editProduct.product_id);
    } else {
      setSkinTemplate("");
      setResearchProductId(null);
      setResearchRows([]);
    }
  }, [editProduct]);

  function clearDuplicateState() {
    setDupResult(null);
    setDupFingerprint(null);
    setRecordedDecision(null);
  }

  function setField<K extends keyof Draft>(key: K, value: Draft[K]) {
    // Identity change invalidates prior DuplicateCheck / operator decision.
    // Clear related state outside the setDraft updater (React updater purity).
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
    setDraft((prev) => ({ ...prev, [key]: value }));
    if (identityKeys.includes(key)) {
      clearDuplicateState();
    }
  }

  function loadResearchedP4Draft() {
    const next: Draft = {
      ...EMPTY,
      brand: "SKIN1004",
      product_name: "Madagascar Centella Hyalu-Cica Water-Fit Sun Serum",
      product_line: "SKIN",
      variant: "",
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
    setIntro("SKIN1004 Madagascar Centella Hyalu-Cica Water-Fit Sun Serum 50ml");
    setDraft(next);
    clearDuplicateState();
    setErr(null);
    setMsg("پیش‌نویس پژوهشی P4 بارگذاری شد. بازار، نسخه بسته‌بندی، GTIN، variant و SPF از روی نام حدس زده نشده‌اند. هویت محصول همچنان نیازمند بررسی است؛ این کار هنوز هیچ رکوردی ایجاد نکرده است.");
  }

  function runComplete() {
    if (!intro.trim()) {
      setErr("ابتدا خلاصه معرفی محصول را بنویسید.");
      return;
    }
    const completed = completeFromIntro(intro);
    if (editing) completed.product_id = draft.product_id;
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
    if (!draft.brand.trim() || !draft.product_name.trim()) {
      setErr("برای بررسی تکراری، برند و نام محصول الزامی است؛ شناسه را backend تولید می‌کند.");
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
    if (!editing && draft.product_id.trim() === "TEST-P1C-001") {
      setErr("TEST-P1C-001 یک شناسهٔ آزمایشی ازپیش‌موجود است؛ ایجاد محصول با این شناسه از مسیر Intake ممنوع است.");
      return;
    }
    setMsg(null);
    if ((editing && !draft.product_id.trim()) || !draft.brand.trim() || !draft.product_name.trim()) {
      setErr("برای ثبت، برند و نام محصول الزامی است؛ شناسهٔ محصول را backend تولید می‌کند.");
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
          brand: draft.brand.trim(),
          product_name: draft.product_name.trim(),
          product_line: draft.product_line.trim().toUpperCase(),
          variant: draft.variant || null,
          size_value: draft.size_value,
          size_unit: draft.size_unit || "ml",
          barcode_gtin: draft.barcode_gtin || null,
          market_region: draft.market_region || null,
          packaging_version: draft.packaging_version || null,
        };
        // New intake never submits a client-invented product_id. Backend allocates after DuplicateCheck.
        if (
          String(dupResult?.result || "").toUpperCase() === "POSSIBLE_MATCH" &&
          dupResult?.check_id
        ) {
          body.duplicate_check_id = dupResult.check_id;
        }
        const created = await createProduct(body, activeToken);
        setMsg(`ثبت اولیه انجام شد: ${created.product_id} — وضعیت محصول: Draft`);
        setIntro("");
        setResearchProductId(created.product_id);
        clearDuplicateState();
        await loadResearch(created.product_id);
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
            <button type="button" className="pro-btn-secondary" onClick={loadResearchedP4Draft}>
              بارگذاری پیش‌نویس پژوهشی P4 · SKIN1004
            </button>
          </div>
          <p className="pro-lead" style={{ marginTop: "0.5rem", fontSize: "0.85rem" }}>
            شروع سریع P4 فقط فیلدها را پیش‌پر می‌کند. بازار کره‌ای/بین‌المللی و آمریکا یکسان فرض نمی‌شوند؛
            پیش از ثبت، مشخصات را بررسی و DuplicateCheck را اجرا کنید. ایجاد رکورد همچنان اقدام جداگانه اپراتور است.
          </p>
        </div>
      )}

      <fieldset className="pro-fieldset" style={{ marginTop: "1rem" }}>
        <legend>۲) فیلدهای پروتکل (قابل ویرایش قبل از ذخیره)</legend>
        <div className="pro-grid-2">
          {!editing && (
            <div style={{ gridColumn: "1 / -1" }}>
              <p className="pro-lead">شناسهٔ محصول پس از عبور از DuplicateCheck به‌صورت یکتا توسط backend تولید می‌شود؛ شناسهٔ دستی یا حدس هوش مصنوعی وارد نمی‌شود.</p>
            </div>
          )}
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
              onChange={(e) => { setField("product_line", e.target.value); if (e.target.value !== "SKIN") setSkinTemplate(""); }}
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

      {draft.product_line === "SKIN" && (
        <fieldset className="pro-fieldset" style={{ marginTop: "1rem" }}>
          <legend>۳) قالب ثابت محصول پوست (V1)</legend>
          <p className="pro-lead">
            این مسیر فقط برای هفت محصول موجودِ ماتریس فعال است. هر باکسِ پرشده با منبع به‌صورت پیش‌نویس پژوهشی ثبت می‌شود؛
            فقط باکس‌هایی که نگاشت معنایی معتبر دارند field می‌گیرند. «سایر ویژگی‌ها» با field خالی و claim_type=UNKNOWN ذخیره می‌شود.
            این مسیر محصول نمی‌سازد و QA را تأیید نمی‌کند.
          </p>
          <label className="pro-label" htmlFor="skin-template">قالب محصول پوست</label>
          <select id="skin-template" className="pro-input" value={isApprovedSevenProduct ? selectedSkinTemplate : skinTemplate} onChange={(e) => setSkinTemplate(e.target.value)} disabled={isApprovedSevenProduct}>
            <option value="">— انتخاب قالب —</option>
            {SKIN_TEMPLATES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
          {isApprovedSevenProduct && (
            <p className="pro-lead">قالب این محصول از ماتریس مصوب هفت محصول تعیین شده است؛ برای جلوگیری از ثبت در قالب اشتباه، انتخاب قالب قفل است.</p>
          )}
          {!isApprovedSevenProduct && (
            <p className="pro-lead">ثبت باکس‌های این مسیر فعلاً فقط برای هفت شناسهٔ مصوب فعال است.</p>
          )}

          <div className="pro-grid-2" style={{ marginTop: "0.75rem" }}>
            <div>
              <label className="pro-label">نوع منبع *</label>
              <select className="pro-input" value={researchSourceType} onChange={(e) => setResearchSourceType(e.target.value)} disabled={!canSaveSkinEvidenceDraft}>
                <option value="MANUFACTURER">تولیدکننده</option>
                <option value="REGULATORY">مرجع مقرراتی</option>
                <option value="PEER_REVIEWED">مقاله داوری‌شده</option>
                <option value="CLINICAL_TRIAL">کارآزمایی بالینی</option>
                <option value="OTHER">سایر</option>
                <option value="OPERATOR_DECLARATION">اظهار اپراتور</option>
              </select>
            </div>
            <div>
              <label className="pro-label">نوع ادعا</label>
              <select className="pro-input" value={researchClaimType} onChange={(e) => setResearchClaimType(e.target.value)} disabled={!canSaveSkinEvidenceDraft}>
                <option value="UNKNOWN">نامشخص</option>
                <option value="MANUFACTURER_CLAIM">ادعای تولیدکننده</option>
                <option value="EVIDENCE">شاهد</option>
                <option value="INFERENCE">استنباط</option>
                <option value="FACT">واقعیت (فقط منبع مستقل مجاز)</option>
                <option value="CONFLICT">متعارض</option>
              </select>
            </div>
            <div style={{ gridColumn: "1 / -1" }}>
              <label className="pro-label">نشانی یا مرجع دقیق منبع *</label>
              <input className="pro-input" value={researchSourceReference} onChange={(e) => setResearchSourceReference(e.target.value)} placeholder="URL، شناسه مقاله یا مرجع دقیق" disabled={!canSaveSkinEvidenceDraft} />
            </div>
            <div>
              <label className="pro-label">منطقه بازار (اختیاری، فقط با شاهد)</label>
              <input className="pro-input" value={researchMarketRegion} onChange={(e) => setResearchMarketRegion(e.target.value)} placeholder="خالی بماند اگر معلوم نیست" disabled={!canSaveSkinEvidenceDraft} />
            </div>
            <div style={{ gridColumn: "1 / -1" }}>
              <label className="pro-label">یادداشت / محدودیت‌ها</label>
              <textarea className="pro-input" rows={2} value={researchNotes} onChange={(e) => setResearchNotes(e.target.value)} placeholder="اختیاری" disabled={!canSaveSkinEvidenceDraft} />
            </div>
          </div>

          <h3>باکس‌های مشترک مجاز (OK)</h3>
          <div className="pro-grid-2">
            {SKIN_OK_EVIDENCE_FIELDS.map((item) => (
              <div key={item.key}>
                <label className="pro-label">{item.label} *</label>
                <textarea
                  className="pro-input"
                  rows={2}
                  value={skinBoxValues[item.key] || ""}
                  onChange={(e) => setSkinBoxValues((prev) => ({ ...prev, [item.key]: e.target.value }))}
                  placeholder={canSaveSkinEvidenceDraft ? "متن ادعا/ویژگی مطابق منبع" : "ابتدا یک محصول پوستِ موجود را باز کنید"}
                  disabled={!canSaveSkinEvidenceDraft}
                />
              </div>
            ))}
            <div>
              <label className="pro-label">سایر ویژگی‌ها (برای هر محصول؛ منبع الزامی)</label>
              <textarea
                className="pro-input"
                rows={2}
                value={skinBoxValues.other_features || ""}
                onChange={(e) => setSkinBoxValues((prev) => ({ ...prev, other_features: e.target.value }))}
                placeholder={canSaveSkinEvidenceDraft ? "ویژگی مستندشده‌ای که باکس اختصاصی ندارد؛ متن آزادِ بررسی‌نشده" : "ابتدا یکی از هفت محصول مصوب را باز کنید"}
                disabled={!canSaveSkinEvidenceDraft}
              />
            </div>
          </div>

          {skinTemplate && (
            <>
              <h3>باکس‌های اختصاصی گروه: {SKIN_TEMPLATES.find(([value]) => value === skinTemplate)?.[1]}</h3>
              <div className="pro-grid-2">
                {(SKIN_TEMPLATES.find(([value]) => value === skinTemplate)?.[2] ?? []).map((label) => {
                  const moisturizerBenefit = skinTemplate === "HYDRATING_MOISTURIZER" && label === "ادعای آبرسانی یا حفظ رطوبت (متن + منبع)";
                  const boxKey = moisturizerBenefit ? "claimed_benefits" : `template:${skinTemplate}:${label}`;
                  const mappedField = moisturizerBenefit ? "claimed_benefits" : skinTemplateEvidenceField(skinTemplate, label);
                  return (
                    <div key={label}>
                      <label className="pro-label">{label}{mappedField ? " *" : " (ادعای منبع‌دار؛ بدون نگاشت ساختاریافته)"}</label>
                      <textarea
                        className="pro-input"
                        rows={2}
                        value={skinBoxValues[boxKey] || ""}
                        onChange={(e) => setSkinBoxValues((prev) => ({ ...prev, [boxKey]: e.target.value }))}
                        placeholder={canSaveSkinEvidenceDraft ? (mappedField ? "متن مطابق منبع؛ وضعیت پیش‌نویس" : "متن مطابق منبع؛ به‌صورت ادعای UNKNOWN ذخیره می‌شود") : "ابتدا یکی از هفت محصول مصوب را باز کنید"}
                        disabled={!canSaveSkinEvidenceDraft}
                      />
                    </div>
                  );
                })}
              </div>
              {(SKIN_PRODUCT_SPECIFIC_BOXES[researchProductId || ""] ?? []).length > 0 && (
                <>
                  <h3>باکس‌های اختصاصی همین محصول</h3>
                  <div className="pro-grid-2">
                    {(SKIN_PRODUCT_SPECIFIC_BOXES[researchProductId || ""] ?? []).map((label) => {
                      const boxKey = `product:${researchProductId}:${label}`;
                      const structured = label.includes("ترکیبات") || label.includes("فیلترهای UV") || label.includes("پپتیدها") || label.includes("مشتق ویتامین C") || label.includes("آزلائیک اسید") || label.includes("سالیسیلیک اسید");
                      return (
                        <div key={boxKey}>
                          <label className="pro-label">{label}{structured ? " *" : " (ادعای منبع‌دار؛ بدون نگاشت ساختاریافته)"}</label>
                          <textarea
                            className="pro-input"
                            rows={2}
                            value={skinBoxValues[boxKey] || ""}
                            onChange={(e) => setSkinBoxValues((prev) => ({ ...prev, [boxKey]: e.target.value }))}
                            placeholder={canSaveSkinEvidenceDraft ? "فقط مطابق منبع همین محصول/نسخه؛ وضعیت پیش‌نویس" : "ابتدا یکی از هفت محصول مصوب را باز کنید"}
                            disabled={!canSaveSkinEvidenceDraft}
                          />
                        </div>
                      );
                    })}
                  </div>
                </>
              )}
            </>
          )}

          <div className="pro-actions" style={{ marginTop: "0.75rem" }}>
            <button type="button" className="pro-btn-primary" disabled={!canSaveSkinEvidenceDraft || researchBusy} onClick={() => void saveSkinEvidenceDraft()}>
              {researchBusy ? "در حال ثبت…" : "ثبت باکس‌های مجاز به‌صورت پیش‌نویس"}
            </button>
          </div>
          <p className="pro-lead" role="note">
            هر assertion فقط با claim، نوع منبع و مرجع منبع ارسال می‌شود. وضعیت QA=PENDING و evidence_status=UNKNOWN باقی می‌ماند؛ تأیید یا فعال‌سازی از این مسیر انجام نمی‌شود.
          </p>
          <div style={{ marginTop: "0.75rem" }}>
            <div className="pro-actions">
              <strong>شواهد ذخیره‌شده: {researchRows.length}</strong>
              <button type="button" className="pro-btn-secondary" disabled={researchBusy} onClick={() => researchProductId && void loadResearch(researchProductId)}>
                بازخوانی شواهد
              </button>
            </div>
            {researchRows.length === 0 ? (
              <p className="pro-lead">هنوز شاهدی برای این محصول بازخوانی نشده است.</p>
            ) : (
              <ul>
                {researchRows.map((item) => (
                  <li key={item.evidence_id} style={{ marginBottom: "0.5rem" }}>
                    <strong>{item.claim || "—"}</strong>
                    <div className="pro-lead" style={{ fontSize: "0.85rem" }}>
                      فیلد: {String(item.field || "—")} · منبع: {item.source_type || "—"} / {item.source_reference || "—"}
                    </div>
                    <div className="pro-lead" style={{ fontSize: "0.85rem" }}>
                      QA: {String(item.qa_status || "PENDING")} · evidence_status: {String(item.evidence_status || "UNKNOWN")} · conflict: {String(item.conflict_status || "NONE")}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </fieldset>
      )}

      {!editing && (
        <fieldset className="pro-fieldset" style={{ marginTop: "1rem" }}>
          <legend>۴) بررسی تکراری (DuplicateCheck)</legend>
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

      {researchProductId && researchProductId !== "TEST-P1C-001" && (
        <fieldset className="pro-fieldset" style={{ marginTop: "1rem" }}>
          <legend>۴) پیش‌نویس پژوهش و بررسی شواهد — {researchProductId}</legend>
          <p className="pro-lead" style={{ fontSize: "0.9rem" }}>
            هر ادعا باید به منبع قابل ردیابی متصل باشد. ثبت پژوهش به‌تنهایی تأیید ایمنی یا صحت ادعا نیست.
          </p>
          <div className="pro-grid-2">
            <div style={{ gridColumn: "1 / -1" }}>
              <label className="pro-label">ادعا / گزاره قابل بررسی *</label>
              <textarea className="pro-input" rows={2} value={researchClaim}
                onChange={(e) => setResearchClaim(e.target.value)}
                placeholder="یک ادعای مشخص؛ بدون تبدیل حدس به واقعیت" />
            </div>
            <div>
              <label className="pro-label">نوع منبع *</label>
              <select className="pro-input" value={researchSourceType}
                onChange={(e) => setResearchSourceType(e.target.value)}>
                <option value="MANUFACTURER">تولیدکننده</option>
                <option value="REGULATORY">مرجع مقرراتی</option>
                <option value="PEER_REVIEWED">مقاله داوری‌شده</option>
                <option value="CLINICAL_TRIAL">کارآزمایی بالینی</option>
                <option value="OTHER">سایر</option>
                <option value="OPERATOR_DECLARATION">اظهار اپراتور</option>
              </select>
            </div>
            <div>
              <label className="pro-label">نوع ادعا</label>
              <select className="pro-input" value={researchClaimType}
                onChange={(e) => setResearchClaimType(e.target.value)}>
                <option value="MANUFACTURER_CLAIM">ادعای تولیدکننده</option>
                <option value="FACT">واقعیت</option>
                <option value="EVIDENCE">شاهد</option>
                <option value="INFERENCE">استنباط</option>
                <option value="UNKNOWN">نامشخص</option>
                <option value="CONFLICT">متعارض</option>
              </select>
            </div>
            <div style={{ gridColumn: "1 / -1" }}>
              <label className="pro-label">نشانی یا مرجع منبع *</label>
              <input className="pro-input" value={researchSourceReference}
                onChange={(e) => setResearchSourceReference(e.target.value)}
                placeholder="URL، شناسه مقاله، شماره سند یا مرجع دقیق" />
            </div>
            <div>
              <label className="pro-label">فیلد دانش محصول</label>
              <select className="pro-input" value={researchField}
                onChange={(e) => setResearchField(e.target.value)}>
                <option value="claimed_benefits">مزایای ادعاشده</option>
                <option value="known_use_cases">موارد مصرف</option>
                <option value="ingredients">ترکیبات</option>
                <option value="contraindications">موارد منع مصرف / احتیاط</option>
                <option value="usage_instructions">دستور مصرف</option>
                <option value="manufacturer_claims">ادعاهای سازنده</option>
              </select>
            </div>
            <div>
              <label className="pro-label">منطقه بازار</label>
              <input className="pro-input" value={researchMarketRegion}
                onChange={(e) => setResearchMarketRegion(e.target.value)} />
            </div>
            <div style={{ gridColumn: "1 / -1" }}>
              <label className="pro-label">یادداشت / محدودیت‌ها</label>
              <textarea className="pro-input" rows={2} value={researchNotes}
                onChange={(e) => setResearchNotes(e.target.value)} />
            </div>
          </div>
          <div className="pro-actions" style={{ marginTop: "0.5rem" }}>
            <button type="button" className="pro-btn-primary" disabled={researchBusy}
              onClick={() => void saveResearchDraft()}>
              {researchBusy ? "در حال ثبت/بررسی…" : "ثبت پیش‌نویس پژوهش"}
            </button>
            <button type="button" className="pro-btn-secondary" disabled={researchBusy}
              onClick={() => void loadResearch(researchProductId)}>
              بازخوانی شواهد
            </button>
          </div>
          <p className="pro-lead" role="note">
            نقش‌های مجاز عملیاتی/QA می‌توانند نتیجه بررسی را ثبت کنند؛ هویت نقش و دلیل بررسی در سابقه ممیزی ذخیره می‌شود. وضعیت VERIFIED یعنی نتیجه بررسی ثبت شده است و به‌تنهایی تضمین صحت علمی یا ایمنی ادعا نیست.
          </p>
          <div style={{ marginTop: "0.75rem" }}>
            <label className="pro-label">دلیل بررسی شاهد (برای ثبت VERIFIED الزامی است)</label>
            <input className="pro-input" value={researchReviewReason}
              onChange={(e) => setResearchReviewReason(e.target.value)}
              placeholder="مثلاً تطبیق مرجع با سند اصلی و بررسی دامنه ادعا" />
          </div>
          <div style={{ marginTop: "0.75rem" }}>
            <strong>شواهد ثبت‌شده ({researchRows.length})</strong>
            {researchRows.length === 0 ? <p className="pro-lead">هنوز شاهدی برای این محصول ثبت نشده است.</p> : (
              <ul>
                {researchRows.map((e) => (
                  <li key={e.evidence_id} style={{ marginBottom: "0.65rem" }}>
                    <div><strong>{e.claim || "—"}</strong></div>
                    <div className="pro-lead" style={{ fontSize: "0.85rem" }}>
                      {e.source_type || "—"} · {e.source_reference || "—"} · فیلد: {String(e.field || "—")}
                    </div>
                    <div className="pro-lead" style={{ fontSize: "0.85rem" }}>
                      نوع ادعا: {String(e.claim_type || "UNKNOWN")} · وضعیت شاهد: {String(e.evidence_status || "UNKNOWN")} · بررسی QA: {String(e.qa_status || "PENDING")}
                    </div>
                    {String(e.qa_status || "PENDING").toUpperCase() !== "VERIFIED" &&
                      String(e.qa_status || "PENDING").toUpperCase() !== "APPROVED" && (
                        <button type="button" className="pro-btn-secondary" disabled={researchBusy || !researchReviewReason.trim()}
                          onClick={() => void reviewEvidence(e.evidence_id)}>
                          بررسی و ثبت VERIFIED
                        </button>
                      )}
                  </li>
                ))}
              </ul>
            )}
          </div>
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
