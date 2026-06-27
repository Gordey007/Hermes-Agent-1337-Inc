# Definition of Done — notes_api

The `notes_api` component is a REST notes service. Immutable (only the `developer` agent edits the component itself, not the DoD).

## Criteria (metric = pass_rate = passed / total, threshold = 1.0)

1. **health** — `GET /health` → `200`, body `{"status": "ok"}`.
2. **create** — `POST /notes` with `{title, body}` → `201`, an integer `id` in the response.
3. **get** — `GET /notes/{id}` → `200`, body matches what was created.
4. **list** — `GET /notes` → `200`, the list contains the created note.
5. **delete** — `DELETE /notes/{id}` → `204`, a subsequent `GET /notes/{id}` → `404`.
6. **not_found** — `GET /notes/999999` → `404`.

Verdict: `keep` if `pass_rate >= threshold` and the metric didn't drop relative to the previous iteration; otherwise `rollback`.
