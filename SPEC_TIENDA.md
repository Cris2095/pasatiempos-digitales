# SPEC — Tienda, entrega y despliegue (Fase 2)

Objetivo: vender el pack de pasatiempos con entrega automatica, sin servicios no-code de pago.

## 1. shop/ (landing)
- `index.html` + CSS propio en espanol: portada, que incluye, muestra gratuita descargable, precio y boton de compra.
- Enlace de descarga de la muestra al PDF en `products/muestra_gratis.pdf`.
- Sin frameworks de pago.

## 2. delivery/serve.py
- Servidor local con stdlib que:
  - sirve la landing y la muestra.
  - genera enlaces de descarga firmados con caducidad (hmac + timestamp) para entregar el pack solo tras pago.
  - endpoint `/download/<token>` que verifica firma y caducidad y sirve el PDF.
- La clave HMAC se lee de variable de entorno; nunca en el repo.
- Tests en `tests/test_delivery.py`: enlace valido, caducado rechazado, alterado rechazado.

## 3. deploy/
- Configuracion y script para publicar en Cloudflare Pages (free) o GitHub Pages.
- Si no hay credenciales, documentar el paso exacto y dejar el script listo.

## 4. ops/regenerar.py
- Regenera los packs con semilla nueva y deja bitacora en `ops/log/`. Pensado para cron semanal.

## Reglas
- Sin servicios de pago ni dependencias nuevas. Solo Python estandar + lo ya instalado.
- Nunca secrets en el repo.
- Textos en espanol y sin promesas de ingresos.

## Aceptacion
- Tests en verde.
- `shop/` sirve la landing y la muestra.
- Los enlaces firmados funcionan y rechazan manipulaciones.
