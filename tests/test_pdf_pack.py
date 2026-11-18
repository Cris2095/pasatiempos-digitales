import tempfile
import unittest
from pathlib import Path

from build_pack import PDF_STEMS, find_chromium, print_pdfs
from generator.build_pack import build


class PdfPackTests(unittest.TestCase):
    @unittest.skipUnless(find_chromium(), "Chromium no disponible")
    def test_real_pdfs(self):
        with tempfile.TemporaryDirectory() as directory:
            build(directory, seed=9, count=2)
            paths = print_pdfs(directory)
            self.assertEqual({path.name for path in paths}, {stem + ".pdf" for stem in PDF_STEMS})
            for path in paths:
                self.assertGreater(path.stat().st_size, 100)
                self.assertTrue(path.read_bytes().startswith(b"%PDF-"))
