---
name: ar-api-contract
description: Write design/api-contract.md (endpoints, methods, request/response schemas).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# ar-api-contract

## WHO
architect.

## WHEN
- `design/data-model.md` is ready.

## STEPS
1. For each frontend↔backend interaction, describe the endpoint: method, path, parameters, request/response schema, error codes.
2. Build the schemas strictly from the fields in `data-model.md` (names match — end-to-end contract).
3. Write `design/api-contract.md`.

## OUTPUT
- `design/api-contract.md`.

## NEXT
- `ar-component-spec`.

## LIMITS
- Fields in the schemas = data-model fields (no renaming). Only the endpoints needed for the DoD.
