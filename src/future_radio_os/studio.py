from dataclasses import asdict, dataclass
from html import escape
import re
from typing import Literal
from urllib.parse import urlparse


StudioStatus = Literal["unknown", "estimated", "modeled", "verified", "active", "blocked", "resolved"]
ALLOWED_STATUSES = {"unknown", "estimated", "modeled", "verified", "active", "blocked", "resolved"}


@dataclass(frozen=True)
class StudioItem:
    item_id: str
    title: str
    status: StudioStatus
    source_url: str


class StudioReadModel:
    """Read-only projection over durable records; it never invents missing status."""

    def __init__(self) -> None:
        self._items: dict[str, list[StudioItem]] = {"past": [], "present": [], "future": []}

    def add_past(self, *, item_id: str, title: str, status: StudioStatus, source_url: str) -> StudioItem:
        return self._add("past", item_id, title, status, source_url)

    def add_present(self, *, item_id: str, title: str, status: StudioStatus, source_url: str) -> StudioItem:
        return self._add("present", item_id, title, status, source_url)

    def add_future(self, *, item_id: str, title: str, status: StudioStatus, source_url: str) -> StudioItem:
        return self._add("future", item_id, title, status, source_url)

    def snapshot(self) -> dict[str, list[dict[str, str]]]:
        return {view: [asdict(item) for item in items] for view, items in self._items.items()}

    def render_html(self) -> str:
        snapshot = self.snapshot()
        sections = []
        for view in ("past", "present", "future"):
            cards = "".join(
                f'<article><h3>{escape(item["title"])}</h3><p>status: {escape(item["status"])}</p>'
                f'<a href="{escape(item["source_url"])}">source</a></article>'
                for item in snapshot[view]
            ) or "<p>status: unknown — no durable record</p>"
            sections.append(f"<section id=\"{view}\"><h2>{view.title()}</h2>{cards}</section>")
        return "<!doctype html><html><head><title>Future Radio Studio</title></head><body>" + "".join(sections) + "</body></html>"

    def _add(self, view: str, item_id: str, title: str, status: StudioStatus, source_url: str) -> StudioItem:
        if not item_id.strip() or not title.strip() or not source_url.strip():
            raise ValueError("studio items require ID, title, and source URL")
        if status not in ALLOWED_STATUSES:
            raise ValueError("studio item status is not classified")
        _validate_source_url(source_url)
        item = StudioItem(item_id, title, status, source_url)
        self._items[view].append(item)
        return item


def _validate_source_url(source_url: str) -> None:
    try:
        parsed = urlparse(source_url)
    except ValueError as exc:
        raise ValueError("source URL is malformed") from exc
    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https", "source", "artifact", "receipt", "proposal", "invoice"}:
        raise ValueError("source URL must use an approved scheme")
    if any(ord(char) < 32 or char in {"\\", "%"} for char in source_url):
        raise ValueError("source URL is malformed")
    if scheme in {"http", "https"}:
        if parsed.username is not None or parsed.password is not None or parsed.netloc.endswith(":"):
            raise ValueError("source URL must not contain userinfo or a dangling port")
        if not parsed.netloc or not parsed.hostname or not re.fullmatch(r"[A-Za-z0-9.:-]+", parsed.hostname):
            raise ValueError("source URL must include a valid HTTP(S) authority")
        try:
            parsed.port
        except ValueError as exc:
            raise ValueError("source URL must include a valid HTTP(S) port") from exc
