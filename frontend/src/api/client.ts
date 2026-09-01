/**
 * Minimal HBI API client — endpoints only as present on backend.
 * Base path: /api/v1
 */
import type {
  CaseCreateRequest,
  CaseDTO,
  CustomerIntakeRequest,
  GuestCreateRequest,
  PilotTokenRequest,
  ProductDTO,
  RecommendationDTO,
  RecommendationRequest,
  TokenPair,
  SaleCreateRequest,
  SaleDTO,
  ProductCreateRequest,
  ProductUpdateRequest,
} from "../types/api";

const BASE = import.meta.env?.VITE_API_BASE ?? "/api/v1";

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`HTTP ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

/** Public — no auth */
export function listProducts(): Promise<ProductDTO[]> {
  return request<ProductDTO[]>("/products/");
}

/** Dev/Pilot only */
export function pilotToken(body: PilotTokenRequest): Promise<TokenPair> {
  return request<TokenPair>("/auth/pilot-token", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** Requires auth; body must use case_type, NOT concerns */
export function createCase(
  body: CaseCreateRequest,
  token: string
): Promise<CaseDTO> {
  return request<CaseDTO>(
    "/cases/",
    { method: "POST", body: JSON.stringify(body) },
    token
  );
}

export function listCasesByCustomer(
  customerId: string,
  token: string
): Promise<CaseDTO[]> {
  return request<CaseDTO[]>(`/cases/customer/${customerId}`, {}, token);
}

export function generateRecommendations(
  body: RecommendationRequest,
  token: string
): Promise<RecommendationDTO[]> {
  return request<RecommendationDTO[]>(
    "/recommendations/generate",
    { method: "POST", body: JSON.stringify(body) },
    token
  );
}

export function listRecommendationsByCase(
  caseId: string,
  token: string
): Promise<RecommendationDTO[]> {
  return request<RecommendationDTO[]>(
    `/recommendations/case/${caseId}`,
    {},
    token
  );
}

/** Customer Intake — requires auth */
export function customerIntake(
  body: CustomerIntakeRequest,
  token: string
): Promise<unknown> {
  return request<unknown>(
    "/customers/intake",
    { method: "POST", body: JSON.stringify(body) },
    token
  );
}

/** Guest creation — no auth required (public) */
export function createGuest(
  body: GuestCreateRequest
): Promise<unknown> {
  return request<unknown>("/customers/guest", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** Get product evidence — requires auth */
export function getProductEvidence(
  productId: string,
  token: string
): Promise<unknown> {
  return request<unknown>(`/evidence/?product_id=${productId}`, {}, token);
}

/** POST /api/v1/sales/ — requires auth; customer_id must match token identity */
export function createSale(
  body: SaleCreateRequest,
  token: string
): Promise<SaleDTO> {
  return request<SaleDTO>(
    "/sales/",
    { method: "POST", body: JSON.stringify(body) },
    token
  );
}

/** GET /api/v1/sales/total — requires auth */
export function getTotalSales(token: string): Promise<{ total_sales: number }> {
  return request<{ total_sales: number }>("/sales/total", {}, token);
}

/** POST /api/v1/products/ — public create (PO-confirmed draft) */
export function createProduct(body: ProductCreateRequest): Promise<ProductDTO> {
  return request<ProductDTO>("/products/", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** GET /api/v1/products/{id} */
export function getProduct(productId: string): Promise<ProductDTO> {
  return request<ProductDTO>(`/products/${encodeURIComponent(productId)}`);
}

/** PATCH /api/v1/products/{id} — PO edit after save */
export function updateProduct(
  productId: string,
  body: ProductUpdateRequest
): Promise<ProductDTO> {
  return request<ProductDTO>(`/products/${encodeURIComponent(productId)}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}
