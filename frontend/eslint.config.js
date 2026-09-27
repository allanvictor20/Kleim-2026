// Shared flat config for every app and package. `pnpm lint` runs this from each
// workspace member, which is what the CI `frontend` job calls.
import js from '@eslint/js';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import globals from 'globals';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  {
    // Globs, not bare names: `dist` alone would miss apps/*/dist and lint the
    // build output.
    ignores: [
      '**/dist/**',
      '**/coverage/**',
      '**/playwright-report/**',
      '**/test-results/**',
      '**/generated/**',
      '**/node_modules/**',
    ],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      globals: globals.browser,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
      // UI/UX Style Guide section 4: components use tokens; a raw hex in
      // component code fails review, so make the linter say so first.
      'no-restricted-syntax': [
        'error',
        {
          selector: 'Literal[value=/#[0-9a-fA-F]{3,8}\\b/]',
          message:
            'Use a design token from @kleim/ui tokens.css, not a raw hex colour (UI/UX Style Guide section 4).',
        },
      ],
    },
  },
  {
    // The token file and its tests are where the hex values legitimately live.
    files: ['packages/ui/src/tokens.ts', '**/*.test.{ts,tsx}', 'e2e/**'],
    rules: { 'no-restricted-syntax': 'off' },
  },
);
