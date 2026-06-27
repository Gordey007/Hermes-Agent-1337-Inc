---
name: offer-publish
description: Sell a finished project to a client — one call DMs the payment + download links to the client and announces it with a quote-tweet.
version: 2.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [bash]
---

# offer-publish

## WHO
sales.

## WHEN
- Project is built in `/sandbox/projects/<project>` and you need to invoice the client.

## STEPS
1. Run ONE call (replace `<project>` with the dir name):
   ```bash
   curl -s -X POST http://127.0.0.1:8000/offer -H 'Content-Type: application/json' -d '{"project": "2070653124969193883"}'
   ```
   That's it. This single request does everything:
   - creates the payment + download links,
   - **DMs both links to the client automatically**,
   - **posts the quote-tweet announcement**.

   You do NOT need to forward the links anywhere — the client already has them in DM.

## OUTPUT
```json
{
  "payment_url": "https://checkout.stripe.com/c/pay/cs_test_...",
  "download_url": "https://aicoursebuilder1337test1.work/d/cs_test_...",
  "dm": { "dm_event_id": "...", "dm_conversation_id": "..." },
  "quote_tweet": { "id": "...", "text": "..." }
}
```

## LIMITS
- `download_url` is inactive until payment is confirmed; valid 3 min after activation, re-openable.
- The project must exist in `/sandbox/projects/<project>`.
