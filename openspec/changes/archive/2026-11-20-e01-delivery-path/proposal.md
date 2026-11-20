## Why

Recuperación del20nov2026: E01 sigue siendo la única receta validada (686/1125,60,98% LOSO) y no existe todavía ningún camino de entrega. `finalfit`, bundle, `predict` y `validate-submission` figuran como interfaces futuras en [05 §9](../../../../docs/05_technical_architecture.md); sin ellos no hay CSV posible, y el desempate oficial favorece el envío más temprano ([01 §3](../../../../docs/01_problem_definition.md)).

Repetir la restauración RGB no cambia la decisión vigente. La pareja predefinida de [04 §6](../../../../docs/04_solution_and_experiment_design.md) no se promueve ni con las probabilidades E08 provisionales: E01+E08 suma+26 aciertos, pero M03 pierde12 (máximo permitido: uno). La alternativa con OOF aceptados, E01+E02O, suma+4 y M04 pierde20. E11 queda cerrado: RGB está222 aciertos por debajo del líder y el máximo es12. Diagnóstico en [07 §12](../../../../docs/07_results_and_publication_protocol.md). Por eso este ítem asegura la entrega del campeón y aplica la confirmación de semillas prevista, que es el único paso restante del catálogo con señal no bloqueada.

## What Changes

- Registrar la decisión E12 bajo la regla vigente: finalista único E01; sin ensemble ni E11.
- R2-E13 para E01: semillas29 y43, tres LOSO cada una, con receta, épocas, sampler y escalador idénticos a E01/17; restaurar cada modelo desde los NPY originales.
- R2-E14: refit con los1125 clips train usando el conjunto común de semillas que resulte de la regla.
- Bundle portable con predictor por muestra desde NPY originales, validación del CSV y medición CPU de inferencia, todo comprobado solo con train.

## Capabilities

### New Capabilities

- `delivery-bundle`: refit final, bundle restaurable, predicción individual y validación estricta del CSV, sin acceso a payloads test.

## Impact

Este ítem amplía la CLI de baseline con la semilla como parámetro cerrado {17,29,43}. El productor cambia; E01/17 y su snapshot quedan intactos y se aceptan como padre porque receta e hiperparámetros son idénticos. Se añaden `finalfit-baseline`, `predict-bundle` y `validate-submission`. Ledger único: alcance nuevo `e01-delivery-path` de9000s, sin tocar los5147,780808451s medidos ni los18060s retenidos. La reserva final de43200s y la caja USD0 quedan intactas. Solo Cronos CPU y CPU local; sin GPU.

## Acceptance

| AC | Evidencia |
|---|---|
| D1 | La decisión E12/E11 queda documentada con las cifras del diagnóstico. E08 se identifica como provisional y no aceptado, sin crear ningún OOF RGB. |
| D2 | Seis fits80épocas (semillas29/43×M02/M03/M04), cada uno750/375 y restaurado desde originales en proceso nuevo, diferencia ≤1e-6 atol/rtol0. Si los seis completan, se reporta el OOF del promedio de probabilidades17/29/43, por persona y semilla. Cualquier fallo deja solo la semilla17. No se escoge la mejor semilla. |
| D3 | Refit sobre1125 por semilla común, escalador ajustado solo con train y épocas fijas, sin validación ni selección. El bundle contiene pesos, escalador, receta, orden de clases y códigos de01, productor, lock y hashes. |
| D4 | `predict-bundle`, en un proceso nuevo y sin caché de entrenamiento, reconstruye R0 desde NPY y produce probabilidades por muestra. Debe ser invariante al orden y al tamaño de lote, e igual a la predicción en proceso del refit (atol1e-6) sobre los1125 clips train. Se miden tiempo y memoria CPU para375. |
| D5 | `validate-submission` exige el encabezado `video_id,predicted_sign`, cobertura exacta de la plantilla, códigos válidos, UTF-8 y ningún duplicado ni índice. Las pruebas usan una plantilla sintética derivada de train. No se lee la plantilla ni ningún payload test. |
| D6 | Ledger: una reserva por job (900s; TimeLimit600s+KillWait), máximo dos jobs activos y liquidación única. Los18060s siguen comprometidos y la reserva final de43200s queda intacta. La CPU local solo es respaldo si Cronos no está disponible, con la misma contabilidad. |
| D7 | Pruebas completas y revisión independiente de diseño/implementación. Snapshot del productor nuevo, registros canónicos reconciliados y sync/archive. El freeze, la inferencia test y el envío no se ejecutan. |

## Out of scope

Payloads o plantilla test, freeze, CSV competitivo, envíos oficiales, GPU, restauración RGB, nuevas recetas, cambios de umbral, pagos o Git/PR. La enmienda opcional de la regla de pareja (opción B de [04 §16](../../../../docs/04_solution_and_experiment_design.md)) requiere una decisión humana separada.

## Authorization

**Propuesto, pendiente de aprobación humana.** El prompt de recuperación del20nov autorizó recuperación, inspección y preparación del plan, no esta ejecución.
