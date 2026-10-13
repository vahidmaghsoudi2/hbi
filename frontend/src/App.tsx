import { ReactNode } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import NewHomePage from "./pages/NewHomePage";
import NewDashboardGalleryHome from "./pages/NewDashboardGalleryHome";
import CatalogPage from "./pages/CatalogPage";
import PilotPage from "./pages/PilotPage";
import RecommendationPage from "./pages/RecommendationPage";
import AccountingHomePage from "./pages/AccountingHomePage";
import PurchasePage from "./pages/PurchasePage";
import SimpleSalesPage from "./pages/SimpleSalesPage";
import AdminLoginPage from "./pages/AdminLoginPage";

function AdminGate({ children }: { children: ReactNode }) {
  const token = sessionStorage.getItem("hbi_admin_access_token");
  return token ? children : <Navigate to="/login" replace />;
}

/**
 * Compatibility router for old homepage panel links.
 * Sales is a standalone workflow and must never render inside the legacy
 * all-in-one workspace. Keep other legacy panels intact until each has a
 * verified dedicated destination.
 */
function WorkspaceRoute() {
  const location = useLocation();
  const panel = new URLSearchParams(location.search).get("panel");

  if (panel === "sales") return <Navigate to="/sales" replace />;
  if (panel === "catalog") return <Navigate to="/catalog" replace />;
  if (panel === "purchase") return <Navigate to="/purchase" replace />;

  return <NewHomePage />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<AdminLoginPage />} />
      <Route path="/" element={<AdminGate><NewDashboardGalleryHome /></AdminGate>} />
      <Route path="/workspace" element={<AdminGate><WorkspaceRoute /></AdminGate>} />
      <Route path="/catalog" element={<AdminGate><CatalogPage /></AdminGate>} />
      {/* Pilot/recommendation are operator-only internal workflows, not customer
          entry points. Their API tokens do not grant access to the HBI UI. */}
      <Route path="/pilot" element={<AdminGate><PilotPage /></AdminGate>} />
      <Route path="/recommendation" element={<AdminGate><RecommendationPage /></AdminGate>} />
      <Route path="/accounting" element={<AdminGate><AccountingHomePage /></AdminGate>} />
      <Route path="/purchase" element={<AdminGate><PurchasePage /></AdminGate>} />
      <Route path="/sales" element={<AdminGate><SimpleSalesPage /></AdminGate>} />
      {/* Unknown paths should never render an empty shell or bypass AdminGate. */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
