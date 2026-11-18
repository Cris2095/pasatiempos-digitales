"""Genera los HTML existentes y sus PDF con Chromium instalado."""

import argparse
import os
import shutil
import subprocess
from pathlib import Path

from generator.build_pack import build


PDF_STEMS = ("pack_sudokus", "pack_laberintos", "pack_sopas", "muestra_gratis")


def find_chromium():
    candidates = (
        os.environ.get("CHROMIUM_PATH"),
        r"C:\Users\crist\AppData\Local\hermes\tools\chromium-1208\chrome-win\chrome.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        shutil.which("chrome"),
        shutil.which("chromium"),
    )
    return next((Path(path) for path in candidates if path and Path(path).is_file()), None)


def print_pdfs(out, chromium=None):
    out = Path(out)
    browser = Path(chromium) if chromium else find_chromium()
    if not browser or not browser.is_file():
        raise RuntimeError("Chromium no disponible; consulte README.md para el comando de impresión")
    pdfs = []
    for stem in PDF_STEMS:
        source = (out / f"{stem}.html").resolve()
        target = (out / f"{stem}.pdf").resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        subprocess.run(
            [str(browser), "--headless", "--disable-gpu", "--no-sandbox",
             "--no-pdf-header-footer", "--print-to-pdf=" + str(target), source.as_uri()],
            check=True, capture_output=True, text=True, timeout=120,
        )
        if not target.is_file() or target.stat().st_size < 100 or not target.read_bytes().startswith(b"%PDF-"):
            raise RuntimeError(f"Chromium no produjo un PDF válido: {target}")
        pdfs.append(target)
    return pdfs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("products"))
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--n", type=int, default=6)
    args = parser.parse_args(argv)
    paths = build(args.out, args.seed, args.n)
    paths += print_pdfs(args.out)
    for path in paths:
        print(f"{path}: {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
