import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// NOTE: If both vite.config.js and vite.config.ts exist, Vite may load .js first.
// Keep proxy here so /api/v1/* reaches Backend on :8000 (avoids HTTP 404 from Vite).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
