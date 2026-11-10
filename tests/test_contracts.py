import pytest
from pydantic import ValidationError

from future_radio_os.contracts import (
    ArtifactContract,
    MissionContract,
    SolutionContract,
    validate_contract,
)


def provenance(status: str = "verified") -> dict:
    return {"status": status, "source_ids": ["source://test"]}


def mission_payload() -> dict:
    return {
        "id": "mission-001",
        "schema_version": 1,
        "problem_id": "problem-001",
        "goal": "Make a reproducible local build",
        "acceptance_tests": ["bootstrap_passes", "restart_reconstructs"],
        "budget": {"human_minutes_max": 60, "compute_usd_max": 10},
        "status": "proposed",
        "provenance": provenance("planned"),
    }


def test_valid_mission_contract_is_deterministic_and_versioned():
    first = validate_contract("mission", mission_payload())
    second = validate_contract("mission", mission_payload())

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert first.schema_version == 1
    assert first.acceptance_tests == ["bootstrap_passes", "restart_reconstructs"]


def test_mission_without_acceptance_tests_is_rejected():
    payload = mission_payload()
    payload["acceptance_tests"] = []

    with pytest.raises(ValidationError, match="acceptance_tests"):
        validate_contract("mission", payload)


def test_unknown_status_and_extra_fields_are_rejected():
    payload = mission_payload()
    payload["provenance"] = provenance("cash_received")
    with pytest.raises(ValidationError, match="status"):
        validate_contract("mission", payload)

    payload = mission_payload()
    payload["unreviewed_field"] = "ambiguous"
    with pytest.raises(ValidationError, match="unreviewed_field"):
        validate_contract("mission", payload)


def test_solution_requires_evidence_and_limitations():
    solution = SolutionContract(
        id="solution-001",
        schema_version=1,
        problem_signature="local-bootstrap",
        assumptions=["python-3.11"],
        procedure=["run scripts/bootstrap"],
        dependencies=["fastapi"],
        tests=["pytest tests"],
        evidence_ids=["evidence-001"],
        limitations=["storage remains local"],
        status="solved",
        provenance=provenance(),
    )
    assert solution.evidence_ids == ["evidence-001"]
    assert solution.limitations == ["storage remains local"]


def test_artifact_hash_and_provenance_are_required():
    artifact = ArtifactContract(
        id="artifact-001",
        schema_version=1,
        kind="document",
        content_hash="sha256:abc123",
        source_event_ids=["evt-001"],
        provenance=provenance(),
    )
    assert artifact.content_hash.startswith("sha256:")

    with pytest.raises(ValidationError, match="content_hash"):
        ArtifactContract(
            id="artifact-002",
            schema_version=1,
            kind="document",
            content_hash="",
            source_event_ids=["evt-001"],
            provenance=provenance(),
        )
