import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/ui/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    emptyOutDir: true,
  },
  server: {
    port: 3000,
    proxy: {
      '/api': { target: process.env.DEV_PROXY_TARGET || 'http://127.0.0.1:8000', changeOrigin: true, secure: false },
      '/ws':  { target: (process.env.DEV_PROXY_TARGET || 'http://127.0.0.1:8000').replace('http', 'ws'), ws: true },
      '^/(genesis-production-brief|autonomous-brain|hidden-secrets-lab|never-die-monitor|hunger-meter|data-truth-score|health|final-message)$': {
        target: process.env.DEV_PROXY_TARGET || 'http://127.0.0.1:8000', changeOrigin: true, secure: false,
      },
    }
  },
  preview: {
    port: 4173,
    proxy: {
      '/api': {
        target: process.env.DEV_PROXY_TARGET || 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: true,
      },
      '/ws': {
        target: (process.env.DEV_PROXY_TARGET || 'http://127.0.0.1:8000').replace('https', 'wss').replace('http', 'ws'),
        ws: true,
        changeOrigin: true,
      },
      '^/(genesis-production-brief|autonomous-brain|hidden-secrets-lab|never-die-monitor|hunger-meter|data-truth-score|health|final-message)$': {
        target: process.env.DEV_PROXY_TARGET || 'http://127.0.0.1:8000', changeOrigin: true, secure: false,
      },
    },
  },
})
