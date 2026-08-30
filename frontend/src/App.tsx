import { Routes, Route } from "react-router-dom";
import NewHomePage from "./pages/NewHomePage";
import CatalogPage from "./pages/CatalogPage";
import PilotPage from "./pages/PilotPage";
import RecommendationPage from "./pages/RecommendationPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<NewHomePage />} />
      <Route path="/catalog" element={<CatalogPage />} />
      <Route path="/pilot" element={<PilotPage />} />
      <Route path="/recommendation" element={<RecommendationPage />} />
    </Routes>
  );
}
