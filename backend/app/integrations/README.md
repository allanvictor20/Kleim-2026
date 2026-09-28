# integrations (M0)

Every external service is reached through a `Protocol` with a fake
implementation for development and tests (NFR-10). Nothing outside this package
imports a vendor SDK.

Each package has the same three files:

- `interface.py` — the `Protocol` the rest of the app depends on.
- `fake.py` — the development and test implementation. Records what it was asked
  to do so tests can assert on it.
- `factory.py` — picks the implementation from settings, and fails loudly rather
  than silently falling back to the fake.

Real adapters land in the module that needs them: Africa's Talking in M1,
Cloudinary in M2, the payment aggregator in M6, Firebase Cloud Messaging in M8.
