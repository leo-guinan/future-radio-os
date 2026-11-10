# Future Radio OS Architecture

Version 0.1 — architecture baseline

## Boundary

Future Radio OS is an orchestration repository. Existing production, animation, world-lens, writers-room, and media repositories remain independent systems accessed through versioned adapters. This repository owns mission coordination, evidence, provenance, reusable solutions, policy boundaries, and lifecycle state.

The first implementation is a modular monolith plus durable workers. It must run locally before any distributed deployment is attempted.

## Core flow

Human intention
→ resolve known problems and solutions
→ load canonical context and policy
→ propose a bounded plan
→ estimate dependencies and cost
→ obtain required approval
→ execute tasks
→ record events and artifacts
→ verify acceptance tests
→ register or update a solution
→ optionally produce an evidence-backed episode

## Core modules

- Core domain: stable IDs, versioned entities, state transitions, and invariants.
- Knowledge kernel: world/canon, problems, solutions, capabilities, temporal queries, provenance.
- Mission engine: mission contracts, tasks, dependencies, claims, verification, and completion.
- Event recorder: append-only events with actor, timestamps, correlation, inputs, outputs, verification, and cost.
- HumAIn director: bounded session goals, budgets, permissions, approval requests, and stop conditions.
- Artifact registry: content-addressed metadata for code, documents, media, datasets, and builds.
- Worker runtime: restartable jobs, retries, checkpoints, idempotency, and durable outcomes.
- Adapters: Juwel, Bend, production tools, GitHub, publishing, and payments; each must expose capabilities and evidence.
- Studio API/UI: Past, Present, and Future projections over shared state.

## Source of truth

Versioned canonical data, structured durable storage, and an append-only event journal are authoritative. Chat history is not a source of truth. Derived projections may be rebuilt from events and durable records.

Every temporal record should preserve occurrence time and recording time. Fictional/story time remains separate from real-world time.

## State models

Mission: `proposed → ready → active → verifying → resolved`.

Exceptional states: `blocked`, `failed`, `cancelled`, `reopened`.

Artifact lifecycle: `local → validated → staged → deployed → running`, with `degraded`, `stopped`, and `retired` states.

No state transition to `resolved`, `deployed`, or `running` is implied by an agent message or an upload command. It requires the relevant verification evidence.

## Evidence and integrity

Consequential actions produce structured events. Corrections use compensating events; history is not silently overwritten. Inputs and outputs are referenced by stable artifact IDs and hashes where applicable. Planned, estimated, modeled, and verified values remain distinct.

A solution is reusable only when its problem signature, assumptions, dependencies, procedure, tests, evidence, limitations, and maintenance status are recorded.

## Safety boundary

Agents may propose actions, but authority comes from permission-checked APIs and explicit session policy. External text, audience comments, or model output cannot widen authority. Publishing, spending, external outreach, credential use, and canon changes require explicit policy/approval gates.

Credentials and private data never enter event logs, recordings, public artifacts, or generated media. Untrusted code and contributed artifacts require constrained execution.

## Deliberate non-goals

No new Linux distribution, general AGI, foundation-model training, whole-internet index, fully autonomous financial agent, or 24/7 original-video generation in the first version.

## Initial technical bias

Use one core language and simple interfaces; prefer a relational database with object-storage abstraction and a durable queue. PostgreSQL/pgvector, local filesystem storage, a web studio, FFmpeg, structured logs, OpenTelemetry, and container/systemd deployment are candidates—not commitments—until the first implementation issues establish evidence.
