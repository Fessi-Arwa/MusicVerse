#!/usr/bin/env python3
"""Log every Vibe hook event as one human-readable JSON file.

Each event is appended to ``events/<session_id>/NNN-<slug>.json`` under
the session's cwd, numbered chronologically. The slug is the (possibly
abbreviated) event name plus short filename-safe extras such as the
tool name or a word-cut snippet of the prompt, e.g.
``002-pre_agent-what_would_we_need_to_change.json``.

For readability, any string containing newlines (e.g. tool output) is
stored as an array of lines instead of one long escaped line, and the
derived ``tool_output_text`` rendering is dropped when the structured
``tool_output`` is present.

The script is fully generic over ``hook_event_name``: any event type,
present or future, is logged without script changes (on Vibe versions
that add types, only a new ``[[hooks]]`` row in ``../hooks.toml`` is
needed).

The hook always exits 0 with empty stdout so it is a pure passthrough;
diagnostics go to stderr only.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

EVENTS_DIRNAME = "events"
LOCK_FILENAME = ".lock"
_UNSAFE_CHARS = re.compile(r"[^\w-]+")
_SEQ_PREFIX = re.compile(r"^(\d+)")

# Abbreviations for long event names; unlisted events keep their full name.
EVENT_SHORT = {
    "session_start": "start",
    "session_end": "end",
    "notification": "notify",
}

# Scalar payload fields appended after the event name, per event type.
FILENAME_FIELDS = {
    "session_start": ["source"],
    "pre_tool": ["tool_name"],
    "post_tool": ["tool_name", "tool_status"],
    "notification": ["notification_type", "tool_name"],
    "session_end": ["reason"],
}

# Text payload fields rendered as a first-N-chars, word-cut snippet.
FILENAME_SNIPPETS = {
    "pre_agent": ("prompt", 30),
}

MAX_PART = 20


def _session_dir(payload: dict) -> Path:
    raw = str(payload.get("session_id") or "unknown-session")
    safe = _UNSAFE_CHARS.sub("_", raw).strip("._") or "unknown-session"
    base = Path(str(payload.get("cwd") or os.getcwd())) / EVENTS_DIRNAME / safe
    base.mkdir(parents=True, exist_ok=True)
    return base


def _sanitize(text: str, limit: int) -> str:
    return _UNSAFE_CHARS.sub("_", text).strip("._")[:limit]


def _snippet(text: object, limit: int) -> str:
    if not isinstance(text, str):
        return ""
    flat = _sanitize(" ".join(text.split()), limit)
    cut = flat.rsplit("_", 1)[0]
    return (cut or flat).strip("._")


def _slug(payload: dict) -> str:
    name = str(payload.get("hook_event_name") or "unknown")
    parts = [_sanitize(EVENT_SHORT.get(name, name), MAX_PART)]
    for key in FILENAME_FIELDS.get(name, []):
        value = payload.get(key)
        if isinstance(value, bool) or not isinstance(value, (str, int, float)):
            continue
        text = str(value)
        if key == "tool_name":
            text = text.rsplit(".", 1)[-1]
        part = _sanitize(text, MAX_PART)
        if part:
            parts.append(part)
    if name in FILENAME_SNIPPETS:
        field, limit = FILENAME_SNIPPETS[name]
        snippet = _snippet(payload.get(field), limit)
        if snippet:
            parts.append(snippet)
    return "-".join(parts)


def _split_multiline(value: object) -> object:
    """Replace any string containing newlines with a list of its lines,
    so the indented JSON renders one source line per output line."""
    if isinstance(value, str):
        return value.split("\n") if "\n" in value else value
    if isinstance(value, dict):
        return {key: _split_multiline(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_split_multiline(item) for item in value]
    return value


def _drop_derived_text(payload: dict) -> dict:
    # tool_output_text is the rendered form of the structured tool_output.
    if isinstance(payload.get("tool_output"), dict):
        return {k: v for k, v in payload.items() if k != "tool_output_text"}
    return payload


def _next_seq(session_dir: Path) -> int:
    highest = 0
    for path in session_dir.glob("*.json"):
        match = _SEQ_PREFIX.match(path.stem)
        if match:
            highest = max(highest, int(match.group(1)))
    return highest + 1


def _lock_file(lock) -> None:
    """Lock one byte on Windows, or the whole file on Unix."""
    if os.name == "nt":
        import msvcrt

        lock.seek(0, os.SEEK_END)
        if lock.tell() == 0:
            lock.write(b"\0")
            lock.flush()
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
    else:
        import fcntl

        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)


def _unlock_file(lock) -> None:
    if os.name == "nt":
        import msvcrt

        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def _log(payload: object) -> None:
    if not isinstance(payload, dict):
        payload = {"value": payload}
    payload = _drop_derived_text(payload)
    session_dir = _session_dir(payload)
    # Tool calls in one turn fire hook chains concurrently, so the
    # read-max-plus-one/write sequence must be serialized per session.
    with open(session_dir / LOCK_FILENAME, "a+b") as lock:
        _lock_file(lock)
        try:
            seq = _next_seq(session_dir)
            record = {
                "seq": seq,
                "received_at": datetime.now(timezone.utc).isoformat(),
                "hook_event_name": payload.get("hook_event_name"),
                "event": _split_multiline(payload),
            }
            fd, tmp_name = tempfile.mkstemp(
                dir=session_dir, prefix=".tmp-", suffix=".json"
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                    json.dump(record, tmp, indent=2, ensure_ascii=False)
                    tmp.write("\n")
                os.replace(tmp_name, session_dir / f"{seq:03d}-{_slug(payload)}.json")
            except BaseException:
                try:
                    os.unlink(tmp_name)
                except OSError:
                    pass
                raise
        finally:
            _unlock_file(lock)


def main() -> int:
    try:
        _log(json.load(sys.stdin))
    except Exception as exc:  # a logger must never break the hook chain
        print(f"log_event: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
