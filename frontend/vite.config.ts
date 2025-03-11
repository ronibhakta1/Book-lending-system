import path from "path"
import tailwindcss from "@tailwindcss/vite"
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
    plugins: [react(), tailwindcss()],
    resolve: {
        alias: {
        "@": path.resolve(__dirname, "./src"),
        },
    },
    server: {
        port: 8081,
        host: "0.0.0.0",
        proxy: {
            "/api": {
                target: "http://app:7001",  // Backend container name in Docker
                changeOrigin: true,
            },
        },
    },
});