"""Level 2: a new failure (not in the runbook) seen twice is patched, tested and merged - or undone.

  1. find    the same failure (failed step + last error line, normalised) in two or more
             builds of a channel within 72 h; not deferred (quota, window), not the owner's
             (token, key), not already one of its fixed faults
  2. patch   Gemini (GEMINI_API_KEY_MON) reads the log tail and the code of the deepest frame
             of the traceback in the channel's repository and returns one minimal edit
             (old -> new); the monitor refuses any edit that touches what it may never
             change (FORBID_PATH, FORBID_TEXT): uploads, schedules and publishAt, the
             anti-duplicate, secrets and key handling, QA thresholds, GPU budgets, workflows
  3. test    the edit and an entry in the channel's state/infra_fixes.json go on a branch
             autofix/<channel>-<date> made from dev; the channel's smoke test runs on it
  4. merge   only a green smoke merges the branch into dev, and dev goes to main the
             channel's usual way (its smoke on dev)
  5. watch   if the channel's next build after the merge fails, the edit is undone on dev
             (the same path to main) and the owner gets a letter
At most one patch a channel a day; the stoic channel never.
"""
import json
import os
import re
import urllib.request
from datetime import datetime, timedelta, timezone

from monitor import heal

MODEL = "gemini-flash-latest"
URL = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
FORBID_PATH = re.compile(r"(^|/)\.github/|upload|youtube|publish|schedul|slot|dedup|duplicate|secret|token|credential|"
                         r"(^|/)keys?\b|(^|/)qa|gpu_budget|budget|kaggle_once|(^|/)config|\.env|release", re.I)
FORBID_TEXT = re.compile(r"publishAt|publish_at|privacyStatus|find_by_title|uploaded\.json|YT_TOKEN|API_KEY|secrets\.|"
                         r"os\.environ|getenv|LIMIT_H|WEEKLY|threshold|_MIN\b|_MAX\b|qa\[|\"qa\"", re.I)
MAX_CHANGED_LINES = 30
FRAME = re.compile(r'File "(?:/home/runner/work/[^/]+/[^/]+/)([^"]+)", line (\d+)')


def stamp(now):
    return now.strftime("%Y-%m-%dT%H:%M:%SZ")


def signature(fail):
    from monitor.check import norm
    last = [l for l in (fail.get("tail") or "").splitlines() if l.strip() and not l.lstrip().startswith("##[")]
    return norm(f"{fail.get('step')} | {last[-1] if last else ''}")


def candidates(failures, now, fixes=()):
    """[(signature, [failures])] seen twice or more within 72 h, failures only (not deferred,
    not the owner's), not one of the channel's fixed faults."""
    groups = {}
    for f in failures:
        if heal.classify(f.get("tail")) is not None:
            continue
        t = heal.ts(f.get("at"))
        if t is None or now - t > timedelta(hours=72):
            continue
        if any(all(m in (f.get("tail") or "") for m in x.get("match", [])) for x in fixes):
            continue
        groups.setdefault(signature(f), []).append(f)
    return [(s, fs) for s, fs in groups.items() if len(fs) >= 2]


def ask(prompt):
    key = os.environ.get("GEMINI_API_KEY_MON", "")
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0, "responseMimeType": "application/json"}}
    req = urllib.request.Request(URL.format(m=MODEL), data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read())
    out = "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"])
    return json.loads(out[out.find("{"): out.rfind("}") + 1])


PROMPT = """You fix one failure in a video pipeline's Python code with the smallest possible edit.

THE FAILURE (the end of the failed step's log):
{tail}

THE CODE: {path} (lines {a}-{b}; the failing line is {line})
{code}

Rules: change as little as possible, in this file only; keep the behaviour, only stop the crash
(for example: a value of an unexpected type made into the expected one, a missing key read with a
default). Never touch uploads, schedules, publish times, duplicate checks, secrets or API keys,
thresholds or budgets. If the fix is not small and certain, answer {{"skip": "why"}}.
Answer JSON only: {{"old": "<exact lines from the code above, unique in the file>",
"new": "<their replacement>", "why": "<one sentence>",
"match": "<a short distinctive piece of the error text, to recognise this failure again>"}}"""


def propose(net, ch, fail):
    """(path, old file text, new file text, why, match) or (None, reason)."""
    frames = [(p, int(n)) for p, n in FRAME.findall(fail.get("tail") or "") if not p.startswith(("usr/", "opt/"))]
    frames = [(p, n) for p, n in frames if p.endswith(".py")]
    if not frames:
        return None, "no frame of the channel's own code in the traceback"
    path, line = frames[-1]
    if FORBID_PATH.search(path):
        return None, f"{path} is code the monitor may not change"
    text, _ = net.get_file(ch["repo"], path, "dev")
    lines = text.splitlines()
    a, b = max(1, line - 40), min(len(lines), line + 40)
    code = "\n".join(f"{i:5d}  {lines[i - 1]}" for i in range(a, b + 1))
    ans = ask(PROMPT.format(tail=(fail.get("tail") or "")[-3000:], path=path, a=a, b=b, line=line, code=code))
    if ans.get("skip"):
        return None, f"Gemini: {ans['skip']}"
    old, new = ans.get("old", ""), ans.get("new", "")
    if not old or old == new or text.count(old) != 1:
        return None, "the edit does not match the file once"
    if FORBID_TEXT.search(old) or FORBID_TEXT.search(new):
        return None, "the edit touches what the monitor may not change"
    if abs(len(new.splitlines()) - len(old.splitlines())) + len(old.splitlines()) > MAX_CHANGED_LINES:
        return None, "the edit is not small"
    new_text = text.replace(old, new)
    try:
        compile(new_text, path, "exec")
    except SyntaxError as e:
        return None, f"the edit does not compile: {e}"
    return (path, text, new_text, ans.get("why", ""), (ans.get("match") or "").strip()[:120]), None


def start(net, ch, sig, fails, mem, now):
    """Patch, branch, smoke. Returns a journal entry."""
    got, why = propose(net, ch, fails[-1])
    if got is None:
        return heal.log(mem, now, ch, "autofix", sig[:120], f"no patch: {why}", level=2)
    path, old_text, new_text, reason, match = got
    branch = f"autofix/{ch['key']}-{now:%Y%m%d}"
    net.branch(ch["repo"], branch, "dev")
    _, sha = net.get_file(ch["repo"], path, branch)
    net.put_file(ch["repo"], path, new_text, sha, f"autofix: {reason}\n\nThe failure, twice: {sig[:200]}", branch)
    fixes_path = ch.get("infra_fixes") or "state/infra_fixes.json"
    try:
        ftext, fsha = net.get_file(ch["repo"], fixes_path, branch)
        fixes = json.loads(ftext)
    except OSError:
        fixes, fsha = [], None
    fixes.append({"what": reason, "match": [match or sig[:60]], "fixed_at": stamp(now), "fix": f"monitor {branch}"})
    net.put_file(ch["repo"], fixes_path, json.dumps(fixes, indent=1, ensure_ascii=False) + "\n", fsha,
                 f"autofix: record the fixed fault ({branch})", branch)
    net.dispatch(ch["repo"], "smoke.yml", {"ref": branch}, ref="dev")
    mem.setdefault("autofix", {})[ch["key"]] = {"day": f"{now:%Y-%m-%d}", "branch": branch, "stage": "smoke",
                                                "since": stamp(now), "path": path, "old": old_text, "signature": sig}
    return heal.log(mem, now, ch, f"autofix {branch}", sig[:120], f"patch on {path}, smoke started", level=2)


def follow(net, ch, mem, now, owner):
    """Move a running autofix on: smoke -> merge -> watch -> kept or undone."""
    a = mem.get("autofix", {}).get(ch["key"])
    if not a or a["stage"] in ("kept", "reverted", "smoke-failed"):
        return []
    made = []
    if a["stage"] == "smoke":
        rs = heal.runs(net, ch["repo"], "smoke.yml", 10)
        mine = [r for r in rs if a["branch"] in (r.get("display_title") or "") and r.get("status") == "completed"
                and heal.ts(r.get("created_at")) >= heal.ts(a["since"]) - timedelta(minutes=5)]
        if not mine:
            return []
        if mine[0].get("conclusion") == "success":
            net.merge(ch["repo"], "dev", a["branch"], f"autofix: merge {a['branch']} (its smoke passed)")
            a.update({"stage": "merged", "merged_at": stamp(now)})
            made.append(heal.log(mem, now, ch, f"merge {a['branch']}", "smoke on the branch passed",
                                 "merged into dev; dev goes to main by its smoke", level=2))
        else:
            a["stage"] = "smoke-failed"
            made.append(heal.log(mem, now, ch, f"autofix {a['branch']}", "smoke on the branch failed",
                                 "not merged", level=2))
        return made
    if a["stage"] == "merged":
        after = heal.ts(a["merged_at"])
        done = []
        for wf in ch["builds"]:
            done += [r for r in heal.runs(net, ch["repo"], wf, 10) if r.get("status") == "completed"
                     and heal.ts(r.get("created_at")) > after]
        if not done:
            return []
        first = min(done, key=lambda r: r.get("created_at"))
        if first.get("conclusion") == "success":
            a["stage"] = "kept"
            made.append(heal.log(mem, now, ch, f"autofix {a['branch']}", "the next build passed", "kept", level=2))
        else:
            _, sha = net.get_file(ch["repo"], a["path"], "dev")
            net.put_file(ch["repo"], a["path"], a["old"], sha,
                         f"monitor: undo {a['branch']} - the next build failed after it", "dev")
            a["stage"] = "reverted"
            made.append(heal.log(mem, now, ch, f"revert {a['branch']}", "the next build after the merge failed",
                                 "undone on dev", level=2))
            owner.append(f"{ch['name']}: the automatic fix {a['branch']} was undone - the next build failed after it "
                         f"({first.get('html_url')})")
    return made


def run(net, ch, res, mem, now, owner, fixes=()):
    """Level 2 for one channel on this pass."""
    if not ch.get("act") or not os.environ.get("GEMINI_API_KEY_MON") or not net.can_write():
        return []
    made = follow(net, ch, mem, now, owner)
    a = mem.get("autofix", {}).get(ch["key"])
    if a and a.get("day") == f"{now:%Y-%m-%d}":
        return made                                          # one a channel a day
    if a and a["stage"] in ("smoke", "merged"):
        return made                                          # one at a time
    cands = candidates(res.get("failures") or [], now, fixes)
    if cands:
        sig, fails = cands[0]
        try:
            made.append(start(net, ch, sig, fails, mem, now))
        except (OSError, ValueError, KeyError) as e:
            made.append(heal.log(mem, now, ch, "autofix", sig[:120], f"stopped: {e}", level=2))
            mem.setdefault("autofix", {})[ch["key"]] = {"day": f"{now:%Y-%m-%d}", "stage": "smoke-failed",
                                                        "signature": sig}
    return made
