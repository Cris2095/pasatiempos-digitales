import http.client
import tempfile
import threading
import time
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

from delivery.serve import handler_factory, make_token, verify_token


KEY = "clave-de-prueba-de-al-menos-32-caracteres"


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        (root / "shop").mkdir()
        (root / "products").mkdir()
        (root / "shop" / "index.html").write_text("Tienda", encoding="utf-8")
        (root / "shop" / "style.css").write_text("body{}", encoding="utf-8")
        (root / "products" / "muestra_gratis.pdf").write_bytes(b"%PDF-sample")
        (root / "products" / "pack_sudokus.pdf").write_bytes(b"%PDF-paid")
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler_factory(KEY, root))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def get(self, path):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port)
        connection.request("GET", path)
        response = connection.getresponse()
        result = response.status, response.read(), dict(response.getheaders())
        connection.close()
        return result

    def test_landing_and_sample(self):
        self.assertEqual(self.get("/")[:2], (200, b"Tienda"))
        self.assertEqual(self.get("/muestra_gratis.pdf")[:2], (200, b"%PDF-sample"))
        self.assertEqual(self.get("/pack_sudokus.pdf")[0], 404)

    def test_valid_link(self):
        token = make_token("pack_sudokus.pdf", KEY, time.time() + 60)
        self.assertEqual(verify_token(token, KEY), "pack_sudokus.pdf")
        self.assertEqual(self.get("/download/" + token)[:2], (200, b"%PDF-paid"))

    def test_expired_link_rejected(self):
        token = make_token("pack_sudokus.pdf", KEY, time.time() - 1)
        self.assertIsNone(verify_token(token, KEY))
        self.assertEqual(self.get("/download/" + token)[0], 403)

    def test_altered_link_rejected(self):
        token = make_token("pack_sudokus.pdf", KEY, time.time() + 60)
        payload, signature = token.split(".")
        changed = ("A" if payload[0] != "A" else "B") + payload[1:] + "." + signature
        self.assertIsNone(verify_token(changed, KEY))
        self.assertEqual(self.get("/download/" + changed)[0], 403)


if __name__ == "__main__":
    unittest.main()
