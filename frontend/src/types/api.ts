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
  open_case?: boolean;
}

/** Guest create request (POST /api/v1/customers/guest) */
export interface GuestCreateRequest {
  name: string;
  consent: number;
  concerns?: string;
}

/** POST /api/v1/sales/ body */
export interface SaleItemInput {
  product_id: string;
  quantity: number;
  recommendation_id?: string;
  /** Optional: backend derives the authoritative sale price from inventory when omitted. */
  unit_price_toman?: number;
  unit_price_usd?: number;
}

export interface SaleCreateRequest {
  customer_id: string;
  items: SaleItemInput[];
  fx_rate_usd_to_irr: number;
}

/** Sale response (backend may return ORM-shaped dict) */
export interface SaleDTO {
  sale_id?: string;
  customer_id?: string;
  total_amount_toman?: number;
  items?: Array<{ product_id?: string; quantity?: number; recommendation_id?: string | null }>;
  [key: string]: unknown;
}

/** POST /api/v1/products/ body — matches backend ProductCreate */
export interface ProductCreateRequest {
  product_id: string;
  brand: string;
  product_name: string;
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
