import time
from dataclasses import dataclass
from typing import Any, Protocol


class JuwelError(ValueError):
    """Raised when the JUWEL adapter cannot safely construct a request."""


class JuwelTransport(Protocol):
    def discover(self, endpoint: str, scopes: list[str]) -> dict[str, Any]: ...

    def submit(
        self, endpoint: str, tool: str, payload: dict[str, Any], approval: str | None
    ) -> dict[str, Any]: ...


@dataclass(frozen=True)
class JuwelConfig:
    endpoint: str
    agent_key: str
    scopes: list[str]

    def __repr__(self) -> str:
        return f"JuwelConfig(endpoint={self.endpoint!r}, agent_key='<redacted>', scopes={self.scopes!r})"


@dataclass(frozen=True)
class JuwelCapability:
    name: str
    scope: str
    supported: bool


@dataclass(frozen=True)
class JuwelReceipt:
    request_id: str | None
    status: str
    output: dict[str, Any]
    provenance: dict[str, str]
    cost_usd: float | None = None
    latency_ms: float | None = None
    error: str = ""


class JuwelAdapter:
    TOOL_SCOPES = {
        "juwel_chat": "chat",
        "calendar_create": "calendar.write",
        "gmail_send": "gmail.send",
    }

    def __init__(self, config: JuwelConfig, transport: JuwelTransport):
        if not config.endpoint.strip():
            raise JuwelError("endpoint is required")
        if not config.agent_key.strip():
            raise JuwelError("scoped agent key is required")
        if not config.scopes:
            raise JuwelError("at least one scope is required")
        self.config = config
        self.transport = transport

    def __repr__(self) -> str:
        return f"JuwelAdapter(config={self.config!r})"

    def discover(self) -> list[JuwelCapability]:
        response = self.transport.discover(self.config.endpoint, list(self.config.scopes))
        return [
            JuwelCapability(
                name=item["name"],
                scope=item["scope"],
                supported=bool(item.get("supported", False)),
            )
            for item in response.get("capabilities", [])
        ]

    def submit(
        self,
        tool: str,
        payload: dict[str, Any],
        *,
        effectful: bool = False,
        approval: str | None = None,
    ) -> JuwelReceipt:
        if effectful and not approval:
            raise JuwelError("effectful JUWEL call requires a human approval nonce")
        scope = self.TOOL_SCOPES.get(tool)
        provenance = {"provider": "juwel", "scope": scope or "unknown"}
        if scope is None or scope not in self.config.scopes:
            return JuwelReceipt(
                request_id=None,
                status="unsupported",
                output={},
                provenance=provenance,
                error=f"tool {tool!r} is unsupported or scope {scope!r} is unavailable",
            )
        started = time.monotonic()
        response = self.transport.submit(self.config.endpoint, tool, payload, approval)
        return JuwelReceipt(
            request_id=response.get("request_id"),
            status="accepted",
            output=response.get("output", {}),
            provenance=provenance,
            cost_usd=response.get("cost_usd"),
            latency_ms=(time.monotonic() - started) * 1000,
        )
