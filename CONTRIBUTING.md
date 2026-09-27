# Contributing

How the team works on this repository. Read this once before your first pull request. It applies the Implementation Plan (sections 3 and 6) to daily work.

## 1. Work flows from modules to issues

1. Each module (M0–M13) is a GitHub milestone. Its tasks are issues labelled `m<id>` (for example `m5`).
2. Every issue states its acceptance criteria, the SDD references and the owner.
3. Pick issues only from the current module unless the team lead agrees otherwise.

## 2. Contract first (gate G1)

Before writing endpoint code:

1. Add or change the paths and schemas in `docs/api/openapi.yaml`.
2. Open a pull request titled `contract: m<id> <feature>`; one backend and one frontend developer review it.
3. After merging, regenerate the TypeScript client. Frontend work can start against the mock server (`pnpm mock`).

## 3. Branches and commits

- Branch from `main`: `m<id>/<short-name>`, for example `m5/seller-timeout` or `m3/typo-search`.
- Keep branches short-lived (ideally under three days).
- Commit messages follow Conventional Commits:

```
feat(orders): expire unanswered orders after seller window
fix(pricing): round delivery fee to nearest UGX 500
test(ledger): add partial-return reconciliation case
docs(adr): add ADR-013 for review moderation
```

## 4. Pull requests (gate G2)

Open a pull request early as a draft. Before requesting review, tick the checklist:

- [ ] Linked to its issue; acceptance criteria met.
- [ ] Tests added for new logic; CI green (lint, types, tests, migration up/down).
- [ ] No business logic in routers; modules do not import other modules’ models or repositories.
- [ ] Authorisation checked for every new endpoint, with a forbidden-case test.
- [ ] Migration included for schema changes, with a working downgrade.
- [ ] Money changes use integer UGX and post balanced ledger entries (from M9).
- [ ] New states added to the state machine and history.
- [ ] UI uses tokens and shared components; loading, empty, error and offline states done.
- [ ] Screenshots or a short recording attached for UI changes (light and dark theme).
- [ ] No secrets, personal data or real phone numbers in code, tests or screenshots.

Rules:

- One approving review is required; the backend lead must also approve changes to state machines, pricing or the ledger.
- The author merges after approval using **squash and merge**.
- Review within one working day. Comments are about the code, and each suggestion says why.

## 5. Coding standards

### Backend (Python)

- Formatting and linting with Ruff; type checking with mypy in strict mode for `core`, `orders`, `payments`, `pricing`, `ledger`.
- Module layout: `router.py`, `schemas.py`, `models.py`, `repository.py`, `service.py`, `events.py`, `tests/`.
- Raise domain errors from `app.core.errors` with a code from the API Specification catalogue; never return ad-hoc error bodies.
- Use the shared state-machine helper for any status change; never assign `status` directly.
- Time: use `app.core.clock.now()` (UTC) so tests can control time.

### Frontend (TypeScript)

- ESLint + Prettier; TypeScript strict mode.
- Server state with TanStack Query; local state with React state or Zustand. No `localStorage` for anything sensitive.
- Import UI only from `packages/ui`; no raw hex colours or pixel values outside tokens.
- Every screen follows the UI/UX Style Guide copy rules and status wording.

## 6. Testing expectations

| Area | Minimum |
| --- | --- |
| Pricing, state machines, ranking, ledger | 90% line coverage, table-driven tests |
| Other services | 70% line coverage |
| Every endpoint | Success, validation error, unauthorised and forbidden cases |
| Background jobs | Tested with a controlled clock |
| UI | Component tests for shared components; Playwright for the core order flow |

Run the full suite locally before asking for review: `docker compose exec api pytest && pnpm test`.

## 7. Definition of done

A task is done when the pull request checklist is complete and merged. A module is done when every exit criterion in the Implementation Plan is met, the demo is recorded and gate G3 is signed off by someone other than the module owner.

## 8. Decisions and changes

- A significant technical choice gets an ADR in `docs/adr/` (copy `000-template.md`).
- A change to scope, data, states or APIs follows SDD change control: propose, get approval from the team lead and backend lead, update the SDD, then the plan, then issues.

## 9. Security and privacy

- Report a vulnerability privately to the team lead; do not open a public issue.
- Use fake data in development. Never copy production data to a laptop.
- Customer phone numbers and addresses must not appear in logs; use the logging helper that masks them.

## 10. Communication

| Channel | Use |
| --- | --- |
| GitHub issues and pull requests | All technical discussion that affects code |
| Team chat | Quick questions, standup notes |
| Weekly planning (Monday) | Confirm the week’s module tasks |
| Standup (three times a week) | Done, next, blocked |
| Module demo | End of each module |
