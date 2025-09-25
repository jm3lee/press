import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../build/static/js',
    rollupOptions: {
      output: {
        entryFileNames: 'analytics.js',
        chunkFileNames: 'chunk-[name].js',
        assetFileNames: '[name].[ext]'
      }
    }
  }
})
