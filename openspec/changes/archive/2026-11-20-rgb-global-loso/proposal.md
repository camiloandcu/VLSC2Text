## Why

El reintento RGB completó30 clips y replay. El usuario indicó «Apruebo el siguiente alcance»: extracción global train completa y cabeza RGB con LOSO, según04 R2-E07/E08. Se concreta esa autorización; no se reinicia investigación ni se abre otra receta.

## What Changes

- Caché fijo de1125 clips globales, K16, encoder externo congelado y cobertura completa explícita.
- Cabeza `rgb_pyramid_mlp_v2`, piloto CPU de2 épocas y tres LOSO80 épocas/semilla17 si pasa costo/restauración.
- Restauración desde originales de375 clips por fold y comparación OOF con baseline congelada.
- Ledger único, límites definidos, QA independiente y cierre local.

## Capabilities

### New Capabilities

- `rgb-global-loso`: caché RGB completo, escalado de canal fit-only, MLP y evaluación restaurable.

## Impact

Contratos canónicos en [04 §15](../../../../docs/04_solution_and_experiment_design.md), [05 §16](../../../../docs/05_technical_architecture.md), [06 §13](../../../../docs/06_delivery_and_iteration_plan.md). Alcance aprobado de12h-trabajo máximo, con límites individuales y reserva final intacta, desembolso0. GPU propia para encoder/restauración, CronosCPU4CPU/8GiB para cabezas. NoE09/ROI/ensemble/semillas adicionales/refit/test/pagos/envíos. Implementación≤4h antes de reevaluar dependencia esencial. Sin Git/PR/publicación.

## Acceptance

| AC | Evidencia |
|---|---|
| V1 | Decoder optimizado conserva píxeles de los30 casos históricos y casos sintéticos (incluidos N<K), sin cambiar N/índices/resize/RGB. Si no coincide, conservar decoder previo. Caché1125 cubre exactamente manifest train, SHA/arrays/encoder/procedencia válidos y rechaza cobertura piloto. |
| V2 | Escalador384 canales con todos los frames de750fit, fitIDs registrados; pirámide global/primera mitad/segunda mitad1152. MLP/optimizador/sampler/80épocas17 fijos; validación no cambia estado ni selecciona checkpoint. |
| V3 | Ledger conserva574,955533384s/caja0/reserva43200 y limita extracción/restauración/CPU. Piloto2épocas M02 antes de3fits; gate medido, restore del piloto y proyección de refit/cadena previos a admitirlos. |
| V4 | Tres modelos completos y restauración independiente en proceso nuevo: primero375 del piloto desde caché inmutable, después1125 videos originales sin requerir caché de entrenamiento; cada fold375 conserva probabilidades atol1e-6/rtol0. Fallo se registra sin fingir equivalencia. |
| V5 | OOF1125/3personas/5clases, ninguna predicción in-fit; comparison pareada contra SHA ancla E01 y decisión según04, sin test o ranking. Control temporal inverso diagnóstico sin selección de sentido. |
| V6 | Pruebas, revisión independiente de diseño/implementación/operación, registros reconciliados y sync/archive; siguiente rama no se ejecuta automáticamente. |

## Authorization

Solicitud directa de aprobación del alcance E07/E08 posterior al piloto. Incluye implementar, verificar, preparar caché y ejecutar piloto/3folds/restauración dentro de sus puertas; conservar el fallo previo. No requiere otra confirmación del mismo alcance. Si una puerta falla, detener esa fase y conservar evidencia.


## Corrección acotada y cierre negativo

La alternativa de nuevo contrato contable se retiró por innecesaria antes de implementación. Se conserva18060s comprometidos, actual_secondsnull y fallo original. La reparación de finally y pruebasCPU corresponde al comportamiento ya autorizado; no implica nueva aprobación contable o intentoGPU. Snapshot ejecutado42archivos preservado, fuente posterior diferenciada. Revisión independiente de proporcionalidad conforme. Restauración original fallida yOOFnoejecutado permanecen así; el cierre documental no los convierte en conformes. Corrección/pruebas/QA/lifecycle en curso.
