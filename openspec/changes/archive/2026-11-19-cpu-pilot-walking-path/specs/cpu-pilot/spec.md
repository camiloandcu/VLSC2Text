## ADDED Requirements

### Requirement: Piloto CPU reproducible exclusivo de train

El sistema SHALL ejecutar un piloto con procedencia verificada e insumos exclusivos de train, aislar la persona retenida durante ajuste, conservar semántica opaca y restaurar predicciones sin acceder a payloads test (P1–P5).

#### Scenario: Piloto válido con características opacas

- **WHEN** se suministra un manifest train válido y una partición por persona retenida
- **THEN** el sistema ajusta escalado local al fold y el MLP de dos épocas, conserva evidencia inmutable y otro proceso reconstruye R0 desde NPY train originales y reproduce probabilidades sin caché de entrenamiento
- **AND** las métricas se identifican como diagnóstico del piloto, distinto de un candidato de épocas completas

#### Scenario: Rol inválido o duplicado entre personas

- **WHEN** un insumo referencia test, escapa train, contradice procedencia o tiene contenido idéntico entre personas de ajuste y validación
- **THEN** el sistema lo rechaza antes del ajuste

### Requirement: Ejecución acotada y contabilizada

El sistema SHALL admitir y contabilizar cada intento bajo presupuesto CPU acumulado y reserva de finalización, ejecutar el piloto Slurm autorizado dentro de recursos declarados y conservar artefactos privados (P6–P8).

#### Scenario: Presupuesto insuficiente

- **WHEN** trabajo consumido y comprometido, nueva reserva que cubre estimación con margen y límite real del job con gracia verificada, más reserva final, superan el límite
- **THEN** no inicia un nuevo piloto y la causa queda inspeccionable

#### Scenario: Intento completo o fallido

- **WHEN** un piloto termina o falla tras admitirse
- **THEN** el registro conserva consumo medido y evidencia del intento, liberando solo compromiso no usado
