# rgb-global-loso Specification

## Purpose

Establecer cobertura y procedencia de features RGB train, aislamiento externo del escalador y puertas de costo/restauración antes de aceptar una evaluación LOSO completa. El experimento inicial se archivó con restauración fallida y sin OOF aceptado; estos requisitos conservan las condiciones exigidas a futuras candidatas.

## Requirements

### Requirement: Features RGB fijas y escalado externo aislado

El sistema SHALL exigir cobertura completa1125 train con procedencia/píxeles/encoder íntegros y ajustar el escalador384 únicamente con los750 IDs fit de cada fold, preservando la pirámide1152 y receta fijas.

#### Scenario: Cobertura o procedencia incorrectas

- **WHEN** un caché piloto, alterado o de otro manifiesto se ofrece a la cabeza
- **THEN** se rechaza antes de ajustar o evaluar

#### Scenario: Sujeto externo

- **WHEN** se transforma una muestra del sujeto retenido
- **THEN** se aplica el estado fit sin actualizar medias/desviaciones, pesos o checkpoint

### Requirement: Evaluación RGB completa con costo y restauración verificables

El sistema SHALL medir/admitir el piloto antes de los tres fits80épocas, contabilizar todos los intentos en el ledger único y restaurar las375 predicciones por fold desde originales en proceso nuevo antes del cierre OOF competitivo.

#### Scenario: Piloto insuficiente o fallo de restauración

- **WHEN** falta gate medido o una equivalencia/límite no se cumple
- **THEN** se conserva el fallo y no se presenta una corrida incompleta como candidata completa

#### Scenario: Tres folds conformes

- **WHEN** los tres fits y sus restauraciones se completan
- **THEN** se agregan1125 predicciones externas y se comparan con la baseline congelada según reglas previas, sin test
