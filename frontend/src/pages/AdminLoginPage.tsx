import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

const API_BASE = import.meta.env?.VITE_API_BASE ?? "/api/v1";

export default function AdminLoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail || "ورود ناموفق بود.");
      }
      sessionStorage.setItem("hbi_admin_access_token", data.access_token);
      sessionStorage.setItem("hbi_admin_refresh_token", data.refresh_token);
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "ورود ناموفق بود.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={{ maxWidth: 420, margin: "60px auto", padding: 24 }}>
      <h1>ورود مدیر HBI</h1>
      <p>برای ورود به محیط مدیریتی، نام کاربری و رمز عبور را وارد کنید.</p>
      <form onSubmit={submit}>
        <label>
          نام کاربری
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" required />
        </label>
        <label>
          رمز عبور
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" required />
        </label>
        <button type="submit" disabled={busy}>{busy ? "در حال ورود..." : "ورود"}</button>
      </form>
      {error && <p role="alert">{error}</p>}
    </main>
  );
}
