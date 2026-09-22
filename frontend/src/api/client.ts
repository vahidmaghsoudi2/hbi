/**
 * Minimal HBI API client — endpoints only as present on backend.
 * Base path: /api/v1
 */
import type {
  CaseCreateRequest,
  CaseDTO,
  CustomerIntakeRequest,
  CustomerSearchResult,
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
  SalesReportDTO,
  InventoryReportRow,
  FinancialSummaryDTO,
  StockMovementDTO,
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

/** Dev/Pilot only — operator session for Product Intake governance actions. */
export function pilotOperatorToken(): Promise<TokenPair> {
  return request<TokenPair>("/auth/pilot-operator-token", {
    method: "POST",
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

/** Active customer profile — requires the active customer token. */
/** Search existing customers by name — requires an authenticated operational/customer access token. */
export function searchCustomers(query: string, token: string): Promise<CustomerSearchResult[]> {
  return request<CustomerSearchResult[]>(
    `/customers/search?q=${encodeURIComponent(query)}`,
    {},
    token
  );
}

export function getCustomerById(customerId: string, token: string): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>(
    `/customers/id/${encodeURIComponent(customerId)}`,
    {},
    token
  );
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


/** POST /api/v1/inventory/stock-in — Admin-only purchase/stock intake. */
export function stockInInventory(
  body: {
    product_id: string;
    quantity: number;
    purchase_price_usd: number;
    fx_rate_usd_to_irr: number;
    note?: string;
    reference_type?: string;
    reference_id?: string;
  },
  adminToken: string
): Promise<{
  inventory: Record<string, unknown>;
  movement: Record<string, unknown>;
  before_quantity: number;
}> {
  return request(
    "/inventory/stock-in",
    { method: "POST", body: JSON.stringify(body) },
    adminToken
  );
}

/** GET /api/v1/fx/current — official operational USD/IRR rate; null means unavailable. */
export function getCurrentFx(): Promise<{ fx_rate_usd_to_irr: number | null; source?: unknown }> {
  return request<{ fx_rate_usd_to_irr: number | null; source?: unknown }>("/fx/current");
}

/** GET /api/v1/sales/customer/{customerId} — own purchase history only (AuthZ on path). */
export function listSalesByCustomer(
  customerId: string,
  token: string
): Promise<SaleDTO[]> {
  return request<SaleDTO[]>(
    `/sales/customer/${encodeURIComponent(customerId)}`,
    {},
    token
  );
}

/** POST /api/v1/products/ — requires the active pilot/customer JWT */
export function createProduct(body: ProductCreateRequest, token: string): Promise<ProductDTO> {
  return request<ProductDTO>("/products/", {
    method: "POST",
    body: JSON.stringify(body),
  }, token);
}

/** Operational catalog — includes DRAFT products; requires operator role. */
export function listManageableProducts(token: string): Promise<ProductDTO[]> {
  return request<ProductDTO[]>("/products/manage", {}, token);
}

/** GET /api/v1/products/{id} */
export function getProduct(productId: string): Promise<ProductDTO> {
  return request<ProductDTO>(`/products/${encodeURIComponent(productId)}`);
}

/** GET /api/v1/inventory/product/{id} — authoritative sell price and stock. */
export function getInventoryByProduct(
  productId: string,
  token: string
): Promise<{ product_id: string; quantity_available: number; quantity_reserved: number; stock_status: string; sale_price_toman?: number | null; sale_price_usd?: number | null }> {
  return request(
    `/inventory/product/${encodeURIComponent(productId)}`,
    {},
    token
  );
}

/** PATCH /api/v1/products/{id} — PO edit after save */
export function updateProduct(
  productId: string,
  body: ProductUpdateRequest,
  token: string
): Promise<ProductDTO> {
  return request<ProductDTO>(`/products/${encodeURIComponent(productId)}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  }, token);
}

/** Mission B — Specialist Override.
 * specialist_id is NOT sent; backend derives operator from authenticated token only.
 */
export function createSpecialistOverride(
  body: {
    recommendation_id: string;
    case_id: string;
    action: string;
    reason: string;
    notes?: string;
  },
  token: string
): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>(
    "/specialist/overrides",
    { method: "POST", body: JSON.stringify(body) },
    token
  );
}

export function listOverridesByCase(
  caseId: string,
  token: string
): Promise<Record<string, unknown>[]> {
  return request<Record<string, unknown>[]>(
    `/specialist/overrides/case/${encodeURIComponent(caseId)}`,
    {},
    token
  );
}

/** Mission B — Feedback / Follow-up */
export function createFeedback(
  body: {
    case_id: string;
    source: string;
    outcome?: string;
    rating?: string;
    comment?: string;
    recommendation_id?: string;
    follow_up_at?: string;
  },
  token: string
): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>(
    "/specialist/feedback",
    { method: "POST", body: JSON.stringify(body) },
    token
  );
}

export function listFeedbackByCase(
  caseId: string,
  token: string
): Promise<Record<string, unknown>[]> {
  return request<Record<string, unknown>[]>(
    `/specialist/feedback/case/${encodeURIComponent(caseId)}`,
    {},
    token
  );
}


/** Admin-only reporting APIs used by the Accounting console. */
export function getSalesPeriod(
  kind: "today" | "week" | "month",
  adminToken: string
): Promise<SalesReportDTO> {
  return request<SalesReportDTO>(`/reports/sales/period/${kind}`, {}, adminToken);
}

export function getSalesRange(
  start: string,
  end: string,
  adminToken: string
): Promise<SalesReportDTO> {
  return request<SalesReportDTO>(
    `/reports/sales/range?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`,
    {},
    adminToken
  );
}

export function getFinancialSummary(
  start: string,
  end: string,
  adminToken: string
): Promise<FinancialSummaryDTO> {
  return request<FinancialSummaryDTO>(
    `/reports/financial?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`,
    {},
    adminToken
  );
}

export function getInventoryReport(adminToken: string): Promise<InventoryReportRow[]> {
  return request<InventoryReportRow[]>("/reports/inventory", {}, adminToken);
}

export function getLowStockReport(
  threshold: number,
  adminToken: string
): Promise<InventoryReportRow[]> {
  return request<InventoryReportRow[]>(
    `/reports/inventory/low-stock?threshold=${threshold}`,
    {},
    adminToken
  );
}

export function getStockMovements(
  adminToken: string,
  options: { productId?: string; movementType?: string; limit?: number; offset?: number } = {}
): Promise<StockMovementDTO[]> {
  const params = new URLSearchParams();
  if (options.productId) params.set("product_id", options.productId);
  if (options.movementType) params.set("movement_type", options.movementType);
  params.set("limit", String(options.limit ?? 100));
  params.set("offset", String(options.offset ?? 0));
  const suffix = params.toString();
  return request<StockMovementDTO[]>(
    `/inventory/movements${suffix ? `?${suffix}` : ""}`,
    {},
    adminToken
  );
}
