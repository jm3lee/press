/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { resolve as resolvePath, sep } from 'node:path';
import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolveProxyConfig } from './config/proxy.js';

const proxyConfig = resolveProxyConfig();
const toPosixPath = (value) => value.split(sep).join('/');
const projectRoot = fileURLToPath(new URL('./', import.meta.url));
const nodeModulesDir = resolvePath(projectRoot, 'node_modules');
const materialBase = toPosixPath(resolvePath(nodeModulesDir, '@mui/material'));
const muiUtilsBase = toPosixPath(resolvePath(nodeModulesDir, '@mui/utils'));
const canvasConfettiModule = toPosixPath(
  resolvePath(nodeModulesDir, 'canvas-confetti', 'dist', 'confetti.module.mjs')
);
const flashofferSource = fileURLToPath(
  new URL('../flashoffer-react/src/index.ts', import.meta.url)
);

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: [
      {
        find: 'flashoffer-react',
        replacement: flashofferSource
      },
      {
        find: /^canvas-confetti$/,
        replacement: canvasConfettiModule
      },
      {
        find: /^@mui\/material$/i,
        replacement: `${materialBase}/index.js`
      },
      {
        find: /^@mui\/material\/(.*)$/i,
        replacement: `${materialBase}/$1`
      },
      {
        find: /^@mui\/utils$/i,
        replacement: `${muiUtilsBase}/index.js`
      },
      {
        find: /^@mui\/utils\/(.*)$/i,
        replacement: `${muiUtilsBase}/$1`
      }
    ]
  },
  server: {
    host: '0.0.0.0',
    port: 5175,
    proxy: proxyConfig
  },
  preview: {
    proxy: proxyConfig
  }
});
