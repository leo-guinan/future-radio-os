import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path


INPUT = [1, 2, 3, 4]
EXPECTED = 10
SOURCE = Path(__file__).with_name("sum.bend")
SOURCE_LABEL = "experiments/bend/sum.bend"


def find_bend() -> str:
    candidates = [os.environ.get("BEND_BIN", ""), str(Path.home() / ".bend/bin/bend"), "bend"]
    for candidate in candidates:
        if candidate and (Path(candidate).is_file() or candidate == "bend"):
            return candidate
    raise SystemExit("Bend 2.0.40 is not installed; set BEND_BIN or install the pinned compiler")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    bend = find_bend()
    version = subprocess.run([bend, "version"], check=True, capture_output=True, text=True).stdout.strip()
    if version != "bend 2.0.40":
        raise SystemExit(f"unexpected Bend version: {version!r}")
    started = time.perf_counter()
    result = subprocess.run(
        [bend, str(SOURCE)],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "BEND_NO_TELEMETRY": "1"},
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    bend_output = int(result.stdout.strip())
    conventional_output = sum(INPUT)
    receipt = {
        "status": "verified_local",
        "compiler": version,
        "source": SOURCE_LABEL,
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "input": INPUT,
        "bend_output": bend_output,
        "conventional_output": conventional_output,
        "equivalence_law": "bend_output == conventional_output == 10",
        "equivalent": bend_output == conventional_output == EXPECTED,
        "runtime_ms": elapsed_ms,
        "verdict": "not_run: requires Lean 4.34.0 BendTT kernel",
    }
    print(json.dumps(receipt, sort_keys=True))
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return 0 if receipt["equivalent"] else 1


if __name__ == "__main__":
    sys.exit(main())
