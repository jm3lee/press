import js from "@eslint/js";
import pluginReactHooks from "eslint-plugin-react-hooks";
import pluginReactRefresh from "eslint-plugin-react-refresh";
import pluginReact from "eslint-plugin-react";
import globals from "globals";

const baseRules = {
  ...js.configs.recommended.rules,
  complexity: ["error", { max: 10 }]
};

export default [
  {
    ignores: ["dist/**", "coverage/**", "node_modules/**"]
  },
  {
    files: ["**/*.{js,jsx}"],
    languageOptions: {
      parserOptions: {
        ecmaVersion: 2023,
        sourceType: "module",
        ecmaFeatures: {
          jsx: true
        }
      },
      globals: {
        ...globals.browser,
        ...globals.es2023,
        ...globals.node
      }
    },
    plugins: {
      react: pluginReact,
      "react-hooks": pluginReactHooks,
      "react-refresh": pluginReactRefresh
    },
    settings: {
      react: {
        version: "detect"
      }
    },
    rules: {
      ...baseRules,
      "react/jsx-uses-react": "off",
      "react/jsx-uses-vars": "error",
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true }
      ]
    }
  },
  {
    files: ["config/**/*.js", "vite.config.js"],
    languageOptions: {
      globals: {
        ...globals.node,
        ...globals.es2023
      }
    }
  }
];
