"""Build deterministic, printable HTML puzzle packs and PNG covers."""

import argparse
import html
import random
import struct
import zlib
from pathlib import Path

from generator import maze, sudoku, wordsearch


STYLE = """
@page { size: PAGE_SIZE; margin: 16mm; }
body { font-family: Arial, sans-serif; color: #18304b; margin: 0; }
.page { break-after: page; page-break-after: always; min-height: 240mm; }
.cover { text-align: center; padding-top: 25mm; }
.cover img { width: 70mm; height: 95mm; object-fit: cover; }
h1, h2 { color: #164979; } h2 { margin-bottom: 4mm; }
p { line-height: 1.4; }
table { border-collapse: collapse; margin: 6mm auto; }
td { text-align: center; vertical-align: middle; }
.sudoku td { width: 10mm; height: 10mm; border: 1px solid #778; font-size: 17pt; }
.sudoku tr:nth-child(3n) td { border-bottom: 2px solid #18304b; }
.sudoku td:nth-child(3n) { border-right: 2px solid #18304b; }
.maze td { width: 4.4mm; height: 4.4mm; padding: 0; }
.wall { background: #18304b; } .route { background: #f4bd52; }
.wordsearch td { width: 7mm; height: 7mm; border: 1px solid #ccd; font-weight: bold; }
.found { background: #f4bd52; }
.words { text-align: center; max-width: 150mm; margin: auto; }
.solutions { text-align: center; }
@media screen { body { max-width: 210mm; margin: auto; background: #f3f6fa; }
  .page { background: white; padding: 16mm; margin: 8mm auto; box-shadow: 0 2px 12px #bbb; } }
"""


def cover_png(path, color):
    """Write a valid RGB PNG using only the standard library."""
    width, height = 320, 440
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            band = ((x // 40) + (y // 40)) % 2
            if 30 < x < 290 and 90 < y < 350 and (x // 24 + y // 24) % 3 == 0:
                pixel = (244, 189, 82)
            else:
                pixel = tuple(min(255, channel + band * 18) for channel in color)
            raw.extend(pixel)

    def chunk(kind, data):
        return struct.pack("!I", len(data)) + kind + data + struct.pack("!I", zlib.crc32(kind + data) & 0xffffffff)

    payload = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack("!2I5B", width, height, 8, 2, 0, 0, 0))
               + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))
    path.write_bytes(payload)


def page(title, body, extra_class=""):
    return f'<section class="page {extra_class}"><h2>{html.escape(title)}</h2>{body}</section>'


def table(grid, kind, highlights=()):
    marked = {tuple(cell) for cell in highlights}
    rows = []
    for y, row in enumerate(grid):
        cells = []
        for x, value in enumerate(row):
            if kind == "maze":
                css = "wall" if value else ("route" if (x, y) in marked else "")
                content = ""
            else:
                css = "found" if (x, y) in marked else ""
                content = html.escape(str(value)) if value else "&nbsp;"
            cells.append(f'<td class="{css}">{content}</td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return f'<table class="{kind}">' + "".join(rows) + "</table>"


def maze_route(item):
    cells = set()
    path = item["path"]
    for x, y in path:
        cells.add((2 * x + 1, 2 * y + 1))
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        cells.add((x1 + x2 + 1, y1 + y2 + 1))
    return cells


def render_document(title, items, kind, cover_name, paper="A4"):
    intro = (f'<section class="page cover"><h1>{html.escape(title)}</h1>'
             f'<img src="{html.escape(cover_name)}" alt="Portada decorativa">'
             '<p>Pasatiempos imprimibles · Soluciones al final</p></section>')
    puzzles = []
    solutions = [page("Soluciones", "<p>Respuestas de los pasatiempos anteriores.</p>", "solutions")]
    for index, item in enumerate(items, 1):
        label = f"{kind.capitalize()} {index}"
        if kind == "sudoku":
            puzzles.append(page(label, f'<p>Dificultad: {item["difficulty"]}</p>' + table(item["puzzle"], "sudoku")))
            solutions.append(page(f"Solución · {label}", table(item["solution"], "sudoku")))
        elif kind == "laberinto":
            puzzles.append(page(label, '<p>Entrada: esquina superior izquierda. Salida: esquina inferior derecha.</p>'
                                + table(item["grid"], "maze")))
            solutions.append(page(f"Solución · {label}", table(item["grid"], "maze", maze_route(item))))
        else:
            words = " · ".join(html.escape(word) for word in item["words"])
            puzzles.append(page(label, table(item["grid"], "wordsearch") + f'<p class="words">{words}</p>'))
            marked = [cell for cells in item["placements"].values() for cell in cells]
            solutions.append(page(f"Solución · {label}", table(item["grid"], "wordsearch", marked)))
    css = STYLE.replace("PAGE_SIZE", paper)
    return ('<!doctype html><html lang="es"><head><meta charset="utf-8"><title>'
            + html.escape(title) + '</title><style>' + css + '</style></head><body>'
            + intro + "".join(puzzles + solutions) + '</body></html>\n')


def render_sample(sudokus, one_maze, cover_name):
    intro = (f'<section class="page cover"><h1>Muestra gratis</h1><img src="{cover_name}" alt="Portada decorativa">'
             '<p>2 sudokus y 1 laberinto · Soluciones al final</p></section>')
    puzzles = []
    answers = [page("Soluciones", "<p>Respuestas de la muestra.</p>", "solutions")]
    for index, item in enumerate(sudokus[:2], 1):
        puzzles.append(page(f"Sudoku {index}", table(item["puzzle"], "sudoku")))
        answers.append(page(f"Solución · Sudoku {index}", table(item["solution"], "sudoku")))
    puzzles.append(page("Laberinto 1", table(one_maze["grid"], "maze")))
    answers.append(page("Solución · Laberinto 1", table(one_maze["grid"], "maze", maze_route(one_maze))))
    return ('<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Muestra gratis</title>'
            '<style>' + STYLE.replace("PAGE_SIZE", "A4") + '</style></head><body>'
            + intro + "".join(puzzles + answers) + '</body></html>\n')


def build(out, seed=2026, count=6):
    if count < 2:
        raise ValueError("count must be at least 2 for the free sample")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    sudokus = [sudoku.generate(rng.getrandbits(64), "facil" if index % 2 == 0 else "medio")
               for index in range(count)]
    mazes = [maze.generate(10, 10, rng.getrandbits(64)) for _ in range(count)]
    searches = [wordsearch.generate(wordsearch.DEFAULT_WORDS, rng.getrandbits(64)) for _ in range(count)]
    covers = {"sudokus": (30, 75, 118), "laberintos": (45, 108, 98),
              "sopas": (103, 67, 120), "muestra_gratis": (122, 75, 53)}
    for name, color in covers.items():
        cover_png(out / f"portada_{name}.png", color)
    files = {
        "pack_sudokus.html": render_document("Pack de sudokus", sudokus, "sudoku", "portada_sudokus.png"),
        "pack_sudokus_carta.html": render_document("Pack de sudokus", sudokus, "sudoku", "portada_sudokus.png", "letter"),
        "pack_laberintos.html": render_document("Pack de laberintos", mazes, "laberinto", "portada_laberintos.png"),
        "pack_sopas.html": render_document("Pack de sopas de letras", searches, "sopa", "portada_sopas.png"),
        "muestra_gratis.html": render_sample(sudokus, mazes[0], "portada_muestra_gratis.png"),
    }
    for name, content in files.items():
        (out / name).write_text(content, encoding="utf-8")
    return [out / name for name in files] + [out / f"portada_{name}.png" for name in covers]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("products"))
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--n", type=int, default=6, help="puzzles per full pack; minimum 2")
    args = parser.parse_args(argv)
    for path in build(args.out, args.seed, args.n):
        print(f"{path}: {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
