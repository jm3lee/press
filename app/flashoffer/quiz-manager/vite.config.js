import { resolve as resolvePath, sep } from 'node:path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath, URL } from 'node:url';

function toPosixPath(value) {
  return value.split(sep).join('/');
}

const PROJECT_ROOT = fileURLToPath(new URL('./', import.meta.url));

const NODE_MODULES_DIR = resolvePath(PROJECT_ROOT, 'node_modules');
const MATERIAL_BASE = toPosixPath(resolvePath(NODE_MODULES_DIR, '@mui/material'));
const MUI_UTILS_BASE = toPosixPath(resolvePath(NODE_MODULES_DIR, '@mui/utils'));

const FLASHOFFER_SOURCE = fileURLToPath(
  new URL('../flashoffer-react/src/index.ts', import.meta.url),
);

const CANVAS_CONFETTI_MODULE = toPosixPath(
  resolvePath(NODE_MODULES_DIR, 'canvas-confetti', 'dist', 'confetti.module.mjs'),
);

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: [
      {
        find: 'flashoffer-react',
        replacement: FLASHOFFER_SOURCE,
      },
      {
        find: /^canvas-confetti$/,
        replacement: CANVAS_CONFETTI_MODULE,
      },
      {
        find: /^@mui\/material$/i,
        replacement: `${MATERIAL_BASE}/index.js`,
      },
      {
        find: /^@mui\/material\/(.*)$/i,
        replacement: `${MATERIAL_BASE}/$1`,
      },
      {
        find: /^@mui\/utils$/i,
        replacement: `${MUI_UTILS_BASE}/index.js`,
      },
      {
        find: /^@mui\/utils\/(.*)$/i,
        replacement: `${MUI_UTILS_BASE}/$1`,
      },
    ],
  },
});
