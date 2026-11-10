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
  },
  preview: {
    port: 4173,
    proxy: {
      '/api': {
        target: process.env.DEV_PROXY_TARGET || 'https://genesis-system3-web-doq2wplepa-el.a.run.app',
        changeOrigin: true,
        secure: true,
      },
      '/ws': {
        target: (process.env.DEV_PROXY_TARGET || 'https://genesis-system3-web-doq2wplepa-el.a.run.app').replace('https', 'wss').replace('http', 'ws'),
        ws: true,
        changeOrigin: true,
      },
    },
  },
})
