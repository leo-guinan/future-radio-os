from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable


class PlayoutError(ValueError):
    pass


@dataclass(frozen=True)
class Segment:
    segment_id: str
    uri: str
    approved: bool
    rights_ok: bool
    expires_at: str | None
    source_mission_id: str
    fallback: bool = False

    def eligible(self, now: datetime) -> bool:
        if not now.tzinfo or now.utcoffset() is None:
            raise PlayoutError("playout time must include a timezone")
        if not self.approved or not self.rights_ok:
            return False
        if self.expires_at:
            if not isinstance(self.expires_at, str):
                raise PlayoutError("expiry must be a string")
            try:
                expires = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
            except ValueError as exc:
                raise PlayoutError("expiry must be ISO-8601") from exc
            if not expires.tzinfo or expires.utcoffset() is None:
                raise PlayoutError("expiry must include a timezone")
            if expires <= now:
                return False
        return True


class MediaLibrary:
    def __init__(self):
        self._segments: dict[str, Segment] = {}

    def add(self, segment: Segment) -> None:
        if segment.segment_id in self._segments:
            raise PlayoutError(f"duplicate segment {segment.segment_id}")
        self._segments[segment.segment_id] = segment

    def get(self, segment_id: str) -> Segment:
        try:
            return self._segments[segment_id]
        except KeyError as exc:
            raise PlayoutError(f"segment {segment_id!r} not found") from exc


@dataclass(frozen=True)
class PlayoutResult:
    segment_id: str
    used_fallback: bool


class Scheduler:
    def __init__(self, library: MediaLibrary):
        self.library = library
        self.health = "healthy"
        self.receipts: list[dict[str, str]] = []

    def eligible(self, *, now: datetime | None = None) -> list[Segment]:
        current = now or datetime.now(timezone.utc)
        return [segment for segment in self.library._segments.values() if segment.eligible(current) and not segment.fallback]

    def play(self, segment_id: str, *, playback: Callable[[str], bool]) -> PlayoutResult:
        segment = self.library.get(segment_id)
        if not segment.eligible(datetime.now(timezone.utc)):
            raise PlayoutError(f"segment {segment_id!r} is not eligible")
        if playback(segment.uri):
            self.health = "healthy"
            self.receipts.append({"segment": segment_id, "status": "played"})
            return PlayoutResult(segment_id=segment_id, used_fallback=False)
        fallback = next((item for item in self.library._segments.values() if item.fallback and item.eligible(datetime.now(timezone.utc))), None)
        if fallback is None:
            self.health = "offline"
            raise PlayoutError("playback failed and no eligible fallback exists")
        self.health = "degraded"
        self.receipts.append({"failed_segment": segment_id, "fallback": fallback.segment_id, "status": "fallback"})
        return PlayoutResult(segment_id=fallback.segment_id, used_fallback=True)
