# Seña a seña: demo en vivo LSC5

Página para aprender y practicar las cinco señas con la cámara. El navegador corre MediaPipe Holistic
(`@mediapipe/holistic@0.5.1675471629`) y envía solo los landmarks (1662 valores por fotograma). El servidor
aplica el pipeline y el bundle congelado `bundle_iter4_v1`. El video de la persona nunca sale del dispositivo.
Reconoce solo cinco señas aisladas: no es un traductor.

## Piezas

- `server.py`: FastAPI. Contraseña opcional (`LSC5_PASSWORD`), `/api/predict`, videos guía (`LSC5_LOCAL_VIDEOS=1`).
- `predictor.py` (PyTorch) y `predictor_np.py` (solo numpy, para servidores pequeños). `export_numpy.py` exporta los
  pesos y verifica la paridad: diferencia máxima de probabilidad 1,8e-7 y mismo top-1 en 90 clips de cámara.
- `coach.py`: una corrección concreta por intento, con rangos de referencia sacados de train (`make_coach_ref.py`).
- `make_guides.py`: animaciones de esqueleto desde train, usadas cuando no hay videos guía.

## Archivos que no están en Git

Pesos, videos guía, guías y referencias derivadas del dataset viven en un repositorio privado de Hugging Face.
`fetch_assets.py` los descarga al arrancar con `HF_TOKEN` y `LSC5_ASSETS_REPO`, en la carpeta `LSC5_ASSETS`
(`bundle/`, `private/`, `videos/`).

## Local

```bash
.venv/bin/python demo/make_guides.py && .venv/bin/python demo/make_coach_ref.py
LSC5_LOCAL_VIDEOS=1 PYTHONPATH=src:demo .venv/bin/uvicorn server:app --port 8000
```

La cámara exige HTTPS fuera de `localhost`.

## Despliegue

`demo/Dockerfile` (contexto: raíz del repositorio) construye una imagen sin PyTorch, que usa unos 70 MB de RAM.
El despliegue actual corre en el plan gratuito de Render, con la contraseña y los tokens como variables secretas.
El plan gratuito se duerme tras 15 minutos sin uso y tarda cerca de un minuto en despertar.
