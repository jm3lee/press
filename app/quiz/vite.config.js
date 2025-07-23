import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    // output into search-ui/dist
    outDir: '../build/static/js',
    rollupOptions: {
      output: {
        // no hashes—always `bundle.js`
        entryFileNames: 'quiz.js',
        chunkFileNames: 'chunk-[name].js',
        assetFileNames: '[name].[ext]'
      }
    }
  }
})
