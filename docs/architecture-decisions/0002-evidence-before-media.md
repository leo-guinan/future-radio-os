# ADR 0002: Build the evidence substrate before automatic documentary production

Status: accepted for the first implementation

## Decision

Implement durable events, artifacts, verification, and provenance before automatic episode generation or broadcast.

## Rationale

A documentary generated without inspectable evidence can make activity look like progress. Media is an output of verified work, not the system's source of truth.

## Consequences

Early milestones will look less glamorous. Episode generation must consume approved events and expose source links for factual claims. Failed experiments remain valuable evidence but cannot be labeled successful resolutions.
