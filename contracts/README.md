# Versioned contracts

The Python models in `src/future_radio_os/contracts.py` are the canonical validation boundary for the first implementation. Each contract requires `schema_version: 1`, stable IDs, and provenance with one of `planned`, `estimated`, `modeled`, `verified`, or `unknown` status.

`contract_schema_manifest()` exports JSON Schema-compatible definitions for tooling. Readers must reject unknown future schema versions. Additive changes require a new version or an explicitly documented compatible-field policy; readers must not silently reinterpret existing fields.

The fixtures in `contracts/fixtures/` are synthetic and safe. They demonstrate shape and validation only; they are not evidence of a real mission, participant, deployment, cost, or outcome.
