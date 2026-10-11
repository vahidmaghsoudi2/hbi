import { ReactNode } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import NewHomePage from "./pages/NewHomePage";
import CatalogPage from "./pages/CatalogPage";
import PilotPage from "./pages/PilotPage";
import RecommendationPage from "./pages/RecommendationPage";
import AccountingHomePage from "./pages/AccountingHomePage";
import PurchasePage from "./pages/PurchasePage";
import AdminLoginPage from "./pages/AdminLoginPage";

function AdminGate({ children }: { children: ReactNode }) {
  const token = sessionStorage.getItem("hbi_admin_access_token");
  return token ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<AdminLoginPage />} />
      <Route path="/" element={<NewHomePage />} />
      <Route path="/catalog" element={<AdminGate><CatalogPage /></AdminGate>} />
      {/* Pilot and Recommendation use a separate non-production customer/pilot
          session. AdminGate checks hbi_admin_access_token and would block this
          flow before its own token acquisition. API endpoints remain responsible
          for authorization; the pilot-token endpoint is disabled in production. */}
      <Route path="/pilot" element={<PilotPage />} />
      <Route path="/recommendation" element={<RecommendationPage />} />
      <Route path="/accounting" element={<AdminGate><AccountingHomePage /></AdminGate>} />
      <Route path="/purchase" element={<AdminGate><PurchasePage /></AdminGate>} />
    </Routes>
  );
}
