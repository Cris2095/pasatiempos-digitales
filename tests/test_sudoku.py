import tempfile
import unittest
from pathlib import Path

from generator import sudoku


class SudokuTests(unittest.TestCase):
    def test_unique_valid_and_clue_ranges(self):
        for difficulty in ("facil", "medio"):
            with self.subTest(difficulty=difficulty):
                item = sudoku.generate(12345, difficulty)
                clues = sum(value != 0 for row in item["puzzle"] for value in row)
                self.assertTrue(sudoku.valid_solution(item["solution"]))
                self.assertEqual(sudoku.count_solutions(item["puzzle"]), 1)
                self.assertTrue(all(given in (0, answer) for row, solved in
                                    zip(item["puzzle"], item["solution"])
                                    for given, answer in zip(row, solved)))
                self.assertGreaterEqual(clues, 45 if difficulty == "facil" else 32)
                if difficulty == "medio":
                    self.assertLessEqual(clues, 44)

    def test_deterministic_and_rejects_conflicts(self):
        self.assertEqual(sudoku.generate(77, "facil"), sudoku.generate(77, "facil"))
        bad = [[0] * 9 for _ in range(9)]
        bad[0][0] = bad[0][1] = 1
        self.assertEqual(sudoku.count_solutions(bad), 0)

    def test_cli_output(self):
        with tempfile.TemporaryDirectory() as directory:
            sudoku.main(["--n", "2", "--seed", "2", "--difficulty", "facil", "--out", directory])
            self.assertEqual(len(list(Path(directory).glob("sudoku_*.json"))), 2)


if __name__ == "__main__":
    unittest.main()
