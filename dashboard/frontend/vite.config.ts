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
      '/api': { target: process.env.DEV_PROXY_TARGET || 'http://localhost:8000', changeOrigin: true, secure: false },
      '/ws':  { target: (process.env.DEV_PROXY_TARGET || 'http://localhost:8000').replace('http', 'ws'), ws: true },
    }
  }
})
