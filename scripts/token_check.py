"""What MONITOR_TOKEN may write and whether GEMINI_API_KEY_MON works (owner 06.11).

Run by .github/workflows/token-check.yml. Nothing is written anywhere: the rights are probed
the way the monitor probes them every pass (monitor/check.py Net.rights - a PUT with a sha
that cannot match, refused with 409/422 where the token may write, 403/404 where it may not),
and the key is tried with one model lookup and one tiny request. Neither secret is printed.
Exit 1 if a right or the key is missing.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from monitor import autofix  # noqa: E402
from monitor import channels as C  # noqa: E402
from monitor.check import Net  # noqa: E402


def _quota(e):
    """What a 429 says about the quota: its id and limit (the body holds no secret)."""
    try:
        d = json.loads(e.read().decode("utf-8", "replace"))
    except (ValueError, OSError):
        return ""
    out = []
    for det in d.get("error", {}).get("details", []):
        for v in det.get("violations", []):
            out.append(f"{v.get('quotaId', '?')} limit {v.get('quotaValue', '?')}")
        if det.get("retryDelay"):
            out.append(f"retry in {det['retryDelay']}")
    return "; ".join(out) or d.get("error", {}).get("message", "")[:200]


def gemini(key):
    """(works, text): one model lookup, then one tiny request per model the monitor and
    the footage audit use."""
    if not key:
        return False, "GEMINI_API_KEY_MON is not set"
    h = {"x-goog-api-key": key, "Content-Type": "application/json"}
    root = "https://generativelanguage.googleapis.com/v1beta/models/"
    try:
        with urllib.request.urlopen(urllib.request.Request(root + autofix.MODEL, headers=h), timeout=60) as r:
            json.load(r)
    except urllib.error.HTTPError as e:
        return False, f"the key is refused: HTTP {e.code}"
    except (urllib.error.URLError, OSError) as e:
        return False, f"no answer ({type(e).__name__})"
    lines, ok_all = ["the key is valid (model lookup answered)"], True
    body = json.dumps({"contents": [{"parts": [{"text": "Answer with one word: ok"}]}]}).encode()
    for model in (autofix.MODEL, "gemini-flash-lite-latest"):
        try:
            with urllib.request.urlopen(urllib.request.Request(root + model + ":generateContent", data=body,
                                                               headers=h), timeout=180) as r:
                json.load(r)
            lines.append(f"{model}: answers")
        except urllib.error.HTTPError as e:
            ok_all = ok_all and model != autofix.MODEL
            lines.append(f"{model}: HTTP {e.code} {_quota(e) if e.code == 429 else ''}".rstrip())
        except (urllib.error.URLError, OSError) as e:
            ok_all = ok_all and model != autofix.MODEL
            lines.append(f"{model}: no answer ({type(e).__name__})")
    return ok_all, "; ".join(lines)


def main():
    net = Net()
    if not net.write:
        print("MONITOR_TOKEN is not set")
        return 1
    bad = 0
    repos = [c["repo"] for c in C.CHANNELS if c.get("act")] + [net.repo]
    print("MONITOR_TOKEN (probed, nothing written):")
    for r in repos:
        got = net.rights(r)
        mark = lambda v: "yes" if v else "NO" if v is False else "no answer"
        print(f"  {r:40s} Contents RW: {mark(got['contents']):9s} Workflows RW: {mark(got['workflows'])}")
        bad |= not (got["contents"] and got["workflows"])
    ok, why = gemini(os.environ.get("GEMINI_API_KEY_MON", ""))
    print(f"GEMINI_API_KEY_MON: {why}")
    bad |= not ok
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
