# Seña a seña - contexto de producto y preparación del pitch

Base de trabajo del 26 de noviembre de 2026. Su propósito es conectar el proyecto implementado con un problema de uso, una propuesta de valor y una posible oferta. El [índice](00_INDEX.md) registra el alcance autorizado. La audiencia y el formato del pitch, el segmento comercial y la solicitud final están por definir.

## 1. Punto de partida y fuentes

**Producto implementado:** un prototipo de práctica con cámara para Café, Aromática, Hola, ¿Qué necesitas? y Con gusto. Ofrece cinco lecciones, una guía por seña, un intento delimitado, una indicación para volver a intentar y un repaso. Reconoce esas cinco señas aisladas; no traduce conversaciones ni cubre toda la LSC.

Este documento es el registro de las hipótesis y decisiones de producto y negocio. Los resultados, contratos y reglas mantienen sus fuentes canónicas:

| Insumo | Para qué usarlo |
|---|---|
| [README](../README.md) | Presentación breve, experiencia visible, atribución y navegación. |
| [Demo](../demo/README.md) y [cliente](../demo/static/app.js) | Recorrido implementado, estados, acceso, captura y envío de landmarks. |
| [Resultados, lectura actual](07_results_and_publication_protocol.md#lectura-rápida-del-resultado-actual) y [verificaciones](07_results_and_publication_protocol.md#22-presentación-pública-y-comprobaciones-de-la-demo) | Cifras, procedencia, límites de evaluación, reproducción y disponibilidad comprobada. |
| [Arquitectura actual](05_technical_architecture.md#17-implementación-actual-y-rutas-de-reproducción) | Viabilidad técnica, entradas, salidas y dependencias reales. |
| [Problema original del reto](01_problem_definition.md) | Vocabulario, reglas, derechos de los datos y frontera del test. |
| [Reporte técnico público](09_reporte_tecnico.pdf) | Método, decisiones y análisis de errores para quien necesite profundidad. |

Consultar las cifras en 07 al preparar cada versión del pitch. La historia experimental completa es material de respaldo, no el punto de entrada obligatorio para entender el producto.

## 2. Problema de uso, personas y valor

**Hecho de diseño:** la experiencia actual está orientada a personas oyentes que empiezan a familiarizarse con este vocabulario. El repositorio documenta esa intención y la aplicación; no documenta todavía una investigación de necesidades con ese público.

**Hipótesis H1:** al practicar una seña siguiendo material de referencia, una persona principiante puede necesitar una indicación concreta para saber qué ajustar en su siguiente intento. La frecuencia, importancia y costo de esa dificultad están por validar.

Trabajo que se propone facilitar: **mirar una seña, intentarla frente a la cámara y tener una pista para volver a intentarla**. El valor que ya se puede mostrar es ese ciclo de interacción. Mejorar el aprendizaje, reducir el abandono o ahorrar tiempo docente son beneficios esperados que necesitan evidencia propia.

| Rol | Estado actual |
|---|---|
| Usuario previsto | Persona oyente principiante; intención de diseño, sin segmento validado. |
| Beneficiario directo propuesto | La persona que practica. Un beneficio para la comunicación con otras personas requiere una evaluación distinta. |
| Referentes lingüísticos y pedagógicos | Personas sordas, docentes y especialistas podrían orientar o evaluar la propuesta; no consta una colaboración acordada para ese fin. |
| Comprador y decisor | Por definir. El usuario individual y una institución educativa serían hipótesis diferentes. |

La oportunidad debe formularse desde una situación concreta de práctica. Una necesidad social amplia de comunicación no demuestra, por sí sola, que este vocabulario de cinco señas sea una solución suficiente o una oferta comprable.

## 3. Experiencia y decisiones de diseño existentes

Recorrido implementado, según el cliente y la documentación de demo:

1. Entrar al servicio con acceso autorizado y consultar el encuadre recomendado.
2. Habilitar la cámara y mirar la guía de una de las cinco señas.
3. Hacer un intento delimitado; el navegador extrae landmarks y los envía al servidor.
4. Recibir un estado de acierto, corrección o incertidumbre, según la predicción y las reglas de la aplicación.
5. Reintentar, pasar a otra seña o entrar al repaso, que inicialmente oculta la guía.
6. Consultar el resultado del repaso y volver a practicar. Ese resultado describe la respuesta del sistema, no certifica competencia en LSC.

| Decisión implementada | Intención de producto | Evidencia pendiente |
|---|---|---|
| Una indicación por intento | Dar una acción concreta para volver a probar. | Que la indicación se entienda y sea lingüísticamente adecuada. |
| Guía, práctica y repaso | Dar continuidad a una sesión corta de práctica. | Retención y transferencia fuera de la aplicación. |
| Estados de acierto e incertidumbre | Comunicar cómo respondió el sistema y permitir reintentar. | Comprensión de esos estados y manejo de falsos aciertos. El umbral no acredita calibración. |
| Mensaje y reintento ante error de conexión | Permitir recuperarse de una predicción que no llegó. | Usabilidad observada en distintos dispositivos y conexiones. |
| Extracción de landmarks en el navegador | Evitar enviar el video de cámara en este flujo. | Comprensión de la privacidad y condiciones de tratamiento de los puntos enviados. |

La [figura de cuatro pantallas](media/sena-a-sena.png) permite explicar el recorrido. Cámara y respuestas están simuladas para ilustrar la interfaz; no es un registro de desempeño con usuarios.

**Acceso y dependencia de activos:** la demo alojada mantiene contraseña. El repositorio público no incluye los pesos ni los activos originales del dataset. La autorización de la figura anonimizada no es una licencia general para esos recursos. Una demostración abierta o una oferta comercial necesitarían resolver sus condiciones de uso.

## 4. Qué demuestra la evidencia

| Dimensión | Evidencia disponible | Interpretación para el pitch |
|---|---|---|
| Clasificación | Evaluación por persona y análisis anidado en [07](07_results_and_publication_protocol.md#lectura-rápida-del-resultado-actual). | Resultado de desarrollo sobre tres personas; persiste optimismo por diseño de rasgos informado por sus errores. No es puntuación oficial. |
| Ingeniería | Reproducción de pesos y predicciones, API comprobada y paridad NumPy frente a PyTorch en [07 §22](07_results_and_publication_protocol.md#22-presentación-pública-y-comprobaciones-de-la-demo). | Respalda que se implementó y verificó un recorrido técnico concreto. |
| Uso con cámara | Ensayos exploratorios de una sola persona oyente. | Ilustran comportamiento y sensibilidad al encuadre; no establecen generalización. |
| Usabilidad y aprendizaje | No hay un estudio registrado con usuarios del segmento ni una evaluación educativa. | La interfaz y el ensayo personal no prueban facilidad de uso ni aprendizaje. |
| Adopción y negocio | No hay entrevistas comerciales, clientes, ingresos o uso recurrente documentados. | La propuesta comercial está por validar. La disponibilidad de una demo no constituye tracción. |

La confianza del modelo no equivale a fiabilidad calibrada. El sistema puede equivocarse al aceptar o rechazar un intento; medir aprendizaje exigiría una valoración independiente del propio clasificador.

## 5. Oferta, venta y sostenibilidad por explorar

Las siguientes son **hipótesis de oferta**, no segmentos elegidos, servicios vendidos o funcionalidades adicionales implementadas:

| Opción | Usuario y posible comprador | Valor a contrastar | Canal por explorar |
|---|---|---|---|
| Práctica individual | Una persona principiante; pago individual por confirmar. | Poder practicar este vocabulario con una indicación entre intentos. | Un canal donde ya busque aprender LSC; alcance y conversión desconocidos. |
| Complemento de un curso | Estudiante como usuario; docente o centro educativo como posible decisor o comprador. | Incorporar una actividad de práctica entre sesiones. | Una prueba acordada con un curso; no hay institución comprometida. |

Para comparar las opciones, documentar quién reconoce el problema, cómo lo resuelve hoy, quién tiene presupuesto y qué compromiso estaría dispuesto a asumir. Clases, tutorías y material grabado son categorías de alternativas por investigar, no una comparación competitiva ya realizada. No se ha demostrado superioridad frente a ellas.

**Precio y modelo de ingresos:** contrastar pago individual, acceso por grupo u otra modalidad solo después de identificar comprador y valor. No hay precio aprobado. Una licencia institucional no implica que existan administración de grupos, reportes docentes o integraciones.

**Costos relevantes:** alojamiento e inferencia, mantenimiento, acceso o creación de contenido autorizado, revisión lingüística y pedagógica, soporte, privacidad y adquisición de usuarios. La exportación NumPy demuestra una alternativa de inferencia; no proporciona por sí sola un costo por estudiante, un margen ni una capacidad de servicio medida.

**Mercado y distribución:** si el pitch los requiere, construir una estimación desde compradores elegibles y gasto anual sustentado. Separar tamaño potencial, compradores alcanzables por un canal y adopción. Incluir fuentes, fechas, rangos y costos de llegar al comprador; no asignar un porcentaje arbitrario de un mercado amplio.

El diferenciador que se puede mostrar hoy es la combinación de práctica con cámara, una indicación por intento e inferencia reproducible para este vocabulario. Su valor frente a alternativas y su dificultad de copia están por contrastar.

## 6. Hipótesis y evidencia que permitiría avanzar

Estas verificaciones son propuestas para una fase posterior. Antes de ejecutarlas se deben acordar alcance, participantes, permisos, recursos y criterios de decisión.

| Hipótesis | Evidencia propuesta | Qué permitiría decidir |
|---|---|---|
| H1: existe una dificultad relevante al practicar | Entrevistas y observación de práctica actual, con ejemplos recientes y alternativas usadas. | Elegir o descartar una situación de uso concreta. |
| H2: la experiencia se entiende y ayuda a corregir un intento | Sesiones observadas con principiantes y revisión de las indicaciones con referentes lingüísticos. | Ajustar o conservar el recorrido y sus mensajes. |
| H3: hay aprendizaje que persiste | Evaluación independiente del modelo, con un diseño pedagógico y seguimiento acordados. | Sostener o retirar afirmaciones de eficacia educativa. |
| H4: un comprador adoptaría una oferta | Conversaciones con decisores y un compromiso verificable de prueba o compra bajo condiciones definidas. | Elegir segmento, oferta, canal y prueba de precio. |
| H5: el sistema responde de forma útil con otras personas | Evaluación nueva, separada del diseño de rasgos, incluyendo falsos aciertos, rechazos y condiciones de captura. | Acotar usos y decidir qué mejoras técnicas serían necesarias. |
| H6: el contenido y la operación permiten el uso propuesto | Condiciones acreditadas de medios, pesos y datos; revisión del tratamiento de landmarks y costos operativos. | Definir qué se puede demostrar, distribuir u ofrecer. |

Acordar las métricas y reglas de avance antes de cada prueba. Separar respuesta favorable, uso observado, mejora de aprendizaje y compromiso comercial: son evidencias distintas.

## 7. Argumento y materiales para el pitch

Formulación breve basada en lo implementado:

> Seña a seña es un prototipo para practicar cinco señas de la LSC con cámara. Permite mirar una guía, hacer un intento y recibir una indicación para volver a probar. Ya cuenta con un modelo evaluado y un recorrido de inferencia reproducible; su utilidad educativa y su posible oferta comercial son los siguientes aspectos por validar.

Una vez definida la audiencia, organizar la historia alrededor de:

1. Una persona y una situación de práctica concreta, con evidencia o hipótesis identificada.
2. La experiencia que se ofrece y una demostración breve de guía, intento y corrección.
3. La evidencia técnica más pertinente, con sus límites cerca de la cifra presentada.
4. El valor esperado frente a la alternativa actual y la validación que falta.
5. El equipo y la capacidad de ejecución: evaluación de alternativas en equipo; implementación, experimentos reproducibles y demo desarrollados por Camilo Cuellar.
6. Una solicitud específica, compatible con la audiencia y el siguiente paso. Podría ser una evaluación, un piloto, una colaboración o recursos; no hay una solicitud elegida ni una alianza confirmada.

El modelo con mejor validación entre las alternativas comparadas no equivale al mejor producto del mercado. Los detalles de arquitectura respaldan la propuesta, pero la apertura debe explicar para quién existe y qué permite hacer.

Materiales disponibles: [vista previa](media/sena-a-sena.png), [instrucciones de demo](../demo/README.md), [reporte PDF](09_reporte_tecnico.pdf), [notebook](../notebooks/01_entrenamiento_inferencia.ipynb) y las fuentes de la sección 1. Preparar una alternativa visual si el servicio no está accesible. No incluir la contraseña ni activos privados en diapositivas o enlaces abiertos.

## 8. Arranque del próximo chat

Completar primero destinatario, objetivo, idioma, duración, formato y solicitud deseada. Si hay una convocatoria o rúbrica, incorporar sus requisitos desde la fuente oficial antes de estructurar el material.

Después, precisar la situación de uso con las observaciones que aporte el usuario y elegir el argumento central. Mantener como hipótesis lo que todavía no tenga evidencia; seleccionar solo las verificaciones que cambien la decisión sobre el producto o la oferta.

La preparación del contexto no selecciona un modelo de negocio ni aprueba nuevas funcionalidades. La base técnica cerrada se reutiliza. Un pitch, una investigación comercial o una mejora de producto posterior tendrán su alcance y evidencia correspondientes, conservando las autorizaciones existentes.
