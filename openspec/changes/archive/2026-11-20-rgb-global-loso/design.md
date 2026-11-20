## Context

Fuente/peso y receta en04/05; hardware validado por reintento. Proyección conservadora16043,263s train; cabeza sin costo medido. Ledger único574,955533384s,0pendientes,caja0. El máximo presupuestario se verifica antes deE07; la admisión de tres fits depende además de medir el piloto real.

## Decisions

1. Mantener ViT-S/14 externo/K16/global224/float32/batch4/ImageNet/CLS y tolerancias. Optimizar solo transporte: FFmpeg filtra índices únicos antes de enviar RGB24, sigue decodificando el stream íntegro y ffprobe cuenta N. Pillow sigue haciendo letterbox; duplicar índices en Python. Probar SHA de píxeles contra30casos previos, o conservar implementación previa. No cambiar encoder o dataset para acelerar.
2. Compartir caché externo fijo por fold. Cobertura `full1125`, metadata con todos los IDs/videos/indices/píxeles/versiones; staging+hash+rename. Consumidor de cabeza exige1125 y fuente/identidad; piloto30 no se promociona.
3. Ajustar384 medias/desviaciones poblacionales en750×16frames fit (float64 acumulado, estadofloat32,scale<1e-6→1). Estandarizar cada frame y luego medias global/0:8/8:16, cada384;1152→128ReLU/dropout.3→5. Reusar sampler/LR CPU existentes;80épocas fijas17. Reverse control invierte16frames antes de medias sin refit.
4. CPU en Slurm4CPU/8GiB: piloto M02dosépocas, batch60probe fit-only descartado, ≥10 pasos después de5warmup. Restore375 del piloto desde el caché completo inmutable en otro proceso; no se confunde con restauración desde video. Gate proyecta80épocas y refit1125 antes de reservar tres fits.
5. Tras tres fits, un procesoGPU nuevo reextrae1125 desde videos/peso y obtiene375 embeddings por fold externo; modeloCPU restaurado+scaler producen probabilidades, sin dependencia del caché de entrenamiento. Conservar nuevas features solo como evidencia de verificación, no como ajuste o nuevo candidato. Compare atol1e-6/rtol0. No aceptar resultados del piloto como OOF.
6. Presupuesto de escenario completo previo: dosGPU×18060s +CPUpiloto360 +3×960 =39360s dentro del alcance43200s. Cada GPU TimeLimit18000+60; estimación original10695,509s×1,5=16043,263≤18000. Un extract y un restore, sin reintento automático. CPU300/900s+60, después del gate. La cota no demuestra costo medido de cabeza; si falla su gate, no admitir80épocas. Conservar43200s finales y margen1h antes del corte22nov18:00; verificar calendario de cadena/cola, no solo saldo.

## Risks

El OOM previo no tiene causa confirmada. Mismos umbrales RAM/VRAM, watchdog100ms, exclusión GPU y grupos propios. Supervisor parametrizado por perfiles fijos; no ampliar límites del piloto ni transformar intentos previos. Extracción parcial no equivale a completa; sin reanudar un intento cerrado bajo el mismo claim. Los casos históricos de equivalencia no garantizan distribución de nuevos videos; toda corrupción aborta. Piloto/caché compartido no lleva normalización fit al sujeto retenido.

## Verification

V1–V6 y contratos: pruebas sintéticas/negativas, revisión independiente antes de ejecución, fuente/snapshot fijados durante corrida, SHA de baseline anclado antes de predicciones, restore completo y comparación. No modificar fuente mientras GPU/CPU ejecutan ese productor. Reportar coste original/optimizado sin prometer speedup. Si se agota4h de implementación por dependencia esencial, registrar estado y concretar decisión.


## Corrección acotada y cierre negativo

La alternativa de nuevo contrato contable se retiró por innecesaria antes de implementación. Se conserva18060s comprometidos, actual_secondsnull y fallo original. La reparación de finally y pruebasCPU corresponde al comportamiento ya autorizado; no implica nueva aprobación contable o intentoGPU. Snapshot ejecutado42archivos preservado, fuente posterior diferenciada. Revisión independiente de proporcionalidad conforme. Restauración original fallida yOOFnoejecutado permanecen así; el cierre documental no los convierte en conformes. Corrección/pruebas/QA/lifecycle en curso.
