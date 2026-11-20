# accuracy-diagnostics Specification

## Purpose
Diagnósticos train-only que acreditan representación, atajos y anomalías antes de admitir nuevas candidatas, sin acceso a test.

## Requirements

### Requirement: Diagnósticos restringidos a train

El sistema SHALL ejecutar cada diagnóstico exclusivamente sobre train y MUST NOT leer payloads test ni usar nombres de archivo, códigos de cámara/vista o IDs como features.

#### Scenario: Ruta test solicitada

- **WHEN** un diagnóstico recibe una ruta bajo `data/test`
- **THEN** se rechaza antes de abrir el archivo

### Requirement: Acreditación empírica del layout

El sistema SHALL desbloquear representaciones anatómicas solo si la comparación con un extractor de referencia sobre train cumple los umbrales preregistrados de correlación y error por bloque.

#### Scenario: Comparación fuera de umbral

- **WHEN** algún bloque pose/mano no alcanza correlación0,99 o error mediano0,01
- **THEN** R1/ROI permanecen bloqueadas y se registra la discrepancia
