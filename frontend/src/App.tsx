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
import OperatorShell from "./layout/OperatorShell";

function AdminGate({ children }: { children: ReactNode }) {
  const token = sessionStorage.getItem("hbi_admin_access_token");
  return token ? <>{children}</> : <Navigate to="/login" replace />;
}

/** Old /workspace?panel=sales must never render the kitchen-sink page. */
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

      <Route
        element={
          <AdminGate>
            <OperatorShell />
          </AdminGate>
        }
      >
        <Route path="/" element={<NewDashboardGalleryHome />} />
        <Route path="/sales" element={<SimpleSalesPage />} />
        <Route path="/catalog" element={<CatalogPage />} />
        <Route path="/purchase" element={<PurchasePage />} />
        <Route path="/accounting" element={<AccountingHomePage />} />
        <Route path="/recommendation" element={<RecommendationPage />} />
        <Route path="/pilot" element={<PilotPage />} />
        <Route path="/workspace" element={<WorkspaceRoute />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
