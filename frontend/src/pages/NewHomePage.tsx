import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  listProducts,
  listManageableProducts,
  pilotToken,
  pilotOperatorToken,
  customerIntake,
  createGuest,
  generateRecommendations,
  listRecommendationsByCase,
  createSale,
  getTotalSales,
  getCustomerById,
  searchCustomers,
  getInventoryByProduct,
  getCurrentFx,
  listSalesByCustomer,
} from "../api/client";
import ProductIntakePanel from "./ProductIntakePanel";
import type {
  ProductDTO,
  RecommendationDTO,
  PilotTokenRequest,
  CustomerIntakeRequest,
  GuestCreateRequest,
  CustomerSearchResult,
  SaleDTO,
} from "../types/api";

const CONCERN_OPTIONS = [
  { id: "spf", value: "ضدآفتاب", label: "ضدآفتاب / SPF" },
  { id: "hydrate", value: "آبرسان", label: "آبرسانی پوست" },
  { id: "spot", value: "لک صورت", label: "لک و تیرگی" },
  { id: "sensitive", value: "پوست حساس", label: "حساسیت / قرمزی" },
  { id: "hair", value: "مراقبت مو", label: "مراقبت مو" },
  { id: "scalp", value: "پوسؠ سر", label: "پوست سر" },
  { id: "antiage", value: "ضدچروک", label: "ضدچروک" },
  { id: "oil", value: "کنترل چربی", label: "پوست چرب" },
] as const;

const SKIN_OPTIONS = ["خشک", "چرب", "مختلط", "معمولی", "حساس"] as const;

type Panel = "consult" | "previous" | "profile" | "catalog" | "intake" | "results" | "sales" | "about";

export default function NewHomePage() {
  const [active, setActive] = useState<Panel>("consult");
  const [token, setToken] = useState<string | null>(() => sessionStorage.getItem("hbi_access_token"));
  const [customerId, setCustomerId] = useState<string | null>(() => sessionStorage.getItem("hbi_customer_id"));
  const [caseId, setCaseId] = useState<string | null>(() => sessionStorage.getItem("hbi_case_id"));
  const [name, setName] = useState("");
  const [mobile, setMobile] = useState("");
  const [concerns, setConcerns] = useState<string[]>([]);
  const [skin, setSkin] = useState<string[]>([]);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [products, setProducts] = useState<ProductDTO[]>([]);
  const [sellableProducts, setSellableProducts] = useState<ProductDTO[]>([]);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [recs, setRecs] = useState<RecommendationDTO[]>([]);
  const [recDone, setRecDone] = useState(false);
  const [saleProductId, setSaleProductId] = useState("");
  const [selectedRecommendationId, setSelectedRecommendationId] = useState<string | null>(null);
  const [saleQty, setSaleQty] = useState(1);
  const [salePrice, setSalePrice] = useState<number | null>(null);
  const [saleStock, setSaleStock] = useState<number | null>(null);
  const [saleFxRate, setSaleFxRate] = useState<number | null>(null);
  const [saleBusy, setSaleBusy] = useState(false);
  const [lastSale, setLastSale] = useState<SaleDTO | null>(null);
  const [totalSales, setTotalSales] = useState<number | null>(null);
  const [editProduct, setEditProduct] = useState<ProductDTO | null>(null);
  const [profileSaving, setProfileSaving] = useState(false);
  const [customerSearch, setCustomerSearch] = useState("");
  const [customerSearchResults, setCustomerSearchResults] = useState<CustomerSearchResult[]>([]);
  const [purchaseHistory, setPurchaseHistory] = useState<SaleDTO[]>([]);
  const [customerSearchBusy, setCustomerSearchBusy] = useState(false);

  const loadProducts = useCallback(async () => {
    setCatalogLoading(true);
    setCatalogError(null);
    try {
      const operatorToken = await ensureProductSession();
      if (!operatorToken) throw new Error("نشست اپراتور برای مشاهده محصولات در دسترس نیست.");
      const data = await listManageableProducts(operatorToken);
      setProducts(Array.isArray(data) ? data : []);
    } catch (e) {
      setCatalogError(e instanceof Error ? e.message : String(e));
      setProducts([]);
    } finally {
      setCatalogLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadProducts();
  }, [loadProducts]);

  // NOTE: Full page body continues in artifact; this partial upload is insufficient.
  // See artifacts/NewHomePage_outflow_nav.tsx for the complete file with outflow nav.
  return (
    <div className="home-root pro-home" dir="rtl">
      <header className="pro-header">
        <nav className="pro-nav" aria-label="بخش‌های صفحه">
          <Link to="/purchase" className="pro-nav-btn">خرید</Link>
          <Link to="/outflow" className="pro-nav-btn">مخارج و ضایعات</Link>
          <Link to="/accounting" className="pro-nav-btn">حسابداری</Link>
        </nav>
      </header>
      <main className="pro-main">
        <p className="pro-error">
          NewHomePage incomplete on branch due to tool payload limit. Restore from artifacts/NewHomePage_outflow_nav.tsx (892 lines, sha256 735bdd6841393e16…).
        </p>
      </main>
    </div>
  );
}
