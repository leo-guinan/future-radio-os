# Implementation Roadmap

This roadmap turns the Future Radio OS specification into independently testable GitHub issues. Each issue should produce an artifact, a verification command, known limitations, and a falsifier.

## Sequence

### M0 — Boot and preserve history

Repository contracts, local persistence, append-only event journal, minimal API, restart reconstruction.

Gate: a recorded mission event survives process restart and is queryable by ID and time.

### M1 — Install the Future Radio world

Inventory existing repositories, extract canonical rules, load versioned world data, and validate invariants.

Gate: a fresh session retrieves rules with source references without chat-log reconstruction.

### M2 — Make missions executable

Mission/task state machine, bounded sessions, approvals, verification, and Solution Registry.

Gate: one mission reaches verified resolution and produces a reusable solution.

### M3 — Evidence-backed adapters

Juwel capability discovery and one documented call; pinned Bend sample with source, build, test, cost, and runtime receipts.

Gate: each adapter produces independently inspectable evidence, including unsupported-capability handling.

### M4 — Produce one episode

Select mission events, draft evidence-grounded script, validate claims/canon/privacy, and render a short segment.

Gate: a verified mission produces a playable segment with traceable source evidence.

### M5 — Deploy a small station

Media library, eligibility rules, scheduler, fallback playout, health checks, and standalone packaging.

Gate: approved media plays continuously and recovers from a failed segment.

### M6 — Distributed participation

Public mission pages, bounded claims, evidence submission, review, credits, and draft payment obligations.

Gate: an external participant completes one bounded task and the verified result updates the mission.

### M7 — Possibility engine

Temporal graph, evidence-backed connection hypotheses, uncertainty labels, and experiment ranking.

Gate: prior evidence produces a useful next mission without treating a missing edge as proof.

### M8 — Economic learning loop

Real expense/revenue records, mission attribution, and incremental cost/reuse measurement.

Gate: a completed mission reuses an earlier solution and reports its incremental cost accurately.

## Issue discipline

Work one issue at a time. Prefer dependency order. Do not start an issue whose acceptance test depends on an unverified parent. Close an issue only with linked code/docs, exact verification output, and residual limitations.
