## Context

E01 `raw_stats_mlp_v2`/R0/semilla17 es el campeón: 60,98% LOSO, restaurado desde originales y con un ancla SHA fija. E02O no se promovió, y E08 tiene un resultado provisional del 41,24%, sin restauración aceptada. R1/ROI siguen bloqueadas. Los cortes de 06 son: nuevas ramas hasta el22nov18:00 y freeze el23nov12:00, ambos en Bogotá. El cierre es el25nov y la hora sigue desconocida. Existen dos evaluaciones, cuenta la última y la segunda se reserva para recuperación técnica.

## Decisions

1. **Finalista único.** La pareja que define 04 §6 se evaluó sobre OOF: con E08 provisional M03 pierde12, y con E02O (OOF aceptados) M04 pierde20. Ninguna se promueve. No se cambia el umbral después de ver estas cifras; la opción de enmienda queda documentada aparte, en 04 §16.
2. **Semillas.** Se aplica E13 tal como lo define 04 §6: semillas29/43 solo para E01. El parámetro admite el conjunto cerrado {17,29,43}; cualquier otro valor se rechaza. Receta, sampler, LR, épocas y escalador fit-only no cambian. El run de la semilla17 histórica se reutiliza como padre y no se reentrena.
3. **Agregación.** Si los nueve modelos LOSO están completos, el score de la receta es la accuracy del promedio aritmético de probabilidades17/29/43. También se reportan las tres semillas por separado. Si falta uno, todo se resuelve con la semilla17.
4. **Refit.** Hay un modelo por semilla común sobre los1125 clips, con escalador R0 ajustado en los1125, 80 épocas y ninguna evaluación intermedia. El bundle promedia las probabilidades de sus modelos con el mismo orden de clases.
5. **Bundle/predictor.** El bundle es un directorio inmutable con `bundle.json` (receta, semillas, clases→códigos, productor, lock, hashes por archivo), pesos `state_dict` y escaladores `.npz`, sin pickle. `predict-bundle` lee cada NPY con validación float64/finito/1662 columnas y calcula R0 por muestra. No usa estadísticas del conjunto, tiene orden de salida determinista y aborta ante errores de contenido en lugar de inventar una etiqueta.
6. **Validación del CSV.** `validate-submission` es puramente estructural; no acredita accuracy. Las plantillas sintéticas se derivan de IDs train.
7. **Cómputo.** Cronos Slurm 4CPU/8GiB/10min por job, reserva900s, KillWait verificado, máximo dos jobs activos y nada en login. Restauración y medición de inferencia en CPU local (o Cronos), registradas con tiempos propios.

## Risks

- Promediar tres semillas puede no mejorar el OOF. La regla igual lo fija y no se elige la mejor semilla.
- Tres personas no estiman la accuracy de una cuarta. El OOF sigue siendo evidencia de desarrollo.
- Cronos puede retirarse sin aviso. Copiar los artefactos tras cada job y probar el predictor en CPU local.
- El cambio de productor no debe invalidar E01/17. Su compatibilidad se verifica por identidad de receta e hiperparámetros, no por reetiquetado.

## Verification

Pruebas sintéticas: semillas fuera del conjunto rechazadas, refit sin IDs de validación, round-trip del bundle, invariancia orden/lote, CSV con fila faltante/duplicada/extra/código inválido/encabezado incorrecto rechazado, y ninguna ruta test accesible desde los comandos de este ítem. Ejecución: D2–D4 con train real. Revisión independiente antes de ejecutar y otra de operación al cierre.
