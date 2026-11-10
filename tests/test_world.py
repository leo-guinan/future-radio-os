from pathlib import Path

import pytest

from future_radio_os.world import WorldContextError, WorldContextLoader


def write_world(root: Path, *, invariants: list[dict] | None = None) -> None:
    (root / "future-radio").mkdir(parents=True, exist_ok=True)
    rows = invariants or [
        {
            "id": "canon.title",
            "description": "The world has the expected title",
            "field": "title",
            "equals": "Future Radio",
        }
    ]
    lines = [
        "id: future-radio",
        "version: 1.0.0",
        "sources:",
        "  - docs/product-spec.md",
        "invariants:",
    ]
    for invariant in rows:
        lines.extend(
            [
                f"  - id: {invariant['id']}",
                f"    description: {invariant['description']}",
                f"    field: {invariant['field']}",
                f"    equals: {invariant['equals']}",
            ]
        )
    (root / "future-radio" / "world.yaml").write_text("\n".join(lines) + "\n")


def test_loader_retrieves_versioned_context_with_sources(tmp_path: Path):
    write_world(tmp_path)

    context = WorldContextLoader(tmp_path).load("future-radio", "1.0.0")

    assert context.world_id == "future-radio"
    assert context.version == "1.0.0"
    assert context.sources == ["docs/product-spec.md"]
    assert context.invariants[0].id == "canon.title"


def test_invariant_validation_reports_pass_and_fail(tmp_path: Path):
    write_world(tmp_path)
    context = WorldContextLoader(tmp_path).load("future-radio", "1.0.0")

    assert context.validate({"title": "Future Radio"}).passed == ["canon.title"]
    failed = context.validate({"title": "Other Radio"})
    assert failed.failed == ["canon.title"]
    assert failed.status == "failed"


def test_missing_world_and_contradictory_invariants_fail_closed(tmp_path: Path):
    loader = WorldContextLoader(tmp_path)
    with pytest.raises(WorldContextError, match="not found"):
        loader.load("future-radio", "1.0.0")

    write_world(
        tmp_path,
        invariants=[
            {"id": "title-a", "description": "first", "field": "title", "equals": "A"},
            {"id": "title-b", "description": "second", "field": "title", "equals": "B"},
        ],
    )
    with pytest.raises(WorldContextError, match="contradictory"):
        loader.load("future-radio", "1.0.0")


def test_loader_rejects_wrong_version_and_duplicate_invariant_ids(tmp_path: Path):
    write_world(tmp_path)
    loader = WorldContextLoader(tmp_path)
    with pytest.raises(WorldContextError, match="version"):
        loader.load("future-radio", "2.0.0")

    write_world(
        tmp_path,
        invariants=[
            {"id": "same", "description": "first", "field": "a", "equals": "A"},
            {"id": "same", "description": "second", "field": "b", "equals": "B"},
        ],
    )
    with pytest.raises(WorldContextError, match="duplicate"):
        loader.load("future-radio", "1.0.0")
