---
name: ts-run-tests
description: Bring up the stack (docker-sandbox), run the unit tests, collect logs.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python, docker]
---

# ts-run-tests

## WHEN
- The unit tests are written (`ts-author-unit-tests`).

## WHO
tester.

## STEPS
1. `docker-sandbox`: bring up the stack `-p hab_<tweetid>_s<sprint>` (if it is not up).
2. Run each component's unit tests in its container; collect pass/fail + logs.
3. Capture a summary: how many passed/failed, which components, brief reasons for the failures.

## OUTPUT
- Unit run results (pass/fail + logs) in an internal note.

## NEXT
- `ts-run-dod`.

## LIMITS
- I do not fix code on failure — only record it. The run is in isolation (sandbox) and is not published externally.
