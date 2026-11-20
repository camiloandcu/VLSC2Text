## Context

Evidencia/recetas/autoridad en00 y04–06; no repetir descubrimiento. Flujo: manifest train→30 IDs fijados→hash/conteo/decoder→letterbox16frames→backbone fijo→caché pilot30→replay y reporte de admisión. No hay UI o consumidor de clasificación en este alcance.

## Decisions

Priorizar GTX1650 local, entornoCUDA separado y peso/fuente fijados; Colab implica cuenta/transferencia y pago implica puertas adicionales. Exactitud de transformaciones en05 §14. Cargar el peso con weights_only y strict; streaming de frames para no retener videosHD completos. Caché de piloto separado por identidad/cobertura; no reutilizarlo como completo sin futura verificación/promoción del productor.

Ledger único: añadir clase de ejecución local explícita, reserva660 antes de lanzar, deadline600+60, un intento, receipt de liquidación independiente de Slurm. Cobrar conservadoramente ese tiempo al límite global existente y registrar usoGPU aparte sin sumarlo de nuevo. No falsificar job IDs, no correr entrenamiento en login, no crear un segundo ledger activo. Pruebas cubren aceptación/denegación y preservación histórica.

## Risks / Trade-offs

Disponibilidad instantánea de VRAM/RAM no garantiza recursos futuros. Driver compatible no prueba ejecuciónCUDA. Hub/source mutable, decode con rotación/FPS o relleno distinto rompen identidad. El piloto no estima costo de cabezas y no puede admitir toda la cadena por sí solo. OOM/red/tiempo fallidos no autorizan cambiar precisión o K automáticamente.

## Verification

G1–G5: tests sintéticos, peso/entorno reales, métricas30clips, replay independiente y crítica/QA con alcance limitado. Sin promesa de mejora o de cuota. Responsable de autoría e integración: primario; revisiones de solo lectura. Implementación aprobada y ejecutada. Resultado negativo por fallo de replay; se aplica el escenario de detención, sin modificar protocolo o declarar éxito de G3.
