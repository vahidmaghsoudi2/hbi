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
  unit_price_toman: number;
}

export interface SaleCreateRequest {
  customer_id: string;
  items: SaleItemInput[];
}

/** Sale response (backend may return ORM-shaped dict) */
export interface SaleDTO {
  sale_id?: string;
  customer_id?: string;
  total_amount_toman?: number;
  items?: unknown;
  [key: string]: unknown;
}
