import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    // output into build/static/js
    outDir: '../build/static/js',
    rollupOptions: {
      output: {
        entryFileNames: 'indextree.js',
        chunkFileNames: 'chunk-[name].js',
        assetFileNames: '[name].[ext]'
      }
    }
  }
})
