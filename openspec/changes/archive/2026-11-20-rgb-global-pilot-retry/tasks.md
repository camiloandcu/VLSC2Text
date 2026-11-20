## Tasks

- [x] 1. Registrar autorización y diagnóstico previo de solo lectura.
- [x] 2. Extensión mínima de reserva explícita/pruebas y QA focal (R1).
- [x] 3. Snapshot/reserva, único reintento completo, replay y liquidación (R2/R3).
- [x] 4. Evidencia/revisión final, documentos y sync/archive (R4).

## Evidence

El fallo original se conserva en07 §10 y el ítem archivado anterior. El nuevo alcance está autorizado por petición directa; no cambia modelo, fuentes, selección o contrato científico. Diagnóstico actual no identifica la causa del OOM.

Implementación: únicamente `rgb_budget.py`, CLI y dos escenarios nuevos en `tests/test_rgb.py` difieren del snapshot original. Encoder/decoder/transformaciones/supervisor/dependencias idénticos. Focal11/11 en11,34s; suite completa27/27 en80,86s. Revisión estática independiente sin hallazgos materiales; controles focales independientes pendientes. No se ejecutó CUDA/modelo durante la preparación del reintento.

Revisión independiente previa conforme:2 pruebas nuevas en2,05s y controles adicionales de recibo padre ausente, manifiesto cambiado y recibo padre alterado entre reserva/claim. Sin hallazgos materiales; no GPU/SSH/payloads reales. Productor congelado `e4a8979df15e62bde0c3776250c94c268d3d0585891e680cb3da67c50e01314f`, snapshot36archivos; pipeline idéntico al anterior. Despliegue de código para metadatos verificado; reserva adicional previa a la ejecución local.

Ejecución real: intento02COMPLETED121,448676942s, piloto/replayexit0. Error relativo batch1/batch4 ybatch1/referencia2,143078141×10⁻⁶; batch4/referencia0, límite10⁻⁴. Los30 embeddings entre intentos coinciden en valores (máximo relativo0), N/índices/videos/píxeles idénticos. Todos los hashes/arrays de caché/replay y fuente/snapshot conformes; no workers propios restantes. Evidencia privada en `artifacts/rgb-retry`, resumen autoritativo07 §11; ledger/rawdigests en06 §12. Revisión operativa independiente en curso.

Pase operativo independiente R2/R3:23 controles conformes sobre identidad, caché/arrays, procedencia, errores de replay recalculados, nueve históricos, scopes/globales y vínculo del padre, tiempos/límites/memoria/forward y cero workers remanentes. No ejecutó GPU/SSH/suites o originales. El pase no explica el fallo previo ni acredita estabilidad general/accuracy; R4 documental/lifecycle pendiente.

Revisión documental focal R4 conforme, sin bloqueos materiales; precisión de README aplicada para distinguir30 clips extraídos deun clip de replay. Costos/proyecciones/crossattempt recalculados, primerFAILED preservado y causa raíz desconocida. El siguiente paso de cierre sincroniza/archiva el requisito adicional; no autoriza otro intento ni clasificación/extracción completa.

Cierre efectivo,20 nov2026: requisito adicional sincronizado en `openspec/specs/rgb-global-pilot/spec.md`, cambio archivado como `2026-11-20-rgb-global-pilot-retry`. R1–R3 verificados y R4 procedimental completado tras revisiones/actualización de registros. Endpoint local completo; sin Git/PR/publicación, clasificación, test, gasto o envío. Autorización de reintento agotada.
