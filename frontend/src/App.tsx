import { ReactNode } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import NewHomePage from "./pages/NewHomePage";
import PilotPage from "./pages/PilotPage";
import RecommendationPage from "./pages/RecommendationPage";
import AccountingHomePage from "./pages/AccountingHomePage";
import InventoryHomePage from "./pages/InventoryHomePage";
import PurchasePage from "./pages/PurchasePage";
import AdminLoginPage from "./pages/AdminLoginPage";
import PricingFxPage from "./pages/PricingFxPage";

function AdminGate({ children }: { children: ReactNode }) {
  const token = sessionStorage.getItem("hbi_admin_access_token");
  return token ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<AdminLoginPage />} />
      <Route path="/" element={<AdminGate><NewHomePage /></AdminGate>} />
      <Route path="/catalog" element={<Navigate to="/" replace />} />
      {/* HBI has one system user: the Admin/Operator. Customer records do not
          grant browser access to operational pages. API authorization remains
          independently enforced by the backend. */}
      <Route path="/pilot" element={<AdminGate><PilotPage /></AdminGate>} />
      <Route path="/recommendation" element={<AdminGate><RecommendationPage /></AdminGate>} />
      <Route path="/accounting" element={<AdminGate><AccountingHomePage /></AdminGate>} />
      <Route path="/inventory" element={<AdminGate><InventoryHomePage /></AdminGate>} />
      <Route path="/purchase" element={<AdminGate><PurchasePage /></AdminGate>} />
      <Route path="/pricing-fx" element={<AdminGate><PricingFxPage /></AdminGate>} />
    </Routes>
  );
}
