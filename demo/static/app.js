/* Seña a seña. MediaPipe Holistic runs in the browser; only landmarks reach /api/predict. */
(() => {
  'use strict';
  const W = 1280, H = 720;                 // model frames: 16:9 like the dataset videos
  const MAX_MS = 7000, MIN_FRAMES = 8;
  const START_R = 0.55, END_R = 0.65;      // wrist height: 0 at the shoulders, 1 at the hips
  const ORDER = ['sign_01', 'sign_02', 'sign_03', 'sign_04', 'sign_05'];
  const POSE_CONN = [[11,12],[11,13],[13,15],[12,14],[14,16],[11,23],[12,24],[23,24]];
  const HAND_CONN = [[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[5,9],[9,10],[10,11],[11,12],[9,13],[13,14],[14,15],[15,16],[13,17],[17,18],[18,19],[19,20],[0,17]];
  const OVAL = [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109];
  const LIPS = [61,146,91,181,84,17,314,405,321,375,291,409,270,269,267,0,37,39,40,185];
  const TIP_ICON = { far: 'i-far', frame: 'i-center', up: 'i-up', down: 'i-down', two: 'i-hands', one: 'i-hand', look: 'i-eye', slow: 'i-speed', fast: 'i-speed' };
  const STORE = 'senaasena.v1';

  const $ = (id) => document.getElementById(id);
  const desk = window.matchMedia('(min-width: 980px)');
  const video = $('video'), overlay = $('overlay');
  const off = document.createElement('canvas'); off.width = W; off.height = H;
  const offCtx = off.getContext('2d', { willReadFrequently: false });

  let cfg = null, guides = null, holistic = null, cameraReady = false;
  let mode = 'lesson', idx = 0, target = ORDER[0];
  let done = new Set(), review = null;
  let buffer = [], recording = null, busy = false;
  let armed = false, lockUntil = 0, manualUntil = 0, advanceTimer = null;
  let letterbox = { s: 1, ox: 0, oy: 0, vw: W, vh: H };
  let skeletonOn = true, lastState = 'idle', waitingNext = false;

  // ---------- storage (per-viewer convenience only) ----------
  function load() {
    try { const s = JSON.parse(localStorage.getItem(STORE) || '{}'); done = new Set((s.done || []).filter((k) => ORDER.includes(k))); }
    catch (_) { done = new Set(); }
  }
  function save() { try { localStorage.setItem(STORE, JSON.stringify({ done: [...done] })); } catch (_) { /* ignore */ } }

  // ---------- screens ----------
  function show(id) {
    ['intro', 'practice', 'stageScreen', 'result'].forEach((s) => { $(s).hidden = s !== id; });
    window.scrollTo(0, 0);
  }
  const name = (k) => cfg.signs[k].name;

  // ---------- line ----------
  function renderLine() {
    const items = ORDER.map((k, i) => {
      const cls = [done.has(k) ? 'done' : '', mode === 'lesson' && i === idx ? 'now' : ''].join(' ');
      return `<li class="${cls}"><button class="station" type="button" data-i="${i}" aria-label="${name(k)}${done.has(k) ? ', lograda' : ''}">
        <span class="dot">${done.has(k) ? '<svg class="i"><use href="#i-check"/></svg>' : ''}</span></button><span class="label">${name(k)}</span></li>`;
    });
    items.push(`<li class="end ${mode === 'review' ? 'now' : ''} ${done.size === 5 ? 'done-line' : ''}"><button class="station" type="button" data-review="1" aria-label="Repaso"><span class="dot"></span></button><span class="label">${mode === 'review' ? `Repaso ${review.i + 1} de 5` : 'Repaso'}</span></li>`);
    $('line').innerHTML = items.join('');
    $('line').querySelectorAll('li').forEach((li, i) => {
      if (i === 5 && done.size === 5) li.classList.add('done');
    });
    $('line').querySelectorAll('[data-i]').forEach((b) => b.onclick = () => startLesson(+b.dataset.i));
    $('line').querySelector('[data-review]').onclick = () => startReview();
    if (mode === 'lesson') {
      $('count').textContent = `Seña ${idx + 1} de 5`;
      $('whereLeft').textContent = `Seña ${idx + 1} de 5`;
      $('whereRight').textContent = done.size === 5 ? 'Ya puedes ir al repaso' : 'Repaso al final';
    } else {
      $('count').textContent = `Repaso ${review.i + 1} de 5`;
      $('whereLeft').textContent = 'Las cinco aprendidas';
      $('whereRight').textContent = `Repaso ${review.i + 1} de 5`;
    }
  }

  // ---------- lesson / review ----------
  function setSign(k) {
    target = k;
    const s = cfg.signs[k];
    $('signName').textContent = mode === 'review' ? `Haz: ${s.name}` : s.name;
    $('signKey').textContent = mode === 'review' ? 'Esta vez sin guía' : s.key;
    const li = s.hints.map((h) => `<li>${h}</li>`).join('');
    document.querySelector('#hintSheet .hints').innerHTML = li;
    $('sideHints').innerHTML = li;
    guideStart = performance.now();
    document.querySelectorAll('.inset-guide, .side-guide').forEach((g) => g.classList.remove('peek'));
    setGuideVideo();
  }

  const SPEEDS = [0.8, 0.55, 1];
  let speedI = 0;
  const speedHtml = () => `<svg class="i"><use href="#i-speed"/></svg>${Math.round(SPEEDS[speedI] * 100)}%`;
  function cycleSpeed() {
    speedI = (speedI + 1) % SPEEDS.length;
    for (const fig of document.querySelectorAll('.inset-guide, .side-guide')) {
      const v = fig.querySelector('video'); if (v) v.playbackRate = SPEEDS[speedI];
      const b = fig.querySelector('.speed'); if (b) { b.innerHTML = speedHtml(); b.classList.remove('pop'); void b.offsetWidth; b.classList.add('pop'); }
    }
  }
  // Real guide video (train clip of the sign) when the server allows it; skeleton animation otherwise.
  function setGuideVideo() {
    if (!cfg.local_videos) return;
    for (const fig of document.querySelectorAll('.inset-guide, .side-guide')) {
      let v = fig.querySelector('video');
      if (!v) {
        v = document.createElement('video');
        v.muted = true; v.loop = true; v.playsInline = true; v.setAttribute('playsinline', ''); v.preload = 'auto';
        v.addEventListener('loadedmetadata', () => { v.playbackRate = SPEEDS[speedI]; });
        fig.addEventListener('click', cycleSpeed); fig.title = 'Toca para cambiar la velocidad';
        const b = document.createElement('span'); b.className = 'speed'; b.innerHTML = speedHtml();
        b.setAttribute('aria-label', 'Velocidad del video');
        fig.appendChild(v); fig.appendChild(b); fig.classList.add('has-video');
      }
      const src = `/video/${target}/0`;
      if (!v.src.endsWith(src)) { v.src = src; }
      v.play().catch(() => {});
    }
  }

  function startLesson(i) {
    clearTimeout(advanceTimer);
    mode = 'lesson'; idx = i; review = null;
    document.body.dataset.mode = 'lesson';
    setSign(ORDER[i]); renderLine(); idle(); feet('lesson');
    show('practice'); ensureCamera();
  }

  // Stage change: before the first review question, a short screen explains what changes.
  function startReview(skipIntro) {
    clearTimeout(advanceTimer);
    if (!skipIntro) {
      const all = done.size === 5;
      $('stageTitle').textContent = all ? '¡Aprendiste las cinco señas!' : 'Vas a pasar al repaso';
      $('stageLead').textContent = all ? 'Ahora viene el repaso, para ver si te quedaron.' : `Llevas ${done.size} de 5 señas aprendidas. Igual puedes intentar el repaso.`;
      show('stageScreen');
      return;
    }
    const q = ORDER.slice().sort(() => Math.random() - 0.5);
    mode = 'review'; review = { q, i: 0, tries: 0, results: {} };
    document.body.dataset.mode = 'review';
    setSign(q[0]); renderLine(); idle(); feet('review');
    show('practice'); ensureCamera();
  }

  function nextLesson() {
    clearTimeout(advanceTimer);
    const next = ORDER.findIndex((k, i) => i > idx && !done.has(k));
    const first = ORDER.findIndex((k) => !done.has(k));
    if (next >= 0) startLesson(next);
    else if (first >= 0) startLesson(first);
    else startReview();
  }

  function nextReview() {
    clearTimeout(advanceTimer);
    review.i++; review.tries = 0;
    if (review.i >= 5) return showResult();
    setSign(review.q[review.i]); renderLine(); idle(); feet('review');
  }

  function showResult() {
    const r = review.results;
    const ok = review.q.filter((k) => r[k] && r[k].ok);
    const miss = review.q.filter((k) => !(r[k] && r[k].ok));
    $('scoreNum').textContent = ok.length;
    const q = (k) => `«${name(k)}»`;
    $('scoreTitle').textContent = miss.length === 0 ? '¡Te salieron todas!'
      : miss.length === 1 ? `Vas muy bien. Te falta ${q(miss[0])}`
      : `Vas bien. Practica ${miss.map(q).join(' y ')}`;
    $('scoreList').innerHTML = review.q.map((k) => {
      const x = r[k] || {};
      const note = x.ok ? (x.tries === 1 ? 'a la primera' : 'a la segunda') : 'practícala';
      return `<li class="${x.ok ? '' : 'miss'}"><span class="s"><svg class="i"><use href="#i-${x.ok ? 'check' : 'redo'}"/></svg></span>${name(k)}<em>${note}</em></li>`;
    }).join('');
    $('practiceMiss').textContent = miss.length ? `Practicar ${q(miss[0])}` : 'Practicar otra vez';
    $('practiceMiss').onclick = () => startLesson(miss.length ? ORDER.indexOf(miss[0]) : 0);
    show('result');
  }

  // ---------- footer ----------
  function feet(kind) {
    const sec = $('secondary'), pri = $('primary');
    pri.hidden = true; sec.hidden = false; $('timer').hidden = false;
    document.querySelector('.foot').dataset.kind = kind;
    if (kind === 'lesson') {
      if (desk.matches) { sec.textContent = 'Saltar esta seña'; sec.onclick = () => nextLessonSkip(); }
      else { sec.innerHTML = '<svg class="i"><use href="#i-list"/></svg>Ver pistas'; sec.onclick = () => { $('hintSheet').hidden = false; }; }
    } else if (kind === 'lesson-ok') {
      sec.innerHTML = '<svg class="i"><use href="#i-redo"/></svg>Otra vez';
      sec.onclick = () => { clearTimeout(advanceTimer); idle(); feet('lesson'); };
      pri.hidden = false;
      pri.innerHTML = (done.size === 5 ? 'Ir al repaso' : 'Siguiente') + ' <svg class="i"><use href="#i-arrow"/></svg>';
      pri.onclick = () => nextLesson();
    } else if (kind === 'review-next') {
      sec.hidden = true; $('timer').hidden = true;
      pri.hidden = false; pri.className = 'btn go';
      pri.innerHTML = (review.i >= 4 ? 'Ver resultado' : 'Siguiente') + ' <svg class="i"><use href="#i-arrow"/></svg>';
      pri.onclick = () => nextReview();
      return;
    } else if (kind === 'review') {
      sec.innerHTML = '<svg class="i"><use href="#i-skip"/></svg>Saltar';
      sec.onclick = () => { review.results[target] = { ok: false, tries: review.tries }; nextReview(); };
      pri.hidden = false; pri.className = 'btn ghost compact';
      pri.innerHTML = '<svg class="i"><use href="#i-eye"/></svg>Ver guía';
      pri.onclick = () => { document.querySelectorAll('.inset-guide, .side-guide').forEach((g) => g.classList.toggle('peek')); guideStart = performance.now(); };
      return;
    }
    pri.className = 'btn go';
  }
  function nextLessonSkip() {
    const n = (idx + 1) % 5; startLesson(n);
  }
  desk.addEventListener('change', () => { if (!$('practice').hidden && !busy) feet(mode === 'review' ? 'review' : lastState === 'ok' ? 'lesson-ok' : 'lesson'); });

  // ---------- status ----------
  function setState(state) {
    lastState = state;
    $('stage').dataset.state = state;
    document.body.dataset.state = state;
  }
  function message(kind, icon, title, text, small) {
    const m = $('msg');
    m.className = 'msg ' + kind;
    $('msgIcon').setAttribute('href', '#' + icon);
    $('msgTitle').textContent = title;
    $('msgText').textContent = text || '';
    $('msgText').hidden = !text;
    $('msgSmall').textContent = small || '';
    $('msgSmall').hidden = !small;
  }
  function idle() {
    waitingNext = false;
    setState('idle'); armed = false; restSince = 0; frameNote = ''; frameWarn = false;
    message('idle', 'i-hand', 'Tu turno', 'Hazla una sola vez y baja las manos.');
  }
  function hideMessage(h) { $('msg').classList.toggle('hide', h); }

  // ---------- landmarks ----------
  const zeros = (n) => new Array(n).fill(0);
  const r5 = (v) => Math.round(v * 1e5) / 1e5;
  function serialize(r) {
    const pose = r.poseLandmarks ? r.poseLandmarks.flatMap((l) => [l.x, l.y, l.z, l.visibility ?? 0]) : zeros(132);
    const face = r.faceLandmarks ? r.faceLandmarks.slice(0, 468).flatMap((l) => [l.x, l.y, l.z]) : zeros(1404);
    const lh = r.leftHandLandmarks ? r.leftHandLandmarks.flatMap((l) => [l.x, l.y, l.z]) : zeros(63);
    const rh = r.rightHandLandmarks ? r.rightHandLandmarks.flatMap((l) => [l.x, l.y, l.z]) : zeros(63);
    return pose.concat(face, lh, rh).map(r5);
  }
  const vis = (p, i) => (p[i].visibility ?? 1) > 0.5;
  function wristHeight(pose) {
    if (!pose || !vis(pose, 11) || !vis(pose, 12)) return null;
    const sh = (pose[11].y + pose[12].y) / 2, hip = (pose[23].y + pose[24].y) / 2;
    const L = Math.max(hip - sh, 0.15);
    const ws = [15, 16].filter((i) => vis(pose, i)).map((i) => (pose[i].y - sh) / L);
    return ws.length ? Math.min(...ws) : 1;
  }

  // Framing, measured in the camera frame itself (portrait or landscape).
  let frameNote = '', frameWarn = false;
  function framing(pose) {
    const chip = $('chip');
    if (recording) { chip.hidden = false; chip.className = 'chip rec'; chip.innerHTML = '<span class="pulse"></span>Grabando'; return; }
    const set = (txt, warn, icon, sub) => {
      if (frameNote === txt + warn) return; frameNote = txt + warn;
      if (!warn) {
        chip.hidden = false; chip.className = 'chip';
        chip.innerHTML = `<svg class="i"><use href="#${icon}"/></svg>${txt}`;
        if (frameWarn) { frameWarn = false; if (lastState === 'frame') idle(); }
        return;
      }
      chip.hidden = true;
      if (busy || !['idle', 'frame'].includes(lastState)) return;
      frameWarn = true; setState('frame');
      message('try', icon, txt, sub);
    };
    if (!pose || !vis(pose, 11) || !vis(pose, 12)) return set('No te veo bien', true, 'i-center', 'Ponte de frente a la cámara.');
    const { s, ox, oy, vw, vh } = letterbox;
    const px = (p) => [(p.x * W - ox) / s, (p.y * H - oy) / s];
    const [x11] = px(pose[11]), [x12] = px(pose[12]);
    const swH = Math.abs(x11 - x12) / vh;
    const cx = ((x11 + x12) / 2) / vw;
    if (swH > 0.5 || !vis(pose, 13) || !vis(pose, 14)) return set('Aléjate un poco', true, 'i-far', 'Que se vean tu cintura y tus codos.');
    if (swH < 0.14) return set('Acércate un poco', true, 'i-near', 'Estás muy lejos de la cámara.');
    if (cx < 0.3 || cx > 0.7) return set('Ubícate en el centro', true, 'i-center', 'Muévete hasta quedar en la mitad de la imagen.');
    return set('Buen encuadre', false, 'i-check');
  }

  // ---------- drawing ----------
  function drawSkeleton(ctx, pts, map, scale) {
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    const seg = (arr, conn, color, w) => {
      ctx.strokeStyle = color; ctx.lineWidth = w * scale; ctx.beginPath();
      for (const [a, b] of conn) { if (!arr[a] || !arr[b]) continue; const [x1, y1] = map(arr[a]); const [x2, y2] = map(arr[b]); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); }
      ctx.stroke();
    };
    const loop = (arr, color, w) => {
      ctx.strokeStyle = color; ctx.lineWidth = w * scale; ctx.beginPath();
      arr.forEach((p, i) => { const [x, y] = map(p); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }); ctx.closePath(); ctx.stroke();
    };
    const dots = (arr, color, r) => { ctx.fillStyle = color; for (const p of arr) { const [x, y] = map(p); ctx.beginPath(); ctx.arc(x, y, r * scale, 0, 7); ctx.fill(); } };
    if (pts.oval) loop(pts.oval, 'rgba(255,255,255,.45)', 2);
    if (pts.lips) loop(pts.lips, 'rgba(255,255,255,.45)', 2);
    if (pts.pose) seg(pts.pose, POSE_CONN, 'rgba(238,244,255,.92)', 5);
    if (pts.lh && pts.lhOn) { seg(pts.lh, HAND_CONN, '#8fd0c4', 4); dots(pts.lh, '#8fd0c4', 3.8); }
    if (pts.rh && pts.rhOn) { seg(pts.rh, HAND_CONN, '#ffffff', 4); dots(pts.rh, '#ffffff', 3.8); }
  }
  function livePts(r) {
    const xy = (a) => (a ? a.map((l) => [l.x, l.y]) : null);
    const f = r.faceLandmarks;
    return { pose: xy(r.poseLandmarks), lh: xy(r.leftHandLandmarks), rh: xy(r.rightHandLandmarks),
      lhOn: !!r.leftHandLandmarks, rhOn: !!r.rightHandLandmarks,
      oval: f ? OVAL.map((i) => [f[i].x, f[i].y]) : null, lips: f ? LIPS.map((i) => [f[i].x, f[i].y]) : null };
  }
  function drawLive(r) {
    const ctx = overlay.getContext('2d');
    ctx.clearRect(0, 0, overlay.width, overlay.height);
    if (!skeletonOn) return;
    const { s, ox, oy } = letterbox;
    drawSkeleton(ctx, livePts(r), (p) => [(p[0] * W - ox) / s, (p[1] * H - oy) / s], Math.max(overlay.width, overlay.height) / 1280);
  }

  // Guide: time-based playback at the dataset's 24 fps, independent of the camera loop.
  let guideStart = performance.now();
  function guideBox(g, cw, ch) {
    const xs = [], ys = [];
    const add = (p) => { xs.push(p[0] * 16); ys.push(p[1] * 9); };
    g.pose.forEach((f, i) => {
      [0, 11, 12, 13, 14, 15, 16].forEach((j) => add(f[j]));
      if (g.lh_on[i]) g.lh[i].forEach(add);
      if (g.rh_on[i]) g.rh[i].forEach(add);
      if (g.face_on[i]) g.oval[i].forEach(add);
    });
    const q = (a, p) => a.slice().sort((u, v) => u - v)[Math.floor(p * (a.length - 1))];
    const x0 = q(xs, 0.01), x1 = q(xs, 0.99), y0 = q(ys, 0.01), y1 = q(ys, 0.99), pad = 0.08;
    const k = Math.min(cw * (1 - 2 * pad) / (x1 - x0), ch * (1 - 2 * pad) / (y1 - y0));
    return { x0, y0, k, ox: (cw - (x1 - x0) * k) / 2, oy: (ch - (y1 - y0) * k) / 2 };
  }
  function drawGuide(now) {
    if (!guides || $('practice').hidden || cfg.local_videos) return;
    const g = guides[target] && guides[target][0];
    if (!g) return;
    // Played at 60% of the recorded speed (24 fps) so beginners can follow it, with a pause before it repeats.
    const n = g.pose.length, hold = 18, fps = 24 * 0.6;
    const i = Math.min(Math.floor(((now - guideStart) / 1000) * fps) % (n + hold), n - 1);
    for (const c of document.querySelectorAll('.inset-guide canvas, .side-guide canvas')) {
      if (!c.offsetParent) continue;
      const ctx = c.getContext('2d');
      ctx.clearRect(0, 0, c.width, c.height);
      g.boxes = g.boxes || {};
      const key = c.width + 'x' + c.height;
      const b = g.boxes[key] || (g.boxes[key] = guideBox(g, c.width, c.height));
      const map = (p) => [b.ox + (p[0] * 16 - b.x0) * b.k, b.oy + (p[1] * 9 - b.y0) * b.k];
      // The guide faces you like a person in front of you, so it is mirrored like your own image.
      ctx.save(); ctx.translate(c.width, 0); ctx.scale(-1, 1);
      drawSkeleton(ctx, { pose: g.pose[i], lh: g.lh[i], rh: g.rh[i], lhOn: g.lh_on[i], rhOn: g.rh_on[i],
        oval: g.face_on[i] ? g.oval[i] : null, lips: g.face_on[i] ? g.lips[i] : null }, map, c.width / 300);
      ctx.restore();
    }
  }
  const tick = (now) => { drawGuide(now); requestAnimationFrame(tick); };

  // ---------- recording ----------
  // Start and stop are measured in time, not frames, so a slow phone reacts as fast as a laptop.
  // Replayed on the recorded trial clips at 6 fps: start lag 233 to 67 ms, stop lag 1.3 s to 0.4 s.
  const STOP_MS = 250, ARM_MS = 200, PRE_MS = 700, MIN_MS = 500;
  let quietSince = 0, restSince = 0;
  const isActive = (h) => h !== null && h < START_R;
  const isQuiet = (h) => h === null || h > END_R;

  function onFrame(r, t) {
    const row = serialize(r);
    const h = wristHeight(r.poseLandmarks);
    buffer.push({ row, t }); while (buffer.length > 2 && t - buffer[0].t > PRE_MS) buffer.shift();
    if (busy || waitingNext || $('practice').hidden || lastState === 'ok' || t < lockUntil) return;
    if (!recording) {
      // Arm only after the hands have rested a moment, so a result never re-triggers itself.
      if (!armed) {
        if (isQuiet(h)) restSince = restSince || t; else restSince = 0;
        if ((restSince && t - restSince >= ARM_MS) || t < manualUntil) armed = true; else return;
      }
      if (isActive(h) || (manualUntil && t < manualUntil)) {
        recording = { frames: buffer.slice(), start: t };
        quietSince = 0; setState('rec'); hideMessage(true); $('hintSheet').hidden = true; frameNote = '';
        framing(r.poseLandmarks);
      }
      return;
    }
    recording.frames.push({ row, t });
    if (isQuiet(h)) quietSince = quietSince || t; else quietSince = 0;
    const finished = manualUntil ? t >= manualUntil : (quietSince && t - quietSince >= STOP_MS && t - recording.start > MIN_MS);
    if (finished || t - recording.start > MAX_MS) finish();
  }

  async function finish() {
    const clip = recording; recording = null; manualUntil = 0; frameNote = '';
    if (clip.frames.length < MIN_FRAMES) { idle(); hideMessage(false); return; }
    busy = true;
    message('idle', 'i-eye', 'Revisando', ''); hideMessage(false); setState('idle');
    let r = null;
    try {
      const res = await fetch('/api/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ frames: clip.frames.map((f) => f.row), t: clip.frames.map((f) => f.t), target }) });
      if (!res.ok) throw new Error(String(res.status));
      r = await res.json();
    } catch (e) {
      console.error(e);
      setState('doubt'); message('doubt', 'i-question', 'No pude revisar la seña', 'Revisa la conexión e inténtalo otra vez.');
      busy = false; armed = false; lockUntil = performance.now() + 800; return;
    }
    busy = false; armed = false; lockUntil = performance.now() + 800;
    react(r);
  }

  function react(r) {
    const hit = !r.abstain && r.top === target;
    if (mode === 'lesson') {
      if (hit) {
        done.add(target); save(); setState('ok'); renderLine();
        const nextI = ORDER.findIndex((k, i) => i > idx && !done.has(k));
        const nextName = nextI >= 0 ? name(ORDER[nextI]) : (done.size === 5 ? 'el repaso' : name(ORDER[ORDER.findIndex((k) => !done.has(k))]));
        message('ok', 'i-check', '¡La lograste!', `Sigue ${nextName}.`, 'Toca «Siguiente» cuando quieras.');
        waitingNext = true; feet('lesson-ok');
        return;
      }
      return miss(r);
    }
    // review
    review.tries++;
    if (hit) {
      review.results[target] = { ok: true, tries: review.tries };
      setState('ok'); message('ok', 'i-check', `Bien, era ${name(target)}`, '', 'Toca «Siguiente» cuando quieras.');
      waitingNext = true; feet('review-next');
      return;
    }
    if (review.tries >= 2) {
      review.results[target] = { ok: false, tries: review.tries };
      setState('fail'); message('fail', 'i-x', 'Esta vez no salió', r.tip ? r.tip.text : '', 'La practicas al final. Toca «Siguiente».');
      waitingNext = true; feet('review-next');
      return;
    }
    miss(r);
  }

  function miss(r) {
    const tip = r.tip || { kind: 'look', text: 'Mira la guía otra vez y fíjate en la forma de la mano.' };
    const looked = r.top !== target && tip.kind !== 'look' ? `Se pareció más a ${name(r.top)}. ` : '';
    if (r.abstain) {
      setState('doubt');
      message('doubt', TIP_ICON[tip.kind] || 'i-question', 'Ajusta un detalle', tip.text, 'No la alcancé a reconocer bien. Inténtalo otra vez.');
    } else {
      setState('try');
      message('try', TIP_ICON[tip.kind] || 'i-eye', 'Casi', tip.text, `${looked}Inténtalo otra vez.`);
    }
  }

  // ---------- camera ----------
  async function ensureCamera() {
    if (cameraReady) return;
    cameraReady = true;
    message('idle', 'i-eye', 'Preparando la cámara', 'Un momento');
    try {
      holistic = new Holistic({ locateFile: (f) => `/static/vendor/holistic/${f}` });
      holistic.setOptions({ modelComplexity: 1, smoothLandmarks: true, enableSegmentation: false, refineFaceLandmarks: false,
        minDetectionConfidence: 0.5, minTrackingConfidence: 0.5, selfieMode: false });
      let lastT = 0;
      holistic.onResults((r) => { drawLive(r); framing(r.poseLandmarks); onFrame(r, lastT); });
      await holistic.initialize();
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false });
      video.srcObject = stream; await video.play();
      overlay.width = video.videoWidth; overlay.height = video.videoHeight;
      idle();
      // Process each new camera frame once (requestVideoFrameCallback where available), and skip the
      // 16:9 copy when the camera already delivers 16:9 frames.
      let sized = '';
      const process = async () => {
        if (video.readyState >= 2 && !$('practice').hidden) {
          const vw = video.videoWidth, vh = video.videoHeight;
          const direct = Math.abs(vw / vh - W / H) < 0.01;
          const s = direct ? W / vw : Math.min(W / vw, H / vh);
          const ox = direct ? 0 : (W - vw * s) / 2, oy = direct ? 0 : (H - vh * s) / 2;
          letterbox = { s, ox, oy, vw, vh };
          if (sized !== vw + 'x' + vh) {
            sized = vw + 'x' + vh; overlay.width = vw; overlay.height = vh;
            offCtx.fillStyle = '#000'; offCtx.fillRect(0, 0, W, H);
          }
          if (!direct) offCtx.drawImage(video, ox, oy, vw * s, vh * s);
          lastT = performance.now();
          try { await holistic.send({ image: direct ? video : off }); } catch (e) { console.error(e); }
        }
        schedule();
      };
      const schedule = () => (video.requestVideoFrameCallback ? video.requestVideoFrameCallback(process) : requestAnimationFrame(process));
      schedule();
    } catch (e) {
      console.error(e);
      cameraReady = false;
      setState('doubt');
      message('doubt', 'i-question', 'No pude abrir la cámara', 'Dale permiso de cámara al navegador y recarga la página.');
    }
  }

  // ---------- controls ----------
  $('closeHints').onclick = () => { $('hintSheet').hidden = true; };
  const toggleSkeleton = () => {
    skeletonOn = !skeletonOn;
    $('skel').setAttribute('aria-pressed', String(skeletonOn));
    $('skel2').setAttribute('aria-pressed', String(skeletonOn));
    $('skel2').lastChild.textContent = `Esqueleto sobre tu imagen: ${skeletonOn ? 'sí' : 'no'}`;
    for (const b of [$('skel'), $('skel2')]) b.querySelector('use').setAttribute('href', skeletonOn ? '#i-bones' : '#i-bones-off');
    $('skel').title = skeletonOn ? 'Esqueleto: visible' : 'Esqueleto: oculto';
    overlay.classList.toggle('off', !skeletonOn);
  };
  $('skel').onclick = toggleSkeleton; $('skel2').onclick = toggleSkeleton;
  $('timer').onclick = () => {
    if (busy || recording) return;
    clearTimeout(advanceTimer);
    let n = 3; $('timer').disabled = true; setState('idle');
    const step = () => {
      if (n > 0) { message('idle', 'i-timer', `Empieza en ${n}`, 'Prepárate con las manos abajo'); hideMessage(false); n--; setTimeout(step, 800); return; }
      manualUntil = performance.now() + 3000; armed = true; lockUntil = 0;
      $('timer').disabled = false;
    };
    step();
  };
  $('start').onclick = () => {
    const first = ORDER.findIndex((k) => !done.has(k));
    if (first < 0) startReview(); else startLesson(first);
  };
  $('restart').onclick = () => { done = new Set(); save(); startLesson(0); };
  $('again').onclick = () => startReview(true);
  $('beginReview').onclick = () => startReview(true);
  $('backLessons').onclick = () => { const f = ORDER.findIndex((k) => !done.has(k)); startLesson(f < 0 ? 0 : f); };

  // ---------- boot ----------
  async function boot() {
    cfg = await (await fetch('/api/config')).json();
    try { const g = await fetch('/private/guides.json'); if (g.ok) guides = await g.json(); } catch (_) { /* no guide */ }
    load();
    if (done.size) {
      $('start').innerHTML = (done.size === 5 ? 'Ir al repaso' : 'Seguir donde iba') + ' <svg class="i"><use href="#i-arrow"/></svg>';
      $('restart').hidden = false;
    }
    requestAnimationFrame(tick);
    preview(new URLSearchParams(location.search).get('vista'));
  }

  // Static states for screenshots and rehearsal: ?vista=turno|encuadre|grabando|casi|duda|logro|repaso|resultado
  function preview(v) {
    if (!v) return;
    const fake = { top: 'sign_01', abstain: false, tip: { kind: 'down', text: 'Baja un poco las manos, van a la altura del pecho.' } };
    if (v === 'resultado') {
      review = { q: ['sign_03', 'sign_01', 'sign_05', 'sign_02', 'sign_04'], i: 4, tries: 0,
        results: { sign_03: { ok: true, tries: 1 }, sign_01: { ok: true, tries: 1 }, sign_05: { ok: true, tries: 2 }, sign_02: { ok: true, tries: 1 }, sign_04: { ok: false, tries: 2 } } };
      return showResult();
    }
    done = new Set(['sign_01']);
    if (v === 'repaso') { done = new Set(ORDER); startReview(true); return; }
    if (v === 'etapa') { done = new Set(ORDER); startReview(); return; }
    startLesson(1);
    setTimeout(() => {
      if (v === 'casi') miss(fake);
      if (v === 'duda') miss({ ...fake, abstain: true, tip: { kind: 'look', text: 'Hazla un poco más despacio.' } });
      if (v === 'logro') react({ top: 'sign_02', abstain: false });
      if (v === 'ajuste') miss({ top: 'sign_05', abstain: true, tip: { kind: 'look', text: 'En ¿Qué necesitas? primero señalas hacia adelante y luego abres las dos manos.' } });
      if (v === 'fallo') { setState('fail'); message('fail', 'i-x', 'Esta vez no salió', 'Baja un poco las manos, van a la altura del pecho.', 'La practicas al final. Toca «Siguiente».'); }
      if (v === 'encuadre') { setState('frame'); message('try', 'i-far', 'Aléjate un poco', 'Que se vean tu cintura y tus codos.'); }
      if (v === 'grabando') { setState('rec'); hideMessage(true); const c = $('chip'); c.hidden = false; c.className = 'chip rec'; c.innerHTML = '<span class="pulse"></span>Grabando'; }
    }, 300);
  }
  boot().catch((e) => console.error(e));
})();
