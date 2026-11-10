# JUWEL adapter evidence spike

Reference checked: https://juwel.ai/developers.md

The documented boundary is a scoped `jak_` agent key, capability-filtered MCP/direct-tool/CLI interfaces, and human approval nonces for effectful calls. The adapter therefore:

- accepts an endpoint, scoped key, and explicit scopes;
- discovers capabilities through an injected transport;
- normalizes request ID, output, cost, latency, scope, and status;
- returns `unsupported` instead of pretending an absent scope is available;
- requires an approval nonce for effectful calls;
- redacts the key from representations and never places it in receipts.

The tests use a deterministic fake transport. No live JUWEL credential or effectful call was performed in this issue. The remaining live verification is to configure a scoped key outside the repository, run one read-only capability discovery, and preserve its request receipt without committing the key.
