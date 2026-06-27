# Security Policy

This project is an **autonomous agent that handles money and live credentials**. The rules below
are not optional — they are part of the architecture and the host (L0) agent enforces them at
bootstrap and at runtime.

## Secrets

- **Never commit real credentials.** Secrets live only in a local `.env` (copied from
  `env.example`), which is git-ignored. `env.example` holds placeholders only.
- **Never log keys.** Skills and tools print compact JSON results; tokens must never appear in
  stdout, logs, kanban, `reports/`, or `memory/lessons.jsonl`. Lessons store short, generalizable
  notes — never secrets, tokens, or full file contents.
- **Never send secrets to an external service.** The cleaning/research tools fetch *public* URLs;
  no credential is ever attached to an outbound request beyond the specific API it authenticates.

## Stripe

- The autonomous pipeline uses the **TEST** key (`STRIPE_API_KEY_TEST`, `sk_test_…`) **only**.
- The **live** key (`rk_live_…`) is **forbidden on the VPS**. It must not be present in any `.env`,
  config, or environment the agent can read.
- Stripe actions are limited to creating invoices / payment links and reading their status. The
  agent does not move money on a human's behalf beyond issuing the test invoice.

## Required tokens (placeholders in `env.example`)

| Variable | Used by | Scope |
|---|---|---|
| `X_BEARER_TOKEN` | `01_x_lead/` tweet search, `sales` outreach | read + post within anti-ban limits |
| `GITHUB_TOKEN` | `skills/tools/gh_search/` | public repo/code search only |
| `NVIDIA_API_KEY` | model inference (NemoHermes / DSPy) | inference only |
| `STRIPE_API_KEY_TEST` | `02_sales_pipeline/` | **test** invoices only |
| MinIO access/secret | `infra/` MinIO + presigned delivery | scoped to `hermes-*` buckets |

## Network policy (OpenShell)

Each profile gets the **minimum** network reach it needs, applied at bootstrap:

- `researcher` → `github.com`, `raw.githubusercontent.com`, official-docs domains.
- `sales` → `api.stripe.com`, `x.com`.
- product sandboxes run in an **isolated docker network**; outbound access is denied by default.
- delivery is via **presigned MinIO URLs with a short TTL**, never by exposing the bucket.

## Reporting

This is a hackathon project. If you find a credential leak in the git history or a policy gap,
**rotate the affected credential immediately** and open an issue describing the gap (without
including the secret). Treat any key that has ever touched git history as compromised and rotate it.
