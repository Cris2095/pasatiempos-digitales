# SPEC — Generadores y productos (Fase 1)

Objetivo: generar productos digitales verificables de pasatiempos imprimibles, con coste cero y sin dependencias externas.

## 1. `generator/sudoku.py`
- Genera sudokus de 9x9 con **solución única garantizada** (backtracking + conteo de soluciones con límite 2).
- Parámetro `--n N --seed S --difficulty {facil,medio}` y `--out DIR`.
- Dificultad por número de pistas: facil >= 45, medio 32-44 (verificable).
- Salida por puzzle: JSON con `puzzle`, `solution`, `difficulty`, `seed`.
- Tests: `tests/test_sudoku.py` que verifiquen que la solución es válida, que el puzzle tiene solución única y que las pistas respetan el rango.

## 2. `generator/maze.py`
- Genera laberintos perfectos (uno y solo un camino) con DFS/Kruskal.
- Parámetros `--w W --h H --n N --seed S --out DIR`.
- Verificación: BFS de (0,0) a (W-1,H-1) debe existir camino; y exactamente un camino (laberinto perfecto).
- Salida por laberinto: JSON con la cuadrícula y el camino.
- Tests: `tests/test_maze.py`.

## 3. `generator/wordsearch.py`
- Sopa de letras con lista de palabras controlada (español), sin solapamiento inválido.
- Parámetros `--words FILE --n N --seed S --out DIR`.
- Verificación: cada palabra aparece exactamente donde se colocó.
- Tests: `tests/test_wordsearch.py`.

## 4. `generator/build_pack.py`
- Empaqueta los tres productos en:
  - `products/pack_sudokus.pdf` (A4 y Carta)
  - `products/pack_laberintos.pdf`
  - `products/pack_sopas.pdf`
  - `products/muestra_gratis.pdf` (2 sudokus + 1 laberinto + soluciones)
  - `products/*.png` (portadas)
- Usa solo Python estándar +, si hace falta, `reportlab` (si está disponible) o HTML+weasyprint; si ninguna está disponible, genera HTML imprimible y documenta el comando de impresión.
- Soluciones en sección separada al final.
- Tests: `tests/test_build_pack.py` que verifiquen que los PDF existen y no están vacíos.

## Reglas
- Solo Python estándar + dependencias ya instaladas. Si falta una dependencia, **no la instales**: usa una alternativa o genera HTML imprimible.
- No modifiques archivos de otros equipos ni outside de este repo.
- Cada generador debe ser determinista con la semilla.
- Documenta el uso en `README.md`.

## Aceptación
- `python -m unittest discover -s tests -p "test_*.py"` en verde.
- Los tres packs y la muestra existen en `products/`.
