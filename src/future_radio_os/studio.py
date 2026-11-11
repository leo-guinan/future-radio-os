from dataclasses import asdict, dataclass
from html import escape
from typing import Literal


StudioStatus = Literal["unknown", "estimated", "modeled", "verified", "active", "blocked", "resolved"]


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
        item = StudioItem(item_id, title, status, source_url)
        self._items[view].append(item)
        return item
