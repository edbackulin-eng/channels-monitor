"""One pass over every channel: what is scheduled, what is alive, what failed, what to do.

    python monitor/check.py                 # a pass: README.md, state/monitor.json, a letter on a new alarm
    python monitor/check.py --summary       # the same, and the daily summary when it is 07:00-10:00 in Kyiv
    python monitor/check.py --fixtures DIR  # offline, on fake data (scripts/smoke.py)

Per channel (monitor/channels.py; the channels' repositories are only read):
  buffer    the next three slots of its schedule, and which have a video; fewer than 2 -> alarm
  watchdog  hours since it last showed life (a run going, a run ended, a heartbeat commit);
            over 3 h -> alarm (the stoic channel has a daily heartbeat instead: over 26 h)
  build     hours since its last successful build; over 36 h -> alarm; the failed step of a
            build that failed last
  failed    episodes that failed or failed QA, with the reason; the same reason in two or
            more channels is marked shared
  topics    topics left to build; under 10 -> alarm
  GPU       the Kaggle week (the channels' ledgers, last 7 days) against 27.5 h
Actions: for edbackulin-eng's channels, a dead watchdog or a buffer under 2 starts that
channel's watchdog.yml (at most once in 3 h a channel; needs MONITOR_TOKEN). The stoic
channel is only reported.
Letters: one issue, "Monitor"; a comment mentioning the owner is an email - once for every
new alarm (not again until it has cleared), and the daily summary.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from monitor import channels as C  # noqa: E402

OWNER = "edbackulin-eng"
ISSUE_TITLE = "Monitor"
KYIV = ZoneInfo("Europe/Kyiv")
BUFFER_MIN, WATCHDOG_MAX_H, BUILD_MAX_H, TOPICS_MIN = 2, 3.0, 36.0, 10
DISPATCH_EVERY_H = 3.0
PASS_EVERY_H = 3.0
API = "https://api.github.com/"


class Net:
    """GitHub, read with GITHUB_TOKEN; writes to other repositories with MONITOR_TOKEN."""

    def __init__(self):
        self.read = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
        self.write = os.environ.get("MONITOR_TOKEN") or ""
        self.repo = os.environ.get("GITHUB_REPOSITORY", "edbackulin-eng/channels-monitor")

    def call(self, path, data=None, token=None, method=None):
        req = urllib.request.Request(API + path, data=json.dumps(data).encode() if data is not None else None,
                                     method=method or ("POST" if data is not None else "GET"),
                                     headers={"Accept": "application/vnd.github+json", "User-Agent": "channels-monitor",
                                              **({"Authorization": f"Bearer {token or self.read}"}
                                                 if (token or self.read) else {})})
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
        return json.loads(body) if body.strip() else {}

    def get(self, path):
        return self.call(path)

    def checkout(self, ch, work):
        dest = Path(work) / ch["key"]
        if dest.exists():
            subprocess.run(["git", "-C", str(dest), "pull", "-q", "--depth", "1"], capture_output=True)
            return dest
        url = f"https://github.com/{ch['repo']}.git"
        subprocess.run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--sparse", url, str(dest)],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(dest), "sparse-checkout", "set", "--no-cone", *[f"/{p}" for p in ch["paths"]]],
                       check=True, capture_output=True)
        return dest

    def dispatch(self, repo, workflow):
        if not self.write:
            return "no MONITOR_TOKEN: cannot start it"
        self.call(f"repos/{repo}/actions/workflows/{workflow}/dispatches", {"ref": "main"}, token=self.write)
        return "started"

    issue = None                     # its number, kept in state/monitor.json ("issue")

    def comment(self, body):
        # the number is kept: right after an issue is made, the list does not show it yet, and
        # a second letter in the same pass made a second "Monitor" (05.11)
        n = self.issue
        if n is None:
            issues = self.get(f"repos/{self.repo}/issues?state=open&per_page=50")
            n = min((i["number"] for i in issues if i.get("title") == ISSUE_TITLE and "pull_request" not in i),
                    default=None)
        if n is None:
            n = self.call(f"repos/{self.repo}/issues", {"title": ISSUE_TITLE, "body":
                          "Letters from the channels monitor: a comment here that mentions the owner arrives as an email."})["number"]
        self.call(f"repos/{self.repo}/issues/{n}/comments", {"body": body})
        self.issue = n


class Offline(Net):
    """The smoke test's world: checkouts are fixture folders, API answers come from api.json,
    and what would be written goes to sent.json."""

    def __init__(self, fixtures):
        super().__init__()
        self.dir = Path(fixtures)
        self.answers = json.loads((self.dir / "api.json").read_text(encoding="utf-8"))
        self.write = "fake"
        self.sent = []

    def get(self, path):
        for k, v in self.answers.items():
            if path.startswith(k):
                return v
        return {}

    def checkout(self, ch, work):
        return self.dir / ch["key"]

    def dispatch(self, repo, workflow):
        self.sent.append({"dispatch": f"{repo}/{workflow}"})
        return "started"

    def comment(self, body):
        self.sent.append({"comment": body})


def ts(s):
    return datetime.fromisoformat(str(s).replace("Z", "+00:00")) if s else None


def next_slots(spec, now, n=3):
    tz = ZoneInfo(spec["tz"])
    hh, mm = (int(x) for x in spec["time"].split(":"))
    d = now.astimezone(tz).date()
    out = []
    while len(out) < n:
        s = datetime(d.year, d.month, d.day, hh, mm, tzinfo=tz)
        if s.weekday() in spec["weekdays"] and s.astimezone(timezone.utc) > now:
            out.append(s.astimezone(timezone.utc))
        d += timedelta(days=1)
    return out


def fill(slots, scheduled, tz):
    """For every slot, the video scheduled on its day (local), or None."""
    z = ZoneInfo(tz)
    by_day = {}
    for when, vid, title in scheduled:
        by_day.setdefault(when.astimezone(z).date(), (when, vid, title))
    return [(s, by_day.get(s.astimezone(z).date())) for s in slots]


def age_h(now, t):
    return None if t is None else round((now - t).total_seconds() / 3600, 1)


def watchdog_seen(net, ch, now):
    """The last sign of life of the channel's watchdog: a run going (now), a run's end, a
    heartbeat commit."""
    seen = []
    try:
        runs = net.get(f"repos/{ch['repo']}/actions/workflows/{ch['watchdog']}/runs?per_page=5").get("workflow_runs", [])
    except (urllib.error.URLError, OSError):
        runs = []
    for r in runs:
        if r.get("status") in ("in_progress", "queued", "waiting", "pending", "requested"):
            seen.append(now)
        elif r.get("updated_at"):
            seen.append(ts(r["updated_at"]))
    if ch.get("heartbeat"):
        try:
            c = net.get(f"repos/{ch['repo']}/commits?path={ch['heartbeat']}&per_page=1")
            if isinstance(c, list) and c:
                seen.append(ts(c[0]["commit"]["committer"]["date"]))
        except (urllib.error.URLError, OSError):
            pass
    return max(seen) if seen else None


def builds(net, ch):
    """(last success time, the failed step of the last build if it failed)."""
    ok, last_fail = None, None
    latest = []
    for wf in ch["builds"]:
        try:
            rs = net.get(f"repos/{ch['repo']}/actions/workflows/{wf}/runs?per_page=10").get("workflow_runs", [])
        except (urllib.error.URLError, OSError):
            continue
        for r in rs:
            if r.get("conclusion") == "success":
                t = ts(r.get("updated_at"))
                ok = t if ok is None or t > ok else ok
        done = [r for r in rs if r.get("status") == "completed"]
        if done:
            latest.append(done[0])
    latest.sort(key=lambda r: r.get("updated_at") or "", reverse=True)
    if latest and latest[0].get("conclusion") == "failure":
        r = latest[0]
        step = "?"
        try:
            jobs = net.get(f"repos/{ch['repo']}/actions/runs/{r['id']}/jobs").get("jobs", [])
            for j in jobs:
                bad = [s["name"] for s in j.get("steps", []) if s.get("conclusion") == "failure"]
                if bad:
                    step = f"{j['name']} / {bad[0]}"
                    break
        except (urllib.error.URLError, OSError):
            pass
        last_fail = {"run": r.get("html_url"), "step": step, "at": r.get("updated_at")}
    return ok, last_fail


def gpu_week(roots, now):
    since = now - timedelta(days=7)
    total, parts = 0.0, {}
    for key, path, kind in C.GPU_LEDGERS:
        data = C._json(roots.get(key, Path("/nonexistent")), path, None)
        if data is None:
            continue
        h = 0.0
        if kind == "rows":
            for r in data:
                t = ts(r.get("start"))
                if t and t >= since:
                    h += float(r.get("hours") or 0)
        else:                                     # {"ref@start": hours}
            for k, v in data.items():
                t = ts(k.split("@", 1)[-1]) if "@" in k else None
                if t and t >= since:
                    h += float(v or 0)
        name = "What If" if "whatif" in path else key
        parts[name] = round(parts.get(name, 0) + h, 2)
        total += h
    return round(total, 2), parts


def norm(reason):
    """An error's text without the parts that differ from one run to the next."""
    r = re.sub(r"^\s*(qa-failed|failed)\s*:\s*", "", str(reason).lower())
    r = re.sub(r"https?://\S+|/[\w./-]+|[a-z]:\\\S+", " ", r)
    r = re.sub(r"\d+", "#", r)
    return re.sub(r"\s+", " ", r).strip()[:160]


def look(net, ch, now, work):
    out = {"key": ch["key"], "name": ch["name"], "repo": ch["repo"], "problems": []}
    try:
        root = net.checkout(ch, work)
    except subprocess.CalledProcessError as e:
        out["problems"].append(("read", f"could not read the repository: {e}"))
        return out, None
    sched = sorted(x for x in ch["scheduled"](root) if x[0] and x[0] > now)
    slots = fill(next_slots(ch["slots"], now), sched, ch["slots"]["tz"])
    out["slots"] = [{"at": s.strftime("%Y-%m-%dT%H:%MZ"), "video": (v[1] if v else None),
                     "title": (v[2] if v else None)} for s, v in slots]
    out["buffer"] = sum(1 for _, v in slots if v)
    out["scheduled_ahead"] = len(sched)
    out["waiting"] = ch["waiting"](root) if ch.get("waiting") else None
    seen = watchdog_seen(net, ch, now)
    out["watchdog_h"] = age_h(now, seen)
    ok, fail = builds(net, ch)
    out["build_h"] = age_h(now, ok)
    out["last_build_failed"] = fail
    out["failed"] = [{"episode": e, "reason": r} for e, r in ch["failed"](root)]
    out["topics"] = ch["topics"](root)
    # the alarms
    if out["buffer"] < ch.get("buffer_min", BUFFER_MIN):
        out["problems"].append(("buffer", f"{out['buffer']} of the next 3 slots have a video"
                                + (f" ({out['waiting']} waiting for approval or a slot)" if out.get("waiting") else "")))
    wmax = ch.get("watchdog_max_h", WATCHDOG_MAX_H)
    if out["watchdog_h"] is None or out["watchdog_h"] > wmax:
        out["problems"].append(("watchdog", f"no sign of life for {out['watchdog_h']} h (max {wmax:g})"))
    if out["build_h"] is None or out["build_h"] > BUILD_MAX_H:
        out["problems"].append(("build", f"last successful build {out['build_h']} h ago" if out["build_h"] is not None
                                else "no successful build yet"))
    if fail:
        out["problems"].append(("build-failed", f"last build failed at {fail['step']}"))
    for f in out["failed"]:
        out["problems"].append((f"failed:{f['episode']}", f"{f['episode']}: {str(f['reason'])[:160]}"))
    if out["topics"] is not None and out["topics"] < TOPICS_MIN:
        out["problems"].append(("topics", f"{out['topics']} topics left (min {TOPICS_MIN})"))
    return out, root


def act(net, ch, res, mem, now):
    """Start the channel's watchdog when it is dead or the buffer is short (edbackulin-eng's only)."""
    if not ch["act"]:
        return None
    kinds = {k for k, _ in res["problems"]}
    if not ({"watchdog", "buffer"} & kinds):
        return None
    last = ts(mem.get("dispatched", {}).get(ch["key"]))
    if last and now - last < timedelta(hours=DISPATCH_EVERY_H):
        return f"watchdog started {age_h(now, last)} h ago; not again yet"
    try:
        what = net.dispatch(ch["repo"], ch["watchdog"])
    except (urllib.error.URLError, OSError) as e:
        return f"could not start the watchdog: {e}"
    if what == "started":
        mem.setdefault("dispatched", {})[ch["key"]] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"watchdog.yml: {what}"


def slot_text(s, tz):
    t = ts(s["at"]).astimezone(ZoneInfo(tz))
    return f"{t:%d.%m %H:%M} {'✓' if s['video'] else '✗'}"


def readme(results, gpu, shared, now):
    lines = ["# Channels monitor", "",
             f"Updated {now.astimezone(KYIV):%d.%m.%Y %H:%M} Kyiv ({now:%H:%M} UTC). A pass every 3 hours; "
             "letters go to the issue **Monitor**.", "",
             "| Channel | | Next 3 slots (local time) | Buffer | Watchdog | Last good build | Topics | What is wrong |",
             "|---|---|---|---|---|---|---|---|"]
    for r in results:
        ch = next(c for c in C.CHANNELS if c["key"] == r["key"])
        slots = ", ".join(slot_text(s, ch["slots"]["tz"]) for s in r.get("slots", []))
        bad = "; ".join(t for _, t in r["problems"]) or "—"
        lines.append(f"| [{r['name']}](https://github.com/{r['repo']}) | {'✓' if not r['problems'] else '✗'} | {slots} | "
                     f"{r.get('buffer', '?')}/3 | {r.get('watchdog_h', '?')} h | {r.get('build_h', '?')} h | "
                     f"{'generates' if r.get('topics') is None else r.get('topics')} | {bad} |")
    lines += ["", f"**Kaggle GPU, last 7 days:** {gpu[0]} h of {C.GPU_LIMIT_H} h "
                  f"({', '.join(f'{k} {v} h' for k, v in gpu[1].items())})."]
    if shared:
        lines += ["", "**The same error in more than one channel:**"] + [f"- {t} ({', '.join(cs)})" for t, cs in shared]
    return "\n".join(lines) + "\n"


def summary(results, gpu, now):
    rows = [f"@{OWNER} **Channels, {now.astimezone(KYIV):%d.%m.%Y}**", ""]
    for r in results:
        ch = next(c for c in C.CHANNELS if c["key"] == r["key"])
        slots = ", ".join(slot_text(s, ch["slots"]["tz"]) for s in r.get("slots", []))
        bad = "; ".join(t for _, t in r["problems"]) or "all well"
        rows.append(f"- {'✓' if not r['problems'] else '✗'} **{r['name']}** — {slots} — {bad}")
    rows += ["", f"GPU week: {gpu[0]} h of {C.GPU_LIMIT_H} h."]
    return "\n".join(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--fixtures")
    ap.add_argument("--now")
    ap.add_argument("--out", default=str(ROOT))
    ap.add_argument("--due", action="store_true",
                    help="only when a pass is due (3 h since the last) or the summary is (07:00-10:00 Kyiv)")
    args = ap.parse_args(argv)
    now = ts(args.now) if args.now else datetime.now(timezone.utc)
    out = Path(args.out)
    state_p = out / "state" / "monitor.json"
    mem = json.loads(state_p.read_text(encoding="utf-8")) if state_p.exists() else {}
    if args.due:
        last = ts(mem.get("last_pass"))
        pass_due = last is None or now - last >= timedelta(hours=PASS_EVERY_H) - timedelta(minutes=5)
        summary_due = 7 <= now.astimezone(KYIV).hour < 10 and mem.get("summary_date") != now.astimezone(KYIV).strftime("%Y-%m-%d")
        if not (pass_due or summary_due):
            print(f"not due: last pass {mem.get('last_pass')}, summary sent {mem.get('summary_date')}")
            return 0
        args.summary = args.summary or summary_due
    net = Offline(args.fixtures) if args.fixtures else Net()
    net.issue = mem.get("issue")
    work = out / "work"
    results, roots = [], {}
    for ch in C.CHANNELS:
        res, root = look(net, ch, now, work)
        if root is not None:
            roots[ch["key"]] = root
        res["action"] = act(net, ch, res, mem, now)
        results.append(res)
    gpu = gpu_week(roots, now)
    # one error in two or more channels: shared
    by_text = {}
    for r in results:
        reasons = [f["reason"] for f in r.get("failed", [])]
        if r.get("last_build_failed"):
            reasons.append(r["last_build_failed"]["step"])
        for reason in reasons:
            by_text.setdefault(norm(reason), set()).add(r["name"])
    shared = [(t, sorted(cs)) for t, cs in by_text.items() if len(cs) >= 2 and t]
    for t, cs in shared:
        for r in results:
            if r["name"] in cs:
                r["problems"].append((f"shared:{hashlib.sha1(t.encode()).hexdigest()[:8]}",
                                      f"shared with {', '.join(c for c in cs if c != r['name'])}: {t[:80]}"))
    alarms = {}
    for r in results:
        for k, text in r["problems"]:
            alarms[f"{r['key']}:{k}"] = f"{r['name']}: {text}"
    if gpu[0] > C.GPU_LIMIT_H:
        alarms["gpu:week"] = f"Kaggle GPU week {gpu[0]} h, over {C.GPU_LIMIT_H} h"
    before = set(mem.get("alarms", {}))
    new = {k: v for k, v in alarms.items() if k not in before}
    sent = []
    if new:
        body = (f"@{OWNER} **New alarm{'s' if len(new) > 1 else ''}**\n\n" + "\n".join(f"- {v}" for v in new.values())
                + "".join(f"\n- action: {r['name']}: {r['action']}" for r in results
                          if r.get("action") and r["key"] in {k.split(":", 1)[0] for k in new}))
        try:
            net.comment(body)
            sent.append("alarm")
        except (urllib.error.URLError, OSError) as e:
            print(f"could not write the issue: {e}")
            new = {}
    today = now.astimezone(KYIV).strftime("%Y-%m-%d")
    if args.summary and 7 <= now.astimezone(KYIV).hour < 10 and mem.get("summary_date") != today:
        try:
            net.comment(summary(results, gpu, now))
            mem["summary_date"] = today
            sent.append("summary")
        except (urllib.error.URLError, OSError) as e:
            print(f"could not write the summary: {e}")
    # an alarm stays known until it clears (no second letter); a letter that failed is tried again
    mem["alarms"] = {k: v for k, v in alarms.items() if k in before or k in new}
    mem["last_pass"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    if net.issue:
        mem["issue"] = net.issue
    state_p.parent.mkdir(parents=True, exist_ok=True)
    state_p.write_text(json.dumps(mem, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "state" / "channels.json").write_text(json.dumps({"at": mem["last_pass"], "channels": results,
                                                             "gpu": {"hours": gpu[0], "parts": gpu[1]},
                                                             "shared": shared}, indent=1, ensure_ascii=False,
                                                            default=str), encoding="utf-8")
    (out / "README.md").write_text(readme(results, gpu, shared, now), encoding="utf-8")
    if isinstance(net, Offline):
        (out / "sent.json").write_text(json.dumps(net.sent, indent=1, ensure_ascii=False), encoding="utf-8")
    for r in results:
        print(f"{'OK ' if not r['problems'] else 'BAD'} {r['name']}: buffer {r.get('buffer')}/3, watchdog {r.get('watchdog_h')} h, "
              f"build {r.get('build_h')} h, topics {r.get('topics')}; {'; '.join(t for _, t in r['problems']) or 'all well'}")
    print(f"GPU week {gpu[0]} h {gpu[1]}; new alarms {len(new)}; sent {sent or 'nothing'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
