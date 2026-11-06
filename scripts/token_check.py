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


def gemini(key):
    if not key:
        return False, "GEMINI_API_KEY_MON is not set"
    base = "https://generativelanguage.googleapis.com/v1beta/models/" + autofix.MODEL
    h = {"x-goog-api-key": key, "Content-Type": "application/json"}
    try:
        with urllib.request.urlopen(urllib.request.Request(base, headers=h), timeout=30) as r:
            name = json.load(r).get("name", "?")
        body = json.dumps({"contents": [{"parts": [{"text": "Answer with one word: ok"}]}],
                           "generationConfig": {"maxOutputTokens": 5}}).encode()
        with urllib.request.urlopen(urllib.request.Request(base + ":generateContent", data=body, headers=h),
                                    timeout=60) as r:
            json.load(r)
        return True, f"works ({name}: model found, one request answered)"
    except urllib.error.HTTPError as e:
        return False, f"refused: HTTP {e.code}"
    except (urllib.error.URLError, OSError) as e:
        return False, f"no answer: {type(e).__name__}"


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
