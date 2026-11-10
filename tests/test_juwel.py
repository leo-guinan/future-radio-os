import time
from dataclasses import dataclass
from typing import Any, Protocol

import pytest

from future_radio_os.juwel import JuwelAdapter, JuwelConfig, JuwelError


class FakeTransport:
    def __init__(self):
        self.calls = []

    def discover(self, endpoint: str, scopes: list[str]) -> dict[str, Any]:
        self.calls.append(("discover", endpoint, scopes))
        return {"capabilities": [{"name": "juwel_chat", "scope": "chat", "supported": True}]}

    def submit(self, endpoint: str, tool: str, payload: dict[str, Any], approval: str | None) -> dict[str, Any]:
        self.calls.append(("submit", endpoint, tool, payload, approval))
        return {"request_id": "req-001", "output": {"text": "plan"}, "cost_usd": 0.02}


def test_discovery_and_task_submission_normalize_evidence_without_exposing_key():
    transport = FakeTransport()
    adapter = JuwelAdapter(
        JuwelConfig(endpoint="https://juwel.ai/api", agent_key="jak_secret", scopes=["chat"]), transport
    )

    capabilities = adapter.discover()
    receipt = adapter.submit("juwel_chat", {"prompt": "plan"})

    assert capabilities[0].name == "juwel_chat"
    assert receipt.request_id == "req-001"
    assert receipt.provenance == {"provider": "juwel", "scope": "chat"}
    assert "jak_secret" not in repr(adapter)
    assert transport.calls[-1][-1] is None


def test_unsupported_capability_is_explicit_and_effectful_call_requires_approval():
    adapter = JuwelAdapter(
        JuwelConfig(endpoint="https://juwel.ai/api", agent_key="jak_secret", scopes=["chat"]), FakeTransport()
    )
    unsupported = adapter.submit("gmail_send", {"to": "example@example.com"})
    assert unsupported.status == "unsupported"
    assert "scope" in unsupported.error

    effectful_adapter = JuwelAdapter(
        JuwelConfig(endpoint="https://juwel.ai/api", agent_key="jak_secret", scopes=["chat", "calendar.write"]), FakeTransport()
    )
    with pytest.raises(JuwelError, match="approval"):
        effectful_adapter.submit("calendar_create", {"title": "meeting"}, effectful=True)
    receipt = effectful_adapter.submit("calendar_create", {"title": "meeting"}, effectful=True, approval="nonce-001")
    assert receipt.status == "accepted"


def test_missing_endpoint_or_scope_fails_closed():
    with pytest.raises(JuwelError, match="endpoint"):
        JuwelAdapter(JuwelConfig(endpoint="", agent_key="jak_secret", scopes=["chat"]), FakeTransport())
    with pytest.raises(JuwelError, match="scope"):
        JuwelAdapter(JuwelConfig(endpoint="https://juwel.ai/api", agent_key="jak_secret", scopes=[]), FakeTransport())
