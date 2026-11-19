/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In development the React app runs on :5173 and forwards API and photo requests
// to the Python server on :8000.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/thumbs': 'http://localhost:8000',
    },
  },
  test: { environment: 'jsdom' },
})
