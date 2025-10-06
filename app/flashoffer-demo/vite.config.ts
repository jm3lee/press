import { resolve as resolvePath, sep } from "node:path";
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const toPosixPath = (value: string) => value.split(sep).join("/");

const projectRoot = fileURLToPath(new URL("./", import.meta.url));
const flashofferSource = fileURLToPath(
  new URL("../flashoffer-react/src/index.ts", import.meta.url)
);
const nodeModulesDir = resolvePath(projectRoot, "node_modules");
const compatLegacyRadio = toPosixPath(
  resolvePath(projectRoot, "src/compat/material-ui/Radio.tsx")
);
const materialBase = toPosixPath(
  resolvePath(nodeModulesDir, "@mui/material")
);
const muiUtilsBase = toPosixPath(resolvePath(nodeModulesDir, "@mui/utils"));

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: [
      {
        find: "flashoffer-react",
        replacement: flashofferSource
      },
      {
        find: "@material-ui/core/Radio",
        replacement: compatLegacyRadio
      },
      {
        find: "@material-ui/core/Radio/Radio",
        replacement: compatLegacyRadio
      },
      {
        find: "@material-ui/core/Radio/index",
        replacement: compatLegacyRadio
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
  build: {
    outDir: "../build/static/js",
    emptyOutDir: false,
    rollupOptions: {
      output: {
        entryFileNames: "flashoffer-demo.js",
        chunkFileNames: "chunk-[name].js",
        assetFileNames: "[name].[ext]"
      }
    }
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/setupTests.ts",
    css: true
  }
});
