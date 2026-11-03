import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'

// 后端地址：可用 VITE_API_PROXY_TARGET 覆盖（默认 8000）
const apiTarget = process.env.VITE_API_PROXY_TARGET ?? 'http://127.0.0.1:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // 跨端协作约定 §13：开发环境前端 5173 → 后端 8000
      '/api': {
        target: apiTarget,
        changeOrigin: true,
      },
    },
  },
})
