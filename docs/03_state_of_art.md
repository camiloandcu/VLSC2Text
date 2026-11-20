# Estado del arte y transferencia a LSC5: 2022–2027

Consulta amplia: 2026-11-10. Encargo: investigación amplia y profunda para el siguiente agente; no selección definitiva de solución, diseño experimental o implementación. Contexto vinculante: [definición del problema](01_problem_definition.md). Índice, método y fuentes: [literature/README.md](../literature/README.md).

Actualización focal del 19 de noviembre: recursos Cronos comprobados en [08](08_compute_operations.md), contraste de métodos/pesos para el nuevo límite de cómputo en [04 R2](04_solution_and_experiment_design.md) y precios/condiciones en [06](06_delivery_and_iteration_plan.md). Esa actualización no constituye una nueva búsqueda exhaustiva ni cambia las fechas de corte de la biblioteca.

## 1. Resultado principal

El campo ofrece tres líneas directamente relevantes: reconocimiento especializado en señas con manos/cuerpo/rostro; reconocimiento de acciones mediante esqueletos; y transferencia de representaciones visuales o temporales preentrenadas. Su relevancia para LSC5 depende de la señal que conserven, la separación entre personas, los artefactos realmente disponibles y el costo de adaptación.

La literatura revisada no identifica un ganador demostrado para LSC5. La evidencia de un vocabulario grande en otra lengua o de acciones corporales en NTU no acredita accuracy sobre estas cinco señas de una persona retenida. La prioridad competitiva hace especialmente importante esa distinción: un resultado alto con sujetos compartidos puede ser menos informativo que una mejora modesta bajo separación real entre personas.

La [tabla priorizada](../literature/01_priority_table.md) reúne los recursos; [resources.csv](../literature/resources.csv) conserva sus fichas completas. Cada fila incluye contribución, evidencia, ventajas, limitaciones, modalidad, costo cualitativo, código/pesos/licencia y notas de transferencia. Las prioridades ordenan lectura y evaluación técnica posterior; no representan una arquitectura elegida.

## 2. Qué cubre el intervalo solicitado

Se buscaron trabajos publicados entre 2022 y 2026 y anuncios o publicaciones anticipadas rotuladas 2027 que fueran visibles al corte. Un volumen de revista o congreso 2027 puede anunciarse antes de ese año; ese rótulo no demuestra disponibilidad de artículo completo, código o evaluación independiente.

Los anuncios 2027 se distinguen de los recursos con artículo, preprint o herramienta disponibles y no sirven para inflar ese mínimo de 50. Disponibilidad no equivale a revisión por pares. La revisión no pretende conocer publicaciones que aparezcan después del 10 de noviembre de 2026. El año del índice es el de publicación verificada, o el año del preprint cuando no hay publicación confirmada; cuando una publicación 2022 tiene preprint de 2021 se explica en la ficha.

Hay dos casos concretos: [SignSeek](https://arxiv.org/abs/2609.03695) ya dispone de preprint de septiembre de 2026, aunque sus autores anuncian WACV 2027; se cuenta una vez como recurso 2026. [CSLR-XL](https://cogvis-cvssp.github.io/papers/cslrxl/) ofrece un anuncio de resultados rotulado WACV 2027 y mantiene artículo/código pendientes; se registra aparte. El anuncio autoral de una sede futura no equivale a verificar su programa definitivo.

Es una revisión de alcance orientada a decisiones, con profundización selectiva en métodos, resultados y limitaciones. Todas las entradas requieren una fuente primaria abierta; algunas disponen de revisión de secciones del texto completo y otras de resumen original más repositorio. No se afirma lectura integral de todos los artículos ni reproducción de sus resultados. La profundidad y los bloqueos de acceso constan en las notas de cada recurso.

## 3. Cómo interpretar los resultados publicados

| Distinción | Consecuencia para este reto |
|---|---|
| ISLR: seña aislada / CSLR: secuencia de glosas / SLT: traducción | Accuracy de un clip no es WER de una secuencia ni BLEU de una traducción. La transferencia de un encoder puede ser interesante sin que la tarea completa sea comparable. |
| Per-instance / per-class | Promedio por instancia y promedio por clase son distintos cuando las clases no están balanceadas. Conservar la definición original. |
| Top-1 / top-5 / retrieval Recall@K | El reto exige una única etiqueta. Recuperar una entrada entre varios candidatos mide otra decisión. |
| Cross-subject / cross-view / cross-dataset | Cambiar vista, persona o dataset evalúa variaciones diferentes. Revisar qué factores siguen compartidos. |
| Finetuning / linear probe / zero-shot feature extraction | Un encoder congelado con clasificador ajustado usando etiquetas de train no es clasificación sin ejemplos de la tarea. |
| Una red / varias modalidades / varios streams / ensemble | La cifra final puede acumular varios modelos, aumentos y vistas de inferencia. No atribuirla a una sola red ligera. |
| Etiquetas escasas / datos totales escasos | Un resultado con 1% de etiquetas puede aprovechar mucho dato no etiquetado. LSC5 permite aprender solo de los sujetos públicos. |
| Código / checkpoint / reproducción | Repositorio visible, pesos publicados y ejecución reproducida son tres evidencias distintas. Aquí se verificaron fuentes; no se ejecutaron modelos. |

El registro preserva dataset, protocolo y métrica cuando se cita una cifra; las filas no forman un ranking común de accuracy. El criterio práctico de lectura es la cercanía a los 1.125 clips, tres sujetos y representación MediaPipe del reto, más la solidez de los artefactos.

## 4. Evolución observada

| Periodo | Desarrollo relevante | Qué queda sin demostrar para LSC5 |
|---|---|---|
| 2022 | Modelos de pose y herramientas de señas; GCN/Transformers para acciones; CNN sobre mapas de pose; SSL temporal y regularización entre dominios. | Que un prior de acciones generales preserve detalles de dedos y rostro. |
| 2023 | Preentrenamiento especializado de manos, refinamiento contrastivo, jerarquías de articulaciones y adaptación eficiente de modelos visuales. | Que las mejoras sobrevivan al cambio de esquema anatómico y al reducido número de personas. |
| 2024 | Particiones de atención para esqueletos, alineamiento pose-texto, aprendizaje enmascarado y modelos temporales reutilizables. | Que la alineación semántica de otra lengua o sensor sea directamente válida para LSC. |
| 2025 | Representaciones más especializadas en señas, modelos de prototipos/movimiento y escalamiento de pretraining visual. | Disponibilidad de pesos útiles, derechos y costo de adaptación bajo cómputo compartido. |
| 2026 | Métodos compactos sobre landmarks y nuevas familias temporales preentrenadas con datos sintéticos; versiones recientes de modelos visuales. | Reproducción externa y ventaja local frente a métodos más maduros. |
| 2027 anunciado | Resultados o proyectos con fecha bibliográfica futura, diferenciados en el índice. | La literatura del año completo y los artefactos todavía prometidos. |

La evolución no es un reemplazo lineal por modelos cada vez mayores: siguen apareciendo encoders compactos y mejoras en representación, entrenamiento y protocolos. Esa es una observación del conjunto revisado, no un teorema sobre el mejor tamaño de red.

## 5. Familias directamente relacionadas

### Señales especializadas en señas

SPOTER, OpenHands y trabajos posteriores permiten estudiar secuencias anatómicas con un sesgo más cercano a la tarea que los clasificadores de imágenes generales. SignBERT+, BEST, DSTA-SLR, Siformer, SignRep y los recursos más recientes exploran representación de manos, fusión, reconstrucción, pretraining o relaciones entre partes. Las variantes exactas y sus fuentes están separadas en el índice.

La ventaja contextual es concentrar la capacidad en el movimiento lingüísticamente útil. El límite es que cada extractor define articulaciones, dimensiones y confiabilidad diferentes: un resultado con MMPose/COCO WholeBody no se transfiere por renombrar un array MediaPipe. La lateralidad, los puntos ausentes y el orden de concatenación todavía requieren el contrato pendiente de la etapa 1.

Dos recursos cercanos ilustran el balance entre evidencia y transferencia. El estudio de [reconstrucción y anclas para MediaPipe](https://aclanthology.org/2024.signlang-1.36.pdf), Tablas 3–4 y §5, informa 83,26% top-1 en WLASL100, pero no supera todos los comparadores en AUTSL-100. Su beneficio depende de las condiciones de detección; es especialmente pertinente para interpretar los bloques cero observados, sin demostrar todavía cómo tratarlos en LSC5. [PoET](https://www.scitepress.org/Papers/2026/142375/142375.pdf), Tabla 3, informa 459 mil parámetros y 74,25% top-1 por instancia en WLASL300. Ese tamaño lo hace interesante como lectura sobre eficiencia; no mide su memoria ni tiempo en nuestro entorno.

SignCLIP, SHuBERT y modelos visuales de señas amplían la transferencia mediante pretraining. Para LSC5 interesa la representación aprendida; una etiqueta española como “Aromática” no establece equivalencia de forma con “tea” en ASL u otra lengua. Los modelos de traducción o búsqueda no se consideran clasificadores de las cinco clases ya listos para usar.

SignSeek es especialmente pertinente como lectura reciente: vincula muestras de la misma glosa entre señantes y modela articuladores enmascarados. Su entrada de pose 2D con confianza difiere de las coordenadas almacenadas por LSC5 y sus artefactos aún no están acreditados. Su resultado de búsqueda entre corpus se conserva separado de su clasificación aislada con ajuste; no se equipara Recall@1 con la accuracy de la competencia.

### Esqueletos y reconocimiento de acciones

InfoGCN, EfficientGCN, HD-GCN, Hyperformer, SkateFormer, BlockGCN y ProtoGCN aportan estructuras y mecanismos para representar relaciones espaciales y temporales. MAMP, MotionBERT y otros recursos de SSL permiten estudiar priors de movimiento. FRHead resulta relevante como ejemplo de un cambio de entrenamiento cuyo efecto no implica necesariamente costo adicional de inferencia.

La limitación central es anatómica: los benchmarks corporales suelen usar decenas de articulaciones, mientras que LSC5 contiene cientos de puntos, principalmente faciales. Aumentar el número de nodos modifica significado, conectividad y costo. Por ello, una implementación NTU no es intercambiable con los 543 puntos de Holistic. Los resultados con múltiples streams tampoco describen el costo de una configuración individual.

PoseC3D ofrece otra representación: mapas de calor de pose en lugar de operar únicamente sobre una lista de coordenadas. Esto permite estudiar tolerancia al error espacial, con un costo denso de memoria que debe distinguirse del costo de una GCN. La presencia de landmarks preextraídos no obliga a que todas sus dimensiones sean entradas semánticamente compatibles.

### Video RGB y transferencia eficiente

VideoMAE, VideoMAEv2, UniFormer, VideoMamba, InternVideo y V-JEPA cubren aprendizaje visual temporal de distintas escalas. DINOv2/v3 son referencias de representación espacial que requieren un mecanismo temporal para describir un clip. VideoPrism aporta representaciones visuales generalistas. El índice separa versiones con contribuciones sustantivas y conserva la fecha de disponibilidad de checkpoints cuando difiere de la del artículo.

AIM, ST-Adapter, AdaptFormer y otros métodos de adaptación eficiente reducen parámetros entrenables o reutilizan un backbone. Eso puede reducir memoria del optimizador y costo de aprendizaje, pero no elimina el costo de cargar y ejecutar el backbone, procesar cuadros o usar varios crops. “Pocos parámetros entrenables” no basta para afirmar compatibilidad con la GTX 1650 de 4 GiB.

Los modelos visuales pueden conservar detalles que los landmarks pierdan, además de características de vestuario, fondo o identidad. Las dos posibilidades deben considerarse al interpretar la evidencia de transferencia entre personas; este estudio no ha medido cuál predomina en LSC5.

La evaluación [Sign Language Recognition in the Age of LLMs](https://openaccess.thecvf.com/content/CVPR2026W/MSLR/papers/Javorek_Sign_Language_Recognition_in_the_Age_of_LLMs_CVPRW_2026_paper.pdf) aporta evidencia negativa útil: en los modelos y prompts analizados, el reconocimiento por prompting de VLM queda muy por debajo de clasificadores ISLR supervisados en WLASL300. La conclusión pertenece a esas configuraciones; no demuestra incapacidad de todo VLM futuro. Ayuda a distinguir una herramienta visual generalista de un recurso con evidencia específica en señas.

## 6. Alternativas prometedoras de campos cercanos

Estas conexiones son hipótesis de aplicabilidad apoyadas por evidencia de otros dominios. Se documentan para una decisión posterior; no se han convertido en diseño experimental.

| Alternativa / campo | Evidencia de origen | Por qué podría importar | Límite decisivo | Madurez para transferir |
|---|---|---|---|---|
| SSL de movimiento: MAMP y MotionBERT | Reconstrucción y priors en esqueletos/pose. | Separar dinámica de apariencia puede ayudar al cambio de persona. | Priors de cuerpo y coordenadas físicas no describen automáticamente dedos/rostro de Holistic. | Métodos establecidos; adaptación anatómica pendiente. |
| Pooling temporal localizado: TimeMIL | Clasificación multivariante con fragmentos relevantes y orden temporal. | Una seña contiene preparación, ejecución y cierre; el clip completo puede tener señal desigual. | La selección temporal puede omitir partes semánticas o convertirse en atención a un artefacto. | Código visible; no evidencia local. |
| Convoluciones y espectro: TSLANet, ModernTCN | Clasificación de señales y ruido temporal. | Los landmarks son señales cortas y ruidosas; modelos compactos merecen atención junto a Transformers. | La estructura articulada y los cambios de escala/canal no están garantizados. | Código visible; claims sujetos a protocolo y auditorías. |
| Prototipos de formas: UniShape | Clasificación temporal mediante subsecuencias discriminativas. | Relación con posiciones y transiciones recurrentes de una seña. | Pretraining, canales y licencia de artefactos requieren revisión. | Publicación 2026; evidencia multivariante específica limitada para esta tarea. |
| Priors sintéticos reutilizables: Mantis / TS2Vec-FM | Transferencia temporal desde señales generadas. | Reduce dependencia de obtener datos externos audiovisuales específicos. | No representa por sí mismo anatomía ni gramática; la procedencia de cada checkpoint sigue importando. | Mantis tiene artefactos visibles; TS2Vec-FM sigue como preprint sin artefactos verificados. |
| Inferencia en contexto: TimEE | Clasificación temporal con soporte etiquetado y modelo sintético. | Hay etiquetas públicas de las cinco clases; el mecanismo evita cierto ajuste específico. | Multicanal es una limitación reconocida; debe verificarse independencia de cada query respecto del resto del test. | Exploratoria para LSC5. |
| Consistencia entre dominios: Fishr, SAGM y MIRO | Generalización OOD entrenando en dominios fuente. | El cambio de persona es un desplazamiento de distribución explícito. | Solo tres sujetos para aprender invariancias; resultados de imágenes no prueban ganancias temporales. | Código publicado; costo de entrenamiento y definición de dominios pendientes. |
| Transferencia desde sensores: UniMTS / TF-C | Actividad humana e invariancia entre dispositivos o señales. | Sugiere estudiar qué dinámica se conserva entre personas y modalidades. | Landmarks no equivalen a acelerómetros/giroscopios; invariancias excesivas pueden borrar una seña. | Transferencia conceptual; no conexión directa de checkpoints. |
| Distilación y representaciones intermedias | Familias visuales/temporales y encoders de distintos tamaños. | El pretraining costoso puede reutilizarse sin repetirlo completo. | El profesor puede transmitir sesgos; la disponibilidad y licencia de pesos condicionan viabilidad. | Mecanismo establecido, resultado local desconocido. |

Dos ejemplos de evidencia cuantitativa acotada ayudan a dimensionar estas conexiones. [TimeMIL](https://arxiv.org/html/2405.03140v2) informa en §4.2 accuracy media de 77,4% en 26 datasets UEA; su Tabla 3 compara pooling temporal con otros agregadores. [TS2Vec-FM](https://arxiv.org/html/2610.28602v1) informa en Tabla 1, con encoder congelado y logistic regression, 83,32% en UCR-128 y 75,30% en UEA-27. Son protocolos distintos y ninguno estima la accuracy esperable en LSC5.

La misma fuente reciente reconoce límites: TS2Vec-FM utiliza una sola semilla de pretraining para su modelo principal y queda ligeramente por debajo de MantisV2 en su comparación. [TimEE](https://arxiv.org/html/2607.07500v1), §5, reconoce dificultades para aprovechar dependencias multivariantes. Se preservan como límites de la evidencia, aunque la idea resulte prometedora.

## 7. Herramientas prácticas y qué ofrecen realmente

Estas referencias complementan los métodos del índice; las páginas de herramientas antiguas consultadas hoy no se contabilizan como nuevos artículos de 2022–2027.

| Herramienta / fuente oficial | Uso que documenta | Ventaja | Límite para LSC5 |
|---|---|---|---|
| [OpenHands](../literature/01_priority_table.md) | Ecosistema específico de reconocimiento de señas; ficha y URL autoral en la tabla. | Cercanía de tarea y componentes reutilizables. | Mantenimiento y compatibilidad actuales requieren cautela; consultar advertencia de su ficha. |
| [PYSKL](../literature/01_priority_table.md) | Herramientas y configuraciones para reconocimiento con esqueletos. | Contrasta varias representaciones en un entorno común. | Sus esqueletos/configuraciones no son el esquema Holistic del reto. |
| [MMAction2](https://github.com/open-mmlab/mmaction2) y [model zoo](https://mmaction2.readthedocs.io/en/latest/model_zoo/recognition.html) | Modelos de reconocimiento, configuraciones, checkpoints y protocolos de evaluación. | Expone sampling, crops, FLOPs, pretraining y resultados por configuración. | No es un clasificador LSC5 preparado; dependencias y checkpoints tienen contratos específicos. |
| [MMPose WholeBody](https://mmpose.readthedocs.io/en/latest/model_zoo/wholebody_2d_keypoint.html) | Estimación anatómica y checkpoints con métricas de pose. | Ayuda a entender el extractor usado por muchos trabajos de señas. | AP de pose mide otra tarea; cambiar extractor modifica el contrato de datos. |
| [MediaPipe Gesture Recognizer](https://developers.google.com/edge/mediapipe/solutions/vision/gesture_recognizer) | Landmarks, lateralidad y clasificación de poses de mano predefinidas. | SDK y ejecución de gestos de mano documentados. | Sus siete gestos incorporados no son el vocabulario dinámico LSC5; aceptar video como entrada no demuestra reconocimiento de secuencias lingüísticas. |
| [Mantis](https://github.com/vfeofanov/mantis) | Encoders temporales, checkpoints y soporte multicanal. | Menor tamaño que grandes modelos visuales y artefactos consultables. | Longitud, agregación por canal y normalización deben entenderse antes de transferir; no ejecutar su receta sobre test para aprender estadísticas. |

Las herramientas son fuentes de componentes y evidencia. La compatibilidad de versiones o el funcionamiento en el servidor UNAB no se verificaron en esta etapa.

## 8. Disponibilidad, integridad y condiciones de transferencia

La literatura contiene métodos útiles que no son inmediatamente reproducibles. Se registran por separado enlaces a código, checkpoints y términos, junto con advertencias de repositorios sin mantenimiento, pesos no liberados o anuncios de liberación futura. Una licencia del artículo no licencia automáticamente el software, los pesos ni sus datos de origen.

La revisión encontró diferencias concretas que cambian la utilidad práctica: graph-SkeletonMAE mantiene una promesa de liberar código y STTFormer anuncia pesos futuros; no se los considera recursos ejecutables ya acreditados. VideoPrism distingue checkpoints públicos de los evaluados originalmente. Los pesos pequeños de V-JEPA 2.1 no heredan la cifra máxima de su variante de dos mil millones de parámetros. Las fichas preservan esas advertencias con sus fuentes, sin sustituirlas por una casilla genérica de “código disponible”.

El [repositorio de VideoPrism](https://github.com/google-deepmind/videoprism) publica diferencias entre sus pesos públicos y los del artículo. La [auditoría de ModernTCN](https://github.com/onderakacik/RE-ModernTCN) muestra por qué también importa revisar el entorno experimental; esta consulta pudo verificar su repositorio autoral, pero no abrir el texto definitivo de OpenReview. No se atribuyen a ese texto detalles que no se pudieron comprobar.

Preentrenamiento externo y datos externos son situaciones diferentes en las reglas del reto: se permite transfer learning con atribución; incorporar otros datos exige declaración y criterio del comité. Que un repositorio incluya un script de descarga no autoriza ejecutarlo para competir. Tampoco se debe descargar una copia etiquetada externa de LSC5 para relacionar muestras con test.

Las siguientes restricciones condicionan cualquier transferencia posterior:

- Adaptación al test, actualización de estadísticas con test, seudoetiquetado o selección usando feedback del ranking siguen prohibidos.
- Atención conjunta entre queries de test, transducción o normalización de un lote de test pueden introducir dependencia entre muestras. Un nombre como “few-shot” o “in-context” no resuelve esa condición.
- Transformaciones de inferencia fijadas con train y aplicadas a cada muestra son una operación diferente de aprender del test. Expresiones como “test-time strategy” requieren inspección del mecanismo concreto.
- Igualar la distribución de predicciones al balance declarado no deriva de la evidencia de reconocimiento y requiere aclaración organizativa; no se adopta como método.
- Los reflejos, rotaciones o cambios de velocidad no tienen conservación semántica garantizada para todas las señas. Una invariancia útil en acciones generales puede ser incorrecta lingüísticamente.
- Los ceros observados en los arrays no establecen una convención universal de missingness. El orden y la política del extractor siguen pendientes.
- Las etiquetas explícitas o correlacionadas en nombres de train no constituyen señal visual válida; la revisión no buscó metadatos equivalentes del test.

## 9. Orden de lectura para el siguiente agente

La tabla asigna P1/P2/P3 con razones contextuales. El siguiente responsable puede empezar por recursos especializados compactos sobre landmarks, continuar con refinamientos de entrenamiento y priors de movimiento, y revisar transferencia RGB eficiente. Las familias fundacionales de mayor tamaño y las conexiones de sensores/ICL tienen límites adicionales que deben permanecer visibles.

Para cada recurso que se considere seriamente hacen falta estas comprobaciones documentales, antes de convertirlo en una propuesta concreta:

1. Coincidencia de tarea, modalidad, topología, coordenadas y tratamiento de datos ausentes.
2. Protocolo que sostiene la cifra publicada y separación real entre personas.
3. Configuración individual frente a combinación de redes/streams/vistas.
4. Código y pesos disponibles, revisión/versión y licencia de cada componente.
5. Diferencia entre costo de pretraining, adaptación e inferencia; no usar parámetros entrenables como sustituto de VRAM medida.
6. Compatibilidad del flujo con aprendizaje exclusivo en train e inferencia fija individual del test.

No se asignan aquí epochs, aumentos, folds, hiperparámetros, presupuesto de búsqueda ni una arquitectura final. Los pendientes de hardware y contrato de landmarks están referenciados en la definición del problema y deberán resolverse cuando condicionen una decisión.

## 10. Evidencia y estado de entrega

Se documentaron recursos primarios y sus artefactos públicos sin instalar software, descargar modelos/datasets, entrenar, inferir ni examinar contenidos del test. La consolidación verifica cantidad de recursos, IDs, fechas, enlaces bibliográficos, duplicados y campos esenciales; la revisión independiente final se registra en el índice de investigación.

La investigación permite continuar a una sección posterior de análisis de alternativas o diseño cuando el usuario la solicite. La aplicabilidad en LSC5 y el potencial de mejorar el ranking permanecen como hipótesis hasta contar con evidencia local autorizada.
