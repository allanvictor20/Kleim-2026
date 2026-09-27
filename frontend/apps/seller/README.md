# seller app

Seller app: store setup, products and stock, order queue, payouts (M2, M5, M9, M11).

Created in M0 with Vite + React + TypeScript (`pnpm create vite@latest . --template react-ts`). Dev server port: 5174.

Folder conventions:

- `src/routes/` screens
- `src/features/<module>/` hooks and components per backend module
- `src/lib/` app-specific helpers

Use shared UI from `@kleim/ui` and the generated API client from `@kleim/api-client` only.
