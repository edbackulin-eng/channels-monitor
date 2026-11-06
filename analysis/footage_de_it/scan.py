"""How many minutes of living streets and everyday life each film really holds.

    python -X utf8 analysis/footage_de_it/scan.py de --films 40
    python -X utf8 analysis/footage_de_it/scan.py it --films 25
    python -X utf8 analysis/footage_de_it/scan.py refugees --films 16

Analysis only; nothing is published and nothing outside analysis/footage_de_it/
is written.

The catalogue says what a film is about. It does not say how much of it a viewer
would want to watch: a twenty-minute Marshall Plan reel can be eighteen minutes
of officials at a table and two minutes of a street. So every film is opened and
looked at.

  1. The smallest video derivative is downloaded - enough to see what a shot is,
     a tenth of the size of the master that would be cut from later.
  2. ffmpeg takes one frame every 10 seconds.
  3. Each frame goes to Gemini (the channel's own key) in batches, with one
     question that matters: are ordinary people living their lives in a real
     place here - a street, a market, a shop, a home, a workplace, a station -
     or is this an empty ruin, a parade, a map, a title card, an official
     speaking? Colour is measured in code from the pixels, not asked.
  4. Minutes of usable footage = frames that pass x 10 seconds. It is a sample,
     not a cut: a shot shorter than ten seconds can be missed, and a frame that
     passes can sit in a shot that turns. It is an estimate of the same kind for
     every film, which is what makes the films comparable.

Writes scan_<set>.csv (one row per film) and frames_<set>.csv (one row per
frame, so any number here can be checked against the picture it came from).
Everything is cached: a rerun re-downloads nothing and re-asks nothing.

In GitHub Actions (channels-monitor, .github/workflows/footage-audit.yml, owner 06.11):

    python -X utf8 analysis/footage_de_it/scan.py all

  - the key is GEMINI_API_KEY_MON, and only gemini-flash-lite is asked: flash has 20
    requests a day per Google project and level 2 of the monitor needs them;
  - FOOTAGE_MAX_CALLS caps the requests of a day (the key's project may be shared with
    the channels' own keys, whose day must not be spent here); the sets share it:
    refugees first, then Italy, then Germany with what is left;
  - a film's frames and its length are kept (frames/<id>/meta.json) and the video is
    deleted once its frames are taken (FOOTAGE_DROP_MEDIA=1), so a runner's disk holds
    a few films at a time and the next day opens nothing twice;
  - when the day's cap or FOOTAGE_DEADLINE is reached, films already judged are still
    written, the others are listed as waiting, and nothing new is opened.
"""
import argparse
import base64
import csv
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))

MEDIA = HERE / "media"
FRAMES = HERE / "frames"
CACHE = HERE / "cache"
VERDICTS = CACHE / "verdicts"
UA = {"User-Agent": "archive-channel/1.0 (documentary research; public-domain film only)"}

EVERY_S = 10                     # one frame per this many seconds
# The free tier allows 500 generateContent calls a day PER MODEL, so the cost that
# matters is requests, not tokens or images. Forty frames in one call turns a 90-frame
# film from six calls into three, and the whole job from 545 calls into about 220.
# flash-lite is the channel's own vision model; flash is only reached when flash-lite's
# day is spent, and this channel uses it for nothing else.
MODELS = tuple(m for m in os.environ.get("FOOTAGE_MODELS", "gemini-flash-lite-latest,gemini-flash-latest")
               .split(",") if m)
MAX_CALLS = int(os.environ.get("FOOTAGE_MAX_CALLS", "0") or 0)       # 0: no cap of our own
DEADLINE = float(os.environ.get("FOOTAGE_DEADLINE", "0") or 0)       # epoch seconds; 0: none
DROP_MEDIA = os.environ.get("FOOTAGE_DROP_MEDIA") == "1"
_calls = [0]
_budget = [0]                                                        # this set's share, 0: none
URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
BATCH = 40
MIN_GAP_S = float(os.environ.get("FOOTAGE_MIN_GAP_S", "2.0"))
RETRIES = 5
MAX_MB = 300                     # a derivative larger than this is skipped, with a note
PREFETCH = 5                     # parallel downloads; archive.org gives one stream ~0.6 MB/s

SYSTEM = """You are looking at single frames from American government and Prelinger film
shot in Germany and Italy between 1945 and 1969, for a documentary about how ordinary
people lived.

For each numbered frame answer one question above all: is this USABLE footage of living
streets and everyday life - real people going about their lives in a real place?

usable = true when ordinary civilians are visible and doing something ordinary: walking a
street, shopping, working, eating, queueing, riding a tram or bicycle, playing, farming,
sitting at a cafe, at home, at a station, in a market, at a festival. A few people is
enough; a crowd is not required. Children count. Workers at a job count.

usable = false for: a title card or credits, text on screen, a map or diagram, an empty
street or landscape with no people, ruins with nobody in them, soldiers in formation, a
parade, a military exercise, officials at a desk or signing papers, one person talking to
camera, a close-up of a machine or product with no person, an aerial view where people
cannot be made out, a dark or unreadable frame.

Also give:
  label  one of: streets, everyday, market, transport, work, military, ruins, refugees,
         officials, titles, landscape, other
  people one of: none, few, many
  clean  false when there is burned-in text, a caption, a timecode, a logo or a
         watermark in the frame; otherwise true

Return JSON only:
{"results":[{"i":<n>,"usable":true|false,"label":"<label>","people":"<none|few|many>",
"clean":true|false,"note":"<a few words>"}]}"""


def key():
    k = os.environ.get("GEMINI_API_KEY_MON", "").strip() or os.environ.get("GEMINI_API_KEY_AR", "").strip()
    if not k and (ROOT / ".env").exists():
        for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
            if line.startswith("GEMINI_API_KEY_AR="):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not k:
        raise SystemExit("GEMINI_API_KEY_AR is not set")
    return k


# --- the film ------------------------------------------------------------------------

def metadata(identifier):
    f = CACHE / f"meta_{identifier}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    req = urllib.request.Request(f"https://archive.org/metadata/{identifier}", headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        d = json.loads(r.read().decode("utf-8", "replace"))
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(d), encoding="utf-8")
    return d


VIDEO_EXT = (".mp4", ".m4v", ".mpeg", ".mpg", ".m2v", ".avi", ".mov", ".mkv", ".ogv")


def videos(d):
    return [f for f in d.get("files", [])
            if str(f.get("name", "")).lower().endswith(VIDEO_EXT)]


def best_and_proxy(identifier):
    """(best available resolution as "WxH", the small file to scan, its size in MB)."""
    d = metadata(identifier)
    vids = videos(d)
    if not vids:
        return "", None, 0
    def px(f):
        return int(f.get("width") or 0) * int(f.get("height") or 0)
    top = max(vids, key=px)
    best = f"{top.get('width')}x{top.get('height')}" if px(top) else ""
    small = min(vids, key=lambda f: int(f.get("size") or 1 << 40))
    base = f"https://archive.org/download/{identifier}/"
    return best, base + urllib.parse.quote(small["name"]), int(small.get("size") or 0) / 1e6


def download(url, dst):
    if dst.exists() and dst.stat().st_size > 0:
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(dst.suffix + ".part")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=300) as r, open(tmp, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
    tmp.rename(dst)
    return dst


def prefetch(rows):
    """Fetch every film of the set at once, before any of it is looked at.

    One stream from archive.org runs at about 0.6 MB/s, and these sets are ten gigabytes
    of 512 kb/s derivatives - six hours in series. Five at a time is the difference
    between a run that finishes this afternoon and one that does not.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    jobs = []
    for r in rows:
        try:
            _best, proxy, mb = best_and_proxy(r["identifier"])
        except Exception as e:                                   # noqa: BLE001
            print(f"  {r['identifier']}: metadata failed ({str(e)[:50]})")
            continue
        if not proxy or mb > MAX_MB:
            continue
        dst = MEDIA / f"{r['identifier']}{Path(urllib.parse.urlparse(proxy).path).suffix}"
        if dst.exists() and dst.stat().st_size > 0:
            continue
        jobs.append((proxy, dst, mb))
    if not jobs:
        return
    total = sum(j[2] for j in jobs)
    print(f"  downloading {len(jobs)} file(s), {total/1000:.1f} GB, {PREFETCH} at a time")
    done = [0]
    with ThreadPoolExecutor(max_workers=PREFETCH) as pool:
        futures = {pool.submit(download, u, d): (d, mb) for u, d, mb in jobs}
        for fut in as_completed(futures):
            d, mb = futures[fut]
            done[0] += 1
            try:
                fut.result()
                print(f"  [{done[0]}/{len(jobs)}] {d.name[:50]:50s} {mb:6.0f} MB", flush=True)
            except Exception as e:                               # noqa: BLE001
                print(f"  [{done[0]}/{len(jobs)}] {d.name[:50]:50s} FAILED {str(e)[:50]}",
                      flush=True)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                          "-show_entries", "stream=width,height:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True)
    try:
        d = json.loads(out.stdout)
        st = (d.get("streams") or [{}])[0]
        return (float(d.get("format", {}).get("duration") or 0),
                int(st.get("width") or 0), int(st.get("height") or 0))
    except Exception:                                            # noqa: BLE001
        return 0.0, 0, 0


def extract(path, out_dir, every=EVERY_S):
    out_dir.mkdir(parents=True, exist_ok=True)
    have = sorted(out_dir.glob("*.jpg"))
    if have:
        return have
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path),
                    "-vf", f"fps=1/{every},scale=640:-2", "-q:v", "6",
                    str(out_dir / "%05d.jpg")], check=False)
    return sorted(out_dir.glob("*.jpg"))


def is_colour(path, threshold=14.0):
    """Colour measured from the pixels: the mean distance between the channels.

    A black-and-white print digitised to a colour file still reports "colour" in
    metadata and in ffprobe, so neither can answer this. Sepia and faded stock sit
    just above the line, which is why the number is written down per frame.
    """
    import numpy as np
    with Image.open(path) as im:
        a = np.asarray(im.convert("RGB").resize((160, 120)), dtype=np.float32)
    mx, mn = a.max(axis=2), a.min(axis=2)
    return float((mx - mn).mean()), float((mx - mn).mean()) >= threshold


# --- the judge -----------------------------------------------------------------------

_last = [0.0]


def _throttle():
    wait = MIN_GAP_S - (time.monotonic() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.monotonic()


def _encode(path, side=512):
    with Image.open(path) as im:
        im = im.convert("RGB")
        s = min(1.0, side / max(im.size))
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                       Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=78)
    return base64.b64encode(buf.getvalue()).decode("ascii")


class Quota(RuntimeError):
    pass


_spent = set()


def judge(paths, api_key):
    """[{usable, label, people, clean, note}] for a batch of frames, cached by batch."""
    sha = lambda s: __import__("hashlib").sha1(s.encode()).hexdigest()[:20]
    f = VERDICTS / f"{sha('|'.join(Path(p).relative_to(HERE).as_posix() for p in paths))}.json"
    old = VERDICTS / f"{sha('|'.join(str(p) for p in paths))}.json"
    for g in (f, old):
        if g.exists():
            return json.loads(g.read_text(encoding="utf-8"))
    if (MAX_CALLS and _calls[0] >= MAX_CALLS) or (_budget[0] and _calls[0] >= _budget[0]):
        raise Quota(f"the day's cap of {MAX_CALLS} requests is reached" if MAX_CALLS and _calls[0] >= MAX_CALLS
                    else "this set's share of the day is spent")
    parts = [{"text": "Frames follow, in order."}]
    for i, p in enumerate(paths):
        parts.append({"text": f"frame {i}:"})
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": _encode(p)}})
    payload = {"contents": [{"role": "user", "parts": parts}],
               "systemInstruction": {"parts": [{"text": SYSTEM}]},
               "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.0,
                                    "responseMimeType": "application/json"}}
    body = json.dumps(payload).encode()
    results = None
    for model in MODELS:
        if model in _spent:
            continue
        for attempt in range(RETRIES):
            _throttle()
            _calls[0] += 1
            req = urllib.request.Request(URL.format(model=model), data=body, method="POST",
                                         headers={"Content-Type": "application/json",
                                                  "x-goog-api-key": api_key})
            try:
                with urllib.request.urlopen(req, timeout=300) as r:
                    data = json.loads(r.read().decode("utf-8", "replace"))
                cand = (data.get("candidates") or [{}])[0]
                text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", [])
                               if "text" in p)
                results = json.loads(text).get("results", [])
                break
            except urllib.error.HTTPError as e:
                detail = e.read().decode("utf-8", "replace")
                if e.code == 429 and "PerDay" in detail:
                    _spent.add(model)
                    print(f"    {model}: the day's free requests are spent", flush=True)
                    break
                if e.code not in (429, 500, 502, 503, 504):
                    raise
                time.sleep(5 * (attempt + 1))
            except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
                time.sleep(5 * (attempt + 1))
        if results is not None:
            break
    if results is None and len(_spent) == len(MODELS):
        raise Quota("every model's day is spent")
    if results is None:
        # Never "not usable": a frame nobody looked at is unknown, and counting it as
        # usable or unusable would both be inventing an answer.
        return [{"usable": None, "label": "", "people": "", "clean": None,
                 "note": "not judged"} for _ in paths]
    by_i = {r.get("i"): r for r in results}
    out = []
    for i, _p in enumerate(paths):
        r = by_i.get(i)
        out.append({"usable": None, "label": "", "people": "", "clean": None,
                    "note": "no verdict"} if r is None else
                   {"usable": bool(r.get("usable")), "label": str(r.get("label") or ""),
                    "people": str(r.get("people") or ""), "clean": bool(r.get("clean", True)),
                    "note": str(r.get("note") or "")[:60]})
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


# --- a run ---------------------------------------------------------------------------

def scan_film(row, api_key, every=EVERY_S):
    ident = row["identifier"]
    meta = FRAMES / ident / "meta.json"
    if meta.exists() and sorted((FRAMES / ident).glob("*.jpg")):
        m = json.loads(meta.read_text(encoding="utf-8"))
        best, size_mb, secs, w, h = m["best"], m["size_mb"], m["secs"], m["w"], m["h"]
        frames = sorted((FRAMES / ident).glob("*.jpg"))
    else:
        if row.get("_closed"):
            return {**row, "status": "waiting: not opened yet"}, []
        best, proxy, size_mb = best_and_proxy(ident)
        if not proxy:
            return {**row, "status": "no video file"}, []
        if size_mb > MAX_MB:
            return {**row, "status": f"skipped: smallest copy is {size_mb:.0f} MB", "best_res": best}, []
        path = download(proxy, MEDIA / f"{ident}{Path(urllib.parse.urlparse(proxy).path).suffix}")
        secs, w, h = probe(path)
        if secs <= 0:
            return {**row, "status": "unreadable video", "best_res": best}, []
        frames = extract(path, FRAMES / ident, every)
        if not frames:
            return {**row, "status": "no frames", "best_res": best}, []
        meta.write_text(json.dumps({"best": best, "size_mb": size_mb, "secs": secs, "w": w, "h": h}),
                        encoding="utf-8")
        if DROP_MEDIA:
            path.unlink(missing_ok=True)

    verdicts = []
    for i in range(0, len(frames), BATCH):
        verdicts += judge(frames[i:i + BATCH], api_key)
    rows = []
    for n, (fr, v) in enumerate(zip(frames, verdicts)):
        chroma, colour = is_colour(fr)
        rows.append({"identifier": ident, "frame": fr.name, "at_s": n * every,
                     "usable": v["usable"], "label": v["label"], "people": v["people"],
                     "clean": v["clean"], "chroma": round(chroma, 1), "colour": colour,
                     "note": v["note"]})
    usable = [r for r in rows if r["usable"]]
    unjudged = sum(1 for r in rows if r["usable"] is None)
    # A film the judge only got halfway through is not a film with no street in it.
    # When the day's allowance ran out mid-reel the first run wrote "0.0 min usable"
    # for three films whose frames had never been looked at, which reads as a finding
    # and is not one. Over a tenth unjudged and the minutes are withheld; the next run
    # asks only the batches that failed, because only answered batches are cached.
    if rows and unjudged > len(rows) * 0.10:
        return {**row, "status": f"partly judged: {unjudged} of {len(rows)} frames",
                "best_res": best, "duration_min": round(secs / 60, 1),
                "frames": len(rows), "frames_unjudged": unjudged,
                "usable_min": "", "usable_colour_min": "", "usable_share": ""}, rows
    labels = {}
    for r in usable:
        labels[r["label"]] = labels.get(r["label"], 0) + 1
    colour_frames = sum(1 for r in rows if r["colour"])
    return {**row,
            "status": "scanned",
            "best_res": best, "proxy_mb": round(size_mb, 1),
            "duration_min": round(secs / 60, 1), "scan_res": f"{w}x{h}",
            "frames": len(rows), "frames_unjudged": unjudged,
            "usable_frames": len(usable),
            "usable_min": round(len(usable) * every / 60, 1),
            "usable_share": round(len(usable) / len(rows), 2) if rows else 0,
            "colour_measured": "colour" if colour_frames > len(rows) * 0.6 else
                               "some" if colour_frames > len(rows) * 0.1 else "bw",
            "usable_colour_min": round(sum(1 for r in usable if r["colour"]) * every / 60, 1),
            "clean_share": round(sum(1 for r in usable if r["clean"]) / len(usable), 2)
                           if usable else "",
            "labels": "|".join(f"{k}:{v}" for k, v in
                               sorted(labels.items(), key=lambda kv: -kv[1])),
            }, rows


REFUGEE_TITLE = re.compile(r"displaced person|\bdp camp\b|\bdp\b|refugee|expell|emigra|"
                           r"resettl|repatriat|unrra|\biro\b|relief|camp #", re.I)


def load(which):
    """The films to open, in the order they are worth opening.

    The refugee set is ranked on its own terms. `promise` orders by how much living
    street a film is likely to hold and penalises anything that looks like war, which
    puts "Return of Displaced Persons from Ordruf to Chemnitz" near the bottom - exactly
    the film the series is for.
    """
    if which == "refugees":
        rows = list(csv.DictReader(open(HERE / "films_de.csv", encoding="utf-8")))
        rows = [r for r in rows if "refugees" in (r.get("content") or "")
                and (not r["year"] or 1945 <= int(r["year"]) <= 1955)]
        rows.sort(key=lambda r: (-len(REFUGEE_TITLE.findall(r["title"])),
                                 -int(r["promise"]), r["year"] or "9999"))
        return rows
    return list(csv.DictReader(open(HERE / f"films_{which}.csv", encoding="utf-8")))


COLS = ["identifier", "title", "year", "cities", "content", "status", "duration_min",
        "usable_min", "usable_colour_min", "usable_share", "frames", "usable_frames",
        "frames_unjudged", "colour_measured", "colour", "clean_share", "labels",
        "best_res", "scan_res", "proxy_mb", "licence_rule", "promise", "page"]
CHUNK = 15                       # films fetched at once: a runner's disk holds them easily
SHARE = {"refugees": 0.15, "it": 0.30}   # of the day's cap; Germany takes what is left


def opened(row):
    return (FRAMES / row["identifier"] / "meta.json").exists()


def run_set(which, n_films, api_key):
    rows = load(which)[:n_films]
    print(f"{which}: {len(rows)} film(s), {sum(map(opened, rows))} opened before", flush=True)
    out, frame_rows, stopped = [], [], None
    for c in range(0, len(rows), CHUNK):
        chunk = rows[c:c + CHUNK]
        if not stopped and not (DEADLINE and time.time() > DEADLINE):
            prefetch([r for r in chunk if not opened(r)])
        for n, row in enumerate(chunk, c + 1):
            if not stopped and DEADLINE and time.time() > DEADLINE:
                stopped = "the run's time is up"
            row = {**row, "_closed": bool(stopped)}
            try:
                res, frames = scan_film(row, api_key)
            except Quota as e:
                if not stopped:
                    print(f"  stopped: {e}; what is done is kept", flush=True)
                stopped = stopped or str(e)
                res, frames = {**row, "status": "waiting: not judged yet"}, []
            except Exception as e:                               # noqa: BLE001
                res, frames = {**row, "status": f"error: {str(e)[:80]}"}, []
            out.append(res)
            frame_rows += frames
            if res.get("status") == "scanned" or not str(res.get("status", "")).startswith("waiting"):
                print(f"  [{n}/{len(rows)}] {row['identifier'][:48]:48s} "
                      f"{res.get('status','')[:26]:26s} {res.get('duration_min','?')} min -> "
                      f"{res.get('usable_min','?')} min usable "
                      f"({res.get('colour_measured','?')})", flush=True)

    with open(HERE / f"scan_{which}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    with open(HERE / f"frames_{which}.csv", "w", newline="", encoding="utf-8") as f:
        if frame_rows:
            w = csv.DictWriter(f, fieldnames=list(frame_rows[0]))
            w.writeheader()
            w.writerows(frame_rows)
    done = [r for r in out if r.get("status") == "scanned"]
    waiting = sum(1 for r in out if str(r.get("status", "")).startswith("waiting"))
    total = sum(r["usable_min"] for r in done)
    print(f"{which}: {len(done)} of {len(rows)} film(s) scanned, {waiting} waiting, {total:.0f} usable "
          f"minutes ({sum(r['usable_colour_min'] for r in done):.0f} of them colour); "
          f"{_calls[0]} request(s) so far today", flush=True)
    return {"set": which, "films": len(rows), "scanned": len(done), "waiting": waiting,
            "usable_min": round(total, 1), "stopped": stopped}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=("de", "it", "refugees", "all"))
    ap.add_argument("--films", type=int, default=0, help="the first N of the set (0: all)")
    args = ap.parse_args()

    api_key = key()
    n = args.films or 10 ** 6
    sets = ("refugees", "it", "de") if args.which == "all" else (args.which,)
    progress = []
    for s in sets:
        _budget[0] = (_calls[0] + int(MAX_CALLS * SHARE[s])) if MAX_CALLS and s in SHARE and len(sets) > 1 else 0
        progress.append(run_set(s, n, api_key))
    (HERE / "progress.json").write_text(json.dumps({"requests_today": _calls[0], "sets": progress},
                                                   indent=1), encoding="utf-8")
    left = sum(p["waiting"] for p in progress)
    print(f"\n{_calls[0]} request(s) this run; {left} film(s) still waiting" +
          (". Run again tomorrow; nothing is re-downloaded or re-asked." if left else ". All done."))


if __name__ == "__main__":
    main()
