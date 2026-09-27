# admin app

Admin, operations and finance console: approvals, moderation, exceptions, config, payouts, audit (M9, M10).

Created in M0 with Vite + React + TypeScript (`pnpm create vite@latest . --template react-ts`). Dev server port: 5176.

Folder conventions:

- `src/routes/` screens
- `src/features/<module>/` hooks and components per backend module
- `src/lib/` app-specific helpers

Use shared UI from `@kleim/ui` and the generated API client from `@kleim/api-client` only.
