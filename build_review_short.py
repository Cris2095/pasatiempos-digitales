"""Shorter review prompt: sudoku only, bounded output."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
sudoku = (ROOT / "generator" / "sudoku.py").read_text(encoding="utf-8")
BRIEF = """Revisa este generador de sudokus. Busca SOLO defectos reales: solucion unica no garantizada, conteo de soluciones con limite mal puesto, dificultad que no se corresponde con las pistas, no determinismo por semilla.

Lista numerada: archivo, funcion, defecto. Si no hay defectos, escribe SIN HALLAZGOS. Menos de 250 palabras.

=== generator/sudoku.py ===
""" + sudoku
(ROOT / "prompt_review_short.txt").write_text(BRIEF, encoding="utf-8")
print("bytes:", (ROOT / "prompt_review_short.txt").stat().st_size)
