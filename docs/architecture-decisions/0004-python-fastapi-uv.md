# ADR 0004: Python/FastAPI with uv for the first local runtime

Status: accepted for M0

## Decision

Use Python 3.11, FastAPI, Uvicorn, pytest, and uv for the first local runtime. Keep the initial service dependency-light and expose a small HTTP API before adding durable storage or workers.

## Rationale

The domain model, evidence tooling, adapters, and media orchestration are expected to use Python libraries. FastAPI provides typed HTTP boundaries and a testable application factory; Uvicorn provides a conventional local process. uv gives a reproducible lock/sync path and avoids depending on globally installed packages.

## Rejected alternatives

- TypeScript/Fastify: viable, but would split the first implementation across ecosystems before the mission/evidence loop exists.
- Poetry: familiar, but uv is faster and provides a single environment/sync workflow for this repository.
- PostgreSQL in M0: reserved for the event-journal issue; adding a database service before the health/bootstrap boundary would obscure the first failure modes.
- Docker Compose in M0: useful later for multi-service parity, but not required to prove the local runtime.

## Consequences

The first runtime is not production deployment, durable persistence, or a commitment that all future modules remain Python. Storage and worker boundaries remain explicit so they can be replaced or extracted when measurements justify it.

## Verification

`./scripts/bootstrap`, `./scripts/doctor`, and `env -u PYTHONPATH .venv/bin/python -m pytest tests -q` are the initial local gates.
