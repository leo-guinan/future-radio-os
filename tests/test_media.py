from datetime import datetime, timezone
from typing import Any, cast

import pytest

from future_radio_os.media import MediaLibrary, PlayoutError, Segment, Scheduler


def segment(segment_id: str, *, approved: bool = True, rights_ok: bool = True, expires_at: str | None = None, fallback: bool = False) -> Segment:
    return Segment(segment_id=segment_id, uri=f"artifact://{segment_id}", approved=approved, rights_ok=rights_ok, expires_at=expires_at, source_mission_id="mission-001", fallback=fallback)


def test_scheduler_excludes_ineligible_and_expired_segments():
    library = MediaLibrary()
    library.add(segment("draft", approved=False))
    library.add(segment("rights", rights_ok=False))
    library.add(segment("expired", expires_at="2020-01-01T00:00:00+00:00"))
    library.add(segment("good"))

    assert [item.segment_id for item in Scheduler(library).eligible(now=datetime(2026, 1, 1, tzinfo=timezone.utc))] == ["good"]


def test_failed_playback_uses_deterministic_fallback_and_records_health():
    library = MediaLibrary()
    library.add(segment("fallback", fallback=True))
    library.add(segment("main"))
    scheduler = Scheduler(library)

    result = scheduler.play("main", playback=lambda _: False)

    assert result.segment_id == "fallback"
    assert result.used_fallback is True
    assert scheduler.health == "degraded"
    assert scheduler.receipts[-1]["failed_segment"] == "main"


def test_missing_fallback_or_unapproved_publication_fails_closed():
    library = MediaLibrary()
    library.add(segment("draft", approved=False))
    library.add(segment("main"))
    scheduler = Scheduler(library)
    with pytest.raises(PlayoutError, match="not eligible"):
        scheduler.play("draft", playback=lambda _: True)
    with pytest.raises(PlayoutError, match="fallback"):
        scheduler.play("main", playback=lambda _: False)


def test_naive_expiry_is_rejected_instead_of_comparing_mixed_datetime_types():
    library = MediaLibrary()
    library.add(segment("naive", expires_at="2026-01-01T00:00:00"))
    with pytest.raises(PlayoutError, match="timezone"):
        Scheduler(library).eligible(now=datetime(2026, 1, 1, tzinfo=timezone.utc))


def test_non_string_expiry_is_rejected_with_playout_error():
    library = MediaLibrary()
    library.add(segment("bad", expires_at=cast(Any, 123)))
    with pytest.raises(PlayoutError, match="expiry"):
        Scheduler(library).eligible(now=datetime(2026, 1, 1, tzinfo=timezone.utc))
