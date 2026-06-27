# Immutable eval container: stdlib only, hits the service from dod.json.
FROM python:3.12-slim
WORKDIR /eval
COPY dod.json dod.md dod_eval.py ./
CMD ["python", "dod_eval.py"]
