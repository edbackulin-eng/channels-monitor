"""Smoke test: the monitor on fake channels, offline (smoke.yml).

Five fake checkouts and fake GitHub answers; the passes must find exactly what is wrong:
  1. alarms: a short buffer (Closed Tabs, dinosaurs, archive), a dead watchdog (archive),
     the GPU week over 27.5 h, the same error in two channels (shared), a failed episode;
     the stoic channel's one-day buffer is its normal state;
  2. actions: the watchdogs of the channels with a short buffer or a dead watchdog are
     started, the stoic one never; not again within 3 hours;
  3. letters: one for the new alarms, none for the same alarms again, a new one when an
     alarm that had cleared comes back; the daily summary once a day at 07:00-10:00 Kyiv;
  4. --due: nothing runs when no pass and no summary is due;
  5. README.md: a row for every channel.
"""
import json
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from monitor import check  # noqa: E402

failures = []


def ok(name, cond, detail=""):
    print(f"[{'ok' if cond else 'FAIL'}] {name} {detail if not cond else ''}")
    if not cond:
        failures.append(name)


def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data), encoding="utf-8")


def world(d, ct_scheduled_extra=False):
    """Fake channels as they stand on Thursday 05.11.2026, 05:30 UTC (07:30 Kyiv)."""
    # What If: two of its next three slots (Thu, Fri, Sat 15:00 UTC) filled; one failed on six
    write(d / "whatif/queue/025/episode.json", {"slug": "025", "title": "T25", "status": "published",
                                                "youtube_id": "a", "publish_at": "2026-11-05T15:00:00Z"})
    write(d / "whatif/queue/018/episode.json", {"slug": "018", "title": "T18", "status": "published",
                                                "youtube_id": "b", "publish_at": "2026-11-06T15:00:00Z"})
    write(d / "whatif/queue/019/episode.json", {"slug": "019", "title": "T19", "status": "failed",
                                                "error": "ModuleNotFoundError: No module named 'six'"})
    write(d / "whatif/assets/topics.json", ["T18", "T19", "T25"] + [f"new {i}" for i in range(15)])
    # Closed Tabs: one slot of three; a GPU week over the limit with What If's estimate
    eps = [{"slug": "year-zero", "publish_at": "2026-11-05T17:00:00Z", "youtube_id": "y"}]
    if ct_scheduled_extra:
        eps.append({"slug": "ongs-hat", "publish_at": "2026-11-06T17:00:00Z", "youtube_id": "o"})
    write(d / "closed-tabs/state/episodes.json", eps)
    write(d / "closed-tabs/topics/queue.json", {"topics": [{"slug": f"t{i}", "status": "queued"} for i in range(12)]})
    write(d / "closed-tabs/state/gpu_ledger.json", [{"ref": "x", "start": "2026-11-04T01:00:00+00:00", "hours": 10.0},
                                                    {"ref": "x", "start": "2026-10-20T01:00:00+00:00", "hours": 50.0}])
    write(d / "closed-tabs/state/whatif_gpu.json", {"me/whatif-main@2026-11-03T10:00:00+00:00": 18.0})
    # dinosaurs: nothing scheduled, an episode that failed QA
    write(d / "dinosaurs/state/episodes.json", [{"slug": "lebende-fossilien", "status": "qa-failed",
                                                 "qa_failed": ["hook: 9 shots", "pace: 11 s"]}])
    write(d / "dinosaurs/topics/queue.json", {"topics": [{"slug": f"d{i}", "status": "queued"} for i in range(19)]})
    write(d / "dinosaurs/state/gpu_ledger.json", [{"ref": "p", "start": "2026-11-04T04:22:50+00:00", "hours": 1.45}])
    # the archive channel: nothing scheduled, its watchdog quiet for 5 h, the same six error
    write(d / "archive/state/episodes.json", [{"slug": "ep1", "status": "failed",
                                               "error": "ModuleNotFoundError: No module named 'six'"}])
    write(d / "archive/topics/queue.json", {"topics": [{"slug": f"a{i}", "status": "queued"} for i in range(8)]})
    # stoic: tomorrow's video scheduled (its normal state), a failed one this week
    (d / "stoic/data").mkdir(parents=True, exist_ok=True)
    db = d / "stoic/data/factory.db"
    if db.exists():
        db.unlink()
    c = sqlite3.connect(db)
    c.execute("create table videos (id integer primary key, created_at text, topic text, title text, status text, "
              "youtube_id text, published_at text, error text)")
    c.execute("insert into videos values (1, '2026-11-04T07:00:00+00:00', 't', 'tomorrow', 'published', 'z', "
              "'2026-11-05T19:00:00Z', null)")
    c.execute("insert into videos values (2, '2026-11-03T07:00:00+00:00', 't', 'broken', 'failed', null, null, "
              "'tts timed out')")
    c.commit()
    c.close()
    run = lambda **k: {"workflow_runs": [{"id": 1, "status": "completed", "conclusion": "success",  # noqa: E731
                                          "updated_at": "2026-11-05T04:00:00Z", "html_url": "u", **k}]}
    api = {}
    for key, repo in (("whatif", "edbackulin-eng/whatif-channel"), ("closed-tabs", "edbackulin-eng/closed-tabs"),
                      ("dinosaurs", "edbackulin-eng/prehistoric-channel"), ("archive", "edbackulin-eng/archive-channel")):
        api[f"repos/{repo}/actions/workflows/watchdog.yml/runs"] = (
            run(updated_at="2026-11-05T00:30:00Z") if key == "archive" else {"workflow_runs": [{"status": "in_progress"}]})
        api[f"repos/{repo}/commits"] = [{"commit": {"committer": {"date": "2026-11-05T00:30:00Z"}}}]
    for wf in ("build-video.yml", "daily.yml", "render.yml", "episode.yml"):
        for repo in ("whatif-channel", "closed-tabs", "prehistoric-channel", "archive-channel"):
            api[f"repos/edbackulin-eng/{repo}/actions/workflows/{wf}/runs"] = run()
    api["repos/beautyapp800-ctrl/yt-factory-daily/actions/workflows/heartbeat.yml/runs"] = run(updated_at="2026-11-04T19:45:00Z")
    api["repos/beautyapp800-ctrl/yt-factory-daily/actions/workflows/daily.yml/runs"] = run()
    write(d / "api.json", api)


def pass_(fx, out, now, summary=True, due=False):
    argv = ["--fixtures", str(fx), "--out", str(out), "--now", now]
    argv += ["--summary"] if summary else []
    argv += ["--due"] if due else []
    check.main(argv)
    sent = json.loads((out / "sent.json").read_text(encoding="utf-8")) if (out / "sent.json").exists() else []
    mem = json.loads((out / "state" / "monitor.json").read_text(encoding="utf-8"))
    return sent, mem


def main():
    tmp = Path(tempfile.mkdtemp())
    fx, out = tmp / "fx", tmp / "out"
    world(fx)
    sent, mem = pass_(fx, out, "2026-11-05T05:30:00Z")
    al = mem["alarms"]
    for k in ("closed-tabs:buffer", "dinosaurs:buffer", "archive:buffer", "archive:watchdog", "gpu:week",
              "dinosaurs:failed:lebende-fossilien", "archive:topics"):
        ok(f"alarm {k}", k in al, str(sorted(al)))
    ok("no alarm for What If's buffer (2 of 3) nor the stoic channel's one day", "whatif:buffer" not in al
       and "stoic:buffer" not in al, str(sorted(al)))
    ok("the same error in two channels is shared", any(k.startswith("whatif:shared:") for k in al)
       and any(k.startswith("archive:shared:") for k in al), str(sorted(al)))
    ok("GPU week: 10 + 18 + 1.45 h of the last 7 days", "29.45" in al.get("gpu:week", ""), al.get("gpu:week"))
    dis = sorted(x["dispatch"] for x in sent if "dispatch" in x)
    ok("watchdogs started: Closed Tabs, dinosaurs, archive - never the stoic one",
       dis == sorted(["edbackulin-eng/closed-tabs/watchdog.yml", "edbackulin-eng/prehistoric-channel/watchdog.yml",
                      "edbackulin-eng/archive-channel/watchdog.yml"]), str(dis))
    comments = [x["comment"] for x in sent if "comment" in x]
    ok("one letter for the new alarms and the daily summary, both to the owner",
       len(comments) == 2 and all("@edbackulin-eng" in c for c in comments) and "New alarm" in comments[0]
       and "Channels, 05.11.2026" in comments[1], str([c[:40] for c in comments]))
    readme = (out / "README.md").read_text(encoding="utf-8")
    ok("README: a row for every channel", all(n in readme for n in ("What If", "Closed Tabs", "Urzeit", "Yesterday in Color",
                                                                   "Stoic")), readme[:300])
    # the same world 10 minutes on: no letter, no start, no summary again
    (out / "sent.json").unlink()
    sent, mem = pass_(fx, out, "2026-11-05T05:40:00Z")
    ok("the same alarms again: no letter, no watchdog started again within 3 h", sent == [], str(sent))
    # Closed Tabs gets its second video: its alarm clears; it comes back: a letter again
    world(fx, ct_scheduled_extra=True)
    (out / "sent.json").unlink(missing_ok=True)
    sent, mem = pass_(fx, out, "2026-11-05T08:50:00Z", summary=False)
    ok("an alarm that cleared is forgotten", "closed-tabs:buffer" not in mem["alarms"], str(sorted(mem["alarms"])))
    world(fx)
    (out / "sent.json").unlink(missing_ok=True)
    sent, mem = pass_(fx, out, "2026-11-05T09:00:00Z", summary=False)
    ok("it comes back: one letter for it alone", len([x for x in sent if "comment" in x]) == 1
       and "Closed Tabs" in sent[-1].get("comment", "") and "Urzeit" not in sent[-1].get("comment", ""),
       str(sent))
    # --due: ten minutes after a pass, the summary already sent today: nothing runs
    before = (out / "state" / "monitor.json").read_text(encoding="utf-8")
    (out / "sent.json").unlink(missing_ok=True)
    pass_(fx, out, "2026-11-05T09:10:00Z", due=True)
    ok("--due: no pass when none is due", (out / "state" / "monitor.json").read_text(encoding="utf-8") == before
       and not (out / "sent.json").exists())
    shutil.rmtree(tmp, ignore_errors=True)
    print("\nSMOKE", "PASSED" if not failures else f"FAILED: {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
