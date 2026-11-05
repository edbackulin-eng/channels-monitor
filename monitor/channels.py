"""The channels watched, and how to read each one (its own state files, read-only).

Every reader takes the channel's checkout (a shallow, sparse clone made by
check.py, or a test fixture) and returns plain data:

  scheduled(root)  [(publish_at UTC datetime, video id, title)] of videos with a date
  failed(root)     [(episode, reason)] of episodes that failed or failed QA
  topics(root)     topics still waiting to be built (int), or None when the channel has
                   no such queue
  waiting(root)    videos uploaded without a date (waiting for the owner), as a count

Slots follow each channel's own schedule (weekdays, local time, time zone).
"""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _json(root, path, default=None):
    p = Path(root) / path
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return default


def _when(s):
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


# ---------------------------------------------------------------- What If
def wi_episodes(root):
    out = []
    for f in sorted((Path(root) / "queue").glob("*/episode.json")):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
    return out


def wi_scheduled(root):
    return [(_when(e.get("publish_at")), e.get("youtube_id"), e.get("title") or e.get("slug"))
            for e in wi_episodes(root) if e.get("youtube_id") and _when(e.get("publish_at"))]


def wi_failed(root):
    return [(e.get("slug"), str(e.get("error") or "failed")) for e in wi_episodes(root) if e.get("status") == "failed"]


def wi_topics(root):
    used = {e.get("title") for e in wi_episodes(root)}
    topics = _json(root, "assets/topics.json", [])
    ready = sum(1 for e in wi_episodes(root) if e.get("status") == "ready-to-render")
    return sum(1 for t in topics if t not in used) + ready


# ---------------------------------------------------------------- Closed Tabs
def ct_scheduled(root):
    return [(_when(r.get("publish_at")), r.get("youtube_id"), r.get("title") or r.get("slug"))
            for r in _json(root, "state/episodes.json", []) if r.get("youtube_id") and _when(r.get("publish_at"))]


def ct_failed(root):
    return [(r.get("slug"), str(r.get("error") or r.get("status"))) for r in _json(root, "state/episodes.json", [])
            if str(r.get("status", "")).endswith("failed")]


def ct_topics(root):
    q = _json(root, "topics/queue.json", {"topics": []})
    done = {r.get("slug") for r in _json(root, "state/episodes.json", [])}
    return sum(1 for t in q.get("topics", []) if t.get("status", "queued") == "queued" and t.get("slug") not in done)


# ---------------------------------------------------------------- dinosaurs and the archive channel
def rows_scheduled(root):
    return [(_when(r.get("publish_at")), r.get("youtube_id") or r.get("video_id"), r.get("title") or r.get("slug"))
            for r in _json(root, "state/episodes.json", [])
            if (r.get("youtube_id") or r.get("video_id")) and _when(r.get("publish_at"))
            and str(r.get("status") or r.get("state") or "") not in ("qa-failed", "failed", "rejected")]


def rows_failed(root):
    out = []
    for r in _json(root, "state/episodes.json", []):
        st = str(r.get("status") or r.get("state") or "")
        if st in ("qa-failed", "failed"):
            why = r.get("qa_failed") or r.get("error") or st
            if isinstance(why, list):
                why = "; ".join(str(w).split(":")[0] for w in why)
            out.append((r.get("slug"), f"{st}: {why}"))
    return out


def rows_waiting(root):
    return sum(1 for r in _json(root, "state/episodes.json", [])
               if str(r.get("status") or r.get("state") or "") in ("awaiting_approval", "awaiting_turn", "built"))


def rows_built(root):
    """Built videos in the buffer that have not reached YouTube."""
    return sum(1 for r in _json(root, "state/episodes.json", [])
               if str(r.get("status") or r.get("state") or "") == "built" and not (r.get("youtube_id") or r.get("video_id")))


def queue_topics(root):
    q = _json(root, "topics/queue.json", {"topics": []})
    t = q.get("topics", []) if isinstance(q, dict) else q
    return sum(1 for x in t if x.get("status", "queued") == "queued")


# ---------------------------------------------------------------- stoic (read only)
def _db(root):
    p = Path(root) / "data" / "factory.db"
    return sqlite3.connect(f"file:{p.as_posix()}?mode=ro", uri=True) if p.exists() else None


def st_scheduled(root):
    c = _db(root)
    if not c:
        return []
    rows = c.execute("select published_at, youtube_id, title from videos where youtube_id is not null "
                     "and status = 'published' and published_at is not null").fetchall()
    c.close()
    return [(_when(a), b, t) for a, b, t in rows if _when(a)]


def st_failed(root, days=7):
    c = _db(root)
    if not c:
        return []
    since = datetime.now(timezone.utc).timestamp() - days * 86400
    rows = c.execute("select id, created_at, coalesce(error, ''), coalesce(title, topic) from videos "
                     "where status = 'failed'").fetchall()
    c.close()
    out = []
    for vid, created, err, title in rows:
        w = _when(created)
        if w and w.timestamp() >= since:
            out.append((f"#{vid} {str(title)[:30]}", err or "failed"))
    return out


def st_topics(root):
    """None: the stoic channel draws a new topic from 48 seeds for every video (least used
    first, its pipeline/topic.py), so it has no queue that can run dry."""
    return None


CHANNELS = [
    {"key": "whatif", "name": "What If", "repo": "edbackulin-eng/whatif-channel", "act": True,
     "slots": {"weekdays": [0, 1, 3, 4, 5], "time": "15:00", "tz": "UTC"},
     "paths": ["queue", "assets/topics.json", "state"],
     "watchdog": "watchdog.yml", "builds": ["build-video.yml"], "heartbeat": "state/heartbeat.json",
     "scheduled": wi_scheduled, "failed": wi_failed, "topics": wi_topics, "waiting": None,
     # the runbook (monitor/heal.py): what to start, and how long a run may take before it is hung
     "refill": ("write-scripts.yml", {}), "build": ("build-video.yml", {}), "upload": None,
     "build_hours_utc": (3, 18),            # What If starts builds 03:00-18:00 UTC only
     "hung_h": {"watchdog.yml": 6.2, "build-video.yml": 6.0}, "infra_fixes": "state/infra_fixes.json",
     "requeue": "whatif"},
    {"key": "closed-tabs", "name": "Closed Tabs", "repo": "edbackulin-eng/closed-tabs", "act": True,
     "slots": {"weekdays": [0, 1, 3, 4, 5], "time": "17:00", "tz": "UTC"},
     "paths": ["state", "topics/queue.json"],
     "watchdog": "watchdog.yml", "builds": ["daily.yml", "resume-episode.yml"], "heartbeat": "state/heartbeat.json",
     "scheduled": ct_scheduled, "failed": ct_failed, "topics": ct_topics, "waiting": None,
     "refill": ("topics.yml", {}), "build": ("daily.yml", {"upload": "true", "force_window": "false"}), "upload": None,
     "build_hours_utc": (20, 2),            # its GPU window opens at 20:00 UTC
     "hung_h": {"watchdog.yml": 6.2, "daily.yml": 13.0, "resume-episode.yml": 8.0},
     "infra_fixes": "state/infra_fixes.json", "requeue": None},
    {"key": "dinosaurs", "name": "Urzeit (dinosaurs)", "repo": "edbackulin-eng/prehistoric-channel", "act": True,
     "slots": {"weekdays": [2, 5], "time": "17:00", "tz": "Europe/Berlin"},
     "paths": ["state", "topics/queue.json"],
     "watchdog": "watchdog.yml", "builds": ["render.yml"], "heartbeat": "state/heartbeat.json",
     "scheduled": rows_scheduled, "failed": rows_failed, "topics": queue_topics, "waiting": rows_waiting,
     "refill": ("topics.yml", {}), "build": ("episode.yml", {}), "upload": None,
     "build_hours_utc": None,
     "hung_h": {"watchdog.yml": 6.2, "episode.yml": 6.2, "render.yml": 10.0, "ltx-extra.yml": 5.2},
     # a build started while one of these runs would push it out of their shared queue
     "busy_also": ["ltx-extra.yml", "episode.yml", "render.yml"],
     "infra_fixes": "state/infra_fixes.json", "requeue": None},
    {"key": "archive", "name": "Yesterday in Color", "repo": "edbackulin-eng/archive-channel", "act": True,
     "slots": {"weekdays": [1, 4], "time": "12:00", "tz": "America/New_York"},
     "paths": ["state", "topics/queue.json"],
     "watchdog": "watchdog.yml", "builds": ["episode.yml"], "heartbeat": "state/heartbeat.json",
     "scheduled": rows_scheduled, "failed": rows_failed, "topics": queue_topics, "waiting": rows_waiting,
     "refill": None, "build": ("episode.yml", {}), "upload": ("upload.yml", {}),
     "build_hours_utc": None,
     "hung_h": {"watchdog.yml": 6.2, "episode.yml": 13.5, "upload.yml": 2.0},
     "infra_fixes": "state/infra_fixes.json", "requeue": None},
    {"key": "stoic", "name": "Stoic (yt-factory-daily)", "repo": "beautyapp800-ctrl/yt-factory-daily", "act": False,
     "slots": {"weekdays": [0, 1, 2, 3, 4, 5, 6], "time": "21:00", "tz": "Europe/Kyiv"},
     "paths": ["data/factory.db"],
     # no watchdog of its own: its daily heartbeat workflow is what says it is alive
     "watchdog": "heartbeat.yml", "watchdog_max_h": 26,
     # it makes each video the day before its slot (every video so far: made on day D, out on
     # D+1), so one slot ahead is its normal state
     "buffer_min": 1, "builds": ["daily.yml", "daily-retry.yml"], "heartbeat": None,
     "scheduled": st_scheduled, "failed": st_failed, "topics": st_topics, "waiting": None,
     # read only: nothing is ever started, cancelled or changed in it
     "refill": None, "build": None, "upload": None, "hung_h": {}, "infra_fixes": None, "requeue": None},
]

# Kaggle's weekly GPU hours, shared by the channels: their ledgers (read from these checkouts)
GPU_LIMIT_H = 27.5
GPU_LEDGERS = [("closed-tabs", "state/gpu_ledger.json", "rows"), ("closed-tabs", "state/whatif_gpu.json", "keyed"),
               ("dinosaurs", "state/gpu_ledger.json", "rows")]
