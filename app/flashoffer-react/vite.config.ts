import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import dts from "vite-plugin-dts";
import path from "node:path";

export default defineConfig({
  plugins: [
    react(),
    dts({
      entryRoot: "src",
      outDir: "dist/types",
      tsconfigPath: "./tsconfig.json",
      rollupTypes: true
    })
  ],
  build: {
    lib: {
      entry: path.resolve(__dirname, "src/index.ts"),
      name: "FlashofferReact",
      formats: ["es", "cjs"],
      fileName: (format) =>
        `flashoffer-react.${format === "es" ? "es" : "cjs"}.js`
    },
    rollupOptions: {
      external: [
        "react",
        "react-dom",
        "@mui/material",
        "@emotion/react",
        "@emotion/styled"
      ],
      output: {
        globals: {
          react: "React",
          "react-dom": "ReactDOM",
          "@mui/material": "MaterialUI",
          "@emotion/react": "EmotionReact",
          "@emotion/styled": "EmotionStyled"
        }
      }
    },
    sourcemap: true,
    emptyOutDir: true
  }
});
