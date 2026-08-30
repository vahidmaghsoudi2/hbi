/**
 * Legacy JS API client (kept for compatibility).
 * Standardized to use VITE_API_BASE like client.ts.
 */
const BASE = import.meta.env?.VITE_API_BASE ?? "/api/v1";

export async function hbiGet(path) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

export async function hbiPost(path, body, token) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  }
  return res.json();
}
