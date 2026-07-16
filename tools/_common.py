"""Shared harness for awesome-prompts agent tools.

Every tool follows the same contract so the agent can call any of them the same way:

  - Input  : CLI flags, and/or a JSON payload from a file (``--in path``) or stdin (``--in -``).
  - Output : exactly ONE JSON object on stdout, always shaped as an envelope:
                 {"ok": true,  "tool": "<name>", "data":  <result>}
                 {"ok": false, "tool": "<name>", "error": {"code","message",...}}
  - Exit   : 0 on success, 1 on handled error, 2 on bad usage.

Keep tools composable: the ``data`` of one tool should be pipe-able into the
``--in -`` of another. Never print anything else to stdout (use stderr for logs).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

_TOOL_NAME = "unknown"


def set_tool(name: str) -> None:
    global _TOOL_NAME
    _TOOL_NAME = name


def log(*args) -> None:
    """Human-readable progress goes to stderr, never stdout."""
    print(*args, file=sys.stderr, flush=True)


def emit(data) -> None:
    """Emit a success envelope and exit 0."""
    json.dump({"ok": True, "tool": _TOOL_NAME, "data": data},
              sys.stdout, ensure_ascii=False, indent=2, default=str)
    sys.stdout.write("\n")
    sys.exit(0)


def fail(message: str, code: str = "error", exit_code: int = 1, **extra) -> None:
    """Emit an error envelope and exit non-zero."""
    err = {"code": code, "message": message}
    err.update(extra)
    json.dump({"ok": False, "tool": _TOOL_NAME, "error": err},
              sys.stdout, ensure_ascii=False, indent=2, default=str)
    sys.stdout.write("\n")
    sys.exit(exit_code)


def require(module: str, pip_name: str | None = None):
    """Import an optional dependency or fail with an install hint."""
    try:
        return __import__(module)
    except ImportError:
        fail(f"Missing dependency '{module}'. Install with: pip install {pip_name or module}",
             code="missing_dependency", dependency=pip_name or module)


def env(key: str, required: bool = True) -> str | None:
    """Read an API key / secret from the environment (or tools/.env)."""
    import os
    val = os.environ.get(key)
    if required and not val:
        fail(f"Missing environment variable '{key}'.",
             code="missing_env", variable=key)
    return val


def env_any(names, required: bool = True, label: str | None = None) -> str | None:
    """Return the first set env var among aliases (e.g. FAL_KEY / FAL_AI_API_KEY)."""
    import os
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    if required:
        fail(f"Missing API key. Set one of: {', '.join(names)} "
             f"(in the environment or tools/.env).",
             code="missing_env", variable=label or names[0], accepted=list(names))
    return None


def _load_dotenv() -> None:
    """Load tools/.env into the environment at import (never overrides real env)."""
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                if line.startswith("export "):
                    line = line[7:]
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
    except OSError:
        pass


_load_dotenv()


def load_input(path: str | None):
    """Load a JSON payload from a file path, '-' (stdin), or None (stdin if piped)."""
    import os
    if path == "-":
        raw = sys.stdin.read()
    elif path:
        with open(path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    elif not sys.stdin.isatty():
        raw = sys.stdin.read()
    else:
        return None
    raw = raw.strip()
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"Input is not valid JSON: {exc}", code="bad_input", exit_code=2)
    # Accept either a raw value or a tool envelope ({"ok":...,"data":...}) so
    # tools can be chained without manually unwrapping.
    if isinstance(payload, dict) and "data" in payload and set(payload) <= {"ok", "tool", "data", "error"}:
        return payload["data"]
    return payload


# --- shared field normalization ------------------------------------------------

# Map the many aliases (TikTokApi, yt-dlp, instaloader, hand-authored) onto one schema.
_ALIASES = {
    "views":     ("views", "playCount", "play_count", "view_count", "viewCount"),
    "likes":     ("likes", "diggCount", "digg_count", "like_count", "likeCount", "favorite_count"),
    "comments":  ("comments", "commentCount", "comment_count"),
    "shares":    ("shares", "shareCount", "share_count", "repost_count"),
    "saves":     ("saves", "collectCount", "collect_count", "saved", "bookmark_count"),
    "duration":  ("duration", "video_duration", "durationSec"),
    "created":   ("created", "createTime", "create_time", "createdAt", "posted_date",
                  "timestamp", "upload_date"),
    "url":       ("url", "webVideoUrl", "video_url", "link", "webpage_url"),
    "id":        ("id", "video_id", "aweme_id"),
    "caption":   ("caption", "desc", "description", "title", "text"),
}


def _dig(video: dict, key: str):
    """Pull a value for a canonical key, checking nested stats/statistics blocks."""
    pools = [video]
    for nest in ("stats", "statistics", "statsV2", "music", "video"):
        if isinstance(video.get(nest), dict):
            pools.append(video[nest])
    for alias in _ALIASES.get(key, (key,)):
        for pool in pools:
            if alias in pool and pool[alias] not in (None, ""):
                return pool[alias]
    return None


def to_int(val) -> int | None:
    if val is None:
        return None
    try:
        return int(float(str(val).replace(",", "").strip()))
    except (ValueError, TypeError):
        return None


def parse_created(val):
    """Return a timezone-aware UTC datetime from unix ts (s or ms) / ISO / yt-dlp YYYYMMDD.

    Always returns an *aware* datetime (naive inputs are assumed UTC) so downstream
    sorting and subtraction never mix aware and naive datetimes (which raises).
    """
    if val is None:
        return None
    s = str(val).strip()
    # Numeric unix timestamp: a real int/float, or an all-digit string of >= 9 digits
    # (so an 8-digit YYYYMMDD is not mistaken for one). 13-digit values are milliseconds.
    if isinstance(val, (int, float)) or (s.isdigit() and len(s) >= 9):
        try:
            ts = float(val)
            if ts >= 1e12:  # >= 1e12 is a 13-digit millisecond epoch -> seconds
                ts /= 1000.0
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        except (ValueError, OSError, OverflowError):
            pass
    if s.isdigit() and len(s) == 8:  # yt-dlp upload_date: YYYYMMDD
        try:
            return datetime.strptime(s, "%Y%m%d").replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def normalize_video(video: dict) -> dict:
    """Project any supported input shape onto the canonical video schema."""
    out = {k: to_int(_dig(video, k)) for k in
           ("views", "likes", "comments", "shares", "saves", "duration")}
    out["id"] = _dig(video, "id")
    out["url"] = _dig(video, "url")
    out["caption"] = _dig(video, "caption")
    created = parse_created(_dig(video, "created"))
    out["created"] = created.isoformat() if created else None
    return out


def now_utc(override: str | None = None) -> datetime:
    """Current time, or a caller-supplied ISO date (for reproducible runs/tests)."""
    if override:
        dt = parse_created(override)
        if dt is None:
            fail(f"--now must be an ISO date, got: {override}", code="bad_input", exit_code=2)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return datetime.now(tz=timezone.utc)
