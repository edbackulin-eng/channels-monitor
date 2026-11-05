"""Smoke test: the monitor on fake channels, offline (smoke.yml).

Five fake checkouts and fake GitHub answers; the passes must find what is wrong and put
right what the runbook knows, and nothing else:
  1. what is seen: short buffers, failed episodes, the GPU week, a shared error; the stoic
     channel's one-day buffer is its normal; a 429 is deferred, not a failure
  2. level 1: a hung watchdog cancelled and started; a failed episode of a fixed fault back
     in the queue; topics refilled; a failed upload of a built video repeated; a short buffer
     gets a build (inside the channel's build hours only); a planned dispatch fired; the stoic
     channel never touched; nothing twice within its interval; all of it in the journal
  3. level 2: a new failure seen twice gets a patch on an autofix branch, its smoke, and only
     a green smoke a merge; a failing build after it undoes it and writes to the owner; code
     it may not touch is refused; one patch a channel a day
  4. letters: only when the owner is needed (an expired token, an undone patch), once; the
     morning summary lists what was put right
  5. --due: nothing runs when no pass, no summary and no planned dispatch is due
"""
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from monitor import autofix, check  # noqa: E402

failures = []
WI, CT, DI, AR = ("edbackulin-eng/whatif-channel", "edbackulin-eng/closed-tabs", "edbackulin-eng/prehistoric-channel",
                  "edbackulin-eng/archive-channel")
TRACE = ('Traceback (most recent call last):\n  File "/home/runner/work/whatif-channel/whatif-channel/pipeline/sceneplan.py",'
         ' line 3, in plan\n    s["prompt"] = (r.get("prompt") or "").strip()\nAttributeError: \'dict\' object has no attribute \'strip\'')
SCENEPLAN = 'def plan(r, s):\n    """the plan"""\n    s["prompt"] = (r.get("prompt") or "").strip()\n    return s\n'


def ok(name, cond, detail=""):
    print(f"[{'ok' if cond else 'FAIL'}] {name} {detail if not cond else ''}")
    if not cond:
        failures.append(name)


def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data), encoding="utf-8")


def run(rid, conclusion="success", status="completed", updated="2026-11-05T04:00:00Z", **k):
    return {"id": rid, "status": status, "conclusion": conclusion, "updated_at": updated, "created_at": updated,
            "run_started_at": updated, "html_url": f"https://x/{rid}", **k}


def world(d, ct_extra=False, wi_build_after_merge=None, smoke_on_branch=None):
    """Fake channels as they stand on Thursday 05.11.2026, 05:30 UTC (07:30 Kyiv)."""
    write(d / "whatif/queue/025/episode.json", {"slug": "025", "title": "T25", "status": "published",
                                                "youtube_id": "a", "publish_at": "2026-11-05T15:00:00Z"})
    write(d / "whatif/queue/018/episode.json", {"slug": "018", "title": "T18", "status": "published",
                                                "youtube_id": "b", "publish_at": "2026-11-06T15:00:00Z"})
    six = "/opt/python -m kaggle kernels push -p kaggle/build failed:\nTraceback\n  File _get_module_details\nNo module named 'six'"
    write(d / "whatif/queue/019/episode.json", {"slug": "019", "title": "T19", "status": "failed", "error": six,
                                                "updated": "2026-11-03T12:00:00+00:00"})
    write(d / "whatif/state/infra_fixes.json", [{"what": "six", "match": ["-m kaggle kernels push", "_get_module_details"],
                                                 "fixed_at": "2026-11-04T11:20:00Z", "fix": "7366338"}])
    write(d / "whatif/assets/topics.json", ["T18", "T19", "T25"] + [f"new {i}" for i in range(15)])
    eps = [{"slug": "year-zero", "publish_at": "2026-11-05T17:00:00Z", "youtube_id": "y"}]
    if ct_extra:
        eps.append({"slug": "ongs-hat", "publish_at": "2026-11-06T17:00:00Z", "youtube_id": "o"})
    write(d / "closed-tabs/state/episodes.json", eps)
    write(d / "closed-tabs/topics/queue.json", {"topics": [{"slug": f"t{i}", "status": "queued"} for i in range(12)]})
    write(d / "closed-tabs/state/gpu_ledger.json", [{"ref": "x", "start": "2026-11-04T01:00:00+00:00", "hours": 10.0}])
    write(d / "closed-tabs/state/whatif_gpu.json", {"me/whatif-main@2026-11-03T10:00:00+00:00": 18.0})
    write(d / "dinosaurs/state/episodes.json", [{"slug": "lebende-fossilien", "status": "qa-failed",
                                                 "qa_failed": ["hook: 9 shots"]}])
    write(d / "dinosaurs/topics/queue.json", {"topics": [{"slug": f"d{i}", "status": "queued"} for i in range(9)]})
    write(d / "dinosaurs/state/gpu_ledger.json", [{"ref": "p", "start": "2026-11-04T04:22:50+00:00", "hours": 1.45}])
    write(d / "archive/state/episodes.json", [{"slug": "ep1", "state": "built"}])
    write(d / "archive/topics/queue.json", {"topics": [{"slug": f"a{i}", "status": "queued"} for i in range(20)]})
    (d / "stoic/data").mkdir(parents=True, exist_ok=True)
    db = d / "stoic/data/factory.db"
    if db.exists():
        db.unlink()
    c = sqlite3.connect(db)
    c.execute("create table videos (id integer primary key, created_at text, topic text, title text, status text, "
              "youtube_id text, published_at text, error text)")
    c.execute("insert into videos values (1, '2026-11-04T07:00:00+00:00', 't', 'tomorrow', 'published', 'z', "
              "'2026-11-05T19:00:00Z', null)")
    c.commit()
    c.close()
    api = {"files": {f"{WI}:main:queue/019/episode.json": json.dumps({"slug": "019", "status": "failed", "error": six}),
                     f"{WI}:*:pipeline/sceneplan.py": SCENEPLAN,
                     f"{WI}:*:state/infra_fixes.json": "[]",
                     f"{WI}:*:automation/upload_youtube.py": "x = 1\n"}}
    alive = {"workflow_runs": [run(9, status="in_progress", conclusion=None)]}
    for repo in (WI, DI, AR):
        api[f"repos/{repo}/actions/workflows/watchdog.yml/runs"] = alive
        api[f"repos/{repo}/commits"] = [{"commit": {"committer": {"date": "2026-11-05T05:00:00Z"}}}]
    # Closed Tabs: its watchdog hung for 7 hours
    api[f"repos/{CT}/actions/workflows/watchdog.yml/runs"] = {"workflow_runs": [
        run(70, status="in_progress", conclusion=None, updated="2026-11-04T22:30:00Z")]}
    api[f"repos/{CT}/commits"] = [{"commit": {"committer": {"date": "2026-11-04T22:30:00Z"}}}]
    # What If: the same new failure twice (level 2), then maybe a build after a merge
    wi_runs = [run(51, "failure", updated="2026-11-05T01:00:00Z"), run(52, "failure", updated="2026-11-04T20:00:00Z")]
    if wi_build_after_merge:
        wi_runs.insert(0, run(53, wi_build_after_merge, updated="2026-11-05T12:00:00Z"))
    api[f"repos/{WI}/actions/workflows/build-video.yml/runs"] = {"workflow_runs": wi_runs}
    for rid in (51, 52):
        api[f"repos/{WI}/actions/runs/{rid}/jobs"] = {"jobs": [{"id": rid * 10, "name": "build",
                                                               "steps": [{"name": "Build", "conclusion": "failure"}]}]}
        api[f"log:{WI}:{rid * 10}"] = TRACE
    api[f"repos/{WI}/actions/runs/53/jobs"] = {"jobs": [{"id": 530, "name": "build",
                                                         "steps": [{"name": "Build", "conclusion": "failure"}]}]}
    api[f"log:{WI}:530"] = "Traceback\nValueError: something else"
    smokes = [run(60, smoke_on_branch, created="2026-11-05T05:31:00Z", updated="2026-11-05T05:50:00Z",
                  display_title="smoke autofix/whatif-20261105")] if smoke_on_branch else []
    api[f"repos/{WI}/actions/workflows/smoke.yml/runs"] = {"workflow_runs": smokes}
    # Closed Tabs and the archive: builds fine; dinosaurs: the last build waits for its quota
    for repo, wf in ((CT, "daily.yml"), (AR, "episode.yml")):
        api[f"repos/{repo}/actions/workflows/{wf}/runs"] = {"workflow_runs": [run(80)]}
    api[f"repos/{DI}/actions/workflows/render.yml/runs"] = {"workflow_runs": [run(90, "failure")]}
    api[f"repos/{DI}/actions/runs/90/jobs"] = {"jobs": [{"id": 900, "name": "render",
                                                         "steps": [{"name": "Check", "conclusion": "failure"}]}]}
    api[f"log:{DI}:900"] = "HTTP Error 429: Too Many Requests - quota exceeded, retried later"
    # the archive: its built video's last upload failed - with an expired token
    api[f"repos/{AR}/actions/workflows/upload.yml/runs"] = {"workflow_runs": [run(95, "failure")]}
    api[f"repos/{AR}/actions/workflows/episode.yml/runs"] = {"workflow_runs": [run(81, "failure")]}
    api[f"repos/{AR}/actions/runs/81/jobs"] = {"jobs": [{"id": 810, "name": "upload",
                                                         "steps": [{"name": "Upload", "conclusion": "failure"}]}]}
    api[f"log:{AR}:810"] = "google.auth.exceptions.RefreshError: invalid_grant: Token has been expired or revoked."
    api["repos/beautyapp800-ctrl/yt-factory-daily/actions/workflows/heartbeat.yml/runs"] = {
        "workflow_runs": [run(1, updated="2026-11-04T19:45:00Z")]}
    api["repos/beautyapp800-ctrl/yt-factory-daily/actions/workflows/daily.yml/runs"] = {"workflow_runs": [run(2)]}
    write(d / "api.json", api)


def pass_(fx, out, now, summary=True, due=False):
    argv = ["--fixtures", str(fx), "--out", str(out), "--now", now] + (["--summary"] if summary else []) + \
        (["--due"] if due else [])
    (out / "sent.json").unlink(missing_ok=True)
    check.main(argv)
    sent = json.loads((out / "sent.json").read_text(encoding="utf-8")) if (out / "sent.json").exists() else []
    mem = json.loads((out / "state" / "monitor.json").read_text(encoding="utf-8"))
    acts = json.loads((out / "state" / "actions.json").read_text(encoding="utf-8"))
    return sent, mem, acts


def main():
    os.environ["GEMINI_API_KEY_MON"] = "fake"
    asked = []
    autofix.ask = lambda prompt: asked.append(prompt) or {
        "old": '    s["prompt"] = (r.get("prompt") or "").strip()',
        "new": '    s["prompt"] = str(r.get("prompt") or "").strip()', "why": "a prompt may come as an object",
        "match": "'dict' object has no attribute 'strip'"}
    tmp = Path(tempfile.mkdtemp())
    fx, out = tmp / "fx", tmp / "out"
    out.mkdir()
    world(fx)
    write(out / "state" / "planned.json", [{"id": "ct-0711", "at": "2026-11-05T05:00:00Z", "repo": CT,
                                            "workflow": "daily.yml", "inputs": {"upload": "true"},
                                            "unless_slot_filled": "2026-11-07", "why": "the build for 07.11"}])
    sent, mem, acts = pass_(fx, out, "2026-11-05T05:30:00Z")
    did = [(a["channel"], a["action"]) for a in acts]
    dis = [x["dispatch"] for x in sent if "dispatch" in x]
    # 1. seen
    al = mem["alarms"]
    ok("short buffers seen; the stoic one-day buffer is normal", "closed-tabs:buffer" in al and "dinosaurs:buffer" in al
       and "stoic:buffer" not in al, str(sorted(al)))
    ok("a 429 is deferred, not a failure", "dinosaurs:build-failed" not in al, str(sorted(al)))
    # 2. level 1
    ok("hung watchdog cancelled and started", any(x.get("cancel") == f"{CT}/70" for x in sent)
       and f"{CT}/watchdog.yml" in dis, str(sent))
    ok("failed episode of a fixed fault back in the queue", any(x.get("put") == f"{WI}:main:queue/019/episode.json"
                                                                for x in sent), str(sent))
    ok("topics under 10: the refill started (dinosaurs)", f"{DI}/topics.yml" in dis, str(dis))
    ok("a built video's failed upload repeated (archive)", f"{AR}/upload.yml" in dis, str(dis))
    ok("short buffer: a build where the channel builds now (dinosaurs), none outside its hours (Closed Tabs at 05:30)",
       f"{DI}/episode.yml" in dis and not any(x == f"{CT}/daily.yml" and "inputs" in y and y["inputs"].get("force_window")
                                               for y in sent if "dispatch" in y for x in [y["dispatch"]]), str(dis))
    ok("a planned dispatch fired", any(a["action"] == "planned daily.yml" and a["result"] == "started" for a in acts), str(did))
    ok("the stoic channel never touched", not any("yt-factory" in json.dumps(x) for x in sent if "comment" not in x))
    ok("all of it in the journal and README", len(acts) >= 6 and "Journal" in (out / "README.md").read_text(encoding="utf-8"))
    # 3. level 2: patch, branch, smoke
    puts = [x["put"] for x in sent if "put" in x]
    ok("level 2: a new failure seen twice - a patch on an autofix branch, and its smoke",
       any(x.get("branch", "").startswith(f"{WI}:autofix/whatif-20261105") for x in sent)
       and f"{WI}:autofix/whatif-20261105:pipeline/sceneplan.py" in puts
       and f"{WI}:autofix/whatif-20261105:state/infra_fixes.json" in puts
       and any(x.get("dispatch") == f"{WI}/smoke.yml" and x.get("inputs", {}).get("ref") == "autofix/whatif-20261105"
               for x in sent), str(sent))
    # 4. letters: the expired token, once; the summary with what was put right
    comments = [x["comment"] for x in sent if "comment" in x]
    ok("letter: needs you - the expired token", any("Needs you" in c and "token" in c for c in comments), str(comments))
    ok("the morning summary lists what was put right", any("Put right in the last 24 h" in c for c in comments),
       str([c[:60] for c in comments]))
    # the next pass: nothing again
    sent2, mem, acts2 = pass_(fx, out, "2026-11-05T05:45:00Z")
    ok("next pass: no action and no letter again", not [x for x in sent2 if "dispatch" in x or "comment" in x or "cancel" in x],
       str(sent2))
    # the smoke on the branch passed: merge
    world(fx, smoke_on_branch="success")
    sent3, mem, _ = pass_(fx, out, "2026-11-05T06:00:00Z")
    ok("only a green smoke merges the branch into dev", any(x.get("merge") == f"{WI}:autofix/whatif-20261105->dev"
                                                           for x in sent3), str(sent3))
    # the next build fails: the patch is undone and the owner told
    world(fx, wi_build_after_merge="failure", smoke_on_branch="success")
    sent4, mem, _ = pass_(fx, out, "2026-11-05T12:30:00Z", summary=False)
    ok("a failing build after the merge: undone on dev, and a letter",
       any(x.get("put") == f"{WI}:dev:pipeline/sceneplan.py" and "undo" in x.get("message", "") for x in sent4)
       and any("undone" in x.get("comment", "") for x in sent4), str(sent4))
    ok("one patch a channel a day", len(asked) == 1, str(len(asked)))
    # forbidden code is refused
    bad = {"tail": TRACE.replace("pipeline/sceneplan.py", "automation/upload_youtube.py")}
    got, why = autofix.propose(check.Offline(fx), {"repo": WI}, bad)
    ok("level 2 never touches uploads (and the other forbidden code)", got is None and "may not change" in why, why)
    # 5. --due
    before = (out / "state" / "monitor.json").read_text(encoding="utf-8")
    pass_(fx, out, "2026-11-05T12:40:00Z", due=True)
    ok("--due: nothing when nothing is due", (out / "state" / "monitor.json").read_text(encoding="utf-8") == before)
    shutil.rmtree(tmp, ignore_errors=True)
    print("\nSMOKE", "PASSED" if not failures else f"FAILED: {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
