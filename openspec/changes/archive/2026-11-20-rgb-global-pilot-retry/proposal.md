## Why

El único piloto anterior completó extracción30, pero falló el replay al inicializar CUDA. El usuario pidió expresamente «¿Podrías volver a intentarlo?»,20 nov2026: autoriza un reintento acotado sin retirar el fallo histórico.

## What Changes

- Permitir una sola reserva adicional explícita `--retry-of` ligada al piloto original fallido y liquidado.
- Repetir el piloto completo30/K16 y replay con idénticos modelo, transformaciones, decoder, entorno y límites600s+60s; salida/snapshot nuevos.
- Registrar y revisar resultado, incluido un nuevo fallo, sin reintentos sucesivos ni extracción1125/E08/test/gasto.

## Capabilities

### Modified Capabilities

- `rgb-global-pilot`: reintento único solicitado explícitamente tras fallo terminal.

## Impact

Extensión acotada de `rgb_budget`/CLI y pruebas de denegación; el pipeline RGB no cambia. Nuevo productor porque la huella incluye todo el paquete; snapshots/cachés originales se conservan. Ledger único remoto, alcance `rgb-global-pilot-retry`660s, preservando453,506856442s y reserva final43200s. Endpoint local sin Git/PR/publicación.

## Acceptance

| AC | Evidencia |
|---|---|
| R1 | Reserva explícita de un original fallido/liquidado, ligada a su recibo; negar original completado, claim doble, reintento encadenado y otro intento adicional. Historial/caja/reserva final conservados. |
| R2 | Pipeline y entorno idénticos al snapshot original salvo presupuesto/CLI;30 IDs/K16, activos y fuente fijados. Nueva ejecución instrumentada con los límites originales. |
| R3 | Resultado del nuevo replay identificado como conforme/fallido según tolerancia original, sin ocultar el fallo previo. Contabilidad exacta una vez y cero workers propios restantes. |
| R4 | Revisión independiente focal, registros reconciliados y sync/archive; no abrir otra ejecución por inferencia. |

## Authorization

Solicitud directa del usuario arriba citada. Cubre el reintento y los ajustes mínimos necesarios para registrarlo y verificarlo; no pagos, proveedores, test, cabezas o nuevas variantes. No se pide nuevamente aprobación para este alcance.
