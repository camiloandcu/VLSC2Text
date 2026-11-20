# cpu-baseline Specification

## Purpose

Evaluar la receta R2-E01 completa con tres folds LOSO, perfiles cerrados y predicciones OOF verificables; conservar restauración desde originales, ejecución contabilizada y límites de interpretación. Los AC B1–B6 pertenecen a la [propuesta archivada](../../changes/archive/2026-11-19-cpu-baseline-loso/proposal.md).

## Requirements

### Requirement: Línea base completa y OOF aislado por persona

El sistema SHALL ejecutar R2-E01 con tres folds LOSO de80 épocas/semilla17 y receta R2.1, sin seleccionar checkpoint según validación, y verificar restauración desde train original (B1–B2).

#### Scenario: Fold completo

- **WHEN** se recibe manifest train y split válido con reserva CPU del alcance correcto
- **THEN** se ajusta exclusivamente con dos personas y se guarda la evaluación final de la tercera con procedencia verificable

### Requirement: Agregación íntegra y ejecución contabilizada

El sistema SHALL publicar OOF solo con tres folds completos compatibles, cobertura exacta y verdad acreditada, y conservar presupuesto, evidencia privada y límites de interpretación (B3–B6).

#### Scenario: Entrada incompleta o incompatible

- **WHEN** falta un fold, se repite un ID o contradice perfil, hashes, clases o manifest
- **THEN** se rechaza sin publicar resultados parciales como OOF completo

#### Scenario: Tres folds verificados

- **WHEN** están completos los1125 resultados fuera de ajuste y la contabilidad real de sus jobs
- **THEN** el reporte conserva métricas y diagnósticos reproducibles, sin atribuirlos a test ni a una población independiente de personas
