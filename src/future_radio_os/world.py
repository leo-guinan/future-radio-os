from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class WorldContextError(ValueError):
    """Raised when versioned world context is absent or internally unsafe."""


@dataclass(frozen=True)
class InvariantResult:
    passed: list[str]
    failed: list[str]

    @property
    def status(self) -> str:
        return "passed" if not self.failed else "failed"


@dataclass(frozen=True)
class WorldInvariant:
    id: str
    description: str
    field: str
    expected: Any


@dataclass(frozen=True)
class WorldContext:
    world_id: str
    version: str
    sources: list[str]
    invariants: list[WorldInvariant]

    def validate(self, state: dict[str, Any]) -> InvariantResult:
        passed: list[str] = []
        failed: list[str] = []
        for invariant in self.invariants:
            if state.get(invariant.field) == invariant.expected:
                passed.append(invariant.id)
            else:
                failed.append(invariant.id)
        return InvariantResult(passed=passed, failed=failed)


class WorldContextLoader:
    def __init__(self, root: str | Path):
        self.root = Path(root)

    def load(self, world_id: str, version: str) -> WorldContext:
        path = self.root / world_id / "world.yaml"
        if not path.is_file():
            raise WorldContextError(f"world {world_id!r} not found at {path}")
        try:
            raw = yaml.safe_load(path.read_text())
        except yaml.YAMLError as exc:
            raise WorldContextError(f"world {world_id!r} has invalid YAML") from exc
        if not isinstance(raw, dict):
            raise WorldContextError("world manifest must be an object")
        if raw.get("id") != world_id:
            raise WorldContextError("world manifest id does not match requested world")
        if raw.get("version") != version:
            raise WorldContextError(
                f"world version {raw.get('version')!r} does not match requested version {version!r}"
            )
        sources = raw.get("sources")
        if not isinstance(sources, list) or not sources or any(
            not isinstance(source, str) or not source.strip() for source in sources
        ):
            raise WorldContextError("world sources must be a non-empty list")
        invariants = self._parse_invariants(raw.get("invariants"))
        self._reject_contradictions(invariants)
        return WorldContext(
            world_id=world_id,
            version=version,
            sources=list(sources),
            invariants=invariants,
        )

    @staticmethod
    def _parse_invariants(raw: Any) -> list[WorldInvariant]:
        if not isinstance(raw, list) or not raw:
            raise WorldContextError("world invariants must be a non-empty list")
        parsed: list[WorldInvariant] = []
        ids: set[str] = set()
        for item in raw:
            if not isinstance(item, dict):
                raise WorldContextError("each invariant must be an object")
            required = ("id", "description", "field", "equals")
            if any(not isinstance(item.get(key), str) or not item[key].strip() for key in required):
                raise WorldContextError("each invariant needs id, description, field, and equals")
            if item["id"] in ids:
                raise WorldContextError(f"duplicate invariant id {item['id']!r}")
            ids.add(item["id"])
            parsed.append(
                WorldInvariant(
                    id=item["id"],
                    description=item["description"],
                    field=item["field"],
                    expected=item["equals"],
                )
            )
        return parsed

    @staticmethod
    def _reject_contradictions(invariants: list[WorldInvariant]) -> None:
        expected_by_field: dict[str, Any] = {}
        for invariant in invariants:
            if invariant.field in expected_by_field and expected_by_field[invariant.field] != invariant.expected:
                raise WorldContextError(
                    f"contradictory invariants for field {invariant.field!r}"
                )
            expected_by_field[invariant.field] = invariant.expected
