/**
 * HBI Frontend API contracts — aligned with backend HEAD.
 * Source of Truth: FastAPI routers + app/interface/dto.py
 * Do not invent endpoints or fields not present on the backend.
 */

/** POST /api/v1/auth/pilot-token response (backend TokenPair) */
export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

/** POST /api/v1/auth/pilot-token body */
export interface PilotTokenRequest {
  customer_id: string;
}

/** POST /api/v1/cases/ body — backend CaseCreateRequest */
export interface CaseCreateRequest {
  customer_id: string;
  case_type?: string;
}

/** Case response */
export interface CaseDTO {
  case_id: string;
  customer_id: string;
  case_type?: string;
  [key: string]: unknown;
}

/**
 * POST /api/v1/recommendations/generate body
 * concerns belong here (customer_profile), NOT on CaseCreateRequest.
 */
export interface RecommendationRequest {
  case_id: string;
  customer_profile?: {
    concerns?: string | string[];
    [key: string]: unknown;
  };
}

/**
 * Recommendation response — backend RecommendationDTO / AD-3.
 * Frontend may ignore optional fields but must not reject them.
 */
export interface RecommendationDTO {
  recommendation_id: string;
  case_id: string;
  product_id: string;
  need_match_score?: number | null;
  eligibility_status?: string | null;
  ranking_score?: number | null;
  ranking_reasons?: string | null;
  final_score?: number | null;
  confidence?: number | null;
  eligibility?: string | null;
  reasoning?: string | null;
  evidence_score?: number | null;
  evidence_refs?: unknown[] | null;
  warnings?: unknown[] | null;
  exclusion_reasons?: string[] | null;
  availability?: string | null;
  price?: number | null;
}

/** Public product listing item */
export interface ProductDTO {
  product_id: string;
  brand: string;
  product_name: string;
  identity_status: string;
  qa_verdict: string;
  variant?: string | null;
  size_value?: number | null;
  size_unit?: string | null;
  [key: string]: unknown;
}

/** Customer intake request (POST /api/v1/customers/intake) */
export interface CustomerSearchResult {
  customer_id: string;
  name: string;
  mobile?: string | null;
  consent_to_store_data?: number;
  concerns?: string | null;
  skin_profile?: string | null;
}

/** POST /api/v1/customers/intake request */
export interface CustomerIntakeRequest {
  name: string;
  mobile?: string;
  concerns?: string;
  consent: number;
  skin_profile?: unknown;
  guest?: boolean;
  case_type?: string;
  open_case?: boolean;
}

/** Guest create */
export interface GuestCreateRequest {
  name?: string;
  mobile?: string;
  [key: string]: unknown;
}

/** Sale create */
export interface SaleCreateRequest {
  customer_id: string;
  items?: Array<{ product_id?: string; quantity?: number; recommendation_id?: string | null }>;
  [key: string]: unknown;
}

/** Sale DTO */
export interface SaleDTO {
  sale_id: string;
  customer_id?: string;
  [key: string]: unknown;
}

/** POST /api/v1/products/ body — matches backend ProductCreate */
export interface ProductCreateRequest {
  product_id: string;
  brand: string;
  product_name: string;
  product_line: string;
  variant?: string | null;
  size_value?: number | null;
  size_unit?: string | null;
  barcode_gtin?: string | null;
  market_region?: string | null;
  country_of_origin?: string | null;
  packaging_version?: string | null;
  knowledge_use_cases?: string | null;
  knowledge_evidence_claim?: string | null;
  knowledge_evidence_source_reference?: string | null;
  /** WP-01: after POSSIBLE_MATCH + operator decision=NEW */
  duplicate_check_id?: string | null;
}

/** PATCH /api/v1/products/{id} — matches backend ProductUpdate */
export interface ProductUpdateRequest {
  brand?: string | null;
  product_name?: string | null;
  variant?: string | null;
  size_value?: number | null;
  size_unit?: string | null;
  barcode_gtin?: string | null;
  market_region?: string | null;
  country_of_origin?: string | null;
  packaging_version?: string | null;
  product_line?: string | null;
}

/** POST /api/v1/products/duplicate-check/ — identity payload */
export interface DuplicateCheckRequest {
  product_id?: string | null;
  barcode_gtin?: string | null;
  brand?: string | null;
  product_name?: string | null;
  variant?: string | null;
  size_value?: number | null;
  size_unit?: string | null;
  market_region?: string | null;
  packaging_version?: string | null;
}

export interface DuplicateCheckCandidate {
  product_id: string;
  brand?: string | null;
  product_name?: string | null;
  variant?: string | null;
  size_value?: number | null;
  size_unit?: string | null;
  packaging_version?: string | null;
  result?: string;
  match_tier?: string;
  conflicting_fields?: string[];
}

/** Response of POST /api/v1/products/duplicate-check/ */
export interface DuplicateCheckResponse {
  check_id: string;
  result: "NEW" | "POSSIBLE_MATCH" | "EXISTING" | string;
  reason?: string;
  candidates?: DuplicateCheckCandidate[];
  naming_reference?: Array<Record<string, unknown>>;
  operator_decision_required?: boolean;
  provenance?: Record<string, unknown>;
}

/** POST /api/v1/products/duplicate-check/audit/{check_id}/decision */
export interface DuplicateCheckOperatorDecisionRequest {
  decision: "NEW" | "EXISTING" | "RENAME" | string;
  selected_product_id?: string | null;
  final_product_name?: string | null;
  reason?: string | null;
}

export interface DuplicateCheckOperatorDecisionResponse {
  check_id: string;
  result?: string;
  operator_decision?: Record<string, unknown> | null;
  [key: string]: unknown;
}

/** Admin reporting contracts used by AccountingHomePage. */
export interface SalesReportDTO {
  start: string;
  end: string;
  sale_count: number;
  revenue_usd: number;
  revenue_irr: number;
  revenue_toman: number;
  sales?: Array<Record<string, unknown>>;
}

export interface InventoryReportRow {
  inventory_id: string;
  product_id: string;
  category_id?: string | null;
  quantity_available: number;
  quantity_reserved: number;
  stock_status: string;
  purchase_price_usd?: number | null;
  sale_price_usd?: number | null;
  purchase_price_toman?: number | null;
  sale_price_toman?: number | null;
  price_fx_rate_usd_to_irr?: number | null;
  inventory_value_usd?: number | null;
  inventory_value_irr?: number | null;
  inventory_value_toman?: number | null;
  inventory_value_basis?: string;
}

export interface FinancialSummaryDTO {
  start: string;
  end: string;
  revenue_usd: number;
  revenue_irr: number;
  revenue_toman: number;
  returns_usd: number;
  returns_irr: number;
  returns_toman: number;
  net_revenue_usd: number;
  net_revenue_irr: number;
  net_revenue_toman: number;
  return_count: number;
  sale_count: number;
  discounts?: { status: string; reason?: string };
  cogs?: { status: string; reason?: string };
  gross_profit?: { status: string; reason?: string };
}

export interface StockMovementDTO {
  movement_id: string;
  product_id: string;
  inventory_id?: string | null;
  movement_type: string;
  quantity_delta: number;
  quantity_after: number;
  amount_usd?: number | null;
  amount_irr?: number | null;
  amount_toman?: number | null;
  fx_rate_usd_to_irr?: number | null;
  reference_type?: string | null;
  reference_id?: string | null;
  note?: string | null;
  created_at?: string | null;
}

export interface EvidenceDTO {
  evidence_id: string;
  product_id: string;
  claim?: string | null;
  field?: string | null;
  claim_type?: string | null;
  qa_status?: string | null;
  conflict_status?: string | null;
  source_type?: string | null;
  source_reference?: string | null;
  evidence_status?: string | null;
  [key: string]: unknown;
}

export interface MutationLogDTO {
  id?: string | number | null;
  action?: string | null;
  actor_id?: string | null;
  actor_role?: string | null;
  target_id?: string | null;
  resulting_state?: string | null;
  reason?: string | null;
  before?: unknown;
  after?: unknown;
  created_at?: string | null;
  [key: string]: unknown;
}
