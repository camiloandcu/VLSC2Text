## ADDED Requirements

### Requirement: Secuencia opaca y entrenamiento aislado

El sistema SHALL conservar T y columnas numéricas sin semántica supuesta, ajustar escalado exclusivamente con frames reales de fit y entrenar la TCN cerrada con padding neutralizado (T1–T3).

#### Scenario: Validación o padding distintos

- **WHEN** solo cambian datos retenidos o se añade padding temporal al mismo clip
- **THEN** el ajuste no usa esos datos retenidos y los logits del clip no dependen del padding dentro de la tolerancia declarada

### Requirement: Comparación temporal reproducible y acotada

El sistema SHALL admitir los tres folds completos solo tras piloto viable, conservar restauración desde originales y publicar OOF/comparación pareada íntegros bajo presupuesto acumulado (T4–T6).

#### Scenario: Piloto no viable

- **WHEN** costo con margen, memoria o plazo exceden límites
- **THEN** se cierra la rama con evidencia y no se alteran silenciosamente longitud, batch o receta

#### Scenario: Tres folds completos

- **WHEN** existen1125 predicciones fuera de ajuste, restauraciones y contabilidad conformes
- **THEN** se comparan con R2-E01 por IDs y personas usando criterios previos y sin atribución causal no acreditada
