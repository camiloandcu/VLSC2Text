## ADDED Requirements

### Requirement: Reintento explícito único de un piloto fallido

El sistema SHALL permitir una sola reserva adicional del perfil fijo de reintento, ligada al piloto original liquidado y fallido, con idénticos manifiesto/selección y recibo del padre, conservando el historial y todos los límites anteriores.

#### Scenario: Falta de autorización operativa o padre no elegible

- **WHEN** no se utiliza el indicador explícito, el padre no es el original fallido/liquidado o ya existe un reintento
- **THEN** se rechaza la reserva adicional sin alterar registros previos ni repetir ejecución

#### Scenario: Reintento medido y cierre

- **WHEN** se ejecuta el único reintento explícitamente autorizado con un claim nuevo
- **THEN** se registra y liquida su resultado real por separado y se conserva el fallo anterior, sin abrir otra ejecución automáticamente
