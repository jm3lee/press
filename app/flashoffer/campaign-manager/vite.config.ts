/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { resolve as resolvePath, sep } from "node:path";
import { fileURLToPath, URL } from "node:url";
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

const toPosixPath = (value: string) => value.split(sep).join("/");

const projectRoot = fileURLToPath(new URL("./", import.meta.url));
const flashofferSource = fileURLToPath(
  new URL("../flashoffer-react/src/index.ts", import.meta.url),
);
const nodeModulesDir = resolvePath(projectRoot, "node_modules");
const materialBase = toPosixPath(resolvePath(nodeModulesDir, "@mui/material"));
const muiUtilsBase = toPosixPath(resolvePath(nodeModulesDir, "@mui/utils"));

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiBase = env.VITE_FLASHOFFER_CAMPAIGN_MANAGER_API_BASE?.trim();
  const proxyTarget = apiBase ? apiBase.replace(/\/$/, "") : undefined;

  const proxyConfig =
    proxyTarget !== undefined
      ? {
          "/api": {
            target: proxyTarget,
            changeOrigin: true,
          },
        }
      : undefined;

  return {
    plugins: [react()],
    resolve: {
      alias: [
        { find: "flashoffer-react", replacement: flashofferSource },
        { find: /^@mui\/material$/i, replacement: `${materialBase}/index.js` },
        { find: /^@mui\/material\/(.*)$/i, replacement: `${materialBase}/$1` },
        { find: /^@mui\/utils$/i, replacement: `${muiUtilsBase}/index.js` },
        { find: /^@mui\/utils\/(.*)$/i, replacement: `${muiUtilsBase}/$1` },
      ],
    },
    server: {
      port: 5174,
      proxy: proxyConfig,
    },
    preview: {
      port: 5174,
      proxy: proxyConfig,
    },
    build: {
      outDir: "dist",
      sourcemap: true,
    },
  };
});
