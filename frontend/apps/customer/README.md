# customer app

Customer app: home, search, product, checkout, tracking, orders, profile (M1, M3–M8, M11). Reference: docs/design/screens/.

Created in M0 with Vite + React + TypeScript (`pnpm create vite@latest . --template react-ts`). Dev server port: 5173.

Folder conventions:

- `src/routes/` screens
- `src/features/<module>/` hooks and components per backend module
- `src/lib/` app-specific helpers

Use shared UI from `@kleim/ui` and the generated API client from `@kleim/api-client` only.
