"""Level 1: known failures, put right on every pass, nobody asked (the runbook).

For edbackulin-eng's channels (never the stoic one):
  hung      a run of a watched workflow going longer than its limit (channels.py "hung_h")
            is cancelled; a hung or dead watchdog is started again
  requeue   a failed episode whose error is one of the channel's fixed faults
            (state/infra_fixes.json) goes back to the queue
  topics    fewer than 10 topics: the channel's topic refill is started
  upload    a built video waiting in the buffer whose upload failed: upload again (the
            channel's own upload keeps its anti-duplicate)
  build     a buffer under 2 with no build going: the next episode's build is started,
            inside the hours the channel builds in
  planned   a dispatch planned for a given time (state "planned"), unless its slot is filled
Deferred, not failed: a 429, a spent quota, the GPU window or the week's budget (DEFER).
Every action goes into the journal (state/actions.json, README).
"""
import json
import re
from datetime import datetime, timedelta, timezone

DEFER = re.compile(r"\b429\b|quota|resource.?exhausted|too many requests|rate.?limit|outside the [\w -]*window|"
                   r"waits for the quota day|no free slot|deferred|GPU week nearly spent|retried later", re.I)
OWNER_TOKEN = re.compile(r"invalid_grant|token has been expired|expired or revoked|refresh token[^\n]*(expired|invalid)", re.I)
OWNER_KEY = re.compile(r"api key not valid|invalid api key|API_KEY_INVALID|\bunauthenticated\b|"
                       r"(GEMINI|GROQ|KAGGLE|PIXABAY)[A-Z_]* (is )?(not set|missing)", re.I)
ONCE_H = {"watchdog": 3, "build": 3, "topics": 12, "upload": 3, "cancel": 1, "requeue": 0.25}


def ts(s):
    return datetime.fromisoformat(str(s).replace("Z", "+00:00")) if s else None


def stamp(now):
    return now.strftime("%Y-%m-%dT%H:%M:%SZ")


def log(mem, now, ch, action, why, result, level=1):
    e = {"at": stamp(now), "channel": ch["key"], "level": level, "action": action, "why": why, "result": result}
    mem.setdefault("actions", []).append(e)
    mem["actions"] = mem["actions"][-500:]
    return e


def due(mem, ch, kind, now):
    last = ts(mem.get("done", {}).get(f"{ch['key']}:{kind}"))
    return last is None or now - last >= timedelta(hours=ONCE_H.get(kind, 3))


def mark(mem, ch, kind, now):
    mem.setdefault("done", {})[f"{ch['key']}:{kind}"] = stamp(now)


def runs(net, repo, wf, n=10):
    try:
        return net.get(f"repos/{repo}/actions/workflows/{wf}/runs?per_page={n}").get("workflow_runs", [])
    except OSError:
        return []


def busy(net, repo, wf):
    return any(r.get("status") in ("in_progress", "queued", "waiting", "pending", "requested") for r in runs(net, repo, wf, 5))


def in_hours(hours, now):
    if not hours:
        return True
    a, b = hours
    h = now.hour
    return a <= h < b if a < b else (h >= a or h < b)


def requeue_whatif(net, ch, root, now, done_before=()):
    """What If's queue/<slug>/episode.json: failed on a fixed fault -> ready-to-render."""
    fixes_p = root / ch["infra_fixes"]
    if not fixes_p.exists():
        return []
    fixes = json.loads(fixes_p.read_text(encoding="utf-8"))
    done = []
    for f in sorted((root / "queue").glob("*/episode.json")):
        e = json.loads(f.read_text(encoding="utf-8"))
        if e.get("status") != "failed" or f.parent.name in done_before:
            continue
        err = str(e.get("error") or "")
        when = ts(e.get("updated") or "1970-01-01T00:00:00+00:00")
        fix = next((x for x in fixes if ts(x["fixed_at"]) <= now and when < ts(x["fixed_at"])
                    and all(m in err for m in x["match"])), None)
        if not fix:
            continue
        path = f"queue/{f.parent.name}/episode.json"
        text, sha = net.get_file(ch["repo"], path, "main")
        cur = json.loads(text)
        if cur.get("status") != "failed":
            continue
        cur.pop("error", None)
        cur.update({"status": "ready-to-render", "requeued": f"{now:%Y-%m-%d}: failed on a fixed fault ({fix['fix']}); "
                    "the monitor put it back"})
        net.put_file(ch["repo"], path, json.dumps(cur, indent=2, ensure_ascii=False), sha,
                     f"monitor: requeue {f.parent.name} (its failure was fixed: {fix['fix']})", "main")
        done.append(f.parent.name)
    return done


def runbook(net, ch, res, root, mem, now):
    """The level-1 actions for one channel; returns the journal entries made."""
    if not ch.get("act"):
        return []
    made = []
    repo = ch["repo"]
    # hung runs: cancelled (a hung or dead watchdog is started again below)
    restart_watchdog = False
    for wf, limit in (ch.get("hung_h") or {}).items():
        for r in runs(net, repo, wf, 10):
            if r.get("status") not in ("in_progress", "queued", "waiting", "pending"):
                continue
            started = ts(r.get("run_started_at") or r.get("created_at"))
            seen = mem.setdefault("cancelled", [])
            if started and now - started > timedelta(hours=limit) and r["id"] not in seen:
                seen.append(r["id"])
                mem["cancelled"] = seen[-200:]
                try:
                    net.cancel(repo, r["id"])
                    result = "cancelled"
                except OSError as e:
                    result = f"could not cancel: {e}"
                made.append(log(mem, now, ch, f"cancel {wf} run {r['id']}",
                                f"running {round((now - started).total_seconds() / 3600, 1)} h (limit {limit} h)", result))
                restart_watchdog |= wf == ch["watchdog"]
    dead = any(k == "watchdog" for k, _ in res["problems"])
    if (dead or restart_watchdog) and due(mem, ch, "watchdog", now):
        made.append(log(mem, now, ch, f"start {ch['watchdog']}", "dead" if dead else "hung",
                        net.dispatch(repo, ch["watchdog"])))
        mark(mem, ch, "watchdog", now)
    # failed episodes whose fault has been fixed: back to the queue
    if ch.get("requeue") == "whatif" and root is not None and due(mem, ch, "requeue", now):
        try:
            back = [s for s in requeue_whatif(net, ch, root, now, set(mem.get("requeued", [])))]
            mem["requeued"] = (mem.get("requeued", []) + back)[-200:]
        except OSError as e:
            back = []
            made.append(log(mem, now, ch, "requeue", "fixed faults", f"could not write: {e}"))
        for slug in back:
            made.append(log(mem, now, ch, f"requeue {slug}", "failed on a fault that has been fixed", "ready-to-render"))
        mark(mem, ch, "requeue", now)
    # topics
    if ch.get("refill") and res.get("topics") is not None and res["topics"] < 10 and due(mem, ch, "topics", now):
        wf, inputs = ch["refill"]
        if not busy(net, repo, wf):
            made.append(log(mem, now, ch, f"start {wf}", f"{res['topics']} topics left", net.dispatch(repo, wf, inputs)))
            mark(mem, ch, "topics", now)
    # a built video whose upload failed
    if ch.get("upload") and (res.get("waiting_built") or 0) > 0 and due(mem, ch, "upload", now):
        wf, inputs = ch["upload"]
        last = next(iter(runs(net, repo, wf, 3)), None)
        if last is None or (last.get("status") == "completed" and last.get("conclusion") != "success"):
            made.append(log(mem, now, ch, f"start {wf}", f"{res['waiting_built']} built video(s) not uploaded, last upload "
                            f"{(last or {}).get('conclusion') or 'never ran'}", net.dispatch(repo, wf, inputs)))
            mark(mem, ch, "upload", now)
    # the buffer
    short = res.get("buffer", 3) < ch.get("buffer_min", 2)
    if short and ch.get("build") and due(mem, ch, "build", now) and in_hours(ch.get("build_hours_utc"), now):
        wf, inputs = ch["build"]
        if not any(busy(net, repo, b) for b in {wf, *ch["builds"], *ch.get("busy_also", [])}):
            made.append(log(mem, now, ch, f"start {wf}", f"{res['buffer']} of the next 3 slots have a video",
                            net.dispatch(repo, wf, inputs)))
            mark(mem, ch, "build", now)
    return made


def planned(net, mem, results, now):
    """Dispatches planned for a time (state "planned"): fired once when due, unless the slot they
    are for already has its video."""
    made = []
    for p in mem.get("planned", []):
        if p.get("done") or ts(p["at"]) > now:
            continue
        res = next((r for r in results if r["repo"] == p["repo"]), {})
        ch = {"key": res.get("key", p["repo"])}
        filled = any(s["at"].startswith(p.get("unless_slot_filled", "~")) and s.get("video") for s in res.get("slots", []))
        if filled:
            p["done"] = stamp(now)
            made.append(log(mem, now, ch, f"planned {p['workflow']}", p.get("why", ""), "not needed: its slot is filled"))
            continue
        if any(r.get("status") in ("in_progress", "queued") for r in runs(net, p["repo"], p["workflow"], 3)):
            result = "already running"
        else:
            result = net.dispatch(p["repo"], p["workflow"], p.get("inputs") or {})
        p["done"] = stamp(now)
        made.append(log(mem, now, ch, f"planned {p['workflow']}", p.get("why", ""), result))
    return made


def classify(text):
    """'defer' (quota, window, budget: not a failure), 'token' / 'key' (only the owner can),
    or None (a failure)."""
    t = text or ""
    if OWNER_TOKEN.search(t):
        return "token"
    if OWNER_KEY.search(t):
        return "key"
    if DEFER.search(t):
        return "defer"
    return None
