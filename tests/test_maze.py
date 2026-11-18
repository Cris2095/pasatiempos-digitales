import tempfile
import unittest
from pathlib import Path

from generator import maze


class MazeTests(unittest.TestCase):
    def test_perfect_path_and_determinism(self):
        item = maze.generate(8, 6, 123)
        self.assertEqual(item, maze.generate(8, 6, 123))
        self.assertEqual(item["path"], maze.verify(item["grid"]))
        self.assertEqual(item["path"][0], [0, 0])
        self.assertEqual(item["path"][-1], [7, 5])
        self.assertTrue(all(tuple(b) in maze.neighbors(item["grid"], tuple(a))
                            for a, b in zip(item["path"], item["path"][1:])))

    def test_cycle_is_rejected(self):
        item = maze.generate(4, 4, 8)
        grid = [row[:] for row in item["grid"]]
        for y in range(4):
            for x in range(4):
                if x < 3 and grid[2 * y + 1][2 * x + 2] == 1:
                    grid[2 * y + 1][2 * x + 2] = 0
                    with self.assertRaises(ValueError):
                        maze.verify(grid)
                    return
        self.fail("no closed wall found")

    def test_single_cell(self):
        self.assertEqual(maze.generate(1, 1, 1)["path"], [[0, 0]])

    def test_cli_output(self):
        with tempfile.TemporaryDirectory() as directory:
            maze.main(["--w", "3", "--h", "4", "--n", "2", "--seed", "5", "--out", directory])
            self.assertEqual(len(list(Path(directory).glob("maze_*.json"))), 2)


if __name__ == "__main__":
    unittest.main()
