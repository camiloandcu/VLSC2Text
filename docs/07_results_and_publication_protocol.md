# Evidencia de resultados, reporte y posible artículo

Registro de evidencia y plan de reporte, actualizado el 19 de noviembre de2026 para R2.1. La sección8 contiene la primera línea base completa medida. Prioridad vigente: competición por accuracy top-1; el artículo es una posibilidad secundaria que requiere resultados y revisión posterior. No se garantiza novedad, aceptación o publicación.

## 1. Propósito y fuentes

Este registro define qué evidencia futura permite redactar un reporte técnico y evaluar la viabilidad de un artículo. El protocolo experimental pertenece a [04](04_solution_and_experiment_design.md), los artefactos y schemas a [05](05_technical_architecture.md), y la ejecución/aceptación a [06](06_delivery_and_iteration_plan.md). No copiar sus contratos aquí.

La [auditoría de datos](02_data_audit_public.json) contiene observaciones ya realizadas. Las cifras de papers ajenos pertenecen al [índice bibliográfico](../literature/resources.csv), con dataset/protocolo; nunca rellenan casillas de resultados propios.

## 2. Evidencia mínima que debe conservar cada comparación

| Evidencia | Motivo y consumidor |
|---|---|
| Versión y hashes de datos/manifests, sin distribuir archivos originales | Vincular una cifra con exactamente las muestras usadas; permitir auditoría dentro del acceso autorizado. |
| Configuración resuelta, código/commit y entorno | Reproducir receta y detectar incompatibilidades. |
| Sujeto/fold, semilla, objetivo, pérdida y regla de checkpoint/épocas | Distinguir decisiones previas de selección posterior. |
| Predicción OOF por ID y verdad de train | Recalcular métricas y contrastes pareados; conservar localmente cuando la autorización no permita publicar IDs. |
| Costo real y modo de medición | Separar consumo, créditos y desembolso efectivo según 06, además de tiempo CPU/GPU y memoria. Incluir preparación, extracción, intentos fallidos, almacenamiento, transferencias, refit e inferencia. |
| Dependencias y claves de caché | Distinguir el costo amortizado de una cabeza del costo completo de encoder, decoder y preprocesamiento; acreditar qué se reutilizó sin aprender del fold retenido. |
| Errores/fallos/interrupciones y corridas descartadas | Evitar seleccionar solo ejecuciones favorables. |
| Registro de selección y manifiesto congelado | Demostrar la secuencia selección → refit → inferencia. |
| Recibo/evidencia de entrega y puntuación oficial si se obtiene | Separar desarrollo de evaluación privada; conservar permiso y no usar feedback para ajustar. |
| Origen/licencia de pesos, código y datos utilizados | Atribución y condiciones reales de reutilización. |

No convertir una repetición de semilla sobre los mismos tres sujetos en tres sujetos nuevos. Las vistas simultáneas y los duplicados exactos tampoco amplían el número de personas independientes.

## 3. Tablas y figuras previstas

Las siguientes son especificaciones de contenido; solo se generarán con artefactos reales, sin porcentajes ilustrativos que parezcan resultados.

| Elemento | Contenido | Condición para publicarlo |
|---|---|---|
| Tabla de dataset y calidad | Conteos, longitud, missingness y alcance de supuestos del extractor | Derivar de la auditoría y explicar que cero observado no prueba mano ausente. |
| Comparación principal | Modelo/receta, resultados por sujeto y agregado del protocolo, variación por semilla y costo | Separar recetas fijas, refinamientos adaptativos y combinaciones; mostrar presupuestos comparables. |
| Ablaciones | Cambio de representación o mecanismo y resultado correspondiente | Conservar todas las variantes declaradas y su contexto; no presentar combinaciones como un solo factor. |
| Matriz de confusión | Predicciones OOF agregadas y por sujeto | Reportar denominadores, cinco códigos y significado; no incluir etiquetas privadas del test. |
| Análisis de calidad | Errores frente a ausencia de bloques, vista o longitud | Son asociaciones descriptivas; no probar causalidad ni usar metadata como entrada del modelo. |
| Eficiencia | Tiempo medido, VRAM pico y tamaño del bundle completo | Mismo entorno o diferencias explícitas; separar pretraining externo, extracción fija, adaptación e inferencia desde originales. No presentar solo la cabeza como costo del sistema visual. |
| Diagrama de arquitectura | Flujo efectivamente implementado | Actualizar a la versión final; el diseño inicial no prueba ejecución. |

Las figuras para compartir serán artefactos exportables generados con herramientas de análisis. Publicar fotogramas, rostros, voces, landmarks identificables o ejemplos audiovisuales requiere condiciones expresas del dataset; se pueden usar esquemas sintéticos y agregados mientras esas condiciones no estén aclaradas.

## 4. Cómo interpretar el resultado

La selección entre alternativas sobre OOF hace que la puntuación de la receta seleccionada sea una estimación de desarrollo optimista; conservar la declaración exacta de 04. Un test privado retenido añade evidencia sobre una persona en este dataset, no una estimación universal de utilidad para personas sordas o toda la LSC.

El usuario confirmó dos evaluaciones externas y que cuenta la última. Si se usan ambas, reportar su secuencia, versiones, motivo de corrección y cuál aceptó la organización; no presentar retrospectivamente el máximo como resultado oficial. Preservar el freeze previo y la evidencia de que no se entrenó o seleccionó según feedback. Una corrección técnica debe distinguirse de un cambio de modelo, con evidencia independiente del score. La política y operación pertenecen a 04 §12 y 06 §9.

Las mejoras pequeñas pueden corresponder a pocos clips; reportar aciertos y denominadores además del porcentaje. Un intervalo calculado suponiendo clips independientes omite la dependencia por persona y ejecución. Con tres sujetos públicos, cualquier intervalo entre sujetos o prueba formal tiene limitaciones severas; no afirmar significancia o generalización poblacional por repetir semillas.

Una conclusión negativa —por ejemplo, una representación cara que no supera una alternativa compacta— es válida si el protocolo y las comparaciones son transparentes. Registrar también si un recurso no pudo reproducirse por pesos, permisos, memoria o dependencias; eso no demuestra que su método sea inferior científicamente.

## 5. Estructura del reporte técnico de competición

1. Problema, clases, datos y criterio oficial, con referencia a las reglas.
2. Representación y calidad de los datos, preprocesamiento y supuestos verificados.
3. Métodos realmente usados y procedencia de código/pesos, citados por DOI o referencia bibliográfica.
4. Validación, selección, semillas y presupuesto de comparación.
5. Resultados medidos, limitaciones y decisión de la receta final.
6. Entrenamiento final, reproducción de inferencia y formato de entrega.
7. Integridad, privacidad, licencias/atribuciones y referencias.

El tamaño/formato oficial del reporte todavía debe confirmarse. Redactar desde resultados estructurados y la versión efectivamente entregada; no describir como ejecutadas ramas que solo fueron propuestas.

La ficha del modelo debe declarar modalidad y requisitos reales. Una vista RGB recortada mediante landmarks necesita ambos insumos; una cabeza sobre caché requiere el encoder y sus transformaciones para nuevos clips. Documentar fallbacks, esquema acreditado, hashes, licencia y restauración del bundle completo. Comparar global frente a ROI y pooling frente a TCN como contrastes de recetas; cambiar arquitectura y orden temporal a la vez no identifica una causa única.

## 6. Posible artículo posterior

Una pregunta candidata es qué factores de representación y entrenamiento ayudan a transferir entre personas en un vocabulario pequeño con detecciones anatómicas incompletas y cómputo limitado. Es una orientación para analizar la evidencia futura, no un gap científico aprobado ni una contribución novedosa acreditada.

La literatura respalda investigar calidad de keypoints, representación compacta, relaciones entre partes y transferencia; las fichas del índice guardan citas estables. Ejemplos: Boháček y Hrúz, *SPOTER*, WACV Workshops 2022; Roh et al., *Preprocessing Mediapipe Keypoints with Keypoint Reconstruction and Anchors for Isolated Sign Language Recognition*, SignLang 2024, [ACL Anthology 2024.signlang-1.36](https://aclanthology.org/2024.signlang-1.36/); Lascar et al., *PoET*, VISAPP 2026, [DOI:10.5220/0014237500004084](https://doi.org/10.5220/0014237500004084). No implican que aplicar esas ideas en LSC5 sea novedoso.

Antes de convertir resultados en propuesta de publicación:

- Verificar literatura actualizada y el gap con revisión científica independiente; evitar que la búsqueda de ranking dicte una hipótesis retrospectiva presentada como previa.
- Evaluar si datos, sujetos, controles y presupuesto sostienen la afirmación; un dataset de cuatro sujetos limita fuertemente las conclusiones poblacionales.
- Distinguir estudio descriptivo/reproducibilidad de contribución metodológica; justificar cualquier extensión nueva con evidencia y comparadores apropiados.
- Confirmar derechos de uso/publicación, atribución del dataset, autorías/contribuciones reales y licencias. No inventar aprobación ética o consentimiento para usos no acreditados.
- Elegir propuesta/venue y protocolo adicional con aprobación del usuario. Si se requieren otros datos o experimentos, abrir un alcance nuevo y su autorización.

No se producirán tablas ficticias, tests estadísticos retrospectivos oportunistas, promesas de publicación o borradores que describan resultados inexistentes. Las declaraciones de asistencia, atribución y licencias exigidas por organizadores o revista se conservarán.

## 7. Publicación pública y disponibilidad

El repositorio público puede distribuir el código propio bajo la licencia que el usuario elija, documentación, configuraciones y resultados agregados revisados. Código ajeno, checkpoints o datos mantienen términos propios. Antes de cualquier publicación aplicar la revisión de archivos y atribuciones de W08 en 06: las exclusiones del árbol local no corrigen material que ya haya sido versionado. La entrega al reto y la publicación pública requieren sus autorizaciones correspondientes.

Los textos completos locales son material de consulta y quedan excluidos de publicación. Las referencias duraderas usan DOI, arXiv, editorial o cita bibliográfica. El reporte de disponibilidad debe declarar cómo obtener los datos mediante su canal autorizado, sin redistribuirlos ni incluir rutas privadas necesarias para entender un resultado.

La evidencia privada reproducible puede mantenerse en artefactos locales con hashes y acceso autorizado. La documentación pública referencia el resultado agregado y el identificador de versión adecuado; no debe exigir un enlace a un documento local no publicable para comprender la metodología.


## 8. Primera línea base completa · R2-E01

Medición del19 de noviembre de2026. `raw_stats_mlp_v2`, R0 de columnas opacas y semilla17; receta fija y LOSO de [04 §§4–6](04_solution_and_experiment_design.md). Cada fold ajustó750 clips durante80 épocas y evaluó375 de la persona excluida, una sola vez al final. Escalador fit-only; sin early stopping, búsqueda de checkpoints o selección de semillas. Las otras modalidades/recetas no se ejecutaron en este ítem.

| Persona retenida | Aciertos / clips | Accuracy | Macro-F1, cinco clases |
|---|---:|---:|---:|
| M02 | 164 / 375 | 43,73% | 0,3727 |
| M03 | 280 / 375 | 74,67% | 0,7210 |
| M04 | 242 / 375 | 64,53% | 0,6293 |
| OOF completo | **686 / 1.125** | **60,98%** | **0,5968** |

La métrica agregada se recalculó con una predicción fuera de ajuste para cada ID. Macro-F1 se calcula sobre las cinco clases del conjunto indicado; el global no es el promedio de los tres Macro-F1. No hay resultados de test, comparación entre semillas ni ranking oficial. Tres personas no permiten atribuir a este porcentaje una precisión poblacional estrecha.

Matriz OOF: filas=clase verdadera, columnas=predicción, orden de códigos establecido en01. Cada fila contiene225 clips.

| Verdad / predicción | sign_01 | sign_02 | sign_03 | sign_04 | sign_05 |
|---|---:|---:|---:|---:|---:|
| sign_01 | 139 | 51 | 28 | 7 | 0 |
| sign_02 | 6 | 211 | 1 | 7 | 0 |
| sign_03 | 64 | 1 | 131 | 0 | 29 |
| sign_04 | 21 | 27 | 0 | 132 | 45 |
| sign_05 | 25 | 8 | 74 | 45 | 73 |

**Diagnósticos descriptivos.** Recall por clase: sign_01=61,78%, sign_02=93,78%, sign_03=58,22%, sign_04=58,67% y sign_05=32,44%. M02 recupera solo1/75 ejemplos sign_01, frente a68/75 en M03 y70/75 en M04. La confusión más frecuente es sign_05→sign_03,74 casos; no demuestra por sí sola su causa. Por vista: V01=209/375 (55,73%), V02=251/375 (66,93%) y V03=226/375 (60,27%). Por longitud predefinida:≤40 frames=14/23 (60,87%),41–60=444/758 (58,58%) y>60=228/344 (66,28%). El grupo corto es pequeño; longitud/vista/clase pueden estar relacionadas. Missingness anatómica sigue desconocida y ningún cero se interpreta como ausencia acreditada.

**Interpretación para iterar.** Las pérdidas de ajuste finales están entre0,00035 y0,00123, mientras la precisión retenida varía31 puntos entre personas. Es compatible con sobreajuste o dependencia de rasgos particulares, sin identificar causalmente cuál. R0 descarta orden temporal y no normaliza geometría anatómica. La siguiente hipótesis propuesta es comprobar el contrato anatómico y evaluar la representación temporal normalizada ya prevista en E02; E03 y RGB conservan sus puertas. No se implementó esa hipótesis ni se modificó la receta al observar estos resultados. M02 perdió11 aciertos frente al piloto de dos épocas; no se sustituye retrospectivamente el checkpoint fijo de80 épocas por el piloto.

**Reproducibilidad y costo.** Los tres modelos se restauraron en procesos nuevos desde los375 NPY train originales de su fold, sin caché: diferencia máxima0 en cada uno, tolerancia1e-6/rtol0. La [evidencia por AC](../openspec/changes/archive/2026-11-19-cpu-baseline-loso/tasks.md) posee jobs, reservas, huellas, snapshots y revisión. Los jobs sumaron18 segundos de tiempo asignado Slurm; no es duración extremo a extremo ni suma de CPU-segundos de sus cuatro núcleos. No incluye extracción local R0, transferencias o restauración local, cuyos tiempos completos no se instrumentaron. Sin gasto monetario. Test, pagos y las dos evaluaciones oficiales permanecen fuera de este alcance.

**Ficha del candidato de desarrollo.** Entrada: NPY float64 `(T,1662)` de columnas opacas; extracción R0, escalador y MLP conforme a04/05. Salida: cinco probabilidades en el orden de códigos de01. Uso validado aquí: evaluación de desarrollo en tres personas train; un fold contiene un modelo diferente de los otros dos. No existe aún un bundle reajustado con todo train, freeze final o CSV competitivo. La anatomía no acreditada, el vocabulario cerrado y la variación entre personas limitan su reutilización. Código y dependencias exactos se preservan en un snapshot privado; derechos de datos/licencia propia siguen según01/README. No se redistribuyen IDs, pesos o entradas privadas por este registro.


## 9. Contraste temporal opaco · R2-E02O

Medición del20 de noviembre de2026. Receta `opaque_tcn_v1`/`opaque_sequence_v1`, protocolo R2.2 de [04 §13](04_solution_and_experiment_design.md): proyección1662→64, tres bloques convolucionales residuales dilatados,168773 parámetros. Cada fold conservó T nativo, escalador poblacional por frames reales exclusivamente fit,80 épocas/1520 actualizaciones y semilla17. Se evaluaron375 clips una sola vez al final de cada ajuste de750; sin early stopping ni selección de checkpoint. Ceros originales incluidos, padding excluido; ninguna semántica anatómica supuesta.

| Persona retenida | Aciertos / clips | Accuracy | Macro-F1 | Diferencia de aciertos frente a R2-E01 |
|---|---:|---:|---:|---:|
| M02 | 110 / 375 | 29,33% | 0,2563 | −54 |
| M03 | 252 / 375 | 67,20% | 0,6662 | −28 |
| M04 | 188 / 375 | 50,13% | 0,4763 | −54 |
| OOF completo | **550 / 1.125** | **48,89%** | **0,4935** | **−136** |

**Decisión según umbral prefijado: no promover.** La baseline conserva60,98%; la diferencia es−12,09 puntos porcentuales. La comparación alinea los1125 IDs y la verdad del mismo manifiesto, con una predicción fuera de ajuste por clip y ancla SHA del reporte histórico congelada antes de correr E02O. No alcanza los≥3 aciertos adicionales y pierde más de tres en cada persona. La vía alternativa por costo no se acredita: faltan costos extremo a extremo comparables, y esta receta consume más tiempo de ajuste Slurm. No se sustituye por el piloto de dos épocas ni se abre una búsqueda de semillas/épocas sobre el resultado observado.

La comparación pareada identifica ejemplos complementarios sin seleccionar un ensemble en este ítem:

| Persona | Antes incorrecto, ahora correcto | Antes correcto, ahora incorrecto | Balance |
|---|---:|---:|---:|
| M02 | 67 | 121 | −54 |
| M03 | 42 | 70 | −28 |
| M04 | 28 | 82 | −54 |
| Total | 137 | 273 | −136 |

Matriz OOF, filas=verdad, columnas=predicción, orden de01:

| Verdad / predicción | sign_01 | sign_02 | sign_03 | sign_04 | sign_05 |
|---|---:|---:|---:|---:|---:|
| sign_01 | 123 | 27 | 1 | 41 | 33 |
| sign_02 | 3 | 139 | 0 | 39 | 44 |
| sign_03 | 75 | 0 | 68 | 2 | 80 |
| sign_04 | 27 | 8 | 2 | 124 | 64 |
| sign_05 | 4 | 8 | 46 | 71 | 96 |

**Interpretación.** Las pérdidas finales de ajuste se sitúan entre0,000108 y0,000134; el buen ajuste no se traduce en mejora sobre la persona retenida. El resultado es compatible con sobreajuste/dependencia de persona, sin identificar la causa. Entrada y arquitectura cambiaron simultáneamente: no demuestra que el orden temporal sea perjudicial, ni descarta modelos temporales normalizados o preentrenados. Tampoco acredita anatomía, unidades o ausencia de detecciones. El peor desempeño de esta variante, pese a ser viable en CPU, reduce la prioridad de ampliar su capacidad sin una hipótesis distinta.

**Reproducción.** Los tres modelos se restauraron en procesos nuevos desde sus375 NPY originales, sin usar caché, con diferencia máxima0 en probabilidades (atol1e-6/rtol0). El piloto previo también se restauró antes de admitir folds. Se conservan modelo, scaler, split, logits/probabilidades, métricas y hashes. Productor `e9d812a3d0d0f9e7893ddf1053396ca84ef87ea99207b5565dc043e4cf34abae`; snapshot privado exacto de27 archivos. El productor histórico de R2-E01 permanece intacto. [Evidencia por AC](../openspec/changes/archive/2026-11-20-opaque-temporal-tcn/tasks.md); contabilidad y límites en [06 §10](06_delivery_and_iteration_plan.md). Pruebas sintéticas y revisión de código se distinguen de estos resultados reales.

**Siguiente decisión propuesta.** Conservar R2-E01 como candidato de desarrollo y cerrar esta receta opaca. Priorizar la factibilidad de RGB global congelado E07/E08, prevista en04, para contrastar una modalidad complementaria sin depender del esquema NPY; exige comprobar peso/licencia, acceso y costo de la cadena completa antes de ejecutar. E03/R1,E04/E05 y ROI continúan bloqueados por procedencia anatómica. No se ha elegido ni pagado proveedor, usado GPU, reajustado sobre todo train, inspeccionado test o consumido evaluaciones oficiales. No hay ranking ni freeze final; esta recomendación no amplía la autorización.


## 10. Piloto RGB local · extracción completada, replay fallido

**20 nov2026; decisión: detener la admisión de E07/E08.** Se ejecutó el primer intento aprobado con DINOv2 ViT-S/14 congelado en la GTX1650 local. La extracción de los30 clips train preseleccionados terminó correctamente y publicó un caché íntegro. El proceso nuevo de replay falló al mover el modelo a CUDA (`RuntimeError: CUDA error: out of memory`), después de cargar los pesos en CPU. No produjo embeddings de replay ni recibo de equivalencia batch1/batch4. El intento completo terminó **FAILED**; G3 operativo no está satisfecho. No se repitió, cambió K/batch/precisión ni abrió otra rama.

| Medición | Resultado y alcance |
|---|---|
| Cobertura |30 clips,16 frames/clip,480 imágenes medidas; N real33–97,1920×1080;187472255bytes originales. |
| Encoder |22056576 parámetros, congelados; CLS `(16,384)` float32 por clip, sin normalización L2; identidad en05 §14. |
| Calentamiento y batches |5 batches de4 imágenes descartados de la medición;120 batches medidos. |
| Extracción |194,101s dentro del worker; etapa completa observada por supervisor204,312s. |
| Arranque / calentamiento |34,822s de construcción/carga del encoder;4,432s de calentamiento. |
| Forward medido |12,914s sincronizados para480 imágenes; excluye calentamiento, transferencias, decode y replay. |
| Mayor costo por clip |9,471s, incluyendo hash/conteo/decode/transformación/forward/escritura/verificación; excluye arranque y calentamiento. |
| Intento completo |265,507s, incluyendo etapa de replay fallida59,582s y supervisión/finalización. |
| Caché piloto |30 shards, todos finitos y verificados;691837bytes de shards y724435bytes con metadatos;737280bytes de embeddings sin comprimir. |
| Memoria observada |Máximo agregado del supervisor/trabajador/decoder1,156GiB RSS; mínimo de RAM disponible2,031GiB. PyTorch en extracción:137,298MiB asignados /164MiB reservados de pico. |

**Qué se verificó.** Los30 IDs, hashes/índices y cobertura coinciden con la selección previa. La fuente, peso, lock, productor y archivos de caché pasaron comprobaciones de integridad; un consumidor de1125 rechaza `coverage=pilot30`. El entorno CPU/locks y snapshots anteriores permanecen íntegros. Las pruebas sintéticas verifican rechazos, exclusión, señales y vigilancia durante una consulta GPU lenta; no sustituyen el replay real fallido. Productor `3c6edb096c4605d8dc0f3339f9a4ca3f2c582c8ab157db9c974bcc940f42f767`, snapshot privado exacto de36 archivos.

**Qué sigue desconocido.** La causa raíz del OOM de inicialización no está acreditada. Las206 muestras de memoria global de GPU reportaron un máximo de257MiB usados y un mínimo de3679MiB libres; una consulta agotó su timeout y quedó registrada. Esas consultas y los picos PyTorch de la primera etapa no explican por sí solos el fallo del proceso nuevo ni garantizan disponibilidad futura. No concluir que el modelo necesita más de4GiB, que el controlador es la causa o que basta reducir batch: el fallo ocurrió antes del primer forward de replay. El RSS de hijos publicado por `getrusage` tampoco aísla el consumo estable del decoder; para el límite se usa el muestreo agregado del supervisor.

**Proyección diagnóstica, sin admisión.** Aplicando la fórmula fijada con margen1,5 al mayor costo por clip:16043,263s (**4h27min**) para1125 train y5388,420s (**1h30min**) como referencia de375 clips de longitud similar. Incluye arranque/calentamiento/finalización medidos; no incluye costo desconocido de cabeza/confirmación/refit ni garantía de estabilidad o longitudes futuras. No se abrió test para estimar esta referencia. El forward representa aproximadamente6,65% de los194,101s del worker; acelerar únicamente la GPU no garantiza reducir proporcionalmente el costo completo.

**Decisión del intento01, anterior al reintento de§11.** Conservar R2-E01 como candidato de desarrollo y cerrar este experimento como resultado negativo de reproducibilidad. La primera extracción acredita ejecución visual local, pero el caché piloto no se promueve ni se declara lista la cadena RGB. Proponer un diagnóstico acotado de la inicialización CUDA y, solo con un nuevo alcance aprobado, verificar estabilidad y replay antes de extracción completa/cabeza. No descartar RGB por accuracy: aquí no se entrenó clasificador ni se midió accuracy. No usar losUSD10 hasta justificar una alternativa con costo total/infraestructura y puertas propias. R1/ROI siguen bloqueados; test y las dos evaluaciones oficiales permanecen intactos. [Evidencia por AC](../openspec/changes/archive/2026-11-20-rgb-global-pilot/tasks.md); contabilidad autoritativa en06 §11.


## 11. Reintento RGB autorizado · conforme

**20 nov2026; intento02 COMPLETED.** La petición expresa del usuario autorizó una sola repetición completa del piloto30/K16 y replay, sin cambiar encoder, entorno, selección, decoder, normalización, precisión, batches o límites. El nuevo proceso de replay cargó CUDA correctamente y produjo embeddings desde el video/peso originales. El primer intento sigue registrado comoFAILED; su causa raíz permanece desconocida. Este éxito acredita el recorrido observado, no una corrección demostrada de la causa ni estabilidad indefinida.

| Medición | Original | Reintento |
|---|---:|---:|
| Intento completo, supervisor |265,507s;FAILED |121,449s;COMPLETED |
| Extracción dentro del worker |194,101s |100,284s |
| Mayor costo completo por clip |9,471s |4,153s |
| Arranque del encoder |34,822s |16,014s |
| Calentamiento5 batches |4,432s |2,662s |
| Proyección train1125 con margen1,5 |16043,263s,4h27min |7036,691s,1h57min |
| Referencia375 con margen1,5 |5388,420s,1h30min |2364,438s,39min24s |
| Replay batch1 frente a4, relativoL2 |No verificado |2,143078141×10⁻⁶≤10⁻⁴ |

**Integridad y equivalencia.** Treinta shards `(16,384)` float32 finitos y sus hashes pasaron la validación; cobertura `pilot30`, sin clasificador ni OOF. El replay se ejecutó en proceso nuevo; píxeles e identidad verificados. Respecto de la referencia del reintento, batch1 tiene error relativo2,143078141×10⁻⁶ y batch4 tiene0; máximo error absoluto2,348423004×10⁻⁵. Se recalcularon independientemente a partir de los arrays conservados. Los30 clips mantienen N/índices, SHA de video y píxeles del primer intento; el máximo error relativo entre embeddings de ambas extracciones es0. Esto no implica igualdad del archivo comprimido o de metadatos de tiempos.

**Recursos y alcance medidos.** Admisión real3,163GiB de RAM disponible,3,843GiB de VRAM libre, antes del corte. Pico RSS agregado0,889GiB, RAM disponible mínima2,541GiB; pico PyTorch137,298MiB asignados/164MiB reservados, igual al primer encoder.115 muestrasGPU, sin errores de consulta. Medidos120 batches posteriores a5 de calentamiento:480 imágenes; forward sincronizado9,087s de extracción y1,042s de replay, total10,128s, sin sumar nuevamente al presupuesto. El replay completo tardó14,498s. No quedaron workers propios activos.

**Versiones y controles.** Productor `e4a8979df15e62bde0c3776250c94c268d3d0585891e680cb3da67c50e01314f`, snapshot36archivos. Solo presupuesto/CLI y pruebas difieren del productor original; el pipeline RGB y dependencias conservan sus hashes. Pruebas completas27/27 y focales11/11; revisión independiente previa2 pruebas nuevas más rechazos de padre/recibo/manifiesto. Historial y contabilidad en06 §12. [Evidencia del reintento por AC](../openspec/changes/archive/2026-11-20-rgb-global-pilot-retry/tasks.md).

**Decisión.** La puerta técnica de replay se supera en este intento. Se puede proponer E07 global completo y E08 con su piloto de cabeza CPU y presupuesto de cadena/refit/inferencia; no ejecutarlos por esta autorización. Conservar para planificación la mayor proyección observada,4h27min train y1h30min referencia375, por variación de condiciones/caché y sin atribuir causalmente el cambio a una sola causa. El costo de cabezas/refit y estabilidad de extracción1125 siguen sin medir. R2-E01 conserva60,98% LOSO; todavía no hay accuracy RGB. LosUSD10 y dos evaluaciones oficiales siguen intactos; R1/ROI continúan bloqueados.


## 12. E07 global/E08 · restauración fallida, candidata no aceptada

20nov2026: extracción completa y tresfits terminados; la restauración original falló y detuvo la secuencia. **No existe OOF RGB aceptado ni comparación definitiva**, y E01 conserva su posición como mejor receta validada. Los resultados guardados de los tres modelos son provisionales:155/375 M02,134/375 M03 y175/375 M04, suma464/1125 (41,24%), frente a686/1125 (60,98%) deE01. No superan la baseline ni acreditan rendimiento competitivo; tampoco reemplazan una evaluación restaurada. El piloto de dos épocas permanece diagnóstico. Sin test, refit final, compra o evaluación oficial.

E07 COMPLETED:1125 videos1920×1080,33–97frames;18000 imágenes y4500 batches medidos. Pared4548,825s, forward sincronizado480,997s incluido en esa pared. RSS agregado máximo1639809024bytes, RAM disponible mínima2792284160bytes; PyTorch asignado143967744/reservado171966464bytes. Conteo1598,390s, decodificación excluyendo resize1765,565s y resize434,446s: el forward equivale al10,57% de pared, sin ser utilizaciónGPU ni prueba de aceleración alcanzable en otra máquina. Caché completo SHA de metadatos`478f1a1ccd4182d188c5b44a2f0791643bede15a4a1cffb659e12899fdffe51c`.

Piloto Slurm47 y folds48–50 COMPLETED/salida0:0,6s cadauno. Restauración del piloto desde caché en proceso CPU nuevo:375 probabilidades, diferencia máxima0. Gate real13,625s/fold y15,885s/refit. Memoria CPU máxima351440KiB por proceso; `sacct` no informóMaxRSS, sin pico agregado deljob acreditado. QA independiente verificó1125 hashes/shape/orden/video-manifest, cuatro runs y escaladores recalculados exactamente desde750fit.1125 SHA de video únicos; duplicados cercanos no evaluados.

**Fallo de restauración:** último hito publicado850/1125 y3031,676s parciales. Se conservaron872 archivosNPZ de staging; su mera presencia no acredita integridad ni restauración completa. No hay recibos finales375×3. El traceback demuestra `TimeoutExpired` en la espera del hijo durante el `finally` del supervisor: impidió escribir `execution.json` y pudo ocultar el disparador original. Causa inicial y telemetría final desconocidas; no atribuir el fallo aOOM, CUDA, memoria, límite principal o warnings de xFormers. Observación primaria posterior de `/proc`: sin workers/supervisores RGB, consultas nvidia-smi ni decodificadoresffmpeg/ffprobe; no hubo reintento.

Productor ejecutado`ab5046c5eaf9b896747597a140f2b54540544024070189ab84fcf3d018bb8518`, snapshot42archivos intacto.31 pruebas previas98,16s y cuatro negativos independientes3,14s; equivalencia exacta de píxeles30casos52,281s. La revisión independiente verificó archivos actuales; verificación primaria suplementaria contrastó SHA/inventario/bytes de los42miembros del archivo comprimido. Estas pruebas no anticiparon el fallo de limpieza. Evidencia privada en `artifacts/rgb-loso`, incluido `restore_failure_administrative.json`; duración real final desconocida y reserva retenida según06 §13. Revisión independiente del incidente confirma cierre negativoV4, V5nohabilitado y V3con medición final perdida; no concede conformidad global.

El diagnóstico temporal adverso y la reconciliación documental posterior al lanzamiento permanecen en06 §13. Los relojes entre máquinas no tienen sincronía acreditada. Tres personas y asociación cámara–clase limitan generalización e interpretación; no se identifica una causa del bajo accuracy. El control inverso sigue siendo diagnóstico de la misma cabeza, sin elegir dirección ni otra candidata. Esta receta no acredita la puerta de adaptaciónE11; la pareja preliminar tampoco se evaluó aquí.

Corrección acotada en curso: reparar persistencia durante limpieza; se mantiene la reserva retenida y se descartó el nuevo contrato contable por innecesario. No repetirGPU para ocultar el fallo ni retaggear productor/caché. La reserva sigue protegiendo el presupuesto. Nuevas recetas y evaluaciones oficiales conservan su decisión propia.

Corrección posterior verificada:32pruebasCPU87,77s, cinco focales3,88s y dos escenarios independientesCPU conformes. Snapshot posterior separado del ejecutado, con cambios únicamente en supervisor y prueba. Límites: errores de cierre dellock/restauración de señales posteriores a persistencia pueden no quedar grabados; si `worker_termination_confirmed:false`, la pared del supervisor no acredita duración total del trabajador y no basta para liquidación medida automática. No se recuperó la medición histórica ni se ejecutó otro intento.


**Diagnósticos de recuperación, 20nov2026 (solo lectura, sin entrenamiento ni test).** Se aplicó a los1125 IDs alineados, con la verdad train, la pareja 50/50 fijada en04 §6. Con las probabilidades E08 provisionales, E01+E08 obtiene712/1125 (63,29%), +26 aciertos frente a E01. Por persona da +19 en M02, −12 en M03 y +19 en M04. No es promovible porque M03 pierde más de un acierto. La pareja definida mientras no haya RGB elegible, E01+E02O sobre OOF aceptados, obtiene690/1125 (61,33%), +4 frente a E01, con −5 en M02, +29 en M03 y −20 en M04. Tampoco es promovible. E11 sigue cerrado: E08 está222 aciertos por debajo del líder y el máximo es12.

**Consecuencia.** Aceptar E08 mediante una restauración nueva no cambiaría la selección bajo la regla vigente, y E01 sigue como finalista único. Los872 embeddings del staging de la restauración fallida son legibles e idénticos bit a bit al caché; es una equivalencia parcial de extracción, no de probabilidades, y no sustituye V4 ni crea OOF aceptado. La cifra712 depende de E08 provisional y no se presenta como resultado aceptado. Siguiente ítem propuesto: [camino de entrega E01](../openspec/changes/archive/2026-11-20-e01-delivery-path/proposal.md).


## 13. Diagnósticos X1–X3/X7 y camino de entrega E01 · 20nov2026

Todo con train y CPU/GPU local, sin test ni gasto. Artefactos privados en `artifacts/diagnostics` y `artifacts/e01-delivery`.

**X1 · layout acreditado empíricamente.** Ejecuté MediaPipe Holistic 0.10.14 (complejidad1, confianzas0,5, modo video) sobre los30 clips de la selección piloto. En los30 coincide el número de frames con el NPY. Comparación por bloque en los frames con detección en ambos:

| Bloque | Frames | Correlación mín/mediana | Error XY mediano |
|---|---:|---|---:|
| Pose 33×4 | 1804 | 0,9912 / 0,9991 | 0,0071 |
| Cara 468×3 | 1783 | 0,99985 / 1,0000 | 0,00013 |
| Mano izquierda 21×3 | 607 | 0,9937 / 0,9998 | 0,00031 |
| Mano derecha 21×3 | 890 | 0,9979 / 0,9997 | 0,00050 |

Las hipótesis alternativas no coinciden: con las manos intercambiadas el error es0,10, y con la pose en espejo 0,041. La concordancia de bloques de mano en cero es97,5–97,6%, así que las ausencias son no-detecciones genuinas de MediaPipe. Unidades: fracciones de imagen. La pose 15/16 corresponde a las muñecas izquierda y derecha de la persona, verificado visualmente en X3. La convención izquierda/derecha de los bloques de mano se verificará en X8.

Con esto se cumple el criterio preregistrado y R1/ROI quedan desbloqueadas. También queda abierta la opción de reextraer landmarks propios, por ejemplo con mayor complejidad o recortes, aplicando a test la misma transformación fija por muestra.

**X3 · lateralidad.** En las hojas de contacto, M02 hace sign_01 con la mano izquierda en las tres vistas, mientras M03 y M04 usan la derecha. Lo cuantifiqué con la elevación máxima de la muñeca (pose15/16) respecto del reposo final, normalizada por la anchura de hombros:

- **M02 usa la mano izquierda** en72–75 de75 clips de cada clase.
- M03 y M04 son diestros en casi todas las clases. Excepciones: M03 sign_02 18/75 izquierda; M04 sign_04 35/40, probablemente bimanual.

Explicación compatible con los datos: el fold M02 (43,73%) entrena con dos personas diestras y evalúa a una zurda. Es una hipótesis fuerte, todavía no probada causalmente; se pondrá a prueba en X8.

**X7 · vistas.** V01 es frontal; V02 y V03 son tomas laterales de lados opuestos. No son tomas simultáneas:

- solo el4,3% de los pares por índice tiene el mismo T;
- la correlación de energía de movimiento es −0,02, igual que entre clips cualesquiera;
- los rangos de T difieren por vista.

Además, la ropa cambia entre vistas en M02 y M04. Conclusión: cada persona×clase×vista es un bloque de25 ejecuciones grabado en su propia sesión.

**X2 · atajo de sesión.** Clasifiqué solo con estadísticas de color de franjas de borde del primer frame, sin persona (regresión logística):

- **dentro de cada persona separa las cinco clases al99,5–100%**;
- entre personas (LOSO) acierta376/1125 (33,4%; M02170, M03 81, M04 125; azar 20%).

Es decir, cada sesión de clase tiene firma de fondo y luz propia, y esa firma se transfiere solo parcialmente. Riesgos: los modelos sobre el frame completo y las coordenadas absolutas (encuadre por sesión) pueden aprender la sesión. Este canal no se usa como feature; motiva normalizar respecto al cuerpo y centrarse en las manos.

**E13 · semillas de E01.** Reimplementé la receta en `delivery.py`. Con semilla17 reproduce E01 **bit a bit**: diferencia0 y 686/1125. Resultados por semilla (aciertos M02/M03/M04):

| Semilla | Total | Accuracy | M02/M03/M04 |
|---|---:|---:|---|
| 17 (E01) | 686 | 60,98% | 164/280/242 |
| 29 | 674 | 59,91% | 168/278/228 |
| 43 | 677 | 60,18% | 181/278/218 |
| **Promedio 17/29/43** | **676** | **60,09%** | 171/278/227 |

Los nueve modelos se restauraron desde NPY originales en proceso nuevo con diferencia0. El primer intento mostró diferencias de hasta1,6e-6, causadas por un número distinto de hilos en la predicción; se corrigió fijando cuatro hilos y se conservan ambos registros. La semilla17 estaba en el extremo alto. Por la regla de04 §6, la receta vale676 (60,09%) y el campeón honesto ronda el60%. M04 varía24 aciertos entre semillas, lo que da la escala del ruido.

**E14 · bundle.** `bundle_e01_s17_29_43` contiene el refit sobre los1125 clips con3 semillas, cada una con su escalador, combinadas por promedio de probabilidades. Comprobaciones:

- La predicción en proceso nuevo desde NPY coincide exactamente (diferencia0) con la del refit.
- Es invariante al orden. Por muestra individual la diferencia es1,1e-9.
- CPU: 0,27s para375 clips y RSS pico de unos276MiB.

`validate-submission` y `write_submission` están probados con plantillas sintéticas; **no se generó CSV de test**. El bundle queda listo como respaldo entregable; freeze, inferencia test y envío siguen sin autorizar.

**Consecuencia.** El cuello de botella principal identificado es la lateralidad más la dependencia de sesión y encuadre, no la capacidad del modelo. Próximos ítems propuestos en04 §18.
