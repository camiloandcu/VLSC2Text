## Tasks

- [x] 1. Recuperar aprobación y concretar alcance/contratos/cotas.
- [x] 2. Revisión independiente de diseño y reconciliación de hallazgos.
- [x] 3. Implementar extracción completa, presupuesto, cabeza/restauración/OOF y pruebas; QA.
- [x] 4. Snapshot/despliegue/reserva y extracción1125 con evidencia.
- [x] 5. Piloto CPU/gate y tres fits completos; liquidar y recuperar.
- [ ] 6. Restaurar desde originales, OOF/comparación y revisión operativa.
- [x] 7. Documentar decisión, verificar y sync/archive como cierre negativo explícito.

## Evidence

Autorización del usuario: «Apruebo el siguiente alcance», después de proponer extracción completa train y cabezaRGB LOSO. No implica otras recetas o acciones externas. Evidencia previa autoritativa en07 §11; el primer fallo permanece registrado.

Revisión independiente de fundación `rgb_loso_foundation`,20nov: pase para implementar, sin bloqueos materiales. Contrastó protocolo, identidad, cota39360s/gate medido y restauración; no acredita viabilidad o accuracy. Limitación cámara–clase preservada y pruebas/gates pendientes.

QA independiente `rgb_loso_quality`: productor`ab5046c5eaf9b896747597a140f2b54540544024070189ab84fcf3d018bb8518`, sin bloqueos materiales después de corregir/reproducir controles de inicio tardío y baseline sustituida. Cuatro negativos independientes conformes3,14s; restauración en segundo proceso del piloto incluida en job. Prueba sintética integral3/3 y piloto previo11/11; suite final y ejecución pendientes.

Verificación previa a ejecución:31/31 pruebas98,16s, cuatro negativos independientes3,14s, OpenSpec5/5 estricto,41Markdown/137enlaces/88archivos públicos conformes; scripts/auditoríaJSON válidos. Snapshot42archivos/productor`ab5046c5eaf9b896747597a140f2b54540544024070189ab84fcf3d018bb8518`. Igualdad exacta de N/índices/píxeles/SHA/dimensiones de30videos históricos en52,281s; prueba sintética N<K compara transporte nuevo/anterior. Solo se optimiza transporte, no encoder/preprocesado. Despliegue remoto confirmó productor y cota de cadena antes de reservarGPU. Evidencia privada `artifacts/rgb-loso`.


Estado intermedio anterior al fallo — ejecución parcial acreditada: extracción1125 COMPLETED4548,825s,30equivalencias previas y snapshot42archivos preservados. Caché completo transferido; piloto47 COMPLETED6s y restore-cache375 con diferencia0; gate medido13,625s/fold/15,885s refit. Fits48–50 COMPLETED6s cadauno. En ese estado intermedio la restauración original estaba en curso; el cierre negativo posterior sustituye ese estado. Proyecciones adversa y por pase completo, nueva reserva final y desviación de registro posterior al lanzamiento se conservan en06 §13 y `forecast_reconciliation.json`; revisión independiente focal solicitada.

Revisión focal de previsiones posterior aE07: pase condicionado para continuar dentro de cotas vigentes; gate CPU confirmado y reserva final recalculada17001,069s<43200. La documentación posterior al inicio de restore permanece como desviación procedimental. No sustituye QA operativo/restauración/OOF pendientes.


Cierre negativo de ejecución,20nov: restore falló; último progreso850/1125/3031,676s,872NPZ de staging conservados sin aceptar como resultado. TimeoutExpired durantefinally impidióexecution.json; causa inicial desconocida. Revisión independiente confirmaV4fallido/V5nohabilitado yV3mediciónfinalperdida. NoOOF/comparación definitiva ni reintento. Ledger:15settled/1comprometido,5147,780808451s medidos+18060s retenidos; reserva final43200 y caja0. V6solo cierra documentación negativa; tareas6–7 no se declaran cumplidas. Snapshot42/productor ejecutado preservado. Enmienda de corrección/contabilidad pendiente de decisión; no sync/archive como ejecución conforme.


## Corrección acotada y cierre negativo

La alternativa de nuevo contrato contable se retiró por innecesaria antes de implementación. Se conserva18060s comprometidos, actual_secondsnull y fallo original. La reparación de finally y pruebasCPU corresponde al comportamiento ya autorizado; no implica nueva aprobación contable o intentoGPU. Snapshot ejecutado42archivos preservado, fuente posterior diferenciada. Revisión independiente de proporcionalidad conforme. Restauración original fallida yOOFnoejecutado permanecen así; el cierre documental no los convierte en conformes. Corrección/pruebas/QA/lifecycle en curso.

Cierre negativo verificado: arreglofinally local y32pruebas87,77s,5focales3,88s y2escenariosindependientes conformes. Snapshot posterior separado; originales42inalterados. Tarea6fallida enrestauración,OOF/comparaciónnoejecutados; no marcarla completa. Tarea7 cierra documentación/QA/lifecycle como experimento fallido, conservando18060comprometidos. V3limitado,V4fallido,V5nohabilitado. Archivo no concede aceptaciónexperimental.

Lifecycle efectivo: dos requisitos sincronizados y archivo2026-11-20-rgb-global-loso, con advertencia6/7 tareas intencionalmente conservada: tarea6fallida/noejecutada, sinOOF aceptado. Reserva pendiente no liberada. Endpoint local negativo, sinGit/PR/publicación.
