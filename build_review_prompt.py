"""Build a bounded cross-review prompt for FCC (no file access on the model side)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
sudoku = (ROOT / "generator" / "sudoku.py").read_text(encoding="utf-8")
maze = (ROOT / "generator" / "maze.py").read_text(encoding="utf-8")

BRIEF = """Eres FCC, revisor independiente. Revisa el codigo de dos generadores de un negocio de pasatiempos imprimibles. No tienes acceso a archivos; el codigo va abajo.

Busca SOLO defectos reales y concretos que rompan la correccion del producto:
1. Sudoku: garantiza de verdad solucion unica? el conteo de soluciones tiene fuga o limite mal puesto? la dificultad declarada se corresponde con las pistas reales?
2. Laberinto: es realmente perfecto (un solo camino)? la verificacion BFS prueba lo que dice probar?
3. Cualquier no determinismo por semilla, semilla no usada, o estado global que rompa la reproducibilidad.
4. Cualquier afirmacion del codigo o documentacion que el propio codigo no respalde.

Salida: lista numerada de hallazgos, cada uno con archivo, funcion y por que es un defecto real. Si algo esta bien, no lo menciones. Si no encuentras defectos en una seccion, escribe SIN HALLAZGOS. Menos de 400 palabras.

=== generator/sudoku.py ===
""" + sudoku + "\n\n=== generator/maze.py ===\n" + maze

(ROOT / "prompt_review.txt").write_text(BRIEF, encoding="utf-8")
print("bytes:", (ROOT / "prompt_review.txt").stat().st_size)
