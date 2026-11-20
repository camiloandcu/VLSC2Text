# Diseño del primer recorrido

Aplican [04 R2.1](../../../../docs/04_solution_and_experiment_design.md) y [05](../../../../docs/05_technical_architecture.md). Este incremento entrega únicamente R0/MLP y diagnóstico estructural, no el catálogo completo.

## Decisions

- Python3.10, NumPy1.26.4 y PyTorch2.4.1 CPU, compatibles con Cronos. Pruebas locales aisladas; entrenamiento medido en Slurm, sin cambios al entorno compartido.
- Manifest portable con rutas relativas a train, SHA256 de ambas modalidades, T/dtype y metadata para partición/auditoría. Feature R0 = media y desviación poblacional temporal por columna,3324 valores; no se interpreta anatomía.
- Caché determinista de estadísticas de todo train bajo el nuevo perfil `raw_stats`: JSON de revisión, rol train, esquema `raw_stats_v2`, dtype/shape `[N,3324]` float32, IDs ordenados, hash de manifest/entradas, versión/hash del productor y SHA256 del NPZ. El NPZ contiene valores e IDs, sin etiquetas usadas como features. El productor `features.cache` publica directorio completo de forma atómica, después de verificar integridad/cobertura; el runner rechaza coverage parcial, hash/orden/esquema/procedencia incompatible o datos no finitos. Transformación aprendida por fold serializada aparte; el caché no aprende estadísticas entre clips. Reconstrucción de predicción desde originales no depende del caché.
- MLP3324→128→5, ReLU/dropout0,3, CE/AdamW y primeros dos pasos de épocas del scheduler80/5; muestreador balanceado por persona/clase de 04. No elegir checkpoint con validación ni comparar este piloto con recetas completas.
- Run privado y nuevo por intento, escrituras atómicas, hashes y guardas de rol/procedencia. Checkpoint de tensores, carga `weights_only=True`; NumPy sin pickle. Recuperación a nivel de artefacto completo; reanudación de entrenamiento interrumpido permanece en W02 posterior.
- Registro económico único con lock, reserva y todos los intentos. Antes de `sbatch`, comprometer el máximo entre estimación×1,5 y límite real del job más KillWait; propuesta900 segundos por intento, suficiente solo si600+KillWait≤900. Comprobar KillWait real antes de admitir. Presupuesto propio≤2horas-trabajo dentro del límite global48 y reserva final 12. Mantener compromiso hasta estado terminal Slurm; reconciliar una sola vez con duración real del job, incluidos fallos. El tiempo de proceso es diagnóstico, no un segundo cargo; una copia local del ledger es evidencia, no otro saldo activo.
- Copiar paquete y caché derivados de train a un directorio privado nuevo en Cronos; no extraer ni examinar Test.zip. Guardar código/hash y recuperar resultados. No reutilizar una carpeta ajena ni modificar SSH/configuración remota.

## Risks / limits

La falta del código del extractor impide acreditar anatomía solo por forma/rangos. P2 acepta un diagnóstico explícito, no una certificación falsa. El throughput de R0 no estima directamente TCN/Transformer o GPU. La métrica tras dos épocas prueba el recorrido, no calidad competitiva. Sin permiso de salida/publicación de datos, los artefactos se conservan privados.

## Verification

Fixtures sintéticas para guardas train/test, scaler fold-local, duplicados, muestreo y presupuesto. Integración de entrenamiento/carga en procesos separados y comparación de probabilidades. Dataset real solo para auditoría/piloto autorizado. Revisión independiente de propuesta antes de código y verificación independiente después de pruebas; endpoint local, sin publicación.

Medir≥10 pasos tras excluir los primeros5 de calentamiento de rendimiento; esto no modifica el warm-up de 5 épocas del scheduler. Separar I/O, entrenamiento, evaluación y escritura. Probar backward/optimizerstep con 60ejemplos del lado de ajuste en una copia descartada del modelo, sin tocar el checkpoint ni ajustar con la persona retenida. Extrapolar coste80 épocas por 04, sin extrapolar accuracy. Tras recuperar artefactos, otro proceso local vuelve a calcular R0 desde NPY originales de validación y aplica pesos/escalador; comparar probabilidades con atol 1e-6 y rtol 0.
