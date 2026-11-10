import hashlib
import sqlite3
from pathlib import Path

from future_radio_os.contracts import ArtifactContract


class ArtifactRegistryError(ValueError):
    """Raised when an artifact identity or lifecycle claim is unsafe."""


class ArtifactRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY,
                content_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                evidence_json TEXT NOT NULL
            )
            """
        )
        self._connection.commit()

    def register(self, artifact: ArtifactContract, *, content: bytes | None = None) -> None:
        if artifact.provenance.status != "verified":
            raise ArtifactRegistryError("artifact provenance must be verified")
        if content is not None:
            actual = "sha256:" + hashlib.sha256(content).hexdigest()
            if actual != artifact.content_hash:
                raise ArtifactRegistryError(
                    f"content hash mismatch: expected {artifact.content_hash}, got {actual}"
                )
        if self._connection.execute(
            "SELECT 1 FROM artifacts WHERE artifact_id = ?", (artifact.id,)
        ).fetchone():
            raise ArtifactRegistryError(f"artifact {artifact.id!r} already registered")
        self._connection.execute(
            "INSERT INTO artifacts VALUES (?, ?, ?, ?, ?)",
            (artifact.id, artifact.content_hash, artifact.status, artifact.model_dump_json(), "[]"),
        )
        self._connection.commit()

    def get(self, artifact_id: str) -> ArtifactContract:
        row = self._connection.execute(
            "SELECT payload_json FROM artifacts WHERE artifact_id = ?", (artifact_id,)
        ).fetchone()
        if row is None:
            raise KeyError(artifact_id)
        return ArtifactContract.model_validate_json(row["payload_json"])

    def promote(
        self,
        artifact_id: str,
        target: str,
        *,
        evidence_ids: list[str] | None = None,
        health_ok: bool | None = None,
    ) -> ArtifactContract:
        artifact = self.get(artifact_id)
        if not evidence_ids:
            raise ArtifactRegistryError("promotion requires evidence")
        transitions = {
            "local": {"validated"},
            "validated": {"staged"},
            "staged": {"deployed"},
            "deployed": {"running"},
            "running": {"degraded", "stopped", "retired"},
            "degraded": {"running", "stopped", "retired"},
            "stopped": {"running", "retired"},
            "retired": set(),
        }
        if target not in transitions.get(artifact.status, set()):
            raise ArtifactRegistryError(
                f"cannot transition {artifact.status!r} to {target!r}"
            )
        if target == "running" and health_ok is not True:
            raise ArtifactRegistryError("running requires a positive health readback")
        updated = artifact.model_copy(update={"status": target})
        self._connection.execute(
            "UPDATE artifacts SET status = ?, payload_json = ?, evidence_json = ? WHERE artifact_id = ?",
            (target, updated.model_dump_json(), _json(evidence_ids), artifact_id),
        )
        self._connection.commit()
        return updated

    def close(self) -> None:
        self._connection.close()


def _json(values: list[str]) -> str:
    import json

    return json.dumps(values, sort_keys=True, separators=(",", ":"))
