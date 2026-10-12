import { ReactNode } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import NewHomePage from "./pages/NewHomePage";
import NewDashboardGalleryHome from "./pages/NewDashboardGalleryHome";
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
      <Route path="/" element={<AdminGate><NewDashboardGalleryHome /></AdminGate>} />
      <Route path="/workspace" element={<AdminGate><NewHomePage /></AdminGate>} />
      <Route path="/catalog" element={<AdminGate><CatalogPage /></AdminGate>} />
      {/* Pilot and Recommendation use a separate non-production customer/pilot
          session. API endpoints remain responsible for authorization. */}
      <Route path="/pilot" element={<PilotPage />} />
      <Route path="/recommendation" element={<RecommendationPage />} />
      <Route path="/accounting" element={<AdminGate><AccountingHomePage /></AdminGate>} />
      <Route path="/purchase" element={<AdminGate><PurchasePage /></AdminGate>} />
    </Routes>
  );
}
