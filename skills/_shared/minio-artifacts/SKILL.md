---
name: minio-artifacts
description: Upload an artifact/report to MinIO and issue a temporary presigned link with a TTL.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
    requires_tools: [minio_client]
---

# minio-artifacts

## WHO
orchestrator_global (artifacts), evaluator (reports), sales (presigned delivery).

## WHEN
- Sprint `done` → upload `product/` to `hermes-artifacts`.
- Sprint finished → upload `reports/` to `hermes-reports`.
- Payment confirmed → presigned link to the buyer.

## STEPS
CLI: `python 02_sales_pipeline/minio_client.py`. Buckets: `hermes-artifacts`, `hermes-reports`.

1. Product artifact:
   `minio_client.py upload <work>/product hermes-artifacts hab_<tweetid>/v<outer>/` (recursively).
2. Reports: `minio_client.py upload <work>/reports hermes-reports hab_<tweetid>/s<sprint>.md`.
3. Presigned (ONLY after payment): `minio_client.py presign hermes-artifacts <key> --ttl 24` → URL.

## OUTPUT
- A MinIO key (per `naming.py`) to write into `leads.dev_artifact`/kanban; a presigned URL with a TTL.

## NEXT
- Artifact uploaded → `og-handoff-sales`. Reports uploaded → `ev-push-reports` updates kanban.
- Presigned issued → `sl-deliver` sends the link via x.com.

## LIMITS
- Issue presigned links ONLY after `reply_status='done'` (paid). TTL per `MINIO_PRESIGN_TTL_HOURS` (24).
