import tempfile
import unittest
from pathlib import Path

from generator import wordsearch


class WordSearchTests(unittest.TestCase):
    def test_words_appear_only_at_recorded_positions(self):
        item = wordsearch.generate(wordsearch.DEFAULT_WORDS, 456)
        self.assertEqual(item, wordsearch.generate(wordsearch.DEFAULT_WORDS, 456))
        self.assertTrue(wordsearch.verify(item["grid"], item["placements"]))
        for word, cells in item["placements"].items():
            self.assertEqual(wordsearch.occurrences(item["grid"], word), [cells])

    def test_rejects_false_placement(self):
        item = wordsearch.generate(("LUNA", "NUBE"), 12)
        wrong = dict(item["placements"])
        wrong["LUNA"] = [[0, 0]] * 4
        with self.assertRaises(ValueError):
            wordsearch.verify(item["grid"], wrong)

    def test_normalizes_spanish_and_rejects_duplicates(self):
        self.assertEqual(wordsearch.prepare_words(["árbol", "NIÑO"]), ["ARBOL", "NIÑO"])
        with self.assertRaises(ValueError):
            wordsearch.prepare_words(["sol", "SOL"])

    def test_cli_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "words.txt").write_text("árbol\nNIÑO\n", encoding="utf-8")
            wordsearch.main(["--words", str(path / "words.txt"), "--n", "2", "--seed", "5",
                             "--out", str(path / "output")])
            self.assertEqual(len(list((path / "output").glob("wordsearch_*.json"))), 2)


if __name__ == "__main__":
    unittest.main()
