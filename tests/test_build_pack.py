import tempfile
import unittest
from pathlib import Path

from generator import build_pack


class BuildPackTests(unittest.TestCase):
    def test_printable_packs_and_covers(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = build_pack.build(directory, seed=9, count=2)
            self.assertEqual(len(paths), 9)
            self.assertTrue(all(path.exists() and path.stat().st_size > 100 for path in paths))
            sample = (Path(directory) / "muestra_gratis.html").read_text(encoding="utf-8")
            self.assertEqual(sample.count('<table class="sudoku">'), 4)
            self.assertEqual(sample.count('<table class="maze">'), 2)
            self.assertIn("Soluciones", sample)
            self.assertIn("size: letter", (Path(directory) / "pack_sudokus_carta.html").read_text(encoding="utf-8"))
            self.assertTrue((Path(directory) / "portada_sudokus.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            first = {path.name: path.read_bytes() for path in paths}
            build_pack.build(directory, seed=9, count=2)
            self.assertEqual(first, {path.name: path.read_bytes() for path in paths})


if __name__ == "__main__":
    unittest.main()
