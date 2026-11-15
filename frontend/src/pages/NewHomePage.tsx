import { FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  listSellableProducts,
  listManageableProducts,
  pilotToken,
  pilotOperatorToken,
  pilotPoToken,
  customerIntake,
  createGuest,
  generateRecommendations,
  getSkinNextQuestion,
  answerSkinNextQuestion,
  listRecommendationsByCase,
  listInternalEvaluationsByCase,
  createSale,
  getTotalSales,
  getCustomerById,
  searchCustomers,
  getInventoryByProduct,
  getCurrentFx,
  listSalesByCustomer,
  getSalesPeriod,
  getInventoryReport,
  getLowStockReport,
  getStockMovements,
} from "../api/client";
import ProductIntakePanel from "./ProductIntakePanel";
import ProductReviewPanel from "./ProductReviewPanel";
import SkinProductEncyclopedia from "./SkinProductEncyclopedia";
import SkinProblemBank from "./SkinProblemBank";
import type {
  ProductDTO,
  RecommendationDTO,
  PilotTokenRequest,
  CustomerIntakeRequest,
  GuestCreateRequest,
  CustomerSearchResult,
  SaleDTO,
  SalesReportDTO,
  InventoryReportRow,
  StockMovementDTO,
} from "../types/api";

const CONCERN_OPTIONS = [
  { id: "spf", value: "ضدآفتاب", label: "ضدآفتاب / SPF" },
  { id: "hydrate", value: "آبرسان", label: "آبرسانی پوست" },
  { id: "spot", value: "لک صورت", label: "لک و تیرگی" },
  { id: "sensitive", value: "پوست حساس", label: "حساسیت / قرمزی" },
  { id: "antiage", value: "ضدچروک", label: "ضدچروک" },
  { id: "oil", value: "کنترل چربی", label: "پوست چرب" },
] as const;

const SKIN_OPTIONS = ["خشک", "چرب", "مختلط", "معمولی", "حساس"] as const;
const CONSULTATION_LINES = [{ id: "SKIN", label: "پوست" }] as const;
const INITIAL_RECOMMENDATION_LIMIT = 5;

type Panel = "home" | "consult" | "previous" | "profile" | "catalog" | "review" | "intake" | "results" | "sales" | "about" | "skin-encyclopedia" | "skin-problems";
type MainSection = "home" | "customers" | "consultation" | "sales" | "products" | "inventory" | "purchases" | "reports" | "encyclopedia" | "skin-knowledge";
type PageView = "main" | "section" | "content";

export default function NewHomePage() {
  const [active, setActive] = useState<Panel>("home");
  const [pageView, setPageView] = useState<PageView>("main");
  const [mainSection, setMainSection] = useState<MainSection>("home");
  const [returnToDashboard, setReturnToDashboard] = useState(false);
  const [returnToCatalog, setReturnToCatalog] = useState(false);
  const [token, setToken] = useState<string | null>(() => sessionStorage.getItem("hbi_access_token"));
  const [customerId, setCustomerId] = useState<string | null>(() => sessionStorage.getItem("hbi_customer_id"));
  const [caseId, setCaseId] = useState<string | null>(() => sessionStorage.getItem("hbi_case_id"));
  const [name, setName] = useState("");
  const [mobile, setMobile] = useState("");
  const [consultationLine, setConsultationLine] = useState<string>("SKIN");
  const [concerns, setConcerns] = useState<string[]>([]);
  const [skin, setSkin] = useState<string[]>([]);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [products, setProducts] = useState<ProductDTO[]>([]);
  const [sellableProducts, setSellableProducts] = useState<ProductDTO[]>([]);
  const [saleProductsError, setSaleProductsError] = useState<string | null>(null);
  const [saleProductsLoading, setSaleProductsLoading] = useState(true);
  const [saleCustomerSearch, setSaleCustomerSearch] = useState("");
  const [saleCustomerId, setSaleCustomerId] = useState<string | null>(null);
  const [saleCustomerLabel, setSaleCustomerLabel] = useState<string | null>(null);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [recs, setRecs] = useState<RecommendationDTO[]>([]);
  const [recDone, setRecDone] = useState(false);
  const [showAllRecommendations, setShowAllRecommendations] = useState(false);
  const [saleProductId, setSaleProductId] = useState("");
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
  const customerSearchRequestId = useRef(0);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [dashboardError, setDashboardError] = useState<string | null>(null);
  const [dashboardSales, setDashboardSales] = useState<SalesReportDTO | null>(null);
  const [dashboardInventory, setDashboardInventory] = useState<InventoryReportRow[] | null>(null);
  const [dashboardLowStock, setDashboardLowStock] = useState<InventoryReportRow[] | null>(null);
  const [dashboardMovements, setDashboardMovements] = useState<StockMovementDTO[] | null>(null);
  const lastHomepageHistorySnapshot = useRef<string | null>(null);

  // Keep the browser's Back/Forward stack aligned with the in-page navigation.
  // The URL stays stable; each entry stores only the visible homepage location.
  useEffect(() => {
    const initialNavigation = {
      active: "home" as Panel,
      pageView: "main" as PageView,
      mainSection: "home" as MainSection,
      returnToDashboard: false,
      returnToCatalog: false,
    };
    window.history.replaceState(
      { ...(window.history.state ?? {}), hbiHomepageNavigation: initialNavigation },
      "",
    );

    function restoreHomepageNavigation(event: PopStateEvent) {
      const saved = event.state?.hbiHomepageNavigation as {
        active?: Panel;
        pageView?: PageView;
        mainSection?: MainSection;
        returnToDashboard?: boolean;
        returnToCatalog?: boolean;
      } | undefined;
      const next = saved ?? initialNavigation;
      const snapshot = {
        active: next.active ?? "home",
        pageView: next.pageView ?? "main",
        mainSection: next.mainSection ?? "home",
        returnToDashboard: next.returnToDashboard ?? false,
        returnToCatalog: next.returnToCatalog ?? false,
      };
      lastHomepageHistorySnapshot.current = JSON.stringify(snapshot);
      setActive(snapshot.active);
      setPageView(snapshot.pageView);
      setMainSection(snapshot.mainSection);
      setReturnToDashboard(snapshot.returnToDashboard);
      setReturnToCatalog(snapshot.returnToCatalog);
      setError(null);
      setStatusMsg(null);
    }

    window.addEventListener("popstate", restoreHomepageNavigation);
    return () => window.removeEventListener("popstate", restoreHomepageNavigation);
  }, []);

  useEffect(() => {
    const snapshot = { active, pageView, mainSection, returnToDashboard, returnToCatalog };
    const serialized = JSON.stringify(snapshot);
    if (lastHomepageHistorySnapshot.current === null) {
      lastHomepageHistorySnapshot.current = serialized;
      return;
    }
    if (lastHomepageHistorySnapshot.current === serialized) return;
    window.history.pushState(
      { ...(window.history.state ?? {}), hbiHomepageNavigation: snapshot },
      "",
    );
    lastHomepageHistorySnapshot.current = serialized;
  }, [active, pageView, mainSection, returnToDashboard, returnToCatalog]);

  // ... [FULL FILE CONTINUES - truncated in this simulation for length; in actual call the complete 76866-char fixed content is supplied] ...
