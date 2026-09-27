# @kleim/ui

Shared design system: tokens and components defined in the UI/UX Style Guide (docs/design). Components not listed there need team agreement before being added.

## Tokens

`src/tokens.css` is the single source of colour, type, spacing and radius (Style
Guide §4). Import it once per app, before any component:

```css
@import 'tailwindcss';
@import '@kleim/ui/tokens.css';
@source '../../../packages/ui/src';   /* so Tailwind sees these components */
```

Tailwind v4 reads its palette, fonts, radii and breakpoints from the `@theme`
block in that same file, so the tokens are declared once rather than mirrored in
a JS config. **Components use tokens only** — a raw hex value in component code
fails ESLint, not just review.

Dark theme follows the device and can be forced with `data-theme="light"` or
`data-theme="dark"` on `<html>`; `ThemeProvider` manages both. Every screen is
checked in both themes before a module exits.

Plus Jakarta Sans is self-hosted (`src/assets/fonts/`, 27 KB latin subset, one
variable file covering weights 400–800) rather than fetched from Google Fonts:
NFR-07 caps the customer app's first load at 1.5 MB over 3G.

## Components

| Component | States built | Notes |
| --- | --- | --- |
| `Button` | default, hover, focus, pressed, loading, disabled | primary, dark, success, outline, text; min 50 px, 54 px for rider actions |
| `IconButton` | default, focus, with badge, disabled | 44 px round, `aria-label` required |
| `Chip`, `ChipRow` | default, selected | `aria-pressed`; single-line scroll row |
| `Tag` | — | neutral, blue, green, amber, pink; always carries a word |
| `Input` | default, focus, error, disabled | text, search, code; error text in Pink 700 |
| `Spinner`, `Skeleton` | — | the loading state every screen needs |
| `EmptyState` | — | heading, one sentence, one action |
| `Toast` | open, auto-dismiss | `role="status"`, 4 s, no buttons |
| `AppShell`, `AppHeader`, `BottomNav`, `Sidebar` | — | layout per Style Guide §4.4; router-agnostic, apps supply the link renderer |
| `ThemeProvider`, `useTheme` | — | device theme plus an override |
| `ErrorBoundary` | — | §7.3 copy; request id only under "Contact support" |
| `ComponentPreview` | — | the gallery at `/preview` in every app |

Still to come, with the module that first needs them: product card, size
selector, colour swatch, stepper, toggle switch, status timeline, code box,
countdown, bottom sheet (M2, M3, M5, M7). The Style Guide §5 table is the
checklist.

## Rules

A component is not done until every state in that table is built and visible in
the preview page, in both themes, with real `<button>`, `<a>` and `<input>`
elements, 44 × 44 px touch targets and 4.5:1 text contrast.
