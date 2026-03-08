import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3131,
    proxy: {
      '/dist': {
        target: 'http://127.0.0.1:3133',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'build',
  },
})
