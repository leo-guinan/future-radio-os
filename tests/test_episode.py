import json
from pathlib import Path

import pytest

from future_radio_os.episode import EpisodeBuilder, EpisodeSafetyError


def ev(event_id: str, status: str = "passed", text: str = "Completed the local check") -> dict:
    return {
        "event_id": event_id,
        "type": "mission.task.completed",
        "mission_id": "mission-001",
        "verification": {"status": status, "evidence_ids": [f"evidence-{event_id}"]},
        "outputs": [text],
    }


def test_episode_contains_only_source_linked_verified_claims(tmp_path: Path):
    output = tmp_path / "episode.html"
    receipt = EpisodeBuilder().render(
        mission_id="mission-001",
        title="A verified local check",
        events=[ev("evt-001")],
        output=output,
    )

    html = output.read_text()
    manifest = json.loads(receipt.read_text())
    assert output.exists()
    assert "Completed the local check" in html
    assert "evt-001" in html
    assert manifest["source_event_ids"] == ["evt-001"]
    assert manifest["format"] == "text/html"
    assert manifest["status"] == "verified_sources"


def test_failed_work_is_not_narrated_as_success(tmp_path: Path):
    output = tmp_path / "episode.html"
    EpisodeBuilder().render(
        mission_id="mission-001",
        title="An honest failure",
        events=[ev("evt-fail", status="failed", text="Adapter failed")],
        output=output,
    )

    html = output.read_text()
    assert "did not resolve" in html
    assert "successfully completed" not in html


def test_private_data_and_unlinked_events_fail_closed(tmp_path: Path):
    with pytest.raises(EpisodeSafetyError, match="private"):
        EpisodeBuilder().render(
            mission_id="mission-001",
            title="Unsafe",
            events=[ev("evt-private", text="secret=abc123")],
            output=tmp_path / "episode.html",
        )

    with pytest.raises(EpisodeSafetyError, match="source"):
        EpisodeBuilder().render(
            mission_id="mission-001",
            title="Unlinked",
            events=[{**ev("evt-other"), "mission_id": "other-mission"}],
            output=tmp_path / "episode.html",
        )
