# Definición del problema: LatAm AI Challenge / LSC5

Encuadre y reglas consultados el 10 de noviembre de 2026, America/Bogota; recursos y techo económico reconciliados el 19 de noviembre. Definición y exploración inicial completadas con incertidumbres explícitas. No constituye un diseño aprobado ni autorización de implementación.

Continuación autorizada: la investigación de la etapa 2 se encuentra en [03_state_of_art.md](03_state_of_art.md), con fuentes y método en [literature/README.md](../literature/README.md). Las exclusiones de investigación de este documento describen el alcance de la etapa 1.

## 1. Lectura y autoridad de las fuentes

Este documento es el registro canónico del encuadre, las aclaraciones y los pendientes. La evidencia numérica detallada está en [02_data_audit.json](02_data_audit_public.json). No duplicar estos registros en nuevos resúmenes o historiales.

| Fuente | Alcance y autoridad |
|---|---|
| [Manual_LSC5.md](Manual_LSC5.md) | Instrucciones locales suministradas por el usuario; conservar el original. El archivo real comienza con `Manual`, no `MANUAL`. |
| [Página oficial: dataset, reglas y evaluación](https://www.latamiachallenge.com/dataset.php#reglas) | Reglas públicas y entregables. Consultada el 10 de noviembre mediante HTTP público con `curl`; el navegador de investigación no pudo abrirla. |
| Aclaraciones del usuario del 10 y 19 de noviembre | Prioridades, fecha límite, composición, recursos y presupuesto. El 19 confirmó dos oportunidades de evaluación y que cuenta la última; feedback y ventanas desconocidos. Distinguirlas de reglas publicadas. |
| [02_data_audit.json](02_data_audit_public.json) | Observaciones locales; alcance y limitaciones de cada comprobación. |

Si aparece una diferencia, conservar ambas versiones y pedir aclaración a la organización; no convertir una inferencia en regla. El manual salta de la sección 4 a la 6: es una irregularidad editorial, no evidencia de una regla perdida.

## 2. Objetivo y frontera del producto

La prioridad del equipo es la posición en el ranking. El uso posterior como portafolio es secundario y no amplía los entregables de esta etapa. Son cuatro integrantes; el usuario confirmó el cumplimiento de la composición institucional exigida.

El problema es clasificación supervisada multiclase de señas aisladas de Lengua de Señas Colombiana (LSC). La página oficial lo enmarca como desarrollo de un modelo de Deep Learning; el manual permite distintas arquitecturas y modalidades. Se conserva ese encuadre sin elegir una solución; si más adelante se considera un método ajeno a Deep Learning, su elegibilidad requerirá aclaración. Cada muestra es un clip ya delimitado, con video y una secuencia de landmarks derivados del mismo video. La respuesta es exactamente una de cinco clases:

| Etiqueta contractual | Nombre del manual |
|---|---|
| `sign_01` | Café |
| `sign_02` | Aromática |
| `sign_03` | Hola |
| `sign_04` | Qué necesitas |
| `sign_05` | Congusto |

La página usa “Con gusto” y presenta índices 0–4; el CSV usa los códigos del manual. Las traducciones son aproximadas; no sustituyen una especificación lingüística de toda la LSC.

Formalmente, para una muestra `x_i` y una etiqueta verdadera `y_i`, se requiere una predicción `y_hat_i` perteneciente al conjunto anterior. La unidad de puntuación es el clip; el reto de generalización es la persona señante ausente del entrenamiento. No se ha establecido cuántas ejecuciones físicas independientes representan los clips de diferentes vistas.

Actores y necesidad: el equipo produce resultados reproducibles, el evaluador contrasta predicciones con etiquetas privadas y las personas grabadas conservan sus derechos y privacidad. El resultado observable es una entrega válida y una Accuracy top-1 competitiva en el test reservado.

La documentación no exige una interfaz de usuario, API, traducción continua, captura en vivo ni despliegue. Tampoco define latencia, disponibilidad, consumo energético o una clase “desconocida”. Esos requisitos no se inventan. Un resultado en estas cinco clases y un solo sujeto reservado no demuestra utilidad de un traductor general ni generalización a la población señante.

## 3. Éxito, calendario y entrega

Accuracy top-1 es la métrica oficial, confirmada por la página y por el usuario:

`accuracy = número de predicciones correctas / número de muestras evaluadas`.

Si se evalúan los 375 IDs distribuidos, un acierto adicional equivale a `1/375`, aproximadamente 0,267 puntos porcentuales. No existe un umbral conocido que garantice ganar. El manual menciona macro-F1 y accuracy como ejemplos; la página concreta la métrica principal. No se ha adoptado otra métrica como objetivo del ranking.

La página permite desempatar por tiempo de envío o criterio secundario, sin fijar cuál. La noticia institucional menciona innovación/calidad técnica, pero no proporciona una rúbrica vinculante. No se infiere una ponderación adicional a la métrica oficial.

| Hito o entrega | Estado / fuente |
|---|---|
| Fecha límite | **25 de noviembre de 2026**, America/Bogota; corrección explícita del usuario durante la etapa 3. Sustituye el 21 comunicado inicialmente. Hora exacta pendiente; no asumir 23:59. |
| Servidor | Ventana pública originalmente 11–18 de noviembre; conexión SSH comprobada el 19. Fecha efectiva de retiro pendiente. Inventario en [08](08_compute_operations.md). |
| CSV de predicciones | Exigido por manual y página. |
| Pesos y código de entrenamiento/inferencia | Exigidos por página. |
| Reporte técnico corto | Exigido por página; formato/extensión no precisados. |
| Carga en plataforma | La página menciona `.ipynb` o `.csv` y una persona que entregue por equipo; empaquetado de pesos/código/reporte pendiente. |

Contrato verificable del CSV, sin producirlo en esta etapa:

- Nombre de entrega: `submission.csv`; encabezado exacto `video_id,predicted_sign`.
- Una fila por ID de la plantilla distribuida en `data/test/submission_template.csv`, sin repetidos, ausentes ni adicionales.
- `video_id` es el nombre base, sin extensión; `predicted_sign` es uno de los cinco códigos.
- UTF-8, comas, dos columnas, sin índice adicional. No hay salida prevista para abstención o probabilidades.
- El manual no precisa si el orden de las filas es obligatorio.
- La plantilla local contiene 375 IDs únicos, coincide con ambos inventarios del test y tiene las predicciones vacías.

La reproducibilidad y el respeto de las reglas son condiciones de admisibilidad y auditoría, aunque la prioridad competitiva sea accuracy.

## 4. Datos disponibles y evidencia local

El manual atribuye LSC5 a la Universidad de Antioquia, con cuatro participantes adultos sordos, cinco señas, tres perspectivas y variaciones de vestuario/fondo. Son afirmaciones de la fuente: esta etapa no audita consentimiento ni validación lingüística. La página confirma captura simultánea desde tres ángulos. No se buscó el artículo ni copias externas del dataset.

| Elemento | Observación local |
|---|---|
| Entrenamiento | 1.125 `.mp4` y 1.125 `.npy`; 225 pares por clase. |
| Sujetos de entrenamiento | `M02`, `M03`, `M04`: 375 muestras por sujeto, 75 por clase/sujeto. |
| Vistas de entrenamiento | `V01`, `V02`, `V03`: 375 por vista, 125 por sujeto/vista. |
| Test | 375 `.mp4`, 375 `.npy` y una plantilla CSV. Etiquetas privadas. |
| Correspondencia de modalidades | Conjuntos de nombres base iguales en cada partición, sin pares faltantes. |
| Encabezados NPY de train | Los 1.125 tienen forma `(T, 1662)`, `float64` little-endian, orden C; tamaño del payload coherente con el encabezado. |
| Longitud de train | Mínimo 33, mediana 55, máximo 97 fotogramas; media 56,2524. |
| Volumen local total | 9.466.230.127 bytes: aproximadamente 9,47 GB decimales / 8,82 GiB. |
| Desglose train | 7.453.132.072 bytes: video 6.611.564.008; landmarks 841.568.064. |
| Desglose test | 2.013.098.055 bytes, incluida la plantilla. |

El tamaño de 8,3 GB anunciado en la web no coincide directamente con los bytes del árbol local; no se conoce si describe un archivo comprimido, otra unidad o versión. No demuestra por sí solo corrupción.

Las carpetas de train y `S##` coinciden en los 1.125 archivos. No hay nombres base de landmarks repetidos. Estas comprobaciones no equivalen a una búsqueda de duplicados por contenido, ni a decodificar todos los videos.

### Muestreo limitado de contenido en la etapa 1

En la etapa 1 se seleccionó el primer nombre lexicográfico por combinación clase/sujeto: 15 pares de train. Todos resultaron ser `V01`; el muestreo cubre las 15 combinaciones, pero no todas las vistas ni es aleatorio. Sus límites describen esa inspección inicial; la ampliación de etapa 3 figura a continuación y en el campo `stage3_training_audit` del JSON canónico.

- Los 15 videos declaran H.264, 1920×1080 y 24 fps; duración de 2,04–2,96 segundos. No extrapolar estos metadatos al resto.
- En esos pares, el número de fotogramas declarado por el contenedor coincide con `T`. No se comprobó alineamiento temporal fotograma a fotograma.
- No se observaron NaN/Inf ni fotogramas enteramente cero en esos 15 arrays. El contenido numérico de los otros 1.110 no fue comprobado.
- Hay segmentos de 63 valores totalmente cero; algunas muestras mantienen uno de ellos a cero durante todo el clip. Interpretarlos como una mano no detectada es una hipótesis, sujeta al orden real de extracción.
- Se observan valores negativos y mayores que uno. No se presupone que las 1.662 características compartan rango o unidad.

El test solo se inventarió por rutas/tamaños y contrato CSV. No se leyeron encabezados o valores de sus NPY, imágenes, audio, duraciones ni otras características audiovisuales. No se identificó a ninguna persona ni se buscaron etiquetas ocultas.

### Ampliación de entrenamiento en la etapa 3

Se comprobaron los 1.125 payloads de train: 63.284 frames y 105.178.008 valores, todos finitos. Los metadatos de los 1.125 videos declaran H.264, 1920×1080, 24 fps y el mismo número de frames que su NPY; no equivalen a decodificación completa ni revisión visual integral.

Bajo el orden de bloques todavía supuesto, el bloque izquierdo es completamente cero en el 62,11% de frames, el derecho en el 52,50% y ambos en el 37,36%. Hay 342 clips con el bloque izquierdo entero cero y 175 con el derecho entero cero, ninguno con ambos durante todo el clip. Las tasas difieren fuertemente por sujeto; no se interpretan automáticamente como fallos de detección o dominancia manual. Se encontró un frame totalmente cero y tres pares de NPY idénticos, dentro del mismo sujeto/clase, con MP4 de hashes diferentes: no justifica deduplicar videos ni inferir ejecuciones físicas.

La ubicación de incidencias, agrupaciones, hashes, métodos y límites se conserva únicamente en `stage3_training_audit`. Esta evidencia sustenta máscaras explícitas, una política para anclas inválidas, diagnósticos por persona/missingness y contraste RGB en el diseño posterior; no demuestra el significado anatómico de cada columna.

### Riesgos de interpretación y fuga

El campo `C##`, denominado cámara por el manual, está asociado con la clase en todos los nombres de train:

| Clase | Campo `C##` observado | Muestras |
|---|---|---|
| `sign_01` | `C01` | 225 |
| `sign_02` | `C02` | 225 |
| `sign_03` | `C03` | 225 |
| `sign_04` | `C04` | 225 |
| `sign_05` | `C04` | 225 |

La asociación es una observación, no una explicación del proceso de captura. No permite afirmar que exista un efecto visual de cámara. `S##`, carpetas, cámara y numeración de clips pueden revelar o correlacionar con etiquetas; no constituyen evidencia de reconocimiento visual. El test no conserva esos nombres. Queda pendiente aclarar la semántica de `C##` y la agrupación de ejecuciones simultáneas.

Solo hay tres personas públicas; los 1.125 clips no representan 1.125 sujetos independientes. Vistas simultáneas pueden representar la misma ejecución física. El manual recomienda LOSO por sujeto y mantener juntas las vistas cuando se divida por ejecución. Se registra esa orientación del organizador, sin diseñar un protocolo experimental.

## 5. Contrato incompleto de landmarks

El manual describe 33 puntos de pose con cuatro valores, 468 de rostro con tres y 21 de cada mano con tres: 543 puntos, 1.662 características. La forma real de train es compatible, pero no demuestra el orden de concatenación.

Para interpretar el muestreo se asumieron posiciones `[0:132]` pose, `[132:1536]` rostro, `[1536:1599]` mano izquierda y `[1599:1662]` derecha. Es una suposición explícita, no un contrato aprobado.

La documentación de [MediaPipe Holistic](https://chuoling.github.io/mediapipe/solutions/holistic.html) distingue coordenadas de imagen, coordenadas mundiales de pose, visibilidad y referencias de profundidad para rostro/manos. Esos campos no son intercambiables. Esto contextualiza el esquema; no identifica qué versión, opciones o campos produjo estos archivos.

Faltan el código/configuración de extracción, orden exacto, lateralidad/reflejo, coordenadas/unidades, convención de valores ausentes y garantía de sincronización con video. No se prescribe limpieza ni transformación mientras esas decisiones pertenezcan a etapas posteriores.

## 6. Integridad, datos externos y privacidad

Reglas del manual, aplicables a cualquier trabajo posterior:

- Test únicamente para inferencia de un modelo fijado. Prohibidos entrenamiento, reentrenamiento, ajuste, calibración, aprendizaje de representaciones, seudoetiquetado y adaptación de estadísticas con test, aun sin etiquetas.
- Una transformación determinista fijada con entrenamiento y aplicada individualmente al test es compatible con el manual. Aprender una estadística del conjunto de test no lo es.
- Prohibido recuperar respuestas mediante copias públicas etiquetadas, metadatos, nombres originales, otros equipos o ingeniería inversa. No explotar el balance declarado del test para ajustar resultados sin aclaración organizativa.
- No ajustar modelos con puntuaciones del test. El usuario confirmó el 19 de noviembre dos oportunidades de evaluación y que cuenta la última. Siguen pendientes ventanas, feedback, tratamiento de rechazos y desempate. Esto no autoriza usar puntuaciones como señal de ajuste.
- No identificar/contactar participantes ni redistribuir archivos fuera de autorización. Los IDs aleatorios no anonimizan las imágenes.
- Conservar evidencia de datos usados, preprocesamiento, validación, modelos y selección cuando se ejecuten esas etapas.

La página permite transfer learning citando su origen; datos externos requieren declaración y criterio del comité. Eso no equivale a permiso general para incorporarlos. El CC BY 4.0 anunciado corresponde al código de procesamiento; la autorización de video/landmarks queda por confirmar. No se ha acreditado una licencia abierta para el material audiovisual.

El usuario no conoce reglas adicionales a manual y página. No hay una regla específica acreditada sobre asistentes de IA. La mención pública de Colab como recurso propio no resuelve por sí sola toda condición de almacenamiento, publicación o transferencia de videos a otros servicios.

## 7. Recursos y restricciones operativas conocidas

El 19 de noviembre se accedió a Cronos por SSH con autorización explícita para inspección. No se subieron datos, aprovisionaron recursos ni iniciaron trabajos de entrenamiento.

| Recurso | Evidencia y límite |
|---|---|
| Equipo local | Disponible según el usuario. El entorno actual expone Intel i5-11400H (6 núcleos/12 hilos), GTX 1650 de 4.096 MiB y unos 4,80 GiB de RAM visibles al proceso; esta RAM puede corresponder al límite del entorno y no al total físico del equipo. |
| Colab gratuito | Disponible según el usuario. Google no garantiza cuota fija diaria ni modelo de GPU; la expectativa de 10 horas/día no es una garantía de capacidad. |
| Servidor UNAB | Cronos accesible por SSH el 19. Hardware, límites de la cuenta y entorno comprobados en [08](08_compute_operations.md), registro canónico operativo. La GPU existe pero está bloqueada para estudiantes. El número de grupos activos y la fecha de retiro no se han comprobado. |
| Gasto | El usuario fijó un techo de USD 10 de desembolso total para el rediseño, incluidos cargos y depósitos. No hay transacción aprobada; admisión y consumo en [06](06_delivery_and_iteration_plan.md). |
| Entorno de inspección | Python 3.10.12 y ffprobe 4.4.2; el intérprete consultado no tiene NumPy ni OpenCV. No se instalaron dependencias. |

La [FAQ oficial de Colab](https://research.google.com/colaboratory/faq.html#resource-limits) explica que disponibilidad, GPU, límites y duración varían; las sesiones gratuitas pueden terminar antes de su máximo. Por tanto no puede calcularse un presupuesto garantizado de GPU-horas a partir de una cuota de diez horas.

La [iniciativa ADA de UNAB](https://noticias.unab.cl/unab-launches-ada-a-pioneering-ai-platform-to-accelerate-scientific-research-in-chile/) describe cómputo institucional, inicialmente en nube, pero no vincula esa infraestructura con el servidor del reto. No permite atribuirle GPU, VRAM ni acceso a AWS. No se extrapolaron equipos de otras universidades.

La ventana de servidor publicada terminaba el 18; la entrega corregida por el usuario es el 25. El acceso comprobado el 19 sustituye el estado anterior de especificaciones desconocidas, pero no acredita disponibilidad hasta el cierre final. Las condiciones verificadas y sus límites se mantienen en 08.

Actualización de etapa 3: el usuario busca aprovechar el cómputo gratuito disponible, con una meta de 16 horas diarias entre cuentas Google. Confirmó que pertenecen a integrantes distintos, cada uno con sus propias corridas y límites, y aceptó la meta como disponibilidad no garantizada. La FAQ de Colab prohíbe el uso de varias cuentas para eludir restricciones. El presupuesto operativo y sus límites se concretan en la documentación de diseño posterior. El repositorio futuro será público; no hay licencia propia elegida. Se expresa interés secundario en un posible artículo, sujeto a evidencia y evaluación posterior.

## 8. Preguntas resueltas y pendientes

Resuelto por el usuario: ranking como prioridad, portafolio secundario, cuatro integrantes con composición conforme, entrega corregida al **25 de noviembre Bogotá**, accuracy top-1, computador propio y Colab gratuito. El 19 aportó el manual de Cronos y autorizó inspección por SSH; resultados en 08. No se requiere volver a preguntar experiencia individual u organización interna para cerrar este encuadre.

Las siguientes incógnitas se conservan como límites concretos, sin pedir al usuario que invente información que todavía no tiene:

| ID | Pregunta pendiente | Responsable / por qué importa |
|---|---|---|
| Q01 | ¿Hora exacta y canal de cierre del 25? ¿Cómo se cargan todos los artefactos? | Organización; validez y puntualidad de entrega. |
| Q02 | Resuelto por el usuario: dos evaluaciones, cuenta la última. ¿Ventanas/frecuencia, latencia y contenido del feedback, consumo de intento por rechazo técnico y desempate definitivo? | Organización; integridad y resultado competitivo. La política conservadora está en 04 §12. |
| Q03 | Inventario y límites resueltos por inspección en 08. La disponibilidad GPU anunciada verbalmente no coincide con los permisos actuales. | Administración UNAB; cualquier habilitación futura requiere nueva comprobación. |
| Q04 | SSH, Slurm, concurrencia y máximo por trabajo comprobados en 08. ¿Fecha/hora de retiro y política de interrupciones? | Administración UNAB; disponibilidad futura sin confirmar. |
| Q05 | Software y entorno comprobados en 08. ¿Conectividad saliente y descarga de pesos autorizada/disponible? | Administración UNAB; no se ensayaron descargas. |
| Q06 | Rutas, espacio compartido y permisos comprobados en 08. ¿Respaldo, borrado, restricciones adicionales y soporte? | Administración/organización; conservación y protección de artefactos. |
| Q07 | ¿Código/configuración de extracción, orden/unidades, ceros, lateralidad y sincronía? | Proveedor de datos; significado de los arrays. |
| Q08 | ¿Clave de ejecución física entre vistas y significado real de `C##`? | Proveedor de datos; dependencia y posibles artefactos de captura. |
| Q09 | ¿Condiciones exactas de video/landmarks para nube, demo y portafolio? | Organización; publicación y uso de datos personales. |
| Q10 | ¿Formato del reporte y atribución requerida para pesos/código externos? | Organización; entrega y auditabilidad. |

No se ha enviado ninguna consulta a organizadores. Las partes resueltas de Q03–Q06 se sustentan en el manual y la inspección del 19; las restantes conservan su carácter externo.

## 9. Cobertura profesional y transición

| Especialidad | Cobertura de esta etapa |
|---|---|
| Producto | Activa: objetivo, actores, prioridad, frontera y entregables integrados aquí. |
| Dominio | Activa: revisión independiente del manual por especialista; reglas y ambigüedades integradas. |
| UX | No aplica diseño de interfaz: no existe requisito acreditado de UI en el encuadre. |
| Arquitectura | Activa solo en contratos de entrada/salida y restricciones; diseño de componentes pendiente de etapa posterior. |
| Implementación | No aplica: excluida explícitamente. |
| Calidad | Activa: contraste documental y revisión independiente de alcance/evidencia. |
| Plataforma | Activa en inventario y preguntas; sin diseño operativo o acceso remoto. |
| ML | Activa: objetivo predictivo, significado de generalización y límites de evidencia. |
| Datos | Activa: inventario y auditoría inicial acotada; sin pipeline ni modificaciones del dataset. |
| Ciencia | No aplica estudio científico, literatura, hipótesis o experimentos en esta etapa. |
| Seguridad/privacidad | Activa en restricciones del manual; no se afirma auditoría técnica o validación legal independiente. |

La evidencia local y las reglas bastan para cerrar la definición del problema con las incertidumbres anteriores. Estas pueden condicionar elecciones posteriores; no autorizan asumir hardware, garantías de cómputo, reglas de envío o licencias inexistentes.

Queda fuera del trabajo realizado: literatura, selección/propuesta de soluciones, diseño de experimentos, arquitectura de implementación, instalación de dependencias, entrenamiento e inferencia. La siguiente sección podrá partir de este registro y de las aclaraciones que lleguen; cualquier diseño/implementación conserva sus propias aprobaciones.

## 10. Método y verificación

La auditoría se ejecutó con Python estándar (`pathlib`, `csv`, `ast`, `struct`, `array`, `math`, `statistics`) y consultas de metadatos `ffprobe`. No se crearon módulos de aplicación o entrenamiento. Para repetir el muestreo, ordenar lexicográficamente rutas NPY de train y tomar la primera por cada par `S##,M##`.

Para todos los NPY de train se verificaron firma, forma y tamaño esperado por cabecera; para los 15 seleccionados, finitud, extremos y ceros. Los rangos de bloques usados figuran en la sección 5 y la lista exacta de muestras está en el JSON. `ffprobe` consultó codec, dimensiones, fps, duración y número declarado de frames, sin decodificación completa. El JSON guarda el SHA-256 del manual, versiones y limitaciones; no contiene hashes de todo el dataset, por lo que no certifica su inmutabilidad.

Investigación pública acotada: sitio oficial del reto y noticias de UNAB para contexto/recursos; documentación primaria de MediaPipe y Colab para semántica y límites. La [noticia institucional del 9 de noviembre](https://noticias.unab.cl/ingenieria-unab-impulsa-desafio-internacional-de-ia-para-promover-la-inclusion/) confirma el contexto binacional; no sustituye las reglas operativas. No se realizó búsqueda bibliográfica ni descarga de copias externas de LSC5.

Revisión independiente de calidad: se recontaron los pares y se contrastaron los 1.125 encabezados NPY, tipos/tamaños/longitudes, contrato de plantilla, hash del manual y enlaces locales; resultado conforme. Se incorporaron dos correcciones: explicitar el encuadre oficial de Deep Learning y corregir la referencia a los rangos de bloques. La revisión no certifica los contenidos no muestreados, permisos, hardware UNAB ni decisiones experimentales futuras. La aceptación humana conserva su propio alcance.
