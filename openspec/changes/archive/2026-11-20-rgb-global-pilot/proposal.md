## Why

R2-E02O no mejoró R2-E01. RGB global congelado E07/E08 es la siguiente modalidad prevista y no depende del esquema anatómico. La GPU local existe, pero el entorno actual es CPU; falta acreditar ejecución, memoria y costo del encoder sin gastar ni transferir datos.

## What Changes

- Preparar entorno CUDA separado y extracción R4 global reproducible para30 clips train preseleccionados.
- Medir costo completo, memoria, integridad y replay; proponer admisión o cierre, sin interpretar un piloto como candidatura competitiva.
- Conservar una sola contabilidad y todos los snapshots anteriores.

## Capabilities

### New Capabilities

- `rgb-global-pilot`: factibilidad local de embeddings fijos con caché de alcance explícito.

### Modified Capabilities

Ninguna receta previa. No habilita caché completo o entrenamiento E08.

## Impact

Contratos en [04 §14](../../../../docs/04_solution_and_experiment_design.md), [05 §14](../../../../docs/05_technical_architecture.md), [06 §11](../../../../docs/06_delivery_and_iteration_plan.md). Paquete/CLI RGB y lock de entorno aislado; extensión local del ledger, pruebas y evidencia. Dos horas de implementación antes de reevaluar, instalación≤60min y un piloto≤600s/reserva660s. Sin factura, servicios/cuentas nuevos, ROI, entrenamiento/selección por accuracy, extracción1125, refit, test, envíos o publicación. No cambia48 ajustes: este ítem no contiene ajustes completos.

## Criterios de aceptación

| AC | Resultado verificable |
|---|---|
| G1 | Los30 IDs train fijados antes del modelo, hashes y selección por persona/clase son exactos. N real determina16 índices, y decoder/letterbox/color/normalización cumplen05; ningún fallo se convierte en embedding cero. |
| G2 | Entorno CUDA aislado, fuente/commit y peso SHA/licencia verificables; backbone estándar congelado/eval, CLS384 float32 sin adaptación ni estadísticas aprendidas. El entorno CPU/snapshots previos permanecen íntegros. |
| G3 | Cobertura piloto30, archivos/metadatos íntegros y publicación atómica; un consumidor de1125 rechaza este caché. Replay en proceso nuevo desde video/peso con batches1/4 conserva píxeles y embeddings dentro de tolerancia relativaL2≤1e-4, finitos. |
| G4 | Un intento con reserva local previa y liquidación medida conserva ledger/historial/caja/reserva final; se verifican recursos/corte y límites. Métricas separan costo completo y forward, RAM/VRAM/bytes, warm-up5 y≥10 batches medidos. Proyección usa margen1,5 y declara costos pendientes. |
| G5 | Se decide proponer extracción/cabeza o detener/escalar según evidencia, sin accuracy/test ni apertura automática de otra rama. Pruebas y revisión independientes, documentos reconciliados, sync/archive y endpoint local verificables. |

## Estado y puertas

Investigación de preparación autorizada por «Continúa con el siguiente incremento»,20 nov2026. Propuesta revisada conforme y aprobada por el usuario mediante «Apruebo»,20 nov2026; implementación autorizada bajo G1–G5. Implementación y único intento ejecutados: extracción30 completa, replay fallido con OOM de inicialización CUDA; G3 no satisfecho y admisión detenida. Evidencia en07 §10 y tareas; no hay reintento ni aceptación de reproducibilidad. No hay Git/PR/publicación. Revisión de fundación antes de aprobación; QA independiente de implementación/operación antes del cierre. Si falla una puerta, registrar evidencia y detener sin cambiar el protocolo.
