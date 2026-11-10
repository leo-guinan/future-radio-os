from pathlib import Path

import pytest

from future_radio_os.contracts import SolutionContract
from future_radio_os.solution_registry import (
    AssumptionMismatch,
    SolutionRegistry,
    SolutionRegistryError,
)


def solution(*, status: str = "solved", assumptions: list[str] | None = None) -> SolutionContract:
    return SolutionContract(
        id="solution-001",
        version="1.0.0",
        schema_version=1,
        problem_signature="local-bootstrap",
        assumptions=assumptions or ["python-3.11", "uv-installed"],
        environments=["local"],
        procedure=["run scripts/bootstrap"],
        dependencies=["fastapi"],
        tests=["pytest tests"],
        evidence_ids=["evidence-001"],
        limitations=["local only"],
        status=status,
        maintenance_status="active",
        affected_missions=["mission-001"],
        provenance={"status": "verified", "source_ids": ["evt-001"]},
    )


def test_verified_solution_survives_fresh_registry_session(tmp_path: Path):
    path = tmp_path / "solutions.sqlite3"
    first = SolutionRegistry(path)
    first.register(solution(), mission_id="mission-001")
    first.close()

    second = SolutionRegistry(path)
    matches = second.lookup("local-bootstrap", environment="local", assumptions=["python-3.11", "uv-installed"])

    assert len(matches) == 1
    assert matches[0].solution.id == "solution-001"
    assert matches[0].solution.version == "1.0.0"
    assert matches[0].reusable is True
    assert matches[0].mismatches == []
    second.close()


def test_assumption_mismatch_is_visible_and_blocks_reuse(tmp_path: Path):
    registry = SolutionRegistry(tmp_path / "solutions.sqlite3")
    registry.register(solution(), mission_id="mission-001")

    matches = registry.lookup("local-bootstrap", environment="local", assumptions=["python-3.12"])

    assert len(matches) == 1
    assert matches[0].reusable is False
    assert isinstance(matches[0].mismatches[0], AssumptionMismatch)
    assert "python-3.12" in matches[0].mismatches[0].message
    registry.close()


def test_registry_rejects_unverified_or_duplicate_versions(tmp_path: Path):
    registry = SolutionRegistry(tmp_path / "solutions.sqlite3")
    unverified = SolutionContract.model_validate(
        {**solution().model_dump(), "provenance": {"status": "planned", "source_ids": ["evt-001"]}}
    )
    with pytest.raises(SolutionRegistryError, match="verified"):
        registry.register(unverified, mission_id="mission-001")

    registry.register(solution(), mission_id="mission-001")
    with pytest.raises(SolutionRegistryError, match="already registered"):
        registry.register(solution(), mission_id="mission-001")
    registry.close()


def test_registry_preserves_solution_statuses_and_filters_superseded(tmp_path: Path):
    registry = SolutionRegistry(tmp_path / "solutions.sqlite3")
    registry.register(solution(), mission_id="mission-001")
    superseded = solution().model_copy(
        update={"id": "solution-002", "status": "superseded"}
    )
    registry.register(superseded, mission_id="mission-002", allow_non_solved=True)

    matches = registry.lookup("local-bootstrap", environment="local", assumptions=["python-3.11", "uv-installed"])
    assert [match.solution.id for match in matches] == ["solution-001"]
    assert registry.list_status("superseded")[0].solution.id == "solution-002"
    registry.close()
