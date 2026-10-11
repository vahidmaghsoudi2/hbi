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
      <Route path="/pilot" element={<AdminGate><PilotPage /></AdminGate>} />
      {/* RecommendationPage uses the pilot/customer token (hbi_access_token),
          not the separate admin token. Its API calls enforce endpoint-level
          authorization, so the route must not redirect valid pilot sessions
          to the admin login page before the persisted-readback flow can run. */}
      <Route path="/recommendation" element={<RecommendationPage />} />
      <Route path="/accounting" element={<AdminGate><AccountingHomePage /></AdminGate>} />
      <Route path="/purchase" element={<AdminGate><PurchasePage /></AdminGate>} />
    </Routes>
  );
}
