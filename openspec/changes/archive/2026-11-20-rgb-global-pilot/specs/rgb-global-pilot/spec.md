## ADDED Requirements

### Requirement: Extracción piloto de RGB global fijo

El sistema SHALL extraer embeddings R4 únicamente de los30 videos train fijados, con identidad de pesos/transformaciones y cobertura de piloto explícitas, sin aprendizaje ni semántica anatómica (G1–G3).

#### Scenario: Caché piloto incompleto para clasificación completa

- **WHEN** se intenta consumir30 embeddings como cobertura de1125 clips
- **THEN** se rechaza el uso y no se presenta como caché completo ni resultado OOF

#### Scenario: Replay desde video original

- **WHEN** se restaura el encoder fijo en proceso nuevo y se decodifica el mismo clip con batches1/4
- **THEN** se conservan píxeles y embeddings finitos dentro de la tolerancia declarada

### Requirement: Factibilidad local con recursos y autoridad acotados

El sistema SHALL reservar y contabilizar un intento local dentro del ledger único, respetar recursos/deadline y cerrar con decisión explícita sin activar automáticamente extracción completa, entrenamiento o gasto (G4–G5).

#### Scenario: Recurso, integridad o plazo insuficiente

- **WHEN** no se cumple alguna puerta de ejecución o se supera un límite
- **THEN** se detiene con evidencia, conserva el consumo y no cambia silenciosamente el protocolo
