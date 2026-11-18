# Publicación estática

`preparar.py` crea una carpeta para Cloudflare Pages o GitHub Pages que contiene únicamente la landing, el CSS y la muestra gratuita. **Nunca** suba `products/` completo: contiene los packs de pago. No se publica nada automáticamente.

1. Genere la muestra: `C:\Python314\python.exe build_pack.py --seed 2026 --n 6 --out products`.
2. Configure un checkout HTTPS real en su proveedor de pagos. El servidor de entrega debe recibir una confirmación de pago verificada por el operador o una integración autenticada antes de crear un enlace. Esta fase no implementa cobro ni webhook.
3. Prepare la carpeta: `C:\Python314\python.exe .\deploy\preparar.py --checkout-url "https://SU-CHECKOUT" --out "$env:TEMP\pasatiempos-pages"`.
4. En Cloudflare Pages, cree un proyecto de **carga directa** y cargue los tres archivos de esa carpeta. En GitHub Pages, publique esos tres archivos desde una rama/carpeta dedicada. Configure dominio y HTTPS en la plataforma elegida.
5. Hospede `delivery/serve.py` por separado detrás de HTTPS y configure `PD_HMAC_KEY` y `PD_CHECKOUT_URL` como variables de entorno del host. Pages solo sirve archivos estáticos: no ejecuta Python ni valida tokens.

La entrega no está automatizada hasta conectar una confirmación de pago confiable con el comando privado de enlaces. No configure una ruta pública que genere tokens.
