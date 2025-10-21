/**
 * ESLint configuration for the Flashoffer React component library.
 */
module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2023,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true
    }
  },
  env: {
    browser: true,
    es2023: true,
    node: true
  },
  ignorePatterns: ['dist/', 'coverage/', 'node_modules/'],
  plugins: ['@typescript-eslint'],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended'
  ],
  rules: {
    complexity: ['error', { max: 10 }],
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-explicit-any': 'off'
  },
  overrides: [
    {
      files: ['test/**/*.{ts,tsx}', '**/*.test.{ts,tsx}'],
      env: {
        jest: true
      }
    }
  ]
};
