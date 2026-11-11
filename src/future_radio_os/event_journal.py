import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SUPPORTED_SCHEMA_VERSION = 1


class EventValidationError(ValueError):
    """Raised when an event cannot be accepted by the journal contract."""


class EventJournal:
    """SQLite-backed append-only event journal for local-first operation."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._create_schema()

    @property
    def connection(self) -> sqlite3.Connection:
        return self._connection

    def _create_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                schema_version INTEGER NOT NULL CHECK (schema_version = 1),
                event_type TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                actor_kind TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                mission_id TEXT,
                task_id TEXT,
                inputs_json TEXT NOT NULL,
                outputs_json TEXT NOT NULL,
                verification_json TEXT NOT NULL,
                cost_json TEXT NOT NULL,
                correction_of TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_events_time
                ON events (occurred_at, recorded_at, event_id);

            CREATE TRIGGER IF NOT EXISTS prevent_event_updates
            BEFORE UPDATE ON events
            BEGIN
                SELECT RAISE(ABORT, 'events are append-only');
            END;

            CREATE TRIGGER IF NOT EXISTS prevent_event_deletes
            BEFORE DELETE ON events
            BEGIN
                SELECT RAISE(ABORT, 'events are append-only');
            END;
            """
        )
        self._connection.commit()

    def append(self, event: dict[str, Any]) -> dict[str, Any]:
        normalized = self._validate(event)
        self._connection.execute(
            """
            INSERT INTO events (
                event_id, schema_version, event_type, occurred_at, recorded_at,
                actor_kind, actor_id, correlation_id, mission_id, task_id,
                inputs_json, outputs_json, verification_json, cost_json, correction_of
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                normalized["event_id"],
                normalized["schema_version"],
                normalized["type"],
                normalized["occurred_at"],
                normalized["recorded_at"],
                normalized["actor"]["kind"],
                normalized["actor"]["id"],
                normalized["correlation_id"],
                normalized.get("mission_id"),
                normalized.get("task_id"),
                _json(normalized["inputs"]),
                _json(normalized["outputs"]),
                _json(normalized["verification"]),
                _json(normalized["cost"]),
                normalized.get("correction_of"),
            ),
        )
        self._connection.commit()
        return normalized

    def get(self, event_id: str) -> dict[str, Any]:
        row = self._connection.execute(
            "SELECT * FROM events WHERE event_id = ?", (event_id,)
        ).fetchone()
        if row is None:
            raise KeyError(event_id)
        return _row_to_event(row)

    def list_all(self) -> list[dict[str, Any]]:
        rows = self._connection.execute("SELECT * FROM events").fetchall()
        rows = sorted(rows, key=lambda row: (_event_datetime(row["occurred_at"], allow_legacy_naive=True), _event_datetime(row["recorded_at"], allow_legacy_naive=True), row["event_id"]))
        return [_row_to_event(row) for row in rows]

    def list_between(self, start: str, end: str) -> list[dict[str, Any]]:
        start_utc = _event_datetime(start)
        end_utc = _event_datetime(end)
        rows = self._connection.execute("SELECT * FROM events").fetchall()
        rows = [row for row in rows if start_utc <= _event_datetime(row["occurred_at"], allow_legacy_naive=True) <= end_utc]
        rows = sorted(rows, key=lambda row: (_event_datetime(row["occurred_at"], allow_legacy_naive=True), _event_datetime(row["recorded_at"], allow_legacy_naive=True), row["event_id"]))
        return [_row_to_event(row) for row in rows]

    def close(self) -> None:
        self._connection.close()

    @staticmethod
    def _validate(event: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(event, dict):
            raise EventValidationError("event must be an object")
        required = (
            "event_id",
            "schema_version",
            "type",
            "occurred_at",
            "actor",
            "correlation_id",
            "inputs",
            "outputs",
            "verification",
            "cost",
        )
        missing = [key for key in required if key not in event]
        if missing:
            raise EventValidationError(f"missing fields: {', '.join(missing)}")
        if event["schema_version"] != SUPPORTED_SCHEMA_VERSION:
            raise EventValidationError(
                f"schema_version {event['schema_version']} is unsupported"
            )
        for key in ("event_id", "type", "correlation_id"):
            if not isinstance(event[key], str) or not event[key].strip():
                raise EventValidationError(f"{key} must be a non-empty string")
        actor = event["actor"]
        if not isinstance(actor, dict):
            raise EventValidationError("actor must be an object")
        for key in ("kind", "id"):
            if not isinstance(actor.get(key), str) or not actor[key].strip():
                raise EventValidationError(f"actor.{key} must be a non-empty string")
        for key in ("inputs", "outputs"):
            if not isinstance(event[key], list):
                raise EventValidationError(f"{key} must be a list")
        if not isinstance(event["verification"], dict):
            raise EventValidationError("verification must be an object")
        if not isinstance(event["cost"], dict):
            raise EventValidationError("cost must be an object")
        normalized = dict(event)
        normalized["occurred_at"] = _normalize_timestamp(event["occurred_at"], "occurred_at")
        recorded_at = event.get("recorded_at") or datetime.now(timezone.utc).isoformat()
        normalized["recorded_at"] = _normalize_timestamp(recorded_at, "recorded_at")
        return normalized


def _normalize_timestamp(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise EventValidationError(f"{field} must be an ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EventValidationError(f"{field} must be an ISO-8601 string") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise EventValidationError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _event_datetime(value: Any, *, allow_legacy_naive: bool = False) -> datetime:
    if allow_legacy_naive and isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            parsed = None
        if parsed is not None and parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
    normalized = _normalize_timestamp(value, "timestamp")
    return datetime.fromisoformat(normalized.replace("Z", "+00:00"))


def _validate_timestamp(value: Any, field: str) -> None:
    _normalize_timestamp(value, field)


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _row_to_event(row: sqlite3.Row) -> dict[str, Any]:
    event: dict[str, Any] = {
        "event_id": row["event_id"],
        "schema_version": row["schema_version"],
        "type": row["event_type"],
        "occurred_at": row["occurred_at"],
        "recorded_at": row["recorded_at"],
        "actor": {"kind": row["actor_kind"], "id": row["actor_id"]},
        "correlation_id": row["correlation_id"],
        "inputs": json.loads(row["inputs_json"]),
        "outputs": json.loads(row["outputs_json"]),
        "verification": json.loads(row["verification_json"]),
        "cost": json.loads(row["cost_json"]),
    }
    for key in ("mission_id", "task_id", "correction_of"):
        if row[key] is not None:
            event[key] = row[key]
    return event
