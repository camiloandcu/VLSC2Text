## ADDED Requirements

### Requirement: Refit y bundle reproducibles del candidato fijado

El sistema SHALL reajustar cada semilla común del candidato con los1125 clips train, con receta y épocas fijas, y SHALL empaquetar pesos, escaladores, clases, códigos, productor y hashes en un bundle inmutable que se restaure sin el caché de entrenamiento.

#### Scenario: Semilla no prevista

- **WHEN** se solicita un ajuste con una semilla fuera del conjunto {17,29,43}
- **THEN** se rechaza antes de reservar o entrenar

#### Scenario: Restauración en proceso nuevo

- **WHEN** el bundle predice clips train desde los NPY originales en otro proceso
- **THEN** sus probabilidades coinciden con las del refit en proceso dentro de atol1e-6 y no dependen del orden ni del tamaño de lote

### Requirement: CSV estructuralmente válido sin aprendizaje del test

El sistema SHALL validar el encabezado exacto `video_id,predicted_sign`, la cobertura exacta de la plantilla y los códigos de clase, y MUST NOT calcular estadísticas, calibraciones o selecciones con payloads test.

#### Scenario: CSV defectuoso

- **WHEN** falta, sobra o se repite una fila, o hay un código o encabezado inválido
- **THEN** la validación falla con un motivo explícito y no se produce un archivo de entrega
