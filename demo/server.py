"""LSC5 live demo: the browser runs MediaPipe Holistic and sends landmarks only; this server runs the frozen model.

Run from the repository root:
    PYTHONPATH=src:demo .venv/bin/uvicorn server:app --port 8000

Environment:
    LSC5_ASSETS          folder with bundle/, private/ (guides, videos.json, coach_ref) and videos/ (deploy layout)
    LSC5_BUNDLE          frozen bundle directory (default artifacts/iter3/bundle_iter4_v1, or ASSETS/bundle)
    LSC5_LOCAL_VIDEOS=1  serve the guide videos (only behind a password or on a local machine)
    LSC5_PASSWORD        when set, every page and API call requires this password (cookie after login)
    LSC5_THRESHOLD       minimum confidence before answering (default 0.7)
"""
import hashlib
import hmac
from urllib.parse import parse_qs
import json
import os
import time
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from coach import advice, measures
import importlib.util
if importlib.util.find_spec("torch") is None:      # small servers: same maths in numpy (demo/export_numpy.py checks parity)
    from predictor_np import Predictor
else:
    from predictor import Predictor

ROOT = Path(__file__).resolve().parents[1]
STATIC = Path(__file__).resolve().parent / "static"
ASSETS = Path(os.environ["LSC5_ASSETS"]) if os.environ.get("LSC5_ASSETS") else None
BUNDLE = Path(os.environ.get("LSC5_BUNDLE", ASSETS / "bundle" if ASSETS else ROOT / "artifacts" / "iter3" / "bundle_iter4_v1"))
PRIVATE = ASSETS / "private" if ASSETS else STATIC / "private"
VIDEOS = ASSETS / "videos" if ASSETS else ROOT / "data" / "train" / "videos"
PASSWORD = os.environ.get("LSC5_PASSWORD", "")
TOKEN = hashlib.sha256(("sena-a-sena|" + PASSWORD).encode()).hexdigest()
LOCAL_VIDEOS = os.environ.get("LSC5_LOCAL_VIDEOS") == "1"
THRESHOLD = float(os.environ.get("LSC5_THRESHOLD", "0.7"))
MAX_FRAMES = 240

SIGNS = {
    "sign_01": {"name": "Café", "key": "Una mano, en pinza, frente a la boca",
                "hints": ["Junta el pulgar y el índice", "La mano va frente a la boca", "Es un movimiento corto"]},
    "sign_02": {"name": "Aromática", "key": "Dos manos, a la altura del pecho",
                "hints": ["La mano de arriba en pinza, encima de la otra", "Como si metieras una bolsita en una taza", "No la subas a la cara"]},
    "sign_03": {"name": "Hola", "key": "Mano abierta, desde la frente hacia afuera",
                "hints": ["Dedos juntos", "Empieza junto a la frente", "Sácala hacia afuera, como un saludo"]},
    "sign_04": {"name": "¿Qué necesitas?", "key": "Señala y luego abre las dos manos",
                "hints": ["Primero señala hacia adelante con el índice", "Después abre las manos con las palmas hacia arriba", "Pon cara de pregunta"]},
    "sign_05": {"name": "Con gusto", "key": "La palma en el pecho y luego hacia adelante",
                "hints": ["Mano abierta", "Apóyala en el pecho", "Llévala hacia adelante"]},
}

predictor = Predictor(BUNDLE)
COACH_REF = json.loads((PRIVATE / "coach_ref.json").read_text())
app = FastAPI(title="LSC5 demo", docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=STATIC), name="static")

LOGIN = """<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Seña a seña</title><link rel="stylesheet" href="/static/style.css"></head><body>
<section class="screen intro"><header class="brand">Seña a seña</header><div class="intro-body">
<h1>Entrar</h1><p class="lead">Esta demo es solo para quienes participan en el LatAm IA Challenge. Escribe la contraseña que te compartieron.</p>
<form method="post" action="/login" class="login">
<label for="pw">Contraseña</label><input id="pw" name="pw" type="password" autocomplete="current-password" required autofocus>
{error}<button class="btn go" type="submit">Entrar</button></form></div></section></body></html>"""


@app.middleware("http")
async def gate(request: Request, call_next):
    open_paths = ("/login", "/favicon.ico", "/static/style.css", "/static/fonts/")
    if not PASSWORD or request.url.path.startswith(open_paths):
        return await call_next(request)
    if hmac.compare_digest(request.cookies.get("sas", ""), TOKEN):
        return await call_next(request)
    if request.url.path.startswith("/api/") or request.method != "GET":
        return JSONResponse({"detail": "login required"}, status_code=401)
    return RedirectResponse("/login", status_code=303)


@app.get("/login", include_in_schema=False)
def login_page():
    return HTMLResponse(LOGIN.format(error=""), headers={"Cache-Control": "no-store"})


@app.post("/login", include_in_schema=False)
async def login(request: Request):
    pw = parse_qs((await request.body()).decode()).get("pw", [""])[0]
    if not PASSWORD or not hmac.compare_digest(pw, PASSWORD):
        return HTMLResponse(LOGIN.format(error='<p class="login-error">Esa contraseña no es. Inténtalo otra vez.</p>'), status_code=401)
    res = RedirectResponse("/", status_code=303)
    res.set_cookie("sas", TOKEN, max_age=7 * 24 * 3600, httponly=True, secure=True, samesite="lax")
    return res


@app.get("/private/{name}", include_in_schema=False)
def private_file(name: str):
    if name not in ("guides.json",):
        raise HTTPException(404)
    return FileResponse(PRIVATE / name, media_type="application/json")


class Clip(BaseModel):
    frames: list[list[float]] = Field(..., min_length=8, max_length=MAX_FRAMES)
    t: list[float]
    target: str | None = None


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html", headers={"Cache-Control": "no-store"})


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/api/config")
def config():
    return {"signs": SIGNS, "threshold": THRESHOLD, "local_videos": LOCAL_VIDEOS}


@app.post("/api/predict")
def predict(clip: Clip):
    if len(clip.t) != len(clip.frames) or any(len(f) != 1662 for f in clip.frames):
        raise HTTPException(422, "Expected (T,1662) landmarks with T timestamps")
    t0 = time.perf_counter()
    try:
        p = predictor.predict(np.array(clip.frames), np.array(clip.t))
    except ValueError as e:
        raise HTTPException(422, str(e))
    order = np.argsort(-p)
    top = predictor.classes[int(order[0])]
    abstain = bool(p[order[0]] < THRESHOLD)
    tip = None
    if clip.target in SIGNS and (abstain or top != clip.target):
        x24 = predictor.resample(np.array(clip.frames), np.array(clip.t))
        confused = top if top != clip.target else predictor.classes[int(order[1])]
        tip = advice(measures(x24), clip.target, COACH_REF, SIGNS, confused)
    return {
        "top": top,
        "confidence": float(p[order[0]]),
        "abstain": abstain,
        "tip": tip,
        "ranking": [{"sign": predictor.classes[int(i)], "p": float(p[i])} for i in order],
        "ms": round((time.perf_counter() - t0) * 1000, 1),
        "frames": len(clip.frames),
    }


@app.get("/video/{sign}/{k}")
def video(sign: str, k: int):
    if not LOCAL_VIDEOS:
        raise HTTPException(404)
    videos = json.loads((PRIVATE / "videos.json").read_text())
    if sign not in videos or not 0 <= k < len(videos[sign]):
        raise HTTPException(404)
    return FileResponse(VIDEOS / videos[sign][k], media_type="video/mp4")


@app.exception_handler(FileNotFoundError)
def missing(_, exc):
    return JSONResponse({"detail": "missing local asset"}, status_code=404)
