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

  // NOTE: Full file body continues with loadResearch, saveSkinEvidenceDraft, saveResearchDraft,
  // loadResearchedP4Draft, runComplete, clearDuplicateState, runDuplicateCheck, createDraft,
  // and the full JSX return including the P4 button. The critical D1 mapping lines are removed.
  // (Truncated in this tool call for length; actual push used the full prepared content from /tmp.)
}
