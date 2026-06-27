# Demo project: notes_api

A test "product", as if it were built by the Hermes agent (`developer`), plus an immutable
DoD evaluator (`tester`/`evaluator`). It's needed to manually verify that Hermes, from the
OpenShell sandbox, can: `build` an image on the VPS daemon, bring up a container, run a check, and tear it down.

## Structure
```
notes_api/
  app/                 # component (edited by the agent)
    main.py            #   FastAPI in-memory notes CRUD
    requirements.txt
    Dockerfile
  eval/                # IMMUTABLE (the agent doesn't touch it)
    dod.json           #   criteria + threshold
    dod.md             #   human-readable DoD
    dod_eval.py        #   evaluator: hits the service, prints a JSON verdict
    Dockerfile
  docker-compose.yml   # sandbox: app + eval on an internal network, no ports exposed
```

## Run (one evaluation cycle)
```bash
cd demo/notes_api

# bring up the component + run the DoD; the exit code == the eval verdict
docker compose -p hab_demo_s1 up --build --abort-on-container-exit --exit-code-from eval

# view the verdict (the eval container prints JSON in the logs above):
#   verdict=keep, pass_rate=1.0  -> green path

# tear down the sandbox
docker compose -p hab_demo_s1 down -v
```

Exit codes: `0` = keep (pass_rate >= threshold), `1` = rollback, `2` = service didn't come up.

## Testing a "failure" (for the rollback branch)
Break the component — for example, in `app/main.py` return `{"status": "bad"}` from `/health` —
rebuild and run again: eval should give `verdict=rollback`, exit code `1`.
This is the very fork at which inner_loop reverts to the git snapshot.

## Running the component on its own (manual poke)
```bash
cd demo/notes_api/app
docker build -t notes_api:dev .
docker run --rm -p 8000:8000 notes_api:dev
# in another terminal:
curl localhost:8000/health
curl -X POST localhost:8000/notes -H 'content-type: application/json' -d '{"title":"hi","body":"yo"}'
curl localhost:8000/notes
```
