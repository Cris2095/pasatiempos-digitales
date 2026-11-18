"""Landing pública y entrega de PDF mediante enlaces HMAC temporales."""

import argparse
import base64
import hashlib
import hmac
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PACKS = frozenset(("pack_sudokus.pdf", "pack_laberintos.pdf", "pack_sopas.pdf"))


def _encoded(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _decoded(data):
    return base64.b64decode(data + "=" * (-len(data) % 4), altchars=b"-_", validate=True)


def make_token(filename, key, expires):
    if filename not in PACKS:
        raise ValueError("Producto desconocido")
    payload = _encoded(json.dumps({"file": filename, "exp": int(expires)}, separators=(",", ":")).encode())
    signature = _encoded(hmac.new(key.encode(), payload.encode(), hashlib.sha256).digest())
    return payload + "." + signature


def verify_token(token, key, now=None):
    try:
        payload, signature = token.split(".")
        expected = hmac.new(key.encode(), payload.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(_decoded(signature), expected):
            return None
        claims = json.loads(_decoded(payload))
        current = time.time() if now is None else now
        if claims["file"] not in PACKS or type(claims["exp"]) is not int or current >= claims["exp"]:
            return None
        return claims["file"]
    except (ValueError, KeyError, TypeError, UnicodeError, OverflowError):
        return None


def handler_factory(key, root=ROOT, checkout_url=None):
    root = Path(root)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = unquote(urlsplit(self.path).path)
            if path in ("/", "/index.html"):
                self.send_file(root / "shop" / "index.html", "text/html; charset=utf-8")
            elif path == "/style.css":
                self.send_file(root / "shop" / "style.css", "text/css; charset=utf-8")
            elif path == "/muestra_gratis.pdf":
                self.send_file(root / "products" / "muestra_gratis.pdf", "application/pdf")
            elif path == "/comprar":
                if checkout_url:
                    self.send_response(302)
                    self.send_header("Location", checkout_url)
                    self.end_headers()
                else:
                    self.send_error(503, "Compra pendiente de configurar")
            elif path.startswith("/download/"):
                filename = verify_token(path[len("/download/"):], key)
                if filename is None:
                    self.send_error(403, "Enlace inválido o caducado")
                else:
                    self.send_file(root / "products" / filename, "application/pdf", attachment=True)
            else:
                self.send_error(404)

        def send_file(self, file, content_type, attachment=False):
            try:
                data = file.read_bytes()
            except FileNotFoundError:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store" if attachment else "public, max-age=300")
            if attachment:
                self.send_header("Content-Disposition", f'attachment; filename="{file.name}"')
            self.end_headers()
            self.wfile.write(data)

    return Handler


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--link", choices=sorted(PACKS), help="Crear enlace tras confirmar el pago")
    parser.add_argument("--ttl", type=int, default=3600, help="Validez del enlace en segundos")
    args = parser.parse_args(argv)
    key = os.environ.get("PD_HMAC_KEY")
    if not key or len(key) < 32:
        parser.error("PD_HMAC_KEY debe contener al menos 32 caracteres")
    if args.link:
        if args.ttl <= 0:
            parser.error("--ttl debe ser positivo")
        token = make_token(args.link, key, time.time() + args.ttl)
        print(f"/download/{token}")
        return
    checkout_url = os.environ.get("PD_CHECKOUT_URL")
    server = ThreadingHTTPServer((args.host, args.port), handler_factory(key, checkout_url=checkout_url))
    print(f"Tienda: http://{args.host}:{args.port}/")
    server.serve_forever()


if __name__ == "__main__":
    main()
