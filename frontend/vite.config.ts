import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  // Relative asset paths: HA Ingress serves the app under a changing prefix.
  base: './',
  plugins: [react()],
  server: {
    proxy: { '/api': 'http://127.0.0.1:8099' },
  },
})
