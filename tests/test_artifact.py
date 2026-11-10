import hashlib
from pathlib import Path

import pytest

from future_radio_os.artifact import ArtifactRegistry, ArtifactRegistryError
from future_radio_os.contracts import ArtifactContract


def artifact() -> ArtifactContract:
    return ArtifactContract(
        id="artifact-001",
        schema_version=1,
        kind="build",
        content_hash="sha256:" + hashlib.sha256(b"build").hexdigest(),
        source_event_ids=["evt-001"],
        status="local",
        provenance={"status": "verified", "source_ids": ["evt-001"]},
    )


def test_artifact_identity_and_provenance_survive_registry_restart(tmp_path: Path):
    path = tmp_path / "artifacts.sqlite3"
    first = ArtifactRegistry(path)
    first.register(artifact(), content=b"build")
    first.close()

    second = ArtifactRegistry(path)
    loaded = second.get("artifact-001")
    assert loaded.content_hash == artifact().content_hash
    assert loaded.status == "local"
    assert loaded.source_event_ids == ["evt-001"]
    second.close()


def test_hash_mismatch_and_missing_provenance_block_registration(tmp_path: Path):
    registry = ArtifactRegistry(tmp_path / "artifacts.sqlite3")
    with pytest.raises(ArtifactRegistryError, match="hash"):
        registry.register(artifact(), content=b"tampered")

    unverified = ArtifactContract.model_validate(
        {**artifact().model_dump(), "provenance": {"status": "planned", "source_ids": ["evt-001"]}}
    )
    with pytest.raises(ArtifactRegistryError, match="provenance"):
        registry.register(unverified, content=b"build")
    registry.close()


def test_promotion_requires_evidence_and_health_readback(tmp_path: Path):
    registry = ArtifactRegistry(tmp_path / "artifacts.sqlite3")
    registry.register(artifact(), content=b"build")

    with pytest.raises(ArtifactRegistryError, match="evidence"):
        registry.promote("artifact-001", "validated")
    registry.promote("artifact-001", "validated", evidence_ids=["test-001"])
    registry.promote("artifact-001", "staged", evidence_ids=["deploy-001"])
    registry.promote("artifact-001", "deployed", evidence_ids=["deploy-002"])
    with pytest.raises(ArtifactRegistryError, match="health"):
        registry.promote("artifact-001", "running", evidence_ids=["health-001"], health_ok=False)
    registry.promote("artifact-001", "running", evidence_ids=["health-001"], health_ok=True)
    assert registry.get("artifact-001").status == "running"
    registry.close()


def test_illegal_lifecycle_transition_is_rejected(tmp_path: Path):
    registry = ArtifactRegistry(tmp_path / "artifacts.sqlite3")
    registry.register(artifact(), content=b"build")
    with pytest.raises(ArtifactRegistryError, match="cannot transition"):
        registry.promote("artifact-001", "deployed", evidence_ids=["e"])
    registry.close()
