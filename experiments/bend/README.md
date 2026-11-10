# Bend workload evidence

Pinned compiler: Bend 2.0.40 (`v2.0.40`). Source: `sum.bend` computes the sum of `[1, 2, 3, 4]` using recursive pattern matching.

Run the reproducible workload:

```sh
BEND_NO_TELEMETRY=1 python experiments/bend/run_workload.py
```

The script runs the installed Bend compiler and a conventional Python implementation over the same fixed input, then writes a JSON receipt when `--receipt` is supplied. The equivalence law is `bend_output == conventional_output == 10`.

The basic Bend check/run passed locally and returned `10`. `--verdict` was also attempted but is currently blocked because Bend 2.0.40 requires a Lean 4.34.0 BendTT kernel and this machine has Lean 4.31.0. This is preserved as a limitation, not relabeled as a proof pass.

Bend 2 limitations relevant to this adapter: no built-in HTTP/JSON/TLS library, no general test framework, one C output per program, and F32 facts are not provable. This issue does not claim formal proof, GPU performance, or multi-machine execution.
