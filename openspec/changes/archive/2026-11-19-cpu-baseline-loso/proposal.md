# Línea base CPU completa con LOSO

## Why

El piloto acreditó el recorrido técnico, pero sus dos épocas sobre M02 no evalúan la receta completa. El usuario autorizó continuar después de presentar tres folds R0/MLP de 80 épocas. La receta y selección pertenecen a [04](../../../../docs/04_solution_and_experiment_design.md), el estado a [00](../../../../docs/00_INDEX.md).

## What Changes

- Comando de ajuste externo fijo de 80 épocas, semilla17, sin selección de checkpoint; conserva el piloto de dos épocas como diagnóstico separado.
- Admisión de un alcance CPU nuevo en el ledger existente, sin reiniciar consumos; tres intentos reales en Slurm y restauración de cada uno desde train original.
- Agregación OOF estricta con logits/probabilidades, métricas y diagnósticos train; bloquea resultados incompletos, solapados o incompatibles.

## Capabilities

### New Capabilities

- `cpu-baseline`: evaluación reproducible R2-E01 de la receta completa.

### Modified Capabilities

Ninguna alteración normativa del diagnóstico `cpu-pilot`.

## Impact

Cambios en `src/lsc5/`, pruebas, lanzador Slurm y documentos existentes. Sin dependencias nuevas, Git/PR, pago, GPU, test, refit final ni envíos. El nuevo alcance admite hasta1 hora-trabajo, dentro de48 globales con12 reservadas. Tres jobs de4CPU/8GiB/10min, reserva900s por intento y máximo dos simultáneos. No reintentar ajustes por su accuracy.

## Criterios de aceptación

| AC | Resultado observable |
|---|---|
| B1 | Cada fold conserva receta R2.1, semilla17,80 épocas,750/375 clips, escalador fit-only y muestreo balanceado; validación se evalúa solo al finalizar. Piloto y ajuste completo son fases distintas. |
| B2 | Pesos finales, escalador, split, logits/probabilidades, etiquetas train y costos tienen procedencia/hashes; otro proceso reproduce375 probabilidades desde originales en cada fold con atol1e-6/rtol0. |
| B3 | Agregador admite exactamente M02/M03/M04 completos y compatibles, cubre1125 IDs una vez, verifica verdad contra manifest y publica atómicamente solo tras validar. Rechaza fases piloto, duplicados, faltantes, hashes o clases alterados. |
| B4 | Reporte OOF conserva accuracy, macro-F1, confusión global/por persona, clase, vista y longitud; missingness anatómica se declara desconocida. IDs, logits y errores quedan privados. No interpreta tres personas como incertidumbre poblacional ni selecciona semillas. |
| B5 | Alcance nuevo≤3600s se incorpora idempotentemente al único ledger sin cambiar consumos/límites anteriores. Cada job tiene reserva previa vinculada y reclamable una vez; todos sus estados terminales se liquidan con tiempo real. |
| B6 | Tres trabajos reales Slurm terminan con evidencia recuperada y contabilidad reconciliada; se conserva snapshot exacto del código. Revisión independiente, pruebas focales, docs y sync/archive según evidencia; no hay pago/test/envío. |
