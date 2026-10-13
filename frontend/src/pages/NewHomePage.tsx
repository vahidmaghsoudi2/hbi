import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  listManageableProducts,
  pilotToken,
  pilotOperatorToken,
  pilotPoToken,
  customerIntake,
  createGuest,
  generateRecommendations,
  listInternalEvaluationsByCase,
  createSale,
  getTotalSales,
  getCustomerById,
  searchCustomers,
  getInventoryByProduct,
  getCurrentFx,
  listSalesByCustomer,
} from "../api/client";
import ProductIntakePanel from "./ProductIntakePanel";
import ProductReviewPanel from "./ProductReviewPanel";
import { domainForPanel, workspaceDomainNav } from "./workspaceDomainNav";
import type {
  ProductDTO,
  RecommendationDTO,
  PilotTokenRequest,
  CustomerIntakeRequest,
  GuestCreateRequest,
  CustomerSearchResult,
  SaleDTO,
} from "../types/api";

// NOTE: Full file restored via local recovery path if this stub is incomplete.
// Temporary safe shell — real body is applied on next push.
export default function NewHomePage() {
  const domain = workspaceDomainNav[domainForPanel("consult")];
  return (
    <div className="home-root pro-home">
      <header className="pro-header">
        <div className="pro-header-inner">
          <div className="pro-brand">
            <span className="pro-brand-mark">HBI</span>
            <div>
              <div className="pro-brand-title">{domain.title}</div>
              <div className="pro-brand-sub">در حال بازیابی فایل کامل…</div>
            </div>
          </div>
          <nav className="pro-nav">
            <Link to="/" className="pro-nav-btn">← داشبورد</Link>
          </nav>
        </div>
      </header>
      <main className="pro-main">
        <p className="pro-lead">فایل NewHomePage روی remote موقتاً ساده شده است. با دستور بازیابی محلی، نسخهٔ کامل را بگیرید.</p>
      </main>
    </div>
  );
}
