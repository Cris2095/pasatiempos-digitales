"""Prepara solo la landing y la muestra para Pages, sin publicar nada."""

import argparse
import html
import shutil
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]


def prepare(checkout_url, out):
    parsed = urlsplit(checkout_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("La URL de compra debe usar HTTPS")
    out = Path(out)
    sample = ROOT / "products" / "muestra_gratis.pdf"
    if not sample.is_file():
        raise FileNotFoundError("Genere products/muestra_gratis.pdf primero")
    if out.exists() and any(out.iterdir()):
        raise ValueError("La carpeta de salida debe estar vacía para evitar publicar otros archivos")
    out.mkdir(parents=True, exist_ok=True)
    page = (ROOT / "shop" / "index.html").read_text(encoding="utf-8")
    page = page.replace('href="/comprar"', f'href="{html.escape(checkout_url, quote=True)}"')
    page = page.replace('href="/style.css"', 'href="./style.css"')
    page = page.replace('href="/muestra_gratis.pdf"', 'href="./muestra_gratis.pdf"')
    page = page.replace('href="/"', 'href="./"')
    (out / "index.html").write_text(page, encoding="utf-8")
    shutil.copy2(ROOT / "shop" / "style.css", out / "style.css")
    shutil.copy2(sample, out / "muestra_gratis.pdf")
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout-url", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(f"Sitio estático preparado en {prepare(args.checkout_url, args.out)}")


if __name__ == "__main__":
    main()
