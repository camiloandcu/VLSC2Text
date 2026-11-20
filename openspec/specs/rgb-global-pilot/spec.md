# rgb-global-pilot Specification

## Purpose

Acotar mediciones locales de un encoder RGB congelado sobre treinta clips train, con integridad, contabilidad y límites verificables. Conservar cada resultado y permitir únicamente el reintento adicional solicitado explícitamente, sin convertir el piloto en autorización de extracción completa, clasificación o gasto.

## Requirements

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

### Requirement: Reintento explícito único de un piloto fallido

El sistema SHALL permitir una sola reserva adicional del perfil fijo de reintento, ligada al piloto original liquidado y fallido, con idénticos manifiesto/selección y recibo del padre, conservando el historial y todos los límites anteriores.

#### Scenario: Falta de autorización operativa o padre no elegible

- **WHEN** no se utiliza el indicador explícito, el padre no es el original fallido/liquidado o ya existe un reintento
- **THEN** se rechaza la reserva adicional sin alterar registros previos ni repetir ejecución

#### Scenario: Reintento medido y cierre

- **WHEN** se ejecuta el único reintento explícitamente autorizado con un claim nuevo
- **THEN** se registra y liquida su resultado real por separado y se conserva el fallo anterior, sin abrir otra ejecución automáticamente
