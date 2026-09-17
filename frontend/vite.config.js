import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";


export default defineConfig({
  plugins: [react()],

  // Send API requests to FastAPI during local development
  server: {
    proxy: {
      "/verify": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true
      }
    }
  }
});