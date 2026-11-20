# TCN temporal de columnas opacas

## Why

No se dispone del extractor y no se acredita R1; la primera baseline completa deja una referencia de comparación. Se propone continuar sin anatomía supuesta, conforme a [04 §13](../../../../docs/04_solution_and_experiment_design.md) y [05 §13](../../../../docs/05_technical_architecture.md). Adaptación aprobada por el usuario el19 nov2026 («Sí, apruebo»); no confundirla con la autorización anterior condicionada a R1 acreditada.

## What Changes

- Perfil de secuencia opaca, escalador fit-only por frame y TCN pequeña.
- Piloto de costo y tres folds completos condicionados a viabilidad; comparación pareada con R2-E01.
- Artefactos/restauración desde originales, alcance CPU nuevo y contratos verificables.

## Capabilities

### New Capabilities

- `opaque-temporal`: secuencia completa, TCN y evaluación sin semántica anatómica.

### Modified Capabilities

Ninguna alteración normativa de pilotos/baseline previos.

## Impact

Paquete `src/lsc5/`, pruebas, lanzador Slurm y registros actuales. Sin Git/PR/publicación, nuevas dependencias previstas ni servicios externos. Hasta1 hora-trabajo CPU; preparación local, piloto y transferencia se miden por separado. Ledger activo y consumo previo intactos. No GPU/pago/test/refit/envíos. E02O usa tres slots de E02 en esta ola; no agrega ajustes sobre48. Presupuesto y receta autoritativos en04 §13.

## Criterios de aceptación

| AC | Evidencia exigida |
|---|---|
| T1 | Entradas1125 train y splits750/375 intactos; secuencia opaca, sin columnas de metadata ni interpretación de ceros; escalador por frames reales solo de fit. |
| T2 | TCN/optimización cerradas según04 §13; padding neutralizado e invariancia a padding y composición del batch verificadas; piloto separado de80 épocas fijas/semilla17. |
| T3 | Cambios en retenidos no modifican escalador/pesos/pérdidas de fit; hashes/identidad de artefactos completos y restauración por fold desde originales con atol1e-6/rtol0. |
| T4 | Piloto real mide costo y memoria, y prueba batch60 fit-only descartado; cada admisión verifica duración estimada×1,5≤TimeLimit y TimeLimit+KillWait≤reserva por separado, además de cadena completa dentro de alcance/reserva final/plazo. Todos los intentos se contabilizan una vez sin reinicio. |
| T5 | OOF íntegro1125, distribuciones/logits/verdad verificados; métricas y comparación pareada por persona frente a R2-E01. Regla de promoción prefijada; no afirmar causalidad temporal por cambiar entrada y arquitectura. |
| T6 | Pruebas focales y revisión independiente, evidencias reales o límites explícitos, documentos reconciliados y sync/archive según resultado. No acceso test/pagos/envíos. |
