# Small image for the live demo (Render free plan): numpy only, no torch.
# Private assets (weights, guide videos) are downloaded at start from a private Hugging Face dataset.
# Build context: repository root.  docker build -f demo/Dockerfile -t sena-a-sena .
FROM python:3.10-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN pip install --no-cache-dir numpy==1.26.4 fastapi==0.115.5 uvicorn==0.32.1 huggingface_hub==0.36.0
COPY src/lsc5 /app/src/lsc5
COPY demo/server.py demo/predictor_np.py demo/coach.py demo/fetch_assets.py /app/demo/
COPY demo/static/index.html demo/static/style.css demo/static/app.js /app/demo/static/
COPY demo/static/fonts /app/demo/static/fonts
RUN mkdir -p /app/demo/static/vendor/holistic \
    && curl -sL https://registry.npmjs.org/@mediapipe/holistic/-/holistic-0.5.1675471629.tgz \
       | tar -xz -C /app/demo/static/vendor/holistic --strip-components=1
ENV PYTHONPATH=/app/src:/app/demo LSC5_ASSETS=/tmp/assets LSC5_LOCAL_VIDEOS=1 PORT=10000
EXPOSE 10000
CMD ["sh", "-c", "python /app/demo/fetch_assets.py && exec uvicorn server:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
