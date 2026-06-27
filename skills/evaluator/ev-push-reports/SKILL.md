---
name: ev-push-reports
description: Upload reports/ to MinIO hermes-reports/ and update the kanban.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# ev-push-reports

## WHO
evaluator.

## WHEN
- The environment is cleaned, `reports/` remains (`ev-cleanup`).

## STEPS
1. `minio-artifacts`: upload `reports/*` to `hermes-reports/hab_<tweetid>/s<sprint>.md` (and the accompanying `test_*.md`).
2. Record the MinIO key(s) in the eval task's kanban field.
3. Close the eval task (`done`) with the final verdict → a signal to orchestrator_sprint.

## OUTPUT
- `reports/` in MinIO `hermes-reports/`; keys in the kanban; eval task `done`.

## NEXT
- orchestrator_sprint (`os-decide-next`) executes the verdict; on stop/keep → orchestrator_global.

## LIMITS
- MinIO keys are not published externally (only presigned by the sales agent). The reports are the only thing that survives the sprint.
