# 06 · Ejecución, presupuesto y entrega · revisión R2.1

Propuesta del 19 de noviembre de 2026. Objetivo principal: accuracy top-1 en el reto; entrega el 25 de noviembre, Bogotá, hora exacta pendiente. Experimentos y umbrales en [04](04_solution_and_experiment_design.md), contratos en [05](05_technical_architecture.md), infraestructura en [08](08_compute_operations.md), aprobaciones y foco en [00](00_INDEX.md). No contiene resultados de modelos.

## 1. Restricciones y autoridad

| Condición | Estado / consecuencia |
|---|---|
| Ranking primero; portafolio y posible artículo secundarios | Decisión del usuario. No ampliar el alcance para publicación antes de completar la entrega. |
| USD 10 de desembolso total | Última corrección explícita del usuario; sustituye la consulta de USD 6 y el escenario previo de USD 5. Incluye depósitos, impuestos, comisiones y conversión. No es una aprobación de una transacción concreta. |
| Cronos CPU | Inspección autorizada por SSH y completada. Sus permisos no incluyen GPU; inventario canónico 08. |
| Colab/local | Respaldo disponible, sin horas garantizadas. No constituye dependencia para cumplir el plan base. |
| Datos y pesos externos | Uso sujeto a reglas del reto, procedencia y permisos. No incorporar datasets nuevos ni publicar datos privados. |
| Implementación y uso de otra cuenta | Pendientes de aprobación del diseño/ítem y mecanismo de servicio. La autorización SSH existente se limita al ámbito Cronos. |

La entrega local es el endpoint actual; no hay repositorio Git inicializado ni publicación o PR acordados. Se conserva la revisión del primer ítem y su especificación/OpenSpec antes de implementar. El modo de entrega se registra una sola vez en 00 y no elimina rigor ni gates existentes.

## 2. Dos presupuestos distintos: caja y consumo

El límite innegociable de caja es `cash_paid_usd <= 10`, incluyendo el total final de cada pago y sus cargos externos. Un prepago de USD 10 ya consume toda esa caja aunque se utilicen solo USD 3 de cómputo. Los créditos promocionales no son efectivo del equipo y su disponibilidad no se presupone.

Se propone un **objetivo de consumo facturable de hasta USD 7**, con USD 3 de margen respecto del techo. No autoriza pagar USD 10 y luego gastar USD 3 adicionales en impuestos. Si un proveedor obliga a depositar USD 10, solo es elegible cuando el desembolso final completo es ≤ 10; cualquier saldo no consumido queda dentro de ese prepago y no paga comisiones bancarias externas.

| Uso previsto del consumo | Tope inicial USD | Decisión al alcanzarlo |
|---|---|---|
| Preparación facturada y piloto GPU | 0,50 | Si no se obtiene un piloto íntegro, cerrar el intento y usar respaldo. |
| Extracción train, global y ROI si se admite | 2,00 | Estimar ambas vistas y bytes; reducir aK=8 o una vista antes de OOF, o cerrar RGB. |
| Adaptación opcional, incluidos folds/semillas/refit requeridos | 2,00 | Abrir solo si la proyección completa cabe; nunca financiar únicamente el primer fold. |
| Inferencia final y extracción seleccionada | 1,00 | Reserva protegida hasta demostrar alternativa local/CPU viable con train. |
| Almacenamiento y transferencias | 0,50 | Medir bytes/tarifas; no asumir que parar una instancia termina el cobro. |
| Contingencia de reintento/cierre | 1,00 | Uso documentado; no abre nuevos experimentos. |
| **Consumo objetivo máximo** | **7,00** | Frente al techo de caja USD 10; el margen restante no está comprometido a variantes. |

La redistribución entre partidas solo se permite antes de iniciar una unidad, conservando el tope global y la reserva de finalización. Para cada lanzamiento: `costo_comprometido + costo_restante_estimado*1.5 + reserva_final <= consumo_disponible`. Se incluyen entorno, cola facturada, I/O, almacenamiento, exportación, intentos fallidos y limpieza. Tener saldo no obliga a gastarlo.

El piloto convierte precio en costo de tarea. La estimación de tiempo usa la cadena completa; una GPU más barata por hora puede ser peor por imagen si su CPU/red es lenta. El piloto R0/MLP ya tiene una medición específica; todavía no acredita velocidades de los modelos temporales/visuales ni garantiza completar48 ajustes.

## 3. Proveedores candidatos y puerta de selección

Precios/condiciones consultados el 19 de noviembre de 2026. Son fuentes públicas, no una cotización de cuenta. No se registró una cuenta, recargó saldo, provisionó una instancia ni transfirieron datos.

| Opción | Evidencia primaria | Tratamiento propuesto |
|---|---|---|
| Modal Starter | [Precios oficiales](https://modal.com/pricing): USD 30/mes de cómputo incluido. T4: USD 0,000164/s; L4: USD 0,000222/s. Con 2 núcleos CPU y 8 GiB, cálculo propio≈USD 0,7487/h o 0,9575/h. | Primera opción a verificar si los créditos están disponibles y el alta/uso no exige desembolso incompatible. No se depende de obtenerlos. |
| Runpod | [RTX 4090](https://www.runpod.io/gpu-models/rtx-4090): Community USD 0,34/h; Secure USD 0,89/h, disponibilidad variable. [Guía de financiación](https://www.runpod.io/blog/manage-runpod-account-funding), actualizada el 22 de octubre de 2026: depósito mínimo por tarjeta USD 10. | Ahora puede caber, exclusivamente si checkout y cargos totales no superan USD 10. Confirmar oferta, disco y pago antes de provisionar. |
| Vast.ai | [Quickstart](https://docs.vast.ai/guides/get-started/quickstart): depósito mínimo USD 5. [Tarifas](https://docs.vast.ai/guides/instances/pricing): precio de mercado, disco y tráfico separados. | Alternativa con menor anticipo, condicionada a oferta y control de cierre; no asignar una tarifa de GPU sin cotización. |
| Cronos + local | Infraestructura ya comprobada; sin compra adicional. | Ruta de continuidad si falla el alta, no hay GPU elegible o el checkout excede caja. RGB congelado solo si el piloto local entra en plazo. |

Las cifras Modal son cálculo de consumo base, no costo total garantizado; cargos regionales/impuestos o recursos adicionales pueden cambiarlo. Con créditos utilizables, el consumo sigue registrándose aunque el pago sea cero. No crear varias cuentas para multiplicar beneficios.

La [documentación Modal de presupuestos](https://modal.com/docs/guide/budgets) distingue límite de uso bruto y límite de gasto neto tras créditos. Antes de ejecutar se debe comprobar el límite de workspace y el gasto neto configurado; para usar solo créditos, proponer gasto neto 0 si la cuenta lo admite. No atribuir al plan Starter presupuestos por Environment que requieren otro plan.

En Vast, la [política de saldo negativo](https://docs.vast.ai/guides/reference/billing) permite cobros a tarjetas guardadas por saldo negativo y continúa cobrando almacenamiento en instancias paradas. Desactivar recargas automáticas no constituye por sí solo un límite duro. Solo usar con un control verificable de gasto/cierre, vencimiento previo al saldo crítico y recuperación seguida de eliminación de recursos propios. Si no se puede asegurar el límite, elegir otra opción.

Selección propuesta, después de tener código listo: comprobar primero Modal y sus límites; en paralelo comparar una cotización Runpod de USD 10 finales o Vast de USD 5 finales. Elegir **un único proveedor**. El usuario acuerda mecanismo MCP o manual para ese ámbito antes de usar su cuenta; si no hay MCP suficiente, se presentan pasos manuales. No repetir esa pregunta una vez resuelta para el ámbito elegido.

El uso de un proveedor requiere verificar la transferencia autorizada de train y de artefactos. Para test, preferir la ruta CPU/local ensayada; cualquier GPU externa final usa exclusivamente el bundle congelado y sus muestras independientes, dentro del mismo permiso. No se envían credenciales Cronos al proveedor ni se reutilizan contraseñas.

## 4. Registro económico y admisión de trabajo

Un único `budget.json` privado posee: moneda, techo de caja, pagos/recibos y cargos, saldo prepago, créditos gratuitos, consumo medido, costo comprometido pendiente y reserva final. También agrega horas-trabajo CPU consumidas y pendientes desde todos los runs, incluidos pilotos, fallos y repeticiones. Cada run referencia sus entradas de costo; no se duplica un saldo manual en otro tracker. No guardar números de tarjeta ni secretos. El ledger CPU activo reside en Cronos según08; sus copias locales son snapshots de evidencia. El incremento R2-E01 añade un alcance de3600s sin reiniciar historial, dentro de los límites globales anteriores; AC y evidencia pertenecen al [ítem de línea base](../openspec/changes/archive/2026-11-19-cpu-baseline-loso/tasks.md).

Se declara un valor máximo por transacción antes de confirmar checkout. No iniciar recursos si el medio de pago no permite conocer o acotar impuestos/comisiones a ≤ 10 acumulados. Cuando ya se pagó un prepago de 10, no hay presupuesto para otra recarga. Un reembolso potencial no se cuenta como caja disponible hasta acreditarse.

El runner propone un deadline de proceso y concurrencia 1 en GPU. El corte local de entrenamiento no prueba que la infraestructura deje de facturar: deben verificarse estado final, disco y cargo cerrado. Desactivar reintentos automáticos cobrados y jobs periódicos. La operación de cierre entra al mismo ítem aprobado; no se deja una instancia activa esperando decisiones.

Antes de cada unidad CPU: `horas_consumidas + horas_pendientes_comprometidas + nueva_unidad_estimada*1.5 + reserva_final <= 48`. Lo consumido nunca se libera al terminar una ola: incluye pilotos, éxitos, fallos y repeticiones. Reservar inicialmente 12 horas-trabajo para refit, inferencia y recuperación; las comparaciones y confirmaciones comparten las 36 restantes. Al ejecutar trabajo de finalización, trasladar su costo de reserva a comprometido/consumido, sin contarlo dos veces. No lanzar todas las variantes por tener dos slots. Solicitar memoria por piloto, evitando reservar 32 GiB sin necesidad.

CPU y caja se agotan de manera distinta. La cuota CPU gratuita no habilita retrasar la entrega, y tener GPU pagada no habilita entrenar más variantes si faltan confirmaciones o código estable.

## 5. Calendario actualizado en Bogotá

Este calendario sustituye el orientativo del 10 de noviembre. No afirma que se hayan completado hitos anteriores. El servidor reporta UTC−03; convertir sus logs a Bogotá UTC−05 al contrastar plazos.

| Fecha / corte | Resultado esperado | Acción si no se alcanza |
|---|---|---|
| 19–20 nov | Decisión R2, fundación/primer ítem revisados, esquema mínimo y piloto CPU; dejar una baseline reproducible. | Priorizar R0 y recorrido completo. No alquilar para depurar código sin probar. |
| 20–21 nov | Núcleo LOSO y extracción fija si el proveedor pasa puertas. Cachés recuperables y resultados OOF completos. | Mantener solo modelos cuyo costo/protocolo se completó; reducir olas opcionales. |
| 21–22 nov | Comparación RGB y de representación, controles, posible E11 si cabe. | Cerrar adaptación cuando amenace finalización; conservar baseline congelada. |
| 22 nov 18:00 | No abrir nuevas ramas. | Cualquier tiempo restante va a confirmar/restaurar y documentar. |
| 23 nov 12:00 | Congelar receta, semillas comunes y combinación con evidencia. | Elegir el mejor candidato completo; no completar a medias una búsqueda. |
| 23–24 nov 12:00 | Refit, restauración y preparación del bundle; inferencia fija después de congelar. | Usar recuperación prevista o candidato ya validado; preservar integridad. |
| 24 nov 12:00, objetivo para evaluación 1 | Bundle, CSV, pesos, código y reporte comprobados; efectuar el envío competitivo si está autorizado y la ventana lo permite. | Adelantar si la plataforma tarda en evaluar; no improvisar una baseline para obtener feedback. |
| 24 nov 18:00, reserva para evaluación 2 | Recuperación técnica si hace falta y las reglas la admiten; preservar concordancia de artefactos. | Si el primero fue correcto, conservarlo sin gastar el intento por obligación. |
| 25 nov | Entrega por canal/hora confirmados; conservar recibo. | No asumir cierre 23:59 ni extensión. |

Si el piloto indica que el refit supera la reserva, adelantar congelación. La fecha efectiva de retiro Cronos sigue sin confirmar: copiar artefactos al cerrar cada corrida, mantener dependencias restaurables y ensayar continuidad local. No presupuestar sesiones Colab de 16 horas como reserva asegurada.

## 6. Mapa de trabajo y criterios candidatos

Se conserva una sola especificación por ítem. Los siguientes AC son candidatos hasta la revisión de la propuesta/OpenSpec correspondiente. La tabla define cobertura futura; la disponibilidad efectiva y sus límites se acreditan únicamente en los ítems ejecutados enlazados debajo.

| Ítem R2 | Entrega y dependencias | Criterios verificables candidatos |
|---|---|---|
| W00 · contrato y piloto | Leer train/overlays acreditados y 08; habilita transformaciones semánticas. | AC00.1 layout/índices/unidades/ceros con evidencia; si no, perfil opaco. AC00.2 frame cero/padding distinguidos. AC00.3 costo CPU medido y finalbatch probado, sin test. |
| W01 · base reproducible | Manifest, splits, configs y paquete; depende W00 para perfiles semánticos. | AC01.1 comandos/entornos fijados. AC01.2 contaminación entre roles rechazada. AC01.3 resultados/errores/checkpoints trazables. |
| W02 · recorrido y núcleo | R2-E01–E03; depende W01. | AC02.1 una corrida pequeña restaura y predice train desde originales. AC02.2 nueve ajustes completos o descartes técnicos explícitos. AC02.3 OOF cubre 1.125 IDs por receta elegible, métricas por persona y costo. |
| W03 · frontera GPU/caché | R2-E07; depende W01 y aprobación del servicio/pago/transferencia. | AC03.1 checkout≤caja restante y reserva verificada. AC03.2 peso/crop/shards/IDs íntegros. AC03.3 reanudar omite clips completos. AC03.4 cierre y costo documentados. |
| W04 · comparaciones baratas | E04–E06 y E08–E10; depende núcleo/caché según rama. | AC04.1 cada cambio conserva padre/protocolo. AC04.2 escaladores dentro de fold. AC04.3 promociones/descartes con umbrales 04 y resultados completos. |
| W05 · adaptación opcional | E11; depende RGB útil, replay válido y presupuesto completo. | AC05.1 prefijo fijo y adaptador fold-local. AC05.2 costo de confirmación/refit incluido antes de abrir. AC05.3 parar rama si no cabe; encoder congelado conserva candidatura. |
| W06 · decisión y confirmación | E12/E13; depende comparaciones admitidas. | AC06.1 reglas 50/50 y conjunto común de semillas. AC06.2 todos los intentos preservados. AC06.3 selección/freeze reproducibles sin test. AC06.4 cada ola registra hipótesis, ganados/perdidos y decisión según 04 §11; cierre por costo/plazo. |
| W07 · refit e inferencia | E14/E15; depende W06. | AC07.1 reentrenar con todo train y estados finales. AC07.2 inferencia independiente, portable y sin caché train obligatorio. AC07.3 CSV exacto y hashes. |
| W08 · reporte y entrega | Pesos/código/CSV/reporte; depende W07. | AC08.1 atribución/licencias y limitaciones honestas. AC08.2 restauración y guía probadas. AC08.3 canal/recibo de entrega reales, si se autoriza envío. AC08.4 antes de publicar, revisar archivos, historial, permisos y exclusiones según 07. AC08.5 política de dos evaluaciones/última vigente y vínculo CSV–bundle–acuse comprobados. |

El primer incremento cubre W00/W01 y el recorrido mínimo de W02, con piloto breve y sin compra. Su [propuesta OpenSpec](../openspec/changes/archive/2026-11-19-cpu-pilot-walking-path/proposal.md) posee los AC P1–P8, límites y evidencia; sus [tareas](../openspec/changes/archive/2026-11-19-cpu-pilot-walking-path/tasks.md) poseen ejecución. La autorización vigente se registra solo en00. La tabla anterior conserva cobertura futura, sin duplicar los AC del incremento. Las olas siguientes pueden aprobarse como una secuencia concreta cuando su costo esté medido; no se solicita permiso de nuevo para cada paso ya cubierto.

## 7. Evidencia y recuperación entre sesiones

El estado del proyecto y la autorización se mantienen en 00. Cada ítem activo actualiza aquí su alcance/AC/evidencia; no crear handoffs ni diarios paralelos. Al recuperar una sesión: índice, ítem, protocolo/contratos pertinentes, registro de runs y presupuesto privado; no recargar toda la biblioteca.

R2 comenzó como diseño sin implementación ni métricas. El primer incremento ya entrega el recorrido R0/MLP; su [registro de tareas y evidencia](../openspec/changes/archive/2026-11-19-cpu-pilot-walking-path/tasks.md) posee resultados por AC, mediciones del piloto y límites. El incremento [R2-E01](../openspec/changes/archive/2026-11-19-cpu-baseline-loso/tasks.md) añade los tres ajustes completos y OOF; su interpretación está en07 §8. La disponibilidad del catálogo completo no se infiere de esos recorridos. Cada corrida informa `planned`, `running`, `complete`, `failed` o `interrupted` en su propio artefacto; no son estados de aprobación humana.

Conservar config, versiones, split/fitIDs, cache keys, logs, checkpoint, OOF, duración/memoria/costo, resultado y justificación de selección. No informar solo el mejor ensayo. Antes de cerrar sesión se debe poder identificar último ajuste completo, recuperación válida y siguiente acción autorizada desde los registros canónicos.

## 8. Riesgos y límites del alcance

Los mayores riesgos son esquema erróneo, atajos de captura, poco tiempo de implementación, cola/retiro Cronos y gasto en extracción sin reserva final. Sus tests/kill criteria se poseen en 04; su materialización técnica en 05. Esta revisión no garantiza cabida ni un puesto en el ranking.

El artículo eventual permanece secundario y se rige por [07](07_results_and_publication_protocol.md). El análisis de tres personas y la selección repetida sobre LOSO limitan inferencia; una victoria tampoco demostraría generalización poblacional. No se inventan consentimiento, licencia de datos, resultados o aceptación editorial.

Pendientes externos vigentes: hora/canal de cierre, ventanas/latencia/feedback/rechazos/desempate, detalles del extractor, condiciones de transferencia/publicación, retiro/respaldo Cronos y cuenta/oferta final del proveedor. El número de evaluaciones y que cuenta la última ya están resueltos por el usuario. Los resueltos no se vuelven a preguntar; los desconocidos se tratan como restricciones con respaldo.

## 9. Operación de las dos evaluaciones

La política de selección e integridad pertenece a 04 §12. El calendario anterior es un objetivo local, no una ventana oficial. Confirmar Q01/Q02 de 01 antes de programar el envío. Planificar hacia atrás con `D` cierre efectivo, `W1/W2` cierres de ventanas de carga, `L1/L2` latencias hasta aceptación/diagnóstico técnico accionable de cada oportunidad, `R` tiempo de reparación y revalidación, y `M` margen operativo. Registrar fuentes o supuestos de cada valor; la latencia de mostrar accuracy no es necesaria para entrenar o seleccionar.

Para reservar una recuperación secuencial: `ultimo_envio2 <= min(W2, D-L2-M)` y `ultimo_envio1 <= min(W1, W2-L1-R, D-L1-R-L2-M)`. Si existe una sola ventana, usar su mismo cierre para W1/W2. El margen debe ser positivo, propuesto inicialmente de seis horas y ampliado si la conectividad/servicio lo requiere. Por ejemplo, dos latencias técnicas de 24 horas exigen más de 48 horas antes de D para el primer envío al incluir R y M; esperar hasta el 24 sería incompatible con ese escenario. Es un ejemplo de planificación, no una latencia medida.

Si el cálculo exige adelantar el objetivo del 24, adelantar también freeze/refit y cerrar antes las ramas opcionales. Comprobar también aperturas y zona horaria de ambas ventanas. Una ventana de carga distinta o evaluación posterior al cierre solo cambia estas restricciones con confirmación organizativa. Mientras falten valores, los objetivos del calendario no certifican margen para ambos intentos. No asumir cierre a las 23:59 ni evaluación inmediata.

Antes del primer envío, verificar restauración independiente del bundle, CSV exacto, hashes, artefactos y canal. Fijar quién ejecuta la carga y conservar acuse/hora de Bogotá. Una validación de la página puede consumir intento: no usarla como linter ni enviar archivos ficticios para ensayar. Los controles locales no consumen oportunidades.

La segunda oportunidad no se programa como una nueva búsqueda. Si hay fallo técnico, comprobar qué fue aceptado y si cuenta como intento; recuperar el CSV correcto o corregir el defecto permitido con evidencia local y volver a verificar. Si solo hay una puntuación decepcionante, el modelo queda fijado. Registrar la respuesta oficial como resultado, no como señal para producir un challenger. La última entrega efectiva debe concordar con los pesos/código/reporte.

Mantener la reserva de recuperación económica hasta acreditar entrega válida o cerrar su ventana; no dejar una GPU facturando mientras se espera la página. Usar contingencia para corrección técnica solo si cabe en la caja/consumo restantes. Volver a cargar un CSV ya generado no exige entrenar ni pagar otra sesión GPU. Si se requiere repetir inferencia, aplicar la misma admisión y bundle fijado; un error no amplía el presupuesto.

Si el primer envío fue correcto, una oportunidad sin usar es un resultado operativo válido. No existe garantía de poder recuperar la primera puntuación después de reemplazarla. Conservar la evidencia de ambos intentos si los hubo y verificar cuál reconoció la organización; no inferirlo únicamente del orden de archivos locales.


## 10. Continuidad autorizada sin extractor acreditado

R2.2 es una adaptación aprobada por el usuario, definida en04 §13; contratos en05 §13 y aceptación en el [ítem temporal opaco](../openspec/changes/archive/2026-11-20-opaque-temporal-tcn/proposal.md). Su alcance específico máximo es3600 segundos-trabajo y no autoriza compras. E02O ocupa los tres slots E02 de esta ola; E02/R1 no se ejecuta además sin reconciliación. Ramas con anatomía y ROI continúan condicionadas. El presupuesto global, caja, semilla común, cortes del22/23 y política de evaluaciones no cambian. El piloto debe acreditar cadena completa y finalización a tiempo antes de reservar sus folds. Si no pasa, conservar baseline y evaluar la ruta RGB global mediante sus propias puertas, sin dejar recursos activos esperando respuesta externa.


**Cierre operativo E02O,20 nov.** Único ledger activo conserva21s previos; nuevo alcance `opaque-temporal-tcn` consumió167s (piloto19s; folds51/51/46s), pendientes0, total acumulado188s. Tiempo asignado Slurm, no duración extremo a extremo ni suma de CPU-segundos. Alcance autorizado3600s, máximo global172800s y reserva final43200s intactos; el remanente del alcance no autoriza variantes adicionales. Cero jobs activos al cierre y cero desembolso; USD10 de caja disponibles, sin transacciones. Ajustes completos acumulados: seis (tres E01 y tres E02O); los pilotos de dos épocas conservan contabilidad separada y no son candidatos completos.

Reservas comprobadas:360s piloto y960s por fold; TimeLimit300/900s y KillWait30s, márgenes de terminación60s. Gate medido118,544s por fold con factor1,5 y arranque, dentro de900s; cadena reservable2880s más piloto dentro del alcance. Piloto preparó caché en11,759s y cargó/escaló en2,849s, con33 pasos medidos tras5 de calentamiento; probe60 fit-only descartado conforme. Pico RSS del proceso piloto1556920KiB y máximo observado en folds1582628KiB (aprox.1,51GiB), dentro de8GiB solicitados. MaxRSS de sacct vacío: no se presenta como medición de memoria completa del job. Restauración local completa medida en receipts; preparación/transferencias/OOF no tienen instrumentación extremo a extremo comparable con E01, por lo que no se acredita promoción por costo.

Jobs43–46 completos y liquidados exactamente una vez; una consulta contable antes de terminar44/45 fue rechazada, sin liquidar ni repetir entrenamiento, y se conserva como evidencia. Máximo dos jobs activos; M04 se presentó después de cerrar44/45. Admisión el20 nov, anterior al corte22 nov18:00 con margen para ejecución/restauración. Disponibilidad futura de Cronos y hora/latencia de entrega oficial siguen pendientes; no se deducen de este éxito. Las dos evaluaciones permanecen intactas y rige§9: una entrega competitiva tras freeze, segunda como recuperación técnica; cuenta la última, sin aprendizaje del test. Resultado y siguiente recomendación en07 §9.


## 11. Admisión y operación del piloto RGB local

Incremento siguiente a E02O: preparar y medir30 clips train/R4 en GTX1650 propia, sin cuenta externa, pago, transferencia de videos ni entrenamiento de cabeza. El usuario aprobó la implementación y el único piloto concreto de [este ítem](../openspec/changes/archive/2026-11-20-rgb-global-pilot/proposal.md) mediante «Apruebo»,20 nov2026, después de revisión de diseño conforme. Cierre esperado del ítem: admitir propuesta E07/E08 o detener/escalar por evidencia; ninguna extracción1125, refit o test se activa automáticamente.

Tiempo de trabajo de implementación/preparación: máximo2h antes de reevaluar si falta una dependencia esencial; instalar/descargar en entorno separado tiene máximo60min. Ejecución medida: un intento, TimeLimit de proceso600s más60s de terminación, reserva660s, estimación inicial300s×1,5≤600s. Propuesta de alcance local `rgb-global-pilot`660s. Es reserva de trabajo gratuito, sin factura. Para mantener una sola contabilidad, agregar reserva/consumo al ledger activo de Cronos antes/después de ejecutar localmente; marcar `execution_kind=local_gpu_pilot` y tiempos locales, sin inventar job Slurm. Por prudencia se carga todo el tiempo de este proceso al límite de horas-trabajo existente, aunque parte use GPU; registrar aparte CPU/GPU activas y no duplicar saldos. No alterar los188s históricos, reserva final43200s ni caja. Si no puede reservarse o reconciliarse, conservar evidencia y no abrir otro intento. Preparación/descargas y exploración de solo lectura tienen tiempos separados, sin presentarlos como duración de entrenamiento facturado.

Un único proceso GPU propio, sin trabajos simultáneos de entrenamiento local. Antes de iniciar:≥2GiB de RAM disponible,≥3GiB VRAM libre y≥8GiB de disco; si falla, no ejecutar. Instrumentar VRAM asignada/reservada, RSS del proceso y decoder, tiempos de conteo/decodificación/preprocesado/forward/escritura/hash/restauración, bytes y versiones. Límite conservador de reserva PyTorch3GiB y observar memoria global de GPU; no confundirla con la memoria del proceso. Durante ejecución, un supervisor propio muestrea cada100ms la RAM disponible y RSS agregado del proceso/decoder: detener si disponibilidad<512MiB o RSS agregado>2GiB. Registrar máximos y causa; son umbrales preventivos, no una garantía ante cambios instantáneos. Terminar exclusivamente el grupo de procesos propio con SIGTERM, esperar como máximo10s y aplicar SIGKILL si persiste, siempre dentro de los60s de gracia. Detener también ante OOM, error de integridad, plazo o falta de recursos; no cambiar K/batch/float32 o repetir una ejecución fallida automáticamente.

Tras warm-up de5 batches, medir al menos10 batches y30 costos completos por clip con sincronización CUDA. Proyección de extracción:1,5×(1125×mayor costo por clip+arranque/escritura final), más `1,5×375×mayor costo por clip train` como referencia de inferencia final, a partir de los mismos30 clips. Es una extrapolación condicionada a longitudes similares, no una garantía sobre videos desconocidos; no leer test para medirla. La medición de restauración en proceso nuevo se conserva. Al menos1h de margen operacional antes del corte de nuevas ramas22 nov18:00 Bogotá; cerrar la propuesta de nueva rama si su proyección/cola no cabe. Los costos de cabeza/confirmación/refit todavía no están medidos: no declarar admitida la cadena completa solo por superar el piloto del encoder.

Si el entorno o peso no funcionan, conservar USD10 intactos y presentar una opción Colab/gratuita o pagada con acceso/licencia/cotización/cierre verificados. El primer uso de una cuenta externa sigue requiriendo acordar MCP o pasos manuales. No se cambia la política de dos evaluaciones: ninguna se consume durante este piloto.


**Resultado y cierre operativo,20 nov.** Entorno CUDA separado instalado y comprobado; fuente/peso oficiales descargados (transferencia medida18,543s) y operación CUDA mínima18,411s, separados del tiempo del intento. No se instrumentó toda la preparación/autoría como una sola duración. La instalación terminó dentro de la puerta60min, sin dependencia esencial pendiente. Reserva660s y un único claim local; admisión fresca del supervisor observó2,414GiB RAM disponible,3,843GiB VRAM libre y863,6GiB de disco, antes del corte. El supervisor ejecutó265,506856442s y terminóFAILED por OOM al inicializar CUDA en replay. No hubo reintento, workers propios restantes ni recursos alquilados. Límites y memoria/resultados detallados en07 §10; el error no se convierte en un replay conforme.

Liquidación única `local_gpu_pilot`, sin ID Slurm:265,506856442s cargados una sola vez al límite de trabajo. Los188s históricos se conservan; total453,506856442s,0 pendientes, reserva final43200s intacta, límite172800s. Desembolso0; techoUSD10 intacto y seis ajustes completos acumulados, sin sumar este encoder congelado como ajuste. El campo forward del recibo fallido queda sin valor; los12,914s medidos de forward de extracción están en sus métricas y no se suman otra vez al saldo. La copia local del ledger recuperada por stdout está anonimizada por el transporte SSH; su diferencia de rutas de cuenta no representa modificación del ledger canónico. La comprobación remota de digests conserva la comparación de históricos sin publicar accesos.

**Decisión del primer intento: admisión bloqueada por replay.** Las proyecciones de07 §10 son diagnósticas: ni el presupuesto disponible ni la velocidad permiten saltarse G3. No reservar extracción1125/E08, repetir el intento ni usar un proveedor nuevo a partir de este alcance agotado. Siguiente incremento propuesto: diagnóstico acotado de inicialización CUDA con criterio de estabilidad/replay y su propio límite aprobado; mantener el resto del calendario y la política de evaluaciones. No hay freeze competitivo ni autorización de envío.


## 12. Reintento RGB autorizado explícitamente

20 nov2026: el usuario pidió volver a intentarlo. Autoriza una sola ejecución adicional completa30/K16+replay, sin modificar protocolo, precisión, fuente/peso o entorno. Alcance separado `rgb-global-pilot-retry`660s, TimeLimit600s+60s terminación; conserva el original y sus453,506856442s acumulados, caja0 y reserva final43200s. Preparación/ajuste mínimo≤1h antes de reevaluar, sin instalar dependencias. Reservar antes de ejecutar y liquidar consumo real incluso en fallo. No reutilizar claim/salida/marcador, reiniciar contadores, encadenar intentos o ejecutar cabezas/test. La petición directa autoriza este alcance concreto y las comprobaciones necesarias; no requiere otra confirmación. Resultado pendiente en07 §11.

Si el replay pasa, reportar ambos intentos y conservar la mayor proyección observada al preparar una futura extracción, sin seleccionar por optimismo de caché caliente. El éxito de este reintento no elimina el fallo anterior ni acredita estabilidad indefinida o calidad de clasificación.


**Resultado operativo del reintento,20 nov.** Intento02 reservado660s y reclamado una vez, ligado al recibo del original fallido; ejecución121,448676942s, terminalCOMPLETED, dentro de600s y umbrales observados. Piloto+replay conformes, sin nuevas dependencias, cambios al pipeline o tercera ejecución. Ledger único conserva los nueve intentos anteriores y campos globales mediante digests remotos antes/después. Total574,955533384s,0pendientes,reserva final43200s y caja0 intactas. El remanente del alcance no autoriza otro intento. Snapshot local del ledger está anonimizado por el transporte; el cotejo histórico se hizo sobre datos canónicos remotos sin publicar accesos.

Resultado y variación de tiempos en07 §11. Se mantiene la proyección conservadora de ambos intentos para proponer el siguiente alcance; éxito técnico no equivale a admitir toda la cadena. No se entrenó cabeza, reajustó sobre todo train, inspeccionó test ni consumió evaluación. Alcance de reintento agotado tras su cierre; E07/E08 exige propuesta/admisión propia y no se activa automáticamente.


## 13. Admisión E07 global/E08 aprobados

«Apruebo el siguiente alcance»,20nov2026, autoriza implementar/executar extracción1125 y cabezaRGB LOSO con sus puertas. Caja0, presupuestoUSD10 intacto; límite global172800s y reserva final43200s, historial574,955533384s. Nuevo alcance máximo43200s de trabajo gratuito, compartido porGPUlocal yCPU Slurm, sin doble cargo. Cota previa completa39360s: extracción18060 +restauración18060 +piloto360 +tresfolds2880. Cada fase completa tiene TimeLimit18000s+60s, distinta de los pilotos históricos600+60. Proyección conservadora16043,263s≤18000; máximo una extracción y una restauración, sin reintentos automáticos. CPU4CPU/8GiB; piloto300+60 y cadafold900+60, tres como máximo, solo tras gate real. Máximo dosjobs Slurm activos; uno localGPU. No entrenamiento enlogin.

La cota protege presupuesto/calendario antes deE07; no acredita cabeza ni admite sus80épocas. Medir piloto real: ≥10pasos tras5warm-up, carga/escalado/evaluación/escritura, memoria y probe60fit-only. Gate1,5×(80×época estimada+I/O+evaluación+escritura+arranque observado), dentro900s porfold; refit1125 se proyecta aparte y debe caber en reserva final con referencia inferencia375 de5388,420s y empaquetado. RestoreCPU375delpiloto y consistenciaantes de reservarlos. Si falla, cerrar sin tresfits aunque el caché haya terminado. No reducirépocas/batch/frames para caber.

Implementación≤4h antes de reevaluar dependencia esencial; transferencias/cola/finalización con margen operativo1h antes del corte22nov18:00. Antes de lanzar extracción comprobar que dosfasesGPU y cotasCPU/cola caben también en calendario, incluyendo finalización; detener si no. Mismos límites preventivosRAM≥2GiB/VRAM≥3GiB libres al inicio, RAMdisponible≥512MiB/RSSagregado≤2GiB duranteGPU, reservaPyTorch≤3GiB, SIGTERM→10s→SIGKILL propio. Registrar valor real de ejecución y liquidar exactamenteuna vez incluso fallo. Ningún remanenteautoriza otra receta. Refit/test/pagos/envíos excluidos.


Reconciliación con mediciones,20nov: extracción1125 completada en4548,825s de pared; el diagnóstico heredado1,5×máximo porclip extrapolado da45516,573s para1125 y15185,184s para375. El primero supera18000s y se conserva como advertencia, sin truncarlo ni afirmar que el riesgo desapareció. Para repetir exactamente el pase completo medido,1,5×4548,825+300s de holgura CPU arroja7123,238s<18000; los300s son una asignación conservadora, no restauración CPU medida. Depende de videos, receta, hardware y carga comparables; el límite duro permanece y no hay reintento automático. La cota actual del alcance, extracción real más todos los máximos restantes, es25848,825s<43200.

Piloto Slurm47 completado6s, restauración de375 desde caché en proceso nuevo con diferencia0; gate medido13,625s porfold y15,885s para refit. Folds48–50 completados6s cadauno. El gate congelado conserva referencia histórica5388,420s; la nueva comprobación de reserva emplea15185,184s:15,885+15185,184+1800=17001,069s<43200. No se reescriben el gate histórico ni sus entradas. El campo `whole_chain_admitted:false` de métricas de extracción es constante en su escritor y no representa la admisión operativa; esta se acredita con ledger y recibo del piloto. Desviación procedimental: estas proyecciones actualizadas se documentaron después de iniciar la restauración original; no se afirma conciliación previa. No cambiaron fuente, receta, cotas ni autorización. Revisión focal independiente de la desviación: pase condicionado para continuar con cotas vigentes; la referencia antigua no cambia el resultado de la comprobación suplementaria, y la demora documental queda registrada. No acredita cumplimiento previo. Liquidación y revisión operativa finales pendientes. Evidencia privada: `forecast_reconciliation.json` en el directorio del incremento.

Los relojes de Cronos y la máquina local no tienen sincronía acreditada: no inferir duración u orden físico comparando sus horas absolutas. La secuencia lógica, los bindings y los recibos de cada fase conservan el orden operativo; las duraciones provienen del reloj de su propio supervisor o de Slurm. No se estima un desfase estable con estas observaciones.


Resultado terminal del intento de restauración:FAILED sin recibo final por error de limpieza; medición real total desconocida. No se liquidó con una duración inventada ni se relanzó. Ledger recuperado:16intentos,15liquidados,5147,780808451s medidos globales (4572,825275067s del alcance), más18060s comprometidos retenidos para la restauración fallida. Reserva final43200s/caja0/históricos intactos. La suma medido+comprometido es23207,780808451s; no es consumo físico total acreditado. La cota retenida no demuestra duración real máxima tras fallar cleanup. Recibo administrativo separado identifica evidencia/estadoFAILED y `actual_seconds:null`, sin simular `execution.json`. Retenerla preserva disponibilidad igual; liquidarla requiere contrato administrativo explícito, propuesto y aún no aprobado. Ningún remanente autoriza nuevos intentos. El desenlace real de restauración sustituye su estado previo en curso, sin borrar las proyecciones o la desviación documental.

Decisión de proporcionalidad posterior: conservar indefinidamente la reserva18060comprometida, sin nuevo tipo contable. Revisión independiente conforme; contrato administrativo propuesto descartado antes de implementación. La corrección local solo repara persistencia/cleanup y conserva la duración histórica desconocida. Archivar el experimento no libera la reserva ni reinicia saldos.


## 14. Admisión propuesta · camino de entrega E01

**Estado: propuesto el20nov, sin aprobación.** El ledger remoto se verificó el20nov a las20:01 UTC: SHA idéntico a la copia de cierre, 5147,780808451s medidos, 18060s comprometidos, cero jobs y caja USD0. Margen para nuevos alcances: 172800 − 43200 − 5147,780808451 − 18060 = **106392,219191549s**.

El [ítem](../openspec/changes/archive/2026-11-20-e01-delivery-path/proposal.md) pide un alcance de9000s: nueve jobs ×900s (seis LOSO E13 y hasta tres refit), con TimeLimit600s+KillWait y máximo dos activos. El histórico de E01 fue de unos6s por fit, así que el consumo esperado está muy por debajo de la reserva. Implementación: ≤3h antes de reevaluar. La reserva retenida y la final no se tocan, y no hay GPU ni pagos.

**Calendario (Bogotá).** Ejecutar el21nov para tener el bundle verificado con train antes del22nov18:00. El freeze, la inferencia test y la evaluación1 requieren autorización separada. Conviene adelantarlos frente al objetivo del24. Según la página (01 §3), un empate puede resolverse por el envío en menor tiempo o por un criterio secundario, sin fijar cuál; además, la latencia de evaluación es desconocida. La hora de cierre sigue sin confirmar.


**Ejecución del ítem de entrega, 20nov.** Corrió en CPU local, no en Cronos: unos2,5min de fits y5s de predicción. La reproducción bit a bit de E01 en local hace innecesaria la cola Slurm para recetas de este tamaño. El ledger remoto no se modificó y conserva los valores de arriba. Los diagnósticos X1–X3/X7 también corrieron en local: X1 92s, X2 172s y unos segundos el resto. El bundle de E01 con3 semillas queda como respaldo entregable. Calendario: X8/X4/X6 el21nov; freeze del mejor candidato entre el22 y el23 según04 §17; evaluación1 en cuanto se autorice, sin esperar al24.


**Estado tras la ola, 20nov.** La ola completa corrió en CPU/GPU local: unas2h de reloj, incluidas extracciones y refit. Ledger de Cronos sin cambios; caja USD0.

Ruta de entrega lista:

1. Freeze de `bundle_x4x6_v1` (hashes en07 §14).
2. `lsc5 wave-predict-csv --authorized-test-run` sobre los375 NPY test; unos10s en CPU.
3. `validate-submission`.
4. Carga de la evaluación1 por el integrante designado.

Los pasos 2 a 4 requieren autorización humana. El primer envío conviene hacerlo pronto (posible desempate por tiempo y latencia desconocida); la segunda evaluación se reserva para recuperación técnica.
