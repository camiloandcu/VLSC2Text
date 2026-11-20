## Context

Contrato anatómico sin acreditar. Método y decisiones prospectivas pertenecen a04 §13; límites y autorización real a00. No crear una normalización anatómica implícita bajo un nombre opaco.

## Goals / Non-Goals

Comparar una receta temporal viable contra R0/MLP. No asegurar ganancia, atribuir efecto causal del orden temporal, escoger columnas, explorar hiperparámetros o habilitar otras ramas por inferencia.

## Decisions

Implementar perfiles cerrados piloto/completo, caché no aprendido, scaler serializado fold-local, TCN con máscara temporal y agregación con identidad de receta nueva. Conservar snapshots anteriores y alinear comparación por ID. Un clip cero real participa como observación; padding no contribuye a scaler, convoluciones siguientes o pooling. Contratos de transporte y verificación en05 §13.

## Risks / Trade-offs

Más canales, señales particulares de persona/cámara y detecciones de calidad desigual pueden impedir mejora. Es un contraste de recetas, no una ablación aislada de temporalidad. CPU/RAM pueden superar lo presupuestado: piloto decide admisión; no cambiar T/batch/épocas silenciosamente. Si llegan detalles del extractor, requieren contraste y otra decisión antes de habilitar R1.

## Verification

T1–T6 de la propuesta, pruebas sintéticas de invariancia/aislamiento, piloto real y restauración de cada fold en procesos distintos. No afirmar cumplimiento operativo por pasar tests. Entrega local sin Git/PR; la adaptación fue aprobada y la implementación sigue sus límites.
