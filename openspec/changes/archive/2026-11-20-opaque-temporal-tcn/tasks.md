## 1. Diseño

- [x] 1.1 Concretar adaptación, contratos y costo máximo desde la evidencia del extractor ausente.
- [x] 1.2 Revisión independiente de propuesta y registrar decisión humana real.

## 2. Implementación condicionada a aprobación

- [x] 2.1 Perfil opaco, scaler y caché con procedencia (T1).
- [x] 2.2 TCN, perfiles y pruebas de padding/aislamiento (T2–T3).
- [x] 2.3 Admisión/Slurm y piloto técnico con costo completo (T4).
- [x] 2.4 Tres folds, restauración, OOF y comparación pareada si pasa piloto (T3–T5).
- [x] 2.5 Revisión independiente, evidencia por AC y cierre documental/sync/archive (T6).

## Evidencia

Aprobación humana de R2.2 registrada en00. Implementación local verificada el20 nov2026:16 pruebas conformes en72,50s, incluidos tres folds sintéticos de80 épocas/1520 actualizaciones, aislamiento de retenidos, padding, restauración en proceso nuevo sin caché, gate y OOF/comparador positivos/negativos. Estos datos sintéticos no prueban viabilidad ni accuracy del reto.

Revisión independiente estática: T1/T2 conformes; dos hallazgos medios corregidos y reexaminados sin nuevos hallazgos materiales. Gate ahora exige receipt+NPZ restaurado desde originales, ligados al run/productor/manifest. Comparación exige ancla externa del reporte histórico e identidad completa de tres fuentes OOF. Verificación dinámica independiente y operación real pendientes.

Productor congelado `e9d812a3d0d0f9e7893ddf1053396ca84ef87ea99207b5565dc043e4cf34abae`; snapshot privado de27 archivos y referencia hash de la baseline conservados antes del piloto. Despliegue nuevo conserva ledger global y antecedentes. Job43/piloto M02 presentado retenido, vinculado a reserva360s y liberado; KillWait30s verificado. No se han admitido todavía folds completos.

Piloto real job43 completado:19s Slurm,4CPU/8GiB, límite5min, reserva360s. Caché preparada en11,759s,1125 hashes NPY equivalentes al manifiesto; I/O+scaler2,849s;33 pasos medidos tras5 de calentamiento, máximo0,04720s. Probe batch60 fit-only con backward/paso de optimizador, copia descartada. RSS máximo del proceso1556920KiB; MaxRSS de sacct vacío, sin atribuirle precisión de memoria de job. Restauración local en proceso separado de375 NPY originales, diferencia máxima0; gate enlaza receipt/NPZ y estima118,544s por fold con margen, menor que900s. Reserva2880s para cadena, dentro de3600 y reserva final43200 global. Sin cambio de receta.

Revisión dinámica independiente focal conforme:3 pruebas en53,76s. No hallazgos materiales abiertos de implementación. No sustituye evaluación operativa final.


Cierre medido de T3–T5: tres folds80épocas/1520actualizaciones con semilla17; restauración original375clips/fold, diferencia0. OOF1125 y comparación pareada completos. Resultados autoritativos en [07 §9](../../../../docs/07_results_and_publication_protocol.md); consumo/recursos/plazo en [06 §10](../../../../docs/06_delivery_and_iteration_plan.md). E02O no promovida. Evidencia privada bajo `artifacts/cpu-temporal`: `source_snapshot_manifest.json`, snapshot tar, `deployment.json`, receipts de submissions/admisión/contabilidad, `remote_pilot`, `remote_M02_M03`, `remote_M04`, restauraciones JSON+NPZ, OOF y `paired_comparison.json`. Son snapshots del ledger activo, no presupuestos adicionales. `final_remote_check.txt` acredita0 jobs activos/productor igual y0 reservas pendientes.


Revisión operativa independiente conforme, sin hallazgos materiales abiertos: verificó27 archivos/snapshot/productor, cuatro runs y restauraciones, tres folds80/17/1520, cobertura1125/verdad/logits/softmax, métricas y diagnósticos recalculados, baseline anclada y pareada. Recalculó gate/cadena/reservas; ledger preserva21s previos,167s nuevos,188s totales/0pendientes,0gasto. Contrastó concurrencia/KillWait/plazo con recibos y comprobaciones del script de admisión; no accedió a SSH, credenciales o NPY reales. No certifica procedencia anatómica, calidad competitiva, costo extremo a extremo ni resultados de test. T1–T6 verificados dentro de estos límites; sync/archive se integra como cierre local.

Verificación primaria final previa a archivo:16 pruebas conformes72,50s;3 independientes53,76s; JSON de auditoría y hash del manual conservados. Validación OpenSpec estricta y revisión de enlaces/valores privados conformes; se repiten tras mover el cambio para verificar sus rutas. No hay Git/PR/publicación en este endpoint local. Ningún trabajo remoto activo ni nueva rama experimental autorizada.


Cierre local: cambio archivado el20 nov2026 como `2026-11-20-opaque-temporal-tcn`; especificación normativa sincronizada. Tres especificaciones conformes en modo estricto y enlaces revalidados después del movimiento. Código fuente permanece idéntico al snapshot medido. No quedan criterios pendientes dentro del alcance autorizado; siguientes opciones requieren su propio ítem/decisión.
