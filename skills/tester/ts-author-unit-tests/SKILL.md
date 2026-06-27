---
name: ts-author-unit-tests
description: Write unit tests for the components (structure, fixtures, negative cases).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python]
---

# ts-author-unit-tests

## WHO
tester.

## WHEN
- The testing plan is ready (`ts-read-dod`).

## STEPS
1. For each component, write unit tests in `product/<component>/tests/` (pytest for Python, the framework's test runner for Next.js).
2. Cover: the happy path per api-contract, negative cases (validation/errors), edge values of the data-model fields.
3. Prepare fixtures/mocks for external dependencies; tests are deterministic and isolated.

## OUTPUT
- A set of unit tests next to the components.

## NEXT
- `ts-run-tests`.

## LIMITS
- Tests do NOT change product code. I do not weaken checks to fit the current implementation.
