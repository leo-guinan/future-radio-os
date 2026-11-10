import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from future_radio_os.contracts import SolutionContract


class SolutionRegistryError(ValueError):
    """Raised when a solution cannot be registered or reused safely."""


@dataclass(frozen=True)
class AssumptionMismatch:
    message: str


@dataclass(frozen=True)
class SolutionMatch:
    solution: SolutionContract
    reusable: bool
    mismatches: list[AssumptionMismatch]


class SolutionRegistry:
    """Durable registry of versioned, evidence-backed reusable solutions."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS solutions (
                solution_id TEXT NOT NULL,
                version TEXT NOT NULL,
                problem_signature TEXT NOT NULL,
                status TEXT NOT NULL,
                environments_json TEXT NOT NULL,
                assumptions_json TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                mission_id TEXT NOT NULL,
                PRIMARY KEY (solution_id, version)
            )
            """
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_solutions_problem ON solutions(problem_signature)"
        )
        self._connection.commit()

    def register(
        self,
        solution: SolutionContract,
        *,
        mission_id: str,
        allow_non_solved: bool = False,
    ) -> None:
        if not mission_id.strip():
            raise SolutionRegistryError("mission_id is required")
        if solution.provenance.status != "verified":
            raise SolutionRegistryError("solution registration requires verified provenance")
        if solution.status != "solved" and not allow_non_solved:
            raise SolutionRegistryError("only solved solutions can be registered for reuse")
        existing = self._connection.execute(
            "SELECT 1 FROM solutions WHERE solution_id = ? AND version = ?",
            (solution.id, solution.version),
        ).fetchone()
        if existing:
            raise SolutionRegistryError(
                f"solution {solution.id!r} version {solution.version!r} already registered"
            )
        if mission_id not in solution.affected_missions:
            solution = solution.model_copy(
                update={"affected_missions": [*solution.affected_missions, mission_id]}
            )
        self._connection.execute(
            """
            INSERT INTO solutions (
                solution_id, version, problem_signature, status,
                environments_json, assumptions_json, payload_json, mission_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                solution.id,
                solution.version,
                solution.problem_signature,
                solution.status,
                _json(solution.environments),
                _json(solution.assumptions),
                solution.model_dump_json(),
                mission_id,
            ),
        )
        self._connection.commit()

    def lookup(
        self,
        problem_signature: str,
        *,
        environment: str | None = None,
        assumptions: list[str] | None = None,
    ) -> list[SolutionMatch]:
        rows = self._connection.execute(
            """
            SELECT payload_json FROM solutions
            WHERE problem_signature = ? AND status = 'solved'
            ORDER BY solution_id, version
            """,
            (problem_signature,),
        ).fetchall()
        requested_assumptions = set(assumptions or [])
        matches: list[SolutionMatch] = []
        for row in rows:
            solution = SolutionContract.model_validate_json(row["payload_json"])
            mismatches: list[AssumptionMismatch] = []
            if environment is not None and environment not in solution.environments:
                mismatches.append(
                    AssumptionMismatch(
                        f"environment {environment!r} is not supported; expected one of {solution.environments!r}"
                    )
                )
            required = set(solution.assumptions)
            if required != requested_assumptions:
                mismatches.append(
                    AssumptionMismatch(
                        f"assumptions differ; expected {sorted(required)!r}, received {sorted(requested_assumptions)!r}"
                    )
                )
            matches.append(
                SolutionMatch(solution=solution, reusable=not mismatches, mismatches=mismatches)
            )
        return matches

    def list_status(self, status: str) -> list[SolutionMatch]:
        rows = self._connection.execute(
            "SELECT payload_json FROM solutions WHERE status = ? ORDER BY solution_id, version",
            (status,),
        ).fetchall()
        return [
            SolutionMatch(
                solution=SolutionContract.model_validate_json(row["payload_json"]),
                reusable=False,
                mismatches=[],
            )
            for row in rows
        ]

    def close(self) -> None:
        self._connection.close()


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))
