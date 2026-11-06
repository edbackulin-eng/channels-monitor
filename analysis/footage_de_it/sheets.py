"""A contact sheet for each of the best films: one frame every 20 seconds.

    python -X utf8 analysis/footage_de_it/sheets.py de --top 10
    python -X utf8 analysis/footage_de_it/sheets.py it --top 10
    python -X utf8 analysis/footage_de_it/sheets.py refugees --top 5

Analysis only. Reads the frames scan.py already took - every 10 seconds - and
uses every second one, so nothing is downloaded or decoded again.

A sheet is how a number becomes checkable. "Eleven usable minutes" is an opinion
until someone can see which eleven: every tile carries its timestamp, and a tile
the judge counted as living street is marked, so a wrong verdict shows up as a
marked tile with nobody in it.

Written to analysis/footage_de_it/sheets/<set>_<rank>_<identifier>.jpg. The
repository ignores *.jpg, so they stay on disk unless somebody decides they
belong in git.
"""
import argparse
import csv
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FRAMES = HERE / "frames"
SHEETS = HERE / "sheets"
ROOT = HERE.parent.parent

EVERY = 2                # of the 10-second frames: so one every 20 seconds
COLS = 6
TILE_W = 320
HEAD_H = 96
LABEL_H = 22
MAX_TILES = 90           # a 30-minute film is 90 tiles; longer ones are thinned further

GREEN = (46, 160, 67)
GREY = (70, 70, 74)
AMBER = (210, 150, 30)


def font(size, bold=False):
    # Windows names first; DejaVu on a Linux runner (fonts-dejavu-core)
    for name in (("arialbd.ttf", "seguisb.ttf", "DejaVuSans-Bold.ttf") if bold
                 else ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf")):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def hhmmss(seconds):
    s = int(seconds)
    return f"{s // 3600:d}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 \
        else f"{s // 60:d}:{s % 60:02d}"


def frames_of(identifier, verdicts):
    files = sorted((FRAMES / identifier).glob("*.jpg"))
    out = []
    for n, f in enumerate(files):
        if n % EVERY:
            continue
        out.append((n * 10, f, verdicts.get(f.name)))
    if len(out) > MAX_TILES:                      # keep the whole film in view, thinned
        step = (len(out) + MAX_TILES - 1) // MAX_TILES
        out = out[::step]
    return out


def sheet(film, verdicts, dst):
    tiles = frames_of(film["identifier"], verdicts)
    if not tiles:
        return None
    with Image.open(tiles[0][1]) as probe:
        ratio = probe.height / probe.width
    tile_h = round(TILE_W * ratio)
    rows = (len(tiles) + COLS - 1) // COLS
    W = COLS * TILE_W
    H = HEAD_H + rows * (tile_h + LABEL_H)
    im = Image.new("RGB", (W, H), (16, 16, 18))
    d = ImageDraw.Draw(im)

    title = f"{film['title'][:92]}"
    sub = (f"{film.get('year') or 'undated'} · {film.get('duration_min', '?')} min · "
           f"{film.get('usable_min', '?')} min of living street and everyday life "
           f"({film.get('usable_share', '?')} of the film) · {film.get('colour_measured', '?')} · "
           f"best copy {film.get('best_res') or 'unknown'} · one frame every 20 s")
    d.text((14, 12), title, font=font(26, True), fill=(255, 255, 255))
    for i, line in enumerate(textwrap.wrap(sub, 150)[:2]):
        d.text((14, 48 + i * 20), line, font=font(15), fill=(185, 185, 190))
    d.text((W - 320, 12), film["identifier"][:40], font=font(14), fill=(120, 120, 128))
    d.text((W - 320, 32), film.get("page", ""), font=font(13), fill=(100, 100, 110))

    for k, (at, path, verdict) in enumerate(tiles):
        x = (k % COLS) * TILE_W
        y = HEAD_H + (k // COLS) * (tile_h + LABEL_H)
        with Image.open(path) as t:
            im.paste(t.convert("RGB").resize((TILE_W, tile_h), Image.LANCZOS), (x, y))
        usable = (verdict or {}).get("usable")
        colour = GREEN if usable == "True" else AMBER if usable in (None, "", "None") else GREY
        d.rectangle((x, y + tile_h, x + TILE_W - 1, y + tile_h + LABEL_H - 1), fill=colour)
        label = (verdict or {}).get("label", "") or "not judged"
        d.text((x + 5, y + tile_h + 3), f"{hhmmss(at)}  {label[:22]}", font=font(13),
               fill=(255, 255, 255))
        d.rectangle((x, y, x + TILE_W - 1, y + tile_h - 1), outline=(16, 16, 18), width=1)

    d.text((14, H - 1), "", font=font(10))
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, quality=78, optimize=True)
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=("de", "it", "refugees"))
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()

    films = [r for r in csv.DictReader(open(HERE / f"scan_{args.which}.csv", encoding="utf-8"))
             if r.get("status") == "scanned"]
    films.sort(key=lambda r: -float(r["usable_min"] or 0))
    verdicts = {}
    path = HERE / f"frames_{args.which}.csv"
    if path.exists():
        for r in csv.DictReader(open(path, encoding="utf-8")):
            verdicts.setdefault(r["identifier"], {})[r["frame"]] = r

    made = []
    for rank, film in enumerate(films[:args.top], 1):
        dst = SHEETS / f"{args.which}_{rank:02d}_{film['identifier']}.jpg"
        out = sheet(film, verdicts.get(film["identifier"], {}), dst)
        if out:
            made.append(out)
            print(f"  {rank:>2}. {film['usable_min']:>5} min usable  {out.name}  "
                  f"({out.stat().st_size/1e6:.1f} MB)")
    print(f"{args.which}: {len(made)} sheet(s) in {SHEETS}")


if __name__ == "__main__":
    main()
