# Primer recorrido y piloto CPU

## Why

El diseño R2.1 está elegido por el usuario mediante «Sí, continúa», después de proponer como siguiente bloque verificar el contrato y ejecutar el piloto CPU. Hace falta medir un recorrido reproducible antes de invertir en GPU. La autorización y el estado pertenecen a [00](../../../../docs/00_INDEX.md).

## What Changes

- Paquete Python 3.10 y CLI para manifest exclusivo de train, splits LOSO, estadísticas R0 y piloto `raw_stats_mlp_v2`.
- Artefactos privados con procedencia, escalador ajustado solo al fold, checkpoint seguro y predicción de validación restaurada en otro proceso.
- Contabilidad acumulada CPU y lanzador Slurm de cuatro CPU; un piloto real de dos épocas, sin completar comparaciones oficiales.
- Verificación estructural del contrato. La anatomía sigue sin acreditar si falta el extractor; no habilitar R1/ROI por asumirla.

## Capabilities

### New Capabilities

- `cpu-pilot`: auditar train → preparar features/split → entrenar piloto → restaurar → medir y conservar evidencia.

### Modified Capabilities

Ninguna implementada previamente.

## Impact

Archivos previstos: `pyproject.toml`, locks/dependencias CPU, `src/lsc5/`, `configs/`, `tests/`, lanzador en `scripts/`, y reconciliación de 00/05/06/README. Datos de solo lectura; artefactos en `artifacts/` o `~/resultados/`, excluidos de publicación. Sin Git/PR acordados: entrega local verificada.

## Criterios de aceptación

| AC | Resultado observable |
|---|---|
| P1 | Manifest/loader no recorren test, rechazan rutas fuera de train y conservan hashes/IDs/etiquetas de train sin introducir metadata predictiva. |
| P2 | Forma `(T,1662)`, float64 y finitud verificadas; esquema anatómico queda explícitamente pendiente, con R0 opaco habilitado. |
| P3 | Tres splits LOSO disjuntos; scaler solo con train IDs del fold; coincidencia de contenido entre personas rechazada. |
| P4 | Piloto MLP de dos épocas con receta/muestreo R2.1, semilla 17, estados/costos y resultado diagnóstico explícito; mide≥10 pasos después de calentamiento de medición, I/O/evaluación/escritura, prueba backward/step con batch 60 en copia descartada usando solo IDs de ajuste y extrapola80 épocas con margen 1,5. No se presenta como baseline completa. |
| P5 | Otro proceso recibe NPY train originales, pesos/escalador y reconstruye R0 sin caché de entrenamiento; reproduce probabilidades de validación dentro de tolerancia declarada1e-6. Hashes/rol/coverage incompatibles o caché incompleto se rechazan. |
| P6 | Admisión/registro CPU incluye consumido, fallos, pendientes, nueva unidad con margen y reserva; nunca supera48 horas-trabajo o caja10 por iniciar este bloque. |
| P7 | Trabajo real Slurm4 CPU/8GiB/máximo10min, reserva previa≥máximo real incluido KillWait verificado, evidencia de duración/memoria/estado y recuperación local de artefactos; este bloque admite hasta2 horas-trabajo CPU dentro del límite global. |
| P8 | Pruebas focales, revisión independiente, documentación y sincronización/archive OpenSpec conforme al resultado real. Sin compras, GPU externa, inferencia test o envíos. |

Los AC anteriores son autoritativos para este ítem; 06 conserva solo cobertura del mapa W00/W01/recorrido mínimo W02.
