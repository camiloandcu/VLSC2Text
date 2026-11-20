## Context

La inferencia ya está implementada; el fallo previo está en07 §10. Inspección actual:GPU libre,3935MiB, RAM disponible3,172GiB; no acredita causa raíz ni estabilidad. No hubo operación CUDA adicional durante el diagnóstico previo de este reintento.

## Decisions

Repetir una sola vez el flujo completo aprobado para conservar supervisión y cobertura, sin cambiar encoder/muestreo/precisión/batches. Extender presupuesto con un segundo perfil fijo, no borrar intentos ni reutilizar claims/marcadores. `--retry-of` verifica padre original liquidado y fallido, manifiesto/selección idénticos y vínculo a su recibo. Claim valida nuevamente ese vínculo. Mismos600s+60s y660s reservados. Sin cadena de reintentos.

## Verification

Pruebas focales de política/contabilidad y regresiones; QA independiente antes de ejecución y sobre recibos reales. Comparar hashes del pipeline con snapshot original. Fallo repetido conserva G3 sin verificar; éxito solo admite proponer la siguiente rama, no ejecutarla. Preparación/ajuste mínimo≤1h antes de reevaluar; instalación innecesaria, sin cambio de dependencias.
