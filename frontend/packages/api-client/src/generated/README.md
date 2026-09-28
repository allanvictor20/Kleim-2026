# Generated code

`schema.d.ts` is generated from `docs/api/openapi.yaml`:

    pnpm --filter @kleim/api-client generate

It is committed so that a clone can typecheck and CI can run without a
generation step, and so that a contract change shows up as a reviewable diff
here alongside the change to `openapi.yaml` (gate G1). Never edit it by hand —
the next `generate` will overwrite the change.
