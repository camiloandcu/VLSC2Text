## Tasks

- [x] 1. Recuperar el estado real y calcular el diagnóstico E12 y la equivalencia parcial del staging RGB (solo lectura, sin entrenamiento).
- [x] 2. Aprobación humana: «Apruebo», 20nov2026. La opción B queda admisible según 04 §17.
- [ ] 3. Revisión independiente del diseño. **No realizada**: solo autorrevisión; queda pendiente.
- [x] 4. Implementar semilla cerrada, refit, bundle, `predict_bundle` y `validate-submission`, con pruebas.
- [x] 5. Seis fits E13, restauraciones y OOF agregado (ejecución local; ver desviaciones).
- [x] 6. Refit E14, bundle, predicción train en proceso nuevo y medición CPU.
- [x] 7. Registros y sync/archive. Freeze/test/envío quedan para un alcance separado.

## Evidence

Recuperación20nov2026, 20:01 UTC según el reloj de Cronos:

- **Ledger remoto `~/resultados/lsc5/budget.json`.** SHA `a6073519240a1d826ec3cf6c9ba049394a857a68b3486cd3d9e9e3222b8e4d18`, idéntico a la copia `artifacts/rgb-loso/remote_final/budget.json`. Contiene 16 intentos: 15 liquidados y la restauración RGB comprometida con 18060s. La caja sigue en USD0, la reserva final en 43200s y hay cero jobs en cola. La partición `estudiantes` sigue listando la RTX A6000.
- **Código local.** Productor actual `d8a9c1f4f3d420abffcb9d025973e32d62d6df0e83a7674e3054dbbbd89fb798`, igual al snapshot posterior y con 42 archivos coincidentes. 32/32 pruebas pasan en101,28s. No hay procesos RGB ni ffmpeg activos.
- **GTX1650 local.** 4096MiB con 0MiB usados; el sistema tiene unos 3GiB de RAM disponibles.
- **Diagnóstico E12** sobre los1125 IDs alineados, sin test (detalle en 07 §12):

  | Pareja 50/50 | Aciertos | Δ M02 / M03 / M04 frente a E01 | Promovible |
  |---|---:|---|---|
  | E01+E08, E08 provisional | 712/1125 | +19 / −12 / +19 | No |
  | E01+E02O, OOF aceptados | 690/1125 | −5 / +29 / −20 | No |

- **Staging de la restauración fallida.** Los 872 embeddings reextraídos son legibles e idénticos bit a bit al caché (diferencia máxima 0). Es una equivalencia parcial diagnóstica: no sustituye V4 ni crea OOF aceptado.


Ejecución 20nov2026 (cifras en 07 §13):

- D1 registrado en 04 §16 y 07 §12.
- D2: semilla17 reproducida bit a bit; semillas29/43 dan674/677; el promedio 17/29/43 da676 (60,09%). Las nueve restauraciones desde originales dan diferencia0.
- D3/D4: bundle con3 semillas, diferencia0 en proceso nuevo, invariante al orden, 0,27s para375 clips.
- D5: siete pruebas de CSV.
- D7: 42/42 pruebas. Productor nuevo `5bd84e38b04ef9ea826ac3d09653d5b432cfca94352e9bb5f97d23570d7323ab`; snapshot de35 archivos en `artifacts/e01-delivery`.

**Desviaciones registradas:**

1. Todo corrió en CPU local en lugar de Cronos. La reproducción exacta de E01 demuestra equivalencia. El trabajo total (unos2,5min de fits) no se cargó al ledger de Cronos, que queda intacto.
2. No hubo revisión independiente; se conserva como pendiente.
3. `predict-bundle` existe como función de biblioteca, no como comando CLI. La inferencia test se cableará con su alcance propio.
4. Al revisar el contrato del CSV se mostraron dos IDs de la plantilla test (`head`). No contiene etiquetas ni payloads, y no se usó para nada.
5. El productor nuevo cambia la huella. Los cachés antiguos validados por productor exacto (p.ej. `load_stats`) ya no cargan con este código; sus snapshots quedan intactos.
