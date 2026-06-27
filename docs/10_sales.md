# 10 — Sales Funnel

The `sales` profile on the global-loop side. Cron `0 * * * *`. One step per lead per run (anti-ban/focus).

## Funnel
```
dev_status='done', dev_artifact=<minio-key>
        │  og-handoff-sales
        ▼
sl-build-offer  ── a personal offer from the tweet text + what was built (reports/final.md)
        ▼
sl-send-x       ── quote_tweet / send_dm (x_actions.py); offer_sent=1, reply_status='no_reply'
        ▼
sl-stripe-invoice ── Stripe payment link (TEST key sk_test_ ONLY)
        ▼
sl-dialog       ── low-pressure dialog (≤1 touch/lead/day, cooldown by updated_at)
        ▼
sl-analyze-reply ── reply_status: positive / negative / no_reply + reply_summary
        ▼
sl-deliver      ── after confirmed payment → presigned MinIO (short TTL); reply_status='done'
```

## Stripe (CRITICAL)
- The autonomous pipeline uses **ONLY** `STRIPE_API_KEY_TEST` (`sk_test_...`).
- It is **FORBIDDEN** to use a live key (`rk_live_`/`sk_live_`).
- Keys are NEVER logged or sent out.
- Implementation: `02_sales_pipeline/stripe_offer.py` on top of `stripe-link-cli`.

## MinIO presigned (delivery)
- The artifact lives in `hermes-artifacts/hab_<tweetid>/v<outer>/`.
- ONLY a presigned URL with a short TTL is handed out, and ONLY after payment.
- A permanent key is never handed out. Implementation: `02_sales_pipeline/minio_client.py`.

## Anti-ban
- ≤1 touch/lead/day, cooldown by `updated_at`.
- Don't send the same text en masse, keep a soft tone, respect X's rate-limit.
