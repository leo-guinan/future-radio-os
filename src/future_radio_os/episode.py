import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any


class EpisodeSafetyError(ValueError):
    """Raised when source or privacy checks fail before rendering."""


class EpisodeBuilder:
    def render(
        self,
        *,
        mission_id: str,
        title: str,
        events: list[dict[str, Any]],
        output: str | Path,
    ) -> Path:
        if not mission_id.strip() or not title.strip():
            raise EpisodeSafetyError("mission_id and title are required")
        if not events:
            raise EpisodeSafetyError("episode requires at least one source event")
        claims: list[str] = []
        source_ids: list[str] = []
        for event in events:
            if event.get("mission_id") != mission_id:
                raise EpisodeSafetyError("every claim must have a mission source")
            event_id = event.get("event_id")
            verification = event.get("verification", {})
            status = verification.get("status")
            if not isinstance(event_id, str) or not event_id:
                raise EpisodeSafetyError("source event IDs are required")
            if status not in {"passed", "failed"}:
                raise EpisodeSafetyError("episode sources must be verified or explicitly failed")
            text = " ".join(str(item) for item in event.get("outputs", []))
            if _contains_private(text):
                raise EpisodeSafetyError("private or credential-like data cannot enter an episode")
            source_ids.append(event_id)
            if status == "passed":
                claims.append(
                    f"Verified observation: {html.escape(text)} <small>[source: {html.escape(event_id)}]</small>"
                )
            else:
                claims.append(
                    f"Observed failure: {html.escape(text)}; the mission did not resolve. "
                    f"<small>[source: {html.escape(event_id)}]</small>"
                )
        body = "\n".join(f"<li>{claim}</li>" for claim in claims)
        rendered = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>body{{font:18px system-ui;max-width:760px;margin:4rem auto;padding:0 1rem;background:#111;color:#eee}}small{{color:#9ad}}li{{margin:1.5rem 0;line-height:1.5}}</style>
</head>
<body data-mission-id="{html.escape(mission_id)}"><h1>{html.escape(title)}</h1>
<p>Evidence-backed segment. Claims remain linked to their source events.</p><ol>{body}</ol></body>
</html>
"""
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered)
        digest = hashlib.sha256(output_path.read_bytes()).hexdigest()
        manifest = {
            "status": "verified_sources",
            "format": "text/html",
            "mission_id": mission_id,
            "source_event_ids": source_ids,
            "artifact_sha256": digest,
            "claim_count": len(claims),
        }
        manifest_path = output_path.with_suffix(".manifest.json")
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        return manifest_path


def _contains_private(text: str) -> bool:
    return bool(re.search(r"(?:secret|password|token|private[_ -]?key)\s*[:=]", text, re.I))
