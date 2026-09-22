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
  { id: "scalp", value: "پوست سر", label: "پوست سر" },
  { id: "antiage", value: "ضدچروک", label: "ضدچروک" },
  { id: "oil", value: "کنترل چربی", label: "پوست چرب" },
] as const;

const SKIN_OPTIONS = ["خشک", "چرب", "مختلط", "معمولی", "حساس"] as const;

type Panel = "consult" | "previous" | "profile" | "catalog" | "intake" | "results" | "sales" | "about";

export default function NewHomePage() {
  return (
    <div className="home-root pro-home" dir="rtl">
      <header className="pro-header">
        <nav className="pro-nav">
          <Link to="/purchase" className="pro-nav-btn">خرید</Link>
          <Link to="/outflow" className="pro-nav-btn">مخارج و ضایعات</Link>
          <Link to="/accounting" className="pro-nav-btn">حسابداری</Link>
        </nav>
      </header>
      <main className="pro-main">
        <p className="pro-error">
          NewHomePage به علت حجم پایلود بالا موقتاً خراب شد. نسخهٔ کامل در artifacts/NewHomePage_outflow_nav.tsx آماده است و باید به شاخه بازگردانده شود.
        </p>
      </main>
    </div>
  );
}
