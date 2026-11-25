"""One concrete correction per attempt, from simple body measurements compared with train references.

All distances are in shoulder widths, so they do not depend on how far the person stands from the camera.
The references (5th to 95th percentile per sign) come from the 1125 train clips: demo/make_coach_ref.py.
"""
import numpy as np

WHERE = {"sign_01": "frente a la boca", "sign_02": "a la altura del pecho", "sign_03": "junto a la frente",
         "sign_04": "a la altura del pecho", "sign_05": "sobre el pecho"}

# What tells the target apart from the sign it was confused with (most common confusions first).
CONTRAST = {
    ("sign_04", "sign_05"): "En ¿Qué necesitas? primero señalas hacia adelante y luego abres las dos manos. Con gusto es una sola mano que sale del pecho.",
    ("sign_05", "sign_04"): "Con gusto es una sola mano: apoya la palma en el pecho y llévala hacia adelante, sin señalar.",
    ("sign_02", "sign_01"): "Aromática es con las dos manos y a la altura del pecho. Café es una sola mano frente a la boca.",
    ("sign_01", "sign_02"): "Café es con una sola mano, en pinza, frente a la boca. Deja la otra mano abajo.",
    ("sign_01", "sign_05"): "Café va frente a la boca, en pinza. Con gusto va sobre el pecho, con la mano abierta.",
    ("sign_05", "sign_01"): "Con gusto va sobre el pecho con la mano abierta, no frente a la boca.",
    ("sign_03", "sign_01"): "Hola empieza junto a la frente, con la mano abierta, y sale hacia afuera.",
    ("sign_04", "sign_03"): "¿Qué necesitas? va a la altura del pecho: señala y luego abre las dos manos.",
}


def measures(x, fps=24.0):
    """Body measurements of one attempt; None when the shoulders are not visible."""
    X = np.asarray(x)
    P = X[:, :132].reshape(len(X), 33, 4)
    ok = (P[:, 11, 3] > 0.5) & (P[:, 12, 3] > 0.5)
    if ok.sum() < 3:
        return None
    X, P = X[ok], P[ok]
    sh_y = (P[:, 11, 1] + P[:, 12, 1]) / 2
    sh_x = (P[:, 11, 0] + P[:, 12, 0]) / 2
    sw = float(np.median(np.abs(P[:, 11, 0] - P[:, 12, 0])))
    hip_y = (P[:, 23, 1] + P[:, 24, 1]) / 2
    line = sh_y + 0.55 * np.maximum(hip_y - sh_y, 0.15)
    up = np.stack([(P[:, w, 1] < line) & (P[:, w, 3] > 0.5) for w in (15, 16)], 1)
    active = up.any(1)
    base = {"sw": sw, "active": int(active.sum()), "dur": float(active.sum() / fps)}
    if active.sum() < 3:
        return {**base, "peak": float(np.max((sh_y - P[:, [15, 16], 1].min(1)) / sw)), "two": 0.0, "face": 9.0, "chest": 9.0}
    lift = (sh_y[:, None] - P[:, [15, 16], 1]) / sw
    # Hand position: centre of the detected hand, or the wrist when the hand was not detected.
    hands = []
    for blk, w in ((slice(1536, 1599), 15), (slice(1599, 1662), 16)):
        H = X[:, blk].reshape(len(X), 21, 3)[:, :, :2]
        seen = H.any((1, 2))
        c = np.where(seen[:, None], H.mean(1), P[:, w, :2])
        hands.append(np.where(up[:, [0 if w == 15 else 1]], c, np.nan))
    hands = np.stack(hands, 1)                                   # (T, 2, 2), NaN when that hand is down
    mouth = (P[:, 9, :2] + P[:, 10, :2]) / 2
    chest = np.stack([sh_x, sh_y + 0.45 * sw], 1)
    d = lambda ref: np.nanmin(np.linalg.norm(hands - ref[:, None, :], axis=2)) / sw
    return {**base, "peak": float(np.max(np.where(up, lift, -9))), "two": float(up[active].all(1).mean()),
            "face": float(d(mouth)), "chest": float(d(chest))}


def advice(m, target, ref, names, confused=None):
    """A single short correction for the target sign."""
    if m is None:
        return {"kind": "frame", "text": "Ponte de frente, que no te veo los hombros."}
    if m["sw"] > 0.27:
        return {"kind": "far", "text": "Aléjate un poco, que se vean tu cintura y tus codos."}
    if m["active"] < 3:
        return {"kind": "up", "text": "No alcancé a ver la seña. Sube las manos y bájalas al terminar."}
    r = ref[target]
    if r["two"] > 0.6 and m["two"] < 0.3:
        return {"kind": "two", "text": "Usa las dos manos."}
    if r["two"] < 0.25 and m["two"] > 0.5:
        return {"kind": "one", "text": "Usa una sola mano y deja la otra abajo."}
    if target == "sign_01" and m["face"] > r["face_hi"]:
        return {"kind": "up", "text": "Lleva la mano en pinza frente a la boca."}
    if target == "sign_05" and m["chest"] > r["chest_hi"]:
        return {"kind": "down", "text": "Apoya la palma en el pecho antes de llevarla hacia adelante."}
    if m["peak"] > r["peak_hi"]:
        return {"kind": "down", "text": f"Baja un poco las manos, van {WHERE[target]}."}
    if m["peak"] < r["peak_lo"]:
        return {"kind": "up", "text": f"Sube un poco las manos, van {WHERE[target]}."}
    if m["dur"] < r["dur_lo"]:
        return {"kind": "slow", "text": "Hazla un poco más despacio, sin afán."}
    if m["dur"] > r["dur_hi"]:
        return {"kind": "fast", "text": "Hazla de corrido, sin pausas en la mitad."}
    if confused and (target, confused) in CONTRAST:
        return {"kind": "look", "text": CONTRAST[(target, confused)]}
    if confused and confused != target:
        return {"kind": "look", "text": f"Se parece a {names[confused]['name']}. Recuerda: {names[target]['key'].lower()}."}
    return {"kind": "look", "text": f"Recuerda: {names[target]['key'].lower()}. Fíjate en la forma de la mano en el video."}
