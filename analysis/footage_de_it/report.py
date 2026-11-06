"""Add the scan up: minutes by country, by city, by year, and how many episodes that is.

    python -X utf8 analysis/footage_de_it/report.py

Analysis only. Reads what discover.py and scan.py wrote and writes
summary.md, by_city.csv and by_year.csv beside them. Nothing is fetched.

The one number everything turns on is "usable minutes": frames the vision judge
called living street or everyday life, times the ten seconds each frame stands
for. Two things follow from how it is measured, and both are stated wherever it
is used:

  - it is a sample. A shot shorter than ten seconds can fall between frames, and
    a frame that passes can sit inside a shot that turns away. The error runs
    both ways and is the same for every film, which is what makes films
    comparable to each other but not to a stopwatch.
  - a film is only counted when it was actually opened. Films left in the
    catalogue unscanned are reported separately and never estimated from their
    titles.

Episodes are counted as the brief asks: a shot may be used at most twice on the
channel, and an episode runs 15-20 minutes, so the stock is usable minutes x 2
and an episode spends 17.5 of it on average.
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
EPISODE_MIN = 17.5
USES_PER_SHOT = 2
SETS = ("de", "it", "refugees")
NAMES = {"de": "Germany", "it": "Italy", "refugees": "Germany - Flucht, Vertreibung, Neuanfang"}


def rows(name):
    p = HERE / name
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


def num(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def scanned(which):
    return [r for r in rows(f"scan_{which}.csv") if r.get("status") == "scanned"]


def frames(which):
    return rows(f"frames_{which}.csv")


def episodes(minutes):
    return minutes * USES_PER_SHOT / EPISODE_MIN


def by_city(films, frame_rows):
    """Usable minutes credited to each city a film names.

    A reel that names Berlin and Frankfurt has its minutes credited to both, so
    these add up to more than the country's total. The alternative - splitting
    them evenly - would invent a precision the metadata does not have.
    """
    out = defaultdict(float)
    for f in films:
        mins = num(f.get("usable_min"))
        cities = [c for c in (f.get("cities") or "").split("|") if c]
        for c in cities or ["(no city named)"]:
            out[c] += mins
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def by_year(films):
    out = defaultdict(float)
    for f in films:
        out[f.get("year") or "undated"] += num(f.get("usable_min"))
    return dict(sorted(out.items(), key=lambda kv: (kv[0] == "undated", kv[0])))


def labels(frame_rows):
    c = Counter(r["label"] for r in frame_rows if r.get("usable") == "True" and r.get("label"))
    return c.most_common()


def summarise(which):
    films = scanned(which)
    fr = frames(which)
    catalogue = rows(f"films_{which}.csv") if which != "refugees" else []
    total = sum(num(f.get("usable_min")) for f in films)
    colour = sum(num(f.get("usable_colour_min")) for f in films)
    opened = sum(num(f.get("duration_min")) for f in films)
    judged = sum(int(num(f.get("frames"))) for f in films)
    unjudged = sum(int(num(f.get("frames_unjudged"))) for f in films)
    return {
        "set": which, "name": NAMES[which],
        "catalogued": len(catalogue) or len(rows(f"scan_{which}.csv")),
        "opened": len(films),
        "film_minutes_opened": round(opened, 1),
        "usable_min": round(total, 1),
        "usable_colour_min": round(colour, 1),
        "usable_share": round(total / opened, 3) if opened else 0,
        "frames": judged, "frames_unjudged": unjudged,
        "episodes": round(episodes(total), 1),
        "by_city": by_city(films, fr),
        "by_year": by_year(films),
        "labels": labels(fr),
        "films": sorted(films, key=lambda f: -num(f.get("usable_min"))),
    }


def table(d, head, fmt="{:.1f}"):
    lines = [f"| {head} | minutes | episodes |", "|---|---|---|"]
    for k, v in d.items():
        lines.append(f"| {k} | {fmt.format(v)} | {episodes(v):.1f} |")
    return "\n".join(lines)


def main():
    out = {w: summarise(w) for w in SETS}
    md = ["# Free footage of Germany and Italy, 1945-1969",
          "",
          "Measured, not estimated: every film in the tables below was downloaded and",
          "looked at one frame per ten seconds. \"Usable\" means the vision judge saw",
          "ordinary people living their lives in a real place - a street, a market, a shop,",
          "a home, a workplace, a station - and not an empty ruin, a parade, a map, a title",
          "card or an official at a desk.",
          "",
          f"An episode is taken as {EPISODE_MIN} minutes and a shot may be used at most",
          f"{USES_PER_SHOT} times on the channel, so episodes = usable minutes x "
          f"{USES_PER_SHOT} / {EPISODE_MIN}.",
          ""]
    md += ["## The two countries, side by side", "",
           "| | catalogued free films | opened | minutes opened | usable minutes | of them colour | share usable | episodes |",
           "|---|---|---|---|---|---|---|---|"]
    for w in SETS:
        d = out[w]
        md.append(f"| {d['name']} | {d['catalogued']} | {d['opened']} | "
                  f"{d['film_minutes_opened']:.0f} | **{d['usable_min']:.0f}** | "
                  f"{d['usable_colour_min']:.0f} | {d['usable_share']:.0%} | "
                  f"**{d['episodes']:.0f}** |")
    md.append("")
    for w in SETS:
        d = out[w]
        md += [f"## {d['name']}", ""]
        if not d["opened"]:
            md += ["Not scanned yet.", ""]
            continue
        md += [f"{d['opened']} films opened, {d['film_minutes_opened']:.0f} minutes of film, "
               f"{d['frames']} frames judged"
               + (f" ({d['frames_unjudged']} could not be judged)" if d["frames_unjudged"] else "")
               + ".", "",
               "### By city", "", table(d["by_city"], "city"), "",
               "A film that names two cities is counted under both, so these add up to more "
               "than the total.", "",
               "### By year", "", table(d["by_year"], "year"), "",
               "### What the usable frames show", "",
               ", ".join(f"{k} {v}" for k, v in d["labels"]) or "nothing", "",
               "### The films, best first", "",
               "| usable min | of them colour | share | year | cities | best copy | film |",
               "|---|---|---|---|---|---|---|"]
        for f in d["films"]:
            md.append(f"| {num(f['usable_min']):.1f} | {num(f['usable_colour_min']):.1f} | "
                      f"{num(f['usable_share']):.0%} | {f.get('year') or 'undated'} | "
                      f"{(f.get('cities') or '-').replace('|', ', ')} | "
                      f"{f.get('best_res') or '?'} | [{f['title'][:70]}]({f.get('page','')}) |")
        md.append("")
    (HERE / "summary.md").write_text("\n".join(md), encoding="utf-8")

    with open(HERE / "by_city.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["set", "city", "usable_min", "episodes"])
        for s in SETS:
            for c, v in out[s]["by_city"].items():
                w.writerow([s, c, round(v, 1), round(episodes(v), 1)])
    with open(HERE / "by_year.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["set", "year", "usable_min", "episodes"])
        for s in SETS:
            for y, v in out[s]["by_year"].items():
                w.writerow([s, y, round(v, 1), round(episodes(v), 1)])
    for s in SETS:
        d = out[s]
        print(f"{d['name'][:40]:40s} opened {d['opened']:>3}  usable {d['usable_min']:>7.1f} min  "
              f"colour {d['usable_colour_min']:>6.1f}  -> {d['episodes']:.0f} episodes")
    print(f"\nwritten: {HERE / 'summary.md'}")


if __name__ == "__main__":
    main()
