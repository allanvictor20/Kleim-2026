# rider app

Rider PWA: availability, offers, pickup and drop-off with codes, earnings (M7–M9). See ADR-010.

Created in M0 with Vite + React + TypeScript (`pnpm create vite@latest . --template react-ts`). Dev server port: 5175.

Folder conventions:

- `src/routes/` screens
- `src/features/<module>/` hooks and components per backend module
- `src/lib/` app-specific helpers

Use shared UI from `@kleim/ui` and the generated API client from `@kleim/api-client` only.
