## 1. Fundación y alcance

- [x] 1.1 Registrar autorización y revisar propuesta/contratos B1–B6.

## 2. Implementación y verificación

- [x] 2.1 Ampliar perfiles cerrados y procedencia/restauración (B1–B2).
- [x] 2.2 Implementar agregación estricta y diagnósticos (B3–B4).
- [x] 2.3 Incorporar alcance y Slurm sin reiniciar contabilidad (B5).
- [x] 2.4 Pruebas focales y revisión independiente; resolver hallazgos.

## 3. Ejecución y cierre

- [x] 3.1 Ejecutar tres folds y recuperar artefactos/contabilidad (B6).
- [x] 3.2 Restaurar desde originales en procesos nuevos y recalcular OOF (B2–B4).
- [x] 3.3 Registrar evidencia por AC e interpretación; reconciliar documentos y sync/archive (B6).

## Evidencia

Revisión de fundación conforme. Revisión independiente de implementación conforme:13 pruebas en23,29s y contraste con features retenidas alteradas; pesos, escalador y80 pérdidas idénticos, una evaluación retenida al final. Se corrigió cardinalidad oficial en las fronteras de ajuste/restauración/OOF. Huella revisada `25af8eba4758af5e027cd02f180e72df29aadb4e9aa472f5c4d523c91fdba8e2`. La evidencia real se registra debajo; la prueba sintética acredita comportamiento y no desempeño en LSC5.


## Evidencia operativa por AC · 19 de noviembre de2026

Artefactos privados en `artifacts/cpu-baseline/`. `remote/budget.json` es snapshot recuperado, no otro ledger activo; el único activo permanece en Cronos según08. `deployment.json` conserva workspace/huella. La copia exacta de código, dependencias, pruebas y lanzadores queda en `source_snapshot.tar.gz` y su manifiesto. Manifest/splits train coinciden con los del primer incremento; el caché R0 se reconstruyó con el productor ampliado, sin modificar el caché anterior.

| AC | Evidencia efectiva |
|---|---|
| B1 | Tres runs completos, cada uno80 épocas/semilla17,750 fit/375 val y1520 actualizaciones; pérdidas, batches y scaler fit-only conservados. `remote/runs/*/{run,metrics,split}.json`, `preprocessor.npz`. Revisión independiente sintética acreditó una evaluación retenida final y ausencia de cambios en pesos/pérdidas al alterar solo features retenidas. |
| B2 | `restoration_receipts.json`: tres procesos nuevos,375 probabilidades desde NPY train originales por fold, sin caché; max_abs_difference0 en todos, atol1e-6/rtol0. Modelos, logits/probabilidades y cinco artefactos por run tienen hashes verificables. |
| B3 | `oof/oof.npz`, `oof/report.json`:1125 IDs únicos y ordenados como manifest, verdad cotejada, tres personas una vez y perfiles compatibles; distribución/softmax verificadas. Rechazos sintéticos de cohorte incompleta, faltantes, duplicados, perfil piloto, identidad y valores alterados. |
| B4 | Resultado y diagnósticos medidos pertenecen a [07 §8](../../../../docs/07_results_and_publication_protocol.md). Reporte privado conserva métricas, confusiones, vista y bins de longitud prefijados; missingness anatómica desconocida. Una sola receta/semilla, sin inferencia poblacional o de test. |
| B5 | `remote/budget.json` conserva piloto previo3s y añade18s de tres jobs; total21s consumidos/0pendientes, caja USD0, reserva final43200s intacta. Alcance nuevo3600s; reservas900s por job cubren600s+KillWait30 verificado. Sin reinicio de historial ni segundo claim. |
| B6 | Jobs40(M02),41(M03),42(M04): `COMPLETED`, exit0:0, ElapsedRaw6s cada uno,4CPU, ReqMem8G, TimeLimit10min. Recibos `remote/*-accounting.json`; primero dos jobs y después el tercero. MaxRSS de sacct vacío: solo picos del proceso,301,35/296,57/302,50MiB. No son memoria total del job. Recuperación/snapshot completos; revisión operativa independiente conforme; cierre documental y sync/archive registrados en00. Sin compras, GPU, test, refit o envíos. |

La medición remota se acredita mediante recibos recuperados; no es una observación física independiente del servidor. Los18s asignados no representan duración extremo a extremo, extracción local de características, transferencia o restauración. No hubo nuevos intentos de entrenamiento tras observar accuracy.

Revisión operativa independiente final conforme: verificó hashes, scaler exacto con features permitidas de ajuste, replay de pesos, restauraciones, métricas/grupos OOF, historial previo intacto y snapshot de20 archivos. No consultó originales ni servidor directamente; se mantiene el límite de evidencia por recibos. Trece pruebas conformes en23,29s; no se repitió entrenamiento real para confirmar una puntuación.
