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
  smoke     the channel's smoke test on dev red for more than 12 h -> a letter (owner 06.11)
  rights    what MONITOR_TOKEN may write (Contents, Workflows), probed without writing
Putting things right (edbackulin-eng's channels; the stoic one is only reported):
  level 1  known failures, every pass (monitor/heal.py)
  level 2  a new failure seen twice: an automatic patch, tested, merged or undone (monitor/autofix.py)
Every action goes into the journal (state/actions.json, README.md).
Letters: one issue, "Monitor"; a comment mentioning the owner is an email - only when the
owner is needed (a YouTube token, a key, a patch undone, nothing for tomorrow's slot), once
until it clears, and the morning summary with what was put right.
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
SMOKE_RED_MAX_H = 12.0              # owner 06.11: a channel's dev smoke red longer than this -> a letter
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
        if token is not None and not token:
            # a write without MONITOR_TOKEN never falls back to the read token
            raise OSError("no MONITOR_TOKEN for this write")
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
            # a shallow clone is moved to the newest commit by fetch + reset: "pull --depth 1" can
            # fail without a word, and a pass then read hours-old state (05.11: What If's video for
            # 07.11 was on main, the monitor saw the slot empty and tried to start a build)
            f = subprocess.run(["git", "-C", str(dest), "fetch", "-q", "--depth", "1", "origin", "HEAD"],
                               capture_output=True)
            r = subprocess.run(["git", "-C", str(dest), "reset", "-q", "--hard", "FETCH_HEAD"], capture_output=True)
            if f.returncode == 0 and r.returncode == 0:
                return dest
            import shutil
            shutil.rmtree(dest, ignore_errors=True)       # cannot be moved on: cloned again
        url = f"https://github.com/{ch['repo']}.git"
        subprocess.run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--sparse", url, str(dest)],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(dest), "sparse-checkout", "set", "--no-cone", *[f"/{p}" for p in ch["paths"]]],
                       check=True, capture_output=True)
        return dest

    rights_seen = None               # {repo: {"contents": bool|None, "workflows": bool|None}}, once a pass

    def can_write(self, repo=None, what="contents"):
        if not self.write:
            return False
        if repo is None or not self.rights_seen or repo not in self.rights_seen:
            return True
        return bool(self.rights_seen[repo].get(what))

    def _probe(self, repo, path):
        """True if MONITOR_TOKEN may write this existing file, found without writing it: a PUT
        with a sha that cannot be the file's is refused with 409 when the token may write
        there, 403 (or 404) when it may not. None: no answer."""
        import base64
        try:
            self.call(f"repos/{repo}/contents/{path}", {"message": "monitor: rights probe (never applied)",
                                                        "content": base64.b64encode(b"probe").decode(),
                                                        "sha": "0" * 40}, token=self.write, method="PUT")
        except urllib.error.HTTPError as e:
            return True if e.code in (409, 422) else False if e.code in (401, 403, 404) else None
        except (urllib.error.URLError, OSError):
            return None
        return None                  # never accepted: the sha cannot match

    def rights(self, repo):
        """{"contents": ..., "workflows": ...} MONITOR_TOKEN has in a repository (owner 06.11)."""
        if not self.write:
            return {"contents": False, "workflows": False}
        out = {"contents": None, "workflows": None}
        try:
            top = self.get(f"repos/{repo}/contents/")
            f = next((x["path"] for x in top if x.get("type") == "file"), None)
            wfs = self.get(f"repos/{repo}/contents/.github/workflows")
            w = next((x["path"] for x in wfs if x.get("type") == "file" and x["name"].endswith((".yml", ".yaml"))), None)
        except (urllib.error.URLError, OSError, TypeError):
            return out
        if f:
            out["contents"] = self._probe(repo, f)
        if w:
            out["workflows"] = self._probe(repo, w)
        return out

    def dispatch(self, repo, workflow, inputs=None, ref="main"):
        if not self.write:
            return "no MONITOR_TOKEN: cannot start it"
        self.call(f"repos/{repo}/actions/workflows/{workflow}/dispatches",
                  {"ref": ref, **({"inputs": inputs} if inputs else {})}, token=self.write)
        return "started"

    def cancel(self, repo, run_id):
        self.call(f"repos/{repo}/actions/runs/{run_id}/cancel", {}, token=self.write)

    def job_log(self, repo, job_id, tail=6000):
        """The end of a job's log (GitHub answers with a redirect to the text)."""
        req = urllib.request.Request(API + f"repos/{repo}/actions/jobs/{job_id}/logs",
                                     headers={"Authorization": f"Bearer {self.read}", "User-Agent": "channels-monitor"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read()[-tail * 2:].decode("utf-8", "replace")[-tail:]

    def get_file(self, repo, path, ref):
        import base64
        d = self.call(f"repos/{repo}/contents/{path}?ref={ref}", token=self.write or None)
        return base64.b64decode(d["content"]).decode("utf-8"), d["sha"]

    def put_file(self, repo, path, text, sha, message, branch):
        import base64
        self.call(f"repos/{repo}/contents/{path}", {"message": message, "branch": branch,
                                                     "content": base64.b64encode(text.encode()).decode(),
                                                     **({"sha": sha} if sha else {})}, token=self.write, method="PUT")

    def branch(self, repo, name, base):
        sha = self.call(f"repos/{repo}/git/ref/heads/{base}", token=self.write)["object"]["sha"]
        self.call(f"repos/{repo}/git/refs", {"ref": f"refs/heads/{name}", "sha": sha}, token=self.write)

    def merge(self, repo, base, head, message):
        self.call(f"repos/{repo}/merges", {"base": base, "head": head, "commit_message": message}, token=self.write)

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

    def rights(self, repo):
        return self.answers.get("rights", {}).get(repo, {"contents": True, "workflows": True})

    def dispatch(self, repo, workflow, inputs=None, ref="main"):
        self.sent.append({"dispatch": f"{repo}/{workflow}", **({"inputs": inputs} if inputs else {})})
        return "started"

    def cancel(self, repo, run_id):
        self.sent.append({"cancel": f"{repo}/{run_id}"})

    def job_log(self, repo, job_id, tail=6000):
        return self.answers.get(f"log:{repo}:{job_id}", "")

    def get_file(self, repo, path, ref):
        files = self.answers.get("files", {})
        k = f"{repo}:{ref}:{path}"
        k = k if k in files else f"{repo}:*:{path}"
        if k not in files:
            raise OSError(f"404 {repo} {path}")
        return files[k], "sha-" + str(len(files[k]))

    def put_file(self, repo, path, text, sha, message, branch):
        self.sent.append({"put": f"{repo}:{branch}:{path}", "message": message})
        self.answers.setdefault("files", {})[f"{repo}:{branch}:{path}"] = text

    def branch(self, repo, name, base):
        self.sent.append({"branch": f"{repo}:{name}<-{base}"})

    def merge(self, repo, base, head, message):
        self.sent.append({"merge": f"{repo}:{head}->{base}"})

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


def failure_of(net, ch, r):
    """{run, step, at, tail, kind} of a failed run: its failed job's step and the end of its log;
    kind: 'defer' (quota, window, budget), 'token' / 'key' (the owner's), or None."""
    from monitor import heal
    step, tail = "?", ""
    try:
        for j in net.get(f"repos/{ch['repo']}/actions/runs/{r['id']}/jobs").get("jobs", []):
            bad = [s["name"] for s in j.get("steps", []) if s.get("conclusion") == "failure"]
            if bad:
                step = f"{j['name']} / {bad[0]}"
                try:
                    tail = net.job_log(ch["repo"], j["id"])
                except (urllib.error.URLError, OSError):
                    tail = ""
                break
    except (urllib.error.URLError, OSError):
        pass
    return {"run": r.get("html_url"), "id": r.get("id"), "step": step, "at": r.get("updated_at"),
            "tail": tail, "kind": heal.classify(tail), "workflow": r.get("path")}


def builds(net, ch, now=None, max_failures=4):
    """(last success time, the last build's failure if it failed, failed builds of the last 72 h)."""
    ok = None
    latest, failed = [], []
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
        failed += [r for r in done if r.get("conclusion") == "failure"
                   and (now is None or now - ts(r.get("updated_at")) <= timedelta(hours=72))]
    latest.sort(key=lambda r: r.get("updated_at") or "", reverse=True)
    failed.sort(key=lambda r: r.get("updated_at") or "", reverse=True)
    fails = [failure_of(net, ch, r) for r in failed[:max_failures]]
    last_fail = None
    if latest and latest[0].get("conclusion") == "failure":
        last_fail = next((f for f in fails if f["id"] == latest[0].get("id")), None) or failure_of(net, ch, latest[0])
    return ok, last_fail, fails


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


def smoke_red_since(net, ch):
    """When the channel's smoke test on dev turned red and stayed red (None: green, or no smoke).
    Its runs on dev only - the monitor's own autofix branches are tested by the same workflow."""
    try:
        rs = net.get(f"repos/{ch['repo']}/actions/workflows/{ch.get('smoke', 'smoke.yml')}/runs?per_page=30")             .get("workflow_runs", [])
    except (urllib.error.URLError, OSError):
        return None
    dev = sorted((r for r in rs if r.get("status") == "completed" and r.get("conclusion") in ("success", "failure")
                  and r.get("head_branch") == "dev" and not str(r.get("display_title") or "").startswith("smoke autofix/")),
                 key=lambda r: r.get("created_at") or "", reverse=True)
    since = None
    for r in dev:
        if r.get("conclusion") == "success":
            break
        since = ts(r.get("created_at"))
    return since


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
    ok, fail, fails = builds(net, ch, now)
    out["build_h"] = age_h(now, ok)
    out["last_build_failed"] = {k: v for k, v in fail.items() if k != "tail"} if fail else None
    out["failures"] = fails
    out["waiting_built"] = C.rows_built(root) if ch.get("upload") else 0
    # what only the owner can put right
    out["owner"] = []
    for f in fails:
        if f["kind"] == "token":
            out["owner"].append(("token", "the YouTube token is expired or revoked: authorise it again"))
        elif f["kind"] == "key":
            out["owner"].append(("key", f"a key is missing or refused ({f['step']})"))
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
    if fail and fail["kind"] == "defer":
        out["deferred"] = f"last build waits (quota, GPU window or budget) at {fail['step']}"
    elif fail:
        out["problems"].append(("build-failed", f"last build failed at {fail['step']}"))
    # owner 06.11: the dev smoke red for more than 12 h - nothing on dev reaches main
    red = smoke_red_since(net, ch) if ch.get("act") else None
    if red is not None and now - red > timedelta(hours=SMOKE_RED_MAX_H):
        out["owner"].append(("smoke-red", f"the smoke test on dev has been red for {age_h(now, red)} h "
                             f"(since {red:%d.%m %H:%M} UTC): what is on dev does not reach main"))
    for k, text in out["owner"]:
        out["problems"].append((f"owner-{k}", text))
    # tomorrow's slot empty and nothing scheduled: only the owner can still save it
    if out["slots"] and not out["slots"][0]["video"] and out["buffer"] == 0 \
            and ts(out["slots"][0]["at"]) - now <= timedelta(hours=36):
        out["owner"].append(("buffer0", f"nothing for the next slot ({out['slots'][0]['at']}) and no video ahead"))
    for f in out["failed"]:
        out["problems"].append((f"failed:{f['episode']}", f"{f['episode']}: {str(f['reason'])[:160]}"))
    if out["topics"] is not None and out["topics"] < TOPICS_MIN:
        out["problems"].append(("topics", f"{out['topics']} topics left (min {TOPICS_MIN})"))
    return out, root


def slot_text(s, tz):
    t = ts(s["at"]).astimezone(ZoneInfo(tz))
    return f"{t:%d.%m %H:%M} {'✓' if s['video'] else '✗'}"


def readme(results, gpu, shared, now, journal):
    lines = ["# Channels monitor", "",
             f"Updated {now.astimezone(KYIV):%d.%m.%Y %H:%M} Kyiv ({now:%H:%M} UTC). A pass every 3 hours; known "
             "failures are put right by themselves (level 1), a new one seen twice gets an automatic patch "
             "(level 2); letters go to the issue **Monitor** only when the owner is needed.", "",
             "| Channel | | Next 3 slots (local time) | Buffer | Watchdog | Last good build | Topics | What is wrong |",
             "|---|---|---|---|---|---|---|---|"]
    for r in results:
        ch = next(c for c in C.CHANNELS if c["key"] == r["key"])
        slots = ", ".join(slot_text(s, ch["slots"]["tz"]) for s in r.get("slots", []))
        bad = "; ".join([t for _, t in r["problems"]] + ([r["deferred"]] if r.get("deferred") else [])) or "—"
        lines.append(f"| [{r['name']}](https://github.com/{r['repo']}) | {'✓' if not r['problems'] else '✗'} | {slots} | "
                     f"{r.get('buffer', '?')}/3 | {r.get('watchdog_h', '?')} h | {r.get('build_h', '?')} h | "
                     f"{'generates' if r.get('topics') is None else r.get('topics')} | {bad} |")
    lines += ["", f"**Kaggle GPU, last 7 days:** {gpu[0]} h of {C.GPU_LIMIT_H} h "
                  f"({', '.join(f'{k} {v} h' for k, v in gpu[1].items())})."]
    if shared:
        lines += ["", "**The same error in more than one channel:**"] + [f"- {t} ({', '.join(cs)})" for t, cs in shared]
    day = [e for e in journal if ts(e["at"]) >= now - timedelta(hours=24)]
    lines += ["", "## Journal (last 24 h)", ""]
    if day:
        lines += ["| UTC | Channel | Level | Action | Why | Result |", "|---|---|---|---|---|---|"]
        lines += [f"| {e['at'][5:16].replace('T', ' ')} | {e['channel']} | {e['level']} | {e['action']} | "
                  f"{str(e['why'])[:90]} | {str(e['result'])[:90]} |" for e in reversed(day)]
    else:
        lines.append("Nothing needed doing.")
    return "\n".join(lines) + "\n"


def summary(results, gpu, now, journal):
    rows = [f"@{OWNER} **Channels, {now.astimezone(KYIV):%d.%m.%Y}**", ""]
    for r in results:
        ch = next(c for c in C.CHANNELS if c["key"] == r["key"])
        slots = ", ".join(slot_text(s, ch["slots"]["tz"]) for s in r.get("slots", []))
        bad = "; ".join(t for _, t in r["problems"]) or "all well"
        rows.append(f"- {'✓' if not r['problems'] else '✗'} **{r['name']}** — {slots} — {bad}")
    rows += ["", f"GPU week: {gpu[0]} h of {C.GPU_LIMIT_H} h."]
    day = [e for e in journal if ts(e["at"]) >= now - timedelta(hours=24) and not str(e["result"]).startswith(("no ", "not "))]
    if day:
        rows += ["", "**Put right in the last 24 h:**"] + [f"- {e['channel']}: {e['action']} ({e['why']}) — {e['result']}"
                                                            for e in day]
    return "\n".join(rows)


def main(argv=None):
    from monitor import autofix, heal
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--fixtures")
    ap.add_argument("--now")
    ap.add_argument("--out", default=str(ROOT))
    ap.add_argument("--due", action="store_true",
                    help="only when a pass is due (3 h since the last), the summary is (07:00-10:00 Kyiv) "
                         "or a planned dispatch is")
    args = ap.parse_args(argv)
    now = ts(args.now) if args.now else datetime.now(timezone.utc)
    out = Path(args.out)
    state_p = out / "state" / "monitor.json"
    acts_p = out / "state" / "actions.json"
    mem = json.loads(state_p.read_text(encoding="utf-8")) if state_p.exists() else {}
    planned_p = out / "state" / "planned.json"
    if planned_p.exists():                       # dispatches planned by hand, merged in once
        for p in json.loads(planned_p.read_text(encoding="utf-8")):
            if not any(q.get("id") == p.get("id") for q in mem.get("planned", [])):
                mem.setdefault("planned", []).append(p)
    mem["actions"] = json.loads(acts_p.read_text(encoding="utf-8")) if acts_p.exists() else mem.get("actions", [])
    if args.due:
        last = ts(mem.get("last_pass"))
        pass_due = last is None or now - last >= timedelta(hours=PASS_EVERY_H) - timedelta(minutes=5)
        summary_due = 7 <= now.astimezone(KYIV).hour < 10 and mem.get("summary_date") != now.astimezone(KYIV).strftime("%Y-%m-%d")
        plan_due = any(not p.get("done") and ts(p["at"]) <= now for p in mem.get("planned", []))
        if not (pass_due or summary_due or plan_due):
            print(f"not due: last pass {mem.get('last_pass')}, summary sent {mem.get('summary_date')}")
            return 0
        args.summary = args.summary or summary_due
    net = Offline(args.fixtures) if args.fixtures else Net()
    net.issue = mem.get("issue")
    # what MONITOR_TOKEN may write, probed without writing (owner 06.11), once a pass
    net.rights_seen = {r: net.rights(r) for r in [c["repo"] for c in C.CHANNELS if c.get("act")] + [net.repo]}
    mem["rights"] = net.rights_seen
    work = out / "work"
    results, roots, owner = [], {}, []
    for ch in C.CHANNELS:
        res, root = look(net, ch, now, work)
        if root is not None:
            roots[ch["key"]] = root
        try:
            res["actions"] = heal.runbook(net, ch, res, root, mem, now)
        except (urllib.error.URLError, OSError) as e:
            res["actions"] = [heal.log(mem, now, ch, "runbook", "", f"stopped: {e}")]
        fixes = C._json(root, ch["infra_fixes"], []) if (root is not None and ch.get("infra_fixes")) else []
        try:
            res["actions"] += autofix.run(net, ch, res, mem, now, owner, fixes)
        except (urllib.error.URLError, OSError) as e:
            res["actions"].append(heal.log(mem, now, ch, "autofix", "", f"stopped: {e}", level=2))
        results.append(res)
    heal.planned(net, mem, results, now)
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
    # letters only when the owner is needed: a YouTube token, a key, a patch undone, nothing for
    # tomorrow; everything else is in the morning summary and the journal
    need = {f"{r['key']}:owner-{k}": f"{r['name']}: {text}" for r in results for k, text in r.get("owner", [])}
    for i, text in enumerate(owner):
        need[f"revert:{hashlib.sha1(text.encode()).hexdigest()[:8]}"] = text
    # level 2 off: said once, not kept quiet (owner 06.11)
    for k, text in autofix.off_letters(net, os.environ.get("GEMINI_API_KEY_MON")):
        need[k] = text
    before = set(mem.get("owner_alarms", {}))
    new = {k: v for k, v in need.items() if k not in before}
    sent = []
    if new:
        body = (f"@{OWNER} **Needs you**\n\n" + "\n".join(f"- {v}" for v in new.values()))
        try:
            net.comment(body)
            sent.append("needs-you")
        except (urllib.error.URLError, OSError) as e:
            print(f"could not write the issue: {e}")
            new = {}
    today = now.astimezone(KYIV).strftime("%Y-%m-%d")
    if args.summary and 7 <= now.astimezone(KYIV).hour < 10 and mem.get("summary_date") != today:
        try:
            net.comment(summary(results, gpu, now, mem.get("actions", [])))
            mem["summary_date"] = today
            sent.append("summary")
        except (urllib.error.URLError, OSError) as e:
            print(f"could not write the summary: {e}")
    # a letter is not sent again until its cause has cleared; one that failed is tried again
    mem["owner_alarms"] = {k: v for k, v in need.items() if k in before or k in new}
    mem["alarms"] = alarms
    mem["last_pass"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    if net.issue:
        mem["issue"] = net.issue
    journal = mem.pop("actions", [])
    state_p.parent.mkdir(parents=True, exist_ok=True)
    state_p.write_text(json.dumps(mem, indent=1, ensure_ascii=False), encoding="utf-8")
    acts_p.write_text(json.dumps(journal, indent=1, ensure_ascii=False), encoding="utf-8")
    for r in results:
        for f in r.get("failures", []):
            f.pop("tail", None)
    (out / "state" / "channels.json").write_text(json.dumps({"at": mem["last_pass"], "channels": results,
                                                             "gpu": {"hours": gpu[0], "parts": gpu[1]},
                                                             "shared": shared}, indent=1, ensure_ascii=False,
                                                            default=str), encoding="utf-8")
    (out / "README.md").write_text(readme(results, gpu, shared, now, journal), encoding="utf-8")
    if isinstance(net, Offline):
        (out / "sent.json").write_text(json.dumps(net.sent, indent=1, ensure_ascii=False), encoding="utf-8")
    for r in results:
        print(f"{'OK ' if not r['problems'] else 'BAD'} {r['name']}: buffer {r.get('buffer')}/3, watchdog {r.get('watchdog_h')} h, "
              f"build {r.get('build_h')} h, topics {r.get('topics')}; {'; '.join(t for _, t in r['problems']) or 'all well'}"
              + "".join(f"\n      did: {e['action']} - {e['result']}" for e in r.get("actions", [])))
    print(f"GPU week {gpu[0]} h {gpu[1]}; owner letters {len(new)}; sent {sent or 'nothing'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
