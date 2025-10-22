import { resolve as resolvePath, sep } from 'node:path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath, URL } from 'node:url';

const toPosixPath = (value) => value.split(sep).join('/');
const projectRoot = fileURLToPath(new URL('./', import.meta.url));

const nodeModulesDir = resolvePath(projectRoot, 'node_modules');
const materialBase = toPosixPath(resolvePath(nodeModulesDir, '@mui/material'));
const muiUtilsBase = toPosixPath(resolvePath(nodeModulesDir, '@mui/utils'));

const flashofferSource = fileURLToPath(
  new URL('../flashoffer-react/src/index.ts', import.meta.url),
);

const canvasConfettiModule = toPosixPath(
  resolvePath(nodeModulesDir, 'canvas-confetti', 'dist', 'confetti.module.mjs'),
);

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: [
      {
        find: 'flashoffer-react',
        replacement: flashofferSource,
      },
      {
        find: /^canvas-confetti$/,
        replacement: canvasConfettiModule,
      },
      {
        find: /^@mui\/material$/i,
        replacement: `${materialBase}/index.js`,
      },
      {
        find: /^@mui\/material\/(.*)$/i,
        replacement: `${materialBase}/$1`,
      },
      {
        find: /^@mui\/utils$/i,
        replacement: `${muiUtilsBase}/index.js`,
      },
      {
        find: /^@mui\/utils\/(.*)$/i,
        replacement: `${muiUtilsBase}/$1`,
      },
    ],
  },
});
