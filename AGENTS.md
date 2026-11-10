# Future Radio OS — Agent Instructions

## Mission

Build a local-first system that coordinates bounded work, preserves evidence, and makes verified solutions reusable.

## Rules

1. Load canonical repository data instead of reconstructing context from chat history.
2. Search the Solution Registry before implementing a new solution.
3. Keep planned, estimated, modeled, and verified outcomes separate.
4. Preserve provenance for consequential actions, artifacts, model calls, and decisions.
5. Use existing production repositories through versioned adapters; do not duplicate their logic.
6. Require explicit authorization for publishing, spending, external outreach, and canon changes.
7. Prefer the smallest local implementation that can be tested and later promoted.
8. Write negative tests for safety and authority boundaries.
9. Preserve failures and document limitations.
10. Do not call an artifact deployed, a mission resolved, or a capability verified without independent evidence.

## First deliverable

Implement the persistent event journal, mission and solution contracts, world-invariant loading, a minimal bounded execution contract, and one end-to-end restart/reuse test before building broadcast infrastructure.

## Definition of done

A task is complete when its contract is documented, tests pass, evidence is recorded, relevant events persist, another session can reuse the result, and the change explains what changed and why.
