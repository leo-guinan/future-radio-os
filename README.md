# Future Radio OS

Future Radio OS is a local-first orchestration system for turning bounded problems into verified solutions, reusable capabilities, and evidence-backed media.

The first release is deliberately smaller than the long-term station: a modular monolith with durable workers that can execute one mission end to end and preserve enough context for a second session to reuse the result.

## Primary invariant

Every solved problem should make future problems easier to solve.

## First vertical slice

1. Create a mission with a problem, goal, budget, permissions, and acceptance tests.
2. Persist structured events and reconstruct mission state after restart.
3. Load versioned world/canon context without reconstructing it from chat history.
4. Execute bounded tasks and record artifacts, costs, and verification evidence.
5. Register the verified result as a reusable solution.
6. Demonstrate reuse from a fresh session.

Media production, broadcast, participation, economics, and external adapters follow this substrate. They do not precede it.

## Repository map

- `ARCHITECTURE.md` — system boundaries and first implementation shape
- `AGENTS.md` — implementation rules for humans and coding agents
- `docs/product-spec.md` — source product specification
- `docs/roadmap.md` — staged build plan and issue mapping
- `docs/architecture-decisions/` — decisions that should not be re-litigated by every task
- `contracts/` — versioned machine-readable boundaries
- `missions/` — example mission definitions
- `tests/` — contract and integration coverage as implementation begins

## Status

Architecture baseline only. No production readiness, adapter support, broadcast availability, or economic result is claimed yet.

## Working rule

Ship one independently testable slice at a time. Preserve failures, distinguish planned from verified outcomes, and make every consequential claim traceable to an artifact or test.
