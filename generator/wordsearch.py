"""Seeded Spanish word searches with checked, unique word locations."""

import argparse
import json
import math
import random
import unicodedata
from pathlib import Path


DEFAULT_WORDS = ("LUNA", "SOL", "MAR", "RIO", "NUBE", "FLOR", "BOSQUE", "ARBOL", "PLAYA", "ESTRELLA")
DIRECTIONS = ((1, 0), (0, 1), (1, 1), (-1, 1), (-1, 0), (0, -1), (-1, -1), (1, -1))
ALPHABET = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"


def normalize(word):
    letters = []
    for char in word.strip().upper():
        if char == "Ñ":
            letters.append(char)
        else:
            letters.extend(part for part in unicodedata.normalize("NFD", char)
                           if unicodedata.category(part) != "Mn")
    return "".join(letters)


def prepare_words(words):
    result = [normalize(word) for word in words if word.strip()]
    if not result or len(result) != len(set(result)):
        raise ValueError("words must be nonempty and distinct")
    if any(len(word) < 3 or any(char not in ALPHABET for char in word) for word in result):
        raise ValueError("words must have at least 3 Spanish letters")
    if any(word == word[::-1] for word in result):
        raise ValueError("palindromes cannot have a unique directed location")
    return result


def occurrences(grid, word):
    size = len(grid)
    found = []
    for y in range(size):
        for x in range(size):
            for dx, dy in DIRECTIONS:
                cells = [(x + i * dx, y + i * dy) for i in range(len(word))]
                if all(0 <= cx < size and 0 <= cy < size and grid[cy][cx] == letter
                       for (cx, cy), letter in zip(cells, word)):
                    found.append([[cx, cy] for cx, cy in cells])
    return found


def verify(grid, placements):
    size = len(grid)
    if not grid or any(len(row) != size or any(char not in ALPHABET for char in row) for row in grid):
        raise ValueError("invalid square word search")
    for word, cells in placements.items():
        if len(occurrences(grid, word)) != 1 or occurrences(grid, word)[0] != cells:
            raise ValueError(f"word {word} is absent, ambiguous, or misplaced")
    return True


def generate(words, seed):
    words = prepare_words(words)
    rng = random.Random(seed)
    size = max(10, max(map(len, words)) + 2, math.ceil(math.sqrt(sum(map(len, words)) * 2.5)))
    for _ in range(100):
        grid = [[None] * size for _ in range(size)]
        placements = {}
        for word in sorted(words, key=lambda value: -len(value)):
            candidates = []
            for y in range(size):
                for x in range(size):
                    for dx, dy in DIRECTIONS:
                        cells = [(x + i * dx, y + i * dy) for i in range(len(word))]
                        if all(0 <= cx < size and 0 <= cy < size and grid[cy][cx] in (None, letter)
                               for (cx, cy), letter in zip(cells, word)):
                            candidates.append(cells)
            if not candidates:
                break
            cells = rng.choice(candidates)
            for (x, y), letter in zip(cells, word):
                grid[y][x] = letter
            placements[word] = [[x, y] for x, y in cells]
        if len(placements) != len(words):
            continue
        for y in range(size):
            for x in range(size):
                if grid[y][x] is None:
                    grid[y][x] = rng.choice(ALPHABET)
        try:
            verify(grid, placements)
        except ValueError:
            continue
        return {"seed": seed, "words": words, "grid": grid, "placements": placements}
    raise RuntimeError("could not place every word uniquely in 100 attempts")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--words", type=Path, required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.n < 1:
        parser.error("--n must be positive")
    words = prepare_words(line for line in args.words.read_text(encoding="utf-8").splitlines()
                          if line.strip() and not line.lstrip().startswith("#"))
    args.out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    for index in range(1, args.n + 1):
        item = generate(words, rng.getrandbits(64))
        (args.out / f"wordsearch_{index:03}.json").write_text(
            json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
