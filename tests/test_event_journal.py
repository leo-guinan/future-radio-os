import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

from future_radio_os.event_journal import EventJournal, EventValidationError


def event(event_id: str, occurred_at: str, *, event_type: str = "mission.task.completed", correction_of: str | None = None) -> dict:
    return {
        "event_id": event_id,
        "schema_version": 1,
        "type": event_type,
        "occurred_at": occurred_at,
        "actor": {"kind": "agent", "id": "test-agent"},
        "correlation_id": "run-001",
        "inputs": ["artifact://input"],
        "outputs": ["artifact://output"],
        "verification": {"status": "passed", "evidence_ids": ["evidence-001"]},
        "cost": {"usd": 0.04},
        **({"correction_of": correction_of} if correction_of else {}),
    }


def test_event_survives_restart_and_is_queryable_by_id_and_time(tmp_path: Path):
    path = tmp_path / "events.sqlite3"
    first = EventJournal(path)
    first.append(event("evt-001", "2026-11-10T20:00:00Z"))
    first.close()

    reopened = EventJournal(path)
    loaded = reopened.get("evt-001")
    ordered = reopened.list_between("2026-11-10T19:00:00Z", "2026-11-10T21:00:00Z")

    assert loaded["event_id"] == "evt-001"
    assert loaded["actor"] == {"kind": "agent", "id": "test-agent"}
    assert loaded["verification"]["status"] == "passed"
    assert [item["event_id"] for item in ordered] == ["evt-001"]
    reopened.close()


def test_events_are_ordered_by_occurrence_then_recording_time(tmp_path: Path):
    journal = EventJournal(tmp_path / "events.sqlite3")
    journal.append(event("evt-002", "2026-11-10T20:00:02Z"))
    journal.append(event("evt-001", "2026-11-10T20:00:01Z"))

    assert [item["event_id"] for item in journal.list_all()] == ["evt-001", "evt-002"]
    journal.close()


def test_duplicate_event_id_and_mutation_fail_closed(tmp_path: Path):
    journal = EventJournal(tmp_path / "events.sqlite3")
    journal.append(event("evt-001", "2026-11-10T20:00:00Z"))

    with pytest.raises(sqlite3.IntegrityError):
        journal.append(event("evt-001", "2026-11-10T20:00:01Z"))
    with pytest.raises(sqlite3.DatabaseError):
        journal.connection.execute("DELETE FROM events WHERE event_id = 'evt-001'")
    with pytest.raises(sqlite3.DatabaseError):
        journal.connection.execute("UPDATE events SET event_type = 'changed' WHERE event_id = 'evt-001'")
    journal.close()


def test_invalid_schema_and_identity_are_rejected(tmp_path: Path):
    journal = EventJournal(tmp_path / "events.sqlite3")

    invalid_schema = event("evt-001", "2026-11-10T20:00:00Z")
    invalid_schema["schema_version"] = 2
    with pytest.raises(EventValidationError, match="schema_version"):
        journal.append(invalid_schema)

    missing_identity = event("evt-002", "2026-11-10T20:00:01Z")
    missing_identity["actor"] = {"kind": "agent"}
    with pytest.raises(EventValidationError, match="actor.id"):
        journal.append(missing_identity)
    journal.close()


def test_compensating_correction_preserves_original_event(tmp_path: Path):
    journal = EventJournal(tmp_path / "events.sqlite3")
    journal.append(event("evt-001", "2026-11-10T20:00:00Z"))
    journal.append(
        event(
            "evt-002",
            "2026-11-10T20:00:03Z",
            event_type="mission.task.corrected",
            correction_of="evt-001",
        )
    )

    original = journal.get("evt-001")
    correction = journal.get("evt-002")
    assert original["type"] == "mission.task.completed"
    assert correction["correction_of"] == "evt-001"
    assert [item["event_id"] for item in journal.list_all()] == ["evt-001", "evt-002"]
    journal.close()
