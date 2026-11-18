# Pasatiempos digitales · Fases 1 y 2

Generadores deterministas de Sudoku, laberintos perfectos y sopas de letras. Solo usan Python estándar. Las salidas JSON incluyen la solución o el camino para poder auditarlas.

## Crear productos

Desde la raíz del repositorio:

```powershell
C:\Python314\python.exe -m generator.build_pack --seed 2026 --n 6 --out products
```

Se crean `pack_sudokus.html` (A4), `pack_sudokus_carta.html` (Carta), `pack_laberintos.html`, `pack_sopas.html`, `muestra_gratis.html` y cuatro portadas PNG. Cada documento pone las soluciones al final. La muestra contiene dos sudokus y un laberinto.

Para crear además los cuatro PDF reales con Chromium instalado en el host:

```powershell
C:\Python314\python.exe .\build_pack.py --seed 2026 --n 6 --out products
```

Se crean `pack_sudokus.pdf`, `pack_laberintos.pdf`, `pack_sopas.pdf` y `muestra_gratis.pdf`. El script busca Chromium/Chrome localmente; puede definir `CHROMIUM_PATH` si está en otra ruta. No instala dependencias. Si no hay Chromium, mantenga los HTML y ejecute, por cada archivo, el comando exacto:

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless --disable-gpu --no-sandbox --no-pdf-header-footer --print-to-pdf="$(Resolve-Path .\products)\pack_sudokus.pdf" "$(Resolve-Path .\products\pack_sudokus.html)"
```

Repita con `pack_laberintos`, `pack_sopas` y `muestra_gratis`; sustituya la ruta del ejecutable por su instalación de Chromium. Si el navegador no está instalado, los HTML se pueden imprimir manualmente con **Ctrl+P → Guardar como PDF**.

## Tienda y entrega

La landing está en `shop/`. Para servirla localmente, defina una clave privada de al menos 32 caracteres y ejecute:

```powershell
$env:PD_HMAC_KEY = "UNA-CLAVE-ALEATORIA-PRIVADA-DE-32-CARACTERES-O-MAS"
C:\Python314\python.exe -m delivery.serve --host 127.0.0.1 --port 8000
```

Abra `http://127.0.0.1:8000/`. La muestra se descarga sin clave. Después de verificar un pago fuera del servidor, genere un enlace privado con `C:\Python314\python.exe -m delivery.serve --link pack_sudokus.pdf --ttl 3600`; cambie el nombre por cualquiera de los otros dos packs. El enlace caduca y solo se acepta con la misma `PD_HMAC_KEY`. Para el botón de compra, configure `PD_CHECKOUT_URL` con una URL HTTPS de pago real antes de arrancar el servidor. Sin esa URL, `/comprar` responde 503; no hay cobro simulado. No se guardan claves en el repositorio.

`deploy/README.md` explica cómo preparar y publicar una landing estática en Cloudflare Pages o GitHub Pages. El servidor Python y sus enlaces firmados requieren hospedaje separado con HTTPS; la publicación estática no ejecuta la entrega protegida.

Para regenerar los packs con una semilla aleatoria y registrar el resultado en `ops/log/regeneraciones.jsonl`:

```powershell
C:\Python314\python.exe .\ops\regenerar.py
```

## Generadores individuales

```powershell
C:\Python314\python.exe -m generator.sudoku --n 2 --seed 1 --difficulty facil --out products\datos_sudoku
C:\Python314\python.exe -m generator.maze --w 10 --h 10 --n 2 --seed 1 --out products\datos_laberinto
C:\Python314\python.exe -m generator.wordsearch --words palabras.txt --n 2 --seed 1 --out products\datos_sopa
```

`palabras.txt` contiene una palabra española por línea. Se aceptan tildes y Ñ; las tildes se quitan para la cuadrícula. Las palabras deben ser distintas, tener al menos tres letras y no ser palíndromos, porque estos tendrían dos ubicaciones dirigidas. Los solapamientos solo comparten letras iguales. La verificación rechaza cualquier aparición adicional, incluso accidental. Si no logra una colocación única tras 100 intentos, el generador falla explícitamente.

Sudoku cuenta soluciones hasta dos y exige exactamente una; `facil` tiene al menos 45 pistas y `medio` entre 32 y 44. El laberinto comprueba que todas las celdas estén conectadas y que tenga exactamente `W×H−1` aristas, lo que garantiza un único camino entre cualquier par de celdas.

## Pruebas

```powershell
C:\Python314\python.exe -m unittest discover -s tests -p "test_*.py"
C:\Python314\python.exe -m pytest -q --basetemp $env:TEMP\pd_tests
```
