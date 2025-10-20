import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolveProxyConfig } from './config/proxy.js';

const proxyConfig = resolveProxyConfig();

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5175,
    proxy: proxyConfig
  },
  preview: {
    proxy: proxyConfig
  }
});
