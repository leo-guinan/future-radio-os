# ADR 0001: Start with a modular monolith and durable workers

Status: accepted for the first implementation

## Decision

Build the first Future Radio OS as a modular monolith with background workers and explicit module boundaries. Keep core operations functional on one machine before introducing distributed services.

## Rationale

The primary unknown is whether a mission can become a verified reusable solution. Microservices would add deployment and consistency failure modes before that loop is proven.

## Consequences

The event model, contracts, idempotency, and module interfaces must be designed for later extraction. The first implementation may use one process and local persistence, but it must not hide authority, evidence, or lifecycle transitions in process memory.

## Revisit when

A measured workload or availability requirement demonstrates that a specific module needs independent scaling or isolation. The burden is evidence, not architectural fashion.
