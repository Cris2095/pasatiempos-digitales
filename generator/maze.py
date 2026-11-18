"""Perfect rectangular maze generation and verification."""

import argparse
from collections import deque
import json
import random
from pathlib import Path


def neighbors(grid, cell):
    h, w = (len(grid) - 1) // 2, (len(grid[0]) - 1) // 2
    x, y = cell
    for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and grid[2 * y + 1 + dy][2 * x + 1 + dx] == 0:
            yield nx, ny


def verify(grid):
    """Return the entrance-to-exit path, or raise if the maze is not perfect."""
    if not grid or len(grid) % 2 != 1 or len(grid[0]) % 2 != 1:
        raise ValueError("invalid maze dimensions")
    h, w = (len(grid) - 1) // 2, (len(grid[0]) - 1) // 2
    if h < 1 or w < 1 or any(len(row) != 2 * w + 1 for row in grid):
        raise ValueError("invalid maze dimensions")
    if any(value not in (0, 1) for row in grid for value in row):
        raise ValueError("maze must contain only zeros and ones")
    if any(grid[2 * y + 1][2 * x + 1] != 0 for y in range(h) for x in range(w)):
        raise ValueError("blocked cell")
    queue = deque([(0, 0)])
    parent = {(0, 0): None}
    edge_count = 0
    while queue:
        cell = queue.popleft()
        adjacent = list(neighbors(grid, cell))
        edge_count += len(adjacent)
        for other in adjacent:
            if other not in parent:
                parent[other] = cell
                queue.append(other)
    if len(parent) != w * h or edge_count // 2 != w * h - 1:
        raise ValueError("maze is disconnected or contains a cycle")
    path = []
    cell = (w - 1, h - 1)
    while cell is not None:
        path.append(list(cell))
        cell = parent[cell]
    return list(reversed(path))


def generate(width, height, seed):
    if width < 1 or height < 1:
        raise ValueError("maze width and height must be positive")
    rng = random.Random(seed)
    grid = [[1] * (2 * width + 1) for _ in range(2 * height + 1)]
    for y in range(height):
        for x in range(width):
            grid[2 * y + 1][2 * x + 1] = 0
    seen = {(0, 0)}
    stack = [(0, 0)]
    while stack:
        x, y = stack[-1]
        options = [(nx, ny) for nx, ny in ((x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1))
                   if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen]
        if not options:
            stack.pop()
            continue
        nx, ny = rng.choice(options)
        grid[y + ny + 1][x + nx + 1] = 0
        seen.add((nx, ny))
        stack.append((nx, ny))
    return {"width": width, "height": height, "seed": seed, "grid": grid, "path": verify(grid)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--w", type=int, required=True)
    parser.add_argument("--h", type=int, required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.n < 1:
        parser.error("--n must be positive")
    args.out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    for index in range(1, args.n + 1):
        item = generate(args.w, args.h, rng.getrandbits(64))
        (args.out / f"maze_{index:03}.json").write_text(
            json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
