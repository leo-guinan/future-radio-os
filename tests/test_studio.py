from typing import Any, cast

import pytest
from fastapi.testclient import TestClient

from future_radio_os.app import create_app
from future_radio_os.studio import StudioReadModel


def seeded_model() -> StudioReadModel:
    model = StudioReadModel()
    model.add_past(item_id="evidence-1", title="A verified field observation", status="verified", source_url="https://example.test/evidence/1")
    model.add_present(item_id="mission-1", title="Build the first radio episode", status="active", source_url="https://example.test/missions/1")
    model.add_future(item_id="hypothesis-1", title="Test whether the missing edge exists", status="unknown", source_url="https://example.test/hypotheses/1")
    return model


def test_snapshot_separates_past_present_future_and_preserves_source_links():
    snapshot = seeded_model().snapshot()
    assert snapshot["past"][0]["status"] == "verified"
    assert snapshot["present"][0]["status"] == "active"
    assert snapshot["future"][0]["status"] == "unknown"
    assert snapshot["future"][0]["source_url"].startswith("https://")


def test_unknown_and_modeled_states_are_not_rendered_as_verified():
    model = StudioReadModel()
    model.add_future(item_id="h-1", title="Estimated path", status="estimated", source_url="source://h-1")
    model.add_future(item_id="h-2", title="Modeled path", status="modeled", source_url="source://h-2")
    statuses = {item["status"] for item in model.snapshot()["future"]}
    assert statuses == {"estimated", "modeled"}


def test_external_source_links_reject_unsafe_schemes():
    model = StudioReadModel()
    with pytest.raises(ValueError, match="source URL"):
        model.add_future(item_id="h-xss", title="Unsafe", status="unknown", source_url="javascript:alert(1)")
    with pytest.raises(ValueError, match="source URL"):
        model.add_future(item_id="h-malformed", title="Malformed", status="unknown", source_url="https:")
    for malformed in ("https://@", "https://:", "https://\\", "https://%", "https://example.com:", "https://trusted.example@evil.example"):
        with pytest.raises(ValueError, match="source URL"):
            model.add_future(item_id="h-invalid", title="Malformed", status="unknown", source_url=malformed)


def test_studio_rejects_unclassified_statuses():
    model = StudioReadModel()
    with pytest.raises(ValueError, match="status"):
        model.add_present(item_id="m-bad", title="Bad", status=cast(Any, "invented"), source_url="source://m-bad")


def test_browser_smoke_reads_seeded_studio_path_from_app():
    app = create_app(studio=seeded_model())
    client = TestClient(app)
    response = client.get("/studio")
    assert response.status_code == 200
    assert response.json()["present"][0]["title"] == "Build the first radio episode"

    page = client.get("/studio/view")
    assert page.status_code == 200
    assert "A verified field observation" in page.text
    assert "status: unknown" in page.text
