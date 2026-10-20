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
  { value: "OTHER", label: "عطر و ادکلن (OTHER)" },
] as const;
