# 04 · Alternativas y protocolo experimental · revisión R2.1

Propuesta del 19 de noviembre de 2026, pendiente de aprobación humana. **R2 sustituye el catálogo y las recetas del 10 de noviembre**; no hereda su pase técnico ni autoriza entrenamiento. R2.1 precisa iteración, escalamiento y dos evaluaciones, conservando recetas, IDs y máximos de ajustes de R2. El cambio de presupuesto de USD 6 a **USD 10 de desembolso total** está incorporado. Requisitos en [01](01_problem_definition.md), contratos en [05](05_technical_architecture.md), presupuesto monetario y calendario en [06](06_delivery_and_iteration_plan.md), infraestructura comprobada en [08](08_compute_operations.md).

## 1. Decisión y recomendación

La pregunta es cómo maximizar accuracy top-1 sobre una persona desconocida, con 1.125 clips de tres personas, Cronos limitado a CPU, hasta USD 10 adicionales y cierre el 25 de noviembre en Bogotá. No hay resultados propios de modelos. Una GPU más rápida no constituye evidencia de mayor accuracy.

Se propone una ruta híbrida. Cronos compara modelos compactos de landmarks y entrena cabezas sobre representaciones visuales. Una GPU externa ejecuta principalmente un encoder visual congelado, cuyos resultados se reutilizan entre folds, cabezas y semillas. La adaptación visual tiene una puerta posterior y presupuesto reservado. El encoder y la inferencia final deben poder ejecutarse también en CPU o en la GPU local.

El núcleo conserva tres recetas y nueve ajustes LOSO. El catálogo completo baja de 84 a **48 ajustes neuronales completos como envolvente conservadora**, además de pilotos y extracciones. No se ejecuta por defecto todo el catálogo. Se eliminan de esta revisión el pretraining SSL desde cero, el refinamiento anidado de épocas y la reproducción de grandes modelos de video. El margen se dedica a completar comparaciones, confirmar candidatos y entregar.

Cronos ofrece dos trabajos simultáneos, hasta 4 CPU y 32 GiB por trabajo. Su RTX A6000 está bloqueada para la cuenta. Se propone un máximo de **48 horas-trabajo CPU**, equivalentes a hasta 192 CPU-h si todos usan cuatro CPU; no son 48 horas de reloj ni capacidad reservada. El gasto externo tiene su propio límite en 06. Colab y la GTX 1650 son respaldo oportunista, sin cuota incorporada al plan base.

## 2. Evidencia y consecuencias para el diseño

| Fuente primaria o evidencia local | Hallazgo pertinente | Consecuencia propuesta y límite |
|---|---|---|
| PoET, Lascar et al., VISAPP 2026, [DOI 10.5220/0014237500004084](https://doi.org/10.5220/0014237500004084), §§2 y 3.3 | Encoder de dos capas, cuatro cabezas y dimensión 128; el trabajo original usa 94 puntos y búsqueda de hiperparámetros. | Comparar un Transformer pequeño. Nuestra selección de 49 puntos, épocas y normalización son adaptaciones; no se replica su score ni su búsqueda de 20 horas. |
| Roh et al., SignLang 2024, [registro ACL](https://aclanthology.org/2024.signlang-1.36/), §§3.1–3.3 y resultados | Anclas y tratamiento de manos faltantes modifican el reconocimiento; su interpolación y longitud fija pertenecen a otra receta. | Preservar posición global, forma local y máscaras. No convertir huecos completos de una mano en anatomía inventada ni alargar todo a 512 frames. |
| FR-Head, Zhou et al., CVPR 2023, [arXiv 2303.03729](https://arxiv.org/abs/2303.03729), §3.2 | Refinamiento contrastivo durante entrenamiento sin cabeza auxiliar al inferir. | Ensayar una pérdida supervisada pequeña entre personas. La propuesta SupCon no es la arquitectura ni la pérdida completa de FR-Head. |
| DINOv2, Oquab et al., [arXiv 2304.07193v2](https://arxiv.org/html/2304.07193v2), §7.2 y Tabla 7 | Evalúa video con encoder congelado por frame y agregación temporal. | Reutilizar características externas; comparar agregación barata y cabeza temporal. El resultado en Kinetics/SSv2 no predice LSC5. |
| [DINOv2 oficial](https://github.com/facebookresearch/dinov2), commit `7764ea0f912e53c92e82eb78a2a1631e92725fc8`, consultado el 19 | ViT-S/14 estándar: 21 M de parámetros, embedding 384; código y pesos estándar Apache-2.0. | Artefacto principal propuesto para extracción. No confundir variantes con registros, capas de salida o licencias de derivados. |
| SignRep, Wong et al., [arXiv 2503.08529v1](https://arxiv.org/html/2503.08529v1), §§7.1–7.2 y A8; [repositorio](https://github.com/ryanwongsa/SignRep) | Pretraining específico de señas; RGB Hiera-B. Reconocimiento publicado con ajuste y 64 frames, evaluación congelada de retrieval; pesos publicados en 2025. | Alternativa especializada plausible, aplazada por integración, protocolo y términos no comerciales. No atribuir sus resultados ajustados a una cabeza CPU congelada. |
| Eldele et al., TSLANet, ICML 2024, [arXiv 2404.08472](https://arxiv.org/abs/2404.08472), métodos y escalabilidad | Bloques convolucionales/espectrales compactos para series. | Mantener una alternativa temporal convolucional y diferencias de coordenadas; no asumir que el espectro de una seña corta equivale al de sus benchmarks. |
| Ingimundarson et al., 2026, [arXiv 2609.25862v2](https://arxiv.org/html/2609.25862v2), discusión | Transferencia entre lenguas y normalización de manos/cuerpo importan con pocos datos; evidencia limitada por corridas y contexto. | Priorizar representación y transferencia. Los pesos de otro corpus requieren contrato y licencia; no se inicia aprendizaje multilingüe con datos nuevos. |
| Auditoría completa, [02](02_data_audit_public.json) | 63.284 frames; ambos bloques manuales en cero en 37,36%, bajo layout supuesto; variación por persona. | Mantener RGB temprano y máscaras explícitas. Cero observado no demuestra ausencia física ni fallo del detector. |
| Inspección visual focal del 19, tres frames train | Diferencias de apariencia y encuadre; muestra de tres personas, tres clases y una vista. | Comparar contexto completo y recorte corporal. No acredita cobertura del dataset ni valida por sí sola los índices de landmarks. |

La revisión focal volvió a leer métodos y límites de las fuentes centrales; [la biblioteca](../literature/resources.csv) conserva el research amplio. No se han descargado pesos ni reproducido resultados. Las citas remiten a fuentes durables; las copias locales de artículos no forman parte de la documentación pública.

## 3. Alternativas mecanísticamente distintas

| ID | Propuesta | Por qué podría ganar | Fallo principal / prueba que la debilita | Estado propuesto |
|---|---|---|---|---|
| B0 | Clase mayoritaria, desempate por código | Control del evaluador; 20% analítico por balance. | No aprende reconocimiento. | Control sin ajuste, no candidato. |
| L0 | Estadísticas de las 1.662 columnas y MLP | Forma y posiciones persistentes podrían separar cinco señas con costo mínimo. | Ignora orden y puede aprovechar estilo de captura. | Núcleo, elegible neuronal. |
| L1 | TCN enmascarada sobre cuerpo y manos | Sesgo temporal local y pocos parámetros, adecuada para clips cortos. | Falla si la información necesaria desaparece de los landmarks. | Primera opción temporal. |
| L2 | Transformer pequeño inspirado en PoET | Relaciones temporales flexibles con capacidad moderada. | Sobreajuste o costo sin mejora frente a L1. | Comparador del núcleo. |
| L3 | Forma local de manos, posición global y movimiento sobre L1/L2 | Reduce diferencias de escala y conserva dinámica y lugar de articulación. | Normalización borra información o amplifica anclas inestables. | Dos ablaciones separadas. |
| V0 | DINOv2 congelado, pirámide temporal y MLP | Aprovecha pretraining sin ajustar el encoder y preserva orden grueso. | La representación estática ignora detalles manuales o aprende apariencia. | Primer candidato RGB. |
| V1 | Mismo caché DINOv2 y TCN pequeña | Aprende dinámica de características con ajustes CPU baratos. | Pocos datos no justifican la capacidad adicional. | Comparación RGB controlada. |
| V2 | Adaptador después del penúltimo bloque DINOv2 | Puede acercar la representación visual al dominio de señas. | Costo de activaciones, integración o sobreajuste; requiere nueve evaluaciones completas si se confirman tres semillas. | Condicional tras V0/V1. |
| H0 | Promedio de probabilidades de dos recetas | Landmarks y RGB pueden cometer errores distintos. | Errores correlacionados o degradación de una persona. | Solo con ganancia OOF predefinida. |
| D0 | GCN adaptada, SSL local o encoder especializado de señas | Topología, observaciones parciales o prior específico podrían ayudar. | Mayor integración y costo antes de disponer de baselines concluyentes. | Aplazada; exige nueva revisión de alcance. |

### Comparación previa y sensibilidad

Se proponen pesos antes de puntuar: pertinencia de señal 35%, robustez al cambio de persona 30%, eficiencia total 25%, facilidad de entrega 10%. Son juicios locales de 1 a 5, no probabilidades ni resultados. Primero se aplican restricciones de integridad, licencia, caja disponible y plazo; una puntuación no las compensa.

| Opción | Señal | Transferencia | Eficiencia | Entrega | Total |
|---|---|---|---|---|---|
| L0 | 2 | 2 | 5 | 5 | 3,05 |
| L1 | 4 | 4 | 5 | 5 | 4,35 |
| L2 | 4 | 3 | 4 | 4 | 3,70 |
| L3 | 4 | 4 | 4 | 3 | 3,90 |
| V0 | 5 | 3 | 4 | 4 | 4,05 |
| V1 | 5 | 3 | 4 | 3 | 3,95 |
| V2 | 5 | 3 | 2 | 2 | 3,35 |
| H0 | 5 | 4 | 3 | 3 | 4,00 |

Las fuentes de §2 motivan las valoraciones: L1 evita aprender apariencia; V0 conserva señal RGB con extracción amortizada; V2 repite cálculo y requiere integración. H0 depende de haber validado sus componentes. Al mover el peso bruto de señal de 0,35 a 0,15 o 0,55, manteniendo los otros y renormalizando, L1 queda en 4,44/4,29 y V0 en 3,81/4,21. Con peso 0,75, V0 supera a L1: 4,32 frente a 4,25. La preferencia depende de cuánto se valore recuperar señal RGB; eso justifica medir ambas, sin elegir por esta tabla el modelo final.

### Supuestos críticos y pre-mortem

| Prioridad | Supuesto / nivel de evidencia | Cómo podría fracasar el proyecto | Test y decisión |
|---|---|---|---|
| Crítica | Semántica de landmarks sin confirmar | Se entrenan manos o visibilidad con índices erróneos. | E00 valida layout con extractor o overlays train; hasta entonces solo L0 y RGB global. |
| Crítica | Costo y disponibilidad de GPU sin medir | Se consume el saldo en preparar el entorno y falta inferencia final. | E00/E07 miden toda la cadena y reservan finalización antes de alquilar o ampliar. |
| Alta | Landmarks contienen señal suficiente | L1/L2 aprenden ausencia o estilo en vez de la seña. | Comparación LOSO, diagnóstico de missingness y contraste RGB. |
| Alta | RGB aporta señal transferible | La apariencia y la cámara explican la ganancia de desarrollo. | Recorte corporal frente a global, errores por persona/vista y control temporal del mismo caché. |
| Alta | Acceso Cronos persiste | La cola o el retiro impiden confirmación/refit. | Copia de artefactos al completar cada corrida y ruta CPU/local ensayada con train. |
| Alta | Uso y transferencia de datos/pesos autorizados | Se elige un proveedor o peso incompatible. | Resolver condiciones antes de transferir; alternativa Cronos/local sin nuevo servicio. |

La asociación cámara–clase observada limita la interpretación de cualquier score. No existe un split independiente por cámara que conserve todas las clases con este dataset. Los nombres, cámaras e IDs no son features. Un recorte tampoco demuestra invariancia a cámara; el reporte conserva ese límite.

## 4. Representaciones fijadas para R2

**R0 `raw_stats_v2`.** Mantener las 1.662 columnas como opacas. Por clip calcular media y desviación poblacional temporal, vector de 3.324. Estandarizar cada dimensión con media/std de los clips de ajuste del fold; std menor que `1e-6` se reemplaza por 1. No convertir ceros a ausencias sin contrato. Uso de float32 después de validar la lectura float64.

**R1 `pose49_xy_mask_v2`.** Requiere layout y coordenadas verificadas. Orden: pose `[0,11,12,13,14,15,16]`, mano izquierda `[0..20]`, mano derecha `[0..20]`. Son 49 nodos, XY=98 y máscara original=49: **F=147**. Pose válida si coordenadas finitas, bloque no totalmente cero y visibilidad al menos 0,5; mano válida a nivel de bloque si sus 63 valores no son todos cero y son finitos. Un punto individual XY=0 no determina ausencia.

Antes de la geometría, llevar XY a fracciones de imagen: conservarlos si ya son coordenadas normalizadas de imagen, o dividir x por W e y por H si son píxeles. E00 acredita unidades y dimensiones por muestra; otras coordenadas requieren un nuevo contrato y mantienen R1 bloqueada. Conservar además XY originales para ROI. Los umbrales y respaldos siguientes operan en estas fracciones de imagen, no en píxeles.

Normalización por clip: mediana de centros de hombros y anchuras válidas mayores que `1e-3`. Restar centro y dividir por escala a puntos observados; ausentes permanecen cero. Si no hay hombros válidos en todo el clip pero hay señal utilizable, usar centro `(0.5,0.5)`, escala 1 y `quality_flags.anchor_fallback=true`. Sin observaciones utilizables en todo el clip, error explícito. El flag es metadato de calidad, no feature adicional.

Se conserva T nativo. Frame real totalmente cero: `time_mask=true`, observación falsa y posición temporal conservada. Padding: `time_mask=false`. Neutralizar estados de padding tras la proyección y después de cada operación que alimente otra convolución; atención enmascara keys y estados. No basta con enmascarar el pooling.

**R2 `pose49_localshape_v2`.** Conservar íntegra R1 y añadir, por mano, XY local respecto de su muñeca, escalado por la mediana válida de distancia muñeca–MCP medio del propio clip. Añadir 84 coordenadas locales, 42 indicadores de validez local, dos log-ratios de escala mano/cuerpo y dos indicadores de escala: **F=277**. Escala inválida o menor que `1e-3`: canales locales neutros y validez falsa; no alterar R1. La posición global de las manos permanece en R1. Índices y lateralidad deben estar acreditados.

**R3 `pose49_deltas_v2`.** Añadir a R1 diferencias XY consecutivas de coordenadas normalizadas y 49 máscaras que exigen observación en ambos frames: **F=294**. Primer frame y huecos: diferencias cero y máscara falsa. No conectar a través de ausencias ni llamar velocidad física a estas diferencias. E04 y E05 prueban cambios separados.

**R4 `dinov2s14_cls_v2`.** Encoder estándar sin registros, congelado y en `eval()`, RGB, normalización ImageNet del peso, salida CLS normalizada de dimensión 384. Por clip usar K=16 frames uniformes, índices `floor(j*(N-1)/(K-1)+0.5)`, del primer al último; se registran los índices reales. Si N<K en inferencia, repetir índices de esa misma regla y registrar duplicados, sin aprender una regla nueva del test. No flips ni aumentos estocásticos.

Vista global: conservar el frame entero con letterbox 224 y relleno de la media RGB de normalización. Es una adaptación declarada frente al center-crop habitual de DINOv2, para reducir riesgo de cortar manos. No se afirma equivalencia con su evaluación original.

Vista ROI para E10: caja única por clip con la unión de XY originales en coordenadas de imagen, antes de centrar/escalar por hombros, reutilizando únicamente los índices y máscaras de R1. E00 debe acreditar la conversión a píxeles: si XY son normalizados de imagen, usar x*W e y*H; si son píxeles, conservarlos. Para la caja usar puntos dentro de la imagen en todos los frames; expandir a un cuadrado centrado con lado `max(1.25*ancho,1.25*alto,0.5*min(W,H))`. Tomar límites enteros exteriores y pad fuera de imagen con la misma media RGB; resize 224. Exigir al menos tres nodos distintos y cinco frames con puntos válidos, lado finito y no mayor que `1.5*max(W,H)`; si falla, usar global y registrar fallback. No adaptar el crop frame a frame. Antes de E10 comprobar cobertura en diez clips train, dos por clase, repartidos entre personas y vistas. Estos controles no eligen una receta por accuracy.

La extracción global no depende del layout anatómico. ROI sí depende de verificarlo. Un frame observado con mano no detectada conserva RGB; no se suprime por la máscara de landmarks. Un fallo de decodificación es error de integridad, no un embedding de ceros.

## 5. Modelos y optimización

| Receta | Arquitectura fijada | Optimización / duración |
|---|---|---|
| `raw_stats_mlp_v2` | 3324→128→5, ReLU, dropout 0,3 | AdamW LR 1e-3, WD 1e-3, 80 épocas. |
| `compact_tcn_v2` | F→64; tres bloques residuales, una Conv1D k 5 por bloque, dilataciones 1/2/4, LayerNorm por frame, GELU, dropout 0,2; media enmascarada→5 | Igual MLP, grad clip 1; 80 épocas. |
| `tiny_transformer_v2` | F→128; dos capas, cuatro cabezas, FFN 256, dropout 0,3, posición sinusoidal, CLS→5 | AdamW LR 5e-4, WD 1e-2, grad clip 1; 80 épocas. |
| `rgb_pyramid_mlp_v2` | Media de embeddings en todo el clip y en sus dos mitades temporales, concatenación 1152→128→5, ReLU/dropout 0,3 | AdamW LR 1e-3, WD 1e-3; 80 épocas. |
| `rgb_tcn_v2` | D=384→64 y los mismos tres bloques temporales de la TCN | Igual TCN; 80 épocas. |
| `rgb_adapter_v2` | DINO congelado, adaptador residual 384→16→384 GELU después del penúltimo bloque; cabeza del mejor RGB | Adaptador LR 1e-4, cabeza LR 1e-3, WD 1e-3; 40 épocas. |

No se replica la búsqueda de hiperparámetros de los artículos. Scheduler cosine con warm-up de cinco épocas hasta 1% del LR, CE sin pesos, float32 y sin aumentos en el núcleo. La transformación RGB aprendida es únicamente el escalado por canal de embedding con estadísticas de los clips/frame-embeddings del lado de ajuste, serializado por fold; en el adaptador se aplica ese mismo estado al CLS de salida, sin recalcularlo con validación. RGB y landmarks tienen escaladores distintos.

Muestreo: cuatro clips por estrato `(persona,clase)`, barajado determinista por época. Batch externo 40 y final 60, con remanente balanceado 30/45; cada clip aparece una vez por época. Esto iguala el muestreo de CE y SupCon. CPU: loader 0 workers, un ajuste por trabajo. Si la memoria obliga a acumular gradientes, conservar el mismo batch efectivo; CE se pondera por número real de clips antes del paso. Una modificación del batch efectivo crea variante y requiere evaluación completa nueva.

E06 añade `0.1*SupCon`, temperatura 0,1 y proyección lineal de la representación agrupada a 64 dimensiones, normalizada L2, solo de entrenamiento. Para cada ancla, positivos de la misma clase y distinta persona; negativos de clases distintas. Excluir el propio ejemplo y pares de misma clase/persona; el denominador suma positivos y negativos elegibles. Promediar el log-softmax negativo sobre sus positivos y después sobre anclas con positivos. Conservar el batch efectivo completo para esta pérdida: acumular CE entre microbatches no reproduce sus pares contrastivos. Si no cabe, cerrar E06. Conserva datos/muestreo de su padre; se retira la proyección al inferir. No implementa el mecanismo de prototipos y muestras ambiguas completo de FR-Head.

El adaptador inicializa su última capa a cero. Parámetros del encoder congelados, módulos de encoder siempre en evaluación, gradiente habilitado a través del último bloque hacia el adaptador. Se propone caché opcional de tokens completos después del penúltimo bloque, antes del adaptador, en float32. Su prefijo externo es fijo y compartible; el adaptador y el head son fold-local. La prueba de replay debe comparar CLS con encoder completo sin adaptar: error relativo L2 ≤ 1e-4 sobre el piloto en el mismo entorno. Si falla o el costo de almacenar/transferir tokens no cabe, E11 se aplaza. No se cambia silenciosamente a tokens FP16.

Las combinaciones de forma local y diferencias, el grafo, rostro completo, coordenadas Z, interpolación, aumentos lingüísticos y pérdidas adicionales quedan fuera del catálogo R2. Cada incorporación posterior exige motivo, costo y nueva revisión.

## 6. Validación y selección predefinidas

Tres folds LOSO externos: M03+M04→M02, M02+M04→M03, M02+M03→M04. Son 750 clips de ajuste y 375 retenidos por fold, con clases balanceadas. Todo estado aprendido, incluidos escaladores, adaptadores y prototipos, se ajusta solo con las dos personas permitidas. No hay early stopping ni selección de checkpoint por el sujeto externo: se puntúa la época fija, 80 o 40 según receta.

El caché externo fijo puede calcularse previamente para los 1.125 clips train porque cada representación depende solo de su clip y de pesos externos inmutables. No permite PCA, normalización aprendida, elección de dimensiones o fine-tuning global antes de separar los folds. Test se excluye de todos los pasos de selección, incluidos cachés exploratorios y estadísticas sin etiquetas.

Primera semilla 17. Confirmación adicional 29/43 solo para un máximo de dos recetas. Se comparan todos los finalistas con las tres semillas únicamente si todos las completan; si falta cualquier ajuste requerido, comparación, ensemble y refit final usan solo 17 para todos. Los intentos parciales permanecen en el reporte. No escoger la mejor semilla.

Métricas: accuracy OOF de los 1.125 clips como objetivo; por persona, clase, vista, longitud y missingness para diagnóstico. Conservar confusiones, logits y errores pareados; macro-F1 es secundaria. Un acierto OOF equivale a 0,0889 puntos porcentuales; un acierto en 375 equivale a 0,2667. No son intervalos de confianza.

Orden de recetas individuales: accuracy OOF del promedio de probabilidades entre las semillas comunes admitidas; después mayor mínimo por persona, después menor costo total medido incluyendo extracción, después `variant_id` lexicográfico. No usar el promedio de accuracies como si fuera accuracy del ensemble.

Promoción de una ablación: al menos tres aciertos OOF adicionales frente a su padre y ninguna persona pierde más de tres; o estar a no más de tres aciertos del líder con costo total al menos 30% menor. Es una heurística de cómputo propuesta, no significancia estadística. Nunca ocultar una regresión por persona.

Pareja para ensemble: mejor receta de landmarks y mejor RGB. Si no hay RGB elegible, líder y mejor arquitectura distinta entre landmarks. Se evalúa esa única pareja con pesos 50/50, sin grid ni stacking. Promoverla si gana al menos tres aciertos al mejor componente y ninguna persona pierde más de uno. Esta misma regla se reaplica después de confirmar semillas. Promover a confirmación el líder y su pareja solo si la combinación pasa o la segunda receta está a no más de tres aciertos del líder. Si ninguna combinación pasa, se conserva el líder.

Cambiar familias, crops o features después de mirar OOF produce selección de desarrollo. Los tres sujetos no ofrecen una estimación poblacional independiente ni justifican intervalos estrechos tratando 1.125 clips como personas independientes. Las dos evaluaciones de la organización se rigen por §12: modelo fijado, sin adaptación según feedback, y cuenta la última según aclaración del usuario.

## 7. Catálogo ejecutable propuesto

Los IDs incluyen R2 para que una receta cambiada no se confunda con E00–E17 del diseño previo. El estado medido de R2-E01 está en [07 §8](07_results_and_publication_protocol.md); las demás filas siguen siendo catálogo propuesto, salvo el diagnóstico parcial del primer piloto. Esta tabla no autoriza por sí sola cada ejecución.

| ID | Pregunta / método | Máximo de ajustes completos | Puerta y decisión |
|---|---|---|---|
| R2-E00 | Contrato, integridad, pipeline y costo con train; hasta cuatro pilotos CPU breves y dos calibraciones GPU, la segunda solo para E11 | 0 | Resolver semántica antes de R1/R2/R3/ROI. Medir antes de comprometer tiempo o dinero. |
| R2-E01 | MLP R0, LOSO/17 | 3 | Baseline elegible sin anatomía asumida. |
| R2-E02 | TCN R1, LOSO/17 | 3 | Primera opción temporal si E00 valida esquema. |
| R2-E03 | Transformer R1, LOSO/17 | 3 | Misma entrada y política que E02; medir ganancia/costo. |
| R2-E04 | Mejor temporal del núcleo con R2 localshape | 3 | Tras núcleo; comparar con su padre, sin mezclar diferencias. |
| R2-E05 | Mismo padre temporal del núcleo con R3 deltas | 3 | Tras núcleo; no hereda simultáneamente R2. |
| R2-E06 | Mejor temporal elegible + SupCon | 3 | Padre completo y dos personas por fold; mismo muestreador. |
| R2-E07 | Extracción DINO global y, si cabe, ROI; caché fijo train | 0 | Peso/licencia, transferencia y presupuesto habilitados. Máximo dos vistas; ROI depende de E00. |
| R2-E08 | Pirámide RGB global + MLP, LOSO/17 | 3 | Primera referencia RGB. Escalado fold-local. |
| R2-E09 | TCN sobre el mismo RGB global, LOSO/17 | 3 | Compara cabezas con encoder, frames y crop idénticos. |
| R2-E10 | Mejor cabeza global de E08/E09 sobre ROI, LOSO/17 | 3 | Compara crop con arquitectura constante; sin buscar más recortes. |
| R2-E11 | Adaptador visual de la mejor receta RGB, LOSO/17 | 3 | RGB a ≤ 12 aciertos OOF del líder o pareja preliminar promovible; piloto demuestra costo completo y reserva. Abrir solo hasta el 22. |
| R2-E12 | Pareja preliminar 50/50 sobre OOF | 0 | Una pareja definida en §6; elegir hasta dos recetas para confirmar. |
| R2-E13 | Semillas 29/43 de hasta dos finalistas, tres folds cada una | 12 | Todos los finalistas comparten conjunto de semillas o se usa solo 17. |
| R2-E14 | Refit en 1.125 clips de hasta dos recetas, hasta tres semillas | 6 | Reajustar estados aprendidos con todo train; épocas fijas. |
| R2-E15 | Inferencia final por muestra, validación y entrega | 0 | Bundle congelado y reserva protegida; primer acceso experimental a payloads de test. |

Suma de máximos: nueve del núcleo + nueve de ablaciones landmark + nueve de cabezas/crop RGB + tres de adaptación + doce de confirmación + seis finales = **48**. Sin RGB ni adaptación, el máximo conservador es 36. La ruta mínima viable es núcleo más refit de una receta con semilla 17: diez ajustes, o menos si una receta queda técnicamente descartada antes de iniciar su comparación. Las extracciones no son ajustes, pero consumen dinero y tiempo; se contabilizan por separado.

Orden de trabajo: E00→E01/E02/E03; luego GPU E07 y CPU E04 en paralelo si cabe. E08 precede E09; E05/E06 se abren según horas restantes y evidencia. E10 y E11 no retrasan la confirmación. El 22 a las 18:00 Bogotá se cierran nuevas ramas; el 23 a las 12:00 se congela selección salvo incidencia técnica documentada que obligue a usar un candidato ya validado.

### Controles baratos dentro del catálogo

E00 permuta exclusivamente etiquetas de ajuste en una prueba breve y evalúa las reales del sujeto retenido. Es diagnóstico de fuga, no umbral de éxito ni candidata; las etiquetas externas no se permutan. Probar cobertura de IDs, semántica de máscaras, frame totalmente cero, duplicados dentro de persona y carga/reanudación. El esquema no se valida solo porque una red entrena.

E08 permite un control sin ajuste adicional: en las predicciones de desarrollo, invertir determinísticamente el orden temporal del embedding antes de agregar las dos mitades. Invertir puede cambiar el significado de la seña, por lo que una caída solo evidencia sensibilidad del modelo, no prueba comprensión lingüística. No elegir el sentido por su score. Comparar E08 con E09 cambia arquitectura y agregación; no es una prueba causal aislada del orden.

## 8. Piloto, límites de tiempo y criterio para pagar

E00 usa train. Para CPU medir dos épocas completas de un fold por arquitectura, descartar pesos y reiniciar los fits oficiales. Medir al menos diez pasos después de warm-up, I/O, RAM y evaluación, y probar batch final 60. Para GPU usar 30 clips, dos por cada estrato persona/clase, uno corto y uno largo según T; incluir decodificación, transferencia, ambas vistas si se solicitan y escritura/verificación del caché.

Extrapolación conservadora por ajuste: `1.5*(epocas*tiempo_epoca + evaluacion + escritura)`. Admitir recetas CPU si el ajuste externo proyectado no supera 60 minutos, el refit proyectado cabe y se cumple la admisión acumulada de 06: horas ya consumidas, incluidas pruebas/fallos, más pendientes comprometidas, nueva unidad con margen y reserva dentro de 48 horas-trabajo. Un timeout produce intento incompleto no comparable; no se puntúa una época anterior como si fuese la receta fija.

La cola también consume calendario. Máximo dos trabajos activos, con hasta dos pendientes; no llenar la cola con variantes no promovidas. Medir retraso real y anticipar la congelación si se pierde margen. Cada trabajo ejecuta un único ajuste y preserva checkpoint; ningún entrenamiento corre en la sesión SSH.

E07 requiere presupuesto proyectado de la cadena completa, no solo del forward. Si 16 frames con las vistas propuestas no caben, se permite una única degradación previa a resultados: K=8 para todas las recetas RGB, con nuevo esquema y horas recalculadas. Si aún no cabe, conservar solo global o cerrar RGB. La decisión y el motivo se registran antes de entrenar cabezas. No modificar resolución ni número de cuadros por fold.

E11 solo avanza si su costo incluye tres folds, el modo de confirmación elegido, refit e inferencia, más margen 1,5. Primero evaluar viabilidad de replay de prefijo; su almacenamiento adicional pertenece al costo. Si la adaptación solo cabe usando semilla 17, todos los finalistas se comparan y entrenan finalmente con 17; las otras semillas previas son evidencia adicional. El encoder congelado siempre conserva su candidatura.

Los precios y las reservas monetarias pertenecen a 06. Un piloto fallido no autoriza ampliar saldo. La revisión no promete completar 48 ajustes ni alcanzar un determinado score dentro de USD 10.

## 9. Caché, costo e inferencia reproducible

Con K=16 y D=384, una vista de train necesita `1125*16*384` valores: **26,37 MiB float32**, o 13,18 MiB float16. Se propone float32 para cabezas CPU. Dos vistas duplican esos tamaños; no son 36.000 clips, sino 36.000 forwards de imagen. El test final necesita 6.000 forwards para una vista. Solo se extraen las vistas que requiera el bundle elegido.

Los píxeles de entrada son mucho mayores: una vista uint8 de todos los frames de 224×224 ocupa 2,52 GiB antes de compresión; dos vistas 5,05 GiB. No asumir que transferir videos o frames cuesta lo mismo que transferir embeddings. Preparar en Cronos/local solo los frames necesarios con compresión sin pérdida, registrar bytes reales y probar el decoder. No depender de `ffmpeg` de sistema, ausente en el PATH inspeccionado, sin probar antes OpenCV u otra dependencia autorizada.

Los tokens float32 antes del último bloque tienen 257 tokens por frame, D=384. Una vista train ocupa aproximadamente 6,62 GiB, aparte de metadatos; su caché es exclusivo de E11 y nunca obligatorio para E08/E09. Leer por clip o shard con mmap/streaming, sin cargarlo entero en el límite local. La extracción de todos los tokens por defecto sería una deuda injustificada.

Encoder estándar, prefijo y transformaciones deterministas pueden compartirse entre folds. Adaptadores, cabezas y escaladores no. Un modelo adaptado requiere su propio checkpoint por fold/semilla; no se reutilizan sus embeddings como features externas universales.

La inferencia final es individual y estable al orden/lote. Nunca recalcula estadísticas del test ni hace aprendizaje transductivo, pseudoetiquetado o ajuste con el balance declarado. Se mide con clips train una ruta CPU o GTX 1650 del bundle completo antes de congelar; su extrapolación a 375 muestras debe caber antes de la entrega. Si falla, reservar GPU final o elegir un candidato ya validado que sí pueda ejecutarse.

## 10. Qué conserva y qué cambia frente al diseño anterior

Se conservan requisitos, auditoría, separación LOSO, tres semillas posibles, integridad del test, trazabilidad y reglas de promoción. Cambian el reparto de cómputo, la representación local de manos, el catálogo y la ejecución RGB por caché explícito. Los IDs antiguos no reciben resultados nuevos. La antigua ruta de 84 ajustes queda sustituida; el refinamiento interno V2 y SSL local dejan de ser ramas presupuestadas.

El catálogo hace trade-offs explícitos: menos investigación desde cero; más reutilización de pesos y comparación de representaciones; una única adaptación condicionada; publicación científica posterior a la entrega. Los resultados OOF siguen siendo de desarrollo. Una mejora en otra lengua, un modelo más grande o disponer de USD 10 no garantizan ganar ni publicar.

La decisión humana solicitada es aprobar esta ruta y sus límites, incluida la precisión estratégica R2.1. Después se revisa la fundación reconciliada en 05/06 y el primer ítem de implementación. La selección de proveedor, el mecanismo de uso de su cuenta, una transacción y la transferencia de datos conservan sus autorizaciones propias.

## 11. Mejora continua y escalamiento por evidencia

El objetivo es aumentar la probabilidad de transferir a una cuarta persona. No se puede garantizar el puesto ni una mejora monótona en esa persona; LOSO es evidencia de desarrollo y solo hay tres personas públicas. El catálogo es un árbol de decisiones acotado, no una búsqueda exhaustiva. Mantener un campeón local restaurable; los descartes conservan sus artefactos y costo.

**Ciclo de una ola:** cerrar OOF completo → analizar errores train → formular una hipótesis → admitir una variante del catálogo según presupuesto/plazo → compararla con el padre y campeón → promover, descartar o declarar inconclusa → actualizar selección y costos. Ejecutar como máximo dos trabajos CPU simultáneos, una GPU externa y una hipótesis nueva por rama. No confundir dos slots con autorización para lanzar dos búsquedas sin límite.

Cada intento conserva en sus artefactos existentes: hipótesis/receta padre; diagnóstico previo; cambio único o factores que cambian juntos; umbral de §6; proyección de toda la cadena; resultado por persona/clase; aciertos ganados y perdidos frente al padre; costo y decisión. `selection.json` referencia estos resultados. No crear un diario paralelo ni cambiar el umbral al ver la métrica.

| Evidencia en train/OOF | Próxima acción del catálogo | Qué no demuestra / condición de cierre |
|---|---|---|
| Error de esquema, padding, correspondencia frames o carga | Resolver E00/W00–W02 y repetir solo lo invalidado. | Más capacidad no corrige un contrato erróneo; esos intentos siguen contando en costo. |
| Modelos landmarks débiles donde faltan detecciones | Priorizar extracción fija E07 y referencia global E08, sin esperar que fallen todas las ablaciones CPU. | La ausencia observada no prueba la causa. RGB requiere sus tres folds; no mirar test. |
| Gran diferencia entre ajuste y sujeto retenido, o una persona concentra errores | Contrastar normalización/forma local E04 y SupCon E06 si están admitidos. | El diagnóstico no autoriza retocar estadísticas con el sujeto retenido ni crear variantes ilimitadas. |
| RGB global útil y señales de dependencia de encuadre/apariencia | Contrastar ROI E10 con la misma cabeza, tras verificar coordenadas. | Una mejora de crop es evidencia de receta, no prueba causal de eliminación de sesgos. |
| Cabeza RGB temporal supera la referencia de pooling | Conservar E09 y considerar E11 si cumple todas sus puertas. | Cambian arquitectura y tratamiento temporal; no atribuir causalidad solo al orden. |
| RGB y landmarks corrigen errores distintos | Evaluar la única pareja 50/50 de §6. Contar `ganados = B correcto/A incorrecto` y `perdidos = A correcto/B incorrecto`. | La unión de aciertos es un techo diagnóstico inalcanzable sin conocer etiquetas; no es un selector desplegable. |
| Una variante no alcanza promoción, se interrumpe o solo funciona en un fold | Descartar o declarar incompleta, conservar campeón y pasar a otra hipótesis admitida. | No rescatar la variante eligiendo semilla, época o subconjunto favorable. |

La referencia trivial 20% contextualiza el problema; no es criterio para activar modelos caros. Tampoco se exige un porcentaje arbitrario de accuracy para considerar RGB: E07/E08 recuperan una modalidad complementaria y entran temprano si son viables.

**Escalera GPU y puertas obligatorias:**

1. **Extracción congelada, E07/E08.** Peso/API/licencia y transferencia acreditados; pipeline probado; piloto proyecta extracción, almacenamiento y finalización dentro de 06. Es la primera inversión GPU por reutilización entre folds y semillas.
2. **Mejor uso del mismo encoder, E09/E10.** Comparar cabeza temporal y ROI, conservando factores compartidos. Son cambios de representación/cabeza; todavía no se actualiza el encoder visual.
3. **Adaptación residual, E11.** Abrir solo si el mejor RGB está a no más de 12 aciertos OOF del líder —1,07 puntos porcentuales— o su pareja 50/50 ya es promovible. Además deben pasar replay, permisos, almacenamiento, cadena completa folds/confirmación/refit/inferencia con margen 1,5, reserva protegida y corte del 22. Este requisito de proximidad es una heurística de prioridad, no una probabilidad de éxito. El adaptador también debe superar las reglas de promoción de §6; pasar la puerta no lo convierte en ganador.
4. **Otra familia o fine-tuning más amplio.** SignRep, una GCN nueva o actualizar muchas capas no son extensiones automáticas de E11. Requieren diagnosticar por qué las representaciones actuales fallan, verificar peso/licencia y cotizar un experimento comparable de tres folds más finalización. Si amerita reabrir la ruta, sustituir una rama aún no ejecutada y reconciliar presupuesto/IDs/revisión; los intentos ya realizados no desaparecen. Sin esa revisión, quedan aplazados.

Las confirmaciones de semillas se abren después de disponer de candidatos útiles, sin gastar primero la reserva en estabilidad de una baseline débil. Los finalistas conservan el conjunto común de §6. Se reduce el catálogo si el piloto/cola lo exige; no se reduce el protocolo por persona para aparentar avance. El mejor OOF de desarrollo no se convierte en estimación imparcial por confirmar semillas.

Cerrar exploración al alcanzar cualquiera de estos límites: corte del 22, falta de presupuesto acumulado para una unidad completa más finalización, o ausencia de hipótesis admitida con evidencia nueva. Un resultado negativo no genera automáticamente otra prueba. Desde el freeze del 23, solo restauración, refit fijado e inferencia, más la recuperación técnica permitida en §12: defecto reproducible con contratos/train, revalidación de pasos afectados y nueva versión congelada con trazabilidad. Esa excepción no abre búsqueda ni usa el score como evidencia. Más dinero o un puesto observado en la página no reabren ramas.

## 12. Dos evaluaciones externas: cuenta la última

**Información del usuario, 19 nov:** existen dos oportunidades y se evalúa la última; desconoce el feedback. Falta confirmar ventanas, latencia, si rechazos técnicos consumen intento y detalles de desempate. No se pudo revalidar la página pública en esta actualización. El manual, §8.3, prohíbe modificar modelos en función de la retroalimentación del test. Dos oportunidades no revocan esa regla ni garantizan conservar el primer resultado.

La política recomendada es **un envío competitivo y una oportunidad de recuperación**, con el modelo elegido exclusivamente mediante train/OOF. No se envía una baseline provisional para obtener pistas, un challenger más débil por diversidad o dos modelos para escoger el de mayor puntuación privada. Se permite no consumir la segunda oportunidad.

- **Antes de evaluar:** cerrar candidatos y semillas con §6; seleccionar modelo/ensemble; refit con todo train; restaurar bundle en otro proceso; congelar versión y reglas de predicción. Inferir test individualmente, validar CSV, cobertura y hashes. Un CSV válido no prueba accuracy; una accuracy desconocida no impide comprobar su integridad.
- **Evaluación 1:** usar el mejor bundle elegible elegido localmente. Registrar envío, hash exacto, versión del modelo y respuesta. Priorizar acuse/aceptación técnica; no utilizar score, ranking, fallos por clase o etiquetas que pudiera mostrar la página para modificar pesos, selección o predicciones. Si es posible, separar la recepción del estado técnico de la inspección de la métrica; no se presupone que la interfaz lo permita.
- **Evaluación 2:** reservarla para rechazo de archivo, carga errónea o defecto técnico demostrado con contratos y train, con corrección admitida por las bases y sin usar la puntuación como señal. Ejemplos: delimitador incorrecto, fila/ID omitido o archivo cargado distinto al congelado. Verificar nuevamente y vincular corrección al original. Si ambos envíos fueron técnicamente correctos, no hay motivo automático para reenviar. Una puntuación baja por sí sola no demuestra un bug ni habilita cambiar arquitectura, clase, umbral o ensemble.
- **Cambio legítimo pendiente antes del primer envío:** si se desea comparar otro candidato, hacerlo y terminar su decisión local antes de evaluar; reajustar el calendario conservando margen de recuperación. No usar el primer envío como señal para decidir qué rama entrenar después. Una excepción organizativa explícita debe reconciliarse con el manual y revisarse antes de actuar.

Una puntuación que empeore tras el segundo envío no tiene rollback garantizado. El modelo/código/reporte entregados deben corresponder al último CSV aceptado según la política organizativa; guardar el primero sirve para trazabilidad, no acredita que siga puntuando. Ventanas y ejecución operativa pertenecen a 06. No se presenta ningún envío sin autorización para esa acción externa.


## 13. Adaptación propuesta R2.2 · temporal opaca sin extractor

**Estado: adaptación R2.2 aprobada el19 nov2026; conserva R2.1 salvo los cambios explícitos de esta sección.** El equipo confirmó que solo dispone del manual y los datos. Obtener detalles de los organizadores puede tardar días; no hay plazo de respuesta acreditado. La investigación del contrato concluyó sin acreditar R1 (05 §12). Esto cambia la viabilidad de E02, no valida retrospectivamente su anatomía.

| Alternativa | Ventaja | Límite y decisión propuesta |
|---|---|---|
| Esperar especificación y conservar E02/R1 | Permite aplicar geometría/lateralidad acreditadas. | Dependencia sin fecha. Mantener disponible sin detener todo avance. |
| R2-E02O, TCN de columnas opacas | Recupera secuencia sin atribuir nombres anatómicos a columnas; usa Cronos. | Más canales y sensibilidad a persona/cámara; necesita piloto. Recomendada para la siguiente comparación CPU. |
| RGB global E07/E08 | Ruta visual ya diseñada e independiente del layout NPY. | Requiere habilitar servicio/transferencia, pesos y costo completo. Sigue como opción complementaria, con sus autorizaciones propias. |

**Hipótesis prospectiva:** secuencias numéricas opacas más TCN pueden mejorar el OOF de R0/MLP. Cambian representación y arquitectura conjuntamente; una diferencia no identifica por sí sola el efecto causal del orden temporal o de la normalización anatómica. El resultado previo de R0 y sus errores no se usan para escoger columnas, subconjuntos o épocas.

**Representación propuesta `opaque_sequence_v1`.** Conservar todas las1662 columnas en su orden original y T nativo. Validar float64 finito como en R0. Ajustar media/desviación poblacional por columna sobre TODOS los frames reales de los750 clips de ajuste, acumulando en float64 y guardando parámetros float32; ponderación por frame, no por clip. Desviación menor que1e-6→1. Transformar cada frame y convertir a float32. No usar frames retenidos, padding, IDs, cámaras o etiquetas para calcular ese estado. No asumir bloques, XY, visibilidad, lateralidad o causa de ceros. Un frame original totalmente cero sigue siendo observación real y participa del escalado; después del escalado puede ser no cero. Padding se añade después y tiene máscara temporal falsa; no existe máscara anatómica. No interpolar, remuestrear ni eliminar frames.

**Receta propuesta `opaque_tcn_v1`.** Proyección lineal1662→64; tres bloques residuales. Cada rama: Conv1D64→64,k5,dilatación1/2/4,padding simétrico2d → LayerNorm sobre64 canales de cada frame → GELU → dropout0,2. Sumar entrada residual. Neutralizar padding después de proyección y después de cada suma residual, antes de alimentar otra convolución. Media temporal enmascarada→lineal64→5. Sin BatchNorm ni features de longitud. Atención causal no requerida para clasificar clips completos. Arquitectura local propuesta, sin afirmar réplica de un paper. Optimización y muestreo de05/§5: AdamW LR1e-3/WD1e-3,CE,clip gradiente1,80 épocas,cinco de warmup/cosine hasta1%,semilla17,batch40/remanente30. No early stopping ni validación intermedia.

**Prueba y decisión.** Piloto técnico de dos épocas sobre M02, distinto de candidato: comprobar al menos10 pasos tras cinco de calentamiento de medición, memoria, I/O, batch60 en copia descartada fit-only y restauración desde originales. Estimar cadena completa con margen1,5 antes de admitir tres folds. Si no cabe en recursos/plazos/reservas, cerrar la rama sin reducir longitud/batch/épocas silenciosamente. Después tres LOSO completos,750/375 por fold, cobertura1125, receta fija. Comparación pareada frente a R2-E01: conservar aciertos ganados/perdidos por persona, confusion y costo; promoción según§6 (≥3 aciertos adicionales y ninguna persona pierde>3, o alternativa económica definida allí). No elegir otro checkpoint por el resultado. Confirmaciones/refit solo mediante las reglas existentes y alcance posterior.

**Catálogo y presupuesto propuestos.** E02O sustituye la ejecución de E02 en esta ola: tres ajustes completos, no una adición sobre sus tres slots. E02/R1 sigue sin ejecutarse; si después se habilita, reconciliar catálogo y presupuesto antes de admitirla. E03/R1,E04/E05 y ROI siguen condicionadas a esquema; no heredan representación opaca automáticamente. Máximo global48 ajustes,48 horas-trabajo CPU con12 reservadas,USD10 de caja intactos. Este incremento propone hasta1 hora-trabajo: piloto Slurm4CPU/8GiB/5min con reserva360s; cada fold4CPU/8GiB/15min con reserva960s. Suma de reservas3240s, verificando por separado duración estimada*1,5≤TimeLimit (300s piloto,900s fold) y TimeLimit+KillWait≤reserva, con KillWait≤60s; si falla alguna condición, no admitir. La gracia de terminación no es tiempo disponible para completar entrenamiento. Máximo dos jobs simultáneos. Registrar preparación local/transferencias por separado; tiempos del MLP no estiman la nueva TCN. Sin GPU, cuentas nuevas, pago, test, refit final o envíos.

Una solicitud del extractor puede avanzar por el equipo en paralelo; no se contactó a organizadores desde el proyecto. Información mínima solicitada: concatenación/orden intrapunto, salidas y versión/configuración MediaPipe, unidades, espejo y relleno de detecciones ausentes. No afirmar que esa consulta vaya a resolverse antes del cierre.


Resultado de R2.2/E02O,20 nov: receta completa ejecutada según este protocolo y no promovida frente a R2-E01. Métricas/comparación e interpretación autoritativas en [07 §9](07_results_and_publication_protocol.md); costos/admisión en [06 §10](06_delivery_and_iteration_plan.md). No se modifican retrospectivamente receta, umbral, semillas o slots por este resultado.


## 14. Piloto RGB global local aprobado

El usuario aprobó el20 nov la implementación y un único piloto local posterior a E02O. El alcance resuelve primero si la GTX1650 local ejecuta R4 congelada con integridad, memoria y duración aceptables; no medir aún accuracy ni abrir E08. La alternativa Colab mantiene cuota/acceso inciertos y requiere acordar mecanismo de cuenta; un proveedor pagado requiere elección/pago/transferencia explícitos. La opción local prioriza costo y evita transferir videos, sin asumir que4GiB bastan antes de medir.

Comprobación de solo lectura del20 nov: GTX1650 con4096MiB y3935MiB libres al consultar, controlador610.91. El entorno existente tiene PyTorch2.4.1+cpu, sin CUDA; no es evidencia de incompatibilidad de la GPU. RAM disponible observada2225MiB, variable; disco libre aprox.870GiB. FFmpeg/ffprobe4.4.2 y Pillow11.3.0 locales disponibles. Treinta videos train seleccionados antes de ejecutar modelo —mínimo/máximo `(T_landmark,ID)` por persona/clase— coinciden con sus hashes, son1920×1080 y tienen33–97 frames; en estos30, el conteo de video coincide con T de NPY. No generalizar esa igualdad al resto: el extractor usará N del video. Total187472255bytes, inspección24,34s; no hubo acceso a test.

**Contrato conservado.** DINOv2 ViT-S/14 sin registros, K16, letterbox224 del frame completo, RGB/valores ImageNet, salida `x_norm_clstoken` de384 componentes float32. En el código oficial “norm” corresponde a LayerNorm final; no agregar normalización L2 ni ajustar estadísticas del dataset durante extracción. No ROI, aumentos, pesos adaptados o cambios por accuracy. Versiones/decoder/padding exactos y tolerancia en05 §14; criterios ejecutables del piloto en su propuesta.

**Decisión al terminar.** Un piloto conforme permite proponer extracción global train completa y E08, con costo de cabezas/refit/restauración aún por medir; no los autoriza automáticamente ni acredita la cadena completa. Si K16 no cabe por costo/memoria, documentar fallo y una propuesta de la degradación K8 ya prevista antes de cualquier score; no cambiarla silenciosamente ni probar variantes ilimitadas. Colab o pago solo tras resolver sus puertas. No extrapolar tiempos de otros equipos ni prometer mejora sobre60,98%.


**Resultado del primer piloto,20 nov2026:** extracción30 conforme, replay en proceso nuevo fallido por OOM al inicializar CUDA. No se supera la puerta de reproducibilidad y no se admite E07/E08. No se probó K8 ni otra precisión; la causa raíz permanece desconocida. Resultados e interpretación en [07 §10](07_results_and_publication_protocol.md), contabilidad en06 §11. Próxima propuesta: diagnóstico acotado de inicialización/estabilidad antes de una nueva ejecución aprobada; este resultado no amplía el alcance.


**Actualización tras reintento solicitado explícitamente,20 nov:** segundo piloto completo y replay conformes, conservando el fallo original y sin cambiar protocolo. Se habilita proponer E07 global/E08 bajo sus puertas de costo completo, no ejecutarlos automáticamente. Resultado autoritativo en [07 §11](07_results_and_publication_protocol.md); contabilidad en06 §12. No modifica recetas, semillas, umbrales de promoción o la reserva de dos evaluaciones.


## 15. Alcance aprobado E07 global/E08

El usuario aprobó el siguiente alcance tras el reintento conforme: caché global1125 y `rgb_pyramid_mlp_v2`, tresLOSO750/375,80épocas/semilla17. Conserva R4/optimización/umbrales existentes, ROI bloqueada y sin E09/E12/E13/refit/test. El piloto CPU de2épocas debe completar gate de costo/restauración antes de tres fits; la extracción tiene presupuesto de cadena conservador previo, no se presenta como medición de cabeza. [Ítem/AC V1–V6](../openspec/changes/archive/2026-11-20-rgb-global-loso/proposal.md); contratos05 §16 y límites06 §13. Se admite optimizar transporte de frames solo con equivalencia de píxeles verificada y sin cambiar representación. No abrir otra receta si los resultados no mejoran.


## 16. Decisión E12 en recuperación y opción pendiente

El20nov se aplicó la regla de pareja de§6 sin modificarla; las cifras están en07 §12. Ninguna pareja se promueve y E11 permanece cerrado, de modo que el finalista único es E01. La confirmación E13 (semillas29/43) y el refit E14 se proponen en el [ítem de entrega](../openspec/changes/archive/2026-11-20-e01-delivery-path/proposal.md).

**Opción B, pendiente de decisión humana y no recomendada por defecto.** E01+E08 gana en dos de tres personas (+19/+19) y pierde12 en M03: +2,3 puntos porcentuales OOF de media. Es la única señal de mejora observada sobre60,98%, pero la regla que lo impide fue fijada antes de ver los datos. Relajarla ahora sería un cambio posterior a observar el resultado y sesgaría la estimación. Si el usuario lo decide explícitamente, se exigiría además:

1. Una restauración RGB nueva con contrato de compatibilidad entre los modelos del productor ejecutado y el supervisor corregido.
2. Un camino de inferencia DINOv2 para375 videos test dentro del bundle.
3. Las semillas comunes de ambas recetas, o solo la semilla17.
4. Terminar antes del corte del22nov18:00.

Sin esa decisión, la regla vigente se conserva.


## 17. Flexibilización del protocolo interno y objetivo80%

**Decisión del usuario, 20nov2026:** priorizar el acercamiento al80% LOSO sobre la rigidez del protocolo interno.

**Qué pasa a ser orientativo.** Las reglas internas de promoción y pareja de§6, los cortes del22 y del23 de06 §5, el principio de una hipótesis por rama y el bloqueo documental de R1. Cada desviación se registra con su motivo y se marca como posterior a observar el resultado cuando lo sea, porque afecta la interpretación del OOF.

**Qué no cambia.** Las reglas del reto y la integridad de evaluación de01:

- Test se usa solo para inferencia de un modelo fijado.
- No hay ajuste con feedback de test.
- No se usan etiquetas, nombres de archivo ni metadatos como features.
- Se respetan las reglas del servidor.
- Se usa LOSO con estado aprendido fit-only.

**Criterio práctico de promoción.** Ganancia OOF ≥3 aciertos frente al campeón y media por persona positiva. Las regresiones por persona siempre se reportan y se consideran en la decisión. La opción B de§16 (E01+E08) queda admisible como candidata. Diagnósticos y candidatas propuestos en el [ítem de diagnóstico](../openspec/changes/archive/2026-11-20-accuracy-diagnostics/proposal.md).


## 18. Consecuencias de X1–X3/X7 y siguiente ola

Resultados en07 §13. R1 queda acreditada empíricamente, así que se reactivan R1/R2/R3, la TCN y ROI con las unidades y la lateralidad verificadas. Ítems propuestos, en orden de valor esperado:

| Ítem | Hipótesis y cambio | Criterio |
|---|---|---|
| **X8 · lateralidad canónica** | Por clip, sin etiqueta, se detecta la mano activa (elevación de muñeca). Si es la izquierda, se aplica espejo `x→1−x` con intercambio de bloques izquierda/derecha y de los puntos pares de pose. Es una transformación determinista por muestra, válida también en inferencia. Se combina con espejo aleatorio como aumento en entrenamiento. Se aplica primero sobre R0/MLP, cambiando solo esto. | Ganancia OOF y por persona frente al promedio de semillas (676), con especial atención a M02. |
| **X4 · normalización corporal** | Coordenadas centradas en el punto medio de hombros y escaladas por su anchura; manos relativas a la muñeca (R1/R2 de§4). Elimina encuadre y posición por sesión. | Igual. |
| **X6 · secuencia** | `compact_tcn_v2` sobre R1/R2 canónicas con recorte del segmento activo y aumentos de escala/rotación/velocidad. | Igual; candidata. |
| **X5 · RGB de manos** | DINOv2 sobre recortes de mano desde1080p, guiados por landmarks acreditados. | ≥10 puntos sobre el global en un subconjunto. |
| **X9 · reextracción de landmarks** | MediaPipe con complejidad2 o sobre recortes de mitad superior a mayor resolución, para reducir el37% de frames sin manos. Se mide primero la tasa de detección en los30 clips de X1. | Menos frames sin manos y ganancia OOF. |

Cada ítem compara también con la mejor variante anterior; se usa la promoción flexibilizada de§17.


## 19. Candidato de entrega tras la ola

Resultados en07 §14. **Candidato:** X4+X6 al 50/50 sobre landmarks normalizados con lateralidad canónica, 93,87% LOSO de desarrollo. Supera ampliamente a E01 y al objetivo del80%. El bundle de E01 se conserva como respaldo técnico.

RGB de manos (X5) y una tercera receta quedan aplazados: su valor esperado es bajo frente al riesgo de calendario. Mejoras posibles si se reabre exploración antes del freeze: separar sign_02, sign_04 y sign_05 (rasgos de movimiento o forma local) y añadir RGB de manos con extracción completa.

**Siguiente paso operativo:** freeze de `bundle_x4x6_v1`, inferencia test autorizada, validación del CSV y evaluación1 según la política de§12. Requiere autorización explícita.
