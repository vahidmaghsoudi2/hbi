import { useEffect, useState } from "react";
import { ReactNode } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import NewHomePage from "./pages/NewHomePage";
import CatalogPage from "./pages/CatalogPage";
import PilotPage from "./pages/PilotPage";
import RecommendationPage from "./pages/RecommendationPage";
import AccountingHomePage from "./pages/AccountingHomePage";
import PurchasePage from "./pages/PurchasePage";
import AdminLoginPage from "./pages/AdminLoginPage";

const API_BASE = import.meta.env?.VITE_API_BASE ?? "/api/v1";

function AdminGate({ children }: { children: ReactNode }) {
  const token = sessionStorage.getItem("hbi_admin_access_token");
  return token ? children : <Navigate to="/" replace />;
}

export default function App() {
  const [sessionReady, setSessionReady] = useState(false);
  const [sessionError, setSessionError] = useState("");

  useEffect(() => {
    let active = true;
    async function openLocalSession() {
      try {
        const response = await fetch(`${API_BASE}/auth/local-session`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        });
        const raw = await response.text();
        let data: { access_token?: string; refresh_token?: string; detail?: string } = {};
        if (raw) {
          try { data = JSON.parse(raw); } catch {
            throw new Error("پاسخ سرور معتبر نیست. سرویس HBI را بررسی کنید.");
          }
        }
        if (!response.ok) {
          throw new Error(data.detail || `ایجاد نشست محلی ناموفق بود (HTTP ${response.status}).`);
        }
        if (!data.access_token || !data.refresh_token) {
          throw new Error("پاسخ سرور فاقد اطلاعات نشست است.");
        }
        sessionStorage.setItem("hbi_admin_access_token", data.access_token);
        sessionStorage.setItem("hbi_admin_refresh_token", data.refresh_token);
        if (active) setSessionError("");
      } catch (error) {
        if (active) setSessionError(error instanceof Error ? error.message : "اتصال به سرویس HBI برقرار نشد.");
      } finally {
        if (active) setSessionReady(true);
      }
    }
    void openLocalSession();
    return () => { active = false; };
  }, []);

  if (!sessionReady) {
    return <main style={{ maxWidth: 560, margin: "80px auto", padding: 24 }} dir="rtl">در حال آماده‌سازی محیط محلی HBI...</main>;
  }
  if (sessionError) {
    return <main style={{ maxWidth: 560, margin: "80px auto", padding: 24 }} dir="rtl">
      <h1>اجرای HBI نیاز به بررسی دارد</h1>
      <p role="alert">{sessionError}</p>
      <p>پنجرهٔ Backend را بررسی کنید و مطمئن شوید HBI با راه‌انداز رسمی همین لپ‌تاپ اجرا شده است.</p>
      <button onClick={() => window.location.reload()}>تلاش دوباره</button>
    </main>;
  }

  return (
    <Routes>
      <Route path="/login" element={<Navigate to="/" replace />} />
      <Route path="/" element={<AdminGate><NewHomePage /></AdminGate>} />
      <Route path="/catalog" element={<AdminGate><CatalogPage /></AdminGate>} />
      {/* Pilot and Recommendation keep their separate non-production session flow. */}
      <Route path="/pilot" element={<PilotPage />} />
      <Route path="/recommendation" element={<RecommendationPage />} />
      <Route path="/accounting" element={<AdminGate><AccountingHomePage /></AdminGate>} />
      <Route path="/purchase" element={<AdminGate><PurchasePage /></AdminGate>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
