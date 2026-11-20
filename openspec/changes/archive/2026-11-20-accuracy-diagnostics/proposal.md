## Why

E01 llega al60,98% LOSO. La pérdida de ajuste ronda0,0004 y la accuracy por persona varía31 puntos, lo que indica que el cuello de botella es generalizar a una persona nueva, no la capacidad del modelo. Cuatro hipótesis baratas pueden explicar gran parte del déficit, y ninguna se ha comprobado:

1. R0 codifica posición y tamaño absolutos de la persona.
2. La ruta RGB global reduce1920×1080 a224 y casi no ve las manos.
3. Cada clase se grabó en una sesión distinta (código C##), con el posible atajo que eso implica.
4. El bloqueo de R1 se debe a la falta de procedencia documental, aunque 1662 = 33×4 + 468×3 + 2×21×3 coincide exactamente con la serialización estándar de MediaPipe Holistic y puede verificarse empíricamente con train.

El objetivo de la ola es identificar la representación capaz de acercarse al80% LOSO. No se garantiza esa cifra.

## What Changes

Una ola de diagnósticos cortos, aprobables y ejecutables por separado, solo con train. X1 condiciona X4, X5 y X6; los demás son independientes.

| Ítem | Pregunta | Método mínimo | Criterio de decisión | Costo estimado |
|---|---|---|---|---|
| X1 | ¿Las1662 columnas son Holistic (pose x,y,z,visibilidad; cara; mano izq./der.), con qué unidades, espejo y convención de lateralidad? | MediaPipe0.10.14 (la versión de Cronos) en un entorno separado sobre30 clips train (dos por persona×clase), frames nativos. Correlación y error por bloque frente al NPY, y concordancia de bloques cero. | **Acreditado** si en los frames con detección en ambos lados cada bloque pose/mano tiene correlación ≥0,99 y error mediano ≤0,01 en fracción de imagen. Si no, se prueba una lateralidad o espejo alternativo. Si nada coincide, se propone extraer landmarks propios de los videos con transformación fija por muestra. | CPU local, ~1h |
| X2 | ¿Existe un atajo de sesión/captura que se transfiera entre personas? | Estadísticas de color y luminancia de bordes del frame sin persona (K=4 frames) y regresión logística LOSO. | Accuracy >35%: hay señal de captura, y se reporta como riesgo. Ese canal **no** se usa como feature. | CPU local, ≤1h |
| X3 | ¿Por qué M02 acierta sign_01 en 1/75? | Hojas de contacto de frames de sign_01 por persona y vista. Si X1 pasa, energía de movimiento por mano. | Hipótesis escrita (variante, mano dominante, detección o encuadre) con evidencia visual. Sin entrenamiento. | ≤1h |
| X4 | ¿Cuánto mejora normalizar respecto al cuerpo? | Requiere X1. Variante de R0 con coordenadas centradas en el punto medio de hombros y escaladas por su anchura, manos relativas a la muñeca; mismo MLP/LOSO/semilla17. | Ganancia OOF y por persona frente a E01. Si gana, se usa como entrada para X6. | Cronos CPU, 3 fits ~6s |
| X5 | ¿RGB centrado en las manos supera al frame global? | Requiere X1. Recortes de mano desde el video original en1080p → DINOv2 congelado sobre un subconjunto estratificado (p.ej.300 clips), con kNN/logística LOSO frente al mismo subconjunto del caché global. | Si los recortes superan al global por ≥10 puntos, se propone extracción completa de recortes. | GTX1650, ≤30min |
| X6 | ¿La secuencia normalizada recupera información temporal? | Requiere X1/X4. Recorte del segmento activo (estadística de energía por clip, sin estado aprendido de validación) y TCN `compact_tcn_v2` sobre R1/R2 con aumentos de escala/rotación/traslación/velocidad. | Promoción por la regla flexibilizada de04 §17. Es candidata, no solo diagnóstico. | Cronos CPU, 3–6 fits |
| X7 | ¿Las vistas V01–V03 son tomas simultáneas de la misma ejecución? | Comparar longitudes y trayectorias NPY de clips con igual índice entre vistas. Solo análisis de la estructura de los datos: nunca como feature. | Diversidad efectiva por persona y clase (25 o 75 ejecuciones) para dimensionar aumentos y la interpretación. | ≤30min |

## Capabilities

### New Capabilities

- `accuracy-diagnostics`: diagnósticos train-only que acreditan representación, atajos y anomalías antes de nuevas candidatas.

## Impact

Hay que instalar MediaPipe en un entorno local nuevo, sin tocar `.venv`/`.venv-rgb`. Por cada ítem que se ejecute: código de análisis, artefactos privados y un resultado en 07. Ledger único: alcance `accuracy-diagnostics` de hasta7200s, sin tocar los18060s retenidos ni la reserva final. Caja USD0.

## Acceptance

| AC | Evidencia |
|---|---|
| A1 | Cada ítem ejecutado registra pregunta, método, cifras, decisión y límites en07, aunque el resultado sea negativo. |
| A2 | Solo se usa train. Test no se lee, ni siquiera para estadísticas o comprobaciones visuales. Nombres de archivo, C##, V## e IDs no se usan como features. |
| A3 | X1 acredita o rechaza el layout con las cifras del criterio. R1/ROI se desbloquean solo si queda acreditado. |
| A4 | Las candidatas que salgan de X4/X6 conservan LOSO750/375, estado fit-only y restauración desde originales antes de entrar en la selección final. |

## Authorization

El usuario aprobó, el20nov2026, proponer los diagnósticos cortos necesarios para buscar el80%. **La ejecución de cada ítem requiere aprobación humana.**
