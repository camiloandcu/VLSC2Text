## 1. Preparación

- [x] 1.1 Verificar hardware/decoder/fuente y30 videos train, sin implementar.
- [x] 1.2 Revisión independiente y registrar aprobación real del ítem.

## 2. Implementación condicionada

- [x] 2.1 Entorno separado/lock y backbone fijo (G2).
- [x] 2.2 Decoder/muestreo/letterbox/caché con pruebas (G1/G3).
- [x] 2.3 Contabilidad local y piloto real/replay instrumentado (G3/G4).
- [x] 2.4 Revisiones, decisión, documentación y sync/archive (G5).

## Evidencia

Preparación del20 nov2026: evidencia privada en `artifacts/rgb-feasibility` (`local_readiness.json`, `source_checks.json`, `video_preflight.json`). Resumen público en04 §14 y05 §14; costos/caps en06 §11. Treinta hashes verificados y conteo real; entornoCPU intacto, peso soloHEAD. No resultados de embeddings ni tiemposGPU. La primera consulta ffprobe usó una sección no soportada por4.4; se diagnosticó, corrigió a show_streams y completó30, sin inferir corrupción de videos. El diagnóstico y tiempo de la pasada exitosa están en la evidencia; no hubo entrenamiento.


Revisión independiente focal: pase para presentar a decisión humana, sin hallazgos materiales. Comprobó coherencia de30 registros/480 índices/bytes, cinco archivos fuente contra sus hashes, contratos de representación/caché, recursos/contabilidad/plazo y límites de autoridad. Hallazgo menor de RAM corregido en06 §11: umbrales durante ejecución, supervisor y terminación del grupo propio. No ejecutó CUDA ni verificó binario/servidor en vivo; no acredita viabilidad o resultado del piloto. La aprobación humana posterior quedó registrada en00;1.2 está cerrado.

Verificación de preparación:32 Markdown públicos y125 enlaces locales conformes;64 archivos públicos sin valores de acceso o referencias a textos privados; JSON de auditoría conservado. Tres especificaciones más este cambio conformes en OpenSpec estricto. Productor/snapshot de27 archivos del último incremento medido intactos. No se repiten suites de software porque no cambió código.

Aprobación humana concreta registrada en00,20 nov2026; G1–G5 autorizados. Instalación y ejecución en curso.

Implementación,20 nov: entorno `.venv-rgb` separado y `requirements/rgb.lock`; CUDA mínimo conforme, sin modificar el entorno CPU. Fuente DINOv2 y peso oficiales descargados y verificados, todavía sin ejecutar el backbone. Pruebas completas:25/25 en179,76s; focales RGB:9/9 en19,46s. La revisión estática independiente señaló cinco controles materiales (reutilización de reserva, consulta GPU bloqueante, señales/descendientes, comparación directa entre batches y contrato de caché); se corrigieron y se añadieron escenarios sintéticos de regresión. Pase dinámico independiente y operación real pendientes; los mocks no acreditan factibilidad.

Pase independiente previo a ejecución:9 pruebas focales en18,64s, con `-p no:cacheprovider`, más inspección de las cinco correcciones; sin bloqueos materiales. SIGKILL forzado y vencimiento real600s no se ejercitaron; los controles sintéticos no acreditan resultados DINOv2. Productor congelado `3c6edb096c4605d8dc0f3339f9a4ca3f2c582c8ab157db9c974bcc940f42f767`, snapshot privado36 archivos. Intento único reservado y ligado al directorio/máquina; piloto real iniciado.


## Resultado del único intento y revisión operativa

Intento `r2-e07-global-pilot-20261120-01`, terminalFAILED: extracción30 completada, replayexit1 por CUDAOOM en carga del modelo al dispositivo. No hubo arrays/recibo de replay exitoso, repetición o cambio del protocolo. Las tareas realizadas no implican que G3 haya pasado. Evidencia privada: `execution/execution.json`, `execution/pilot/{run,metrics}.json`, `execution/pilot/cache`, stderr de las dos etapas, diagnóstico posterior, reserva y liquidación. Resultados públicos autoritativos en07 §10; costo y límites en06 §11.

| AC | Estado y evidencia |
|---|---|
| G1 | Verificado:30 IDs/índices/hashes conformes con selección/preflight; decoder/transformación probados sintéticamente. El revisor no volvió a leer videos originales. |
| G2 | Verificado: fuente/peso/entorno y snapshot36archivos conformes; CLS fijo float32, congelado/eval; entornoCPU/lock y archivos históricos intactos. |
| G3 | **Fallido operativo:** caché íntegro y alcance1125 rechazado en prueba; equivalencia de replay entre procesos/batches no acreditada por CUDAOOM antes del forward. |
| G4 | Contabilidad/límites observados verificados:265,506856442s adicionales,453,506856442s totales,0pendientes,caja0,reserva final intacta. Forward global del intento no medido: campo nulo; métricas de extracción no lo sustituyen. |
| G5 | Verificado como cierre procedimental negativo: decisión detener, revisión y documentos reconciliados; dos requisitos sincronizados y cambio archivado. G3 sigue fallido; no hay nueva rama ni aceptación de reproducibilidad. |

Revisión operativa independiente: integridad de caché/arrays, fuente/peso/snapshot, reserva/recibo, memoria y proyecciones conformes con evidencia; recomienda cierre negativo y detención. Alcance/limitaciones: no ejecutó GPU, SSH o videos originales; no ejercitó SIGKILL forzado ni600s reales.206 muestrasGPU y un timeout de consulta registrado; causa raíz del OOM desconocida. Pruebas sintéticas y extracción real no sustituyen replay. `implementation_checks.json` se reconcilia por fases: ejecución real sí, extracción completa sí, replay no, terminalFAILED.

La copia local del ledger está anonimizada por el wrapper SSH. El recibo `canonical_history_verification.json` cotejó remotamente, en lectura, digests de los ocho registros históricos y campos globales originales: ambos conformes, sin publicar accesos. No se presenta igualdad bytea-byte entre copias anonimizadas y originales. Productor/snapshot permanecen los del único intento; no hay cambio de código posterior.

Revisión final independiente: pase para cierre documental negativo después de reconciliar fases, anonimización y2,414GiB de RAM en admisión. Conservación remota de históricos comprobada por digest independiente. Sin bloqueos materiales de software/documentación; G3 permanece fallido y la causa no acreditada. El siguiente paso de cierre sincroniza/archiva esta decisión, sin conceder aceptación operativa o humana de RGB.

Cierre efectivo,20 nov2026: dos requisitos sincronizados en `openspec/specs/rgb-global-pilot/spec.md`; ítem archivado como `2026-11-20-rgb-global-pilot`. Endpoint local del experimento completado, sin Git/PR/publicación. G1/G2 y límites/contabilidad observados verificados, G3 fallido, medición GPU global incompleta y G5 procedimental cerrado. No concede aceptación humana/competitiva. Las comprobaciones públicas finales y la siguiente acción vigente están en00; no se repiten suites sin cambios de fuente.
