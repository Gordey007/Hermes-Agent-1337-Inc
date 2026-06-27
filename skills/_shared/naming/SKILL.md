---
name: naming
description: Generate a correct name (task/container/directory/MinIO key) via naming.py.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# naming

## WHO
All profiles — before creating any named entity.

## WHEN
- Before creating a kanban task, a docker project/container, a working directory, or a MinIO key.

## STEPS
Module: `infra/naming.py` (prefix `hab`). Never assemble names by hand.

1. `python -c "from infra.naming import task_id; print(task_id(tweet_id, sprint, role, seq))"`
   → `hab-<tweetid>-s<sprint>-<role>-<seq>`.
2. `docker_project(tweet_id, sprint)` → `hab_<tweetid>_s<sprint>` (for `docker compose -p`).
3. `container_name(tweet_id, sprint, component)` → `hab_<tweetid>_s<sprint>_<component>`.
4. `work_dir(tweet_id, sprint)` → `/sandbox/work/hab_<tweetid>/s<sprint>/`.
5. `minio_artifact_key(...)` / `minio_report_key(...)` — bucket keys.

## OUTPUT
- A name string ready to use in kanban/docker/MinIO/filesystem.

## NEXT
- Name obtained → I create the entity with the corresponding skill (`kanban-write`/`docker-sandbox`/`minio-artifacts`).

## LIMITS
- `<tweetid>` is the last 7 digits of tweet_id (short form). A naming mismatch breaks monitoring — do not deviate.
