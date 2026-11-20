## Context

Hechos de partida en07 §§8–12: E01 alcanza 60,98%, E02O 48,89% y E08 41,24% provisional. Las 3 personas tienen 375 clips cada una (5 clases × 3 vistas × 25), y el código C## está asociado a la clase en train. El 37,36% de los frames tiene ambos bloques de mano en cero (bajo el layout supuesto).

## Decisions

1. Primero X1, porque condiciona las palancas de mayor valor esperado (normalización corporal, secuencia, recortes de mano). X2, X3 y X7 corren en paralelo y no requieren entrenamiento.
2. Las estadísticas que podrían aprender algo se calculan solo con el lado fit de cada fold. El recorte temporal y la normalización corporal son transformaciones deterministas por clip.
3. Los resultados se comparan siempre frente a E01 y su ancla SHA, por persona.

## Risks

- MediaPipe0.10.14 puede no reproducir la configuración del extractor original, por ejemplo por otra complejidad de modelo. Si no coincide, eso no prueba que el layout sea otro.
- El subconjunto de X5 da una estimación ruidosa: sirve para decidir, no como resultado final.
- La señal de captura de X2 puede confundirse con la seña si el fondo cambia con la persona.
