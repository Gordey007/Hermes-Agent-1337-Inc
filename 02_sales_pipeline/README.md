# 02_sales_pipeline — global orchestrator (cron) + sales

Hermes cron blueprint: **one step per lead per run** (anti-ban, focus). It connects lead
hunting (01) → team build (04+03) → artifact in MinIO → Stripe invoice → low-pressure
conversation on x.com → presigned delivery after payment.

## Files

| File | What | Skill |
|---|---|---|
| `api.py` | Payments + delivery API (Stripe Checkout + MinIO streaming) | `sl-stripe-invoice`, `sl-deliver` |
| `stripe_offer.py` | Stripe invoice (TEST key) + payment polling | `sl-stripe-invoice`, `sl-deliver` |
| `minio_client.py` | Upload artifacts/reports + presigned URL with TTL | `minio-artifacts`, `ev-push-reports` |
| `x_actions.py` | x.com write (`quote_tweet`/`send_dm`) | `sl-send-x` |

## Environment (provide keys via your own secret store — never commit them)

```bash
export LEADS_DB_PATH=/sandbox/x_lead/leads.db
export KANBAN_DB_PATH=/sandbox/kanban/tasks.db
# Stripe — TEST key ONLY for autonomous delivery
export STRIPE_API_KEY_TEST=sk_test_...
# MinIO
export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=...
export MINIO_SECRET_KEY=...
export MINIO_PRESIGN_TTL_HOURS=24
# x.com write
export X_USER_ACCESS_TOKEN=...   # OAuth2 PKCE, see x_actions.py / x_oauth2_pkce.py
```

> **SECURITY.** Every Stripe entry point refuses any key other than `sk_test_`. The live key
> (`rk_live_...`) is NOT used in the autonomous hackathon pipeline. Keys are never logged.

## Dependencies

```bash
uv pip install stripe boto3 flask        # plus the existing requests, python-dotenv
```

## Global orchestrator cron blueprint

Profile `orchestrator_global` (see [04_team/profiles/orchestrator_global](../04_team/profiles/orchestrator_global)).
A skill with `metadata.hermes.blueprint.schedule` — one funnel pass per run:

```
*/30 * * * *   # example; the real cadence lives in the profile blueprint
```

## Funnel steps (one lead per run)

1. **Qualify** (`og-qualify-lead`): `SELECT ... WHERE is_relevant=0 AND dev_status='pending'`
   → assess relevance → set `is_relevant`.
2. **Pick the simplest task** (`og-pick-task`): one lead → `dev_status='in_progress'`,
   first-pass DoD (`og-author-dod`), start the sprint (`og-start-sprint` → orchestrator_sprint → 04+03).
3. **Build** with the team of profiles (04) in isolation (03). Every step is a kanban task.
4. **Done** → artifacts to MinIO:
   ```bash
   python minio_client.py upload --dir --local .../product \
       --bucket hermes-artifacts --key hab_<tweetid>/v<outer>
   ```
   containers torn down (`down -v`), `dev_status='done'`, `dev_artifact=<minio-key>`.
5. **Handoff to sales** (`og-handoff-sales` → sales):
   ```bash
   python stripe_offer.py create --email <lead> --product "<name>" --amount 49 --desc "..."
   ```
   `offer_sent=1`, `reply_status='no_reply'`; offer → x.com (`sl-send-x`, `send_dm`/`quote_tweet`).
6. **Low-pressure conversation** (`sl-dialog`): ≤1 touch/lead/day, cooldown by `updated_at`,
   gentle tone; reply analysis (`sl-analyze-reply`) → `reply_status` `positive`/`negative` +
   `reply_summary`. Payment (`stripe_offer.py check`) → `reply_status='done'` + presigned:
   ```bash
   python minio_client.py presign --bucket hermes-artifacts --key hab_<tweetid>/v<outer>/<file>
   ```
7. **Failure** → `dev_status='failed'`, evaluator report to MinIO `hermes-reports/`, wait for
   the next day.

## OpenShell policies (network)

Allow outbound to: `api.stripe.com`, `api.twitter.com`/`api.x.com`, the MinIO endpoint.
Deny everything else. See [docs/10_sales.md](../docs/10_sales.md), [docs/11_infra.md](../docs/11_infra.md).

## x.com anti-ban

- ≤1 touch per lead per day (cooldown via `leads.updated_at`).
- Personal, tweet-relevant offer (not template spam); `send_dm` only if the recipient has
  opened DMs, otherwise `quote_tweet`.
- Daily volume is capped on the blueprint side (one lead per run).
