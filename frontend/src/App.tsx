import { Link, Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import PilotPage from "./pages/PilotPage";
import RecommendationPage from "./pages/RecommendationPage";

export default function App() {
  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <span className="brand-mark">HBI</span>
          <span className="brand-sub">Health & Beauty Intelligence</span>
        </div>
        <nav className="nav">
          <Link to="/">محصولات</Link>
          <Link to="/pilot">مسیر Pilot</Link>
        </nav>
      </header>
      <main className="main">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/pilot" element={<PilotPage />} />
          <Route path="/recommendation" element={<RecommendationPage />} />
        </Routes>
      </main>
      <footer className="footer">
        <span>HBI Pilot UI · قرارداد Backend بدون endpoint جعلی</span>
      </footer>
    </div>
  );
}
