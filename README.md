# Future Radio OS

Future Radio OS is a local-first orchestration system for turning bounded problems into verified solutions, reusable capabilities, and evidence-backed media.

The system is deliberately smaller than the long-term station: a modular monolith with durable workers and explicit authority boundaries. It preserves what happened, what was verified, what remains unknown, and what can be reused in a later session.

Primary invariant: every solved problem should make future problems easier to solve.

## What is implemented

The initial architecture queue is complete. GitHub issues #1–#16 are closed with code, tests, verification output, and documented residual limitations.

- Runtime bootstrap with Python 3.11, FastAPI, Uvicorn, and uv
- Append-only SQLite event journal with restart reconstruction, corrections, UTC normalization, and legacy timestamp reads
- Strict versioned contracts for problems, missions, tasks, evidence, solutions, capabilities, artifacts, and session policies
- Versioned Future Radio world context with source references, invariants, and contradiction checks
- Mission/task lifecycle with claims, dependencies, bounded completion, evidence, failure preservation, and reopening
- Durable Solution Registry with provenance, environment/assumption matching, reuse, and supersession
- Bounded execution policy with tool, environment, data, time, compute, revocation, and approval gates
- Artifact identity, provenance, lifecycle promotion, and health-gated running status
- Scoped JUWEL adapter boundary with capability discovery, unsupported-capability receipts, approval nonces, timeout handling, and key redaction
- Pinned Bend 2.0.40 workload with a preserved execution receipt and explicit formal-verdict limitation
- Evidence-backed episode rendering from mission-scoped events, including failed outcomes and privacy rejection
- Media library eligibility rules, scheduling, fallback playout, health state, and playback receipts
- Bounded external participation flow with eligibility, claims, evidence submission, review, completion, and payment states
- Evidence-backed temporal graph with confidence, provenance, as-of projections, and falsifiable hypotheses
- Mission-attributed financial ledger with Decimal amounts, explicit units, provenance, quote-to-earned states, provider readback, and incremental cost
- Read-only Past/Present/Future studio projection with JSON and HTML views, source links, and explicit status distinctions

## Repository map

- `ARCHITECTURE.md` — system boundaries and first implementation shape
- `AGENTS.md` — implementation rules for humans and coding agents
- `docs/product-spec.md` — source product specification
- `docs/roadmap.md` — staged build plan and issue mapping
- `docs/architecture-decisions/` — decisions that should not be re-litigated by every task
- `docs/chromebook-usb.md` — Chromebook Linux/USB setup and boundaries
- `scripts/chromebook-usb` — portable prepare, doctor, test, and run launcher
- `contracts/` — versioned machine-readable boundaries and fixtures
- `worlds/future-radio/world.yaml` — canonical world context fixture
- `experiments/bend/` — pinned Bend workload and execution receipt
- `src/future_radio_os/` — runtime, persistence, policy, media, graph, ledger, and studio modules
- `tests/` — contract, safety, persistence, integration, and API read-path coverage

## Run locally

Requirements: macOS/Linux, Python 3.11, and [uv](https://docs.astral.sh/uv/).

```bash
./scripts/bootstrap
./scripts/doctor
env -u PYTHONPATH .venv/bin/future-radio-os --host 127.0.0.1 --port 8000
```

For a Chromebook Linux container with the repository stored on a USB stick, use:

```bash
./scripts/chromebook-usb prepare
./scripts/chromebook-usb doctor
./scripts/chromebook-usb run
```

See [`docs/chromebook-usb.md`](docs/chromebook-usb.md) for the ChromeOS Linux setup, USB sharing, architecture boundaries, and safe-removal procedure.

The local API exposes:

- `GET /health` — process health
- `GET /ready` — readiness checks
- `GET /studio` — Past/Present/Future JSON read model
- `GET /studio/view` — minimal HTML operator view

The default server binds to `127.0.0.1`. External publishing, spending, outreach, and other effectful actions remain outside the local read path and require explicit authorization.

## Verify

Run the complete suite from the repository root:

```bash
env -u PYTHONPATH .venv/bin/python -m pytest tests -q
ruff check src tests
env -u PYTHONPATH .venv/bin/python -m compileall -q src tests
git diff --check
```

The current suite contains 66 passing tests. The test environment emits an existing Starlette/httpx deprecation warning; it does not fail the suite.

## Evidence and safety posture

Every consequential boundary is designed to fail closed:

- Planned, estimated, modeled, unknown, and verified states are distinct.
- Credentials and private data are rejected from episode content and redacted from adapter representations.
- Event timestamps are timezone-aware for new writes and ordered by parsed UTC instants.
- Financial amounts must be finite, provenance-backed, and unit-consistent per mission.
- Studio source links allow only approved schemes and validated HTTP(S) authorities.
- Media cannot play unless approval, rights, and expiry checks pass.
- A provider receipt must be independently read back before revenue becomes received.
- Low-confidence graph relationships remain hypotheses and require evidence plus a falsifier.

## Current limitations

This is a verified architecture baseline, not a production station:

- The studio read model is currently an in-memory projection seeded by callers; event-journal projection wiring is the next persistence step.
- Episode output is evidence-backed HTML, not native video or broadcast media.
- The JUWEL adapter is a scoped boundary with test transport; no live credentialed provider call is claimed.
- The Bend workload computes its result, but Bend's formal `--verdict` path remains blocked by the installed Lean version mismatch; the receipt preserves that miss.
- The ledger records and verifies financial state but does not connect to a payment provider.
- Media scheduling and participation are local modules, not deployed public services.

## Working rule

Ship one independently testable slice at a time. Preserve failures, distinguish planned from verified outcomes, and make every consequential claim traceable to an artifact, source record, or test.
