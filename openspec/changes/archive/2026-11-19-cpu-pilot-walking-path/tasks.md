## 1. Preparación

- [x] 1.1 Revisar propuesta y alcance de fundación del primer bloque; registrar autorización real en00.
- [x] 1.2 Fijar entorno Python3.10/dependenciasCPU y exclusiones privadas.

## 2. Implementación

- [x] 2.1 Implementar manifest train, comprobación estructural y splits seguros (P1–P3).
- [x] 2.2 Implementar R0, MLP/muestreo/piloto, artefactos y restauración (P4–P5).
- [x] 2.3 Implementar presupuesto acumulado y lanzador Slurm (P6–P7).

## 3. Verificación y entrega

- [x] 3.1 Ejecutar pruebas focales y piloto real, recuperar evidencia (P1–P7).
- [x] 3.2 Obtener revisión independiente de implementación; resolver hallazgos (P8).
- [x] 3.3 Reconciliar documentos, registrar evidencia por AC y validar cambio y preparar sincronización; archivar después del cierre verificado (P8).

## Evidencia por criterio · 19 de noviembre de 2026

Artefactos privados en `artifacts/cpu-pilot/`, excluidos de publicación. El subdirectorio `remote/` es una copia de evidencia recuperada, no un segundo ledger activo. El registro económico canónico permanece en `~/resultados/lsc5/budget.json` de Cronos. La carpeta remota de código es inmutable para esta ejecución; su nombre y huella están en `deployment.json`. `source_snapshot.tar.gz` y su manifiesto conservan localmente la versión exacta de código/dependencias para restauración posterior, aunque cambie el árbol de trabajo.

| AC | Resultado y evidencia efectiva |
|---|---|
| P1 | Conforme. Auditoría real de 1.125 pares train con hashes por modalidad; fixtures rechazan escape por ruta/symlink y test. `train_manifest.json`; código/10 pruebas. Metadata de archivo queda fuera de los3324 valores predictivos. |
| P2 | Conforme al alcance estructural:63.284 frames float64 de 1662 columnas, finitos. `schema_status=opaque_only_anatomy_unverified`; R1/ROI no habilitados. Anatomía no certificada. |
| P3 | Conforme. Tres splits deterministas; piloto M02 con 750 fit/375 val. IDs de scaler coinciden exclusivamente con fit. Duplicado entre personas rechazado en fixture. `splits/` y `remote/runs/r2-e00-r0-m02-s17-20261119-01/split.json`. |
| P4 | Conforme. Dos épocas/semilla 17,38 pasos y33 tras calentamiento, batch 40 con remanente30; prueba backward/step60 en copia descartada fit-only. Modelo426.245 parámetros. Proyección80 épocas4,2122 s con margen 1,5, incluyendo I/O/evaluación/escritura, sin cola ni arranque frío; estimación exclusiva de R0/MLP. `metrics.json`. |
| P5 | Conforme. Otro proceso local reconstruyó R0 desde375 NPY train originales; mismos IDs y diferencia máxima0,0 frente al resultado remoto, atol 1e-6/rtol 0. `restoration_receipt.json`, `restored_from_originals.npz`. Regresiones independientes rechazan inventario de hashes vacío, esquema/receta incompatibles y caché alterado/incompleto. |
| P6 | Conforme. Reserva previa900 s cubre TimeLimit 600+KillWait 30 observados. Intento reclamable una sola vez; prueba independiente concurrente4 procesos/8 solicitudes:1 admitida/7 rechazadas. Ledger liquidado una vez:3 s, sin pendientes, caja USD 0, reserva final 12 h intacta. `remote/budget.json` es snapshot; duración de proceso no se cobró de nuevo. |
| P7 | Conforme con límite de memoria explícito. Job39 `COMPLETED`, exit0:0, ElapsedRaw3 s,4 CPU, solicitud8 G, límite10min. `remote/r2-e00-r0-m02-s17-20261119-01-accounting.json`. `sacct.MaxRSS` vacío; único pico disponible es del proceso:316560 KiB=309,14 MiB. Artefactos recuperados y hashes comprobados por revisión independiente, sin observación independiente del servidor. |
| P8 | Revisión independiente de propuesta y código conforme;10 pruebas pasaron en32,55 s en la verificación independiente, más prueba de concurrencia. Se corrigieron reuso de intento y restauración sin inventario/identidad completos. Cierre documental, sincronización de los dos requisitos y archivo completados; estado final en00. |

## Interpretación y siguiente incremento

El piloto obtuvo175/375 aciertos (46,67%) sobre M02 después de solo dos épocas. Es diagnóstico de un fold y no el resultado de la receta fija80 épocas, un OOF completo, una estimación del test o un criterio de promoción. No justifica descartar o elegir la arquitectura. El costo observado permite proponer después E01 completo de tres folds con su propio alcance revisado; TCN/Transformer requieren resolver R1 y otros pilotos. No extrapolar esta velocidad a secuencias o video. No hubo compras, GPU, payloads test o envíos.
