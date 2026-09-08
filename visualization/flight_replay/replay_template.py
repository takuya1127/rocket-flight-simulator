REPLAY_HTML = r'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
  * { box-sizing: border-box; }
  html, body {
    margin: 0;
    padding: 0;
    background: transparent;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }
  .replay-wrap { width: 100%; }
  .replay-card {
    width: 100%;
    background: #071426;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 8px 24px rgba(2,10,22,.10);
  }
  .canvas-wrap {
    position: relative;
    width: 100%;
    height: __CANVAS_HEIGHT__px;
    background: #0b1d35;
  }
  canvas { display: block; width: 100%; height: 100%; }
  .timeline-row {
    height: 46px;
    display: flex;
    align-items: center;
    padding: 2px 14px 6px 14px;
    background: #071426;
    border-top: 1px solid rgba(255,255,255,.08);
  }
  input[type="range"] {
    width: 100%;
    accent-color: #ff5a52;
    cursor: pointer;
  }
  .external-controls {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 10px;
  }
  .control-btn {
    height: __CONTROL_HEIGHT__px;
    border-radius: 9px;
    border: 1px solid #bcc4d0;
    background: #ffffff;
    color: #202735;
    font-size: 15px;
    font-weight: 650;
    cursor: pointer;
  }
  .control-btn:hover { background: #f6f8fb; }
  .control-btn:active { transform: scale(.985); }
</style>
</head>
<body>
<div class="replay-wrap">
  <div class="replay-card">
    <div class="canvas-wrap">
      <canvas id="flightCanvas"></canvas>
    </div>
    <div class="timeline-row">
      <input id="timeline" type="range" min="0" max="1000" value="0" step="1" aria-label="再生位置" />
    </div>
  </div>

  <div class="external-controls">
    <button id="playBtn" class="control-btn">▶ 再生</button>
    <button id="pauseBtn" class="control-btn">Ⅱ 一時停止</button>
  </div>
</div>

<script>
const DATA = __DATA__;
const EVENT_TIMES = __EVENT_TIMES__;
const PLAYBACK_DURATION = 12000;
const STATUS_FONT_SIZE = __STATUS_FONT_SIZE__;
const ROCKET_HEIGHT = __ROCKET_HEIGHT__;

const canvas = document.getElementById('flightCanvas');
const ctx = canvas.getContext('2d', { alpha: false });
const timeline = document.getElementById('timeline');
const playBtn = document.getElementById('playBtn');
const pauseBtn = document.getElementById('pauseBtn');

function imageFrom(src){
    const image = new Image();
    image.src = src;
    return image;
}

const firstStageImg = imageFrom(__FIRST_STAGE__);
const secondStageImg = imageFrom(__SECOND_STAGE__);
const boosterImg = imageFrom(__BOOSTER__);
const fairingImg = imageFrom(__FAIRING__);
const launchPadImg = imageFrom(__LAUNCH_PAD__);
const flameImg = imageFrom(__FLAME__);
const smokeImg = imageFrom(__SMOKE__);
const groundImg = imageFrom(__GROUND_BACKGROUND__);
const upperImg = imageFrom(__UPPER_BACKGROUND__);
const spaceImg = imageFrom(__SPACE_BACKGROUND__);

const allImages = [
  firstStageImg,
  secondStageImg,
  boosterImg,
  fairingImg,
  launchPadImg,
  flameImg,
  smokeImg,
  groundImg,
  upperImg,
  spaceImg,
];

const xMaxRaw = Math.max(...DATA.map(p => p.x), 1);
const yMaxRaw = Math.max(...DATA.map(p => p.y), 1);
const xMax = xMaxRaw * 1.04;
const yMax = yMaxRaw * 1.08;

let playing = false;
let progress = 0;
let lastTimestamp = null;
let rafId = null;

function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v));
}

function mixColor(a, b, t) {
  const c = [];
  for (let i = 0; i < 3; i++) {
    c.push(Math.round(a[i] + (b[i] - a[i]) * t));
  }
  return `rgb(${c[0]},${c[1]},${c[2]})`;
}

function skyColors(altitude) {
  const lowTop = [67, 145, 214];
  const lowBottom = [167, 219, 246];
  const midTop = [19, 65, 122];
  const midBottom = [65, 135, 190];
  const highTop = [5, 17, 45];
  const highBottom = [20, 55, 105];
  const spaceTop = [1, 4, 13];
  const spaceBottom = [5, 12, 30];

  if (altitude <= 12000) {
    const t = clamp(altitude / 12000, 0, 1);
    return [mixColor(lowTop, midTop, t), mixColor(lowBottom, midBottom, t)];
  }
  if (altitude <= 35000) {
    const t = (altitude - 12000) / 23000;
    return [mixColor(midTop, highTop, t), mixColor(midBottom, highBottom, t)];
  }
  const t = clamp((altitude - 35000) / 45000, 0, 1);
  return [mixColor(highTop, spaceTop, t), mixColor(highBottom, spaceBottom, t)];
}

function drawSky(w, h, altitude) {
  const [topColor, bottomColor] = skyColors(altitude);
  const gradient = ctx.createLinearGradient(0, 0, 0, h);
  gradient.addColorStop(0, topColor);
  gradient.addColorStop(1, bottomColor);
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, w, h);

  const starAlpha = clamp((altitude - 18000) / 40000, 0, .85);
  if (starAlpha > 0) {
    ctx.save();
    ctx.fillStyle = `rgba(255,255,255,${starAlpha})`;
    for (let i = 0; i < 64; i++) {
      const sx = ((i * 83 + 31) % 997) / 997 * w;
      const sy = ((i * 157 + 47) % 991) / 991 * h * .82;
      const size = (i % 7 === 0) ? 1.7 : 1.0;
      ctx.fillRect(sx, sy, size, size);
    }
    ctx.restore();
  }
}

function formatAltitude(value) {
  if (value >= 1000) {
    const km = value / 1000;
    return (km >= 10 ? km.toFixed(0) : km.toFixed(1)) + 'km';
  }
  return Math.round(value) + 'm';
}

function formatDistance(value) {
  if (value >= 1000) {
    return (value / 1000).toFixed(value >= 5000 ? 0 : 1) + 'km';
  }
  return Math.round(value) + 'm';
}

function getInterpolatedState(p) {
  const scaled = p * (DATA.length - 1);
  const i0 = Math.floor(scaled);
  const i1 = Math.min(i0 + 1, DATA.length - 1);
  const f = scaled - i0;
  const a = DATA[i0];
  const b = DATA[i1];
  const lerp = (v0, v1) => v0 + (v1 - v0) * f;
  return {
    index: i0,
    t: lerp(a.t, b.t),
    x: lerp(a.x, b.x),
    y: lerp(a.y, b.y),
    vx: lerp(a.vx, b.vx),
    vy: lerp(a.vy, b.vy),
    speed: lerp(a.speed, b.speed),
    mach: lerp(a.mach, b.mach),
    angle: lerp(a.angle, b.angle),
    flightAngle: lerp(a.flightAngle, b.flightAngle),
    burning: f < .5 ? a.burning : b.burning,
    smoke: lerp(a.smoke, b.smoke),
  };
}

function smoothstep(edge0, edge1, value) {
  const t = clamp((value - edge0) / Math.max(edge1 - edge0, .0001), 0, 1);
  return t * t * (3 - 2 * t);
}

function drawCoverImage(image, w, h, opacity, scale = 1, offsetX = 0, offsetY = 0) {
  if (!image.complete || !image.naturalWidth || !image.naturalHeight || opacity <= .005) {
    return;
  }

  const imageAspect = image.naturalWidth / image.naturalHeight;
  const canvasAspect = w / h;
  let drawWidth;
  let drawHeight;

  if (imageAspect > canvasAspect) {
    drawHeight = h;
    drawWidth = h * imageAspect;
  } else {
    drawWidth = w;
    drawHeight = w / imageAspect;
  }

  drawWidth *= scale;
  drawHeight *= scale;

  ctx.save();
  ctx.globalAlpha = clamp(opacity, 0, 1);
  ctx.drawImage(
    image,
    (w - drawWidth) / 2 + offsetX,
    (h - drawHeight) / 2 + offsetY,
    drawWidth,
    drawHeight
  );
  ctx.restore();
}

function drawBackgroundImage(image, w, h, yOffset = 0, scale = 1.04) {
  if (!image.complete || !image.naturalWidth || !image.naturalHeight) return;

  const imageAspect = image.naturalWidth / image.naturalHeight;
  const canvasAspect = w / h;
  let drawWidth;
  let drawHeight;

  if (imageAspect > canvasAspect) {
    drawHeight = h;
    drawWidth = h * imageAspect;
  } else {
    drawWidth = w;
    drawHeight = w / imageAspect;
  }

  drawWidth *= scale;
  drawHeight *= scale;

  ctx.drawImage(
    image,
    (w - drawWidth) / 2,
    (h - drawHeight) / 2 + yOffset,
    drawWidth,
    drawHeight
  );
}

function slideProgress(altitude, startAltitude, endAltitude) {
  return smoothstep(startAltitude, endAltitude, altitude);
}

function drawBackground(w, h, state) {
  const altitude = Math.max(0, state.y);

  /*
   * Replay V3.1
   *
   * 3枚構成
   *
   * 0 ～ 8 km
   *   地上背景
   *
   * 8 ～ 30 km
   *   地上 → 高高度
   *   スライド + クロスフェード
   *
   * 30 ～ 65 km
   *   高高度背景
   *
   * 65 ～ 110 km
   *   高高度 → 宇宙
   *   スライド + クロスフェード
   *
   * 110 km ～
   *   宇宙背景
   */

  const groundToUpper = smoothstep(
    8000,
    30000,
    altitude
  );

  const upperToSpace = smoothstep(
    65000,
    110000,
    altitude
  );

  ctx.save();

  ctx.fillStyle = '#061225';
  ctx.fillRect(0, 0, w, h);


  // -------------------------
  // 地上 → 高高度
  // -------------------------
  if (altitude < 30000) {

    const p = groundToUpper;

    /*
     * 地上背景
     *
     * p = 0
     *   通常位置
     *
     * p = 1
     *   少し下へスライド
     *   + 完全に透明
     */
    ctx.save();

    ctx.globalAlpha =
      1 - p;

    drawBackgroundImage(
      groundImg,
      w,
      h,
      p * h * 0.35,
      1.05
    );

    ctx.restore();


    /*
     * 高高度背景
     *
     * 最初は少し上に置いて
     * 徐々に下へ入ってくる。
     */
    if (p > 0.001) {

      ctx.save();

      ctx.globalAlpha =
        p;

      drawBackgroundImage(
        upperImg,
        w,
        h,
        -h * 0.35 + p * h * 0.35,
        1.04
      );

      ctx.restore();
    }
  }


  // -------------------------
  // 高高度のみ
  // -------------------------
  else if (altitude < 65000) {

    const drift =
      clamp(
        (altitude - 30000) /
        35000,
        0,
        1
      ) *
      h *
      0.05;

    drawBackgroundImage(
      upperImg,
      w,
      h,
      drift,
      1.04
    );
  }


  // -------------------------
  // 高高度 → 宇宙
  // -------------------------
  else if (altitude < 110000) {

    const p = upperToSpace;


    /*
     * 高高度背景
     */
    ctx.save();

    ctx.globalAlpha =
      1 - p;

    drawBackgroundImage(
      upperImg,
      w,
      h,
      p * h * 0.30,
      1.04
    );

    ctx.restore();


    /*
     * 宇宙背景
     */
    ctx.save();

    ctx.globalAlpha =
      p;

    drawBackgroundImage(
      spaceImg,
      w,
      h,
      -h * 0.30 + p * h * 0.30,
      1.03
    );

    ctx.restore();
  }


  // -------------------------
  // 宇宙
  // -------------------------
  else {

    const drift =
      clamp(
        (altitude - 110000) /
        250000,
        0,
        1
      ) *
      h *
      0.03;

    drawBackgroundImage(
      spaceImg,
      w,
      h,
      drift,
      1.03
    );
  }

  ctx.restore();
}

function drawLaunchGround(w, h, state) {
  const visible = state.t < 18 && state.y < 2200 && state.vy >= -1;
  if (!visible) return;

  const rise = clamp(state.y / 2200, 0, 1);
  const alpha = 1 - smoothstep(.55, 1, rise);
  const groundTop = h * (.84 + rise * .28);

  ctx.save();
  ctx.globalAlpha = alpha;

  const gradient = ctx.createLinearGradient(0, groundTop, 0, h);
  gradient.addColorStop(0, 'rgba(104,110,108,.88)');
  gradient.addColorStop(.32, 'rgba(72,78,77,.96)');
  gradient.addColorStop(1, 'rgba(35,42,43,1)');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, groundTop, w, h - groundTop);

  ctx.fillStyle = 'rgba(18,22,24,.28)';
  ctx.beginPath();
  ctx.ellipse(w * .52, groundTop + h * .025, w * .18, h * .018, 0, 0, Math.PI * 2);
  ctx.fill();

  ctx.restore();
}

function drawLaunchPad(w, h, state) {
  if (!launchPadImg.complete || !launchPadImg.naturalWidth) return;

  const nearLaunchSite = Math.abs(state.x) < 1500;
  const visible = nearLaunchSite && state.t < 18 && state.y < 2200 && state.vy >= -1;
  if (!visible) return;

  const rise = clamp(state.y / 2200, 0, 1);
  const alpha = 1 - smoothstep(.55, 1, rise);

  // 発射台は画面下の地面に固定する。旧V2のように空中へ配置しない。
  const padHeight = h * .44;
  const aspect = launchPadImg.naturalWidth / launchPadImg.naturalHeight;
  const padWidth = padHeight * aspect;
  const groundTop = h * (.84 + rise * .28);
  const padBottom = groundTop + h * .035;

  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.drawImage(
    launchPadImg,
    w * .52 - padWidth * .50,
    padBottom - padHeight,
    padWidth,
    padHeight
  );
  ctx.restore();
}

function imageDimensionsByHeight(
  img,
  height,
  fallbackAspect = .32
) {
  const aspect =
    img.naturalWidth &&
    img.naturalHeight
      ? img.naturalWidth /
        img.naturalHeight
      : fallbackAspect;

  return {
    width: height * aspect,
    height: height,
  };
}


function drawFlame(
  vehicleHeight,
  x = 0,
  y = 0,
  scale = 1.0
) {
  if (
    !flameImg.complete ||
    !flameImg.naturalWidth
  ) {
    return;
  }

  const pulse =
    1 +
    Math.sin(
      performance.now() / 75
    ) * .055;

  const flameHeight =
    vehicleHeight *
    .68 *
    pulse *
    scale;

  const flameWidth =
    flameHeight *
    flameImg.naturalWidth /
    Math.max(
      flameImg.naturalHeight,
      1
    );

  ctx.save();

  ctx.globalAlpha = .93;
  ctx.globalCompositeOperation = 'screen';

  ctx.drawImage(
    flameImg,
    x - flameWidth / 2,
    y + vehicleHeight * .43,
    flameWidth,
    flameHeight
  );

  ctx.restore();
}


function drawLaunchSmoke(
  w,
  h,
  state
) {
  if (
    state.smoke <= .15 ||
    !smokeImg.complete ||
    !smokeImg.naturalWidth ||
    state.y > 1800
  ) {
    return;
  }

  const ratio =
    clamp(
      state.smoke / 10,
      0,
      1
    );

  const smokeWidth =
    w *
    (
      .38 +
      (1 - ratio) * .18
    );

  const smokeHeight =
    smokeWidth *
    smokeImg.naturalHeight /
    Math.max(
      smokeImg.naturalWidth,
      1
    );

  ctx.save();

  ctx.globalAlpha =
    .18 +
    ratio * .58;

  ctx.drawImage(
    smokeImg,
    w * .52 - smokeWidth / 2,
    h * .77 - smokeHeight * .15,
    smokeWidth,
    smokeHeight
  );

  ctx.restore();
}


function drawAttachedBooster(
  side,
  vehicleHeight,
  burning
) {
  if (
    !boosterImg.complete ||
    !boosterImg.naturalWidth
  ) {
    return;
  }

  const boosterHeight =
    vehicleHeight * .78;

  const size =
    imageDimensionsByHeight(
      boosterImg,
      boosterHeight
    );

  const offsetX =
    side *
    vehicleHeight *
    .24;

  const offsetY =
    vehicleHeight *
    .10;

  ctx.save();

  ctx.translate(
    offsetX,
    offsetY
  );

  if (side < 0) {
    ctx.scale(-1, 1);
  }

  if (burning) {
    drawFlame(
      boosterHeight,
      0,
      0,
      .55
    );
  }

  ctx.drawImage(
    boosterImg,
    -size.width / 2,
    -boosterHeight / 2,
    size.width,
    boosterHeight
  );

  ctx.restore();
}


function drawSeparatedBoosters(
  state,
  vehicleHeight
) {
  const separationTime =
    EVENT_TIMES.boosterSeparation;

  if (
    separationTime === null ||
    state.t < separationTime ||
    state.t > separationTime + 3.4 ||
    !boosterImg.complete ||
    !boosterImg.naturalWidth
  ) {
    return;
  }

  const progress =
    clamp(
      (
        state.t -
        separationTime
      ) /
      3.4,
      0,
      1
    );

  const opacity =
    1 - progress;

  const boosterHeight =
    vehicleHeight * .74;

  const size =
    imageDimensionsByHeight(
      boosterImg,
      boosterHeight
    );

  for (
    const side of [-1, 1]
  ) {
    const outward =
      vehicleHeight *
      (
        .28 +
        progress * 1.05
      );

    const downward =
      vehicleHeight *
      (
        .08 +
        progress * .88
      );

    ctx.save();

    ctx.globalAlpha =
      opacity;

    ctx.translate(
      side * outward,
      downward
    );

    ctx.rotate(
      side *
      progress *
      .58
    );

    if (side < 0) {
      ctx.scale(-1, 1);
    }

    ctx.drawImage(
      boosterImg,
      -size.width / 2,
      -boosterHeight / 2,
      size.width,
      boosterHeight
    );

    ctx.restore();
  }
}


function drawSeparatedFirstStage(
  state,
  vehicleHeight
) {
  const separationTime =
    EVENT_TIMES.stageSeparation;

  if (
    separationTime === null ||
    state.t < separationTime ||
    state.t > separationTime + 4.0 ||
    !firstStageImg.complete ||
    !firstStageImg.naturalWidth
  ) {
    return;
  }

  const progress =
    clamp(
      (
        state.t -
        separationTime
      ) /
      4.0,
      0,
      1
    );

  const stageHeight =
    vehicleHeight * .90;

  const size =
    imageDimensionsByHeight(
      firstStageImg,
      stageHeight
    );

  ctx.save();

  ctx.globalAlpha =
    1 - progress;

  ctx.translate(
    -vehicleHeight *
      .16 *
      progress,
    vehicleHeight *
      (
        .30 +
        progress * 1.15
      )
  );

  ctx.rotate(
    -.18 -
    progress * .38
  );

  ctx.drawImage(
    firstStageImg,
    -size.width / 2,
    -stageHeight / 2,
    size.width,
    stageHeight
  );

  ctx.restore();
}


function drawSeparatedFairing(
  state,
  vehicleHeight
) {
  const separationTime =
    EVENT_TIMES.fairingSeparation;

  if (
    separationTime === null ||
    state.t < separationTime ||
    state.t > separationTime + 3.2 ||
    !fairingImg.complete ||
    !fairingImg.naturalWidth
  ) {
    return;
  }

  const progress =
    clamp(
      (
        state.t -
        separationTime
      ) /
      3.2,
      0,
      1
    );

  const fairingHeight =
    vehicleHeight * .48;

  const size =
    imageDimensionsByHeight(
      fairingImg,
      fairingHeight,
      .42
    );

  for (
    const side of [-1, 1]
  ) {
    ctx.save();

    ctx.globalAlpha =
      1 - progress;

    ctx.translate(
      side *
        vehicleHeight *
        (
          .10 +
          progress * .72
        ),
      -vehicleHeight *
        (
          .30 -
          progress * .16
        )
    );

    ctx.rotate(
      side *
      (
        .08 +
        progress * .70
      )
    );

    if (side < 0) {
      ctx.scale(-1, 1);
    }

    ctx.drawImage(
      fairingImg,
      -size.width / 2,
      -fairingHeight / 2,
      size.width,
      fairingHeight
    );

    ctx.restore();
  }
}


function drawRocket(
  px,
  py,
  state
) {
  const stageSeparated =
    EVENT_TIMES.stageSeparation !== null &&
    state.t >=
      EVENT_TIMES.stageSeparation;

  const bodyImage =
    stageSeparated
      ? secondStageImg
      : firstStageImg;

  const vehicleHeight =
    stageSeparated
      ? ROCKET_HEIGHT * .88
      : ROCKET_HEIGHT;

  const size =
    imageDimensionsByHeight(
      bodyImage,
      vehicleHeight
    );

  ctx.save();

  ctx.translate(
    px,
    py
  );

  ctx.rotate(
    (
      90 -
      state.angle
    ) *
    Math.PI /
    180
  );

  const boostersExist =
    EVENT_TIMES.boosterSeparation !== null;

  const boostersAttached =
    boostersExist &&
    !stageSeparated &&
    state.t <
      EVENT_TIMES.boosterSeparation;

  if (boostersAttached) {
    drawAttachedBooster(
      -1,
      vehicleHeight,
      state.burning
    );

    drawAttachedBooster(
      1,
      vehicleHeight,
      state.burning
    );
  }

  if (state.burning) {
    drawFlame(
      vehicleHeight
    );
  }

  if (
    bodyImage.complete &&
    bodyImage.naturalWidth
  ) {
    ctx.drawImage(
      bodyImage,
      -size.width / 2,
      -vehicleHeight / 2,
      size.width,
      vehicleHeight
    );
  }

  drawSeparatedBoosters(
    state,
    vehicleHeight
  );

  drawSeparatedFirstStage(
    state,
    vehicleHeight
  );

  drawSeparatedFairing(
    state,
    vehicleHeight
  );

  ctx.restore();
}

function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio || 1, 1.6);
  canvas.width = Math.max(1, Math.round(rect.width * dpr));
  canvas.height = Math.max(1, Math.round(rect.height * dpr));
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  draw();
}

function draw() {
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;

  if (!w || !h) {
    return;
  }

  const state =
    getInterpolatedState(
      progress
    );

  drawBackground(
    w,
    h,
    state
  );

  const mobile =
    w < 600;

  drawLaunchGround(
    w,
    h,
    state
  );

  drawLaunchPad(
    w,
    h,
    state
  );

  drawLaunchSmoke(
    w,
    h,
    state
  );

  const launchMove =
    clamp(
      state.t / 3.2,
      0,
      1
    );

  const rocketX =
    w * .52;

  const launchY =
    h * .76;

  const trackingY =
    h *
    (
      mobile
        ? .49
        : .46
    );

  const rocketY =
    launchY +
    (
      trackingY -
      launchY
    ) *
    launchMove;

  const overlayAlpha =
    clamp(
      state.y /
      120000,
      .02,
      .11
    );

  ctx.save();

  ctx.fillStyle =
    `rgba(
      0,
      6,
      18,
      ${overlayAlpha}
    )`;

  ctx.fillRect(
    0,
    0,
    w,
    h
  );

  ctx.restore();

  drawRocket(
    rocketX,
    rocketY,
    state
  );

  const stageSeparated =
    EVENT_TIMES.stageSeparation !== null &&
    state.t >=
      EVENT_TIMES.stageSeparation;

  const stageText =
    stageSeparated
      ? 'STAGE 2'
      : 'STAGE 1';

  const statusLines = [
    `T+${state.t.toFixed(1)} s`,
    `ALT  ${(state.y / 1000).toFixed(2)} km`,
    `VEL  ${Math.round(state.speed)} m/s`,
    `MACH ${state.mach.toFixed(2)}`,
    `RNG  ${formatDistance(Math.abs(state.x))}`,
    `PITCH ${state.angle.toFixed(1)}° / PATH ${state.flightAngle.toFixed(1)}°`,
    stageText,
  ];

  const panelX =
    mobile ? 10 : 16;

  const panelY =
    mobile ? 10 : 14;

  const lineHeight =
    mobile ? 18 : 21;

  const panelWidth =
    mobile ? 190 : 230;

  const panelHeight =
    16 +
    statusLines.length *
    lineHeight;

  ctx.save();

  ctx.fillStyle =
    'rgba(4, 10, 19, .78)';

  ctx.fillRect(
    panelX,
    panelY,
    panelWidth,
    panelHeight
  );

  ctx.strokeStyle =
    'rgba(255, 90, 82, .95)';

  ctx.lineWidth = 1.2;

  ctx.strokeRect(
    panelX,
    panelY,
    panelWidth,
    panelHeight
  );

  ctx.font =
    `650 ${STATUS_FONT_SIZE}px system-ui, -apple-system, sans-serif`;

  ctx.fillStyle = '#ffffff';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';

  statusLines.forEach(
    (line, index) => {
      ctx.fillText(
        line,
        panelX + 10,
        panelY +
          12 +
          index *
          lineHeight
      );
    }
  );

  ctx.restore();

  let eventText = '';

  const boosterTime =
    EVENT_TIMES.boosterSeparation;

  const stageTime =
    EVENT_TIMES.stageSeparation;

  const fairingTime =
    EVENT_TIMES.fairingSeparation;

  if (
    boosterTime !== null &&
    Math.abs(
      state.t -
      boosterTime
    ) < 1.7
  ) {
    eventText =
      'BOOSTER SEPARATION';

  } else if (
    fairingTime !== null &&
    Math.abs(
      state.t -
      fairingTime
    ) < 1.7
  ) {
    eventText =
      'FAIRING SEPARATION';

  } else if (
    stageTime !== null &&
    Math.abs(
      state.t -
      stageTime
    ) < 1.7
  ) {
    eventText =
      'STAGE SEPARATION';
  }

  if (eventText) {
    ctx.save();

    ctx.font =
      `700 ${mobile ? 11 : 13}px system-ui, -apple-system, sans-serif`;

    const eventWidth =
      ctx.measureText(
        eventText
      ).width + 20;

    const eventX =
      w -
      eventWidth -
      (mobile ? 10 : 16);

    const eventY =
      mobile ? 10 : 14;

    ctx.fillStyle =
      'rgba(5, 16, 31, .84)';

    ctx.fillRect(
      eventX,
      eventY,
      eventWidth,
      30
    );

    ctx.strokeStyle =
      'rgba(255,255,255,.42)';

    ctx.strokeRect(
      eventX,
      eventY,
      eventWidth,
      30
    );

    ctx.fillStyle =
      '#ffffff';

    ctx.textAlign =
      'center';

    ctx.textBaseline =
      'middle';

    ctx.fillText(
      eventText,
      eventX +
        eventWidth / 2,
      eventY + 15
    );

    ctx.restore();
  }

  ctx.save();

  ctx.font =
    `${mobile ? 10 : 11}px system-ui, -apple-system, sans-serif`;

  ctx.fillStyle =
    'rgba(255,255,255,.84)';

  ctx.textAlign =
    'right';

  ctx.textBaseline =
    'bottom';

  const rangeText =
    state.y < 9000
      ? (state.vy < -1 && Math.abs(state.x) > 4000 ? 'DESCENT / REMOTE GROUND' : 'LOW ATMOSPHERE')
      : state.y < 24000
        ? 'CLOUD LAYER'
        : state.y < 65000
          ? 'UPPER ATMOSPHERE'
          : 'NEAR SPACE';

  ctx.fillText(
    rangeText,
    w - 12,
    h - 10
  );

  ctx.restore();
}

function animate(timestamp) {
  if (!playing) return;
  if (lastTimestamp === null) lastTimestamp = timestamp;
  const delta = timestamp - lastTimestamp;
  lastTimestamp = timestamp;
  progress += delta / PLAYBACK_DURATION;
  if (progress >= 1) {
    progress = 1;
    playing = false;
  }
  timeline.value = Math.round(progress * 1000);
  draw();
  if (playing) rafId = requestAnimationFrame(animate);
}

playBtn.addEventListener('click', () => {
  if (progress >= 1) progress = 0;
  if (!playing) {
    playing = true;
    lastTimestamp = null;
    rafId = requestAnimationFrame(animate);
  }
});

pauseBtn.addEventListener('click', () => {
  playing = false;
  lastTimestamp = null;
  if (rafId) cancelAnimationFrame(rafId);
});

timeline.addEventListener('input', () => {
  progress = Number(timeline.value) / 1000;
  lastTimestamp = null;
  draw();
});

window.addEventListener('resize', resizeCanvas);
allImages.forEach(
    img =>
        img.addEventListener(
            'load',
            draw
        )
);
resizeCanvas();
</script>
</body>
</html>'''
