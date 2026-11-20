## Context

R0 usa columnas opacas y evita depender de anatomía pendiente. Se reutilizan manifest/splits del primer piloto; el caché se reconstruye desde train porque la huella estricta del productor cambia al ampliar código. Se conserva el snapshot anterior para restaurar aquel piloto.

## Goals / Non-Goals

Completar R2-E01, tres ajustes fijos y OOF inspeccionable. No habilitar configuraciones arbitrarias, otras semillas/arquitecturas, búsqueda, test, refit ni selección final para envío.

## Decisions

1. Refactorizar el motor común con perfiles cerrados `diagnostic_pilot` (2) y `outer_baseline` (80). Misma semilla17, scheduler, modelo, batches y escalado. No consultar validación dentro del ciclo; guardar únicamente pesos finales. El probe de batch60 permanece solo diagnóstico.
2. Separar alcance de reserva: `cpu-baseline-loso`, límite3600s. Registro explícito e idempotente, rechazando cambios de un límite existente. El claim debe coincidir también con el alcance esperado del comando. No reinicializar ledger remoto ni usar su snapshot local como activo.
3. Restauración verifica inventario, identidad de perfil y receta, scaler y procedencia; ambos perfiles soportados. Agregación verifica estos mismos contratos sin releer originales; además coteja logits/probabilidades finitos, etiquetas/IDs de validación y clases. Ningún run diagnóstico es elegible.
4. OOF ordenado como manifest, conservado en NPZ con logits/probabilidades/verdad/fold. Reporte JSON con hashes de entradas, métricas y código, directorio publicado por rename atómico tras validar todo. Vista procede exclusivamente de metadata train; longitud se agrupa en≤40,41–60,>60 frames, fijados antes de observar resultados; missingness anatómica permanece desconocida. No emplear esas variables para predecir o elegir subconjuntos.
5. Tres jobs separados, cada uno retenido→bind→release; ejecución secuencial suficiente para respetar dos slots. Reserva900s, TimeLimit600s+KillWait real verificado antes de admitir. Sin repetición por puntuación; fallo técnico se registra y cualquier recuperación conserva nuevo intento y presupuesto.

## Risks / Trade-offs

La huella estricta invalida cachés/restore de versiones distintas; conservar snapshots inmutables y reconstruir caché con el nuevo productor. Accuracy OOF es evidencia de desarrollo, especialmente al comparar después recetas. Un entrenamiento rápido no garantiza calidad ni tiempos de video. El estado remoto puede cambiar; verificar límites efectivos sin explorar cuentas ajenas.

## Verification

Pruebas sintéticas: ambos perfiles, aislamiento, conteo80, rechazos OOF y presupuesto sin reinicio/cruce de alcance. Restauración separada desde originales y métricas recalculadas con1125 resultados reales. Revisiones independientes de propuesta e implementación; endpoint local.
